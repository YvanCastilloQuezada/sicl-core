from __future__ import annotations

import os
import uuid
import hashlib
import json
import shlex
import tempfile
from pathlib import Path
from dataclasses import asdict
from datetime import date, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from api.deps import get_repository
from api.schemas import (
    CanonicalCommandRequest,
    CanonicalProjectCreateRequest,
    CanonicalWriteRequest,
    ActorCreateRequest,
    PositionCreateRequest,
    CycleCreateRequest,
    ScenarioCreateRequest,
    ScenarioSelectRequest,
    ScenarioEvolutionCreateRequest,
    ScenarioEvolutionApplyRequest,
    ComparisonCreateRequest,
    EvidenceCreateRequest,
    SourceCreateRequest,
    EvaluationCreateRequest,
    GenerationCreateRequest,
    GenerationPromoteRequest,
    MemoryApplyRequest,
    MemoryAuthorityRequest,
    MemoryExtractRequest,
    MultiobjectiveRequest,
    PlanningInstrumentLinkRequest,
    RegulationCreateRequest,
    RegulationStatusRequest,
    InterpretationCreateRequest,
    InterpretationReviewRequest,
    SnapshotCreateRequest,
    SnapshotFreezeRequest,
    ScaleRelationCreateRequest,
    ImportObjectiveRequest,
    SimulationCreateRequest,
    ProjectVariableCreateRequest,
    FeasibilityCheckRequest,
    FeasibleParetoRequest,
    SpatialLocationCreateRequest,
    SpatialLocationConfirmRequest,
    DesignKnowledgeQueryRequest,
    DesignIntentInterpretRequest,
    DesignIntentConfirmRequest,
    MultimodalInterpretRequest,
    MultimodalConfirmRequest,
    BIMSnapshotCreateRequest,
    BIMChangeSetCreateRequest,
    V1Envelope,
)
from sicl.cli import CLI
from sicl.domain import Evidence, EvidenceType, Event, HumanReview, InterpretationConfidence, InterpretationState, KNOWLEDGE_STATES, NormativeInterpretation, NormativeSnapshot, NormativeSnapshotState, PlanningInstrumentType, Preference, Regulation, RegulationStatus, ScaleRelationType, Source, SourceType, SpatialScope
from sicl.actors import actor_to_dict, position_to_dict
from sicl.temporal import cycle_to_dict, evolution_to_dict, scenario_to_dict
from sicl.generation import generation_to_dict, list_generation_methods
from sicl.memory import memory_to_dict, memory_types
from sicl.repository import SQLiteRepository
from sicl.media_storage import MAX_MEDIA_BYTES, retrieve_media, store_media
from sicl.site_intelligence import fetch_open_meteo_solar, fetch_open_meteo_solar_coordinates, get_site_observation, fetch_open_meteo_air_quality, fetch_open_meteo_climate
from sicl.simulation import METHODS, SimulationType, list_methods, simulation_to_dict
from sicl.design_principles import get_principle, list_principles
from sicl.regulatory import LEGAL_DISCLAIMER, interpretation_to_dict, regulation_to_dict, snapshot_to_dict
from sicl.multiscale import SCALE_ORDER, children_scopes, parent_scope
from sicl.feasibility import ProjectVariable, VariableType, evaluate_feasibility, feasible_pareto_front, normalized_key, serialize_result
from sicl.design_knowledge import DesignKnowledgeAgent, DesignKnowledgeQuery, list_items as list_knowledge_items, list_patterns as list_knowledge_patterns, list_sources as list_knowledge_sources
from sicl.bim import BIMChangeSetMode, BIMElementReference, BIMFormat, BIMModelSnapshot, BIMReviewState, build_preview_change_set, change_set_to_dict, snapshot_to_dict as bim_snapshot_to_dict
from sicl.ifc_adapter import parse_ifc_file
from sicl.spatial_location import SpatialLocation, LocationStatus, AcquisitionMethod, LocationProvenance
from sicl.spatial_registration import SpatialRegistration, propose_registration, registration_transition
from sicl.georeferenced_site import normalize_reference_point, parse_kml, polygon_metrics, validate_polygon, local_project_frame, site_intelligence, site_fit, terrain_query, context_query
from sicl.multiscale_spatial_evidence import evidence_view, multiscale_summary, surface_conflicts, validate_observation
from sicl.external_spatial_context import query_external_context
from sicl.spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives
from sicl.spatial_evaluation import build_upao001_dataset
from sicl.environmental import EnvironmentalAnalysisError, EnvironmentalLocation, build_solar_analysis
from sicl.capabilities import resolve_example_capability
from sicl.design_intent import confirm_intent, interpret_intent
from sicl.multimodal import confirm_multimodal_candidate, interpret_multimodal_input
from sicl.design_intelligence import controlled_exploration, query_design_knowledge_for_intent
from sicl.gdi import evolve_from_candidate, explore_design_space, multi_agent_challenge, multiobjective_search
from sicl.spatial_synthesis import build_spatial_graph, demo_program, generate_space_layout, synthesize_form_space
from sicl.design_memory import direction_event, explain_design, project_memory, query_memory, replay
from sicl.advanced_evolution import advanced_evolution, bounded_diverse_exploration, cross_branch, design_distance, search_by_example
from sicl.candidate_normalization import normalize_design_candidate
from sicl.multiscale_generative import capability_matrix, cross_scale_context, resolve_generative_capabilities
from sicl.multi_agent_design import multi_agent_exploration
from sicl.semantic_reasoning import build_semantic_reasoning
from sicl.design_contribution_trace import build_design_contribution_trace
from sicl.spatial_operations import execute_operation, execute_sequence, operation_capabilities, propose_operation
from sicl.v11 import Alternative

CONTRACT_VERSION = "1.0"
router = APIRouter(prefix="/v1", tags=["canonical-v1"])


def _auth(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("SICL_CORE_SERVICE_TOKEN", "").strip()
    if not expected:
        return
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Invalid or missing service token")


def _status_for(code: str) -> int:
    if code in {"METHOD_NOT_FOUND", "SIMULATION_NOT_FOUND", "MULTIOBJECTIVE_NOT_FOUND", "GENERATION_NOT_FOUND", "CANDIDATE_NOT_FOUND", "MEMORY_NOT_FOUND", "OBJECTIVE_NOT_FOUND", "PLANNING_INSTRUMENT_NOT_FOUND", "REGULATION_NOT_FOUND", "INTERPRETATION_NOT_FOUND", "SNAPSHOT_NOT_FOUND", "SOURCE_NOT_FOUND", "BIM_SNAPSHOT_NOT_FOUND", "SCALE_RELATION_REQUIRED", "EXAMPLE_NOT_FOUND"}:
        return 404
    if code == "METHOD_TYPE_MISMATCH":
        return 409
    if code in {"INSUFFICIENT_INPUTS", "INVALID_INPUTS", "INVALID_DISTRIBUTION", "PARAMETER_NOT_FOUND"}:
        return 422
    if code == "PROJECT_NOT_FOUND":
        return 404
    if code in {"PROJECT_ALREADY_EXISTS", "INVALID_STATE", "CONFLICT", "SOURCE_ALREADY_EXISTS", "BIM_SNAPSHOT_ALREADY_EXISTS", "PLANNING_INSTRUMENT_ALREADY_LINKED", "INVALID_SCOPE_RELATION", "LOCATION_ALREADY_EXISTS"}:
        return 409
    if code in {"HUMAN_REVIEW_REQUIRED", "HUMAN_AUTHORITY_REQUIRED", "HUMAN_CONFIRMATION_REQUIRED", "MEMORY_REVOKED", "SEMANTIC_REJECTION", "OBJECTIVE_DIRECTION_REQUIRED", "INVALID_SOURCE_TYPE", "INVALID_LOCATION", "BIM_PREVIEW_ONLY"}:
        return 422
    return 400


def _error(result: dict[str, Any], project_id: str | None = None) -> None:
    if result.get("code") == "OK":
        return
    raise HTTPException(
        status_code=_status_for(str(result.get("code", "INVALID_ARGUMENT"))),
        detail={
            "contract_version": CONTRACT_VERSION,
            "status": "ERROR",
            "code": result.get("code", "INVALID_ARGUMENT"),
            "message": result.get("message", "Request rejected"),
            "project_id": project_id,
            "observed_version": None,
            "data": result.get("data", {}),
        },
    )


def _ok(data: dict[str, Any], project_id: str | None = None, version: int | None = None) -> V1Envelope:
    return V1Envelope(
        contract_version=CONTRACT_VERSION,
        status="OK",
        code="OK",
        message="ok",
        project_id=project_id,
        observed_version=version,
        data=data,
    )




def _confirmed_location(project: Any) -> SpatialLocation | None:
    if project is None:
        return None
    confirmed = [
        item for item in project.spatial_locations.values()
        if item.status is LocationStatus.CONFIRMED and item.geometry_type == "Point"
    ]
    return confirmed[-1] if confirmed else None

def _snapshot(repo: SQLiteRepository, project_id: str) -> tuple[dict[str, Any], int]:
    project = repo.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail={"contract_version": CONTRACT_VERSION, "status": "ERROR", "code": "PROJECT_NOT_FOUND", "message": project_id, "data": {}})
    return asdict(project), project.version


@router.get("/health", dependencies=[Depends(_auth)])
def v1_health() -> dict[str, str]:
    return {"contract_version": CONTRACT_VERSION, "status": "OK", "service": "sicl-core-api"}


@router.get("/operations-research/methods", dependencies=[Depends(_auth)])
def methods() -> dict[str, Any]:
    return {"contract_version": CONTRACT_VERSION, "read_only": True, "methods": []}


@router.get("/simulations/methods", dependencies=[Depends(_auth)])
def simulation_methods() -> dict[str, Any]:
    return {"contract_version": CONTRACT_VERSION, "status": "OK", "code": "OK", "message": "ok", "project_id": None, "observed_version": None, "data": {"methods": list_methods()}}


@router.get("/generations/methods", dependencies=[Depends(_auth)])
def generation_methods() -> V1Envelope:
    return _ok({"methods": list_generation_methods()})


@router.get("/design-knowledge/catalog", dependencies=[Depends(_auth)])
def design_knowledge_catalog(scope: str | None = None, typology: str | None = None) -> V1Envelope:
    spatial_scope = None
    if scope is not None:
        try:
            spatial_scope = SpatialScope(scope)
        except ValueError:
            _error({"code": "INVALID_SCOPE", "message": scope})
    return _ok({"sources": list_knowledge_sources(), "items": list_knowledge_items(spatial_scope, typology), "patterns": list_knowledge_patterns(spatial_scope, typology), "scales": [item.value for item in SpatialScope]})


@router.post("/design-knowledge/query", dependencies=[Depends(_auth)])
def query_design_knowledge(request: DesignKnowledgeQueryRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    spatial_scope = None
    if request.spatial_scope is not None:
        try:
            spatial_scope = SpatialScope(request.spatial_scope)
        except ValueError:
            _error({"code": "INVALID_SCOPE", "message": request.spatial_scope})
    regulations = [regulation_to_dict(item) for item in repo.list_regulations()]
    result = DesignKnowledgeAgent(regulations).query(DesignKnowledgeQuery(
        spatial_scope=spatial_scope,
        typology=request.typology,
        jurisdiction=request.jurisdiction,
        objectives=request.objectives,
        problem_terms=request.problem_terms,
        requested_operation=request.requested_operation,
        facts=request.facts,
        assumptions=request.assumptions,
        preferences=request.preferences,
    ))
    return _ok(asdict(result))


@router.post("/design-intents/interpret", dependencies=[Depends(_auth)])
def interpret_design_intent(request: DesignIntentInterpretRequest) -> V1Envelope:
    try:
        result = interpret_intent(request.text, project_id=request.project_id, spatial_scope=request.spatial_scope)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)})
    return _ok(result, request.project_id)


@router.post("/projects/{project_id}/design-intents/confirm", dependencies=[Depends(_auth)])
def confirm_design_intent(project_id: str, request: DesignIntentConfirmRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        adopted, event_payload = confirm_intent(project_id, request.interpretation, request.approved_ids, request.actor)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    event = Event(None, datetime.now(timezone.utc).isoformat(), project_id, event_payload["type"], event_payload["payload"], request.actor, event_payload["source"])
    repo.add_event(event)
    return _ok({"adopted_intent": adopted, "event_type": event.type, "decision_created": False, "human_authority": True}, project_id, project.version)

@router.post("/projects/{project_id}/gdi/semantic-reasoning", dependencies=[Depends(_auth)])
def gdi_semantic_reasoning(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload.get("payload", request.payload)
    adopted_intent = payload.get("adopted_intent")
    if not isinstance(adopted_intent, dict) or adopted_intent.get("adoption") != "HUMAN_CONFIRMED":
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "A human-confirmed intent is required"}, project_id)
    try:
        result = build_semantic_reasoning(
            adopted_intent,
            payload.get("knowledge") if isinstance(payload.get("knowledge"), dict) else {},
            payload.get("alternative") if isinstance(payload.get("alternative"), dict) else None,
            spatial_scope=payload.get("spatial_scope"),
            context=str(payload.get("context", "")),
        )
    except (TypeError, ValueError, KeyError) as exc:
        _error({"code": "SEMANTIC_REASONING_ERROR", "message": str(exc)}, project_id)
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "SEMANTIC_REASONING_PROJECTED", result, request.actor, "gdi-semantic-depth"))
    return _ok(result, project_id)

