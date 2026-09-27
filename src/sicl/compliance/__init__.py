"""ARKI Compliance Validator — Pilar VIII (experimental, no certificación legal).

Reglas 41–43 se validan contra JSON Schema y reglas semánticas explícitas.
La proveniencia implementada aquí es integridad por hash, no firma criptográfica.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PENDING_REVIEW = "PENDING_REVIEW"


@dataclass(frozen=True)
class ComplianceResult:
    rule_id: str
    status: ComplianceStatus
    message: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"ruleId": self.rule_id, "status": self.status.value, "message": self.message, "details": self.details or {}}


class ComplianceValidator:
    """Valida contratos de gobernanza del Pilar VIII (experimental)."""

    def __init__(self, schemas_dir: Path | None = None):
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent.parent.parent.parent / "docs" / "schemas"
        self.schemas_dir = Path(schemas_dir)
        self._load_schemas()

    def _load_schemas(self) -> None:
        try:
            with open(self.schemas_dir / "domain_profile.json", encoding="utf-8") as f:
                self.domain_profile_schema = json.load(f)
            with open(self.schemas_dir / "provenance_signature.json", encoding="utf-8") as f:
                self.provenance_signature_schema = json.load(f)
            with open(self.schemas_dir / "ethical_impact_assessment.json", encoding="utf-8") as f:
                self.ethical_impact_assessment_schema = json.load(f)
        except FileNotFoundError as exc:
            raise RuntimeError(f"Schemas not found in {self.schemas_dir}.") from exc

    @staticmethod
    def _schema_error(schema: dict[str, Any], payload: dict[str, Any]) -> str | None:
        errors = sorted(Draft7Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
        if not errors:
            return None
        error = errors[0]
        location = ".".join(str(part) for part in error.path) or "payload"
        return f"Schema validation failed at {location}: {error.message}"

    def validate_domain_profile(self, profile: dict[str, Any]) -> ComplianceResult:
        required_fields = ["domain_id", "risk_tier", "hard_constraints", "aia_required"]
        missing_fields = [field for field in required_fields if field not in profile]
        if missing_fields:
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, f"Missing required fields: {missing_fields}", {"missing_fields": missing_fields})
        if profile.get("risk_tier") not in ["MINIMAL", "LIMITED", "HIGH", "UNACCEPTABLE"]:
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, f"Invalid risk_tier: {profile.get('risk_tier')}", {"invalid_tier": profile.get("risk_tier")})
        schema_error = self._schema_error(self.domain_profile_schema, profile)
        if schema_error:
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, schema_error)
        valid_tiers = ["MINIMAL", "LIMITED", "HIGH", "UNACCEPTABLE"]
        if profile["risk_tier"] not in valid_tiers:
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, f"Invalid risk_tier: {profile['risk_tier']}")
        if profile["risk_tier"] in ["HIGH", "LIMITED"] and not profile["aia_required"]:
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, f"risk_tier={profile['risk_tier']} requires aia_required=True")
        if profile["risk_tier"] == "UNACCEPTABLE":
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, "risk_tier=UNACCEPTABLE: operation blocked by compliance policy")
        return ComplianceResult("RULE_41", ComplianceStatus.COMPLIANT, f"Domain profile valid for risk_tier={profile['risk_tier']}", {"risk_tier": profile["risk_tier"], "aia_required": profile["aia_required"]})

    def validate_provenance_hash(self, output_content: str | bytes, provenance: dict[str, Any]) -> ComplianceResult:
        required_fields = ["generator_id", "timestamp", "content_hash", "hash_algorithm", "domain_profile_ref"]
        missing_fields = [field for field in required_fields if field not in provenance]
        if missing_fields:
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, f"Missing required provenance hash fields: {missing_fields}", {"missing_fields": missing_fields})
        content_hash = provenance.get("content_hash", "")
        if len(content_hash) != 64 or not all(char in "0123456789abcdef" for char in content_hash):
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, "Invalid content_hash: must be 64 hex characters", {"content_hash_length": len(content_hash)})
        schema_error = self._schema_error(self.provenance_signature_schema, provenance)
        if schema_error:
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, schema_error)
        if isinstance(output_content, str):
            output_content = output_content.encode("utf-8")
        computed_hash = hashlib.sha256(output_content).hexdigest()
        if computed_hash != content_hash:
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, "Content hash mismatch: output has been tampered with", {"computed_hash": computed_hash, "provided_hash": content_hash})
        return ComplianceResult("RULE_42", ComplianceStatus.COMPLIANT, "Content hash valid; no cryptographic signature is asserted", {"generator_id": provenance["generator_id"], "timestamp": provenance["timestamp"], "algorithm": provenance["hash_algorithm"]})

    def validate_provenance_signature(self, output_content: str | bytes, provenance: dict[str, Any]) -> ComplianceResult:
        """Compatibility alias; validates a provenance hash, not a signature."""
        return self.validate_provenance_hash(output_content, provenance)

    def validate_ethical_impact_assessment(self, output_ref: str, aia: dict[str, Any], risk_tier: str) -> ComplianceResult:
        if risk_tier == "MINIMAL":
            return ComplianceResult("RULE_43", ComplianceStatus.COMPLIANT, "AIA not required for MINIMAL risk tier", {"risk_tier": risk_tier})
        required_fields = ["assessment_id", "target_output_ref", "bias_declaration", "harm_assessment_score", "authority_approval_id", "status"]
        missing_fields = [field for field in required_fields if field not in aia]
        if missing_fields:
            return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"AIA required for risk_tier={risk_tier} but missing fields: {missing_fields}", {"missing_fields": missing_fields, "risk_tier": risk_tier})
        if not 0 <= aia.get("harm_assessment_score", 0) <= 100:
            return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"harm_assessment_score {aia.get('harm_assessment_score')} out of range [0, 100]", {"harm_score": aia.get("harm_assessment_score")})
        schema_error = self._schema_error(self.ethical_impact_assessment_schema, aia)
        if schema_error:
            return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, schema_error, {"risk_tier": risk_tier})
        if risk_tier in ["LIMITED", "HIGH"]:
            if aia["status"] != "APPROVED":
                return ComplianceResult("RULE_43", ComplianceStatus.PENDING_REVIEW, f"AIA status is {aia['status']}, not APPROVED", {"aia_status": aia["status"], "risk_tier": risk_tier})
            if not aia["authority_approval_id"]:
                return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, "AIA is APPROVED but missing authority_approval_id")
            if aia["target_output_ref"] != output_ref:
                return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"AIA target_output_ref mismatch: expected {output_ref}, got {aia['target_output_ref']}")
            return ComplianceResult("RULE_43", ComplianceStatus.COMPLIANT, f"AIA approved for risk_tier={risk_tier}", {"assessment_id": aia["assessment_id"], "harm_score": aia["harm_assessment_score"], "authority_approval_id": aia["authority_approval_id"]})
        return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"Unexpected risk_tier: {risk_tier}")

    def validate_full_compliance(self, domain_profile: dict[str, Any], output_content: str | bytes, provenance: dict[str, Any], output_ref: str, aia: dict[str, Any] | None = None) -> list[ComplianceResult]:
        result_41 = self.validate_domain_profile(domain_profile)
        results = [result_41]
        if result_41.status == ComplianceStatus.NON_COMPLIANT:
            return results
        results.append(self.validate_provenance_hash(output_content, provenance))
        risk_tier = domain_profile["risk_tier"]
        if aia is None and risk_tier in ["LIMITED", "HIGH"]:
            results.append(ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"AIA required for risk_tier={risk_tier} but not provided", {"risk_tier": risk_tier}))
        elif aia is not None:
            results.append(self.validate_ethical_impact_assessment(output_ref, aia, risk_tier))
        return results


__all__ = ["ComplianceStatus", "ComplianceResult", "ComplianceValidator"]
