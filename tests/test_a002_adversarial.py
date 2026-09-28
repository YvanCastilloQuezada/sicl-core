from __future__ import annotations

import pytest

from sicl.a002 import A002H005Gate, EvidenceRef, KnowledgeItem, KnowledgeState, SufficiencyEngine, SufficiencyRequest, SufficiencyStatus, requirements_for
from sicl.domain import SpatialScope

OP = "preliminary building massing"
REQ = requirements_for(OP)


def e(eid, statement="verified", project="P", scale=SpatialScope.EDIFICACION, jurisdiction="Trujillo"):
    return EvidenceRef.from_statement(eid, statement, "OFFICIAL", project, scale=scale, jurisdiction=jurisdiction)


def k(field, state, value, refs=(), scale=SpatialScope.EDIFICACION, jurisdiction="Trujillo", reason=""):
    return KnowledgeItem(field, value, state, tuple(refs), scale, jurisdiction, None, 1, reason)


def complete(project="P"):
    evidence = [
        e("site", project=project, scale=SpatialScope.PARCELA_SITIO),
        e("program", project=project), e("area", project=project), e("orientation", project=project, scale=SpatialScope.PARCELA_SITIO),
        e("jurisdiction", project=project, scale=SpatialScope.DISTRITO_CIUDAD), e("height", project=project), e("preferences", project=project),
    ]
    knowledge = [
        k("site_geometry", KnowledgeState.KNOWN, "site", ("site",), SpatialScope.PARCELA_SITIO),
        k("program", KnowledgeState.KNOWN, "program", ("program",)), k("target_floor_area", KnowledgeState.KNOWN, 1000, ("area",)),
        k("orientation", KnowledgeState.OBSERVED, "north", ("orientation",), SpatialScope.PARCELA_SITIO),
        k("jurisdiction", KnowledgeState.KNOWN, "Trujillo", ("jurisdiction",), SpatialScope.DISTRITO_CIUDAD),
        k("height_limit", KnowledgeState.KNOWN, 12, ("height",)), k("budget", KnowledgeState.MISSING, None),
        k("client_preferences", KnowledgeState.KNOWN, "patio", ("preferences",)),
    ]
    return evidence, knowledge


def req(knowledge, evidence, project="P", allow=False, operation=OP, scale=SpatialScope.EDIFICACION, jurisdiction="Trujillo"):
    return SufficiencyRequest(project, operation, tuple(knowledge), REQ, tuple(evidence), scale, "conceptual", jurisdiction, allow)


def test_null_empty_and_whitespace_fields_cannot_be_known():
    evidence, knowledge = complete()
    bad = list(knowledge)
    bad[1] = k("program", KnowledgeState.KNOWN, None, ("program",))
    result = SufficiencyEngine().evaluate(req(bad, evidence))
    assert result.overall_status is not SufficiencyStatus.SUFFICIENT


def test_wrong_type_does_not_bypass_missing_height():
    evidence, knowledge = complete()
    bad = list(knowledge)
    bad[5] = k("height_limit", KnowledgeState.KNOWN, {"height": "12m"}, ("height",))
    result = SufficiencyEngine().evaluate(req(bad, evidence))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "height_limit" in result.unknown


def test_stale_evidence_version_is_not_silently_preferred():
    evidence, knowledge = complete()
    stale = evidence
    bad = list(knowledge)
    bad[5] = k("height_limit", KnowledgeState.KNOWN, 12, ("height-v2",))
    result = SufficiencyEngine().evaluate(req(bad, stale))
    assert result.overall_status is not SufficiencyStatus.SUFFICIENT


def test_wrong_operation_result_cannot_pass_gate():
    evidence, knowledge = complete()
    result = SufficiencyEngine().evaluate(req(knowledge, evidence))
    other = req(knowledge, evidence, operation="construction documents")
    assert not A002H005Gate.check(other, result).permitted


