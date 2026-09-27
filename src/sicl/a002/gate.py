"""Explicit integration gate between A-002 sufficiency and H-005 execution."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, TypeVar
from .model import SufficiencyRequest, SufficiencyResult, SufficiencyStatus

T = TypeVar("T")


@dataclass(frozen=True)
class GateDecision:
    permitted: bool
    reason: str


class A002H005Gate:
    """Enforces A-002 before invoking an already-authorized H-005 executor."""

    @staticmethod
    def check(request: SufficiencyRequest, result: SufficiencyResult) -> GateDecision:
        if result.project_id != request.project_id or result.operation != request.operation:
            return GateDecision(False, "A002_RESULT_CONTEXT_MISMATCH")
        if result.request_fingerprint != request.fingerprint():
            return GateDecision(False, "A002_RESULT_STALE_OR_FORGED")
        if result.overall_status is SufficiencyStatus.SUFFICIENT:
            return GateDecision(True, "A002_SUFFICIENT")
        if result.overall_status is SufficiencyStatus.CONDITIONALLY_SUFFICIENT and request.policy_allow_assumptions:
            return GateDecision(True, "A002_CONDITIONALLY_SUFFICIENT_POLICY_PERMITS")
        return GateDecision(False, f"A002_{result.overall_status.value}_BLOCKS_H005")

    @classmethod
    def execute_if_permitted(cls, request: SufficiencyRequest, result: SufficiencyResult, executor: Callable[[], T]) -> T:
        decision = cls.check(request, result)
        if not decision.permitted:
            raise PermissionError(decision.reason)
        return executor()
