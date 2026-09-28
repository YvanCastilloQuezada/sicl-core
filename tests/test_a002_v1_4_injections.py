from __future__ import annotations
import pytest
from sicl.a002 import (ApplicabilityStatus, EvidenceRef, EvidenceVerificationLevel, HumanAuthorityRef, KnowledgeItem, KnowledgeState, OperationRequirement, PolicyIdentity, SufficiencyEngine, SufficiencyRequest, SufficiencyStatus, compute_evaluation_id, EvaluationIdentityPayload)

def ev(project="P", field="x"):
    return EvidenceRef.from_statement("E-"+field, "verified "+field, "USER", project)

def req(field="x", **kw):
    return OperationRequirement(field, (KnowledgeState.KNOWN, KnowledgeState.OBSERVED, KnowledgeState.ASSUMED), True, reason="required", **kw)

def request(item, evidence=(), **kw):
    return SufficiencyRequest("P", "op", (item,), (req(item.field, **kw),), tuple(evidence))

def test_declared_known_without_valid_provenance_is_observed_and_blocked():
    result = SufficiencyEngine().evaluate(request(KnowledgeItem("x", "value", KnowledgeState.KNOWN)))
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "x" in result.observed and "EVIDENCE" in " ".join(result.reason_codes)

def test_policy_identity_is_structured_and_serialized():
    policy = PolicyIdentity("policy", 1, "a" * 64, "test")
    result = SufficiencyEngine().evaluate(SufficiencyRequest("P", "op", (KnowledgeItem("x", "v", KnowledgeState.KNOWN),), (req(),), (), policy=policy))
    assert result.policy == policy
    assert result.to_dict()["policy"]["policyId"] == "policy"

def test_evaluation_identity_is_reproducible_and_canonical():
    item = KnowledgeItem("x", "v", KnowledgeState.KNOWN)
    r1 = SufficiencyEngine().evaluate(request(item))
    r2 = SufficiencyEngine().evaluate(request(item))
    assert r1.evaluation_id == r2.evaluation_id and len(r1.evaluation_id) == 64
    assert r1.evaluation_id == compute_evaluation_id(EvaluationIdentityPayload("P", r1.request_fingerprint, "op", 1, "op"))

def test_human_authority_requirement_blocks_without_reference():
    evidence = ev()
    item = KnowledgeItem("x", "v", KnowledgeState.KNOWN, (evidence.evidence_id,))
    r = SufficiencyEngine().evaluate(request(item, [evidence], require_human_authority=True))
    assert r.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "HUMAN_AUTHORITY_REQUIRED" in r.reason_codes
    authority = HumanAuthorityRef("actor", "APPROVAL", "2026-09-27T00:00:00Z", "REF-1")
    r2 = SufficiencyEngine().evaluate(SufficiencyRequest("P", "op", (item,), (req(require_human_authority=True),), (evidence,), human_authority_ref=authority))
    assert r2.human_authority_ref == authority

def test_conditional_reasons_distinguish_assumed_blocking():
    item = KnowledgeItem("x", "assumed", KnowledgeState.ASSUMED, reason="client assumption")
    r = SufficiencyEngine().evaluate(SufficiencyRequest("P", "op", (item,), (req(allow_assumed=True),), (), policy_allow_assumptions=False))
    assert r.overall_status is SufficiencyStatus.INSUFFICIENT
    assert "ASSUMED_BLOCKING" in r.conditional_reasons

def test_conflicting_applicability_is_preserved():
    item = KnowledgeItem("x", "v", KnowledgeState.KNOWN, applicability=ApplicabilityStatus.CONFLICTING)
    r = SufficiencyEngine().evaluate(request(item, [ev()], applicability_required=True))
    assert r.overall_status is SufficiencyStatus.CONFLICTING
    assert "x" in r.conflicting

def test_evidence_verification_level_is_explicit_and_bounded():
    evidence = ev()
    item = KnowledgeItem("x", "v", KnowledgeState.KNOWN, (evidence.evidence_id,))
    r = SufficiencyEngine().evaluate(request(item, [evidence]))
    assert r.evidence_levels == ((evidence.evidence_id, EvidenceVerificationLevel.CONTENT_HASH_MATCHES_DECLARED.value),)
    assert all(level != EvidenceVerificationLevel.SUPPORT_SEMANTICALLY_VERIFIED.value for _, level in r.evidence_levels)
