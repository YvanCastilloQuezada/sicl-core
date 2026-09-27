"""A-002 semantic model: explicit knowledge states and auditable evidence."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping
import hashlib
import json

from ..domain import SpatialScope


class KnowledgeState(str, Enum):
    KNOWN = "KNOWN"
    OBSERVED = "OBSERVED"
    ASSUMED = "ASSUMED"
    UNKNOWN = "UNKNOWN"
    MISSING = "MISSING"
    CONFLICTING = "CONFLICTING"


class SufficiencyStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    CONDITIONALLY_SUFFICIENT = "CONDITIONALLY_SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class KnowledgeItem:
    field: str
    value: Any
    state: KnowledgeState
    evidence_refs: tuple[str, ...] = ()
    scale: SpatialScope | None = None
    jurisdiction: str | None = None
    context: str | None = None
    version: int = 1
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.field.strip():
            raise ValueError("field must be non-empty")
        if self.version < 1:
            raise ValueError("version must be positive")
        if self.state is KnowledgeState.ASSUMED and not self.reason.strip():
            raise ValueError("ASSUMED items require an explicit reason")

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "value": self.value,
            "state": self.state.value,
            "evidenceRefs": list(self.evidence_refs),
            "scale": self.scale.value if self.scale else None,
            "jurisdiction": self.jurisdiction,
            "context": self.context,
            "version": self.version,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    statement: str
    source_type: str
    hash: str
    project_id: str
    scale: SpatialScope | None = None
    jurisdiction: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        if not self.evidence_id.strip() or not self.statement.strip():
            raise ValueError("evidence_id and statement are required")
        if not self.hash.strip():
            raise ValueError("evidence hash is required")
        expected = hashlib.sha256(self.statement.encode("utf-8")).hexdigest()
        if self.hash != expected:
            raise ValueError("evidence hash does not match statement")
        if self.version < 1:
            raise ValueError("evidence version must be positive")

    @classmethod
    def from_statement(cls, evidence_id: str, statement: str, source_type: str, project_id: str, **kwargs: Any) -> "EvidenceRef":
        digest = hashlib.sha256(statement.encode("utf-8")).hexdigest()
        return cls(evidence_id, statement, source_type, digest, project_id, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidenceId": self.evidence_id,
            "statement": self.statement,
            "sourceType": self.source_type,
            "hash": self.hash,
            "projectId": self.project_id,
            "scale": self.scale.value if self.scale else None,
            "jurisdiction": self.jurisdiction,
            "version": self.version,
        }


@dataclass(frozen=True)
class OperationRequirement:
    field: str
    required_states: tuple[KnowledgeState, ...]
    blocking: bool
    applicable_scales: tuple[SpatialScope, ...] = ()
    applicable_context: str | None = None
    jurisdiction_required: bool = False
    reason: str = ""
    allow_assumed: bool = False

    def applies_to(self, scale: SpatialScope | None, context: str | None, jurisdiction: str | None) -> bool:
        if self.applicable_context is not None and self.applicable_context != context:
            return False
        return not self.jurisdiction_required or bool(jurisdiction and jurisdiction.strip())

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "requiredStates": [item.value for item in self.required_states],
            "blocking": self.blocking,
            "applicableScales": [item.value for item in self.applicable_scales],
            "applicableContext": self.applicable_context,
            "jurisdictionRequired": self.jurisdiction_required,
            "reason": self.reason,
            "allowAssumed": self.allow_assumed,
        }


@dataclass(frozen=True)
class SufficiencyRequest:
    project_id: str
    operation: str
    knowledge: tuple[KnowledgeItem, ...]
    requirements: tuple[OperationRequirement, ...]
    evidence: tuple[EvidenceRef, ...] = ()
    scale: SpatialScope | None = None
    context: str | None = None
    jurisdiction: str | None = None
    policy_allow_assumptions: bool = False

    def canonical(self) -> dict[str, Any]:
        return {
            "projectId": self.project_id,
            "operation": self.operation,
            "knowledge": [item.to_dict() for item in sorted(self.knowledge, key=lambda x: json.dumps(x.to_dict(), sort_keys=True, separators=(",", ":")))],
            "requirements": [item.to_dict() for item in sorted(self.requirements, key=lambda x: x.field)],
            "evidence": [item.to_dict() for item in sorted(self.evidence, key=lambda x: (x.evidence_id, x.version))],
            "scale": self.scale.value if self.scale else None,
            "context": self.context,
            "jurisdiction": self.jurisdiction,
            "policyAllowAssumptions": self.policy_allow_assumptions,
        }

    def fingerprint(self) -> str:
        return hashlib.sha256(json.dumps(self.canonical(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class SufficiencyResult:
    project_id: str
    operation: str
    overall_status: SufficiencyStatus
    known: tuple[str, ...]
    observed: tuple[str, ...]
    assumed: tuple[str, ...]
    unknown: tuple[str, ...]
    missing: tuple[str, ...]
    conflicting: tuple[str, ...]
    blocking_items: tuple[str, ...]
    non_blocking_items: tuple[str, ...]
    questions_for_human: tuple[str, ...]
    assumptions_used: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    coverage: tuple[str, ...]
    reason_codes: tuple[str, ...]
    request_fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return {"projectId": self.project_id, "operation": self.operation, "overallStatus": self.overall_status.value, "known": list(self.known), "observed": list(self.observed), "assumed": list(self.assumed), "unknown": list(self.unknown), "missing": list(self.missing), "conflicting": list(self.conflicting), "blockingItems": list(self.blocking_items), "nonBlockingItems": list(self.non_blocking_items), "questionsForHuman": list(self.questions_for_human), "assumptionsUsed": list(self.assumptions_used), "evidenceRefs": list(self.evidence_refs), "coverage": list(self.coverage), "reasonCodes": list(self.reason_codes), "requestFingerprint": self.request_fingerprint}

    @property
    def permits_h005(self) -> bool:
        return self.overall_status is SufficiencyStatus.SUFFICIENT
