"""A-002 semantic model: explicit knowledge states and auditable evidence.

Design rule (v1.4.1):
- `KnowledgeItem` only carries the *declared* state, exactly as supplied.
- The *effective* state (post-validation) is produced by the engine and
  exposed via `ItemAssessment` on `SufficiencyResult`. The item never lies
  about its own assessment.
- Normative applicability is NOT a property of a knowledge item. It lives
  in `ApplicabilityDeclaration` on the request, because applicability is a
  relation between (regulation, jurisdiction, entity), not an intrinsic
  attribute of a datum.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import hashlib
import json

from ..domain import SpatialScope
from .authority import HumanAuthorityRef
from .policy import PolicyIdentity


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


class ApplicabilityStatus(str, Enum):
    ESTABLISHED = "ESTABLISHED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"


class EvidenceVerificationLevel(str, Enum):
    ABSENT = "ABSENT"
    HASH_FORMAT_VALID = "HASH_FORMAT_VALID"
    CONTENT_HASH_MATCHES_DECLARED = "CONTENT_HASH_MATCHES_DECLARED"
    SUPPORT_SEMANTICALLY_VERIFIED = "SUPPORT_SEMANTICALLY_VERIFIED"


@dataclass(frozen=True)
class KnowledgeItem:
    """A declared knowledge fact.

    The `state` here is what the *caller* declares. It is NOT the effective
    state — the engine produces the effective state separately.
    """

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
    """A reference to evidence whose hash is derived from its statement.

    The constructor enforces `hash == sha256(statement)`. Therefore, any
    instance that exists has, at minimum, `CONTENT_HASH_MATCHES_DECLARED`
    verification level. `SUPPORT_SEMANTICALLY_VERIFIED` is out of A-002 scope.
    """

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
        if self.hash != hashlib.sha256(self.statement.encode("utf-8")).hexdigest():
            raise ValueError("evidence hash does not match statement")
        if self.version < 1:
            raise ValueError("evidence version must be positive")

    @classmethod
    def from_statement(
        cls,
        evidence_id: str,
        statement: str,
        source_type: str,
        project_id: str,
        **kwargs: Any,
    ) -> "EvidenceRef":
        digest = hashlib.sha256(statement.encode("utf-8")).hexdigest()
        return cls(evidence_id, statement, source_type, digest, project_id, **kwargs)

    def guaranteed_verification_level(self) -> EvidenceVerificationLevel:
        """Return the level guaranteed by construction.

        Documented invariant: since __post_init__ enforces hash == sha256(statement),
        any existing EvidenceRef is at CONTENT_HASH_MATCHES_DECLARED.
        """
        return EvidenceVerificationLevel.CONTENT_HASH_MATCHES_DECLARED

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
class ApplicabilityDeclaration:
    """Explicit applicability declaration for a (field, jurisdiction, regulation).

    Kept on the *request*, not on the item, because applicability is a
    relation, not an intrinsic attribute.
    """

    field: str
    jurisdiction: str
    regulation_id: str
    status: ApplicabilityStatus

    def __post_init__(self) -> None:
        if not self.field.strip():
            raise ValueError("field must be non-empty")
        if not self.jurisdiction.strip():
            raise ValueError("jurisdiction must be non-empty")
        if not self.regulation_id.strip():
            raise ValueError("regulation_id must be non-empty")


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
    require_human_authority: bool = False
    applicability_required: bool = False

    def applies_to(
        self,
        scale: SpatialScope | None,
        context: str | None,
        jurisdiction: str | None,
    ) -> bool:
        if self.applicable_context is not None and self.applicable_context != context:
            return False
        if self.jurisdiction_required and not (jurisdiction and jurisdiction.strip()):
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "requiredStates": [s.value for s in self.required_states],
            "blocking": self.blocking,
            "applicableScales": [s.value for s in self.applicable_scales],
            "applicableContext": self.applicable_context,
            "jurisdictionRequired": self.jurisdiction_required,
            "reason": self.reason,
            "allowAssumed": self.allow_assumed,
            "requireHumanAuthority": self.require_human_authority,
            "applicabilityRequired": self.applicability_required,
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
    policy: PolicyIdentity | None = None
    human_authority_ref: HumanAuthorityRef | None = None
    applicability: tuple[ApplicabilityDeclaration, ...] = ()

    def canonical(self) -> dict[str, Any]:
        return {
            "projectId": self.project_id,
            "operation": self.operation,
            "knowledge": [
                item.to_dict()
                for item in sorted(
                    self.knowledge,
                    key=lambda x: json.dumps(x.to_dict(), sort_keys=True, separators=(",", ":")),
                )
            ],
            "requirements": [r.to_dict() for r in sorted(self.requirements, key=lambda x: x.field)],
            "evidence": [e.to_dict() for e in sorted(self.evidence, key=lambda x: (x.evidence_id, x.version))],
            "applicability": [
                {
                    "field": a.field,
                    "jurisdiction": a.jurisdiction,
                    "regulationId": a.regulation_id,
                    "status": a.status.value,
                }
                for a in sorted(self.applicability, key=lambda x: (x.field, x.jurisdiction, x.regulation_id))
            ],
            "scale": self.scale.value if self.scale else None,
            "context": self.context,
            "jurisdiction": self.jurisdiction,
            "policyAllowAssumptions": self.policy_allow_assumptions,
            "policy": self.policy.to_dict() if self.policy else None,
            "humanAuthority": self.human_authority_ref.to_dict() if self.human_authority_ref else None,
        }

    def fingerprint(self) -> str:
        canonical = json.dumps(self.canonical(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ItemAssessment:
    """Post-validation assessment of a single field.

    This is the honest carrier of `declared_state` vs `effective_state` and
    the reason for any downgrade.
    """

    field: str
    declared_state: KnowledgeState
    effective_state: KnowledgeState
    downgrade_reason: str = ""
    evidence_ids: tuple[str, ...] = ()
    evidence_level: EvidenceVerificationLevel = EvidenceVerificationLevel.ABSENT
    applicability_status: ApplicabilityStatus = ApplicabilityStatus.UNKNOWN
    blocking: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "declaredState": self.declared_state.value,
            "effectiveState": self.effective_state.value,
            "downgradeReason": self.downgrade_reason,
            "evidenceIds": list(self.evidence_ids),
            "evidenceLevel": self.evidence_level.value,
            "applicabilityStatus": self.applicability_status.value,
            "blocking": self.blocking,
        }


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
    evidence_levels: tuple[tuple[str, str], ...]
    coverage: tuple[str, ...]
    reason_codes: tuple[str, ...]
    conditional_reasons: tuple[str, ...]

    assessments: tuple[ItemAssessment, ...]

    request_fingerprint: str
    evaluation_id: str = ""
    identity_payload: dict[str, Any] | None = None
    policy: PolicyIdentity | None = None
    human_authority_ref: HumanAuthorityRef | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "projectId": self.project_id,
            "operation": self.operation,
            "overallStatus": self.overall_status.value,
            "known": list(self.known),
            "observed": list(self.observed),
            "assumed": list(self.assumed),
            "unknown": list(self.unknown),
            "missing": list(self.missing),
            "conflicting": list(self.conflicting),
            "blockingItems": list(self.blocking_items),
            "nonBlockingItems": list(self.non_blocking_items),
            "questionsForHuman": list(self.questions_for_human),
            "assumptionsUsed": list(self.assumptions_used),
            "evidenceRefs": list(self.evidence_refs),
            "evidenceLevels": [list(x) for x in self.evidence_levels],
            "coverage": list(self.coverage),
            "reasonCodes": list(self.reason_codes),
            "conditionalReasons": list(self.conditional_reasons),
            "assessments": [a.to_dict() for a in self.assessments],
            "requestFingerprint": self.request_fingerprint,
            "evaluationId": self.evaluation_id,
            "identityPayload": self.identity_payload,
            "policy": self.policy.to_dict() if self.policy else None,
            "humanAuthorityRef": self.human_authority_ref.to_dict() if self.human_authority_ref else None,
        }

    @property
    def permits_h005(self) -> bool:
        return self.overall_status is SufficiencyStatus.SUFFICIENT

    def effective_state_of(self, field: str) -> KnowledgeState | None:
        for a in self.assessments:
            if a.field == field:
                return a.effective_state
        return None
