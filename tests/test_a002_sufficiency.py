from __future__ import annotations

import pytest

from sicl.a002 import (
    A002H005Gate,
    EvidenceRef,
    KnowledgeItem,
    KnowledgeState,
    OperationRequirement,
    SufficiencyEngine,
    SufficiencyRequest,
    SufficiencyStateStore,
    SufficiencyStatus,
    requirements_for,
)
from sicl.domain import SpatialScope
from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.h005 import ExecutionStatus, RecomputationRegistry, SelectiveRecomputationEngine
from sicl.reaction import ReactionPlanner
from sicl.validity import ValidityAnalyzer

OP = "preliminary building massing"
REQ = requirements_for(OP)


def ev(eid: str, text: str, project: str = "A002-P", scale: SpatialScope | None = None, jurisdiction: str | None = None) -> EvidenceRef:
    return EvidenceRef.from_statement(eid, text, "USER_PROVIDED", project, scale=scale, jurisdiction=jurisdiction)


def item(field: str, state: KnowledgeState, value: object, evidence_id: str | None = None, scale: SpatialScope | None = None, jurisdiction: str | None = None, reason: str = "") -> KnowledgeItem:
    return KnowledgeItem(field, value, state, (evidence_id,) if evidence_id else (), scale, jurisdiction, None, 1, reason)


def base_knowledge(evidence: list[EvidenceRef], *, height: KnowledgeState = KnowledgeState.MISSING, orientation: KnowledgeState = KnowledgeState.KNOWN, project: str = "A002-P") -> tuple[KnowledgeItem, ...]:
    ids = {x.evidence_id for x in evidence}
    return (
        item("site_geometry", KnowledgeState.KNOWN, "site-geometry", "site" if "site" in ids else None, SpatialScope.PARCELA_SITIO),
        item("program", KnowledgeState.KNOWN, "housing", "program" if "program" in ids else None, SpatialScope.EDIFICACION),
        item("target_floor_area", KnowledgeState.KNOWN, 1000, "area" if "area" in ids else None, SpatialScope.EDIFICACION),
        item("orientation", orientation, "north", "orientation" if orientation is not KnowledgeState.ASSUMED and "orientation" in ids else None, SpatialScope.PARCELA_SITIO, reason="client direction" if orientation is KnowledgeState.ASSUMED else ""),
        item("jurisdiction", KnowledgeState.KNOWN, "Trujillo", "jurisdiction" if "jurisdiction" in ids else None, SpatialScope.DISTRITO_CIUDAD, "Trujillo"),
        item("height_limit", height, 12, "height" if height in {KnowledgeState.KNOWN, KnowledgeState.OBSERVED} and "height" in ids else None, SpatialScope.EDIFICACION, "Trujillo"),
        item("budget", KnowledgeState.MISSING, None),
        item("client_preferences", KnowledgeState.KNOWN, "patio", "preferences" if "preferences" in ids else None, SpatialScope.EDIFICACION),
    )


def full_evidence(project: str = "A002-P") -> list[EvidenceRef]:
    return [
        ev("site", "Site geometry surveyed", project, SpatialScope.PARCELA_SITIO),
        ev("program", "Program approved", project, SpatialScope.EDIFICACION),
        ev("area", "Target floor area approved", project, SpatialScope.EDIFICACION),
        ev("orientation", "Orientation observed", project, SpatialScope.PARCELA_SITIO),
        ev("jurisdiction", "Jurisdiction is Trujillo", project, SpatialScope.DISTRITO_CIUDAD, "Trujillo"),
        ev("height", "Height limit is 12m", project, SpatialScope.EDIFICACION, "Trujillo"),
        ev("preferences", "Client preference is patio", project, SpatialScope.EDIFICACION),
    ]


def request(knowledge, evidence, *, allow=False, project="A002-P", scale=SpatialScope.EDIFICACION):
    return SufficiencyRequest(project, OP, tuple(knowledge), REQ, tuple(evidence), scale, "conceptual", "Trujillo", allow)


def test_missing_height_is_insufficient_and_asks_specific_question():
    evidence = full_evidence()
    result = SufficiencyEngine().evaluate(request(base_knowledge(evidence), evidence))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "height_limit" in result.blocking_items
    assert any("height_limit" in question and "WHY REQUIRED" in question for question in result.questions_for_human)


