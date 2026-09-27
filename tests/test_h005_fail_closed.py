from __future__ import annotations

import pytest

from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.h005 import ExecutionStatus, RecomputationRegistry, SelectiveRecomputationEngine
from sicl.reaction import ActionStatus, ActionType, PlannedAction, ReactionPlan, ReactionPlanner
from sicl.validity import ArtifactValidity, DerivationValidity, ValidityAnalyzer, ValidityReport


class Store:
    def __init__(self): self.items = []
    def add_event(self, event): self.items.append(event); return event
    def events(self, project_id=None): return [e for e in self.items if project_id is None or e.project_id == project_id]


def record(rid="D1", output=None, input_ref=None, method="m", version="1.0"):
    output = output or VersionedRef("Area", "A", 1)
    input_ref = input_ref or VersionedRef("Geometry", "G", 1)
    return DerivationRecord(rid, output, (input_ref,), method, version, (TypedRelation(output, input_ref, "COMPUTED_FROM", "COMPUTATIONAL"),))


def stale_plan(ledger, project="P", current=None):
    if current is None:
        current = {("Geometry", "G"): VersionedRef("Geometry", "G", 2)}
    return ReactionPlanner().plan_reaction(ValidityAnalyzer(ledger).evaluate_validity(project, current))


def test_review_reject_escalate_blocked_and_requires_authority_never_execute():
    artifact = VersionedRef("Area", "A", 1)
    actions = tuple(PlannedAction(artifact, typ, status, 0, typ.value, authority) for typ, status, authority in (
        (ActionType.REVIEW, ActionStatus.REQUIRES_AUTHORITY, True),
        (ActionType.REJECT, ActionStatus.REQUIRES_AUTHORITY, True),
        (ActionType.ESCALATE, ActionStatus.REQUIRES_AUTHORITY, True),
        (ActionType.ESCALATE, ActionStatus.BLOCKED, True),
        (ActionType.RECOMPUTE, ActionStatus.REQUIRES_AUTHORITY, True),
    ))
    dvs = tuple(DerivationValidity(f"D{i}", artifact, "UNCERTAIN", source_checks=(f"integrity_checks_D{i}",)) for i in range(5))
    av = ArtifactValidity(artifact, "REQUIRES_HUMAN_REVIEW", dvs, {}, {})
    plan = ReactionPlan(validity_report=ValidityReport(artifact_validities=(av,)), planned_actions=actions)
    result = SelectiveRecomputationEngine(DerivationLedger(Store()), RecomputationRegistry()).execute("P", plan, {})
    assert all(item.status is ExecutionStatus.REJECTED for item in result.records)
    assert all("ACTION_NOT_ELIGIBLE" in item.reason for item in result.records)


def test_forged_recompute_against_fully_valid_report_is_blocked():
    store = Store(); ledger = DerivationLedger(store); ledger.record("P", record())
    artifact = VersionedRef("Area", "A", 1)
    dv = DerivationValidity("D1", artifact, "VALID", source_checks=("integrity_checks_D1",))
    av = ArtifactValidity(artifact, "FULLY_VALID", (dv,), {}, {})
    forged = ReactionPlan(validity_report=ValidityReport(artifact_validities=(av,)), planned_actions=(PlannedAction(artifact, ActionType.RECOMPUTE, ActionStatus.PLANNED, 0, "forged", False),))
    result = SelectiveRecomputationEngine(ledger, RecomputationRegistry()).execute("P", forged, {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    assert result.records[0].status is ExecutionStatus.BLOCKED
    assert result.records[0].reason == "STALE_OR_INVALID_PLAN"


def test_missing_dependency_and_identity_uncertainty_fail_closed_at_planning():
    store = Store(); ledger = DerivationLedger(store); ledger.record("P", record(input_ref=VersionedRef("Geometry", "G", 1, "a" * 64)))
    missing = stale_plan(ledger, current={})
    assert missing.planned_actions[0].action_type is ActionType.ESCALATE
    assert missing.planned_actions[0].requires_human_authority is True
    uncertain = stale_plan(ledger, current={("Geometry", "G"): VersionedRef("Geometry", "G", 1)})
    assert uncertain.planned_actions[0].action_type is ActionType.ESCALATE
    assert uncertain.planned_actions[0].requires_human_authority is True
    mismatch = stale_plan(ledger, current={("Geometry", "G"): VersionedRef("Geometry", "G", 1, "b" * 64)})
    assert mismatch.planned_actions[0].action_type is ActionType.RECOMPUTE
    assert mismatch.planned_actions[0].requires_human_authority is False


def test_missing_and_ambiguous_handlers_do_not_execute():
    store = Store(); ledger = DerivationLedger(store); ledger.record("P", record())
    plan = stale_plan(ledger)
    missing = SelectiveRecomputationEngine(ledger, RecomputationRegistry()).execute("P", plan, {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    assert missing.records[0].reason == "HANDLER_NOT_REGISTERED"
    registry = RecomputationRegistry(); registry.register("m", "1.0", lambda *args: record("D2", VersionedRef("Area", "A", 2), VersionedRef("Geometry", "G", 2))); registry.register("m", "1.0", lambda *args: record("D3", VersionedRef("Area", "A", 2), VersionedRef("Geometry", "G", 2)))
    ambiguous = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    assert ambiguous.records[0].reason == "AMBIGUOUS_HANDLER"


def test_malformed_handler_output_and_dependency_race_are_blocked():
    store = Store(); ledger = DerivationLedger(store); ledger.record("P", record())
    plan = stale_plan(ledger)
    registry = RecomputationRegistry(); registry.register("m", "1.0", lambda *args: {"not": "a derivation"})
    malformed = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    assert malformed.records[0].reason == "MALFORMED_HANDLER_OUTPUT"
    registry2 = RecomputationRegistry(); registry2.register("m", "1.0", lambda *args: record("D2", VersionedRef("Area", "A", 2), VersionedRef("Geometry", "G", 1)))
    race = SelectiveRecomputationEngine(ledger, registry2).execute("P", plan, {})
    assert race.records[0].reason == "MISSING_CURRENT_DEPENDENCY"


def test_cross_project_execution_cannot_reuse_other_project_derivation():
    store = Store(); ledger = DerivationLedger(store); ledger.record("P1", record())
    plan = stale_plan(ledger, "P1")
    result = SelectiveRecomputationEngine(ledger, RecomputationRegistry()).execute("P2", plan, {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    assert result.records[0].status is ExecutionStatus.BLOCKED
    assert result.records[0].reason == "DERIVATION_NOT_FOUND"
    assert ledger.list("P2") == []
