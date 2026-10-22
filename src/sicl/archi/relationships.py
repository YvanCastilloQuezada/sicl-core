"""Architectural metadata relationships and H-001 projection."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import hashlib, json
from .identity import ArchiElementId
from ..derivation import DerivationRecord, TypedRelation, VersionedRef

class RelationshipKind(str, Enum):
    HOSTED_IN="HOSTED_IN"
    BOUNDS="BOUNDS"

@dataclass(frozen=True)
class ArchiRelationship:
    relationship_id: str
    kind: RelationshipKind
    source_id: ArchiElementId
    target_id: ArchiElementId
    source_version: int = 1
    target_version: int = 1
    def __post_init__(self):
        if self.source_id == self.target_id: raise ValueError("relationship cannot self-reference")
    @classmethod
    def compute_id(cls, kind, source_id, target_id):
        raw=json.dumps({"schema":"ARKI-ARCHI-REL-v1","kind":kind.value,"source":source_id.value,"target":target_id.value}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()
    @classmethod
    def create(cls, kind, source_id, target_id, source_version=1, target_version=1):
        return cls(cls.compute_id(kind, source_id, target_id), kind, source_id, target_id, source_version, target_version)

def project_derived_from(dependent: VersionedRef, input_ref: VersionedRef) -> TypedRelation:
    return TypedRelation(dependent, input_ref, "DERIVED_FROM", "ARCHITECTURAL")

def architectural_derivation(record_id: str, output: VersionedRef, inputs: tuple[VersionedRef, ...]) -> DerivationRecord:
    """Build one H-001 record; HOSTED_IN/BOUNDS remain outside this record."""
    return DerivationRecord(
        record_id, output, inputs, "archi.relationship_projection", "1.0",
        tuple(project_derived_from(output, item) for item in inputs),
    )

__all__=["RelationshipKind","ArchiRelationship","project_derived_from","architectural_derivation"]
