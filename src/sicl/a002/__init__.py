"""A-002 Input Sufficiency: deterministic, operation-specific, fail-closed."""
from .engine import SufficiencyEngine
from .gate import A002H005Gate, GateDecision
from .model import (
    ApplicabilityDeclaration,
    ApplicabilityStatus,
    EvidenceRef,
    EvidenceVerificationLevel,
    ItemAssessment,
    KnowledgeItem,
    KnowledgeState,
    OperationRequirement,
    SufficiencyRequest,
    SufficiencyResult,
    SufficiencyStatus,
)
from .policy import PolicyIdentity
from .identity import EvaluationIdentityPayload, compute_evaluation_id
from .authority import HumanAuthorityRef
from .persistence import SufficiencyStateStore
from .requirements import (
    policy_for,
    preliminary_building_massing_requirements,
    requirements_for,
)

__all__ = [
    "A002H005Gate",
    "ApplicabilityDeclaration",
    "ApplicabilityStatus",
    "EvaluationIdentityPayload",
    "EvidenceRef",
    "EvidenceVerificationLevel",
    "GateDecision",
    "HumanAuthorityRef",
    "ItemAssessment",
    "KnowledgeItem",
    "KnowledgeState",
    "OperationRequirement",
    "PolicyIdentity",
    "SufficiencyEngine",
    "SufficiencyRequest",
    "SufficiencyResult",
    "SufficiencyStateStore",
    "SufficiencyStatus",
    "compute_evaluation_id",
    "policy_for",
    "preliminary_building_massing_requirements",
    "requirements_for",
]