def test_all_required_known_is_sufficient():
    evidence = full_evidence()
    knowledge = base_knowledge(evidence, orientation=KnowledgeState.OBSERVED, height=KnowledgeState.KNOWN)
    result = SufficiencyEngine().evaluate(request(knowledge, evidence))
    assert result.overall_status is SufficiencyStatus.SUFFICIENT
    assert result.blocking_items == ()


def test_assumption_is_explicit_and_conditionally_sufficient():
    evidence = full_evidence()
    knowledge = base_knowledge(evidence, orientation=KnowledgeState.ASSUMED, height=KnowledgeState.KNOWN)
    result = SufficiencyEngine().evaluate(request(knowledge, evidence))
    assert result.overall_status is SufficiencyStatus.CONDITIONALLY_SUFFICIENT
    assert "orientation" in result.assumed
    assert result.assumptions_used


def test_unknown_never_promotes_to_known_without_evidence():
    evidence = full_evidence()
    knowledge = list(base_knowledge(evidence, height=KnowledgeState.KNOWN))
    knowledge[5] = item("height_limit", KnowledgeState.KNOWN, 12, "not-present", SpatialScope.EDIFICACION, "Trujillo")
    result = SufficiencyEngine().evaluate(request(knowledge, evidence))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "height_limit" in result.unknown
    assert "height_limit" not in result.known


def test_wrong_project_evidence_is_not_valid_provenance():
    evidence = full_evidence()
    knowledge = base_knowledge(evidence, height=KnowledgeState.KNOWN)
    wrong = [ev(x.evidence_id, x.statement, "OTHER-P", x.scale, x.jurisdiction) if x.evidence_id == "height" else x for x in evidence]
    result = SufficiencyEngine().evaluate(request(knowledge, wrong))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "height_limit" in result.unknown


def test_wrong_scale_evidence_does_not_satisfy_requirement():
    evidence = full_evidence()
    knowledge = list(base_knowledge(evidence, height=KnowledgeState.KNOWN))
    knowledge[5] = item("height_limit", KnowledgeState.KNOWN, 12, "height", SpatialScope.PARCELA_SITIO, "Trujillo")
    result = SufficiencyEngine().evaluate(request(knowledge, evidence))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "height_limit" in result.missing


def test_conflicting_authoritative_values_never_choose_arbitrarily():
    evidence = full_evidence() + [ev("height-2", "Height limit is 18m", scale=SpatialScope.EDIFICACION, jurisdiction="Trujillo")]
    knowledge = list(base_knowledge(evidence, height=KnowledgeState.KNOWN))
    knowledge.extend([item("height_limit", KnowledgeState.KNOWN, 18, "height-2", SpatialScope.EDIFICACION, "Trujillo")])
    result = SufficiencyEngine().evaluate(request(knowledge, evidence))
    assert result.overall_status is SufficiencyStatus.CONFLICTING
    assert "height_limit" in result.conflicting


def test_regulation_available_without_jurisdiction_does_not_become_applicable():
    evidence = [x for x in full_evidence() if x.evidence_id != "jurisdiction"]
    knowledge = list(base_knowledge(evidence, height=KnowledgeState.KNOWN))
    knowledge[4] = item("jurisdiction", KnowledgeState.UNKNOWN, "unknown", None, SpatialScope.DISTRITO_CIUDAD)
    result = SufficiencyEngine().evaluate(request(knowledge, evidence))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "jurisdiction" in result.blocking_items


def test_determinism_is_independent_of_input_order():
    evidence = full_evidence()
    knowledge = base_knowledge(evidence, height=KnowledgeState.KNOWN)
    first = SufficiencyEngine().evaluate(request(knowledge, evidence))
    second = SufficiencyEngine().evaluate(request(tuple(reversed(knowledge)), tuple(reversed(evidence))))
    assert first.to_dict() == second.to_dict()


def test_multiscale_ontology_evaluates_object_space_building_site_city_region_country():
    scales = (SpatialScope.OBJETO, SpatialScope.ESPACIO, SpatialScope.EDIFICACION, SpatialScope.PARCELA_SITIO, SpatialScope.DISTRITO_CIUDAD, SpatialScope.REGION, SpatialScope.PAIS)
    evidence = tuple(ev(f"scale-{scale.value}", f"verified {scale.value}", scale=scale) for scale in scales)
    knowledge = tuple(item(f"field-{index}", KnowledgeState.KNOWN, scale.value, f"scale-{scale.value}", scale) for index, scale in enumerate(scales))
    requirements = tuple(OperationRequirement(f"field-{index}", (KnowledgeState.KNOWN,), True, (scale,), reason=f"requires {scale.value}") for index, scale in enumerate(scales))
    result = SufficiencyEngine().evaluate(SufficiencyRequest("A002-P", "multiscale audit", knowledge, requirements, evidence, None, "audit", None))
    assert result.overall_status is SufficiencyStatus.SUFFICIENT
    assert set(result.coverage) == {f"field-{index}" for index in range(len(scales))}


