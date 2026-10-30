from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from api.deps import get_repository
from sicl.repository import SQLiteRepository

router = APIRouter(prefix="/v1/projects/{project_id}/continuity", tags=["continuity-v1"])

MAX_EVENT_BYTES = 256_000
ALLOWED_EVENT_TYPES = {
    "SESSION_OPENED", "SESSION_CLOSED", "DECISION_RECORDED",
    "TASK_STARTED", "TASK_UPDATED", "TASK_BLOCKED", "TASK_COMPLETED",
    "EVIDENCE_ATTACHED", "ROADMAP_CHANGED", "HANDOFF_CREATED",
    "CORRECTION_RECORDED",
}


def _continuity_auth(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("SICL_CORE_SERVICE_TOKEN", "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail={"code": "CONTINUITY_AUTH_NOT_CONFIGURED",
                    "message": "SICL_CORE_SERVICE_TOKEN must be configured"},
        )
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail={"code": "INVALID_SERVICE_TOKEN"})


class ContinuityEventRequest(BaseModel):
    event_id: str = Field(min_length=1, max_length=160)
    event_type: str = Field(min_length=1, max_length=80)
    workstream_id: str = Field(min_length=1, max_length=160)
    occurred_at: str = Field(min_length=1, max_length=64)
    recorded_at: str | None = Field(default=None, max_length=64)
    actor: str = Field(min_length=1, max_length=160)
    authority_ref: str | None = Field(default=None, max_length=500)
    source_system: str = Field(min_length=1, max_length=120)
    source_sha: str | None = Field(default=None, max_length=128)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    payload: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=1, max_length=200)
    correlation_id: str | None = Field(default=None, max_length=160)
    supersedes_event_id: str | None = Field(default=None, max_length=160)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in ALLOWED_EVENT_TYPES:
            raise ValueError("Unsupported continuity event_type")
        return value

    @field_validator("occurred_at")
    @classmethod
    def validate_occurred_at(cls, value: str) -> str:
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("occurred_at must be ISO-8601") from exc
        return value

    def canonical(self) -> dict[str, Any]:
        data = self.model_dump()
        data["recorded_at"] = data["recorded_at"] or data["occurred_at"]
        return data


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))



def _ensure_continuity_key_index(repo: SQLiteRepository) -> None:
    repo.conn.executescript("""
        CREATE TABLE IF NOT EXISTS continuity_event_keys (
          project_id TEXT NOT NULL,
          event_id TEXT NOT NULL,
          idempotency_key TEXT NOT NULL,
          event_sequence INTEGER NOT NULL UNIQUE REFERENCES events(id),
          sha256 TEXT NOT NULL,
          PRIMARY KEY(project_id, event_id),
          UNIQUE(project_id, idempotency_key)
        );
        CREATE TRIGGER IF NOT EXISTS continuity_event_keys_no_update
        BEFORE UPDATE ON continuity_event_keys
        BEGIN SELECT RAISE(ABORT, 'continuity event keys are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS continuity_event_keys_no_delete
        BEFORE DELETE ON continuity_event_keys
        BEGIN SELECT RAISE(ABORT, 'continuity event keys are append-only'); END;
    """)
    repo.conn.commit()

def _project_or_404(repo: SQLiteRepository, project_id: str) -> None:
    if repo.get_project(project_id) is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "project_id": project_id})


