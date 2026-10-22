"""Authority Gate — LAB-004: autoridad humana inquebrantable."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .sandbox_ledger import SandboxEvent, SandboxEventType, SandboxLedger


class PromotionStatus(str, Enum):
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


@dataclass(frozen=True)
class PromotionResult:
    status: PromotionStatus
    alternative_id: str
    authority_approval_id: str | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status.value, "alternativeId": self.alternative_id, "authorityApprovalId": self.authority_approval_id, "message": self.message}


class AuthorityRequiredError(Exception):
    """Se lanza cuando falta la firma de Autoridad Humana."""


class AuthorityGate:
    def __init__(self, ledger: SandboxLedger):
        self.ledger = ledger

    def promote_to_canonical(self, project_id: str, alternative_id: str, authority_approval_id: str) -> PromotionResult:
        if not authority_approval_id:
            result = PromotionResult(PromotionStatus.REJECTED, alternative_id, None, "Cannot promote: authority_approval_id is required")
            self.ledger.record(SandboxEvent(SandboxEventType.PROMOTED_TO_CANONICAL, datetime.now(timezone.utc).isoformat(), project_id, result.to_dict()))
            raise AuthorityRequiredError(result.message)
        result = PromotionResult(PromotionStatus.PROMOTED, alternative_id, authority_approval_id, f"Alternative {alternative_id} promoted to CANONICAL")
        self.ledger.record(SandboxEvent(SandboxEventType.PROMOTED_TO_CANONICAL, datetime.now(timezone.utc).isoformat(), project_id, result.to_dict()))
        return result


__all__ = ["AuthorityGate", "PromotionResult", "PromotionStatus", "AuthorityRequiredError"]