def test_gate_permits_sufficient_and_calls_h005_once():
    evidence = full_evidence()
    req = request(base_knowledge(evidence, height=KnowledgeState.KNOWN), evidence)
    result = SufficiencyEngine().evaluate(req)
    calls = []
    value = A002H005Gate.execute_if_permitted(req, result, lambda: calls.append("executed") or "ok")
    assert value == "ok"
    assert calls == ["executed"]


def test_gate_blocks_insufficient_before_h005():
    evidence = full_evidence()
    req = request(base_knowledge(evidence), evidence)
    result = SufficiencyEngine().evaluate(req)
    with pytest.raises(PermissionError, match="INSUFFICIENT"):
        A002H005Gate.execute_if_permitted(req, result, lambda: pytest.fail("H005 must not execute"))


def test_sufficient_a002_permits_real_h005_recomputation():
    evidence = full_evidence()
    req = request(base_knowledge(evidence, height=KnowledgeState.KNOWN), evidence)
    a002_result = SufficiencyEngine().evaluate(req)
    store = type("Store", (), {"__init__": lambda self: setattr(self, "items", []), "add_event": lambda self, event: (self.items.append(event) or event), "events": lambda self, project_id=None: [event for event in self.items if project_id is None or event.project_id == project_id]})()
    ledger = DerivationLedger(store)
    registry = RecomputationRegistry()
    old_input = VersionedRef("Geometry", "G", 1, "a" * 64)
    current_input = VersionedRef("Geometry", "G", 2, "b" * 64)
    old_output = VersionedRef("Area", "A", 1)
    previous = DerivationRecord("D1", old_output, (old_input,), "area_from_geometry", "1.0", (TypedRelation(old_output, old_input, "COMPUTED_FROM", "COMPUTATIONAL"),))
    ledger.record("A002-P", previous)
    registry.register("area_from_geometry", "1.0", lambda project, record, refs: DerivationRecord("D2", VersionedRef("Area", "A", 2), (refs[("Geometry", "G")],), record.method, record.method_version, (TypedRelation(VersionedRef("Area", "A", 2), refs[("Geometry", "G")], "COMPUTED_FROM", "COMPUTATIONAL"),)))
    h005 = SelectiveRecomputationEngine(ledger, registry)
    plan = ReactionPlanner().plan_reaction(ValidityAnalyzer(ledger).evaluate_validity("A002-P", {("Geometry", "G"): current_input}))
    report = A002H005Gate.execute_if_permitted(req, a002_result, lambda: h005.execute("A002-P", plan, {("Geometry", "G"): current_input}))
    assert report.records[0].status is ExecutionStatus.EXECUTED


def test_gate_rejects_stale_result():
    evidence = full_evidence()
    req = request(base_knowledge(evidence, height=KnowledgeState.KNOWN), evidence)
    result = SufficiencyEngine().evaluate(req)
    changed = request(base_knowledge(evidence, height=KnowledgeState.KNOWN), evidence, project="NEW-P")
    decision = A002H005Gate.check(changed, result)
    assert not decision.permitted
    assert decision.reason == "A002_RESULT_CONTEXT_MISMATCH"


def test_persistence_preserves_insufficient_then_sufficient_after_reopen(tmp_path):
    evidence = full_evidence()
    engine = SufficiencyEngine()
    t0 = engine.evaluate(request(base_knowledge(evidence), evidence))
    t1 = engine.evaluate(request(base_knowledge(evidence, height=KnowledgeState.KNOWN), evidence))
    path = tmp_path / "a002.jsonl"
    store = SufficiencyStateStore(path)
    store.append(t0)
    store.append(t1)
    store.close()
    reopened = SufficiencyStateStore.reopen(path)
    rows = reopened.list_results("A002-P")
    assert [row["overallStatus"] for row in rows] == ["INSUFFICIENT", "SUFFICIENT"]
    assert len(rows) == 2


def test_evidence_hash_mismatch_rejected():
    with pytest.raises(ValueError, match="hash"):
        EvidenceRef("e", "statement", "USER_PROVIDED", "bad", "A002-P")
