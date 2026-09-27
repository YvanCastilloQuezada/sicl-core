"""A-002 Input Sufficiency: deterministic, operation-specific, fail-closed."""
from .engine import SufficiencyEngine
from .gate import A002H005Gate, GateDecision
from .model import EvidenceRef, KnowledgeItem, KnowledgeState, OperationRequirement, SufficiencyRequest, SufficiencyResult, SufficiencyStatus
from .persistence import SufficiencyStateStore
from .requirements import preliminary_building_massing_requirements, requirements_for

__all__ = ["SufficiencyEngine", "A002H005Gate", "GateDecision", "SufficiencyStateStore", "EvidenceRef", "KnowledgeItem", "KnowledgeState", "OperationRequirement", "SufficiencyRequest", "SufficiencyResult", "SufficiencyStatus", "preliminary_building_massing_requirements", "requirements_for"]
