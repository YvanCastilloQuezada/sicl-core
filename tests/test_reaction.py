"""Tests TDD para H-004 Reaction Planning."""
import json
import pytest
from sicl.derivation import (
    DerivationLedger, DerivationRecord, VersionedRef, TypedRelation,
    DerivationValidationError
)
from sicl.validity import (
    ArtifactValidity,
    DerivationValidity,
    ValidityAnalyzer,
    ValidityReport,
)
from sicl.reaction import ReactionPlanner, ActionType, ActionStatus
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
def validity_analyzer(ledger):
    return ValidityAnalyzer(ledger)


@pytest.fixture
def planner():
    return ReactionPlanner()


class TestReactionPlanner_Basic:
    def test_empty_validity_report_returns_empty_plan(self, planner, validity_analyzer, ledger):
        validity_report = validity_analyzer.evaluate_validity("empty-project")
        plan = planner.plan_reaction(validity_report)
        assert plan.contract_version == 1
        assert len(plan.planned_actions) == 0
        assert plan.read_only is True

    def test_fully_valid_artifact_no_action(self, ledger, validity_analyzer, planner):
        project_id = "test-project"
        record = DerivationRecord(
            id="R1", output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3, "a" * 64),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3, "a" * 64),
                relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)
        current_refs = {("Geometry", "G1"): VersionedRef("Geometry", "G1", 3, "a" * 64)}
        validity_report = validity_analyzer.evaluate_validity(project_id, current_refs)
        plan = planner.plan_reaction(validity_report)
        assert len(plan.planned_actions) == 0


class TestReactionPlanner_R02:
    def test_fully_stale_artifact_plans_recompute(self, ledger, validity_analyzer, planner):
        project_id = "test-project"
        record = DerivationRecord(
            id="R1", output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),
            method="M1", method_version="1",
            relations=(TypedRelation(
                from_ref=VersionedRef("Area", "A1", 1),
                to_ref=VersionedRef("Geometry", "G1", 3),
                relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"
            ),)
        )
        ledger.record(project_id, record)
        current_refs = {("Geometry", "G1"): VersionedRef("Geometry", "G1", 4)}
        validity_report = validity_analyzer.evaluate_validity(project_id, current_refs)
        plan = planner.plan_reaction(validity_report)
        assert len(plan.planned_actions) == 1
        action = plan.planned_actions[0]
        assert action.action_type == ActionType.RECOMPUTE
        assert action.requires_human_authority is False
        assert action.status == ActionStatus.PLANNED


