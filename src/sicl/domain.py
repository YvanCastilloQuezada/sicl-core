from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any

from .v11 import Alternative, Comparison, Evaluation, Recommendation
from .simulation import Simulation


class MultiobjectiveState(str, Enum):
    EXECUTED = "EXECUTED"
    INSUFFICIENT = "INSUFFICIENT"

STAGES = {"DRAFT", "ACTIVE", "PRELIMINARY_DESIGN", "CLOSED"}
DIRECTIONS = {"MAXIMIZE", "MINIMIZE"}
KNOWLEDGE_STATES = {"UNKNOWN", "CONFLICTING", "INSUFFICIENT", "OBSERVED"}


class SpatialScope(str, Enum):
    PAIS = "pais"
    REGION = "region"
    PROVINCIA_METROPOLI = "provincia_metropoli"
    CIUDAD_DISTRITO = "ciudad_distrito"
    BARRIO_SECTOR = "barrio_sector"
    PARCELA_SITIO = "parcela_sitio"
    EDIFICIO = "edificio"
    ESPACIO = "espacio"
    OBJETO = "objeto"

    @property
    def label(self) -> str:
        return {
            SpatialScope.PAIS: "País",
            SpatialScope.REGION: "Región",
            SpatialScope.PROVINCIA_METROPOLI: "Provincia / Metrópoli",
            SpatialScope.CIUDAD_DISTRITO: "Ciudad / Distrito",
            SpatialScope.BARRIO_SECTOR: "Barrio / Sector",
            SpatialScope.PARCELA_SITIO: "Parcela / Sitio",
            SpatialScope.EDIFICIO: "Edificio",
            SpatialScope.ESPACIO: "Espacio",
            SpatialScope.OBJETO: "Objeto",
        }[self]


class TemporalScope(str, Enum):
    PROYECTO = "proyecto"
    CORTO_PLAZO = "corto_plazo"
    MEDIANO_PLAZO = "mediano_plazo"
    LARGO_PLAZO = "largo_plazo"
    ESCENARIO_2030 = "escenario_2030"
    ESCENARIO_2040 = "escenario_2040"
    ESCENARIO_2050 = "escenario_2050"

    @property
    def label(self) -> str:
        return {
            TemporalScope.PROYECTO: "Proyecto",
            TemporalScope.CORTO_PLAZO: "Corto plazo",
            TemporalScope.MEDIANO_PLAZO: "Mediano plazo",
            TemporalScope.LARGO_PLAZO: "Largo plazo",
            TemporalScope.ESCENARIO_2030: "Escenario 2030",
            TemporalScope.ESCENARIO_2040: "Escenario 2040",
            TemporalScope.ESCENARIO_2050: "Escenario 2050",
        }[self]


class EvidenceType(str, Enum):
    DOCUMENT = "DOCUMENT"
    OBSERVATION = "OBSERVATION"
    MEASUREMENT = "MEASUREMENT"
    REFERENCE = "REFERENCE"
    TESTIMONY = "TESTIMONY"
    NORMATIVE = "NORMATIVE"
    OTHER = "OTHER"


class SourceType(str, Enum):
    OFFICIAL = "OFFICIAL"
    SECONDARY = "SECONDARY"
    USER_PROVIDED = "USER_PROVIDED"
    UNKNOWN = "UNKNOWN"


class PlanningInstrumentType(str, Enum):
    PLAN_NACIONAL = "PLAN_NACIONAL"
    PLAN_REGIONAL = "PLAN_REGIONAL"
    PLAN_PROVINCIAL = "PLAN_PROVINCIAL"
    PLAN_METROPOLITANO = "PLAN_METROPOLITANO"
    PLAN_URBANO = "PLAN_URBANO"
    PLAN_LOCAL = "PLAN_LOCAL"
    PLAN_SECTORIAL = "PLAN_SECTORIAL"
    POLITICA_NACIONAL = "POLITICA_NACIONAL"
    INSTRUMENTO_TERRITORIAL = "INSTRUMENTO_TERRITORIAL"
    OTRO = "OTRO"


class PlanningInstrumentStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REPEALED = "REPEALED"
    UNKNOWN = "UNKNOWN"


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
    evidence: dict[str, "Evidence"] = field(default_factory=dict)
    sources: dict[str, "Source"] = field(default_factory=dict)
    simulations: dict[str, Simulation] = field(default_factory=dict)
    multiobjective_results: dict[str, "MultiobjectiveResult"] = field(default_factory=dict)
    planning_instruments: dict[str, "PlanningInstrument"] = field(default_factory=dict)
    # spatial_scope remains optional: null means that no spatial scale is declared.
    spatial_scope: SpatialScope | None = None
    temporal_scope: TemporalScope = TemporalScope.PROYECTO


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


@dataclass(frozen=True)
class MultiobjectiveResult:
    multiobjective_id: str
    project_id: str
    method: str
    method_version: str
    objectives: list[str]
    alternatives: list[str]
    pareto_front: list[str]
    dominated: list[str]
    incomplete: list[str]
    tradeoffs: dict[str, Any]
    state: MultiobjectiveState
    inputs_hash: str
    created_at: datetime
    version: int = 1


@dataclass(frozen=True)
class PlanningInstrument:
    instrument_id: str
    project_id: str | None
    instrument_type: PlanningInstrumentType
    name: str
    jurisdiction: str
    authority: str | None
    approval_date: date | None
    validity_period: str | None
    scope_applicable: list[SpatialScope]
    status: PlanningInstrumentStatus
    objectives: list[str]
    url: str | None
    summary: str | None
    source: str
    version: int = 1


@dataclass(frozen=True)
class Source:
    """Optional provenance record referenced by one or more Evidence items."""

    source_id: str
    project_id: str
    source_type: SourceType
    title: str
    url: str | None = None
    version: int = 1


@dataclass(frozen=True)
class Evidence:
    """Immutable declaration captured from a source, observation, or testimony.

    Evidence records what was captured; it does not become a Fact or Assumption
    automatically. A missing hash is deterministically derived from statement.
    """

    evidence_id: str
    project_id: str
    source_id: str | None
    statement: str
    evidence_type: EvidenceType
    captured_at: datetime
    method_version: str
    evidence_url: str | None
    evidence_hash: str | None
    state: str
    version: int = 1
