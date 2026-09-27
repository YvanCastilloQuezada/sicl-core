"""Deterministic A-002 sufficiency engine."""
from __future__ import annotations
from collections import defaultdict
from .model import KnowledgeState, SufficiencyRequest, SufficiencyResult, SufficiencyStatus


class SufficiencyEngine:
    def evaluate(self, request: SufficiencyRequest) -> SufficiencyResult:
        if not isinstance(request, SufficiencyRequest):
            raise TypeError("request must be SufficiencyRequest")
        by_field: dict[str, list] = defaultdict(list)
        for item in request.knowledge:
            by_field[item.field].append(item)
        known: list[str] = []
        observed: list[str] = []
        assumed: list[str] = []
        unknown: list[str] = []
        missing: list[str] = []
        conflicting: list[str] = []
        blocking: list[str] = []
        non_blocking: list[str] = []
        questions: list[str] = []
        assumptions: list[str] = []
        evidence: set[str] = set()
        reasons: list[str] = []
        for requirement in request.requirements:
            if not requirement.applies_to(request.scale, request.context, request.jurisdiction):
                continue
            allowed_scales = set(requirement.applicable_scales)
            items = [
                item for item in by_field.get(requirement.field, [])
                if (not allowed_scales or item.scale in allowed_scales)
                and (item.jurisdiction is None or request.jurisdiction is None or item.jurisdiction == request.jurisdiction)
            ]
            for item in items:
                evidence.update(item.evidence_refs)
            if not items:
                missing.append(requirement.field)
                code = "MISSING_REQUIRED_INPUT" if requirement.blocking else "MISSING_OPTIONAL_INPUT"
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reasons.append(code)
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: {requirement.field}; WHY REQUIRED: {requirement.reason}; OPERATION: {request.operation}; WHY CANNOT CONTINUE: this blocking requirement has no evidence.")
                continue
            states = {item.state for item in items}
            if len(states) > 1 and any(item.state is KnowledgeState.CONFLICTING for item in items):
                conflicting.append(requirement.field)
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reasons.append("CONFLICTING_EVIDENCE")
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: authoritative resolution for {requirement.field}; WHY REQUIRED: evidence conflicts; OPERATION: {request.operation}; WHY CANNOT CONTINUE: arbitrary selection is unsafe.")
                continue
            if len(items) > 1 and len({repr(item.value) for item in items}) > 1:
                conflicting.append(requirement.field)
                (blocking if requirement.blocking else non_blocking).append(requirement.field)
                reasons.append("CONFLICTING_VALUES")
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: authoritative value for {requirement.field}; WHY REQUIRED: duplicate evidence disagrees; OPERATION: {request.operation}; WHY CANNOT CONTINUE: the engine cannot choose arbitrarily.")
                continue
            item = sorted(items, key=lambda x: x.version)[-1]
            invalid_value = item.value is None or (isinstance(item.value, str) and not item.value.strip()) or isinstance(item.value, (dict, list, set))
            if item.state in {KnowledgeState.KNOWN, KnowledgeState.OBSERVED} and invalid_value:
                unknown.append(item.field)
                (blocking if requirement.blocking else non_blocking).append(item.field)
                reasons.append("INVALID_INPUT_VALUE")
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: a valid value for {item.field}; WHY REQUIRED: the supplied value has an invalid type or is empty; OPERATION: {request.operation}; WHY CANNOT CONTINUE: malformed input cannot establish sufficiency.")
                continue
            evidence_by_id = {ref.evidence_id: ref for ref in request.evidence}
            evidence_valid = bool(item.evidence_refs) and all(
                ref_id in evidence_by_id
                and evidence_by_id[ref_id].project_id == request.project_id
                and (not allowed_scales or evidence_by_id[ref_id].scale in allowed_scales)
                and (evidence_by_id[ref_id].jurisdiction is None or request.jurisdiction is None or evidence_by_id[ref_id].jurisdiction == request.jurisdiction)
                for ref_id in item.evidence_refs
            )
            if item.state in {KnowledgeState.KNOWN, KnowledgeState.OBSERVED} and not evidence_valid:
                unknown.append(item.field)
                (blocking if requirement.blocking else non_blocking).append(item.field)
                reasons.append("MISSING_OR_INVALID_PROVENANCE")
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: valid provenance for {item.field}; WHY REQUIRED: the supplied evidence is absent, stale, cross-project, or out of scope; OPERATION: {request.operation}; WHY CANNOT CONTINUE: the state cannot be promoted to {item.state.value} without matching evidence.")
            elif item.state is KnowledgeState.KNOWN:
                known.append(item.field)
            elif item.state is KnowledgeState.OBSERVED:
                observed.append(item.field)
            elif item.state is KnowledgeState.ASSUMED:
                assumed.append(item.field)
                assumptions.append(f"{item.field}: {item.reason}")
                if not (request.policy_allow_assumptions and requirement.allow_assumed):
                    (blocking if requirement.blocking else non_blocking).append(item.field)
                    reasons.append("ASSUMPTION_NOT_PERMITTED")
                    if requirement.blocking:
                        questions.append(f"WHAT IS MISSING: confirmed value for {item.field}; WHY REQUIRED: the current policy does not permit this assumption; OPERATION: {request.operation}; WHY CANNOT CONTINUE: an assumption cannot be treated as fact.")
            elif item.state is KnowledgeState.UNKNOWN:
                unknown.append(item.field)
                (blocking if requirement.blocking else non_blocking).append(item.field)
                reasons.append("UNKNOWN_INPUT")
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: verified {item.field}; WHY REQUIRED: {requirement.reason}; OPERATION: {request.operation}; WHY CANNOT CONTINUE: unknown input cannot be promoted to known.")
            elif item.state is KnowledgeState.MISSING:
                missing.append(item.field)
                (blocking if requirement.blocking else non_blocking).append(item.field)
                reasons.append("MISSING_INPUT")
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: {item.field}; WHY REQUIRED: {requirement.reason}; OPERATION: {request.operation}; WHY CANNOT CONTINUE: missing input blocks safe execution.")
            elif item.state is KnowledgeState.CONFLICTING:
                conflicting.append(item.field)
                (blocking if requirement.blocking else non_blocking).append(item.field)
                reasons.append("CONFLICTING_INPUT")
                if requirement.blocking:
                    questions.append(f"WHAT IS MISSING: conflict resolution for {item.field}; WHY REQUIRED: {requirement.reason}; OPERATION: {request.operation}; WHY CANNOT CONTINUE: the engine cannot select an arbitrary source.")
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
        coverage = tuple(sorted({item.field for item in request.knowledge if item.field in {r.field for r in request.requirements}}))
        return SufficiencyResult(request.project_id, request.operation, status, tuple(sorted(set(known))), tuple(sorted(set(observed))), tuple(sorted(set(assumed))), tuple(sorted(set(unknown))), tuple(sorted(set(missing))), tuple(sorted(set(conflicting))), tuple(sorted(set(blocking))), tuple(sorted(set(non_blocking))), tuple(questions), tuple(assumptions), tuple(sorted(evidence)), coverage, tuple(sorted(set(reasons))), request.fingerprint())
