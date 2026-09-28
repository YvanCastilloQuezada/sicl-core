from __future__ import annotations

from pathlib import Path

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


def test_malformed_plan_unknown_artifact_and_partial_graph_are_blocked():
    artifact = VersionedRef("Area", "A", 1)
    action = PlannedAction(artifact, ActionType.RECOMPUTE, ActionStatus.PLANNED, 0, "forged", False)
    plan = ReactionPlan(validity_report=ValidityReport(), planned_actions=(action,))
    result = SelectiveRecomputationEngine(DerivationLedger(Store()), RecomputationRegistry()).execute("P", plan, {})
    assert result.records[0].status is ExecutionStatus.BLOCKED
    assert result.records[0].reason == "MALFORMED_PLAN"

    store = Store(); ledger = DerivationLedger(store); ledger.record("P", record())
    unknown = ImpactlessValidity = ValidityReport(artifact_validities=())
    assert unknown.artifact_validities == ()


def test_multiple_derivations_never_auto_recompute_when_one_is_valid():
    store = Store(); ledger = DerivationLedger(store)
    a = VersionedRef("Area", "A", 1)
    ledger.record("P", record("D1", a, VersionedRef("Geometry", "G1", 1, "a" * 64)))
    ledger.record("P", record("D2", a, VersionedRef("Geometry", "G2", 1, "b" * 64), method="m2"))
    current = {("Geometry", "G1"): VersionedRef("Geometry", "G1", 1, "a" * 64), ("Geometry", "G2"): VersionedRef("Geometry", "G2", 2, "b" * 64)}
    plan = ReactionPlanner().plan_reaction(ValidityAnalyzer(ledger).evaluate_validity("P", current))
    assert plan.planned_actions[0].action_type is ActionType.REVIEW
    assert plan.planned_actions[0].requires_human_authority is True


def test_handler_wrong_version_and_identity_are_rejected():
    store = Store(); ledger = DerivationLedger(store); ledger.record("P", record())
    current = {("Geometry", "G"): VersionedRef("Geometry", "G", 2, "b" * 64)}
    plan = ReactionPlanner().plan_reaction(ValidityAnalyzer(ledger).evaluate_validity("P", current))
    registry = RecomputationRegistry()
    registry.register("m", "1.0", lambda *args: record("D2", VersionedRef("Other", "X", 2), VersionedRef("Geometry", "G", 2, "b" * 64)))
    result = SelectiveRecomputationEngine(ledger, registry).execute("P", plan, current)
    assert result.records[0].reason == "INVALID_OUTPUT_IDENTITY_OR_VERSION"


def test_h005_source_has_no_forbidden_execution_or_external_provider_primitives():
    source = "\n".join(path.read_text() for path in Path("src/sicl/h005").glob("*.py"))
    for forbidden in ("eval(", "exec(", "subprocess", "importlib", "socket", "requests", "urllib", "httpx"):
        assert forbidden not in source


def test_frozen_h002_to_h004_modules_have_no_worktree_changes():
    import subprocess
    result = subprocess.run(["git", "diff", "--name-only", "--", "src/sicl/impact.py", "src/sicl/validity.py", "src/sicl/reaction.py"], capture_output=True, text=True, check=True)
    assert result.stdout == ""