@router.post("/projects/{project_id}/gdi/design-contribution-trace", dependencies=[Depends(_auth)])
def gdi_design_contribution_trace(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Return a structured before/after trace without creating a winner or decision."""
    payload = request.payload.get("payload", request.payload)
    intent = payload.get("adopted_intent")
    knowledge = payload.get("knowledge") if isinstance(payload.get("knowledge"), dict) else {}
    hypotheses = payload.get("hypotheses") if isinstance(payload.get("hypotheses"), list) else []
    if not isinstance(intent, dict) or intent.get("adoption") != "HUMAN_CONFIRMED":
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "A human-confirmed intent is required"}, project_id)
    if not hypotheses:
        _error({"code": "HYPOTHESES_REQUIRED", "message": "At least one confirmed hypothesis is required"}, project_id)
    explorations = []
    try:
        reasoning = build_semantic_reasoning(intent, knowledge, spatial_scope=payload.get("spatial_scope"), context=str(payload.get("context", "")))
        for hypothesis in hypotheses:
            if not isinstance(hypothesis, dict) or hypothesis.get("human_confirmed") is not True:
                _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "Every explored hypothesis must be explicitly human-confirmed"}, project_id)
            adopted_variant = dict(intent)
            adopted_variant["adopted_intents"] = [hypothesis.get("statement", "")]
            explorations.append(controlled_exploration(str(hypothesis.get("base_alternative_id", "UPAO-001-A")), adopted_variant, knowledge))
        result = build_design_contribution_trace(project_id=project_id, intent=intent, knowledge=knowledge, hypotheses=hypotheses, explorations=explorations, semantic_reasoning=reasoning, human_confirmed=True)
    except (TypeError, ValueError, KeyError) as exc:
        _error({"code": "DESIGN_TRACE_ERROR", "message": str(exc)}, project_id)
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "DESIGN_CONTRIBUTION_TRACE_GENERATED", result, request.actor, "gdi-causal-design-trace"))
    return _ok(result, project_id)

@router.get("/projects/{project_id}/gdi/spatial-operations/capabilities", dependencies=[Depends(_auth)])
def gdi_spatial_operation_capabilities(project_id: str) -> V1Envelope:
    return _ok({"capabilities": operation_capabilities(), "spatial_scopes": ["edificacion", "parcela_sitio"], "new_canonical_entities": 0}, project_id)

@router.post("/projects/{project_id}/gdi/spatial-operations/preview", dependencies=[Depends(_auth)])
def gdi_spatial_operation_preview(project_id: str, request: CanonicalWriteRequest) -> V1Envelope:
    payload = request.payload.get("payload", request.payload)
    alternative = payload.get("alternative")
    if not isinstance(alternative, dict):
        _error({"code": "ALTERNATIVE_REQUIRED", "message": "A canonical alternative is required"}, project_id)
    try:
        normalized = Alternative(**normalize_design_candidate(alternative, project_id))
        result = propose_operation(normalized, str(payload.get("operation_type", "")), payload.get("parameters", {}), intent_linkage=payload.get("intent_linkage", []), knowledge_linkage=payload.get("knowledge_linkage", []), controls=payload.get("controls", {}))
    except (KeyError, TypeError, ValueError) as exc:
        _error({"code": "SPATIAL_OPERATION_PREVIEW_ERROR", "message": str(exc)}, project_id)
    return _ok(result, project_id)

@router.post("/projects/{project_id}/gdi/spatial-operations/execute", dependencies=[Depends(_auth)])
def gdi_spatial_operation_execute(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload.get("payload", request.payload)
    alternative = payload.get("alternative")
    if not isinstance(alternative, dict):
        _error({"code": "ALTERNATIVE_REQUIRED", "message": "A canonical alternative is required"}, project_id)
    if payload.get("human_confirmed") is not True:
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "Explicit human confirmation is required before execution"}, project_id)
    try:
        normalized = Alternative(**normalize_design_candidate(alternative, project_id))
        if isinstance(payload.get("operations"), list):
            result = execute_sequence(normalized, payload["operations"], human_confirmed=True)
        else:
            result = execute_operation(normalized, str(payload.get("operation_type", "")), payload.get("parameters", {}), intent_linkage=payload.get("intent_linkage", []), knowledge_linkage=payload.get("knowledge_linkage", []), controls=payload.get("controls", {}), human_confirmed=True)
    except (KeyError, TypeError, ValueError) as exc:
        _error({"code": "SPATIAL_OPERATION_EXECUTION_ERROR", "message": str(exc)}, project_id)
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "SPATIAL_OPERATION_EXECUTED", result, request.actor, "gdi-spatial-operations-p0"))
    return _ok(result, project_id)

@router.get("/projects/{project_id}/design-memory", dependencies=[Depends(_auth)])
def get_design_memory(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    try:
        return _ok(project_memory(repo, project_id), project_id)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)

@router.get("/projects/{project_id}/design-memory/query", dependencies=[Depends(_auth)])
def query_design_memory(project_id: str, q: str = Query(..., min_length=1), repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    try:
        return _ok(query_memory(project_memory(repo, project_id), q), project_id)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)

@router.get("/projects/{project_id}/design-memory/explain/{alternative_id}", dependencies=[Depends(_auth)])
def explain_design_memory(project_id: str, alternative_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    try:
        return _ok(explain_design(project_memory(repo, project_id), alternative_id), project_id)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)

@router.get("/projects/{project_id}/design-memory/replay", dependencies=[Depends(_auth)])
def replay_design_memory(project_id: str, alternative_id: str | None = Query(default=None), repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    try:
        return _ok(replay(project_memory(repo, project_id), alternative_id), project_id)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)

@router.post("/projects/{project_id}/design-memory/directions", dependencies=[Depends(_auth)])
def record_design_direction(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload
    try:
        event_payload = direction_event(project_id, str(payload["alternative_id"]), str(payload["status"]), request.actor, payload.get("reason"))
    except (KeyError, ValueError) as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    event = Event(None, datetime.now(timezone.utc).isoformat(), project_id, event_payload["type"], event_payload["payload"], request.actor, event_payload["source"])
    repo.add_event(event)
    return _ok({"status": event_payload["payload"]["status"], "alternative_id": event_payload["payload"]["alternative_id"], "human_reason": event_payload["payload"]["human_reason"], "decision_created": False}, project_id)

@router.post("/projects/{project_id}/gdi/advanced-evolution", dependencies=[Depends(_auth)])
def gdi_advanced_evolution(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload
    parent = payload.get("parent") or payload.get("candidate")
    if not isinstance(parent, dict):
        _error({"code": "PARENT_REQUIRED", "message": "A parent historical alternative is required"}, project_id)
    try:
        parent = normalize_design_candidate(parent, project_id)
        if payload.get("mode") == "BOUNDED_DIVERSE":
            result = bounded_diverse_exploration(parent, payload)
        elif payload.get("mode") == "DISTANCE":
            result = design_distance(parent, normalize_design_candidate(payload["other"], project_id))
        elif payload.get("mode") == "SEARCH":
            result = search_by_example(parent, [normalize_design_candidate(item, project_id) for item in payload.get("candidates", [])], payload.get("search_mode", "SIMILAR"))
        elif payload.get("mode") == "CROSS_BRANCH":
            result = cross_branch(parent, normalize_design_candidate(payload["other"], project_id), payload.get("inherit", []), payload.get("other_inherit", []))
        else:
            result = advanced_evolution(parent, payload)
    except (KeyError, ValueError) as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    alternative = result.get("alternative", {}) if isinstance(result, dict) else {}
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "ADVANCED_EVOLUTION_EXPLORED", {"alternative_id": alternative.get("alternative_id"), "parent_alternative_id": parent.get("alternative_id") or parent.get("alternative", {}).get("alternative_id"), "advanced_evolution": result, "decision_created": False}, request.actor, "gdi-p6"))
    return _ok(result, project_id)

@router.post("/projects/{project_id}/multimodal/interpret", dependencies=[Depends(_auth)])
def interpret_multimodal(project_id: str, request: MultimodalInterpretRequest) -> V1Envelope:
    try:
        result = interpret_multimodal_input(project_id, request.modality, request.payload, input_id=request.input_id)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    return _ok(result, project_id)

@router.post("/projects/{project_id}/multimodal/confirm", dependencies=[Depends(_auth)])
def confirm_multimodal(project_id: str, request: MultimodalConfirmRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    try:
        result = confirm_multimodal_candidate(request.candidate, request.actor)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "MULTIMODAL_INPUT_CONFIRMED", {"candidate": result, "modality": result.get("provenance", {}).get("modality"), "decision_created": False}, request.actor, "multimodal"))
    return _ok({"adopted_input": result, "decision_created": False, "human_authority": True}, project_id)


@router.post("/projects/{project_id}/design-intelligence/knowledge", dependencies=[Depends(_auth)])
def design_intelligence_knowledge(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    adopted = request.payload.get("adopted_intent", request.payload)
    regulations = [regulation_to_dict(item) for item in repo.list_regulations()]
    result = query_design_knowledge_for_intent(adopted, regulations=regulations)
    return _ok(result, project_id)


@router.post("/projects/{project_id}/design-intelligence/explore", dependencies=[Depends(_auth)])
def design_intelligence_explore(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload
    adopted = payload.get("adopted_intent", {})
    if adopted.get("adoption") != "HUMAN_CONFIRMED":
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "Adopted human intent is required"}, project_id)
    knowledge = payload.get("knowledge") or query_design_knowledge_for_intent(adopted, regulations=[regulation_to_dict(item) for item in repo.list_regulations()])
    try:
        result = controlled_exploration(str(payload.get("base_alternative_id", "UPAO-001-A")), adopted, knowledge)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    return _ok(result, project_id)


@router.post("/projects/{project_id}/gdi/operations", dependencies=[Depends(_auth)])
def gdi_operations(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload
    adopted = payload.get("adopted_intent", {})
    if adopted.get("adoption") != "HUMAN_CONFIRMED":
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "Human-confirmed intent is required"}, project_id)
    knowledge = payload.get("knowledge", {})
    result = explore_design_space(str(payload.get("base_alternative_id", "UPAO-001-A")), adopted, knowledge, payload)
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "DESIGN_OPERATION_APPLIED", {"alternative_id": result.get("derived_alternative", {}).get("alternative_id"), "parent_alternative_id": payload.get("base_alternative_id", "UPAO-001-A"), "candidate": result.get("derived_alternative"), "operation": result.get("operation"), "intent": adopted, "decision_created": False}, "system", "gdi"))
    return _ok(result, project_id)


@router.post("/projects/{project_id}/gdi/evolve", dependencies=[Depends(_auth)])
def gdi_evolve(project_id: str, request: CanonicalWriteRequest) -> V1Envelope:
    payload = request.payload
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict):
        _error({"code": "CANDIDATE_REQUIRED", "message": "A generated candidate is required"}, project_id)
    if payload.get("action") not in {"KEEP_THIS", "CHANGE_THAT", "RETURN_TO_PARENT", "EXPLORE_FROM_HERE"}:
        _error({"code": "INVALID_EVOLUTION_ACTION", "message": "Unsupported architect evolution action"}, project_id)
    if payload["action"] == "KEEP_THIS":
        return _ok({"candidate": candidate, "state": "KEPT_FOR_EXPLORATION", "decision_created": False}, project_id)
    return _ok(evolve_from_candidate(candidate, payload["action"], payload), project_id)


@router.post("/projects/{project_id}/gdi/challenge", dependencies=[Depends(_auth)])
def gdi_challenge(project_id: str, request: CanonicalWriteRequest) -> V1Envelope:
    candidate = request.payload.get("candidate")
    if not isinstance(candidate, dict):
        _error({"code": "CANDIDATE_REQUIRED", "message": "A candidate is required"}, project_id)
    return _ok(multi_agent_challenge(candidate, request.payload.get("knowledge")), project_id)


@router.post("/projects/{project_id}/gdi/multiobjective", dependencies=[Depends(_auth)])
def gdi_multiobjective(project_id: str, request: CanonicalWriteRequest) -> V1Envelope:
    exploration = request.payload.get("exploration")
    if not isinstance(exploration, dict):
        _error({"code": "EXPLORATION_REQUIRED", "message": "A bounded exploration is required"}, project_id)
    return _ok(multiobjective_search(exploration), project_id)


@router.post("/projects/{project_id}/spatial-synthesis/program", dependencies=[Depends(_auth)])
def spatial_synthesis_program(project_id: str, request: CanonicalWriteRequest) -> V1Envelope:
    program = demo_program(project_id)
    graph = build_spatial_graph(program)
    return _ok({"program": program.to_dict(), "spatial_graph": graph.to_dict(), "provenance": "SYNTHETIC / DEMONSTRATION DATA", "decision_created": False}, project_id)


@router.post("/projects/{project_id}/spatial-synthesis/generate", dependencies=[Depends(_auth)])
def spatial_synthesis_generate(project_id: str, request: CanonicalWriteRequest) -> V1Envelope:
    payload = request.payload
    adopted = payload.get("adopted_intent", {})
    if adopted.get("adoption") != "HUMAN_CONFIRMED":
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "Human-confirmed intent is required before spatial synthesis"}, project_id)
    program = demo_program(project_id)
    graph = build_spatial_graph(program)
    families = payload.get("families") or ["CENTRALIZED", "COURTYARD", "LINEAR"]
    alternatives = [generate_space_layout(program, graph, f"{project_id}-P3-{index + 1}", str(family)) for index, family in enumerate(families[:5])]
    result = synthesize_form_space(program, graph, alternatives)
    result["intent_id"] = adopted.get("intent_id") or adopted.get("interpretation_id")
    result["gdi_p1_loop"] = ["GENERATE", "SELECT", "KEEP_THIS", "CHANGE_THAT", "BRANCH", "EVOLVE", "COMPARE", "EVALUATE", "CHALLENGE", "HUMAN_REVIEW", "HUMAN_DECISION"]
    return _ok(result, project_id)


@router.post("/projects/{project_id}/spatial-synthesis/layout", dependencies=[Depends(_auth)])
def spatial_synthesis_layout(project_id: str, request: CanonicalWriteRequest) -> V1Envelope:
    payload = request.payload
    program = demo_program(project_id)
    graph = build_spatial_graph(program)
    family = str(payload.get("family", "COURTYARD"))
    alternative_id = str(payload.get("alternative_id", f"{project_id}-P3-SELECTED"))
    return _ok(generate_space_layout(program, graph, alternative_id, family), project_id)


@router.post("/projects/{project_id}/bim/snapshots", dependencies=[Depends(_auth)])
def create_bim_snapshot(project_id: str, request: BIMSnapshotCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if repo.get_bim_snapshot(project_id, request.exchange_id) is not None:
        _error({"code": "BIM_SNAPSHOT_ALREADY_EXISTS", "message": request.exchange_id}, project_id)
    try:
        item = BIMModelSnapshot(
            request.exchange_id, BIMFormat(request.format.upper()), request.source_application,
            request.source_version, project_id, SpatialScope(request.spatial_scope),
            request.coordinate_reference_system, request.units, request.model_hash,
            [BIMElementReference(element.global_id, element.entity, element.parameters, element.provenance) for element in request.elements],
            BIMReviewState(request.review_state.upper()),
        )
    except ValueError as exc:
        _error({"code": "INVALID_BIM_SNAPSHOT", "message": str(exc)}, project_id)
    except KeyError as exc:
        _error({"code": "INVALID_BIM_SNAPSHOT", "message": str(exc)}, project_id)
    repo.insert_bim_snapshot(item, datetime.now(timezone.utc).isoformat())
    return _ok({"snapshot": bim_snapshot_to_dict(item), "write_mode": "APPEND_ONLY"}, project_id, project.version)


@router.post("/projects/{project_id}/bim/ifc-import", dependencies=[Depends(_auth)])
async def import_ifc_read_only(
    project_id: str,
    file: UploadFile = File(...),
    spatial_scope: str = "edificacion",
    coordinate_reference_system: str = "UNKNOWN",
    units: str = "SI",
    repo: SQLiteRepository = Depends(get_repository),
) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if not file.filename or not file.filename.lower().endswith(".ifc"):
        _error({"code": "INVALID_IFC_FILE", "message": "An .ifc file is required"}, project_id)
    try:
        scope = SpatialScope(spatial_scope)
    except ValueError:
        _error({"code": "INVALID_SCOPE", "message": spatial_scope}, project_id)
    contents = await file.read()
    if not contents:
        _error({"code": "INVALID_IFC_FILE", "message": "The IFC file is empty"}, project_id)
    fixture = Path(__file__).resolve().parents[2] / "data" / "regulatory" / "rne_a010_sample.json"
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as temporary:
            temporary.write(contents)
            temporary_path = temporary.name
        result = parse_ifc_file(temporary_path, project_id, scope, coordinate_reference_system, units, fixture)
        if repo.get_bim_snapshot(project_id, result.snapshot.exchange_id) is not None:
            _error({"code": "BIM_SNAPSHOT_ALREADY_EXISTS", "message": result.snapshot.exchange_id}, project_id)
        repo.insert_bim_snapshot(result.snapshot, datetime.now(timezone.utc).isoformat())
        return _ok({"snapshot": bim_snapshot_to_dict(result.snapshot), "rne_validation": [asdict(row) for row in result.findings], "read_only": True, "export_applied": False}, project_id, project.version)
    except (RuntimeError, ValueError, OSError) as exc:
        _error({"code": "INVALID_IFC_FILE", "message": str(exc)}, project_id)
    finally:
        if temporary_path:
            Path(temporary_path).unlink(missing_ok=True)


@router.get("/projects/{project_id}/bim/snapshots", dependencies=[Depends(_auth)])
def list_bim_snapshots(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"snapshots": [bim_snapshot_to_dict(item) for item in repo.list_bim_snapshots(project_id)]}, project_id, project.version)


@router.get("/projects/{project_id}/bim/snapshots/{exchange_id}", dependencies=[Depends(_auth)])
def get_bim_snapshot(project_id: str, exchange_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    item = repo.get_bim_snapshot(project_id, exchange_id)
    if item is None:
        _error({"code": "BIM_SNAPSHOT_NOT_FOUND", "message": exchange_id}, project_id)
    return _ok({"snapshot": bim_snapshot_to_dict(item)}, project_id, project.version)


@router.post("/projects/{project_id}/bim/change-sets", dependencies=[Depends(_auth)])
def create_bim_change_set(project_id: str, request: BIMChangeSetCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if request.mode.upper() != BIMChangeSetMode.PREVIEW.value:
        _error({"code": "BIM_PREVIEW_ONLY", "message": "RFC-027 only permits PREVIEW change sets"}, project_id)
    if repo.get_bim_snapshot(project_id, request.snapshot_id) is None:
        _error({"code": "BIM_SNAPSHOT_NOT_FOUND", "message": request.snapshot_id}, project_id)
    item = build_preview_change_set(request.change_set_id, project_id, request.snapshot_id, request.changes, request.requested_by)
    repo.insert_bim_change_set(item, datetime.now(timezone.utc).isoformat())
    return _ok({"change_set": change_set_to_dict(item), "applied": False, "write_mode": "PREVIEW_ONLY"}, project_id, project.version)


@router.get("/projects/{project_id}/bim/change-sets", dependencies=[Depends(_auth)])
def list_bim_change_sets(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"change_sets": [change_set_to_dict(item) for item in repo.list_bim_change_sets(project_id)]}, project_id, project.version)


@router.post("/projects/{project_id}/generations", dependencies=[Depends(_auth)])
def create_generation(project_id: str, request: GenerationCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}"), project_id)
    command = f"/GENERATE DESIGN {shlex.quote(request.method)} {shlex.quote(json.dumps(request.inputs, sort_keys=True))}"
    result = cli.execute(command)
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"generation": result["data"]["generation"]}, project_id, project.version if project else None)


@router.get("/projects/{project_id}/generations", dependencies=[Depends(_auth)])
def list_generations(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"generations": [generation_to_dict(item) for item in repo.list_generations(project_id)]}, project_id, project.version)


@router.get("/projects/{project_id}/generations/{generation_id}", dependencies=[Depends(_auth)])
def get_generation(project_id: str, generation_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    generation = repo.get_generation(project_id, generation_id)
    if generation is None:
        _error({"code": "GENERATION_NOT_FOUND", "message": generation_id}, project_id)
    return _ok({"generation": generation_to_dict(generation)}, project_id, project.version)


@router.post("/projects/{project_id}/generations/{generation_id}/promote", dependencies=[Depends(_auth)])
def promote_generation(project_id: str, generation_id: str, request: GenerationPromoteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor=request.actor)
    _error(cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}"), project_id)
    command = f"/ALTERNATIVE PROMOTE {shlex.quote(generation_id)} {request.candidate_index} {shlex.quote(request.actor)} {shlex.quote(request.authority)}"
    result = cli.execute(command)
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.get("/memory", dependencies=[Depends(_auth)])
def list_memory(repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    return _ok({"memories": [memory_to_dict(item) for item in repo.list_memory()]})


@router.get("/memory/types", dependencies=[Depends(_auth)])
def memory_catalog() -> V1Envelope:
    return _ok({"types": memory_types()})


@router.get("/memory/{memory_id}", dependencies=[Depends(_auth)])
def get_memory(memory_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    memory = repo.get_memory(memory_id)
    if memory is None:
        _error({"code": "MEMORY_NOT_FOUND", "message": memory_id})
    return _ok({"memory": memory_to_dict(memory)})


@router.post("/memory/extract", dependencies=[Depends(_auth)])
def extract_memory_http(request: MemoryExtractRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(request.project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": request.project_id}, request.project_id)
    cli = CLI(repo, actor=request.actor)
    command = f"/MEMORY EXTRACT {shlex.quote(request.project_id)} {shlex.quote(request.actor)} {shlex.quote(request.authority)}"
    result = cli.execute(command)
    _error(result, request.project_id)
    return _ok(result["data"], request.project_id)


@router.post("/memory/{memory_id}/revoke", dependencies=[Depends(_auth)])
def revoke_memory_http(memory_id: str, request: MemoryAuthorityRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    cli = CLI(repo, actor=request.actor)
    command = f"/MEMORY REVOKE {shlex.quote(memory_id)} {shlex.quote(request.actor)} {shlex.quote(request.authority)}"
    result = cli.execute(command)
    _error(result)
    return _ok(result["data"])


@router.post("/projects/{project_id}/memory/apply", dependencies=[Depends(_auth)])
def apply_memory_http(project_id: str, request: MemoryApplyRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    cli = CLI(repo, actor=request.actor)
    command = f"/MEMORY APPLY {shlex.quote(request.memory_id)} {shlex.quote(project_id)}"
    result = cli.execute(command)
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.post("/projects/{project_id}/actors", dependencies=[Depends(_auth)])
def create_actor(project_id: str, request: ActorCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor=request.name)
    command = f"/ACTOR ADD {shlex.quote(request.actor_id)} {shlex.quote(request.role)} {shlex.quote(request.name)} {shlex.quote(request.authority_level)} {shlex.quote(json.dumps(request.interests))} {shlex.quote(json.dumps(request.constraints))}"
    result = cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}")
    _error(result, project_id)
    result = cli.execute(command)
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.get("/projects/{project_id}/actors", dependencies=[Depends(_auth)])
def list_actors(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"actors": [actor_to_dict(item) for item in repo.list_actors(project_id)]}, project_id, repo.get_project(project_id).version)


@router.get("/projects/{project_id}/actors/{actor_id}", dependencies=[Depends(_auth)])
def get_actor(project_id: str, actor_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    actor = repo.get_actor(project_id, actor_id)
    if actor is None:
        _error({"code": "ACTOR_NOT_FOUND", "message": actor_id}, project_id)
    return _ok({"actor": actor_to_dict(actor)}, project_id, repo.get_project(project_id).version)


@router.post("/projects/{project_id}/positions", dependencies=[Depends(_auth)])
def create_position(project_id: str, request: PositionCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor=request.actor_id)
    opened = cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}")
    _error(opened, project_id)
    command = f"/POSITION ADD {shlex.quote(request.actor_id)} {shlex.quote(request.subject_type)} {shlex.quote(request.subject_id)} {shlex.quote(request.stance)} {shlex.quote(request.reason)} {shlex.quote(json.dumps(request.conditions))}"
    result = cli.execute(command)
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.get("/projects/{project_id}/positions", dependencies=[Depends(_auth)])
def list_positions(project_id: str, subject_id: str | None = None, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"positions": [position_to_dict(item) for item in repo.list_positions(project_id, subject_id)]}, project_id, repo.get_project(project_id).version)


@router.get("/projects/{project_id}/positions/{position_id}", dependencies=[Depends(_auth)])
def get_position(project_id: str, position_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    position = repo.get_position(project_id, position_id)
    if position is None:
        _error({"code": "POSITION_NOT_FOUND", "message": position_id}, project_id)
    return _ok({"position": position_to_dict(position)}, project_id, repo.get_project(project_id).version)


@router.post("/projects/{project_id}/cycles", dependencies=[Depends(_auth)])
def create_cycle(project_id: str, request: CycleCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None: _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}"), project_id)
    command = f"/CYCLE CREATE {shlex.quote(request.cycle_id)} {shlex.quote(request.horizon)} {shlex.quote(request.start_date.isoformat())} {shlex.quote(request.end_date.isoformat() if request.end_date else 'NONE')} {shlex.quote(json.dumps(request.assumptions))} {shlex.quote(json.dumps(request.objectives_at_horizon))} {shlex.quote(json.dumps(request.actors_involved))}"
    result = cli.execute(command); _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.get("/projects/{project_id}/cycles", dependencies=[Depends(_auth)])
def list_cycles(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None: _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"cycles": [cycle_to_dict(item) for item in repo.list_cycles(project_id)]}, project_id, repo.get_project(project_id).version)


@router.get("/projects/{project_id}/cycles/{cycle_id}", dependencies=[Depends(_auth)])
def get_cycle(project_id: str, cycle_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    cycle = repo.get_cycle(project_id, cycle_id)
    if cycle is None: _error({"code": "CYCLE_NOT_FOUND", "message": cycle_id}, project_id)
    return _ok({"cycle": cycle_to_dict(cycle)}, project_id, repo.get_project(project_id).version)


@router.post("/projects/{project_id}/scenarios", dependencies=[Depends(_auth)])
def create_scenario(project_id: str, request: ScenarioCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None: _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}"), project_id)
    command = f"/SCENARIO CREATE {shlex.quote(request.branch_id)} {shlex.quote(request.parent_cycle_id or 'NONE')} {shlex.quote(request.scenario_name)} {shlex.quote(json.dumps(request.conditions))} {shlex.quote(json.dumps(request.objectives))}"
    result = cli.execute(command); _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.get("/projects/{project_id}/scenarios", dependencies=[Depends(_auth)])
def list_scenarios(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None: _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"scenarios": [scenario_to_dict(item) for item in repo.list_scenarios(project_id)]}, project_id, repo.get_project(project_id).version)


@router.post("/projects/{project_id}/scenarios/{branch_id}/select", dependencies=[Depends(_auth)])
def select_scenario(project_id: str, branch_id: str, request: ScenarioSelectRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None: _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor=request.actor)
    _error(cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}"), project_id)
    result = cli.execute(f"/SCENARIO SELECT {shlex.quote(branch_id)} {shlex.quote(request.actor)} {shlex.quote(request.authority)}"); _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.post("/projects/{project_id}/scenario-evolutions", dependencies=[Depends(_auth)])
def create_scenario_evolution(project_id: str, request: ScenarioEvolutionCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None: _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}"), project_id)
    result = cli.execute(f"/EVOLUTION CREATE {shlex.quote(request.evolution_id)} {shlex.quote(request.scenario_id)} {shlex.quote(request.from_cycle_id)} {shlex.quote(request.to_cycle_id)}")
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.get("/projects/{project_id}/scenario-evolutions", dependencies=[Depends(_auth)])
def list_scenario_evolutions(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None: _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"evolutions": [evolution_to_dict(item) for item in repo.list_scenario_evolutions(project_id)]}, project_id, repo.get_project(project_id).version)


@router.get("/projects/{project_id}/scenario-evolutions/{evolution_id}", dependencies=[Depends(_auth)])
def get_scenario_evolution(project_id: str, evolution_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    evolution = repo.get_scenario_evolution(project_id, evolution_id)
    if evolution is None: _error({"code": "EVOLUTION_NOT_FOUND", "message": evolution_id}, project_id)
    return _ok({"evolution": evolution_to_dict(evolution)}, project_id, repo.get_project(project_id).version)


@router.post("/scenario-evolutions/{evolution_id}/apply", dependencies=[Depends(_auth)])
def apply_scenario_evolution(evolution_id: str, request: ScenarioEvolutionApplyRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    match = next(((project.project_id, item) for project in repo.list_projects() for item in repo.list_scenario_evolutions(project.project_id) if item.evolution_id == evolution_id), None)
    if match is None: _error({"code": "EVOLUTION_NOT_FOUND", "message": evolution_id}, None)
    project_id, evolution = match
    cli = CLI(repo, actor=request.actor)
    _error(cli.execute(f"/PROJECT OPEN {shlex.quote(project_id)}"), project_id)
    result = cli.execute(f"/EVOLUTION APPLY {shlex.quote(evolution_id)} {shlex.quote(request.actor)} {shlex.quote(request.authority)}")
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result["data"], project_id, project.version if project else None)


@router.get("/design/principles", dependencies=[Depends(_auth)])
def design_principles(category: str | None = None) -> dict[str, Any]:
    return {"contract_version": CONTRACT_VERSION, "status": "OK", "code": "OK", "message": "ok", "project_id": None, "observed_version": None, "data": {"principles": list_principles(category)}}


@router.get("/design/principles/{principle_id}", dependencies=[Depends(_auth)])
def design_principle(principle_id: str) -> dict[str, Any]:
    principle = get_principle(principle_id)
    if principle is None:
        raise HTTPException(status_code=404, detail={"contract_version": CONTRACT_VERSION, "status": "ERROR", "code": "PRINCIPLE_NOT_FOUND", "message": principle_id, "project_id": None, "observed_version": None, "data": {}})
    return {"contract_version": CONTRACT_VERSION, "status": "OK", "code": "OK", "message": "ok", "project_id": None, "observed_version": None, "data": {"principle": principle}}


@router.get("/scales", dependencies=[Depends(_auth)])
def scales() -> V1Envelope:
    return _ok({"scales": [{"scope": item.value, "label": item.label, "parent": parent_scope(item).value if parent_scope(item) else None, "children": [child.value for child in children_scopes(item)]} for item in SCALE_ORDER]})


@router.get("/scales/{scope}/parent", dependencies=[Depends(_auth)])
def scale_parent(scope: str) -> V1Envelope:
    try:
        parent = parent_scope(scope)
    except ValueError:
        _error({"code": "INVALID_ARGUMENT", "message": f"invalid scope: {scope}"})
    return _ok({"scope": scope.lower(), "parent": parent.value if parent else None})


@router.get("/scales/{scope}/children", dependencies=[Depends(_auth)])
def scale_children(scope: str) -> V1Envelope:
    try:
        children = children_scopes(scope)
    except ValueError:
        _error({"code": "INVALID_ARGUMENT", "message": f"invalid scope: {scope}"})
    return _ok({"scope": scope.lower(), "children": [item.value for item in children]})


@router.post("/projects/{project_id}/scale-relations", dependencies=[Depends(_auth)])
def create_scale_relation(project_id: str, request: ScaleRelationCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if project_id not in {request.parent_project_id, request.child_project_id}:
        _error({"code": "INVALID_ARGUMENT", "message": "path project_id must be parent or child project"}, project_id)
    cli = CLI(repo, actor=request.created_by)
    result = cli.scale_relate([request.parent_project_id, request.child_project_id, request.relation_type, request.description] if request.description else [request.parent_project_id, request.child_project_id, request.relation_type])
    _error(result, project_id)
    return _ok({"relation": result["data"]}, project_id, repo.get_project(project_id).version)


@router.get("/projects/{project_id}/scale-relations", dependencies=[Depends(_auth)])
def list_scale_relations(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"relations": [asdict(item) for item in repo.list_scale_relations(project_id)]}, project_id, repo.get_project(project_id).version)


@router.post("/projects/{project_id}/import-objective", dependencies=[Depends(_auth)])
def import_objective(project_id: str, request: ImportObjectiveRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    cli = CLI(repo, actor=request.actor)
    opened = cli.project_open([project_id])
    _error(opened, project_id)
    result = cli.project_import_objective([request.source_project_id, request.objective_id])
    _error(result, project_id)
    return _ok({"objective": result["data"]}, project_id, repo.get_project(project_id).version)


@router.get("/planning/instruments", dependencies=[Depends(_auth)])
def planning_instruments(instrument_type: str | None = None, jurisdiction: str | None = None, scope_applicable: str | None = None, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if instrument_type:
        try:
            instrument_type = PlanningInstrumentType(instrument_type.upper()).value
        except ValueError:
            _error({"code": "INVALID_ARGUMENT", "message": "invalid instrument_type"})
    values = []
    for item in repo.list_planning_instruments(instrument_type, jurisdiction, scope_applicable):
        value = asdict(item)
        value["instrument_type"] = item.instrument_type.value
        value["status"] = item.status.value
        value["scope_applicable"] = [scope.value for scope in item.scope_applicable]
        value["approval_date"] = item.approval_date.isoformat() if item.approval_date else None
        values.append(value)
    return _ok({"instruments": values})


@router.get("/planning/instruments/{instrument_id}", dependencies=[Depends(_auth)])
def planning_instrument(instrument_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    item = repo.get_planning_instrument(instrument_id)
    if item is None:
        _error({"code": "PLANNING_INSTRUMENT_NOT_FOUND", "message": instrument_id})
    value = asdict(item)
    value["instrument_type"] = item.instrument_type.value
    value["status"] = item.status.value
    value["scope_applicable"] = [scope.value for scope in item.scope_applicable]
    value["approval_date"] = item.approval_date.isoformat() if item.approval_date else None
    return _ok({"instrument": value})


@router.get("/planning/types", dependencies=[Depends(_auth)])
def planning_types() -> V1Envelope:
    return _ok({"types": [item.value for item in PlanningInstrumentType]})


def _regulatory_project(repo: SQLiteRepository) -> str:
    projects = repo.list_projects()
    if not projects:
        raise HTTPException(status_code=409, detail={"code": "PROJECT_REQUIRED", "message": "a project is required for the append-only event log"})
    return projects[0].project_id


@router.post("/regulations", dependencies=[Depends(_auth)])
def create_regulation(request: RegulationCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project_id = request.project_id or _regulatory_project(repo)
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id})
    if repo.get_regulation(request.regulation_id):
        _error({"code": "CONFLICT", "message": request.regulation_id}, project_id)
    item = Regulation(request.regulation_id, request.jurisdiction, request.authority, request.code, request.title, request.version, None, None, RegulationStatus.NO_VERIFICADA, request.source_url, SourceType.OFFICIAL if request.source_url else SourceType.UNKNOWN, None, [], None, None)
    cli = CLI(repo, actor="api")
    repo.insert_regulation_and_event(item, cli._event(project_id, "REGULATION_REGISTERED", regulation_to_dict(item)))
    return _ok({"regulation": regulation_to_dict(item)}, project_id, repo.get_project(project_id).version)


@router.get("/regulations", dependencies=[Depends(_auth)])
def list_regulations(repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    return _ok({"regulations": [regulation_to_dict(item) for item in repo.list_regulations()]})


@router.get("/regulations/{regulation_id}", dependencies=[Depends(_auth)])
def get_regulation(regulation_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    item = repo.get_regulation(regulation_id)
    if item is None:
        _error({"code": "REGULATION_NOT_FOUND", "message": regulation_id})
    return _ok({"regulation": regulation_to_dict(item)})


@router.post("/regulations/{regulation_id}/status", dependencies=[Depends(_auth)])
def set_regulation_status(regulation_id: str, request: RegulationStatusRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    current = repo.get_regulation(regulation_id)
    if current is None:
        _error({"code": "REGULATION_NOT_FOUND", "message": regulation_id})
    try:
        status = RegulationStatus(request.status.upper())
    except ValueError:
        _error({"code": "INVALID_ARGUMENT", "message": "invalid regulation status"})
    project_id = _regulatory_project(repo)
    item = Regulation(current.regulation_id, current.jurisdiction, current.authority, current.code, current.title, current.version, current.publication_date, current.effective_date, status, current.source_url, current.source_type, current.evidence_hash, current.scope_applicable, current.parent_regulation_id, current.summary, current.version_field + 1)
    cli = CLI(repo, actor="api")
    repo.insert_regulation_and_event(item, cli._event(project_id, "REGULATION_STATUS_CHANGED", regulation_to_dict(item)))
    return _ok({"regulation": regulation_to_dict(item)}, project_id, repo.get_project(project_id).version)


@router.post("/regulations/{regulation_id}/interpretations", dependencies=[Depends(_auth)])
def create_interpretation(regulation_id: str, request: InterpretationCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_regulation(regulation_id) is None:
        _error({"code": "REGULATION_NOT_FOUND", "message": regulation_id})
    project_id = request.applied_to_project_id or _regulatory_project(repo)
    if repo.get_interpretation(request.interpretation_id):
        _error({"code": "CONFLICT", "message": request.interpretation_id}, project_id)
    item = NormativeInterpretation(request.interpretation_id, regulation_id, request.article_reference, request.interpretation_text, request.applied_to_project_id, "api", date.today(), InterpretationConfidence.UNKNOWN, InterpretationState.DRAFT, LEGAL_DISCLAIMER)
    cli = CLI(repo, actor="api")
    repo.insert_interpretation_and_event(item, cli._event(project_id, "NORMATIVE_INTERPRETATION_REGISTERED", interpretation_to_dict(item)))
    return _ok({"interpretation": interpretation_to_dict(item)}, project_id, repo.get_project(project_id).version)


@router.get("/regulations/{regulation_id}/interpretations", dependencies=[Depends(_auth)])
def list_interpretations(regulation_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_regulation(regulation_id) is None:
        _error({"code": "REGULATION_NOT_FOUND", "message": regulation_id})
    return _ok({"interpretations": [interpretation_to_dict(item) for item in repo.list_interpretations(regulation_id)]})


@router.post("/interpretations/{interpretation_id}/review", dependencies=[Depends(_auth)])
def review_interpretation(interpretation_id: str, request: InterpretationReviewRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    current = repo.get_interpretation(interpretation_id)
    if current is None:
        _error({"code": "INTERPRETATION_NOT_FOUND", "message": interpretation_id})
    if not request.actor or not request.authority:
        _error({"code": "INVALID_ARGUMENT", "message": "actor and authority required"})
    project_id = current.applied_to_project_id or _regulatory_project(repo)
    item = NormativeInterpretation(current.interpretation_id, current.regulation_id, current.article_reference, current.interpretation_text, current.applied_to_project_id, request.actor, current.interpretation_date, current.confidence, InterpretationState.REVIEWED, LEGAL_DISCLAIMER, current.version + 1)
    cli = CLI(repo, actor=request.actor)
    repo.insert_interpretation_and_event(item, cli._event(project_id, "NORMATIVE_INTERPRETATION_REVIEWED", {**interpretation_to_dict(item), "authority": request.authority}))
    return _ok({"interpretation": interpretation_to_dict(item), "authority": request.authority, "applicable": True}, project_id, repo.get_project(project_id).version)


@router.post("/projects/{project_id}/normative-snapshots", dependencies=[Depends(_auth)])
def create_normative_snapshot(project_id: str, request: SnapshotCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if repo.get_normative_snapshot(request.snapshot_id):
        _error({"code": "CONFLICT", "message": request.snapshot_id}, project_id)
    try:
        cut_date = date.fromisoformat(request.cut_date)
    except ValueError:
        _error({"code": "INVALID_ARGUMENT", "message": "cut_date must be YYYY-MM-DD"}, project_id)
    item = NormativeSnapshot(request.snapshot_id, project_id, cut_date, request.jurisdiction, [r.regulation_id for r in repo.list_regulations()], [i.interpretation_id for i in repo.list_interpretations()], NormativeSnapshotState.DRAFT, None, datetime.now(timezone.utc))
    cli = CLI(repo, actor="api")
    repo.insert_snapshot_and_event(item, cli._event(project_id, "NORMATIVE_SNAPSHOT_CREATED", snapshot_to_dict(item)))
    return _ok({"snapshot": snapshot_to_dict(item)}, project_id, repo.get_project(project_id).version)


@router.get("/projects/{project_id}/normative-snapshots", dependencies=[Depends(_auth)])
def list_normative_snapshots(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"snapshots": [snapshot_to_dict(item) for item in repo.list_normative_snapshots(project_id)]}, project_id, repo.get_project(project_id).version)


@router.post("/normative-snapshots/{snapshot_id}/freeze", dependencies=[Depends(_auth)])
def freeze_normative_snapshot(snapshot_id: str, request: SnapshotFreezeRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    current = repo.get_normative_snapshot(snapshot_id)
    if current is None:
        _error({"code": "SNAPSHOT_NOT_FOUND", "message": snapshot_id})
    if current.state == NormativeSnapshotState.FROZEN:
        _error({"code": "INVALID_STATE", "message": "FROZEN snapshot is immutable"}, current.project_id)
    item = NormativeSnapshot(current.snapshot_id, current.project_id, current.cut_date, current.jurisdiction, current.regulations_included, current.interpretations_included, NormativeSnapshotState.FROZEN, request.reviewer, current.created_at, current.version + 1)
    cli = CLI(repo, actor=request.reviewer)
    repo.insert_snapshot_and_event(item, cli._event(current.project_id, "NORMATIVE_SNAPSHOT_FROZEN", snapshot_to_dict(item)))
    return _ok({"snapshot": snapshot_to_dict(item)}, current.project_id, repo.get_project(current.project_id).version)


@router.post("/projects/{project_id}/planning/instruments", dependencies=[Depends(_auth)])
def link_planning_instrument(project_id: str, request: PlanningInstrumentLinkRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    instrument = repo.get_planning_instrument(request.instrument_id)
    if instrument is None:
        _error({"code": "PLANNING_INSTRUMENT_NOT_FOUND", "message": request.instrument_id}, project_id)
    if any(item.instrument_id == request.instrument_id for item in repo.list_project_planning_instruments(project_id)):
        _error({"code": "PLANNING_INSTRUMENT_ALREADY_LINKED", "message": request.instrument_id}, project_id)
    project.version += 1
    cli = CLI(repo, actor="api")
    cli.current_project = project_id
    event = cli._event(project_id, "PLANNING_INSTRUMENT_LINKED", {"instrument_id": instrument.instrument_id})
    repo.link_planning_instrument_and_event(project, instrument.instrument_id, "api", event)
    value = asdict(instrument)
    value["instrument_type"] = instrument.instrument_type.value
    value["status"] = instrument.status.value
    value["scope_applicable"] = [scope.value for scope in instrument.scope_applicable]
    value["approval_date"] = instrument.approval_date.isoformat() if instrument.approval_date else None
    return _ok({"instrument": value, "linked": True, "constraint_created": False}, project_id, project.version)


@router.get("/projects/{project_id}/planning/instruments", dependencies=[Depends(_auth)])
def project_planning_instruments(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    values = []
    for item in repo.list_project_planning_instruments(project_id):
        value = asdict(item)
        value["instrument_type"] = item.instrument_type.value
        value["status"] = item.status.value
        value["scope_applicable"] = [scope.value for scope in item.scope_applicable]
        value["approval_date"] = item.approval_date.isoformat() if item.approval_date else None
        values.append(value)
    return _ok({"instruments": values}, project_id, project.version)


@router.post("/projects/{project_id}/simulations", dependencies=[Depends(_auth)])
def create_simulation(project_id: str, request: SimulationCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        simulation_type = SimulationType(request.simulation_type.upper())
    except ValueError:
        _error({"code": "INVALID_ARGUMENT", "message": "invalid simulation_type"}, project_id)
    method = METHODS.get(request.method)
    if method is None:
        _error({"code": "METHOD_NOT_FOUND", "message": request.method}, project_id)
    if method["type"] != simulation_type.value:
        _error({"code": "METHOD_TYPE_MISMATCH", "message": request.method}, project_id)
    missing = [key for key in method["inputs_required"] if key not in request.inputs]
    if missing:
        _error({"code": "INSUFFICIENT_INPUTS", "message": "missing inputs: " + ", ".join(missing), "data": {"missing_inputs": missing}}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f'/PROJECT OPEN "{project_id}"'), project_id)
    payload = json.dumps(request.inputs, sort_keys=True, separators=(",", ":"))
    result = cli.execute(f"/SIMULATE RUN {simulation_type.value} {request.method} '{payload}'")
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result.get("data", {}), project_id, project.version if project else None)


@router.get("/projects/{project_id}/simulations", dependencies=[Depends(_auth)])
def list_simulations(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"simulations": [simulation_to_dict(item) for item in project.simulations.values()]}, project_id, project.version)


@router.get("/projects/{project_id}/simulations/{simulation_id}", dependencies=[Depends(_auth)])
def get_simulation(project_id: str, simulation_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    simulation = repo.get_simulation(project_id, simulation_id)
    if simulation is None:
        _error({"code": "SIMULATION_NOT_FOUND", "message": simulation_id}, project_id)
    return _ok({"simulation": simulation_to_dict(simulation)}, project_id, project.version)


@router.post("/projects/{project_id}/multiobjective/pareto", dependencies=[Depends(_auth)])
def multiobjective_pareto(project_id: str, request: MultiobjectiveRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute("/MULTIOBJECTIVE PARETO " + " ".join(request.objectives))
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result.get("data", {}), project_id, project.version if project else None)


@router.post("/projects/{project_id}/multiobjective/tradeoffs", dependencies=[Depends(_auth)])
def multiobjective_tradeoffs(project_id: str, request: MultiobjectiveRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if len(request.objectives) != 2:
        _error({"code": "INVALID_ARGUMENT", "message": "exactly two objectives required"}, project_id)
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute("/MULTIOBJECTIVE TRADEOFFS " + " ".join(request.objectives))
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result.get("data", {}), project_id, project.version if project else None)


@router.get("/projects/{project_id}/multiobjective", dependencies=[Depends(_auth)])
def list_multiobjective(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    values = []
    for item in repo.list_multiobjective_results(project_id):
        value = asdict(item)
        value["state"] = item.state.value
        values.append(value)
    return _ok({"multiobjectives": values}, project_id, project.version)


@router.get("/projects/{project_id}/multiobjective/{multiobjective_id}", dependencies=[Depends(_auth)])
def get_multiobjective(project_id: str, multiobjective_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    item = repo.get_multiobjective_result(project_id, multiobjective_id)
    if item is None:
        _error({"code": "MULTIOBJECTIVE_NOT_FOUND", "message": multiobjective_id}, project_id)
    value = asdict(item)
    value["state"] = item.state.value
    return _ok({"multiobjective": value}, project_id, project.version)


@router.post("/projects/{project_id}/variables", dependencies=[Depends(_auth)])
def create_project_variable(project_id: str, request: ProjectVariableCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        variable = ProjectVariable(request.variable_id, project_id, normalized_key(request.normalized_key), VariableType(request.variable_type.upper()), request.value, request.actor_id, request.authority, request.unit, request.spatial_scope, request.source, 1, None, request.normative_reference)
        if variable.variable_id in project.project_variables or any(item.get("normalized_key") == variable.normalized_key for item in project.project_variables.values()):
            _error({"code": "CONFLICT", "message": "project variable key already exists"}, project_id)
        variable_payload = {**asdict(variable), "variable_type": variable.variable_type.value}
        event = CLI(repo, actor=request.actor_id)._event(project_id, "PROJECT_VARIABLE_RECORDED", variable_payload)
        repo.add_event(event)
    except (ValueError, KeyError) as exc:
        _error({"code": "INVALID_INPUTS", "message": str(exc)}, project_id)
    return _ok({"variable": variable_payload}, project_id, repo.get_project(project_id).version)


@router.get("/projects/{project_id}/variables", dependencies=[Depends(_auth)])
def list_project_variables(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"variables": list(project.project_variables.values())}, project_id, project.version)


@router.post("/projects/{project_id}/feasibility", dependencies=[Depends(_auth)])
def check_feasibility(project_id: str, request: FeasibilityCheckRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    result = evaluate_feasibility(request.alternative_id, request.values, [asdict(item) for item in project.constraints.values()])
    repo.add_event(CLI(repo, actor="api")._event(project_id, "FEASIBILITY_EVALUATED", serialize_result(result)))
    return _ok({"feasibility": serialize_result(result), "decision_created": False, "recommendation_created": False}, project_id, project.version)


@router.post("/projects/{project_id}/multiobjective/feasible-pareto", dependencies=[Depends(_auth)])
def feasible_pareto(project_id: str, request: FeasibleParetoRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    from sicl.feasibility import FeasibilityState, FeasibilityResult, ConstraintCheck
    results = []
    for payload in project.feasibility_results.values():
        checks = tuple(ConstraintCheck(**item) for item in payload.get("checks", []))
        results.append(FeasibilityResult(payload["alternative_id"], FeasibilityState(payload["state"]), checks, tuple(payload.get("failed_constraint_ids", [])), tuple(payload.get("unknown_constraint_ids", [])), tuple(payload.get("insufficient_constraint_ids", [])), tuple(), tuple(), payload.get("evaluated_by", "api")))
    return _ok({"pareto_front": request.pareto_front, "feasible_pareto_front": feasible_pareto_front(request.pareto_front, results)}, project_id, project.version)


@router.get("/projects", dependencies=[Depends(_auth)])
def list_projects(repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    projects = [asdict(project) for project in repo.list_projects()]
    return _ok({"projects": projects})


@router.post("/projects", dependencies=[Depends(_auth)])
def create_project(request: CanonicalProjectCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    cli = CLI(repo, actor=request.actor)
    spatial_scope = request.spatial_scope
    temporal_scope = request.temporal_scope
    if isinstance(spatial_scope, dict):
        spatial_scope = spatial_scope.get("scope") or spatial_scope.get("value")
    if isinstance(temporal_scope, dict):
        temporal_scope = temporal_scope.get("scope") or temporal_scope.get("value")
    command = f'/PROJECT CREATE "{request.project_id}" "{request.name}"'
    if spatial_scope is not None:
        command += f' "{spatial_scope}"'
        if temporal_scope is not None:
            command += f' "{temporal_scope}"'
    result = cli.execute(command)
    _error(result, request.project_id)
    snapshot, version = _snapshot(repo, request.project_id)
    return _ok({"snapshot": snapshot}, request.project_id, version)


@router.get("/projects/{project_id}/snapshot", dependencies=[Depends(_auth)])
def snapshot(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    value, version = _snapshot(repo, project_id)
    return _ok({"snapshot": value}, project_id, version)


@router.get("/projects/{project_id}/history", dependencies=[Depends(_auth)])
def history(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    _snapshot(repo, project_id)
    return _ok({"events": [asdict(event) for event in repo.events(project_id)]}, project_id, repo.get_project(project_id).version)


@router.post("/projects/{project_id}/commands", dependencies=[Depends(_auth)])
def command(project_id: str, request: CanonicalCommandRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor=request.actor)
    opened = cli.execute(f"/PROJECT OPEN {project_id}")
    _error(opened, project_id)
    result = cli.execute(request.command)
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok(result.get("data", {}), project_id, project.version if project else None)


@router.post("/projects/{project_id}/preferences", dependencies=[Depends(_auth)])
def preference(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    actor = str(request.payload.get("actor", "api"))
    cli = CLI(repo, actor=actor)
    statement = str(request.payload.get("statement", request.payload.get("text", ""))).strip()
    if not statement:
        _error({"code": "INVALID_ARGUMENT", "message": "Preference statement required"}, project_id)
    project = repo.get_project(project_id)
    preference = Preference(f"PREF-{uuid.uuid4().hex[:10]}", project_id, statement, actor)
    project.preferences[preference.preference_id] = preference
    project.version += 1
    repo.insert_entity_and_event(
        "INSERT INTO preferences VALUES (?, ?, ?, ?, ?)",
        (preference.preference_id, project_id, statement, actor, preference.version),
        project,
        cli._event(project_id, "PREFERENCE_RECORDED", asdict(preference)),
    )
    return _ok({"preference": asdict(preference)}, project_id, project.version)


@router.post("/projects/{project_id}/human-reviews", dependencies=[Depends(_auth)])
def human_review(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    p = request.payload
    args = [str(p.get("actor", "")), str(p.get("timestamp", "")), str(p.get("review", "")), str(p.get("reason", "")), str(p.get("authority", ""))]
    cli = CLI(repo, actor=args[0] or "api")
    result = cli.execute("/PROJECT OPEN " + project_id)
    _error(result, project_id)
    result = cli.execute('/HUMAN REVIEW ' + ' '.join(f'"{item}"' for item in args))
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"human_review": result.get("data", {})}, project_id, project.version if project else None)


@router.post("/projects/{project_id}/decisions", dependencies=[Depends(_auth)])
def decision(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    p = request.payload
    actor = str(p.get("actor", ""))
    authority = str(p.get("authority", ""))
    statement = str(p.get("statement", ""))
    cli = CLI(repo, actor=actor or "api")
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute(f'/DECISION RECORD "{statement}" "{actor}" "{authority}"')
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"decision": result.get("data", {})}, project_id, project.version if project else None)


@router.post("/projects/{project_id}/recommendations", dependencies=[Depends(_auth)])
def recommendation(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    cli = CLI(repo, actor=str(request.payload.get("actor", "api")))
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute("/RECOMMEND")
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"recommendation": result.get("data", {})}, project_id, project.version if project else None)


@router.get("/projects/{project_id}/council", dependencies=[Depends(_auth)])
def council(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    value, version = _snapshot(repo, project_id)
    return _ok({"read_only": True, "finding": "Council projection requires comparison and recommendation data.", "snapshot": value, "comparisons": list(value.get("comparisons", {}).values()), "recommendations": list(value.get("recommendations", {}).values()), "decision_created": False}, project_id, version)


@router.post("/projects/{project_id}/site-observations", dependencies=[Depends(_auth)])
def site_observation(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if repo.get_project(project_id) is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    location = str(request.payload.get("location", "")).strip()
    if not location:
        _error({"code": "INVALID_ARGUMENT", "message": "location required"}, project_id)
    cli = CLI(repo, actor=str(request.payload.get("actor", "api")))
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute(f'/SITE INTELLIGENCE "{location}"')
    _error(result, project_id)
    observation = get_site_observation(location)
    project = repo.get_project(project_id)
    return _ok({"observation": asdict(observation), "result": result.get("data", {})}, project_id, project.version if project else None)


@router.post("/projects/{project_id}/agents/{agent}/evaluations", dependencies=[Depends(_auth)])
def agent_evaluation(project_id: str, agent: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    if agent.lower() not in {"bioclimatic", "structural", "economic"}:
        _error({"code": "INVALID_ARGUMENT", "message": "agent must be bioclimatic, structural or economic"}, project_id)
    alternative = str(request.payload.get("alternative_id", "")).strip()
    cli = CLI(repo, actor=str(request.payload.get("actor", "api")))
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute(f"/AGENT RUN {agent.upper()} {alternative}")
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"evaluation": result.get("data", {}).get("evaluation"), "source": "EXPERT_SYSTEM", "decision_created": False}, project_id, project.version if project else None)


@router.post("/projects/{project_id}/pareto", dependencies=[Depends(_auth)])
def pareto(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    objectives = request.payload.get("objectives", [])
    if not isinstance(objectives, list) or len(objectives) != 2:
        _error({"code": "INVALID_ARGUMENT", "message": "exactly two objectives required"}, project_id)
    cli = CLI(repo, actor=str(request.payload.get("actor", "api")))
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute(f"/PARETO {objectives[0]} {objectives[1]}")
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({**result.get("data", {}), "decision_created": False}, project_id, project.version if project else None)


@router.post("/projects/{project_id}/debate", dependencies=[Depends(_auth)])
def debate(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    alternative = str(request.payload.get("alternative_id", "")).strip()
    cli = CLI(repo, actor=str(request.payload.get("actor", "api")))
    _error(cli.execute(f"/PROJECT OPEN {project_id}"), project_id)
    result = cli.execute(f"/DEBATE {alternative}")
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"text": result.get("data", {}).get("text", ""), "decision_created": False}, project_id, project.version if project else None)


@router.post("/projects/{project_id}/evidence", dependencies=[Depends(_auth)])
def create_evidence(project_id: str, request: EvidenceCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if project.stage == "CLOSED":
        _error({"code": "INVALID_STATE", "message": "Project is CLOSED"}, project_id)
    if repo.get_evidence(project_id, request.evidence_id) is not None:
        _error({"code": "EVIDENCE_ALREADY_EXISTS", "message": request.evidence_id}, project_id)
    try:
        evidence_type = EvidenceType(request.evidence_type.upper())
    except ValueError:
        _error({"code": "INVALID_EVIDENCE_TYPE", "message": request.evidence_type}, project_id)
    state = request.state.upper()
    if state not in KNOWLEDGE_STATES:
        _error({"code": "INVALID_STATE", "message": request.state}, project_id)
    captured_at = request.captured_at or datetime.now(timezone.utc)
    if captured_at.tzinfo is None:
        captured_at = captured_at.replace(tzinfo=timezone.utc)
    captured_at = captured_at.astimezone(timezone.utc)
    evidence = Evidence(
        evidence_id=request.evidence_id,
        project_id=project_id,
        source_id=request.source_id,
        statement=request.statement,
        evidence_type=evidence_type,
        captured_at=captured_at,
        method_version=request.method_version,
        evidence_url=request.evidence_url,
        evidence_hash=request.evidence_hash or hashlib.sha256(request.statement.encode("utf-8")).hexdigest(),
        state=state,
    )
    project.evidence[evidence.evidence_id] = evidence
    project.version += 1
    cli = CLI(repo, actor="api")
    repo.insert_evidence_and_event(
        evidence,
        project,
        cli._event(project_id, "EVIDENCE_ADDED", {"evidence_id": evidence.evidence_id, "statement": evidence.statement, "evidence_type": evidence.evidence_type.value, "state": evidence.state}),
    )
    return _ok({"evidence": asdict(evidence)}, project_id, project.version)


@router.post("/projects/{project_id}/sources", dependencies=[Depends(_auth)])
def create_source(project_id: str, request: SourceCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if project.stage == "CLOSED":
        _error({"code": "INVALID_STATE", "message": "Project is CLOSED"}, project_id)
    if request.source_id in project.sources:
        _error({"code": "SOURCE_ALREADY_EXISTS", "message": request.source_id}, project_id)
    try:
        source_type = SourceType(request.source_type.upper())
    except ValueError:
        _error({"code": "INVALID_SOURCE_TYPE", "message": request.source_type}, project_id)
    source = Source(request.source_id, project_id, source_type, request.title, request.url, 1)
    project.sources[source.source_id] = source
    project.version += 1
    cli = CLI(repo, actor="api")
    repo.insert_entity_and_event(
        "INSERT INTO sources(source_id, project_id, source_type, title, url, version) VALUES (?, ?, ?, ?, ?, ?)",
        (source.source_id, source.project_id, source.source_type.value, source.title, source.url, source.version),
        project,
        cli._event(project_id, "SOURCE_ADDED", asdict(source)),
    )
    return _ok({"source": asdict(source)}, project_id, project.version)


@router.get("/projects/{project_id}/sources", dependencies=[Depends(_auth)])
def list_sources(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"sources": [asdict(item) for item in project.sources.values()]}, project_id, project.version)


@router.get("/projects/{project_id}/sources/{source_id}", dependencies=[Depends(_auth)])
def get_source(project_id: str, source_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    source = project.sources.get(source_id)
    if source is None:
        _error({"code": "SOURCE_NOT_FOUND", "message": source_id}, project_id)
    return _ok({"source": asdict(source)}, project_id, project.version)


@router.post("/projects/{project_id}/evaluations", dependencies=[Depends(_auth)])
def create_evaluation(project_id: str, request: EvaluationCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if request.alternative is None or request.objective is None or request.value is None:
        _error({"code": "INVALID_ARGUMENT", "message": "alternative, objective and value are required"}, project_id)
    alternative = next((item for item in project.alternatives.values() if item.alternative_id == request.alternative or item.name == request.alternative.upper()), None)
    if alternative is None:
        raise HTTPException(status_code=404, detail={"contract_version": CONTRACT_VERSION, "status": "ERROR", "code": "ALTERNATIVE_NOT_FOUND", "message": request.alternative, "project_id": project_id, "observed_version": project.version, "data": {}})
    objective = next((item for item in project.objectives.values() if item.objective_id == request.objective or item.key == request.objective), None)
    if objective is None:
        raise HTTPException(status_code=404, detail={"contract_version": CONTRACT_VERSION, "status": "ERROR", "code": "OBJECTIVE_NOT_FOUND", "message": request.objective, "project_id": project_id, "observed_version": project.version, "data": {}})
    if any(item.alternative_id == alternative.alternative_id and item.objective_id == objective.objective_id for item in project.evaluations.values()):
        _error({"code": "CONFLICT", "message": "evaluation already exists for alternative and objective"}, project_id)
    try:
        confidence = float(request.confidence)
    except (TypeError, ValueError):
        _error({"code": "INVALID_ARGUMENT", "message": "confidence must be numeric"}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f'/PROJECT OPEN "{project_id}"'), project_id)
    result = cli.execute(f'/EVALUATE "{alternative.name}" "{objective.key}" {request.value} "{request.unit}" {confidence} "{request.source}"')
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"evaluation": result.get("data", {})}, project_id, project.version if project else None)


@router.get("/projects/{project_id}/evaluations", dependencies=[Depends(_auth)])
def list_evaluations(project_id: str, alternative: str | None = None, objective: str | None = None, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    values = list(project.evaluations.values())
    if alternative:
        found = next((item for item in project.alternatives.values() if item.alternative_id == alternative or item.name == alternative.upper()), None)
        values = [item for item in values if found and item.alternative_id == found.alternative_id]
    if objective:
        found = next((item for item in project.objectives.values() if item.objective_id == objective or item.key == objective), None)
        values = [item for item in values if found and item.objective_id == found.objective_id]
    return _ok({"evaluations": [asdict(item) for item in values]}, project_id, project.version)


@router.post("/projects/{project_id}/comparisons", dependencies=[Depends(_auth)])
def create_comparison(project_id: str, request: ComparisonCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if request.alternatives is None or len(request.alternatives) < 2:
        _error({"code": "INVALID_ARGUMENT", "message": "at least two alternatives are required"}, project_id)
    selected = []
    for name in request.alternatives:
        alternative = next((item for item in project.alternatives.values() if item.alternative_id == name or item.name == name.upper()), None)
        if alternative is None:
            raise HTTPException(status_code=404, detail={"contract_version": CONTRACT_VERSION, "status": "ERROR", "code": "ALTERNATIVE_NOT_FOUND", "message": name, "project_id": project_id, "observed_version": project.version, "data": {}})
        selected.append(alternative)
    ids = [item.alternative_id for item in selected]
    if len(set(ids)) < 2:
        _error({"code": "INVALID_ARGUMENT", "message": "alternatives must be distinct"}, project_id)
    if any(set(item.alternative_ids) == set(ids) for item in project.comparisons.values()):
        _error({"code": "CONFLICT", "message": "comparison already exists for this alternative set"}, project_id)
    cli = CLI(repo, actor="api")
    _error(cli.execute(f'/PROJECT OPEN "{project_id}"'), project_id)
    result = cli.execute("/COMPARE " + " ".join(f'"{item.name}"' for item in selected))
    _error(result, project_id)
    project = repo.get_project(project_id)
    return _ok({"comparison": result.get("data", {}), "objectives": request.objectives or []}, project_id, project.version if project else None)


@router.get("/projects/{project_id}/comparisons", dependencies=[Depends(_auth)])
def list_comparisons(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"comparisons": [asdict(item) for item in project.comparisons.values()]}, project_id, project.version)


@router.get("/projects/{project_id}/evidence", dependencies=[Depends(_auth)])
def list_evidence(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"evidence": [asdict(item) for item in repo.list_evidence(project_id)]}, project_id, project.version)


@router.post("/projects/{project_id}/spatial-evidence", dependencies=[Depends(_auth)])
def add_spatial_evidence(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Add a manual/external/photo-backed observation using canonical Evidence."""
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    payload = request.payload
    statement = str(payload.get("statement", "")).strip()
    if not statement:
        _error({"code": "INVALID_ARGUMENT", "message": "statement is required"}, project_id)
    try:
        observation = validate_observation(payload)
        requested_evidence_type = str(payload.get("evidence_type", "OBSERVATION")).upper()
        evidence_type = EvidenceType.OBSERVATION if requested_evidence_type == "PHOTO" else EvidenceType(requested_evidence_type)
    except (ValueError, KeyError) as exc:
        _error({"code": "INVALID_INPUTS", "message": str(exc)}, project_id)
    evidence_id = str(payload.get("evidence_id") or f"EVD-{uuid.uuid4().hex[:12]}")
    if repo.get_evidence(project_id, evidence_id) is not None:
        _error({"code": "CONFLICT", "message": f"evidence already exists: {evidence_id}"}, project_id)
    actor = str(payload.get("actor", "api"))
    captured_at_text = payload.get("captured_at") or datetime.now(timezone.utc).isoformat()
    try:
        captured_at = datetime.fromisoformat(str(captured_at_text).replace("Z", "+00:00"))
    except ValueError as exc:
        _error({"code": "INVALID_INPUTS", "message": "captured_at must be an ISO timestamp"}, project_id)
    evidence_state = str(payload.get("evidence_state", "OBSERVED"))
    evidence = Evidence(evidence_id=evidence_id, project_id=project_id, source_id=payload.get("source_id"), statement=statement, evidence_type=evidence_type, captured_at=captured_at, method_version=str(payload.get("method_version", "SPATIAL-EVIDENCE/1")), evidence_url=payload.get("evidence_url"), evidence_hash=payload.get("evidence_hash") or hashlib.sha256(statement.encode("utf-8")).hexdigest(), state=evidence_state)
    project.evidence[evidence_id] = evidence
    project.version += 1
    metadata = {"evidence_id": evidence_id, "statement": statement, "spatial_scope": observation["spatial_scope"], "observation_type": payload.get("observation_type", "MANUAL_OBSERVATION"), "value": payload.get("value"), "unit": observation["unit"], "qualifier": observation["qualifier"], "epistemic_state": observation["epistemic_state"], "relevance": observation["relevance"], "source_kind": payload.get("source_kind", "USER / FIELD_OBSERVATION"), "actor": actor, "observed_at": payload.get("observed_at"), "captured_at": captured_at.isoformat(), "retrieved_at": payload.get("retrieved_at"), "observation_point": payload.get("observation_point"), "photo_reference": payload.get("photo_reference"), "photo_direction": payload.get("photo_direction", "UNKNOWN"), "specific_object": payload.get("specific_object", "UNKNOWN"), "unknowns": payload.get("unknowns", []), "evidence_hash": evidence.evidence_hash, "media_id": payload.get("media_id"), "media_content_type": payload.get("media_content_type"), "media_byte_size": payload.get("media_byte_size"), "media_original_filename": payload.get("media_original_filename"), "media_storage_key": payload.get("media_storage_key"), "human_confirmed": False, "decision_created": False}
    repo.insert_evidence_and_event(evidence, project, CLI(repo, actor=actor)._event(project_id, "SPATIAL_EVIDENCE_ADDED", metadata))
    return _ok({"evidence": metadata, "decision_created": False}, project_id, project.version)


@router.post("/projects/{project_id}/spatial-evidence/media", dependencies=[Depends(_auth)])
async def add_persistent_spatial_evidence(
    project_id: str,
    file: UploadFile = File(...),
    payload_json: str = Form(...),
    repo: SQLiteRepository = Depends(get_repository),
) -> V1Envelope:
    """Persist image bytes, then associate the generated reference with Evidence."""
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError:
        _error({"code": "INVALID_INPUTS", "message": "payload_json must be valid JSON"}, project_id)
    if not isinstance(payload, dict):
        _error({"code": "INVALID_INPUTS", "message": "payload_json must be an object"}, project_id)
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        _error({"code": "UNSUPPORTED_MEDIA", "message": "only JPEG, PNG and WEBP are supported"}, project_id)
    content = await file.read(MAX_MEDIA_BYTES + 1)
    if len(content) > MAX_MEDIA_BYTES:
        _error({"code": "MEDIA_TOO_LARGE", "message": f"media exceeds {MAX_MEDIA_BYTES} bytes"}, project_id)
    media_id = str(payload.get("media_id") or f"MED-{uuid.uuid4().hex[:16]}")
    try:
        stored = store_media(media_id, content, file.content_type or "application/octet-stream", file.filename or "upload")
    except ValueError as exc:
        _error({"code": "INVALID_MEDIA", "message": str(exc)}, project_id)
    payload.update({
        "evidence_type": "PHOTO",
        "evidence_url": f"/v1/projects/{project_id}/spatial-evidence/media/{stored.media_id}",
        "photo_reference": stored.media_id,
        "evidence_hash": stored.sha256,
        "media_id": stored.media_id,
        "media_content_type": stored.content_type,
        "media_byte_size": stored.byte_size,
        "media_original_filename": stored.original_filename,
        "media_storage_key": stored.storage_key,
    })
    return add_spatial_evidence(project_id, CanonicalWriteRequest(**payload), repo)


@router.get("/projects/{project_id}/spatial-evidence/media/{media_id}", dependencies=[Depends(_auth)])
def retrieve_persistent_spatial_evidence(project_id: str, media_id: str, repo: SQLiteRepository = Depends(get_repository)) -> FileResponse:
    """Retrieve media only through the already-authorized project scope."""
    project = repo.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")
    evidence = repo.get_evidence(project_id, media_id) or next((item for item in repo.list_evidence(project_id) if item.evidence_url and item.evidence_url.endswith(f"/{media_id}")), None)
    if evidence is None:
        raise HTTPException(status_code=404, detail="MEDIA_NOT_FOUND")
    try:
        _, content_type, filename = retrieve_media(media_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="MEDIA_NOT_FOUND") from None
    from sicl.media_storage import media_root
    return FileResponse(media_root() / filename, media_type=content_type, filename=filename, headers={"Cache-Control": "private, max-age=0"})


@router.get("/projects/{project_id}/spatial-evidence", dependencies=[Depends(_auth)])
def list_spatial_evidence(project_id: str, spatial_scope: str | None = None, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        records = evidence_view(repo, project_id, spatial_scope)
    except ValueError as exc:
        _error({"code": "INVALID_SCOPE", "message": str(exc)}, project_id)
    return _ok({"evidence": records, "conflicts": surface_conflicts(records), "spatial_scope": spatial_scope, "decision_created": False}, project_id, project.version)


@router.get("/projects/{project_id}/spatial-evidence/multiscale", dependencies=[Depends(_auth)])
def multiscale_spatial_evidence(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok(multiscale_summary(repo, project_id), project_id, project.version)


@router.post("/projects/{project_id}/spatial-evidence/{evidence_id}/review", dependencies=[Depends(_auth)])
def review_spatial_evidence(project_id: str, evidence_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if repo.get_evidence(project_id, evidence_id) is None:
        _error({"code": "EVIDENCE_NOT_FOUND", "message": evidence_id}, project_id)
    payload = request.payload
    actor = str(payload.get("actor", "human")); authority = str(payload.get("authority", "project_owner")); status = str(payload.get("status", "APPROVED")).upper()
    if status not in {"APPROVED", "REJECTED", "PENDING"}:
        _error({"code": "INVALID_INPUTS", "message": "status must be APPROVED, REJECTED or PENDING"}, project_id)
    review = HumanReview(f"REV-{uuid.uuid4().hex[:10]}", project_id, actor, datetime.now(timezone.utc).isoformat(), str(payload.get("review", "")), str(payload.get("reason", "")), authority, status)
    project.human_reviews[review.review_id] = review; project.version += 1
    repo.insert_entity_and_event("INSERT INTO human_reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (review.review_id, project_id, review.actor, review.timestamp, review.review, review.reason, review.authority, review.status, review.version), project, CLI(repo, actor=actor)._event(project_id, "SPATIAL_EVIDENCE_REVIEWED", {"evidence_id": evidence_id, **asdict(review), "decision_created": False}))
    return _ok({"review": asdict(review), "evidence_id": evidence_id, "decision_created": False}, project_id, project.version)


@router.get("/projects/{project_id}/evidence/{evidence_id}", dependencies=[Depends(_auth)])
def get_evidence(project_id: str, evidence_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    evidence = repo.get_evidence(project_id, evidence_id)
    if evidence is None:
        _error({"code": "EVIDENCE_NOT_FOUND", "message": evidence_id}, project_id)
    return _ok({"evidence": asdict(evidence)}, project_id, project.version)


@router.post("/projects/{project_id}/locations", dependencies=[Depends(_auth)])
def create_project_location(project_id: str, request: SpatialLocationCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if not request.confirm:
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "Location candidate must be explicitly confirmed"}, project_id)
    try:
        location = SpatialLocation(
            location_id=request.location_id or f"LOC-{uuid.uuid4().hex[:12]}",
            project_id=project_id,
            spatial_scope=SpatialScope(request.spatial_scope),
            geometry_type=request.geometry_type,
            geometry=request.geometry,
            crs=request.crs,
            place_label=request.place_label,
            acquisition_method=AcquisitionMethod(request.acquisition_method),
            provenance=LocationProvenance(request.provenance),
            status=LocationStatus.CONFIRMED,
            actor_id=request.actor_id,
            authority=request.authority,
            version=max((item.version for item in project.spatial_locations.values()), default=0) + 1,
            supersedes_location_id=request.supersedes_location_id,
        )
    except (ValueError, KeyError) as exc:
        _error({"code": "INVALID_LOCATION", "message": str(exc)}, project_id)
    if location.location_id in project.spatial_locations:
        _error({"code": "LOCATION_ALREADY_EXISTS", "message": location.location_id}, project_id)
    project.spatial_locations[location.location_id] = location
    project.version += 1
    repo.save(project)
    repo.add_event(CLI(repo, actor=request.actor_id)._event(project_id, "SPATIAL_LOCATION_CONFIRMED", location.to_dict()))
    return _ok({"location": location.to_dict()}, project_id, project.version)


@router.get("/projects/{project_id}/locations", dependencies=[Depends(_auth)])
def list_project_locations(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    locations = [item.to_dict() for item in project.spatial_locations.values()]
    return _ok({"locations": locations}, project_id, project.version)


@router.get("/projects/{project_id}/locations/current", dependencies=[Depends(_auth)])
def current_project_location(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    current = _confirmed_location(project)
    return _ok({"location": current.to_dict() if current else None}, project_id, project.version)


@router.post("/projects/{project_id}/spatial-registrations", dependencies=[Depends(_auth)])
def propose_spatial_registration(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    payload = request.payload
    actor = str(payload.get("actor", "api"))
    registration_id = str(payload.get("registration_id") or f"REG-{uuid.uuid4().hex[:12]}")
    if registration_id in project.spatial_registrations:
        _error({"code": "REGISTRATION_ALREADY_EXISTS", "message": registration_id}, project_id)
    try:
        registration = propose_registration(project_id, payload, registration_id=registration_id, actor=actor)
    except ValueError as exc:
        _error({"code": "INVALID_SPATIAL_REGISTRATION", "message": str(exc)}, project_id)
    project.version += 1
    project.spatial_registrations[registration.registration_id] = registration
    repo.save(project)
    repo.add_event(CLI(repo, actor=actor)._event(project_id, "REGISTRATION_PROPOSED", registration.to_dict()))
    return _ok({"registration": registration.to_dict(), "decision_created": False}, project_id, project.version)


@router.get("/projects/{project_id}/spatial-registrations", dependencies=[Depends(_auth)])
def list_spatial_registrations(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    return _ok({"registrations": [item.to_dict() for item in project.spatial_registrations.values()]}, project_id, project.version)


@router.post("/projects/{project_id}/spatial-registrations/{registration_id}/transition", dependencies=[Depends(_auth)])
def transition_spatial_registration(project_id: str, registration_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    registration = project.spatial_registrations.get(registration_id)
    if registration is None:
        _error({"code": "REGISTRATION_NOT_FOUND", "message": registration_id}, project_id)
    payload = request.payload
    actor = str(payload.get("actor", "api"))
    action = str(payload.get("action", ""))
    try:
        updated = registration_transition(registration, action, actor=actor, side_confirmation=payload.get("site_side_confirmation"))
    except ValueError as exc:
        _error({"code": "INVALID_REGISTRATION_TRANSITION", "message": str(exc)}, project_id)
    project.version += 1
    project.spatial_registrations[registration_id] = updated
    repo.save(project)
    event_type = {"CONFIRM": "REGISTRATION_CONFIRMED", "LOCK": "REGISTRATION_LOCKED", "UNLOCK": "REGISTRATION_RECALIBRATED", "RECALIBRATE": "REGISTRATION_RECALIBRATED"}[action]
    repo.add_event(CLI(repo, actor=actor)._event(project_id, event_type, updated.to_dict()))
    return _ok({"registration": updated.to_dict(), "decision_created": False, "human_authority": True}, project_id, project.version)


@router.post("/projects/{project_id}/georeferenced-site/parse", dependencies=[Depends(_auth)])
async def parse_georeferenced_site(project_id: str, file: UploadFile = File(...), repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Preview a KML/KMZ as untrusted input; parsing never confirms a boundary."""
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        data = await file.read()
        if len(data) > 20 * 1024 * 1024:
            _error({"code": "INVALID_LOCATION", "message": "site file exceeds 20 MiB"}, project_id)
        result = parse_kml(data, file.filename or "site.kml")
    except (ValueError, UnicodeError) as exc:
        _error({"code": "INVALID_LOCATION", "message": str(exc)}, project_id)
    result["human_confirmation_required"] = result["classification"] in {"VALID_SINGLE_POLYGON", "MULTIPLE_POLYGONS", "AMBIGUOUS_SITE_BOUNDARY"}
    result["project_id"] = project_id
    return _ok({"site_preview": result, "confirmed": False, "decision_created": False}, project_id, project.version)


@router.post("/projects/{project_id}/georeferenced-site/confirm", dependencies=[Depends(_auth)])
def confirm_georeferenced_site(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Confirm a validated point/polygon into the existing SpatialLocation state."""
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    payload = request.payload
    actor = str(payload.get("actor", "api"))
    if payload.get("human_confirmed") is not True or payload.get("confirm") is not True:
        _error({"code": "HUMAN_CONFIRMATION_REQUIRED", "message": "georeferenced site requires explicit human confirmation"}, project_id)
    geometry = payload.get("geometry")
    if not isinstance(geometry, dict) or geometry.get("type") not in {"Point", "Polygon"}:
        _error({"code": "INVALID_LOCATION", "message": "Point or Polygon GeoJSON geometry required"}, project_id)
    crs = str(payload.get("crs", "EPSG:4326"))
    validation = {"state": "VALID"}
    metrics = None
    frame = None
    if geometry["type"] == "Point":
        try:
            coords = geometry["coordinates"]
            point = normalize_reference_point(float(coords[0]), float(coords[1]), crs=crs, elevation=payload.get("elevation"), source=payload.get("source", "USER_INPUT"), accuracy=payload.get("accuracy"), actor_id=actor)
        except (ValueError, IndexError, TypeError) as exc:
            _error({"code": "INVALID_LOCATION", "message": str(exc)}, project_id)
        validation = {"state": "VALID", "boundary_state": "UNKNOWN"}
    else:
        coordinates = geometry.get("coordinates", [])
        if len(coordinates) != 1 or not isinstance(coordinates[0], list):
            _error({"code": "INVALID_LOCATION", "message": "Only a single Polygon ring can be confirmed in this phase"}, project_id)
        validation = validate_polygon(coordinates[0], crs)
        if validation["state"] != "VALID":
            _error({"code": "INVALID_LOCATION", "message": validation}, project_id)
        metrics = polygon_metrics(coordinates[0], crs)
        frame = local_project_frame(coordinates[0], crs=crs)
    try:
        location = SpatialLocation(location_id=payload.get("location_id") or f"LOC-{uuid.uuid4().hex[:12]}", project_id=project_id, spatial_scope=SpatialScope.PARCELA_SITIO, geometry_type=geometry["type"], geometry=geometry, crs=crs, place_label=payload.get("place_label"), acquisition_method=AcquisitionMethod(payload.get("acquisition_method", "USER_INPUT")), provenance=LocationProvenance(payload.get("provenance", "USER_DECLARED")), status=LocationStatus.CONFIRMED, actor_id=actor, authority=payload.get("authority", "project_owner"), version=max((item.version for item in project.spatial_locations.values()), default=0) + 1, supersedes_location_id=payload.get("supersedes_location_id"))
    except (ValueError, KeyError) as exc:
        _error({"code": "INVALID_LOCATION", "message": str(exc)}, project_id)
    project.spatial_locations[location.location_id] = location
    project.version += 1
    repo.save(project)
    repo.add_event(CLI(repo, actor=actor)._event(project_id, "GEOREFERENCED_SITE_CONFIRMED", {"location": location.to_dict(), "validation": validation, "metrics": metrics, "local_project_frame": frame, "terrain": "UNKNOWN", "context": "UNKNOWN", "human_confirmed": True}))
    return _ok({"location": location.to_dict(), "validation": validation, "metrics": metrics, "local_project_frame": frame, "site_intelligence": site_intelligence(), "decision_created": False}, project_id, project.version)


@router.post("/projects/{project_id}/georeferenced-site/analyze", dependencies=[Depends(_auth)])
def analyze_georeferenced_site(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Analyze confirmed site geometry without turning context into a decision."""
    project = repo.get_project(project_id)
    if project is None and project_id != "UPAO-001":
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    payload = request.payload
    geometry = payload.get("site_geometry") or payload.get("geometry")
    if not isinstance(geometry, dict):
        _error({"code": "INVALID_LOCATION", "message": "site_geometry is required"}, project_id)
    crs = str(payload.get("crs", "EPSG:4326"))
    metrics = polygon_metrics(geometry.get("coordinates", [[]])[0], crs) if geometry.get("type") == "Polygon" else {"status": "UNKNOWN"}
    frame = local_project_frame(geometry.get("coordinates", [[]])[0], crs=crs) if geometry.get("type") == "Polygon" else {"status": "UNKNOWN"}
    alternative_id = payload.get("alternative_id", "UPAO-001-A")
    site_fit_result: dict[str, Any] = {"state": "UNKNOWN", "reason": "NO_SPATIAL_ALTERNATIVE_SUPPLIED"}
    if project_id == "UPAO-001":
        alternative = next((item for item in generate_upao001_alternatives() if item.alternative_id == alternative_id), None)
        if alternative is not None:
            representation = UPAO001SpatialGenerator().generate(alternative).to_dict()
            footprint = next((item["geometry"] for item in representation["elements"] if item["element_type"] == "BuildingFootprint"), None)
            if footprint is not None:
                site_fit_result = site_fit(geometry, footprint) if crs == "LOCAL_PROJECT_METRIC" else {"state": "UNKNOWN", "reason": "SITE_AND_DESIGN_CRS_MISMATCH"}
    terrain = terrain_query(site_geometry=geometry)
    context = context_query(site_geometry=geometry, extent=str(payload.get("context_extent", "IMMEDIATE")))
    return _ok({"site_geometry": geometry, "crs": crs, "metrics": metrics, "local_project_frame": frame, "site_fit": site_fit_result, "terrain": terrain, "context": context, "provenance": {"site": payload.get("site_provenance", "USER_CONFIRMED_OR_EXTERNAL"), "metrics": "DERIVED_COMPUTATION", "terrain": terrain.get("provider"), "context": context.get("source_type")}, "unknowns": ["Regulatory compliance", "setbacks", "legal ownership", "legal access", "buildability"], "decision_created": False}, project_id, project.version if project else None)


@router.post("/projects/{project_id}/external-context/query", dependencies=[Depends(_auth)])
def query_external_spatial_context(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Query bounded public context and optionally record normalized features as external evidence."""
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        result = query_external_context(request.payload)
    except (ValueError, KeyError) as exc:
        _error({"code": "INVALID_CONTEXT_QUERY", "message": str(exc)}, project_id)
    persisted: list[str] = []
    if bool(request.payload.get("persist", False)) and result.get("features"):
        scope = str(request.payload["spatial_scope"])
        actor = str(request.payload.get("actor", "external-context"))
        for feature in result["features"][:100]:
            properties = feature.get("properties") or {}
            evidence_id = f"EXT-{uuid.uuid4().hex[:12]}"
            statement = f"External {properties.get('category', 'feature')} {properties.get('external_id', 'unknown')}"
            evidence = Evidence(evidence_id, project_id, None, statement, EvidenceType.REFERENCE, datetime.now(timezone.utc), "EXTERNAL-CONTEXT/1", None, hashlib.sha256(statement.encode()).hexdigest(), "EXTERNAL_SOURCE")
            project.evidence[evidence_id] = evidence; project.version += 1
            metadata = {"evidence_id": evidence_id, "spatial_scope": scope, "observation_type": properties.get("category", "external_feature"), "value": feature.get("geometry"), "qualifier": "UNKNOWN", "unit": None, "epistemic_state": "EXTERNAL_SOURCE", "source_kind": "OpenStreetMap / Overpass", "external_id": properties.get("external_id"), "provider": properties.get("provider"), "dataset": properties.get("dataset"), "source_attributes": properties.get("source_attributes", {}), "retrieved_at": properties.get("retrieved_at"), "geometry": feature.get("geometry"), "unknowns": ["legal_access", "verified_building_condition", "regulatory_status"], "decision_created": False}
            repo.insert_evidence_and_event(evidence, project, CLI(repo, actor=actor)._event(project_id, "EXTERNAL_SPATIAL_EVIDENCE_ADDED", metadata, source="EXTERNAL_PROVIDER"))
            persisted.append(evidence_id)
    return _ok({"context": result, "persisted_evidence_ids": persisted, "decision_created": False}, project_id, project.version)


@router.get("/projects/{project_id}/missing-data", dependencies=[Depends(_auth)])
def project_missing_data(project_id: str, spatial_scope: str = "edificacion", repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    try:
        scope = SpatialScope(spatial_scope)
        from sicl.variable_catalog import seed_catalog
        catalog = seed_catalog()
        location = _confirmed_location(project)
        values = project.project_variables
        statuses: list[dict[str, Any]] = []
        for variable_id in catalog.definitions:
            try:
                profile = catalog.profile(variable_id, scope)
            except KeyError:
                continue
            if variable_id in values:
                state = "PRESENT"
                source = values[variable_id].get("source", "PROJECT_VARIABLE")
            elif variable_id == "SITE_COORDINATE_REFERENCE" and location:
                state, source = "PRESENT", location.acquisition_method.value
            elif profile.applicability == "NOT_APPLICABLE":
                state, source = "NOT_APPLICABLE", None
            elif profile.applicability == "NOT_AVAILABLE":
                state, source = "NOT_AVAILABLE", None
            else:
                state, source = "MISSING", None
            statuses.append({"canonical_variable_id": variable_id, "state": state, "source": source, "acquisition_paths": ["USER_INPUT", "MAP_SELECTION", "PROJECT_DOCUMENT", "GIS", "EXTERNAL_SOURCE", "DERIVATION", "ASSUMPTION"] if state == "MISSING" else []})
        solar = "AVAILABLE" if location else "REQUIRES_DATA"
        return _ok({"spatial_scope": scope.value, "location_present": bool(location), "variables": statuses, "capabilities": [{"capability_id": "SOLAR_ANALYSIS", "state": solar, "missing_requirements": [] if location else ["SITE_COORDINATE_REFERENCE"]}]}, project_id, project.version)
    except ValueError as exc:
        _error({"code": "INVALID_SCOPE", "message": str(exc)}, project_id)

@router.get("/projects/{project_id}/spatial-representations", dependencies=[Depends(_auth)])
def spatial_representations(project_id: str, alternative: str | None = None, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Read-only transport for the S2 derived spatial projection.

    UPAO-001 is an explicit synthetic educational fixture. Other projects
    require persisted alternatives and are never silently fabricated.
    """
    project = repo.get_project(project_id)
    if project is None and project_id != "UPAO-001":
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    if project_id == "UPAO-001":
        alternatives = list(generate_upao001_alternatives())
        version = None
    else:
        alternatives = list(project.alternatives.values()) if project else []
        version = project.version if project else None
    if alternative:
        alternatives = [item for item in alternatives if item.alternative_id == alternative or item.name == alternative.upper()]
        if not alternatives:
            _error({"code": "ALTERNATIVE_NOT_FOUND", "message": alternative}, project_id)
    if not alternatives:
        _error({"code": "SPATIAL_REPRESENTATION_UNAVAILABLE", "message": "no alternatives available"}, project_id)
    generator = UPAO001SpatialGenerator()
    try:
        representations = [generator.generate(item) for item in alternatives]
    except Exception as exc:
        _error({"code": "SPATIAL_GENERATION_ERROR", "message": str(exc)}, project_id)
    return _ok(
        {
            "representations": [item.to_dict() for item in representations],
            "metrics": {item.alternative_id: generator.metrics(item) for item in representations},
            "explanations": {item.alternative_id: generator.explain(item) for item in representations},
            "provenance": "SYNTHETIC / EDUCATIONAL / MODEL PROJECT" if project_id == "UPAO-001" else "DERIVED_FROM_PROJECT_ALTERNATIVE",
            "read_only": True,
        },
        project_id,
        version,
    )


@router.get("/examples/{example_id}/pareto", dependencies=[Depends(_auth)])
def upao001_pareto_transport(example_id: str) -> V1Envelope:
    """Read-only transport for the canonical UPAO-001 educational Pareto dataset."""
    if example_id != "UPAO-001":
        _error({"code": "EXAMPLE_NOT_FOUND", "message": example_id})

    generator = UPAO001SpatialGenerator()
    representations = [
        generator.generate(item) for item in generate_upao001_alternatives()
    ]
    dataset = build_upao001_dataset(representations)
    values = {
        (item.alternative_id, item.objective_id): item.value
        for item in dataset.evaluations
    }
    statuses = {item: "NON_DOMINATED" for item in dataset.pareto.non_dominated}
    statuses.update({item: "DOMINATED" for item in dataset.pareto.dominated})
    statuses.update({item: "INCOMPLETE" for item in dataset.pareto.incomplete})

    alternatives = []
    for representation in representations:
        alternative_id = representation.alternative_id
        alternatives.append(
            {
                "alternative_id": alternative_id,
                "gross_massing_area": values[(alternative_id, "OBJ-GROSS-MASSING-AREA")],
                "gross_massing_area_unit": "m²",
                "open_site_area": values[(alternative_id, "OBJ-OPEN-SITE-AREA")],
                "open_site_area_unit": "m²",
                "raw_pareto_status": statuses[alternative_id],
            }
        )

    return _ok(
        {
            "example_id": example_id,
            "objectives": ["GROSS_MASSING_AREA", "OPEN_SITE_AREA"],
            "alternatives": alternatives,
            "provenance": list(dataset.provenance),
            "read_only": True,
            "evaluations_persisted": False,
            "feasible_pareto_used": False,
            "recommendation_created": dataset.recommendation_created,
            "human_review_created": dataset.human_review_created,
            "decision_created": dataset.decision_created,
        }
    )


@router.get("/examples/{example_id}/territorial-environment", dependencies=[Depends(_auth)])
def territorial_environment(example_id: str, selected_date: str, selected_time: str = "12:00", spatial_scope: str = "distrito_ciudad", include_air_quality: bool = True, include_climate: bool = True) -> V1Envelope:
    if example_id != "UPAO-001":
        _error({"code": "EXAMPLE_NOT_FOUND", "message": example_id}, example_id)
    allowed_scopes = {"distrito_ciudad", "provincia_metropoli", "region", "macro_region", "pais"}
    if spatial_scope not in allowed_scopes:
        _error({"code": "SCOPE_NOT_AUTHORIZED", "message": "TESU-P1 supports only distrito_ciudad, provincia_metropoli, region, macro_region and pais"}, example_id)
    latitude, longitude = -8.1116, -79.0287
    profiles = {
        "distrito_ciudad": {"role": "LOCAL_CONTEXT", "visual": "POINT_CONTEXT + PROVIDER_MODEL_GRID", "goal": "Understand city-district environmental context", "resolution": "provider cell; not administrative boundary"},
        "provincia_metropoli": {"role": "METROPOLITAN_PATTERN", "visual": "PROVIDER_MODEL_GRID + TEMPORAL_SERIES", "goal": "Compare metropolitan environmental patterns", "resolution": "provider cell; not provincial boundary"},
        "region": {"role": "REGIONAL_CONTEXT", "visual": "REGIONAL_PATTERN + TEMPORAL_SERIES", "goal": "Understand regional climate and environmental context", "resolution": "provider model cell; no regional polygon asserted"},
        "macro_region": {"role": "MACRO_REGIONAL_PATTERN", "visual": "PATTERN_COMPARISON + SCENARIO_CONTEXT", "goal": "Compare broader territorial environmental patterns", "resolution": "provider model resolution; no macro-region polygon asserted"},
        "pais": {"role": "NATIONAL_PATTERN", "visual": "NATIONAL_PATTERN + REGIONAL_COMPARISON", "goal": "Explore national environmental patterns without architectural geometry", "resolution": "provider model resolution; no national polygon asserted"},
    }
    profile = profiles[spatial_scope]
    layers: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    if include_air_quality:
        try:
            aq = fetch_open_meteo_air_quality(latitude, longitude, selected_date, location_label="Trujillo / distrito_ciudad proxy")
            index = (aq["hourly"].get("time") or []).index(f"{selected_date}T{selected_time}")
            layers.append({"family": "AIR_QUALITY", "status": "AVAILABLE", "provider": aq["source"], "model": aq["source_model"], "time": f"{selected_date}T{selected_time}", "values": {k: v[index] for k, v in aq["hourly"].items() if k != "time"}, "spatial_resolution": aq["spatial_resolution"], "provenance": aq["evidence_url"]})
        except Exception as exc:
            errors.append({"family": "AIR_QUALITY", "code": "SOURCE_UNAVAILABLE", "message": str(exc)})
    if include_climate:
        try:
            climate = fetch_open_meteo_climate(latitude, longitude, start_date=selected_date, end_date=selected_date, location_label="Trujillo / distrito_ciudad climate proxy")
            layers.append({"family": "CLIMATE", "status": "AVAILABLE", "provider": climate["source"], "model": climate["source_model"], "time_horizon": {"start": climate["start_date"], "end": climate["end_date"]}, "temporal_resolution": climate["temporal_resolution"], "values": {k: (v[0] if isinstance(v, list) and v else None) for k, v in climate["daily"].items() if k != "time"}, "spatial_resolution": climate["spatial_resolution"], "bias_correction": climate["bias_correction"], "provenance": climate["evidence_url"]})
        except Exception as exc:
            errors.append({"family": "CLIMATE", "code": "SOURCE_UNAVAILABLE", "message": str(exc)})
    return _ok({"example_id": example_id, "spatial_scope": spatial_scope, "capability_profile": profile, "representation": profile["visual"], "location": {"name": f"Trujillo / {spatial_scope} provider context", "latitude": latitude, "longitude": longitude, "provenance": "Open-Meteo model output; not local sensor or cadastral boundary"}, "selected_date": selected_date, "selected_time": selected_time, "weather_vs_climate_separated": True, "cross_scale": {"from": "distrito_ciudad", "to": spatial_scope, "containment_asserted": False, "relationship_evidence": "none"}, "layers": layers, "errors": errors, "decision_created": False, "human_review_created": False, "recommendation_created": False, "read_only": True})


@router.get("/examples/{example_id}/environmental-analysis", dependencies=[Depends(_auth)])
def upao001_environmental_analysis(example_id: str, selected_date: str, selected_time: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    """Read-only hourly solar analysis for the approved educational location."""
    if example_id != "UPAO-001":
        _error({"code": "EXAMPLE_NOT_FOUND", "message": example_id})
    if len(selected_time) != 5 or selected_time[2] != ":" or selected_time[3:] != "00":
        _error({"code": "INVALID_DATE_TIME", "message": "selected_time must be an hourly HH:00 value"}, example_id)
    try:
        confirmed = _confirmed_location(repo.get_project(example_id))
        if confirmed is not None:
            source = fetch_open_meteo_solar_coordinates(
                confirmed.latitude, confirmed.longitude, selected_date,
                location_label=confirmed.place_label or f"{confirmed.latitude:.6f}, {confirmed.longitude:.6f}",
            )
            location = EnvironmentalLocation(
                name=confirmed.place_label or "Confirmed project location",
                latitude=confirmed.latitude,
                longitude=confirmed.longitude,
                timezone=source["timezone"],
                location_class="PROJECT_CONFIRMED",
                provenance=f"{confirmed.provenance.value} / {confirmed.acquisition_method.value}",
            )
        else:
            source = fetch_open_meteo_solar("Trujillo, Peru", selected_date)
            location = EnvironmentalLocation(
                name="Trujillo, Peru",
                latitude=-8.1116,
                longitude=-79.0287,
                timezone=source["timezone"],
            )
        local_key = f"{selected_date}T{selected_time}"
        hourly = source["hourly"]
        timestamps = hourly.get("time", [])
        if local_key not in timestamps:
            _error({"code": "SOURCE_TIME_UNAVAILABLE", "message": local_key}, example_id)
        index = timestamps.index(local_key)
        source_values = {name: (hourly.get(name) or [None] * len(timestamps))[index] for name in source["source_variables"]}
        if any(value is None for value in source_values.values()):
            _error({"code": "ANALYSIS_INCOMPLETE", "message": "Open-Meteo lacks a required hourly solar variable"}, example_id)
        analyses = [
            build_solar_analysis(
                example_id=example_id,
                alternative_id=alternative_id,
                selected_date=selected_date,
                selected_time=selected_time,
                location=location,
                source_values=source_values,
                source=source["source"],
                source_model=source["source_model"],
                source_retrieved_at=source["captured_at"],
                source_variables=tuple(source["source_variables"]),
            ).to_dict()
            for alternative_id in ("UPAO-001-A", "UPAO-001-B", "UPAO-001-C")
        ]
    except EnvironmentalAnalysisError as exc:
        _error({"code": exc.code, "message": str(exc)}, example_id)
    except Exception as exc:
        _error({"code": "WEATHER_SOURCE_UNAVAILABLE", "message": str(exc)}, example_id)
    return _ok({
        "example_id": example_id,
        "analysis_type": "SOLAR",
        "temporal_mode": "INSTANT",
        "selected_date": selected_date,
        "selected_time": selected_time,
        "location": asdict(location),
        "analyses": analyses,
        "source_data_disclaimer": "Open-Meteo weather/radiation source data; not building simulation.",
        "educational_disclaimer": "UPAO-001 remains synthetic LOCAL_ENU geometry and is not a surveyed UPAO site.",
        "read_only": True,
        "recommendation_created": False,
        "human_review_created": False,
        "decision_created": False,
    }, example_id)


@router.get("/examples/{example_id}/capabilities/{capability_id}", dependencies=[Depends(_auth)])
def get_example_capability(
    example_id: str,
    capability_id: str,
    spatial_scope: str = Query(...),
    typology: str | None = Query(default=None),
    stage: str | None = Query(default=None),
    available_data: list[str] | None = Query(default=None),
    objectives: list[str] | None = Query(default=None),
    context: str | None = Query(default=None),
    repo: SQLiteRepository = Depends(get_repository),
) -> V1Envelope:
    try:
        project = repo.get_project(example_id)
        confirmed = _confirmed_location(project)
        data = None
        if project is not None:
            data = {"location", "environmental_data"} if confirmed is not None else set()
        result = resolve_example_capability(
            example_id,
            capability_id,
            spatial_scope,
            typology=typology,
            stage=stage,
            available_data=(available_data if available_data is not None else data),
            objectives=objectives,
            context=context,
        )
    except ValueError as exc:
        message = str(exc)
        code = message.split(":", 1)[0]
        _error({"code": code, "message": message}, example_id)
    return _ok(result.to_dict(), example_id)


@router.get("/multiscale/generative-capabilities", dependencies=[Depends(_auth)])
def get_multiscale_generative_capabilities(spatial_scope: str | None = Query(default=None), typology: str | None = None, stage: str | None = None, data: str | None = None) -> V1Envelope:
    try:
        if spatial_scope:
            result = resolve_generative_capabilities(spatial_scope, typology, stage, [item for item in (data or "").split(",") if item])
        else:
            result = {"scopes": capability_matrix(), "exact_scope_count": 11, "truthful": True}
        return _ok(result)
    except ValueError as exc:
        _error({"code": str(exc), "message": str(exc)})


@router.post("/projects/{project_id}/multiscale/context", dependencies=[Depends(_auth)])
def create_multiscale_context(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload
    try:
        result = cross_scale_context(payload["source_scope"], payload["source_alternative_id"], payload["target_scope"], payload.get("target_alternative_id"))
    except (KeyError, ValueError) as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "CROSS_SCALE_CONTEXT_LINKED", result, request.actor, "multiscale-p7"))
    return _ok(result, project_id)


@router.post("/projects/{project_id}/gdi/multi-agent-exploration", dependencies=[Depends(_auth)])
def gdi_multi_agent_exploration(project_id: str, request: CanonicalWriteRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    payload = request.payload
    alternative = payload.get("alternative") or payload.get("parent")
    if not isinstance(alternative, dict):
        _error({"code": "ALTERNATIVE_REQUIRED", "message": "A canonical alternative is required"}, project_id)
    try:
        alternative = normalize_design_candidate(alternative, project_id)
        result = multi_agent_exploration(alternative, str(payload.get("spatial_scope", "edificacion")), payload.get("active_agents"), payload.get("intent"))
    except (KeyError, ValueError, TypeError) as exc:
        _error({"code": str(exc), "message": str(exc)}, project_id)
    repo.add_event(Event(None, datetime.now(timezone.utc).isoformat(), project_id, "MULTI_AGENT_EXPLORATION_REQUESTED", {"alternative_id": alternative.get("alternative_id"), "spatial_scope": payload.get("spatial_scope", "edificacion"), "agents": payload.get("active_agents"), "result": result, "decision_created": False}, request.actor, "gdi-p8"))
    return _ok(result, project_id)
