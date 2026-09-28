"""A-002 semantic model: explicit knowledge states and auditable evidence."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any
import hashlib, json, re
from ..domain import SpatialScope
from .policy import PolicyIdentity
from .authority import HumanAuthorityRef

class KnowledgeState(str, Enum):
    KNOWN="KNOWN"; OBSERVED="OBSERVED"; ASSUMED="ASSUMED"; UNKNOWN="UNKNOWN"; MISSING="MISSING"; CONFLICTING="CONFLICTING"
class SufficiencyStatus(str, Enum):
    SUFFICIENT="SUFFICIENT"; CONDITIONALLY_SUFFICIENT="CONDITIONALLY_SUFFICIENT"; INSUFFICIENT="INSUFFICIENT"; CONFLICTING="CONFLICTING"; UNKNOWN="UNKNOWN"
class ApplicabilityStatus(str, Enum):
    ESTABLISHED="ESTABLISHED"; NOT_APPLICABLE="NOT_APPLICABLE"; CONFLICTING="CONFLICTING"; UNKNOWN="UNKNOWN"
class EvidenceVerificationLevel(str, Enum):
    ABSENT="ABSENT"; HASH_FORMAT_VALID="HASH_FORMAT_VALID"; CONTENT_HASH_MATCHES_DECLARED="CONTENT_HASH_MATCHES_DECLARED"; SUPPORT_SEMANTICALLY_VERIFIED="SUPPORT_SEMANTICALLY_VERIFIED"

@dataclass(frozen=True)
class KnowledgeItem:
    field: str; value: Any; state: KnowledgeState; evidence_refs: tuple[str,...]=(); scale: SpatialScope|None=None; jurisdiction: str|None=None; context: str|None=None; version: int=1; reason: str=""; applicability: ApplicabilityStatus=ApplicabilityStatus.UNKNOWN
    def __post_init__(self):
        if not self.field.strip(): raise ValueError("field must be non-empty")
        if self.version < 1: raise ValueError("version must be positive")
        if self.state is KnowledgeState.ASSUMED and not self.reason.strip(): raise ValueError("ASSUMED items require an explicit reason")
    @property
    def declared_state(self) -> KnowledgeState: return self.state
    @property
    def effective_state(self) -> KnowledgeState: return self.state
    @property
    def downgrade_reason(self) -> str: return ""
    def to_dict(self): return {"field":self.field,"value":self.value,"state":self.state.value,"declaredState":self.declared_state.value,"effectiveState":self.effective_state.value,"downgradeReason":self.downgrade_reason,"evidenceRefs":list(self.evidence_refs),"scale":self.scale.value if self.scale else None,"jurisdiction":self.jurisdiction,"context":self.context,"version":self.version,"reason":self.reason,"applicability":self.applicability.value}

@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str; statement: str; source_type: str; hash: str; project_id: str; scale: SpatialScope|None=None; jurisdiction: str|None=None; version: int=1
    def __post_init__(self):
        if not self.evidence_id.strip() or not self.statement.strip(): raise ValueError("evidence_id and statement are required")
        if not self.hash.strip(): raise ValueError("evidence hash is required")
        if self.hash != hashlib.sha256(self.statement.encode()).hexdigest(): raise ValueError("evidence hash does not match statement")
        if self.version < 1: raise ValueError("evidence version must be positive")
    @classmethod
    def from_statement(cls,evidence_id,statement,source_type,project_id,**kwargs): return cls(evidence_id,statement,source_type,hashlib.sha256(statement.encode()).hexdigest(),project_id,**kwargs)
    def verification_level(self) -> EvidenceVerificationLevel: return EvidenceVerificationLevel.CONTENT_HASH_MATCHES_DECLARED
    def to_dict(self): return {"evidenceId":self.evidence_id,"statement":self.statement,"sourceType":self.source_type,"hash":self.hash,"projectId":self.project_id,"scale":self.scale.value if self.scale else None,"jurisdiction":self.jurisdiction,"version":self.version}

@dataclass(frozen=True)
class OperationRequirement:
    field: str; required_states: tuple[KnowledgeState,...]; blocking: bool; applicable_scales: tuple[SpatialScope,...]=(); applicable_context: str|None=None; jurisdiction_required: bool=False; reason: str=""; allow_assumed: bool=False; require_human_authority: bool=False; applicability_required: bool=False
    def applies_to(self,scale,context,jurisdiction): return (self.applicable_context is None or self.applicable_context==context) and (not self.jurisdiction_required or bool(jurisdiction and jurisdiction.strip()))
    def to_dict(self): return {"field":self.field,"requiredStates":[x.value for x in self.required_states],"blocking":self.blocking,"applicableScales":[x.value for x in self.applicable_scales],"applicableContext":self.applicable_context,"jurisdictionRequired":self.jurisdiction_required,"reason":self.reason,"allowAssumed":self.allow_assumed,"requireHumanAuthority":self.require_human_authority,"applicabilityRequired":self.applicability_required}

@dataclass(frozen=True)
class SufficiencyRequest:
    project_id: str; operation: str; knowledge: tuple[KnowledgeItem,...]; requirements: tuple[OperationRequirement,...]; evidence: tuple[EvidenceRef,...]=(); scale: SpatialScope|None=None; context: str|None=None; jurisdiction: str|None=None; policy_allow_assumptions: bool=False; policy: PolicyIdentity|None=None; human_authority_ref: HumanAuthorityRef|None=None
    def canonical(self): return {"projectId":self.project_id,"operation":self.operation,"knowledge":[x.to_dict() for x in sorted(self.knowledge,key=lambda x:json.dumps(x.to_dict(),sort_keys=True,separators=(",",":")))],"requirements":[x.to_dict() for x in sorted(self.requirements,key=lambda x:x.field)],"evidence":[x.to_dict() for x in sorted(self.evidence,key=lambda x:(x.evidence_id,x.version))],"scale":self.scale.value if self.scale else None,"context":self.context,"jurisdiction":self.jurisdiction,"policyAllowAssumptions":self.policy_allow_assumptions,"policy":self.policy.to_dict() if self.policy else None,"humanAuthority":self.human_authority_ref.to_dict() if self.human_authority_ref else None}
    def fingerprint(self): return hashlib.sha256(json.dumps(self.canonical(),sort_keys=True,separators=(",",":")).encode()).hexdigest()

@dataclass(frozen=True)
class SufficiencyResult:
    project_id: str; operation: str; overall_status: SufficiencyStatus; known: tuple[str,...]; observed: tuple[str,...]; assumed: tuple[str,...]; unknown: tuple[str,...]; missing: tuple[str,...]; conflicting: tuple[str,...]; blocking_items: tuple[str,...]; non_blocking_items: tuple[str,...]; questions_for_human: tuple[str,...]; assumptions_used: tuple[str,...]; evidence_refs: tuple[str,...]; coverage: tuple[str,...]; reason_codes: tuple[str,...]; request_fingerprint: str; policy: PolicyIdentity|None=None; evaluation_id: str=""; identity_payload: dict[str,Any]|None=None; human_authority_ref: HumanAuthorityRef|None=None; conditional_reasons: tuple[str,...]=(); evidence_levels: tuple[tuple[str,str],...]=()
    def to_dict(self): return {"projectId":self.project_id,"operation":self.operation,"overallStatus":self.overall_status.value,"known":list(self.known),"observed":list(self.observed),"assumed":list(self.assumed),"unknown":list(self.unknown),"missing":list(self.missing),"conflicting":list(self.conflicting),"blockingItems":list(self.blocking_items),"nonBlockingItems":list(self.non_blocking_items),"questionsForHuman":list(self.questions_for_human),"assumptionsUsed":list(self.assumptions_used),"evidenceRefs":list(self.evidence_refs),"evidenceLevels":[list(x) for x in self.evidence_levels],"coverage":list(self.coverage),"reasonCodes":list(self.reason_codes),"conditionalReasons":list(self.conditional_reasons),"requestFingerprint":self.request_fingerprint,"policy":self.policy.to_dict() if self.policy else None,"evaluationId":self.evaluation_id,"identityPayload":self.identity_payload,"humanAuthorityRef":self.human_authority_ref.to_dict() if self.human_authority_ref else None}
    @property
    def permits_h005(self): return self.overall_status is SufficiencyStatus.SUFFICIENT
