"""ARKI Copilot CP-01: conversation/action contract.

This module is intentionally policy-only. It does not call LLMs, tools, project
repositories, generation pipelines, or geometry engines.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CopilotIntent(str, Enum):
    CONVERSE = "CONVERSE"
    RESEARCH = "RESEARCH"
    EXPLORE = "EXPLORE"
    DESIGN_INTENT = "DESIGN_INTENT"
    PREPARE_ACTION = "PREPARE_ACTION"
    EXECUTE = "EXECUTE"
    REVIEW = "REVIEW"
    CONTINUE = "CONTINUE"


class FactStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    PROPOSED = "PROPOSED"
    MISSING = "MISSING"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class CopilotFact:
    """A contextual fact with explicit epistemic status and provenance."""
    key: str
    value: Any = None
    status: FactStatus = FactStatus.UNKNOWN
    source: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("fact key must not be empty")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.status in {FactStatus.MISSING, FactStatus.UNKNOWN, FactStatus.AMBIGUOUS} and self.value is not None:
            raise ValueError(f"{self.status.value} facts must not carry a value")


@dataclass(frozen=True)
class CopilotMessage:
    """Transport-neutral message shape; persistence is implemented in CP-02."""
    message_id: str
    session_id: str
    role: str
    content: str
    attachments: tuple[str, ...] = ()
    created_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.message_id.strip():
            raise ValueError("message_id must not be empty")
        if not self.session_id.strip():
            raise ValueError("session_id must not be empty")
        if self.role not in {"architect", "copilot", "system", "tool"}:
            raise ValueError("role must be architect, copilot, system, or tool")


@dataclass(frozen=True)
class ActionGateInput:
    """Facts required to evaluate an action. This gate never performs the action."""
    intent: CopilotIntent
    explicit_execution_request: bool = False
    capability_available: bool = False
    inputs_validated: bool = False
    permission_granted: bool = False
    risk_policy_satisfied: bool = False
    confirmation_required: bool = True
    user_confirmed: bool = False


@dataclass(frozen=True)
class ActionGateDecision:
    allowed: bool
    reasons: tuple[str, ...]


def evaluate_action_gate(request: ActionGateInput) -> ActionGateDecision:
    """Fail-closed policy: EXECUTE must be explicit and satisfy every gate."""
    reasons: list[str] = []

    if request.intent is not CopilotIntent.EXECUTE:
        reasons.append("intent_is_not_execute")
    if not request.explicit_execution_request:
        reasons.append("explicit_execution_request_missing")
    if not request.capability_available:
        reasons.append("capability_unavailable")
    if not request.inputs_validated:
        reasons.append("inputs_not_validated")
    if not request.permission_granted:
        reasons.append("permission_not_granted")
    if not request.risk_policy_satisfied:
        reasons.append("risk_policy_not_satisfied")
    if request.confirmation_required and not request.user_confirmed:
        reasons.append("user_confirmation_missing")

    return ActionGateDecision(allowed=not reasons, reasons=tuple(reasons))
