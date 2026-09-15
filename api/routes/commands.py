from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_repository
from api.schemas import APIResponse, CommandRequest
from sicl.cli import CLI
from sicl.repository import SQLiteRepository

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("", response_model=APIResponse)
def execute_command(request: CommandRequest, repo: SQLiteRepository = Depends(get_repository)) -> APIResponse:
    interpreter = CLI(repo, actor=request.actor)
    command = request.command
    if not command.upper().startswith(("/PROJECT CREATE", "/PROJECT OPEN", "/PROJECT LIST")):
        projects = repo.list_projects()
        if len(projects) == 1:
            opened = interpreter.execute(f"/PROJECT OPEN {projects[0].project_id}")
            if opened.get("code") != "OK":
                raise HTTPException(status_code=409, detail=opened)
    result = interpreter.execute(command)
    if result.get("code") != "OK":
        code = result.get("code")
        status = 404 if code == "PROJECT_NOT_FOUND" else 409 if code in {"PROJECT_ALREADY_EXISTS", "INVALID_STATE"} else 400
        raise HTTPException(status_code=status, detail=result)
    return APIResponse(**result)
