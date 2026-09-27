"""Tests TDD para H-003 Validity / Invalidation.

Estos tests DEBEN FALLAR inicialmente hasta que H-003 esté implementado.
"""
import pytest
from sicl.derivation import (
    DerivationLedger, DerivationRecord, VersionedRef, TypedRelation,
    DerivationValidationError
)
from sicl.validity import ValidityAnalyzer
from sicl.domain import Event


class MockEventStore:
    def __init__(self):
        self.events_list = []

    def add_event(self, event: Event) -> Event:
        self.events_list.append(event)
        return event

    def events(self, project_id: str | None = None) -> list[Event]:
        if project_id is None:
            return self.events_list
        return [e for e in self.events_list if e.project_id == project_id]



@pytest.fixture
def ledger():
    store = MockEventStore()
    return DerivationLedger(store)


@pytest.fixture
def analyzer(ledger):
    return ValidityAnalyzer(ledger)


class TestValidityAnalyzer_Basic:
    """Tests básicos de ValidityAnalyzer"""

    def test_empty_project_returns_empty_report(self, analyzer):
        """Proyecto vacío → reporte vacío"""
        report = analyzer.evaluate_validity("empty-project")

        assert report.contract_version == 1
        assert len(report.derivation_validities) == 0
        assert len(report.artifact_validities) == 0
        assert report.read_only is True

    def test_single_valid_derivation(self, ledger, analyzer):
        """Derivación con inputs válidos → VALID"""
        project_id = "test-project"

        # Registrar derivación: A1@1 ← G1@3
        record = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3, "a" * 64),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3, "a" * 64),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)

        # Inputs actuales coinciden con los esperados
        current_refs = {
            ("Geometry", "G1"): VersionedRef("Geometry", "G1", 3, "a" * 64)
        }

        report = analyzer.evaluate_validity(project_id, current_refs)

        assert len(report.derivation_validities) == 1
        assert report.derivation_validities[0].state == "VALID"

        assert len(report.artifact_validities) == 1
        assert report.artifact_validities[0].state == "FULLY_VALID"
        assert report.artifact_validities[0].recommendation["action"] == "NO_ACTION"


class TestValidityAnalyzer_V02:
    """V-02: ONE STALE DERIVATION ≠ STALE ARTIFACT"""

    def test_output_with_two_derivations_one_stale_one_valid(self, ledger, analyzer):
        """
        A1@1 tiene dos derivaciones:
          R1: A1@1 ← G1@3 (G1 cambia a G1@4 → R1 se vuelve STALE)
          R2: A1@1 ← G2@1 (G2 no cambia → R2 sigue VALID)

        Resultado: PARTIALLY_VALID (no FULLY_STALE)
        """
        project_id = "test-project"

        # Derivación 1: A1@1 ← G1@3
        record1 = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3, "a" * 64),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3, "a" * 64),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )

        # Derivación 2: A1@1 ← G2@1
        record2 = DerivationRecord(
            id="R2",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G2", 1, "b" * 64),),
            method="M2", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G2", 1, "b" * 64),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )

        ledger.record(project_id, record1)
        ledger.record(project_id, record2)

        # G1 cambió a versión 4, G2 sigue en versión 1
        current_refs = {
            ("Geometry", "G1"): VersionedRef("Geometry", "G1", 4, "a" * 64),
            ("Geometry", "G2"): VersionedRef("Geometry", "G2", 1, "b" * 64),
        }

        report = analyzer.evaluate_validity(project_id, current_refs)

        # R1 debe ser STALE (G1 cambió)
        r1_validity = next(dv for dv in report.derivation_validities if dv.derivation_id == "R1")
        assert r1_validity.state == "STALE"

        # R2 debe ser VALID (G2 no cambió)
        r2_validity = next(dv for dv in report.derivation_validities if dv.derivation_id == "R2")
        assert r2_validity.state == "VALID"

        # A1@1 debe ser PARTIALLY_VALID (no FULLY_STALE)
        artifact_validity = report.artifact_validities[0]
        assert artifact_validity.state == "PARTIALLY_VALID"
        assert artifact_validity.summary["validCount"] == 1
        assert artifact_validity.summary["staleCount"] == 1
        assert artifact_validity.recommendation["action"] == "REVIEW"


class TestValidityAnalyzer_V03:
    """V-03: UNCERTAIN → REQUIRES_HUMAN_REVIEW"""

    def test_derivation_with_uncertain_input(self, ledger, analyzer):
        """
        A1@1 ← G1@3, pero G1@3 tiene identityStatus = UNCERTAIN

        Resultado: REQUIRES_HUMAN_REVIEW
        """
        project_id = "test-project"

        # Derivación: A1@1 ← G1@3 (sin hash en el registro)
        record = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),  # SIN hash
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)

        # Current con hash (asimetría → IDENTITY_UNCERTAIN)
        current_refs = {
            ("Geometry", "G1"): VersionedRef("Geometry", "G1", 3, "a" * 64)
        }

        report = analyzer.evaluate_validity(project_id, current_refs)

        # R1 debe ser UNCERTAIN
        r1_validity = report.derivation_validities[0]
        assert r1_validity.state == "UNCERTAIN"

        # A1@1 debe ser REQUIRES_HUMAN_REVIEW
        artifact_validity = report.artifact_validities[0]
        assert artifact_validity.state == "REQUIRES_HUMAN_REVIEW"
        assert artifact_validity.recommendation["requiresHumanAuthority"] is True


