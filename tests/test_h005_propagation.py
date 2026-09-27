from __future__ import annotations

from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.h005 import ExecutionStatus, RecomputationRegistry, SelectiveRecomputationEngine
from sicl.reaction import ActionStatus, ActionType, PlannedAction, ReactionPlan, ReactionPlanner
from sicl.validity import ArtifactValidity, DerivationValidity, ValidityAnalyzer, ValidityReport


class Store:
    def __init__(self): self.items = []
    def add_event(self, event): self.items.append(event); return event
    def events(self, project_id=None): return [e for e in self.items if project_id is None or e.project_id == project_id]


def rec(rid, output, input_ref, method):
    return DerivationRecord(rid, output, (input_ref,), method, "1.0", (TypedRelation(output, input_ref, "COMPUTED_FROM", "COMPUTATIONAL"),))


def test_three_level_chain_recomputes_in_topological_order_without_stale_inputs():
    store = Store(); ledger = DerivationLedger(store); registry = RecomputationRegistry()
    g1, g2 = VersionedRef("Geometry", "G", 1), VersionedRef("Geometry", "G", 2)
    a1, q1, c1 = VersionedRef("Area", "A", 1), VersionedRef("Quantity", "Q", 1), VersionedRef("Cost", "C", 1)
    ledger.record("P", rec("D-A1", a1, g1, "area"))
    ledger.record("P", rec("D-Q1", q1, a1, "quantity"))
    ledger.record("P", rec("D-C1", c1, q1, "cost"))
    calls = []

    def handler(method, output):
        def run(project, previous, refs):
            calls.append((method, refs.copy()))
            key = next(key for key in refs if key == previous.inputs[0].key())
            current = refs[key]
            return rec(f"{method}-v2", VersionedRef(output.entity_type, output.entity_id, 2), current, method)
        return run

    registry.register("area", "1.0", handler("area", a1))
    registry.register("quantity", "1.0", handler("quantity", q1))
    registry.register("cost", "1.0", handler("cost", c1))
    current = {("Geometry", "G"): g2, ("Area", "A"): VersionedRef("Area", "A", 2), ("Quantity", "Q"): VersionedRef("Quantity", "Q", 2)}
    plan = ReactionPlanner().plan_reaction(ValidityAnalyzer(ledger).evaluate_validity("P", current))
    assert [item.artifact_ref.entity_id for item in plan.planned_actions] == ["A", "Q", "C"]
    report = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, current)
    assert [item.status for item in report.records] == [ExecutionStatus.EXECUTED] * 3
    assert [item.artifact_requested.entity_id for item in report.records] == ["A", "Q", "C"]
    assert [item.new_output.version for item in report.records] == [2, 2, 2]
    assert [method for method, _ in calls] == ["area", "quantity", "cost"]
    assert calls[1][1][("Area", "A")].version == 2
    assert calls[2][1][("Quantity", "Q")].version == 2


def test_cycle_is_blocked_and_never_executes():
    store = Store(); ledger = DerivationLedger(store); registry = RecomputationRegistry()
    area, quantity = VersionedRef("Area", "A", 1), VersionedRef("Quantity", "Q", 1)
    dv_a = DerivationValidity("D-A", area, "STALE", discrepancies=({"reference": quantity.to_dict(), "code": "VERSION_MISMATCH"},), source_checks=("integrity_checks_D-A",))
    dv_q = DerivationValidity("D-Q", quantity, "STALE", discrepancies=({"reference": area.to_dict(), "code": "VERSION_MISMATCH"},), source_checks=("integrity_checks_D-Q",))
    report = ValidityReport(artifact_validities=(ArtifactValidity(area, "FULLY_STALE", (dv_a,), {}, {}), ArtifactValidity(quantity, "FULLY_STALE", (dv_q,), {}, {})))
    plan = ReactionPlanner().plan_reaction(report)
    assert all(item.status is ActionStatus.BLOCKED for item in plan.planned_actions)
    result = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, {})
    assert all(item.status is ExecutionStatus.REJECTED for item in result.records)
    assert store.items == []


def test_replaying_a_plan_after_success_is_blocked_as_stale():
    store = Store(); ledger = DerivationLedger(store); registry = RecomputationRegistry()
    old_input = VersionedRef("Geometry", "G", 1); current_input = VersionedRef("Geometry", "G", 2); old_output = VersionedRef("Area", "A", 1)
    ledger.record("P", rec("D1", old_output, old_input, "area"))
    registry.register("area", "1.0", lambda project, previous, refs: rec("D2", VersionedRef("Area", "A", 2), refs[("Geometry", "G")], "area"))
    plan = ReactionPlanner().plan_reaction(ValidityAnalyzer(ledger).evaluate_validity("P", {("Geometry", "G"): current_input}))
    engine = SelectiveRecomputationEngine(ledger, registry)
    first = engine.execute("P", plan, {("Geometry", "G"): current_input})
    second = engine.execute("P", plan, {("Geometry", "G"): current_input})
    assert first.records[0].status is ExecutionStatus.EXECUTED
    assert second.records[0].status is ExecutionStatus.BLOCKED
    assert second.records[0].reason == "STALE_PLAN"
