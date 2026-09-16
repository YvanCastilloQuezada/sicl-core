from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .v11 import Alternative, Comparison, Evaluation, Recommendation

STAGES = {"DRAFT", "ACTIVE", "PRELIMINARY_DESIGN", "CLOSED"}
DIRECTIONS = {"MAXIMIZE", "MINIMIZE"}
KNOWLEDGE_STATES = {"UNKNOWN", "CONFLICTING", "INSUFFICIENT", "OBSERVED"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Project:
    project_id: str
    name: str
    stage: str = "DRAFT"
    version: int = 1
    objectives: dict[str, "Objective"] = field(default_factory=dict)
    constraints: dict[str, "Constraint"] = field(default_factory=dict)
    roles: dict[str, "Role"] = field(default_factory=dict)
    facts: dict[str, "Fact"] = field(default_factory=dict)
    assumptions: dict[str, "Assumption"] = field(default_factory=dict)
    preferences: dict[str, "Preference"] = field(default_factory=dict)
    decisions: dict[str, "Decision"] = field(default_factory=dict)
    human_reviews: dict[str, "HumanReview"] = field(default_factory=dict)
    alternatives: dict[str, Alternative] = field(default_factory=dict)
    evaluations: dict[str, Evaluation] = field(default_factory=dict)
    comparisons: dict[str, Comparison] = field(default_factory=dict)
    recommendations: dict[str, Recommendation] = field(default_factory=dict)


@dataclass(frozen=True)
class Objective:
    objective_id: str
    project_id: str
    key: str
    direction: str
    value: str
    version: int = 1


@dataclass(frozen=True)
class Constraint:
    constraint_id: str
    project_id: str
    key: str
    operator: str
    value: str
    unit: str = ""
    hard: bool = True
    version: int = 1


@dataclass(frozen=True)
class Role:
    role_id: str
    project_id: str
    name: str
    actor: str
    version: int = 1


@dataclass(frozen=True)
class Fact:
    fact_id: str
    project_id: str
    statement: str
    source: str = ""
    version: int = 1


@dataclass(frozen=True)
class Assumption:
    assumption_id: str
    project_id: str
    statement: str
    basis: str = ""
    version: int = 1


@dataclass(frozen=True)
class Preference:
    preference_id: str
    project_id: str
    statement: str
    actor: str
    version: int = 1


@dataclass(frozen=True)
class Decision:
    decision_id: str
    project_id: str
    statement: str
    actor: str
    authority: str
    version: int = 1


@dataclass(frozen=True)
class HumanReview:
    review_id: str
    project_id: str
    actor: str
    timestamp: str
    review: str
    reason: str
    authority: str
    status: str = "APPROVED"
    version: int = 1


@dataclass(frozen=True)
class Event:
    id: int | None
    timestamp: str
    project_id: str
    type: str
    payload: dict[str, Any]
    actor: str
    source: str