class TestValidityAnalyzer_V04:
    """V-04: INVALID → REQUIRES_HUMAN_REVIEW"""

    def test_derivation_with_missing_dependency(self, ledger, analyzer):
        """
        A1@1 ← G1@3, pero G1@3 no existe en current_refs

        Resultado: REQUIRES_HUMAN_REVIEW
        """
        project_id = "test-project"

        record = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)

        # G1@3 no existe en current_refs
        current_refs = {}

        report = analyzer.evaluate_validity(project_id, current_refs)

        # R1 debe ser INVALID
        r1_validity = report.derivation_validities[0]
        assert r1_validity.state == "INVALID"

        # A1@1 debe ser REQUIRES_HUMAN_REVIEW
        artifact_validity = report.artifact_validities[0]
        assert artifact_validity.state == "REQUIRES_HUMAN_REVIEW"
        assert artifact_validity.recommendation["requiresHumanAuthority"] is True


class TestValidityAnalyzer_V06:
    """V-06: FULLY_STALE → RECOMMEND_RECOMPUTE"""

    def test_all_derivations_stale(self, ledger, analyzer):
        """
        A1@1 ← G1@3, G1 cambia a G1@4

        Resultado: FULLY_STALE, recommend RECOMPUTE
        """
        project_id = "test-project"

        record = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)

        # G1 cambió a versión 4
        current_refs = {
            ("Geometry", "G1"): VersionedRef("Geometry", "G1", 4)
        }

        report = analyzer.evaluate_validity(project_id, current_refs)

        # R1 debe ser STALE
        r1_validity = report.derivation_validities[0]
        assert r1_validity.state == "STALE"

        # A1@1 debe ser FULLY_STALE
        artifact_validity = report.artifact_validities[0]
        assert artifact_validity.state == "FULLY_STALE"
        assert artifact_validity.recommendation["action"] == "RECOMPUTE"
        assert artifact_validity.recommendation["requiresHumanAuthority"] is False


class TestValidityAnalyzer_V08:
    """V-08: READ-ONLY"""

    def test_h003_does_not_modify_ledger(self, ledger, analyzer):
        """H-003 no modifica DerivationLedger"""
        project_id = "test-project"

        record = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)

        ledger_before = ledger.list(project_id)

        # Ejecutar H-003
        analyzer.evaluate_validity(project_id)

        ledger_after = ledger.list(project_id)

        # Ledger no debe haber cambiado
        assert ledger_after == ledger_before

    def test_source_checks_is_tuple_of_names_not_characters(self, ledger, analyzer):
        """RT-78: sourceChecks conserva nombres completos de checks."""
        project_id = "source-checks-contract"
        record = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)

        report = analyzer.evaluate_validity(
            project_id,
            {("Geometry", "G1"): VersionedRef("Geometry", "G1", 4)},
        )
        source_checks = report.derivation_validities[0].source_checks
        assert source_checks == ("integrity_checks_R1",)
        assert all(isinstance(check, str) and len(check) > 1 for check in source_checks)
        assert report.derivation_validities[0].to_dict()["sourceChecks"] == ["integrity_checks_R1"]


class TestValidityAnalyzer_Integration:
    """Tests de integración con RT-A (múltiples derivaciones)"""

    def test_rt_a_multiple_derivations_aggregated_correctly(self, ledger, analyzer):
        """
        RT-A: A1@1 tiene dos derivaciones legítimas (R1 y R2).
        Ambas deben evaluarse y agregarse correctamente.
        """
        project_id = "test-project"

        # Derivación 1: A1@1 ← G1@3
        record1 = DerivationRecord(
            id="R1",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3, "a" * 64),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3, "a" * 64),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )

        # Derivación 2: A1@1 ← G2@1
        record2 = DerivationRecord(
            id="R2",
            output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G2", 1, "b" * 64),),
            method="M2", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G2", 1, "b" * 64),
                relation_type="COMPUTED_FROM",
                relation_domain="COMPUTATIONAL"
            ),)
        )

        ledger.record(project_id, record1)
        ledger.record(project_id, record2)

        # Ambos inputs válidos
        current_refs = {
            ("Geometry", "G1"): VersionedRef("Geometry", "G1", 3, "a" * 64),
            ("Geometry", "G2"): VersionedRef("Geometry", "G2", 1, "b" * 64),
        }

        report = analyzer.evaluate_validity(project_id, current_refs)

        # Ambas derivaciones deben ser VALID
        assert len(report.derivation_validities) == 2
        assert all(dv.state == "VALID" for dv in report.derivation_validities)

        # A1@1 debe ser FULLY_VALID
        artifact_validity = report.artifact_validities[0]
        assert artifact_validity.state == "FULLY_VALID"
        assert artifact_validity.summary["totalDerivations"] == 2
        assert artifact_validity.summary["validCount"] == 2
