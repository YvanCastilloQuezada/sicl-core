"""ARKI H-003: Validity / Invalidation — Read-only evaluation.

H-003 evalúa la validez de derivaciones y artefactos basándose en
integrity_checks de H-001. NO invalida automáticamente. NO recomputa.
NO muta. NO ejecuta. Solo reporta.

Regla fundamental:
  VALIDITY EVALUATION ≠ INVALIDATION EXECUTION

Arquitectura de dos fases:
  Fase 1: Validez por derivación (cada DerivationRecord)
  Fase 2: Situación por artefacto (agregación de derivaciones)

Dependencias:
  - H-001 DerivationLedger (read-only)
  - H-001 integrity_checks (para evaluar inputs)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping
from .derivation import DerivationLedger, VersionedRef, DerivationRecord


# ──────────────────────────────────────────────
# TIPOS DE VALIDEZ
# ──────────────────────────────────────────────

DerivationValidityState = str  # 'VALID' | 'STALE' | 'INVALID' | 'UNCERTAIN'
ArtifactValidityState = str    # 'FULLY_VALID' | 'PARTIALLY_VALID' | 'FULLY_STALE' | 'PARTIALLY_STALE' | 'REQUIRES_HUMAN_REVIEW' | 'INVALID'


# ──────────────────────────────────────────────
# ESTRUCTURAS DE DATOS
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class DerivationValidity:
    """Validez de una derivación específica."""
    derivation_id: str
    output: VersionedRef
    state: DerivationValidityState

    # Discrepancias encontradas (si state !== VALID)
    discrepancies: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    # Proveniencia: qué integrity_checks generaron este estado
    source_checks: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Garantiza que la trazabilidad conserve nombres completos de checks."""
        if not isinstance(self.source_checks, tuple):
            raise TypeError("source_checks must be tuple[str, ...]")
        prefix = "integrity_checks_"
        if any(
            not isinstance(check, str)
            or not check.startswith(prefix)
            or len(check) <= len(prefix)
            for check in self.source_checks
        ):
            raise ValueError("source_checks entries must be integrity_checks_<derivation_id> names")

    def to_dict(self) -> dict[str, Any]:
        return {
            "derivationId": self.derivation_id,
            "output": self.output.to_dict(),
            "state": self.state,
            "discrepancies": list(self.discrepancies),
            "sourceChecks": list(self.source_checks),
        }


@dataclass(frozen=True)
class ArtifactValidity:
    """Situación agregada de un artefacto (output) considerando todas sus derivaciones."""
    artifact_ref: VersionedRef
    state: ArtifactValidityState

    # Todas las derivaciones que contribuyen a este output
    derivation_validities: tuple[DerivationValidity, ...]

    # Resumen agregado
    summary: dict[str, int]

    # Recomendación (NO es decisión automática)
    recommendation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifactRef": self.artifact_ref.to_dict(),
            "state": self.state,
            "derivationValidities": [dv.to_dict() for dv in self.derivation_validities],
            "summary": self.summary,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class ValidityReport:
    """Reporte completo de validez."""
    contract_version: int = 1

    # Input: qué cambio se está evaluando (opcional)
    observed_change: dict[str, Any] | None = None

    # Output: validez de cada derivación
    derivation_validities: tuple[DerivationValidity, ...] = field(default_factory=tuple)

    # Output: situación agregada por artefacto
    artifact_validities: tuple[ArtifactValidity, ...] = field(default_factory=tuple)

    # Metadata
    analysis_metadata: dict[str, int] = field(default_factory=dict)

    # Read-only guarantee
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "contractVersion": self.contract_version,
            "observedChange": self.observed_change,
            "derivationValidities": [dv.to_dict() for dv in self.derivation_validities],
            "artifactValidities": [av.to_dict() for av in self.artifact_validities],
            "analysisMetadata": self.analysis_metadata,
            "readOnly": self.read_only,
        }

    def canonical_dict(self) -> dict[str, Any]:
        """Representación pública estable para comparaciones deterministas."""
        return self.to_dict()


# ──────────────────────────────────────────────
# ANALIZADOR
# ──────────────────────────────────────────────

