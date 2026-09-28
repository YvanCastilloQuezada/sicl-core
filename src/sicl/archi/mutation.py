"""Deterministic architectural mutation requests."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import hashlib, json
from .identity import ArchiElementId

class MutationKind(str, Enum):
    MOVE="MOVE"; RESIZE="RESIZE"; ADD_OPENING="ADD_OPENING"; DELETE="DELETE"

@dataclass(frozen=True)
class ArchiMutation:
    project_id: str
    mutation_kind: MutationKind
    target_id: ArchiElementId
    target_version: int
    canonical_payload: dict
    request_nonce: str
    requested_at_iso: str | None = None
    def __post_init__(self):
        if self.target_version < 1: raise ValueError("target_version must be positive")
        if not self.request_nonce.strip(): raise ValueError("request_nonce is required")
    def canonical_dict(self):
        return {"schema":"ARKI-ARCHI-MUTATION-v1","project_id":self.project_id,"mutation_kind":self.mutation_kind.value,"target_id":self.target_id.value,"target_version":self.target_version,"canonical_payload":self.canonical_payload,"request_nonce":self.request_nonce}
    def compute_id(self) -> str:
        raw=json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()

__all__=["MutationKind","ArchiMutation"]
