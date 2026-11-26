"""CP-02 service-authenticated endpoints for Copilot session persistence.

Actor IDs are caller-declared at this stage. Until Core has user-level identity
binding, this API must remain behind a trusted server boundary and must not be
exposed directly to browsers or unauthenticated clients.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_repository, get_copilot_session_repository
from sicl.repository import SQLiteRepository
from sicl.copilot_session_repository import CopilotSessionRepository

router = APIRouter(prefix="/v1/copilot", tags=["copilot-session-v1"])


def _copilot_service_auth(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("SICL_CORE_SERVICE_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail={"code": "COPILOT_AUTH_NOT_CONFIGURED"})
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail={"code": "INVALID_SERVICE_TOKEN"})


class SessionCreate(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()), min_length=1, max_length=160)
    project_id: str = Field(min_length=1, max_length=160)
    actor_id: str = Field(min_length=1, max_length=160)
    channel: str = Field(default="OTHER", max_length=10)
    title: str = Field(default="", max_length=240)


class MessageCreate(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()), min_length=1, max_length=160)
    role: str = Field(min_length=1, max_length=20)
    content: str = Field(default="", max_length=64000)
    attachments: list[str] = Field(default_factory=list, max_length=20)
    metadata: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=1, max_length=200)


def _project_exists(repo: SQLiteRepository, project_id: str) -> bool:
    return repo.get_project(project_id) is not None


@router.post("/sessions", status_code=201, dependencies=[Depends(_copilot_service_auth)])
def create_session(body: SessionCreate, project_repo: SQLiteRepository = Depends(get_repository),
                   sessions: CopilotSessionRepository = Depends(get_copilot_session_repository)):
    if not _project_exists(project_repo, body.project_id):
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"})
    try:
        return sessions.create_session(session_id=body.session_id, project_id=body.project_id,
                                     actor_id=body.actor_id, channel=body.channel, title=body.title)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail={"code": "COPILOT_SESSION_CONFLICT"}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_SESSION", "message": str(exc)}) from exc


@router.get("/sessions", dependencies=[Depends(_copilot_service_auth)])
def list_sessions(project_id: str, actor_id: str, limit: int = 50,
                   sessions: CopilotSessionRepository = Depends(get_copilot_session_repository)):
    try:
        return {"sessions": sessions.list_sessions(project_id=project_id, actor_id=actor_id, limit=limit)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_LIMIT", "message": str(exc)}) from exc


@router.get("/sessions/{session_id}/messages", dependencies=[Depends(_copilot_service_auth)])
def read_messages(session_id: str, actor_id: str, after_sequence: int = 0, limit: int = 100,
                 sessions: CopilotSessionRepository = Depends(get_copilot_session_repository)):
    session = sessions.get_session(session_id)
    if session is None or session["actor_id"] != actor_id:
        raise HTTPException(status_code=404, detail={"code": "COPILOT_SESSION_NOT_FOUND"})
    try:
        messages = sessions.list_messages(session_id=session_id, after_sequence=after_sequence, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_CURSOR_OR_LIMIT"}) from exc
    return {"session": session, "messages": messages, "next_sequence": messages[-1]["sequence"] if messages else after_sequence}


@router.post("/sessions/{session_id}/messages", status_code=201, dependencies=[Depends(_copilot_service_auth)])
def append_message(session_id: str, body: MessageCreate, actor_id: str,
                  sessions: CopilotSessionRepository = Depends(get_copilot_session_repository)):
    session = sessions.get_session(session_id)
    if session is None or session["actor_id"] != actor_id:
        raise HTTPException(status_code=404, detail={"code": "COPILOT_SESSION_NOT_FOUND"})
    try:
        result = sessions.append_message(message_id=body.message_id, session_id=session_id, role=body.role,
                                        content=body.content, attachments=body.attachments,
                                        metadata=body.metadata, idempotency_key=body.idempotency_key)
        if result.get("code") == "DUPLICATE":
            return result
        return result
    except KeyError as exc:
        raise HTTPException(status_code=404, detail={"code": str(exc)}) from exc
    except ValueError as exc:
        code = str(exc)
        status = 409 if "CONFLICT" in code or "CLOSED" in code else 422
        raise HTTPException(status_code=status, detail={"code": code}) from exc
