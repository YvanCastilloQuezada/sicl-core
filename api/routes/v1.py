from __future__ import annotations

import os
import uuid
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException

from api.deps import get_repository
from api.schemas import (
    CanonicalCommandRequest,
    CanonicalProjectCreateRequest,
    CanonicalWriteRequest,
    ComparisonCreateRequest,
    EvidenceCreateRequest,
    EvaluationCreateRequest,
    MultiobjectiveRequest,
    PlanningInstrumentLinkRequest,
    SimulationCreateRequest,
    V1Envelope,
)
from sicl.cli import CLI
from sicl.domain import Evidence, EvidenceType, KNOWLEDGE_STATES, PlanningInstrumentType, Preference
from sicl.repository import SQLiteRepository
from sicl.site_intelligence import get_site_observation
from sicl.simulation import METHODS, SimulationType, list_methods, simulation_to_dict
from sicl.design_principles import get_principle, list_principles

CONTRACT_VERSION = "1.0"
router = APIRouter(prefix="/v1", tags=["canonical-v1"])


def _auth(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("SICL_CORE_SERVICE_TOKEN", "").strip()
    if not expected:
        return
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Invalid or missing service token")


def _status_for(code: str) -> int:
    if code in {"METHOD_NOT_FOUND", "SIMULATION_NOT_FOUND", "MULTIOBJECTIVE_NOT_FOUND", "OBJECTIVE_NOT_FOUND", "PLANNING_INSTRUMENT_NOT_FOUND"}:
        return 404
    if code == "METHOD_TYPE_MISMATCH":
        return 409
    if code == "INSUFFICIENT_INPUTS":
        return 422
    if code == "PROJECT_NOT_FOUND":
        return 404
    if code in {"PROJECT_ALREADY_EXISTS", "INVALID_STATE", "CONFLICT", "PLANNING_INSTRUMENT_ALREADY_LINKED"}:
        return 409
    if code in {"HUMAN_REVIEW_REQUIRED", "SEMANTIC_REJECTION", "OBJECTIVE_DIRECTION_REQUIRED"}:
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


@router.get("/design/principles", dependencies=[Depends(_auth)])
def design_principles(category: str | None = None) -> dict[str, Any]:
    return {"contract_version": CONTRACT_VERSION, "status": "OK", "code": "OK", "message": "ok", "project_id": None, "observed_version": None, "data": {"principles": list_principles(category)}}


@router.get("/design/principles/{principle_id}", dependencies=[Depends(_auth)])
def design_principle(principle_id: str) -> dict[str, Any]:
    principle = get_principle(principle_id)
    if principle is None:
        raise HTTPException(status_code=404, detail={"contract_version": CONTRACT_VERSION, "status": "ERROR", "code": "PRINCIPLE_NOT_FOUND", "message": principle_id, "project_id": None, "observed_version": None, "data": {}})
    return {"contract_version": CONTRACT_VERSION, "status": "OK", "code": "OK", "message": "ok", "project_id": None, "observed_version": None, "data": {"principle": principle}}


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


@router.get("/projects", dependencies=[Depends(_auth)])
def list_projects(repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    projects = [asdict(project) for project in repo.list_projects()]
    return _ok({"projects": projects})


@router.post("/projects", dependencies=[Depends(_auth)])
def create_project(request: CanonicalProjectCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    cli = CLI(repo, actor=request.actor)
    result = cli.execute(f'/PROJECT CREATE "{request.project_id}" "{request.name}"')
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


@router.get("/projects/{project_id}/evidence/{evidence_id}", dependencies=[Depends(_auth)])
def get_evidence(project_id: str, evidence_id: str, repo: SQLiteRepository = Depends(get_repository)) -> V1Envelope:
    project = repo.get_project(project_id)
    if project is None:
        _error({"code": "PROJECT_NOT_FOUND", "message": project_id}, project_id)
    evidence = repo.get_evidence(project_id, evidence_id)
    if evidence is None:
        _error({"code": "EVIDENCE_NOT_FOUND", "message": evidence_id}, project_id)
    return _ok({"evidence": asdict(evidence)}, project_id, project.version)