def test_wrong_scale_result_cannot_pass_gate():
    evidence, knowledge = complete()
    result = SufficiencyEngine().evaluate(req(knowledge, evidence))
    other = req(knowledge, evidence, scale=SpatialScope.PARCELA_SITIO)
    assert not A002H005Gate.check(other, result).permitted


def test_cross_project_result_cannot_pass_gate():
    evidence, knowledge = complete("P")
    result = SufficiencyEngine().evaluate(req(knowledge, evidence, project="P"))
    other_evidence, other_knowledge = complete("Q")
    other = req(other_knowledge, other_evidence, project="Q")
    assert not A002H005Gate.check(other, result).permitted


def test_manual_status_mutation_is_impossible_on_frozen_result():
    evidence, knowledge = complete()
    result = SufficiencyEngine().evaluate(req(knowledge, evidence))
    with pytest.raises(Exception):
        result.overall_status = SufficiencyStatus.SUFFICIENT


def test_assumed_disguised_as_known_without_provenance_is_rejected():
    evidence, knowledge = complete()
    bad = list(knowledge)
    bad[5] = k("height_limit", KnowledgeState.KNOWN, 12, ())
    result = SufficiencyEngine().evaluate(req(bad, evidence))
    assert result.overall_status is not SufficiencyStatus.SUFFICIENT
    assert "height_limit" in result.unknown


def test_partial_evidence_cannot_satisfy_all_requirements():
    evidence, knowledge = complete()
    partial = evidence[:2]
    result = SufficiencyEngine().evaluate(req(knowledge, partial))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert result.blocking_items


def test_conflicting_source_is_not_resolved_by_order():
    evidence, knowledge = complete()
    evidence = evidence + [e("height-b", "height 20m", project="P")]
    knowledge = list(knowledge) + [k("height_limit", KnowledgeState.KNOWN, 20, ("height-b",))]
    first = SufficiencyEngine().evaluate(req(knowledge, evidence))
    second = SufficiencyEngine().evaluate(req(list(reversed(knowledge)), list(reversed(evidence))))
    assert first.overall_status is SufficiencyStatus.CONFLICTING
    assert first.to_dict() == second.to_dict()


def test_conditionally_sufficient_requires_explicit_policy_for_gate():
    evidence, knowledge = complete()
    knowledge = list(knowledge)
    knowledge[3] = k("orientation", KnowledgeState.ASSUMED, "north", (), SpatialScope.PARCELA_SITIO, reason="temporary design assumption")
    no_policy = req(knowledge, evidence, allow=False)
    result = SufficiencyEngine().evaluate(no_policy)
    assert result.overall_status is SufficiencyStatus.CONDITIONALLY_SUFFICIENT
    assert not A002H005Gate.check(no_policy, result).permitted
    with_policy = req(knowledge, evidence, allow=True)
    result2 = SufficiencyEngine().evaluate(with_policy)
    assert A002H005Gate.check(with_policy, result2).permitted


def test_human_question_is_not_generic():
    evidence, knowledge = complete()
    bad = list(knowledge)
    bad[5] = k("height_limit", KnowledgeState.UNKNOWN, None, ())
    result = SufficiencyEngine().evaluate(req(bad, evidence))
    assert result.questions_for_human
    assert "Provide more information" not in result.questions_for_human[0]
    assert "height_limit" in result.questions_for_human[0]


def test_h005_executor_not_called_for_conflicting_result():
    evidence, knowledge = complete()
    evidence.append(e("height-b", "height 20m"))
    knowledge.append(k("height_limit", KnowledgeState.KNOWN, 20, ("height-b",)))
    result = SufficiencyEngine().evaluate(req(knowledge, evidence))
    with pytest.raises(PermissionError):
        A002H005Gate.execute_if_permitted(req(knowledge, evidence), result, lambda: pytest.fail("bypass"))


def test_malformed_evidence_hash_fails_closed_at_construction():
    with pytest.raises(ValueError):
        EvidenceRef("fake", "authoritative", "OFFICIAL", "0" * 64, "P")
