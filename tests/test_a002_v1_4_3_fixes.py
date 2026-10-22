from __future__ import annotations

from sicl.a002 import (
    ApplicabilityDeclaration,
    ApplicabilityStatus,
    EvidenceRef,
    KnowledgeItem,
    KnowledgeState,
    OperationRequirement,
    SufficiencyEngine,
    SufficiencyRequest,
    SufficiencyStatus,
)


def evidence(project: str = "P") -> EvidenceRef:
    return EvidenceRef.from_statement("E-X", "verified x", "USER", project)


def test_required_states_are_enforced():
    ref = evidence()
    request = SufficiencyRequest(
        "P",
        "op",
        (KnowledgeItem("x", "value", KnowledgeState.OBSERVED, (ref.evidence_id,)),),
        (OperationRequirement("x", (KnowledgeState.KNOWN,), True, reason="known required"),),
        (ref,),
    )
    result = SufficiencyEngine().evaluate(request)
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "x" in result.blocking_items
    assert result.effective_state_of("x") is KnowledgeState.OBSERVED
    assert "STATE_NOT_ALLOWED" in result.reason_codes


def test_allowed_required_state_passes():
    ref = evidence()
    request = SufficiencyRequest(
        "P",
        "op",
        (KnowledgeItem("x", "value", KnowledgeState.KNOWN, (ref.evidence_id,)),),
        (OperationRequirement("x", (KnowledgeState.KNOWN,), True),),
        (ref,),
    )
    result = SufficiencyEngine().evaluate(request)
    assert result.overall_status is SufficiencyStatus.SUFFICIENT
    assert result.known == ("x",)


def test_foreign_jurisdiction_declaration_does_not_satisfy_requirement():
    ref = evidence()
    request = SufficiencyRequest(
        "P",
        "op",
        (KnowledgeItem("x", "value", KnowledgeState.KNOWN, (ref.evidence_id,)),),
        (OperationRequirement("x", (KnowledgeState.KNOWN,), True, applicability_required=True),),
        (ref,),
        jurisdiction="PE",
        applicability=(
            ApplicabilityDeclaration("x", "US", "R-US", ApplicabilityStatus.ESTABLISHED),
        ),
    )
    result = SufficiencyEngine().evaluate(request)
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert result.effective_state_of("x") is KnowledgeState.UNKNOWN
    assert "APPLICABILITY_UNKNOWN" in result.reason_codes


def test_matching_jurisdiction_declaration_satisfies_requirement():
    ref = evidence()
    request = SufficiencyRequest(
        "P",
        "op",
        (KnowledgeItem("x", "value", KnowledgeState.KNOWN, (ref.evidence_id,)),),
        (OperationRequirement("x", (KnowledgeState.KNOWN,), True, applicability_required=True),),
        (ref,),
        jurisdiction="PE",
        applicability=(
            ApplicabilityDeclaration("x", "PE", "RNE-A010", ApplicabilityStatus.ESTABLISHED),
        ),
    )
    result = SufficiencyEngine().evaluate(request)
    assert result.overall_status is SufficiencyStatus.SUFFICIENT