class ValidityAnalyzer:
    """
    Política explícita: FULLY_STALE se recomienda para RECOMPUTE sin
    autoridad humana adicional. Esto no ejecuta ni invalida el artefacto.
    """
    """
    H-003: Evalúa la validez de derivaciones y artefactos.

    Reglas contractuales:
      V-01: VALIDITY EVALUATION ≠ INVALIDATION EXECUTION
      V-02: ONE STALE DERIVATION ≠ STALE ARTIFACT
      V-03: UNCERTAIN → REQUIRES_HUMAN_REVIEW
      V-04: INVALID → REQUIRES_HUMAN_REVIEW
      V-05: PARTIALLY_VALID → REVIEW (requires human authority)
      V-06: FULLY_STALE → RECOMMEND_RECOMPUTE, sin autoridad humana adicional
      V-07: HUMAN AUTHORITY REQUIRED FOR INVALIDATION
      V-08: READ-ONLY
    """

    def __init__(self, ledger: DerivationLedger):
        self.ledger = ledger

    def evaluate_validity(
        self,
        project_id: str,
        current_refs: Mapping[tuple[str, str], VersionedRef] | None = None,
        observed_change: dict[str, Any] | None = None,
    ) -> ValidityReport:
        """
        Evalúa la validez de todas las derivaciones del proyecto.

        Fase 1: Para cada DerivationRecord, ejecuta integrity_checks.
        Fase 2: Agrega resultados por output.

        NO invalida automáticamente. Solo reporta.
        """
        if current_refs is None:
            current_refs = {}

        # ──────────────────────────────────────────────
        # FASE 1: Validez por derivación
        # ──────────────────────────────────────────────

        derivation_validities: list[DerivationValidity] = []
        records = self.ledger.list(project_id)
        checks = self.ledger.integrity_checks(project_id, current_refs)
        checks_by_record: dict[str, list[dict[str, Any]]] = {}
        for check in checks:
            checks_by_record.setdefault(check["record_id"], []).append(check)

        for record in records:
            # H-001 reports missing/version/hash discrepancies. H-003 adds
            # the identity-uncertainty signal when only one side has a hash.
            relevant_checks = list(checks_by_record.get(record.id, ()))
            existing_codes = {c.get("code") for c in relevant_checks}
            for expected in record.inputs:
                current = current_refs.get(expected.key())
                if current is None or current.version != expected.version:
                    continue
                if (expected.content_hash is None) != (current.content_hash is None):
                    if "IDENTITY_UNCERTAIN" not in existing_codes:
                        relevant_checks.append({
                            "record_id": record.id,
                            "reference": expected.to_dict(),
                            "current": current.to_dict(),
                            "code": "IDENTITY_UNCERTAIN",
                        })
                        existing_codes.add("IDENTITY_UNCERTAIN")

            # Determinar estado de la derivación
            state = self._determine_derivation_state(relevant_checks)

            derivation_validities.append(DerivationValidity(
                derivation_id=record.id,
                output=record.output,
                state=state,
                discrepancies=tuple(relevant_checks),
                source_checks=(f"integrity_checks_{record.id}",),
            ))

        # ──────────────────────────────────────────────
        # FASE 2: Situación por artefacto
        # ──────────────────────────────────────────────

        # Agrupar derivaciones por output
        by_output: dict[VersionedRef, list[DerivationValidity]] = {}
        for dv in derivation_validities:
            by_output.setdefault(dv.output, []).append(dv)

        artifact_validities: list[ArtifactValidity] = []

        for output, dvs in by_output.items():
            # Agregar estados
            state = self._aggregate_derivation_validities(dvs)

            # Resumen
            summary = {
                "totalDerivations": len(dvs),
                "validCount": sum(1 for dv in dvs if dv.state == "VALID"),
                "staleCount": sum(1 for dv in dvs if dv.state == "STALE"),
                "invalidCount": sum(1 for dv in dvs if dv.state == "INVALID"),
                "uncertainCount": sum(1 for dv in dvs if dv.state == "UNCERTAIN"),
            }

            # Recomendación
            recommendation = self._generate_recommendation(state)

            artifact_validities.append(ArtifactValidity(
                artifact_ref=output,
                state=state,
                derivation_validities=tuple(dvs),
                summary=summary,
                recommendation=recommendation,
            ))

        # Metadata
        analysis_metadata = {
            "totalDerivationsEvaluated": len(derivation_validities),
            "totalArtifactsEvaluated": len(artifact_validities),
            "identityUncertaintyCount": sum(
                1 for dv in derivation_validities
                if dv.state == "UNCERTAIN"
            ),
        }

        return ValidityReport(
            contract_version=1,
            observed_change=observed_change,
            derivation_validities=tuple(derivation_validities),
            artifact_validities=tuple(artifact_validities),
            analysis_metadata=analysis_metadata,
            read_only=True,
        )

    def _determine_derivation_state(self, checks: list[dict[str, Any]]) -> DerivationValidityState:
        """
        Determina el estado de una derivación basándose en integrity_checks.

        Reglas:
          - Si hay MISSING_DEPENDENCY → INVALID
          - Si hay IDENTITY_UNCERTAIN → UNCERTAIN
          - Si hay VERSION_MISMATCH o CONTENT_HASH_MISMATCH → STALE
          - Si no hay checks → VALID
        """
        if not checks:
            return "VALID"

        codes = {c.get("code") for c in checks}

        # V-04: INVALID si hay MISSING_DEPENDENCY
        if "MISSING_DEPENDENCY" in codes:
            return "INVALID"

        # V-03: UNCERTAIN si hay IDENTITY_UNCERTAIN
        if "IDENTITY_UNCERTAIN" in codes or "IDENTITY_UNVERIFIABLE" in codes:
            return "UNCERTAIN"

        # STALE si hay VERSION_MISMATCH o CONTENT_HASH_MISMATCH
        if "VERSION_MISMATCH" in codes or "CONTENT_HASH_MISMATCH" in codes:
            return "STALE"

        return "VALID"

    def _aggregate_derivation_validities(self, dvs: list[DerivationValidity]) -> ArtifactValidityState:
        """
        Agrega los estados de múltiples derivaciones para un mismo output.

        Reglas:
          V-02: ONE STALE DERIVATION ≠ STALE ARTIFACT
          V-03: UNCERTAIN → REQUIRES_HUMAN_REVIEW
          V-04: INVALID → REQUIRES_HUMAN_REVIEW
          V-05: PARTIALLY_VALID → REVIEW (requires human authority)
          V-06: FULLY_STALE → RECOMMEND_RECOMPUTE, sin autoridad humana adicional
        """
        counts = {
            "VALID": sum(1 for dv in dvs if dv.state == "VALID"),
            "STALE": sum(1 for dv in dvs if dv.state == "STALE"),
            "INVALID": sum(1 for dv in dvs if dv.state == "INVALID"),
            "UNCERTAIN": sum(1 for dv in dvs if dv.state == "UNCERTAIN"),
        }

        # V-03: UNCERTAIN → REQUIRES_HUMAN_REVIEW
        if counts["UNCERTAIN"] > 0:
            return "REQUIRES_HUMAN_REVIEW"

        # V-04: INVALID → REQUIRES_HUMAN_REVIEW
        if counts["INVALID"] > 0:
            return "REQUIRES_HUMAN_REVIEW"

        # V-02: al menos una VALID → PARTIALLY_VALID o FULLY_VALID
        if counts["VALID"] > 0:
            return "FULLY_VALID" if counts["VALID"] == len(dvs) else "PARTIALLY_VALID"

        # Todas son STALE
        return "FULLY_STALE" if counts["STALE"] == len(dvs) else "PARTIALLY_STALE"

    def _generate_recommendation(self, state: ArtifactValidityState) -> dict[str, Any]:
        """
        Genera una recomendación basada en el estado del artefacto.

        Reglas:
          V-05: PARTIALLY_VALID → REVIEW (requires human authority)
          V-06: FULLY_STALE → RECOMMEND_RECOMPUTE, sin autoridad humana adicional
          V-03/V-04: REQUIRES_HUMAN_REVIEW → REQUIRES_HUMAN_AUTHORITY
        """
        if state == "FULLY_VALID":
            return {
                "action": "NO_ACTION",
                "reason": "All derivations are valid",
                "requiresHumanAuthority": False,
            }

        if state == "PARTIALLY_VALID":
            return {
                "action": "REVIEW",
                "reason": "At least one derivation is valid, but others are stale",
                "requiresHumanAuthority": True,
            }

        if state == "FULLY_STALE":
            return {
                "action": "RECOMPUTE",
                "reason": "All derivations are stale",
                "requiresHumanAuthority": False,
            }

        if state == "PARTIALLY_STALE":
            return {
                "action": "REVIEW",
                "reason": "Some derivations are stale",
                "requiresHumanAuthority": True,
            }

        if state == "REQUIRES_HUMAN_REVIEW":
            return {
                "action": "REVIEW",
                "reason": "Identity uncertainty or invalid dependencies detected",
                "requiresHumanAuthority": True,
            }

        return {
            "action": "REVIEW",
            "reason": "Unknown state",
            "requiresHumanAuthority": True,
        }


__all__ = [
    "DerivationValidity",
    "ArtifactValidity",
    "ValidityReport",
    "ValidityAnalyzer",
]
