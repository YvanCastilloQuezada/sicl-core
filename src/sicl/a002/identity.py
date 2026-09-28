"""Canonical evaluation identity for A-002 reports."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json

@dataclass(frozen=True)
class EvaluationIdentityPayload:
    project_id: str
    snapshot_fingerprint: str
    profile_id: str
    profile_version: int
    operation: str
    schema: str = "a002-evaluation-identity-v1"
    def to_dict(self) -> dict[str, object]:
        return {"schema": self.schema, "projectId": self.project_id, "snapshotFingerprint": self.snapshot_fingerprint, "profileId": self.profile_id, "profileVersion": self.profile_version, "operation": self.operation}

def compute_evaluation_id(payload: EvaluationIdentityPayload) -> str:
    canonical = json.dumps(payload.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
