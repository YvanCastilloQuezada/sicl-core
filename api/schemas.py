from __future__ import annotations

from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    spatial_scope: str | None = None
    temporal_scope: str = "proyecto"
    actor: str = Field(default="api", min_length=1)


class ProjectUpdateRequest(BaseModel):
    stage: str | None = None
    actor: str = Field(default="api", min_length=1)


class CommandRequest(BaseModel):
    command: str = Field(min_length=1)
    actor: str = Field(default="api", min_length=1)


class APIResponse(BaseModel):
    status: str
    code: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class V1Envelope(BaseModel):
    contract_version: str
    status: str
    code: str
    message: str
    project_id: str | None = None
    observed_version: int | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class CanonicalProjectCreateRequest(BaseModel):
    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    spatial_scope: str | dict[str, Any] | None = None
    temporal_scope: str | dict[str, Any] | None = None
    actor: str = Field(default="api", min_length=1)


class CanonicalCommandRequest(BaseModel):
    command: str = Field(min_length=1)
    actor: str = Field(default="api", min_length=1)


class CanonicalWriteRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    @property
    def payload(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class ActorCreateRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    role: str = Field(min_length=1)
    name: str = Field(min_length=1)
    authority_level: str = Field(min_length=1)
    interests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class PositionCreateRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    subject_type: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    stance: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    conditions: list[str] = Field(default_factory=list)


class CycleCreateRequest(BaseModel):
    cycle_id: str = Field(min_length=1)
    horizon: str = Field(min_length=1)
    start_date: date
    end_date: date | None = None
    assumptions: list[str] = Field(default_factory=list)
    objectives_at_horizon: list[str] = Field(default_factory=list)
    actors_involved: list[str] = Field(default_factory=list)


class ScenarioCreateRequest(BaseModel):
    branch_id: str = Field(min_length=1)
    parent_cycle_id: str | None = None
    scenario_name: str = Field(min_length=1)
    conditions: dict[str, Any] = Field(default_factory=dict)
    objectives: list[str] = Field(default_factory=list)


class ScenarioSelectRequest(BaseModel):
    actor: str = Field(min_length=1)
    authority: str = Field(min_length=1)


class ScenarioEvolutionCreateRequest(BaseModel):
    evolution_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    from_cycle_id: str = Field(min_length=1)
    to_cycle_id: str = Field(min_length=1)


class ScenarioEvolutionApplyRequest(BaseModel):
    actor: str = Field(min_length=1)
    authority: str = Field(min_length=1)


class EvidenceCreateRequest(BaseModel):
    evidence_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    evidence_type: str = Field(min_length=1)
    source_id: str | None = None
    evidence_url: str | None = None
    method_version: str = "API/1.0"
    captured_at: datetime | None = None
    evidence_hash: str | None = None
    state: str = "OBSERVED"


class SourceCreateRequest(BaseModel):
    source_id: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str | None = None


class EvaluationCreateRequest(BaseModel):
    alternative: str | None = None
    objective: str | None = None
    value: float | None = None
    unit: str = ""
    confidence: str | float = "1.0"
    source: str = "USER_INPUT"


class ComparisonCreateRequest(BaseModel):
    alternatives: list[str] | None = None
    objectives: list[str] | None = None


class SimulationCreateRequest(BaseModel):
    simulation_type: str = Field(min_length=1)
    method: str = Field(min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    method_version: str = "1.0"


class MultiobjectiveRequest(BaseModel):
    objectives: list[str] = Field(min_length=2)


class ProjectVariableCreateRequest(BaseModel):
    variable_id: str = Field(min_length=1)
    normalized_key: str = Field(min_length=1)
    variable_type: str = Field(min_length=1)
    value: Any
    actor_id: str = Field(min_length=1)
    authority: str = Field(min_length=1)
    unit: str | None = None
    spatial_scope: str = "edificacion"
    source: str = "USER_INPUT"
    normative_reference: str | None = None


class FeasibilityCheckRequest(BaseModel):
    alternative_id: str = Field(min_length=1)
    values: dict[str, Any] = Field(default_factory=dict)


class FeasibleParetoRequest(BaseModel):
    pareto_front: list[str] = Field(min_length=1)


class GenerationCreateRequest(BaseModel):
    method: str = Field(min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)


class GenerationPromoteRequest(BaseModel):
    candidate_index: int = Field(ge=0)
    actor: str = Field(min_length=1)
    authority: str = Field(min_length=1)


class DesignKnowledgeQueryRequest(BaseModel):
    spatial_scope: str | None = None
    typology: str | None = None
    jurisdiction: str | None = None
    objectives: list[str] = Field(default_factory=list)
    problem_terms: list[str] = Field(default_factory=list)
    requested_operation: str = "KNOWLEDGE_RETRIEVAL"
    facts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)


class BIMElementRequest(BaseModel):
    global_id: str = Field(min_length=1)
    entity: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)


class BIMSnapshotCreateRequest(BaseModel):
    exchange_id: str = Field(min_length=1)
    format: str = Field(min_length=1)
    source_application: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    spatial_scope: str = Field(min_length=1)
    coordinate_reference_system: str = Field(min_length=1)
    units: str = Field(min_length=1)
    model_hash: str = Field(min_length=1)
    elements: list[BIMElementRequest] = Field(default_factory=list)
    review_state: str = "HUMAN_REVIEW_REQUIRED"