@router.post("/events", dependencies=[Depends(_continuity_auth)])
def append_continuity_event(
    project_id: str,
    body: ContinuityEventRequest,
    repo: SQLiteRepository = Depends(get_repository),
) -> dict[str, Any]:
    _project_or_404(repo, project_id)
    event = body.canonical()
    serialized = _canonical_json(event)
    if len(serialized.encode("utf-8")) > MAX_EVENT_BYTES:
        raise HTTPException(status_code=413, detail={"code": "CONTINUITY_EVENT_TOO_LARGE"})
    fingerprint = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    stored_payload = {"continuity": event, "continuity_sha256": fingerprint}

    try:
        _ensure_continuity_key_index(repo)
        repo.conn.execute("BEGIN IMMEDIATE")
        existing = repo.conn.execute(
            """SELECT event_sequence, sha256 FROM continuity_event_keys
               WHERE project_id=? AND (event_id=? OR idempotency_key=?) LIMIT 1""",
            (project_id, event["event_id"], event["idempotency_key"]),
        ).fetchone()
        if existing is not None:
            repo.conn.commit()
            if existing["sha256"] == fingerprint:
                return {
                    "status": "OK", "code": "DUPLICATE",
                    "project_id": project_id, "event_id": event["event_id"],
                    "event_sequence": int(existing["event_sequence"]), "sha256": fingerprint,
                }
            raise HTTPException(
                status_code=409,
                detail={"code": "CONTINUITY_IDEMPOTENCY_CONFLICT",
                        "event_id": event["event_id"],
                        "message": "event_id or idempotency_key already exists with different content"},
            )

        cursor = repo.conn.execute(
            """INSERT INTO events(timestamp, project_id, type, payload, actor, source)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event["recorded_at"], project_id, "CONTINUITY_" + event["event_type"],
             _canonical_json(stored_payload), event["actor"], event["source_system"]),
        )
        sequence = int(cursor.lastrowid)
        repo.conn.execute(
            """INSERT INTO continuity_event_keys(project_id, event_id, idempotency_key, event_sequence, sha256)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, event["event_id"], event["idempotency_key"], sequence, fingerprint),
        )
        repo.conn.commit()
    except HTTPException:
        if repo.conn.in_transaction:
            repo.conn.rollback()
        raise
    except Exception:
        if repo.conn.in_transaction:
            repo.conn.rollback()
        raise

    return {
        "status": "OK", "code": "RECORDED", "project_id": project_id,
        "event_id": event["event_id"], "event_sequence": sequence,
        "sha256": fingerprint,
    }


@router.get("/events", dependencies=[Depends(_continuity_auth)])
def read_continuity_events(
    project_id: str,
    after_id: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    repo: SQLiteRepository = Depends(get_repository),
) -> dict[str, Any]:
    _project_or_404(repo, project_id)
    rows = repo.conn.execute(
        """SELECT id, timestamp, type, payload, actor, source
           FROM events
           WHERE project_id=? AND id>? AND type LIKE 'CONTINUITY_%'
           ORDER BY id LIMIT ?""",
        (project_id, after_id, limit),
    ).fetchall()
    events = []
    for row in rows:
        stored = json.loads(row["payload"])
        continuity = stored.get("continuity") if isinstance(stored, dict) else None
        if not isinstance(continuity, dict):
            continue
        events.append({
            "sequence": int(row["id"]),
            "event": continuity,
            "sha256": stored.get("continuity_sha256"),
        })
    next_cursor = events[-1]["sequence"] if events else after_id
    return {
        "status": "OK", "project_id": project_id, "events": events,
        "after_id": after_id, "next_after_id": next_cursor,
        "has_more": len(events) == limit,
    }


@router.get("/checkpoint", dependencies=[Depends(_continuity_auth)])
def continuity_checkpoint(
    project_id: str,
    repo: SQLiteRepository = Depends(get_repository),
) -> dict[str, Any]:
    _project_or_404(repo, project_id)
    row = repo.conn.execute(
        """SELECT COALESCE(MAX(id), 0) AS last_event_id, COUNT(*) AS event_count
           FROM events WHERE project_id=? AND type LIKE 'CONTINUITY_%'""",
        (project_id,),
    ).fetchone()
    project = repo.get_project(project_id)
    return {
        "status": "OK", "project_id": project_id,
        "project_version": getattr(project, "version", None),
        "last_event_id": int(row["last_event_id"]),
        "event_count": int(row["event_count"]),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recovery": {
            "events_endpoint": f"/v1/projects/{project_id}/continuity/events",
            "next_after_id": int(row["last_event_id"]),
        },
    }
