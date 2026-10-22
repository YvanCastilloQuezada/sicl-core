"""Stable identity for the operation policy executed by A-002."""
from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class PolicyIdentity:
    policy_id: str
    policy_version: int
    policy_fingerprint: str
    policy_text: str = ""
    def __post_init__(self) -> None:
        if not self.policy_id.strip(): raise ValueError("policy_id is required")
        if self.policy_version < 1: raise ValueError("policy_version must be positive")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", self.policy_fingerprint): raise ValueError("policy_fingerprint must be 64 hex characters")
    def to_dict(self) -> dict[str, object]:
        return {"policyId": self.policy_id, "policyVersion": self.policy_version, "policyFingerprint": self.policy_fingerprint.lower(), "policyText": self.policy_text}
