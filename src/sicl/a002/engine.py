"""Deterministic A-002 sufficiency engine (v1.4.1).

Rules:
- declared vs effective state is computed and recorded as ItemAssessment.
- A KNOWN without valid evidence downgrades to OBSERVED.
- Applicability is read from the request's ApplicabilityDeclaration set.
- Policy is resolved automatically from operation if not supplied.
"""
from __future__ import annotations

from collections import defaultdict

from .identity import EvaluationIdentityPayload, compute_evaluation_id
from .model import (
    ApplicabilityDeclaration,
    ApplicabilityStatus,
    EvidenceVerificationLevel,
    ItemAssessment,
    KnowledgeState,
    SufficiencyRequest,
    SufficiencyResult,
    SufficiencyStatus,
)
from .requirements import policy_for


def _is_valid_value(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (dict, list, set, tuple)):
        return False
    return True


def _applicability_index(
    declarations: tuple[ApplicabilityDeclaration, ...],
) -> dict[str, ApplicabilityStatus]:
    """Aggregate declarations per field. If two disagree, mark CONFLICTING."""
    out: dict[str, ApplicabilityStatus] = {}
    for decl in declarations:
        current = out.get(decl.field)
        if current is None:
            out[decl.field] = decl.status
        elif current != decl.status:
            out[decl.field] = ApplicabilityStatus.CONFLICTING
    return out


