"""Explicit integration gate between A-002 sufficiency and H-005 execution.

Fail-closed: any mismatch or empty identity rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

from .identity import EvaluationIdentityPayload, compute_evaluation_id
from .model import SufficiencyRequest, SufficiencyResult, SufficiencyStatus

T = TypeVar("T")


@dataclass(frozen=True)
class GateDecision:
    permitted: bool
    reason: str


class A002H005Gate:
    @staticmethod
    def check(request: SufficiencyRequest, result: SufficiencyResult) -> GateDecision:
        if result.project_id != request.project_id or result.operation != request.operation:
            return GateDecision(False, "A002_RESULT_CONTEXT_MISMATCH")
        if result.request_fingerprint != request.fingerprint():
            return GateDecision(False, "A002_RESULT_STALE_OR_FORGED")

        policy = request.policy if request.policy is not None else result.policy
        policy_id = policy.policy_id if policy else ""
        policy_version = policy.policy_version if policy else 0

        expected = compute_evaluation_id(
            EvaluationIdentityPayload(
                project_id=request.project_id,
                snapshot_fingerprint=request.fingerprint(),
                operation=request.operation,
                policy_id=policy_id,
                policy_version=policy_version,
            )
        )
        # RT-V14-03: strict comparison, no fail-open on empty.
        if result.evaluation_id != expected:
            return GateDecision(False, "A002_EVALUATION_ID_MISMATCH")

        if result.overall_status is SufficiencyStatus.SUFFICIENT:
            return GateDecision(True, "A002_SUFFICIENT")

        if (
            result.overall_status is SufficiencyStatus.CONDITIONALLY_SUFFICIENT
            and request.policy_allow_assumptions
            and "ASSUMED_BLOCKING" not in result.conditional_reasons
        ):
            return GateDecision(True, "A002_CONDITIONALLY_SUFFICIENT_POLICY_PERMITS")

        return GateDecision(False, f"A002_{result.overall_status.value}_BLOCKS_H005")

    @classmethod
    def execute_if_permitted(
        cls,
        request: SufficiencyRequest,
        result: SufficiencyResult,
        executor: Callable[[], T],
    ) -> T:
        decision = cls.check(request, result)
        if not decision.permitted:
            raise PermissionError(decision.reason)
        return executor()
