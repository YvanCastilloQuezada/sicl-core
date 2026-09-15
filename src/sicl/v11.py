from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ALTERNATIVE_STATUSES = {"GENERATED", "PROPOSED", "FEASIBLE", "REJECTED", "SELECTED", "ARCHIVED"}
EVALUATION_SOURCES = {"USER_INPUT", "AI_INFERENCE", "SIMULATION", "FACT", "ASSUMPTION", "EXPERT_SYSTEM"}
RECOMMENDATION_STATUSES = {"PENDING_APPROVAL", "APPROVED", "REJECTED"}


@dataclass
class Alternative:
    alternative_id: str
    project_id: str
    name: str
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    status: str = "GENERATED"
    version: int = 1
    source: str = "USER_COMMAND"

    def __post_init__(self) -> None:
        self.name = self.name.upper()
        if self.status not in ALTERNATIVE_STATUSES:
            raise ValueError(f"Invalid alternative status: {self.status}")


@dataclass(frozen=True)
class Evaluation:
    evaluation_id: str
    alternative_id: str
    objective_id: str
    value: float
    unit: str = ""
    confidence: float = 1.0
    source: str = "USER_INPUT"
    version: int = 1

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.source not in EVALUATION_SOURCES:
            raise ValueError(f"Invalid evaluation source: {self.source}")


@dataclass(frozen=True)
class Comparison:
    comparison_id: str
    project_id: str
    alternative_ids: list[str]
    evaluations: list[Evaluation] = field(default_factory=list)
    tradeoffs: dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def __post_init__(self) -> None:
        if len(self.alternative_ids) < 2:
            raise ValueError("Comparison requires at least 2 alternatives")


@dataclass(frozen=True)
class Recommendation:
    recommendation_id: str
    comparison_id: str
    recommended_alternative_id: str
    reason: str
    confidence: float
    status: str = "PENDING_APPROVAL"
    version: int = 1

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.status not in RECOMMENDATION_STATUSES:
            raise ValueError(f"Invalid recommendation status: {self.status}")