class TestReactionPlanner_R05:
    def test_partially_valid_artifact_plans_review(self, ledger, validity_analyzer, planner):
        project_id = "test-project"
        record1 = DerivationRecord(
            id="R1", output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),
            method="M1", method_version="1",
            relations=(TypedRelation(from_ref=VersionedRef("Area", "A1", 1), to_ref=VersionedRef("Geometry", "G1", 3), relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"),)
        )
        record2 = DerivationRecord(
            id="R2", output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G2", 1, "b" * 64),),
            method="M2", method_version="1",
            relations=(TypedRelation(from_ref=VersionedRef("Area", "A1", 1), to_ref=VersionedRef("Geometry", "G2", 1, "b" * 64), relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"),)
        )
        ledger.record(project_id, record1)
        ledger.record(project_id, record2)
        current_refs = {
            ("Geometry", "G1"): VersionedRef("Geometry", "G1", 4),
            ("Geometry", "G2"): VersionedRef("Geometry", "G2", 1, "b" * 64),
        }
        validity_report = validity_analyzer.evaluate_validity(project_id, current_refs)
        plan = planner.plan_reaction(validity_report)
        assert len(plan.planned_actions) == 1
        action = plan.planned_actions[0]
        assert action.action_type == ActionType.REVIEW
        assert action.requires_human_authority is True


class TestReactionPlanner_R04:
    def test_uncertain_artifact_plans_escalate(self, ledger, validity_analyzer, planner):
        project_id = "test-project"
        record = DerivationRecord(
            id="R1", output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),),
            method="M1", method_version="1",
            relations=(TypedRelation(from_ref=VersionedRef("Area", "A1", 1), to_ref=VersionedRef("Geometry", "G1", 3), relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"),)
        )
        ledger.record(project_id, record)
        current_refs = {("Geometry", "G1"): VersionedRef("Geometry", "G1", 3, "a" * 64)}
        validity_report = validity_analyzer.evaluate_validity(project_id, current_refs)
        plan = planner.plan_reaction(validity_report)
        assert len(plan.planned_actions) == 1
        action = plan.planned_actions[0]
        assert action.action_type == ActionType.ESCALATE
        assert action.requires_human_authority is True


class TestReactionPlanner_R07:
    def test_dependencies_processed_first(self, ledger, validity_analyzer, planner):
        project_id = "test-project"
        ledger.record(project_id, DerivationRecord(
            id="R1", output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),), method="M1", method_version="1",
            relations=(TypedRelation(from_ref=VersionedRef("Area", "A1", 1), to_ref=VersionedRef("Geometry", "G1", 3), relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"),)
        ))
        ledger.record(project_id, DerivationRecord(
            id="R2", output=VersionedRef("Quantity", "Q1", 1),
            inputs=(VersionedRef("Area", "A1", 1),), method="M2", method_version="1",
            relations=(TypedRelation(from_ref=VersionedRef("Quantity", "Q1", 1), to_ref=VersionedRef("Area", "A1", 1), relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"),)
        ))
        current_refs = {("Geometry", "G1"): VersionedRef("Geometry", "G1", 4)}
        validity_report = validity_analyzer.evaluate_validity(project_id, current_refs)
        plan = planner.plan_reaction(validity_report)
        a1_action = next(a for a in plan.planned_actions if a.artifact_ref.entity_id == "A1")
        q1_action = next(a for a in plan.planned_actions if a.artifact_ref.entity_id == "Q1")
        assert a1_action.priority < q1_action.priority


class TestReactionPlanner_R09:
    def test_planner_does_not_modify_ledger(self, ledger, validity_analyzer, planner):
        project_id = "test-project"
        record = DerivationRecord(
            id="R1", output=VersionedRef("Area", "A1", 1),
            inputs=(VersionedRef("Geometry", "G1", 3),), method="M1", method_version="1",
            relations=(TypedRelation(from_ref=VersionedRef("Area", "A1", 1), to_ref=VersionedRef("Geometry", "G1", 3), relation_type="COMPUTED_FROM", relation_domain="COMPUTATIONAL"),)
        )
        ledger.record(project_id, record)
        ledger_before = ledger.list(project_id)
        current_refs = {("Geometry", "G1"): VersionedRef("Geometry", "G1", 4)}
        validity_report = validity_analyzer.evaluate_validity(project_id, current_refs)
        planner.plan_reaction(validity_report)
        ledger_after = ledger.list(project_id)
        assert ledger_after == ledger_before


@pytest.mark.parametrize("state", ["FULLY_STALE", "PARTIALLY_VALID"])
def test_h003_h004_agree_on_human_authority_per_state(planner, state):
    artifact = VersionedRef("Area", "A1", 1)
    derivation = DerivationValidity("R1", artifact, state)
    artifact_validity = ArtifactValidity(
        artifact_ref=artifact,
        state=state,
        derivation_validities=(derivation,),
        summary={},
        recommendation={"requiresHumanAuthority": True},
    )
    report = ValidityReport(artifact_validities=(artifact_validity,))
    action = planner.plan_reaction(report).planned_actions[0]
    assert action.requires_human_authority is (state == "PARTIALLY_VALID")


def test_h004_malformed_discrepancy_escalates(planner):
    artifact = VersionedRef("Area", "A1", 1)
    derivation = DerivationValidity(
        "R1",
        artifact,
        "STALE",
        discrepancies=({"reference": {"id": "G1"}, "code": "VERSION_MISMATCH"},),
    )
    artifact_validity = ArtifactValidity(
        artifact_ref=artifact,
        state="FULLY_STALE",
        derivation_validities=(derivation,),
        summary={},
        recommendation={"requiresHumanAuthority": True},
    )
    report = ValidityReport(artifact_validities=(artifact_validity,))
    action = planner.plan_reaction(report).planned_actions[0]
    assert action.status == ActionStatus.BLOCKED
    assert action.action_type == ActionType.ESCALATE
    assert action.reason == "MALFORMED_DISCREPANCY"
    assert action.requires_human_authority is True


def test_h004_cycle_reason_names_blocked_artifacts(planner):
    """RT-77: el bloqueo de ciclo debe ser explicable y trazable."""
    area = VersionedRef("Area", "A1", 1)
    quantity = VersionedRef("Quantity", "Q1", 1)
    a_derivation = DerivationValidity(
        "RA", area, "FULLY_STALE",
        discrepancies=({"reference": quantity.to_dict(), "code": "VERSION_MISMATCH"},),
    )
    q_derivation = DerivationValidity(
        "RQ", quantity, "FULLY_STALE",
        discrepancies=({"reference": area.to_dict(), "code": "VERSION_MISMATCH"},),
    )
    report = ValidityReport(artifact_validities=(
        ArtifactValidity(area, "FULLY_STALE", (a_derivation,), {}, {"action": "RECOMPUTE"}),
        ArtifactValidity(quantity, "FULLY_STALE", (q_derivation,), {}, {"action": "RECOMPUTE"}),
    ))
    actions = planner.plan_reaction(report).planned_actions
    assert len(actions) == 2
    assert all(action.status == ActionStatus.BLOCKED for action in actions)
    assert all(action.action_type == ActionType.ESCALATE for action in actions)
    assert all("Dependency cycle detected:" in action.reason for action in actions)
    assert all(action.blocked_by for action in actions)


def test_h003_h004_canonical_dicts_are_deterministic(planner):
    """RT-87: los reportes públicos de H-003/H-004 son reproducibles."""
    report = ValidityReport()
    first_report = json.dumps(report.canonical_dict(), sort_keys=True, separators=(",", ":"))
    second_report = json.dumps(report.canonical_dict(), sort_keys=True, separators=(",", ":"))
    assert first_report == second_report

    first_plan = planner.plan_reaction(report)
    first_plan_json = json.dumps(first_plan.canonical_dict(), sort_keys=True, separators=(",", ":"))
    second_plan_json = json.dumps(planner.plan_reaction(report).canonical_dict(), sort_keys=True, separators=(",", ":"))
    assert first_plan_json == second_plan_json
