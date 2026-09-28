"""Deterministic architectural and IFC identities."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import uuid
import ifcopenshell.guid

_SCHEMA = "ARKI-ARCHI-ID-v1"

@dataclass(frozen=True, order=True)
class ArchiElementId:
    value: str

    @classmethod
    def compute(cls, project_id: str, kind: str, birth_nonce: str) -> "ArchiElementId":
        payload = {"schema": _SCHEMA, "project_id": project_id, "kind": kind, "birth_nonce": birth_nonce}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return cls(hashlib.sha256(raw.encode()).hexdigest())

    def __post_init__(self) -> None:
        if len(self.value) != 64 or any(c not in "0123456789abcdef" for c in self.value):
            raise ValueError("ArchiElementId must be lowercase SHA-256 hex")

@dataclass(frozen=True, order=True)
class IfcGlobalId:
    value: str

    @classmethod
    def from_archi_id(cls, archi_id: ArchiElementId) -> "IfcGlobalId":
        if not isinstance(archi_id, ArchiElementId):
            raise TypeError("archi_id must be ArchiElementId")
        return cls(ifcopenshell.guid.compress(str(uuid.UUID(hex=archi_id.value[:32]))))

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value:
            raise ValueError("IfcGlobalId must be non-empty")

__all__ = ["ArchiElementId", "IfcGlobalId"]
