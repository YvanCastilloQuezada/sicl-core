"""H-005 contract: selective recomputation eligibility, no execution."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..derivation import VersionedRef
from ..reaction import ActionStatus, ActionType, PlannedAction, ReactionPlan


class H005Error(Exception):
    """Base error for fail-closed H-005 operations."""


class ActionNotEligibleError(H005Error):
    pass


class ExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class RecomputationCandidate:
    artifact_ref: VersionedRef
    action: PlannedAction
    method: str
    method_version: str

    @classmethod
    def from_action(cls, action: PlannedAction, *, method: str, method_version: str) -> "RecomputationCandidate":
        if not isinstance(action, PlannedAction):
            raise ActionNotEligibleError("action must be a PlannedAction")
        if action.action_type is not ActionType.RECOMPUTE:
            raise ActionNotEligibleError("only ActionType.RECOMPUTE is eligible")
        if action.status is not ActionStatus.PLANNED:
            raise ActionNotEligibleError("only ActionStatus.PLANNED is eligible")
        if action.requires_human_authority:
            raise ActionNotEligibleError("requires_human_authority must be False")
        if not isinstance(method, str) or not method.strip():
            raise ActionNotEligibleError("method must be non-empty")
        if not isinstance(method_version, str) or not method_version.strip():
            raise ActionNotEligibleError("method_version must be non-empty")
        return cls(action.artifact_ref, action, method.strip(), method_version.strip())


@dataclass(frozen=True)
class ExecutionRecord:
    project_id: str
    artifact_requested: VersionedRef
    derivation_selected: str | None
    method: str | None
    method_version: str | None
    inputs: tuple[VersionedRef, ...]
    previous_output: VersionedRef | None
    new_output: VersionedRef | None
    status: ExecutionStatus
    reason: str

    def to_dict(self) -> dict[str, Any]:
        ref = lambda value: value.to_dict() if value is not None else None
        return {
            "projectId": self.project_id,
            "artifactRequested": ref(self.artifact_requested),
            "derivationSelected": self.derivation_selected,
            "method": self.method,
            "methodVersion": self.method_version,
            "inputs": [item.to_dict() for item in self.inputs],
            "previousOutput": ref(self.previous_output),
            "newOutput": ref(self.new_output),
            "status": self.status.value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class H005ExecutionReport:
    records: tuple[ExecutionRecord, ...]
    contract_version: int = 1
    read_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"contractVersion": self.contract_version, "records": [item.to_dict() for item in self.records], "readOnly": self.read_only}


def eligible_for_automatic_recomputation(action: PlannedAction) -> bool:
    try:
        RecomputationCandidate.from_action(action, method="placeholder", method_version="placeholder")
    except H005Error:
        return False
    return True


__all__ = ["H005Error", "ActionNotEligibleError", "ExecutionStatus", "RecomputationCandidate", "ExecutionRecord", "H005ExecutionReport", "eligible_for_automatic_recomputation"]