class BIMChangeSetCreateRequest(BaseModel):
    change_set_id: str = Field(min_length=1)
    snapshot_id: str = Field(min_length=1)
    changes: list[dict[str, Any]] = Field(default_factory=list)
    requested_by: str = Field(min_length=1)
    mode: str = "PREVIEW"


class MemoryExtractRequest(BaseModel):
    project_id: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    authority: str = Field(min_length=1)


class MemoryAuthorityRequest(BaseModel):
    actor: str = Field(min_length=1)
    authority: str = Field(min_length=1)


class MemoryApplyRequest(BaseModel):
    memory_id: str = Field(min_length=1)
    actor: str = Field(min_length=1)


class PlanningInstrumentLinkRequest(BaseModel):
    instrument_id: str = Field(min_length=1)


class RegulationCreateRequest(BaseModel):
    regulation_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    title: str = Field(min_length=1)
    jurisdiction: str = "UNKNOWN"
    source_url: str | None = None
    authority: str = "UNKNOWN"
    version: str = "1.0"
    project_id: str | None = None


class RegulationStatusRequest(BaseModel):
    status: str = Field(min_length=1)


class InterpretationCreateRequest(BaseModel):
    interpretation_id: str = Field(min_length=1)
    article_reference: str = Field(min_length=1)
    interpretation_text: str = Field(min_length=1)
    applied_to_project_id: str | None = None


class InterpretationReviewRequest(BaseModel):
    actor: str = Field(min_length=1)
    authority: str = Field(min_length=1)


class SnapshotCreateRequest(BaseModel):
    snapshot_id: str = Field(min_length=1)
    cut_date: str = Field(min_length=10)
    jurisdiction: str = "UNKNOWN"


class SnapshotFreezeRequest(BaseModel):
    reviewer: str = Field(min_length=1)


class ScaleRelationCreateRequest(BaseModel):
    parent_project_id: str = Field(min_length=1)
    child_project_id: str = Field(min_length=1)
    relation_type: str = Field(min_length=1)
    description: str | None = None
    created_by: str = Field(default="api", min_length=1)


class ImportObjectiveRequest(BaseModel):
    source_project_id: str = Field(min_length=1)
    objective_id: str = Field(min_length=1)
    actor: str = Field(default="api", min_length=1)


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    stage: str
    version: int
    spatial_scope: str | None = None
    temporal_scope: str = "proyecto"
    objectives: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    roles: dict[str, Any] = Field(default_factory=dict)
    facts: dict[str, Any] = Field(default_factory=dict)
    assumptions: dict[str, Any] = Field(default_factory=dict)
    decisions: dict[str, Any] = Field(default_factory=dict)
    alternatives: dict[str, Any] = Field(default_factory=dict)
    evaluations: dict[str, Any] = Field(default_factory=dict)
    comparisons: dict[str, Any] = Field(default_factory=dict)
    recommendations: dict[str, Any] = Field(default_factory=dict)


class ParcelSnapshotCreateRequest(BaseModel):
    feature: dict[str, Any]
    source_url: str = Field(min_length=1)
    source_type: str = "OFFICIAL"
    jurisdiction: str = "UNKNOWN"
    source_crs: str = "EPSG:4326"
    analysis_crs: str = "EPSG:4326"
    validity_date: str | None = None


class OGCQueryRequest(BaseModel):
    url: str = Field(min_length=1)
    source_type: str = "OFFICIAL"
    jurisdiction: str = "UNKNOWN"
    source_crs: str = "EPSG:4326"
    analysis_crs: str = "EPSG:4326"


class CopilotTranslateRequest(BaseModel):
    text: str = Field(min_length=1)
    model: str | None = None


class SpatialLocationCreateRequest(BaseModel):
    location_id: str | None = None
    spatial_scope: str = "parcela_sitio"
    geometry_type: str = "Point"
    geometry: dict[str, Any]
    crs: str = "EPSG:4326"
    place_label: str | None = None
    acquisition_method: str = "MAP_SELECTION"
    provenance: str = "USER_DECLARED"
    actor_id: str = Field(default="api", min_length=1)
    authority: str = Field(default="project_owner", min_length=1)
    supersedes_location_id: str | None = None
    confirm: bool = False

class SpatialLocationConfirmRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    authority: str = Field(min_length=1)
    confirm: bool = True


class DesignIntentInterpretRequest(BaseModel):
    text: str = Field(min_length=1)
    project_id: str | None = None
    spatial_scope: str | None = None


class DesignIntentConfirmRequest(BaseModel):
    interpretation: dict[str, Any]
    approved_ids: list[str] = Field(min_length=1)
    actor: str = Field(min_length=1)


class MultimodalInterpretRequest(BaseModel):
    modality: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    input_id: str = Field(default="MMI-LOCAL", min_length=1)


class MultimodalConfirmRequest(BaseModel):
    candidate: dict[str, Any]
    actor: str = Field(min_length=1)
