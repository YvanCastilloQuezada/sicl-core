"""ARKI H-001: deterministic, read-only derivation integrity primitives.

The ledger reuses the append-only Event Store only as persistence. It records and
queries derivation evidence; it never propagates, invalidates, recomputes,
mutates geometry, or changes Human Authority decisions.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from .domain import Event, now_iso

RELATION_DOMAINS = frozenset({"ARCHITECTURAL", "COMPUTATIONAL", "EPISTEMIC", "NORMATIVE", "GOVERNANCE"})
RELATION_TYPES = frozenset({"DERIVED_FROM", "COMPUTED_FROM", "SUPPORTED_BY"})

class DerivationValidationError(ValueError):
    pass


def _required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DerivationValidationError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, order=True)
class VersionedRef:
    entity_type: str
    entity_id: str
    version: int
    content_hash: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity_type", _required_text(self.entity_type, "entity_type"))
        object.__setattr__(self, "entity_id", _required_text(self.entity_id, "entity_id"))
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 1:
            raise DerivationValidationError("version must be a positive integer")
        if self.content_hash is not None and (not isinstance(self.content_hash, str) or len(self.content_hash) != 64 or any(c not in "0123456789abcdef" for c in self.content_hash)):
            raise DerivationValidationError("content_hash must be lowercase SHA-256 hex")

    def to_dict(self) -> dict[str, Any]:
        value = {"entityType": self.entity_type, "entityId": self.entity_id, "version": self.version}
        if self.content_hash is not None:
            value["contentHash"] = self.content_hash
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "VersionedRef":
        if not isinstance(value, Mapping):
            raise DerivationValidationError("versioned ref must be an object")
        unknown = set(value) - {"entityType", "entityId", "version", "contentHash"}
        if unknown:
            raise DerivationValidationError(f"versioned ref has unknown fields: {sorted(unknown)}")
        try:
            return cls(value["entityType"], value["entityId"], value["version"], value.get("contentHash"))
        except KeyError as exc:
            raise DerivationValidationError(f"versioned ref missing {exc.args[0]}") from exc

    def key(self) -> tuple[str, str]:
        return self.entity_type, self.entity_id


@dataclass(frozen=True)
class TypedRelation:
    """A subject-predicate-object edge: from_ref RELATION to_ref.

    Examples: Area COMPUTED_FROM Geometry; Claim SUPPORTED_BY Evidence.
    """
    from_ref: VersionedRef
    to_ref: VersionedRef
    relation_type: str
    relation_domain: str

    def __post_init__(self) -> None:
        if not isinstance(self.from_ref, VersionedRef) or not isinstance(self.to_ref, VersionedRef):
            raise DerivationValidationError("relation endpoints must be VersionedRef")
        relation_type = _required_text(self.relation_type, "relation_type")
        relation_domain = _required_text(self.relation_domain, "relation_domain")
        object.__setattr__(self, "relation_type", relation_type)
        object.__setattr__(self, "relation_domain", relation_domain)
        if relation_type not in RELATION_TYPES:
            raise DerivationValidationError(f"unsupported relation_type: {relation_type}")
        if relation_domain not in RELATION_DOMAINS:
            raise DerivationValidationError(f"unsupported relation_domain: {relation_domain}")
        if self.from_ref == self.to_ref:
            raise DerivationValidationError("relation cannot connect a ref to itself")
        if relation_type == "SUPPORTED_BY" and relation_domain != "EPISTEMIC":
            raise DerivationValidationError("SUPPORTED_BY relations must be EPISTEMIC")
        if relation_type == "COMPUTED_FROM" and relation_domain != "COMPUTATIONAL":
            raise DerivationValidationError("COMPUTED_FROM relations must be COMPUTATIONAL")
        if relation_type == "DERIVED_FROM" and relation_domain == "GOVERNANCE":
            raise DerivationValidationError("DERIVED_FROM relation domain is unsupported")

    def to_dict(self) -> dict[str, Any]:
        return {"from": self.from_ref.to_dict(), "to": self.to_ref.to_dict(), "relationType": self.relation_type, "relationDomain": self.relation_domain}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TypedRelation":
        if not isinstance(value, Mapping):
            raise DerivationValidationError("typed relation must be an object")
        unknown = set(value) - {"from", "to", "relationType", "relationDomain"}
        if unknown:
            raise DerivationValidationError(f"typed relation has unknown fields: {sorted(unknown)}")
        try:
            return cls(VersionedRef.from_dict(value["from"]), VersionedRef.from_dict(value["to"]), value["relationType"], value["relationDomain"])
        except KeyError as exc:
            raise DerivationValidationError(f"typed relation missing {exc.args[0]}") from exc


@dataclass(frozen=True)
class DerivationRecord:
    CONTRACT_VERSION = 1

    id: str
    output: VersionedRef
    inputs: tuple[VersionedRef, ...]
    method: str
    method_version: str
    relations: tuple[TypedRelation, ...]
    fingerprint: str | None = None
    project_context_version: int | None = None
    assumptions: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _required_text(self.id, "id"))
        object.__setattr__(self, "method", _required_text(self.method, "method"))
        object.__setattr__(self, "method_version", _required_text(self.method_version, "method_version"))
        if not isinstance(self.output, VersionedRef):
            raise DerivationValidationError("output must be VersionedRef")
        if not self.inputs:
            raise DerivationValidationError("derivation requires at least one input")
        if any(not isinstance(item, VersionedRef) for item in self.inputs):
            raise DerivationValidationError("inputs must be VersionedRef values")
        if self.output in self.inputs:
            raise DerivationValidationError("output cannot also be an input")
        if len(set(self.inputs)) != len(self.inputs):
            raise DerivationValidationError("derivation inputs must be unique")
        if any(not isinstance(item, TypedRelation) for item in self.relations):
            raise DerivationValidationError("relations must be TypedRelation values")
        if len(set(self.relations)) != len(self.relations):
            raise DerivationValidationError("derivation relations must be unique")
        for ref in self.inputs:
            matching = [r for r in self.relations if r.from_ref == self.output and r.to_ref == ref]
            if len(matching) != 1:
                raise DerivationValidationError("each input must have exactly one output-to-input typed relation")
        allowed_pairs = {(self.output, ref) for ref in self.inputs}
        if any((r.from_ref, r.to_ref) not in allowed_pairs for r in self.relations):
            raise DerivationValidationError("relations may only connect the output to declared inputs")
        if self.fingerprint is not None and (not isinstance(self.fingerprint, str) or len(self.fingerprint) != 64 or any(c not in "0123456789abcdef" for c in self.fingerprint)):
            raise DerivationValidationError("fingerprint must be lowercase SHA-256 hex")
        if self.project_context_version is not None and (isinstance(self.project_context_version, bool) or not isinstance(self.project_context_version, int) or self.project_context_version < 1):
            raise DerivationValidationError("project_context_version must be a positive integer")
        if any(not isinstance(a, str) or not a.strip() for a in self.assumptions):
            raise DerivationValidationError("assumptions must be non-empty strings")
        normalized_assumptions = tuple(a.strip() for a in self.assumptions)
        if len(set(normalized_assumptions)) != len(normalized_assumptions):
            raise DerivationValidationError("assumptions must be unique after normalization")
        object.__setattr__(self, "assumptions", normalized_assumptions)

    def to_dict(self) -> dict[str, Any]:
        return {"contractVersion": self.CONTRACT_VERSION, "id": self.id, "output": self.output.to_dict(), "inputs": [x.to_dict() for x in self.inputs], "method": self.method, "methodVersion": self.method_version, "relations": [x.to_dict() for x in self.relations], "fingerprint": self.fingerprint, "projectContextVersion": self.project_context_version, "assumptions": list(self.assumptions)}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "DerivationRecord":
        if not isinstance(value, Mapping):
            raise DerivationValidationError("derivation record must be an object")
        unknown = set(value) - {"contractVersion", "id", "output", "inputs", "method", "methodVersion", "relations", "fingerprint", "projectContextVersion", "assumptions"}
        if unknown:
            raise DerivationValidationError(f"derivation record has unknown fields: {sorted(unknown)}")
        if value.get("contractVersion") != cls.CONTRACT_VERSION:
            raise DerivationValidationError(f"unsupported derivation contractVersion: {value.get('contractVersion')}")
        try:
            return cls(id=value["id"], output=VersionedRef.from_dict(value["output"]), inputs=tuple(VersionedRef.from_dict(x) for x in value["inputs"]), method=value["method"], method_version=value["methodVersion"], relations=tuple(TypedRelation.from_dict(x) for x in value["relations"]), fingerprint=value.get("fingerprint"), project_context_version=value.get("projectContextVersion"), assumptions=tuple(value.get("assumptions", ())))
        except KeyError as exc:
            raise DerivationValidationError(f"derivation record missing {exc.args[0]}") from exc

    def canonical_json(self) -> str:
        value = self.to_dict()
        value["inputs"] = sorted(value["inputs"], key=lambda x: (x["entityType"], x["entityId"], x["version"], x.get("contentHash", "")))
        value["relations"] = sorted(
            value["relations"],
            key=lambda x: (
                x["relationDomain"], x["relationType"],
                x["from"]["entityType"], x["from"]["entityId"], x["from"]["version"],
                x["to"]["entityType"], x["to"]["entityId"], x["to"]["version"],
            ),
        )
        value["assumptions"] = sorted(value["assumptions"])
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def stable_fingerprint(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()


class EventStore(Protocol):
    def add_event(self, event: Event) -> Event: ...
    def events(self, project_id: str | None = None) -> list[Event]: ...


class DerivationLedger:
    EVENT_TYPE = "DERIVATION_RECORDED"
    EVENT_SOURCE = "H001_DERIVATION_INTEGRITY"

    def __init__(self, store: EventStore):
        self.store = store

    def list(self, project_id: str) -> list[DerivationRecord]:
        _required_text(project_id, "project_id")
        result: list[DerivationRecord] = []
        ids: dict[str, DerivationRecord] = {}
        for event in self.store.events(project_id):
            if event.type != self.EVENT_TYPE:
                continue
            if not isinstance(event.payload, Mapping):
                raise DerivationValidationError("DERIVATION_RECORDED event payload must be an object")
            payload = event.payload.get("derivation")
            if not isinstance(payload, Mapping):
                raise DerivationValidationError("DERIVATION_RECORDED event missing valid derivation object")
            record = DerivationRecord.from_dict(payload)
            prior_id = ids.get(record.id)
            if prior_id is not None:
                if prior_id == record:
                    continue
                raise DerivationValidationError(f"historical derivation id conflict: {record.id}")
            ids[record.id] = record
            result.append(record)
        return result

    def record(self, project_id: str, record: DerivationRecord, *, actor: str = "system") -> DerivationRecord:
        _required_text(project_id, "project_id"); _required_text(actor, "actor")
        if not isinstance(record, DerivationRecord):
            raise DerivationValidationError("record must be DerivationRecord")
        for existing in self.list(project_id):
            if existing.id == record.id:
                if existing == record:
                    return existing  # idempotent replay, no duplicate event
                raise DerivationValidationError(f"derivation id already exists with different content: {record.id}")
        self.store.add_event(Event(None, now_iso(), project_id, self.EVENT_TYPE, {"derivation": record.to_dict()}, actor, self.EVENT_SOURCE))
        return record

    def why(self, project_id: str, output: VersionedRef) -> list[DerivationRecord]:
        """Return every recorded justification path for output, deterministically and cycle-bounded."""
        records = self.list(project_id)
        by_output: dict[VersionedRef, list[DerivationRecord]] = {}
        for record in records:
            by_output.setdefault(record.output, []).append(record)
        for alternatives in by_output.values():
            alternatives.sort(key=lambda record: record.id)

        result: list[DerivationRecord] = []
        visited_records: set[str] = set()

        def visit(ref: VersionedRef, active_refs: frozenset[VersionedRef]) -> None:
            if ref in active_refs:
                return
            next_active = active_refs | {ref}
            for record in by_output.get(ref, ()):
                if record.id not in visited_records:
                    visited_records.add(record.id)
                    result.append(record)
                for input_ref in record.inputs:
                    visit(input_ref, next_active)

        visit(output, frozenset())
        return result

    def explain(self, project_id: str, output: VersionedRef) -> dict[str, Any]:
        records = self.why(project_id, output)
        derived = {r.output for r in records}
        leaves = sorted({i for r in records for i in r.inputs if i not in derived}, key=lambda x:(x.entity_type,x.entity_id,x.version))
        return {"output": output.to_dict(), "records": [r.to_dict() for r in records], "leaf_inputs": [x.to_dict() for x in leaves]}

    def dependency_checks(self, project_id: str, current_versions: Mapping[tuple[str, str], int]) -> list[dict[str, Any]]:
        """Observe dependency availability/version only; never infer STALE or mutate."""
        checks=[]
        seen=set()
        for record in self.list(project_id):
            for ref in record.inputs:
                marker=(record.id,ref)
                if marker in seen: continue
                seen.add(marker)
                current=current_versions.get(ref.key())
                if current is None:
                    checks.append({"record_id":record.id,"reference":ref.to_dict(),"code":"MISSING_DEPENDENCY"})
                elif isinstance(current,bool) or not isinstance(current,int) or current < 1:
                    raise DerivationValidationError("current versions must be positive integers")
                elif current != ref.version:
                    checks.append({"record_id":record.id,"reference":ref.to_dict(),"current_version":current,"code":"VERSION_MISMATCH"})
        return checks

    def version_mismatches(self, project_id: str, current_versions: Mapping[tuple[str, str], int]) -> list[dict[str, Any]]:
        return [x for x in self.dependency_checks(project_id,current_versions) if x["code"]=="VERSION_MISMATCH"]

    def integrity_checks(self, project_id: str, current_refs: Mapping[tuple[str, str], VersionedRef]) -> list[dict[str, Any]]:
        """Compare exact dependency identity without inferring validity or taking action."""
        checks: list[dict[str, Any]] = []
        for record in self.list(project_id):
            for expected in record.inputs:
                current = current_refs.get(expected.key())
                if current is None:
                    checks.append({"record_id": record.id, "reference": expected.to_dict(), "code": "MISSING_DEPENDENCY"})
                    continue
                if not isinstance(current, VersionedRef) or current.key() != expected.key():
                    raise DerivationValidationError("current_refs values must be matching VersionedRef values")
                if current.version != expected.version:
                    checks.append({"record_id": record.id, "reference": expected.to_dict(), "current": current.to_dict(), "code": "VERSION_MISMATCH"})
                elif expected.content_hash is None and current.content_hash is None:
                    checks.append({"record_id": record.id, "reference": expected.to_dict(), "current": current.to_dict(), "code": "IDENTITY_UNVERIFIABLE"})
                elif expected.content_hash is None or current.content_hash is None:
                    checks.append({"record_id": record.id, "reference": expected.to_dict(), "current": current.to_dict(), "code": "IDENTITY_UNCERTAIN"})
                elif expected.content_hash != current.content_hash:
                    checks.append({"record_id": record.id, "reference": expected.to_dict(), "current": current.to_dict(), "code": "CONTENT_HASH_MISMATCH"})
        return checks

__all__=["DerivationValidationError","VersionedRef","TypedRelation","DerivationRecord","DerivationLedger","RELATION_DOMAINS","RELATION_TYPES"]
