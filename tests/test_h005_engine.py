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


def make_record(rid, output, input_ref, method="area_from_geometry", version="1.0", *, assumptions=()):
    return DerivationRecord(rid, output, (input_ref,), method, version, (TypedRelation(output, input_ref, "COMPUTED_FROM", "COMPUTATIONAL"),), assumptions=assumptions)


def make_plan(ledger, project, current):
    report = ValidityAnalyzer(ledger).evaluate_validity(project, current)
    return ReactionPlanner().plan_reaction(report)


@pytest.mark.parametrize("malformed_action", [None, {"actionType": "RECOMPUTE"}, "RECOMPUTE"])
def test_h005_malformed_action_object_returns_blocked_not_crash(malformed_action):
    plan = ReactionPlan(validity_report=ValidityReport(), planned_actions=(malformed_action,))
    result = SelectiveRecomputationEngine(DerivationLedger(Store()), RecomputationRegistry()).execute("P1", plan, {})
    assert len(result.records) == 1
    assert result.records[0].status is ExecutionStatus.BLOCKED
    assert result.records[0].reason == "MALFORMED_PLAN"
    assert result.records[0].artifact_requested == VersionedRef("UNKNOWN", "UNKNOWN", 1)


def test_engine_executes_only_full_stale_recompute_and_records_new_derivation():
    store = Store(); ledger = DerivationLedger(store); registry = RecomputationRegistry()
    old_input = VersionedRef("Geometry", "G", 1, "a" * 64)
    current_input = VersionedRef("Geometry", "G", 2, "b" * 64)
    old_output = VersionedRef("Area", "A", 1)
    ledger.record("P", make_record("D1", old_output, old_input, assumptions=("controlled",)))

    def recompute(project, previous, refs):
        new_output = VersionedRef("Area", "A", 2)
        return make_record("D2", new_output, refs[("Geometry", "G")], assumptions=previous.assumptions)

    registry.register("area_from_geometry", "1.0", recompute)
    plan = make_plan(ledger, "P", {("Geometry", "G"): current_input})
    report = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, {("Geometry", "G"): current_input})
    assert [item.status for item in report.records] == [ExecutionStatus.EXECUTED]
    result = report.records[0]
    assert result.previous_output == old_output
    assert result.new_output == VersionedRef("Area", "A", 2)
    assert len(ledger.list("P")) == 2
    assert [item.id for item in ledger.why("P", result.new_output)] == ["D2"]
    assert result.previous_output == old_output


def test_engine_ignores_fully_valid_artifact():
    store = Store(); ledger = DerivationLedger(store); registry = RecomputationRegistry()
    input_ref = VersionedRef("Geometry", "G", 1, "a" * 64)
    output = VersionedRef("Area", "A", 1)
    ledger.record("P", make_record("D1", output, input_ref))
    plan = make_plan(ledger, "P", {("Geometry", "G"): input_ref})
    assert plan.planned_actions == ()
    result = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, {("Geometry", "G"): input_ref})
    assert result.records == ()


def test_engine_blocks_missing_handler_without_mutating_ledger():
    store = Store(); ledger = DerivationLedger(store); registry = RecomputationRegistry()
    old_input = VersionedRef("Geometry", "G", 1); old_output = VersionedRef("Area", "A", 1)
    ledger.record("P", make_record("D1", old_output, old_input))
    plan = make_plan(ledger, "P", {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    before = list(ledger.list("P"))
    result = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    assert result.records[0].status is ExecutionStatus.BLOCKED
    assert result.records[0].reason == "HANDLER_NOT_REGISTERED"
    assert ledger.list("P") == before


def test_engine_blocks_human_authority_and_forged_review_plan():
    artifact = VersionedRef("Area", "A", 1)
    dv = DerivationValidity("D1", artifact, "UNCERTAIN", source_checks=("integrity_checks_D1",))
    av = ArtifactValidity(artifact, "REQUIRES_HUMAN_REVIEW", (dv,), {}, {})
    plan = ReactionPlan(validity_report=ValidityReport(artifact_validities=(av,)), planned_actions=(PlannedAction(artifact, ActionType.REVIEW, ActionStatus.REQUIRES_AUTHORITY, 0, "review", True),))
    result = SelectiveRecomputationEngine(DerivationLedger(Store()), RecomputationRegistry()).execute("P", plan, {})
    assert result.records[0].status is ExecutionStatus.REJECTED
    assert "ACTION_NOT_ELIGIBLE" in result.records[0].reason


def test_engine_blocks_handler_exception_and_malformed_output():
    store = Store(); ledger = DerivationLedger(store); registry = RecomputationRegistry()
    old_input = VersionedRef("Geometry", "G", 1); old_output = VersionedRef("Area", "A", 1)
    ledger.record("P", make_record("D1", old_output, old_input))
    registry.register("area_from_geometry", "1.0", lambda *args: (_ for _ in ()).throw(RuntimeError("boom")))
    plan = make_plan(ledger, "P", {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    result = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, {("Geometry", "G"): VersionedRef("Geometry", "G", 2)})
    assert result.records[0].status is ExecutionStatus.BLOCKED
    assert result.records[0].reason == "HANDLER_EXCEPTION:RuntimeError"
