"""Deterministic A-002 sufficiency engine, v1.4 extensions."""
from __future__ import annotations
from collections import defaultdict
from .model import KnowledgeState, SufficiencyRequest, SufficiencyResult, SufficiencyStatus, ApplicabilityStatus, EvidenceVerificationLevel
from .identity import EvaluationIdentityPayload, compute_evaluation_id

def _valid_value(value): return not (value is None or (isinstance(value,str) and not value.strip()) or isinstance(value,(dict,list,set)))

class SufficiencyEngine:
    def evaluate(self, request: SufficiencyRequest) -> SufficiencyResult:
        if not isinstance(request, SufficiencyRequest): raise TypeError("request must be SufficiencyRequest")
        by_field: dict[str,list] = defaultdict(list)
        for item in request.knowledge: by_field[item.field].append(item)
        known=[]; observed=[]; assumed=[]; unknown=[]; missing=[]; conflicting=[]; blocking=[]; non_blocking=[]; questions=[]; assumptions=[]; evidence=set(); reasons=[]; conditional=[]; levels=[]
        evidence_by_id={ref.evidence_id:ref for ref in request.evidence}
        for requirement in request.requirements:
            if not requirement.applies_to(request.scale,request.context,request.jurisdiction): continue
            allowed=set(requirement.applicable_scales)
            items=[item for item in by_field.get(requirement.field,[]) if (not allowed or item.scale in allowed) and (item.jurisdiction is None or request.jurisdiction is None or item.jurisdiction==request.jurisdiction)]
            if not items:
                missing.append(requirement.field); (blocking if requirement.blocking else non_blocking).append(requirement.field); reasons.append("MISSING_REQUIRED_INPUT" if requirement.blocking else "MISSING_OPTIONAL_INPUT")
                if not requirement.blocking: conditional.append("NON_BLOCKING_MISSING")
                if requirement.blocking: questions.append(f"WHAT IS MISSING: {requirement.field}; WHY REQUIRED: {requirement.reason}; OPERATION: {request.operation}; WHY CANNOT CONTINUE: this blocking requirement has no evidence.")
                continue
            states={item.state for item in items}
            if len(states)>1 and KnowledgeState.CONFLICTING in states or len(items)>1 and len({repr(i.value) for i in items})>1:
                conflicting.append(requirement.field); (blocking if requirement.blocking else non_blocking).append(requirement.field); reasons.append("CONFLICTING_EVIDENCE" if KnowledgeState.CONFLICTING in states else "CONFLICTING_VALUES")
                if not requirement.blocking: conditional.append("NON_BLOCKING_CONFLICTING")
                if requirement.blocking: questions.append(f"WHAT IS MISSING: authoritative resolution for {requirement.field}; WHY REQUIRED: evidence conflicts; OPERATION: {request.operation}; WHY CANNOT CONTINUE: arbitrary selection is unsafe.")
                continue
            item=sorted(items,key=lambda x:x.version)[-1]
            refs=[evidence_by_id[r] for r in item.evidence_refs if r in evidence_by_id]
            evidence.update(item.evidence_refs)
            for ref in refs: levels.append((ref.evidence_id,ref.verification_level().value))
            evidence_valid=bool(item.evidence_refs) and all(ref_id in evidence_by_id and evidence_by_id[ref_id].project_id==request.project_id and (not allowed or evidence_by_id[ref_id].scale in allowed) and (evidence_by_id[ref_id].jurisdiction is None or request.jurisdiction is None or evidence_by_id[ref_id].jurisdiction==request.jurisdiction) for ref_id in item.evidence_refs)
            effective=item.state; reason=""
            if item.state in {KnowledgeState.KNOWN, KnowledgeState.OBSERVED} and not _valid_value(item.value): effective=KnowledgeState.UNKNOWN; reason="INVALID_INPUT_VALUE"
            elif item.state is KnowledgeState.ASSUMED and not item.reason.strip(): effective=KnowledgeState.UNKNOWN; reason="ASSUMED_WITHOUT_REASON"
            elif item.state is KnowledgeState.KNOWN and not evidence_valid:
                effective=KnowledgeState.OBSERVED; reason="KNOWN_WITHOUT_EVIDENCE" if not item.evidence_refs else "EVIDENCE_INVALID"
            if requirement.applicability_required and item.applicability is ApplicabilityStatus.CONFLICTING:
                effective=KnowledgeState.CONFLICTING; conflicting.append(item.field); reasons.append("CONFLICTING_APPLICABILITY")
                if requirement.blocking: questions.append(f"WHAT IS MISSING: applicability arbitration for {item.field}; WHY REQUIRED: normative sources conflict; OPERATION: {request.operation}; WHY CANNOT CONTINUE: applicability is not safely established.")
            elif requirement.applicability_required and item.applicability is ApplicabilityStatus.UNKNOWN:
                effective=KnowledgeState.UNKNOWN; reason=reason or "APPLICABILITY_UNKNOWN"
            if effective is KnowledgeState.KNOWN: known.append(item.field)
            elif effective is KnowledgeState.OBSERVED: observed.append(item.field)
            elif effective is KnowledgeState.ASSUMED:
                assumed.append(item.field); assumptions.append(f"{item.field}: {item.reason}")
                if requirement.blocking: conditional.append("ASSUMED_BLOCKING")
                else: conditional.append("ASSUMED_NON_BLOCKING")
                if not (request.policy_allow_assumptions and requirement.allow_assumed): (blocking if requirement.blocking else non_blocking).append(item.field); reasons.append("ASSUMPTION_NOT_PERMITTED")
            elif effective is KnowledgeState.UNKNOWN: unknown.append(item.field); (blocking if requirement.blocking else non_blocking).append(item.field); reasons.append(reason or "UNKNOWN_INPUT")
            elif effective is KnowledgeState.MISSING: missing.append(item.field); (blocking if requirement.blocking else non_blocking).append(item.field); reasons.append(reason or "MISSING_INPUT")
            elif effective is KnowledgeState.CONFLICTING: conflicting.append(item.field); (blocking if requirement.blocking else non_blocking).append(item.field)
            if reason and effective is KnowledgeState.OBSERVED: unknown.append(item.field); (blocking if requirement.blocking else non_blocking).append(item.field); reasons.append(reason)
            if requirement.blocking and effective in {KnowledgeState.UNKNOWN, KnowledgeState.MISSING, KnowledgeState.OBSERVED}:
                questions.append(f"WHAT IS MISSING: verified {item.field}; WHY REQUIRED: {requirement.reason}; OPERATION: {request.operation}; WHY CANNOT CONTINUE: the supplied value or provenance cannot establish sufficiency.")
            if requirement.require_human_authority and request.human_authority_ref is None:
                (blocking if requirement.blocking else non_blocking).append(item.field); reasons.append("HUMAN_AUTHORITY_REQUIRED")
        if conflicting: status=SufficiencyStatus.CONFLICTING
        elif blocking: status=SufficiencyStatus.INSUFFICIENT
        elif unknown: status=SufficiencyStatus.UNKNOWN
        elif assumed: status=SufficiencyStatus.CONDITIONALLY_SUFFICIENT
        else: status=SufficiencyStatus.SUFFICIENT
        if any(r.require_human_authority for r in request.requirements if r.applies_to(request.scale,request.context,request.jurisdiction)) and request.human_authority_ref is None:
            status=SufficiencyStatus.INSUFFICIENT
        if assumed and not any(x.startswith("ASSUMED_") for x in conditional): conditional.append("ASSUMED_BLOCKING" if blocking else "ASSUMED_NON_BLOCKING")
        coverage=tuple(sorted({i.field for i in request.knowledge if i.field in {r.field for r in request.requirements}}))
        fingerprint=request.fingerprint(); payload=EvaluationIdentityPayload(request.project_id,fingerprint,request.operation,1,request.operation); evaluation_id=compute_evaluation_id(payload)
        return SufficiencyResult(request.project_id,request.operation,status,tuple(sorted(set(known))),tuple(sorted(set(observed))),tuple(sorted(set(assumed))),tuple(sorted(set(unknown))),tuple(sorted(set(missing))),tuple(sorted(set(conflicting))),tuple(sorted(set(blocking))),tuple(sorted(set(non_blocking))),tuple(questions),tuple(assumptions),tuple(sorted(evidence)),coverage,tuple(sorted(set(reasons))),fingerprint,request.policy,evaluation_id,payload.to_dict(),request.human_authority_ref,tuple(sorted(set(conditional))),tuple(sorted(set(levels))))
