from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_repository
from api.schemas import APIResponse, ProjectCreateRequest, ProjectUpdateRequest
from sicl.cli import CLI
from sicl.repository import SICLError, SQLiteRepository

router = APIRouter(prefix="/projects", tags=["projects"])


def _error(result: dict) -> None:
    if result.get("code") != "OK":
        code = result.get("code")
        status = 404 if code == "PROJECT_NOT_FOUND" else 409 if code in {"PROJECT_ALREADY_EXISTS", "INVALID_STATE"} else 400
        raise HTTPException(status_code=status, detail=result)


@router.get("", response_model=APIResponse)
def list_projects(repo: SQLiteRepository = Depends(get_repository)) -> APIResponse:
    return APIResponse(status="OK", code="OK", message="ok", data={"projects": [asdict(project) for project in repo.list_projects()]})


@router.post("", response_model=APIResponse, status_code=201)
def create_project(request: ProjectCreateRequest, repo: SQLiteRepository = Depends(get_repository)) -> APIResponse:
    command = f'/PROJECT CREATE "{request.project_id}" "{request.name}"'
    if request.spatial_scope is not None:
        command += f' {request.spatial_scope} {request.temporal_scope}'
    result = CLI(repo, actor=request.actor).execute(command)
    _error(result)
    return APIResponse(**result)


@router.get("/{project_id}", response_model=APIResponse)
def get_project(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> APIResponse:
    project = repo.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": project_id})
    return APIResponse(status="OK", code="OK", message="ok", data=asdict(project))


@router.put("/{project_id}", response_model=APIResponse)
def update_project(project_id: str, request: ProjectUpdateRequest, repo: SQLiteRepository = Depends(get_repository)) -> APIResponse:
    if repo.get_project(project_id) is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": project_id})
    if request.stage is None:
        return APIResponse(status="OK", code="OK", message="no state change requested", data=asdict(repo.get_project(project_id)))
    interpreter = CLI(repo, actor=request.actor)
    result = interpreter.execute(f'/PROJECT OPEN {project_id}')
    _error(result)
    result = interpreter.execute(f'/STAGE SET {request.stage}')
    _error(result)
    return APIResponse(**result)


@router.delete("/{project_id}", response_model=APIResponse)
def close_project(project_id: str, repo: SQLiteRepository = Depends(get_repository)) -> APIResponse:
    """Logical delete: closes the project; physical deletion is forbidden by the audit model."""
    if repo.get_project(project_id) is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": project_id})
    interpreter = CLI(repo, actor="api")
    result = interpreter.execute(f'/PROJECT OPEN {project_id}')
    _error(result)
    result = interpreter.execute('/STAGE SET CLOSED')
    _error(result)
    return APIResponse(**result)
