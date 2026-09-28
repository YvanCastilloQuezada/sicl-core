"""Canonical evaluation identity for A-002 reports.

The identity is a function of:
  (schema, project_id, snapshot_fingerprint, operation, policy_id, policy_version)

No ad-hoc string concatenation: canonical JSON with sorted keys.
"""
from __future__ import annotations

from dataclasses import dataclass

import hashlib
import json


@dataclass(frozen=True)
class EvaluationIdentityPayload:
    project_id: str
    snapshot_fingerprint: str
    operation: str
    policy_id: str
    policy_version: int
    schema: str = "a002-evaluation-identity-v1"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "projectId": self.project_id,
            "snapshotFingerprint": self.snapshot_fingerprint,
            "operation": self.operation,
            "policyId": self.policy_id,
            "policyVersion": self.policy_version,
        }


def compute_evaluation_id(payload: EvaluationIdentityPayload) -> str:
    canonical = json.dumps(payload.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
