from __future__ import annotations

from pathlib import Path

from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.impact import ChangeKind, ImpactAnalyzer, ImpactChange
from sicl.h005 import ExecutionStatus, RecomputationRegistry, SelectiveRecomputationEngine
from sicl.reaction import ReactionPlanner
from sicl.repository import SQLiteRepository
from sicl.validity import ValidityAnalyzer


def rec(rid, output, input_ref):
    return DerivationRecord(rid, output, (input_ref,), "area", "1.0", (TypedRelation(output, input_ref, "COMPUTED_FROM", "COMPUTATIONAL"),), assumptions=("synthetic",))


def test_h001_to_h005_e2e_survives_close_reopen(tmp_path: Path):
    db = tmp_path / "arki-f1.sqlite"
    project = "ARKI-F1-FIXTURE"
    g1 = VersionedRef("Geometry", "G", 1, "a" * 64)
    g2 = VersionedRef("Geometry", "G", 2, "b" * 64)
    a1 = VersionedRef("Area", "A", 1)
    a2 = VersionedRef("Area", "A", 2)
    repo = SQLiteRepository(db)
    ledger = DerivationLedger(repo)
    ledger.record(project, rec("D1", a1, g1))
    current_refs = {g2.key(): g2}

    impact = ImpactAnalyzer(ledger).analyze_change(project, ImpactChange(g1, g2, ChangeKind.VERSION_UPGRADED))
    assert impact.fail_closed_reason == "NO_AUTOMATIC_RETROACTIVE_IMPACT"
    validity = ValidityAnalyzer(ledger).evaluate_validity(project, current_refs, observed_change={"kind": "VERSION_UPGRADED"})
    plan = ReactionPlanner().plan_reaction(validity)
    assert plan.planned_actions[0].artifact_ref == a1
    assert plan.planned_actions[0].requires_human_authority is False

    registry = RecomputationRegistry()
    registry.register("area", "1.0", lambda p, previous, refs: rec("D2", a2, refs[g2.key()]))
    execution = SelectiveRecomputationEngine(ledger, registry).execute(project, plan, current_refs)
    assert execution.records[0].status is ExecutionStatus.EXECUTED
    assert execution.records[0].new_output == a2
    repo.close()

    reopened = SQLiteRepository(db)
    reopened_ledger = DerivationLedger(reopened)
    records = reopened_ledger.list(project)
    assert [item.id for item in records] == ["D1", "D2"]
    assert reopened_ledger.why(project, a2)[0].id == "D2"
    explanation = reopened_ledger.explain(project, a2)
    assert explanation["output"] == a2.to_dict()
    assert [item["id"] for item in explanation["records"]] == ["D2"]
    dependency_checks = reopened_ledger.dependency_checks(project, {g2.key(): 2})
    assert {item["record_id"] for item in dependency_checks} == {"D1"}
    integrity_checks = reopened_ledger.integrity_checks(project, {g2.key(): g2})
    assert {item["record_id"] for item in integrity_checks} == {"D1"}
    assert reopened.events(project)[0].type == "DERIVATION_RECORDED"
    reopened.close()
