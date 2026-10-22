"""Human authority reference; A-002 records a reference and does not sign."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class HumanAuthorityRef:
    actor_id: str
    decision_context: str
    recorded_at_iso: str
    reference: str
    def __post_init__(self) -> None:
        if not all(v and v.strip() for v in (self.actor_id, self.decision_context, self.recorded_at_iso, self.reference)):
            raise ValueError("all HumanAuthorityRef fields are required")
    def to_dict(self) -> dict[str, str]:
        return {"actorId": self.actor_id, "decisionContext": self.decision_context, "recordedAt": self.recorded_at_iso, "reference": self.reference}
