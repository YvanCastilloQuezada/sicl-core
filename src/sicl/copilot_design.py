"""CP-05 structured architectural/design reasoning contracts.

This module captures a traceable brief and alternatives. It does not create geometry,
compute performance, or write canonical ARKI project state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .copilot_contract import CopilotFact, FactStatus


class CriterionDirection(str, Enum):
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"
    TARGET = "TARGET"


@dataclass(frozen=True)
class DesignCriterion:
    criterion_id: str
    name: str
    description: str
    weight: float
    direction: CriterionDirection
    target: float | None = None
    unit: str = ""
    source_fact_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.criterion_id.strip() or not self.name.strip():
            raise ValueError("criterion_id and name are required")
        if not 0 <= self.weight <= 1:
            raise ValueError("criterion weight must be in [0,1]")
        if self.direction is CriterionDirection.TARGET and self.target is None:
            raise ValueError("TARGET criterion requires target value")


@dataclass(frozen=True)
class AlternativeScore:
    criterion_id: str
    value: float
    normalized_score: float | None = None
    explanation: str = ""
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.criterion_id.strip():
            raise ValueError("criterion_id required")
        if self.normalized_score is not None and not 0 <= self.normalized_score <= 1:
            raise ValueError("normalized_score must be in [0,1]")


@dataclass(frozen=True)
class DesignAlternative:
    alternative_id: str
    title: str
    concept: str
    scores: tuple[AlternativeScore, ...] = ()
    unresolved: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.alternative_id.strip() or not self.title.strip() or not self.concept.strip():
            raise ValueError("alternative id, title, and concept are required")
        score_ids = [s.criterion_id for s in self.scores]
        if len(score_ids) != len(set(score_ids)):
            raise ValueError("duplicate score criterion_id")


@dataclass(frozen=True)
class DesignBrief:
    brief_id: str
    project_id: str
    created_at: str
    title: str
    purpose: str
    facts: tuple[CopilotFact, ...]
    criteria: tuple[DesignCriterion, ...]
    alternatives: tuple[DesignAlternative, ...] = ()
    context_refs: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    next_questions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name, value in (("brief_id", self.brief_id), ("project_id", self.project_id),
                                  ("title", self.title), ("purpose", self.purpose)):
            if not value.strip():
                raise ValueError(f"{field_name} is required")
        from datetime import datetime
        try:
            datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("created_at must be ISO-8601") from exc
        criterion_ids = [c.criterion_id for c in self.criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("duplicate criterion_id")
        alternative_ids = [a.alternative_id for a in self.alternatives]
        if len(alternative_ids) != len(set(alternative_ids)):
            raise ValueError("duplicate alternative_id")
        if self.criteria and abs(sum(c.weight for c in self.criteria) - 1.0) > 1e-6:
            raise ValueError("criterion weights must sum to 1")
        known = set(criterion_ids)
        for alternative in self.alternatives:
            unknown = [s.criterion_id for s in alternative.scores if s.criterion_id not in known]
            if unknown:
                raise ValueError("alternative score references unknown criteria: " + ", ".join(unknown))
