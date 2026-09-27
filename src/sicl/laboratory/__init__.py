"""Laboratorio de IA hermano del Core, con reglas LAB-001 a LAB-004."""

from .authority_gate import AuthorityGate, AuthorityRequiredError, PromotionResult, PromotionStatus
from .corpus_validator import CorpusValidationResult, CorpusValidationStatus, CorpusValidator
from .deterministic_generator import DeterministicGenerator, GeneratedAlternative
from .sandbox_ledger import SandboxEvent, SandboxEventType, SandboxLedger

__all__ = [
    "AuthorityGate", "AuthorityRequiredError", "PromotionResult", "PromotionStatus",
    "CorpusValidationResult", "CorpusValidationStatus", "CorpusValidator",
    "DeterministicGenerator", "GeneratedAlternative",
    "SandboxEvent", "SandboxEventType", "SandboxLedger",
]
