"""Corpus Validator — LAB-003: desconocido antes que inventado."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .sandbox_ledger import SandboxEvent, SandboxEventType, SandboxLedger


class CorpusValidationStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class CorpusValidationResult:
    status: CorpusValidationStatus
    required_sources: int
    available_sources: int
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status.value, "requiredSources": self.required_sources, "availableSources": self.available_sources, "message": self.message}


class CorpusValidator:
    def __init__(self, ledger: SandboxLedger, min_sources: int = 3):
        self.ledger = ledger
        self.min_sources = min_sources

    def validate(self, project_id: str, corpus: list[str]) -> CorpusValidationResult:
        available = len(corpus)
        if available < self.min_sources:
            result = CorpusValidationResult(CorpusValidationStatus.INSUFFICIENT, self.min_sources, available, f"Cannot generate: insufficient corpus. Required: {self.min_sources}, Available: {available}")
            self.ledger.record(SandboxEvent(SandboxEventType.CORPUS_INSUFFICIENT, datetime.now(timezone.utc).isoformat(), project_id, result.to_dict()))
            return result
        result = CorpusValidationResult(CorpusValidationStatus.SUFFICIENT, self.min_sources, available, f"Corpus sufficient: {available} sources available")
        self.ledger.record(SandboxEvent(SandboxEventType.CORPUS_VALIDATED, datetime.now(timezone.utc).isoformat(), project_id, result.to_dict()))
        return result


__all__ = ["CorpusValidator", "CorpusValidationResult", "CorpusValidationStatus"]
