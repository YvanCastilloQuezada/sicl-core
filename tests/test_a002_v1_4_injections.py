from __future__ import annotations

import pytest

from sicl.a002 import (
    ApplicabilityDeclaration,
    ApplicabilityStatus,
    EvaluationIdentityPayload,
    EvidenceRef,
    EvidenceVerificationLevel,
    HumanAuthorityRef,
    ItemAssessment,
    KnowledgeItem,
    KnowledgeState,
    OperationRequirement,
    PolicyIdentity,
    SufficiencyEngine,
    SufficiencyRequest,
    SufficiencyStatus,
    compute_evaluation_id,
)


def ev(project: str = "P", field: str = "x") -> EvidenceRef:
    return EvidenceRef.from_statement("E-" + field, "verified " + field, "USER", project)


def req(field: str = "x", **kw) -> OperationRequirement:
    return OperationRequirement(
        field,
        (KnowledgeState.KNOWN, KnowledgeState.OBSERVED, KnowledgeState.ASSUMED),
        True,
        reason="required",
        **kw,
    )


def request(item, evidence=(), **kw):
    return SufficiencyRequest("P", "op", (item,), (req(item.field, **kw),), tuple(evidence))


def test_declared_known_without_evidence_downgrades_to_unknown():
    result = SufficiencyEngine().evaluate(
        request(KnowledgeItem("x", "value", KnowledgeState.KNOWN))
    )
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    a = next(a for a in result.assessments if a.field == "x")
    assert a.declared_state is KnowledgeState.KNOWN
    assert a.effective_state is KnowledgeState.UNKNOWN
    assert a.downgrade_reason == "KNOWN_WITHOUT_EVIDENCE"
    # RT-V14-08: observed but NOT unknown.
    assert "x" in result.unknown
    assert "x" not in result.observed


def test_policy_resolved_automatically_when_not_provided():
    result = SufficiencyEngine().evaluate(
        request(KnowledgeItem("x", "v", KnowledgeState.KNOWN))
    )
    assert result.policy is not None
    assert result.policy.policy_id == "a002-op"
    assert len(result.policy.policy_fingerprint) == 64


def test_policy_identity_preserved_when_explicit():
    policy = PolicyIdentity("custom-policy", 2, "b" * 64, "test")
    result = SufficiencyEngine().evaluate(
        SufficiencyRequest(
            "P", "op",
            (KnowledgeItem("x", "v", KnowledgeState.KNOWN),),
            (req(),),
            (),
            policy=policy,
        )
    )
    assert result.policy == policy


def test_evaluation_identity_uses_policy_not_operation_twice():
    evidence = ev()
    item = KnowledgeItem("x", "v", KnowledgeState.KNOWN, (evidence.evidence_id,))
    r = SufficiencyEngine().evaluate(request(item, [evidence]))
    assert len(r.evaluation_id) == 64
    payload = EvaluationIdentityPayload(
        project_id=r.project_id,
        snapshot_fingerprint=r.request_fingerprint,
        operation=r.operation,
        policy_id=r.policy.policy_id,
        policy_version=r.policy.policy_version,
    )
    assert r.evaluation_id == compute_evaluation_id(payload)


def test_human_authority_requirement_blocks_without_reference():
    evidence = ev()
    item = KnowledgeItem("x", "v", KnowledgeState.KNOWN, (evidence.evidence_id,))
    r = SufficiencyEngine().evaluate(request(item, [evidence], require_human_authority=True))
    assert r.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "HUMAN_AUTHORITY_REQUIRED" in r.reason_codes
    authority = HumanAuthorityRef("actor", "APPROVAL", "2026-09-27T00:00:00Z", "REF-1")
    r2 = SufficiencyEngine().evaluate(
        SufficiencyRequest(
            "P", "op",
            (item,),
            (req(require_human_authority=True),),
            (evidence,),
            human_authority_ref=authority,
        )
    )
    assert r2.human_authority_ref == authority


def test_conditional_reasons_distinguish_assumed_blocking():
    item = KnowledgeItem("x", "assumed", KnowledgeState.ASSUMED, reason="client assumption")
    r = SufficiencyEngine().evaluate(
        SufficiencyRequest(
            "P", "op",
            (item,),
            (req(allow_assumed=True),),
            (),
            policy_allow_assumptions=False,
        )
    )
    assert r.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "ASSUMED_BLOCKING" in r.conditional_reasons


def test_conflicting_applicability_is_preserved_from_request():
    decl = ApplicabilityDeclaration("x", "PE", "RNE-A010", ApplicabilityStatus.CONFLICTING)
    r = SufficiencyEngine().evaluate(
        SufficiencyRequest(
            "P", "op",
            (KnowledgeItem("x", "v", KnowledgeState.KNOWN),),
            (req(applicability_required=True),),
            (ev(),),
            applicability=(decl,),
        )
    )
    assert r.overall_status is SufficiencyStatus.CONFLICTING
    assert "x" in r.conflicting


def test_evidence_verification_level_is_explicit_and_bounded():
    evidence = ev()
    item = KnowledgeItem("x", "v", KnowledgeState.KNOWN, (evidence.evidence_id,))
    r = SufficiencyEngine().evaluate(request(item, [evidence]))
    assert r.evidence_levels == (
        (evidence.evidence_id, EvidenceVerificationLevel.CONTENT_HASH_MATCHES_DECLARED.value),
    )
    assert all(
        level != EvidenceVerificationLevel.SUPPORT_SEMANTICALLY_VERIFIED.value
        for _, level in r.evidence_levels
    )