class SufficiencyEngine:
    def evaluate(self, request: SufficiencyRequest) -> SufficiencyResult:
        if not isinstance(request, SufficiencyRequest):
            raise TypeError("request must be SufficiencyRequest")

        # RT-V14-07: resolve policy automatically if not provided.
        policy = request.policy if request.policy is not None else policy_for(request.operation)

        by_field: dict[str, list] = defaultdict(list)
        for item in request.knowledge:
            by_field[item.field].append(item)

        evidence_by_id = {e.evidence_id: e for e in request.evidence}
        applicability_by_field = _applicability_index(request.applicability)

        known: list[str] = []
        observed: list[str] = []
        assumed: list[str] = []
        unknown: list[str] = []
        missing: list[str] = []
        conflicting: list[str] = []

        blocking: list[str] = []
        non_blocking: list[str] = []
        questions: list[str] = []
        assumptions_used: list[str] = []
        evidence_refs_seen: set[str] = set()
        evidence_levels: list[tuple[str, str]] = []
        reason_codes: list[str] = []
        conditional_reasons: list[str] = []
        assessments: list[ItemAssessment] = []

        for requirement in request.requirements:
            if not requirement.applies_to(request.scale, request.context, request.jurisdiction):
                continue

            allowed_scales = set(requirement.applicable_scales)
            items = [
                item
                for item in by_field.get(requirement.field, [])
                if (not allowed_scales or item.scale in allowed_scales)
                and (
                    item.jurisdiction is None
                    or request.jurisdiction is None
                    or item.jurisdiction == request.jurisdiction
                )
            ]

            if not items:
                missing.append(requirement.field)
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reason_codes.append(
                    "MISSING_REQUIRED_INPUT" if requirement.blocking else "MISSING_OPTIONAL_INPUT"
                )
                if not requirement.blocking:
                    conditional_reasons.append("NON_BLOCKING_MISSING")
                if requirement.blocking:
                    questions.append(
                        f"WHAT IS MISSING: {requirement.field}; "
                        f"WHY REQUIRED: {requirement.reason}; "
                        f"OPERATION: {request.operation}; "
                        f"WHY CANNOT CONTINUE: this blocking requirement has no evidence."
                    )
                assessments.append(
                    ItemAssessment(
                        field=requirement.field,
                        declared_state=KnowledgeState.MISSING,
                        effective_state=KnowledgeState.MISSING,
                        downgrade_reason="NO_ITEM_PROVIDED",
                        blocking=requirement.blocking,
                    )
                )
                continue

            # Conflict check (mixed states or conflicting values).
            states = {item.state for item in items}
            values_differ = len({repr(item.value) for item in items}) > 1
            if KnowledgeState.CONFLICTING in states or (len(items) > 1 and values_differ):
                conflicting.append(requirement.field)
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reason_codes.append(
                    "CONFLICTING_EVIDENCE" if KnowledgeState.CONFLICTING in states else "CONFLICTING_VALUES"
                )
                if not requirement.blocking:
                    conditional_reasons.append("NON_BLOCKING_CONFLICTING")
                if requirement.blocking:
                    questions.append(
                        f"WHAT IS MISSING: authoritative resolution for {requirement.field}; "
                        f"WHY REQUIRED: evidence conflicts; "
                        f"OPERATION: {request.operation}; "
                        f"WHY CANNOT CONTINUE: arbitrary selection is unsafe."
                    )
                assessments.append(
                    ItemAssessment(
                        field=requirement.field,
                        declared_state=KnowledgeState.CONFLICTING,
                        effective_state=KnowledgeState.CONFLICTING,
                        downgrade_reason="CONFLICTING_VALUES_OR_STATES",
                        blocking=requirement.blocking,
                    )
                )
                continue

            # Pick latest version.
            item = sorted(items, key=lambda x: x.version)[-1]

            # Evidence checks.
            evidence_ids_in_item = tuple(item.evidence_refs)
            resolved_evidence = [evidence_by_id[i] for i in evidence_ids_in_item if i in evidence_by_id]
            for ref in resolved_evidence:
                evidence_refs_seen.add(ref.evidence_id)
                evidence_levels.append((ref.evidence_id, ref.guaranteed_verification_level().value))

            evidence_valid = bool(item.evidence_refs) and all(
                ref_id in evidence_by_id
                and evidence_by_id[ref_id].project_id == request.project_id
                and (not allowed_scales or evidence_by_id[ref_id].scale in allowed_scales)
                and (
                    evidence_by_id[ref_id].jurisdiction is None
                    or request.jurisdiction is None
                    or evidence_by_id[ref_id].jurisdiction == request.jurisdiction
                )
                for ref_id in item.evidence_refs
            )

            declared = item.state
            effective = declared
            downgrade_reason = ""

            if declared in {KnowledgeState.KNOWN, KnowledgeState.OBSERVED} and not _is_valid_value(item.value):
                effective = KnowledgeState.UNKNOWN
                downgrade_reason = "INVALID_INPUT_VALUE"
            elif declared is KnowledgeState.ASSUMED and not item.reason.strip():
                effective = KnowledgeState.UNKNOWN
                downgrade_reason = "ASSUMED_WITHOUT_REASON"
            elif declared is KnowledgeState.KNOWN and not evidence_valid:
                effective = KnowledgeState.UNKNOWN
                downgrade_reason = (
                    "KNOWN_WITHOUT_EVIDENCE" if not item.evidence_refs else "EVIDENCE_INVALID"
                )

            # Applicability (RT-V14-05: sourced from request, not from item).
            applicability_status = applicability_by_field.get(requirement.field, ApplicabilityStatus.UNKNOWN)
            if requirement.applicability_required:
                if applicability_status is ApplicabilityStatus.CONFLICTING:
                    effective = KnowledgeState.CONFLICTING
                    conflicting.append(requirement.field)
                    (blocking if requirement.blocking else non_blocking).append(requirement.field)
                    reason_codes.append("CONFLICTING_APPLICABILITY")
                    if requirement.blocking:
                        questions.append(
                            f"WHAT IS MISSING: applicability arbitration for {requirement.field}; "
                            f"WHY REQUIRED: normative sources conflict; "
                            f"OPERATION: {request.operation}; "
                            f"WHY CANNOT CONTINUE: applicability is not safely established."
                        )
                elif applicability_status is ApplicabilityStatus.UNKNOWN and requirement.blocking:
                    effective = KnowledgeState.UNKNOWN
                    downgrade_reason = downgrade_reason or "APPLICABILITY_UNKNOWN"
                elif applicability_status is ApplicabilityStatus.NOT_APPLICABLE and requirement.blocking:
                    effective = KnowledgeState.MISSING
                    downgrade_reason = downgrade_reason or "APPLICABILITY_NOT_APPLICABLE"

            # Classify into buckets (RT-V14-08: no double counting).
            if effective is KnowledgeState.KNOWN:
                known.append(requirement.field)
            elif effective is KnowledgeState.OBSERVED:
                observed.append(requirement.field)
                reason_codes.append(downgrade_reason or "OBSERVED_INPUT")
                if downgrade_reason:
                    (blocking if requirement.blocking else non_blocking).append(requirement.field)
            elif effective is KnowledgeState.ASSUMED:
                assumed.append(requirement.field)
                assumptions_used.append(f"{requirement.field}: {item.reason}")
                conditional_reasons.append(
                    "ASSUMED_BLOCKING" if requirement.blocking else "ASSUMED_NON_BLOCKING"
                )
                if not (request.policy_allow_assumptions and requirement.allow_assumed):
                    (blocking if requirement.blocking else non_blocking).append(requirement.field)
                    reason_codes.append("ASSUMPTION_NOT_PERMITTED")
            elif effective is KnowledgeState.UNKNOWN:
                unknown.append(requirement.field)
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reason_codes.append(downgrade_reason or "UNKNOWN_INPUT")
            elif effective is KnowledgeState.MISSING:
                missing.append(requirement.field)
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reason_codes.append(downgrade_reason or "MISSING_INPUT")
            elif effective is KnowledgeState.CONFLICTING:
                if requirement.field not in conflicting:
                    conflicting.append(requirement.field)
                if requirement.field not in blocking and requirement.field not in non_blocking:
                    (blocking if requirement.blocking else non_blocking).append(requirement.field)

            # Blocking questions for observed/unknown/missing.
            if requirement.blocking and effective in {
                KnowledgeState.UNKNOWN,
                KnowledgeState.MISSING,
                KnowledgeState.OBSERVED,
            }:
                questions.append(
                    f"WHAT IS MISSING: verified {requirement.field}; "
                    f"WHY REQUIRED: {requirement.reason}; "
                    f"OPERATION: {request.operation}; "
                    f"WHY CANNOT CONTINUE: the supplied value or provenance cannot establish sufficiency."
                )

            # Human authority requirement.
            if requirement.require_human_authority and request.human_authority_ref is None:
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reason_codes.append("HUMAN_AUTHORITY_REQUIRED")

            assessments.append(
                ItemAssessment(
                    field=requirement.field,
                    declared_state=declared,
                    effective_state=effective,
                    downgrade_reason=downgrade_reason,
                    evidence_ids=evidence_ids_in_item,
                    evidence_level=(
                        EvidenceVerificationLevel.CONTENT_HASH_MATCHES_DECLARED
                        if evidence_valid
                        else EvidenceVerificationLevel.ABSENT
                    ),
                    applicability_status=applicability_status,
                    blocking=requirement.blocking,
                )
            )

        # Aggregate status (fail-closed precedence).
        if conflicting:
            status = SufficiencyStatus.CONFLICTING
        elif blocking:
            status = SufficiencyStatus.INSUFFICIENT
        elif unknown:
            status = SufficiencyStatus.UNKNOWN
        elif assumed:
            status = SufficiencyStatus.CONDITIONALLY_SUFFICIENT
        else:
            status = SufficiencyStatus.SUFFICIENT

        if (
            any(
                r.require_human_authority
                for r in request.requirements
                if r.applies_to(request.scale, request.context, request.jurisdiction)
            )
            and request.human_authority_ref is None
        ):
            status = SufficiencyStatus.INSUFFICIENT

        coverage = tuple(
            sorted(
                {
                    item.field
                    for item in request.knowledge
                    if item.field in {r.field for r in request.requirements}
                }
            )
        )

        # Evaluation identity (RT-V14-02: use real policy identity).
        request_fingerprint = request.fingerprint()
        policy_id = policy.policy_id if policy else ""
        policy_version = policy.policy_version if policy else 0
        payload = EvaluationIdentityPayload(
            project_id=request.project_id,
            snapshot_fingerprint=request_fingerprint,
            operation=request.operation,
            policy_id=policy_id,
            policy_version=policy_version,
        )
        evaluation_id = compute_evaluation_id(payload)

        return SufficiencyResult(
            project_id=request.project_id,
            operation=request.operation,
            overall_status=status,
            known=tuple(sorted(set(known))),
            observed=tuple(sorted(set(observed))),
            assumed=tuple(sorted(set(assumed))),
            unknown=tuple(sorted(set(unknown))),
            missing=tuple(sorted(set(missing))),
            conflicting=tuple(sorted(set(conflicting))),
            blocking_items=tuple(sorted(set(blocking))),
            non_blocking_items=tuple(sorted(set(non_blocking))),
            questions_for_human=tuple(questions),
            assumptions_used=tuple(assumptions_used),
            evidence_refs=tuple(sorted(evidence_refs_seen)),
            evidence_levels=tuple(sorted(set(evidence_levels))),
            coverage=coverage,
            reason_codes=tuple(sorted(set(reason_codes))),
            conditional_reasons=tuple(sorted(set(conditional_reasons))),
            assessments=tuple(assessments),
            request_fingerprint=request_fingerprint,
            evaluation_id=evaluation_id,
            identity_payload=payload.to_dict(),
            policy=policy,
            human_authority_ref=request.human_authority_ref,
        )
