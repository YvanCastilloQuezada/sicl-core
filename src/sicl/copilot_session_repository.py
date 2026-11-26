"""CP-02 isolated persistent store for ARKI Copilot conversations.

This storage is intentionally separate from the SICL continuity ledger and from the
canonical SQLiteRepository schema. Conversation persistence is not project evidence.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class CopilotSessionRepository:
    """Append-only session/message store with bounded payloads and idempotent writes."""

    MAX_MESSAGE_BYTES = 64_000

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS copilot_sessions (
          session_id TEXT PRIMARY KEY,
          project_id TEXT NOT NULL,
          actor_id TEXT NOT NULL,
          channel TEXT NOT NULL CHECK(channel IN ('FIELD','OFFICE','OTHER')),
          title TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','CLOSED'))
        );
        CREATE INDEX IF NOT EXISTS copilot_sessions_project_actor
          ON copilot_sessions(project_id, actor_id, updated_at);
        CREATE TABLE IF NOT EXISTS copilot_messages (
          message_id TEXT PRIMARY PRIMARY KEY,
          session_id TEXT NOT NULL REFERENCES copilot_sessions(session_id),
          sequence INTEGER NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('architect','copilot','system','tool')),
          content TEXT NOT NULL,
          attachments_json TEXT NOT NULL DEFAULT '[]',
          metadata_json TEXT NOT NULL DEFAULT '{}',
          idempotency_key TEXT NOT NULL,
          fingerprint TEXT NOT NULL,
          created_at TEXT NOT NULL,
          UNIQUE(session_id, sequence),
          UNIQUE(session_id, idempotency_key)
        );
        CREATE TRIGGER IF NOT EXISTS copilot_messages_no_update
          BEFORE UPDATE ON copilot_messages
          BEGIN SELECT RAISE(ABORT, 'copilot messages are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS copilot_messages_no_delete
          BEFORE DELETE ON copilot_messages
          BEGIN SELECT RAISE(ABORT, 'copilot messages are append-only'); END;
        """)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def create_session(self, *, session_id: str, project_id: str, actor_id: str,
                      channel: str = "OTHER", title: str = "") -> dict[str, Any]:
        for name, value in (("session_id", session_id), ("project_id", project_id), ("actor_id", actor_id)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must not be empty")
        channel = channel.strip().upper()
        if channel not in {"FIELD", "OFFICE", "OTHER"}:
            raise ValueError("channel must be FIELD, OFFICE, or OTHER")
        if len(title) > 240:
            raise ValueError("title exceeds 240 characters")
        now = _utc_now()
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            self.conn.execute(
                "INSERT INTO copilot_sessions(session_id,project_id,actor_id,channel,title,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (session_id, project_id, actor_id, channel, title, now, now),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM copilot_sessions WHERE session_id=?", (session_id,)).fetchone()
        return dict(row) if row else None

    def list_sessions(self, *, project_id: str, actor_id: str, limit: int = 50) -> list[dict[str, Any]]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        rows = self.conn.execute(
            "SELECT * FROM copilot_sessions WHERE project_id=? AND actor_id=? ORDER BY updated_at DESC LIMIT ?",
            (project_id, actor_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def append_message(self, *, message_id: str, session_id: str, role: str, content: str,
                      attachments: list[str] | tuple[str, ...] = (), metadata: dict[str, Any] | None = None,
                      idempotency_key: str) -> dict[str, Any]:
        if role not in {"architect", "copilot", "system", "tool"}:
            raise ValueError("unsupported message role")
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        attachments = tuple(attachments)
        if not content.strip() and not attachments:
            raise ValueError("message must include content or attachments")
        metadata = metadata or {}
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ValueError("idempotency_key must not be empty")
        payload = {"message_id": message_id, "session_id": session_id, "role": role,
                   "content": content, "attachments": attachments, "metadata": metadata}
        serialized = _canonical(payload)
        if len(serialized.encode("utf-8")) > self.MAX_MESSAGE_BYTES:
            raise ValueError("message exceeds size limit")
        fingerprint = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        created_at = _utc_now()
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            session = self.conn.execute(
                "SELECT status FROM copilot_sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            if session is None:
                raise KeyError("COPILOT_SESSION_NOT_FOUND")
            if session["status"] != "OPEN":
                raise ValueError("COPILOT_SESSION_CLOSED")
            existing = self.conn.execute(
                "SELECT * FROM copilot_messages WHERE session_id=? AND (message_id=? OR idempotency_key=?) LIMIT 1",
                (session_id, message_id, idempotency_key),
            ).fetchone()
            if existing:
                self.conn.commit()
                if existing["fingerprint"] == fingerprint:
                    return {**dict(existing), "attachments": json.loads(existing["attachments_json"]),
                            "metadata": json.loads(existing["metadata_json"]), "code": "DUPLICATE"}
                raise ValueError("COPILOT_IDEMPOTENCY_CONFLICT")
            sequence = int(self.conn.execute(
                "SELECT COALESCE(MAX(sequence),0)+1 AS next FROM copilot_messages WHERE session_id=?",
                (session_id,),
            ).fetchone()["next"])
            self.conn.execute(
                """INSERT INTO copilot_messages(message_id,session_id,sequence,role,content,
                   attachments_json,metadata_json,idempotency_key,fingerprint,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (message_id, session_id, sequence, role, content, _canonical(attachments),
                 _canonical(metadata), idempotency_key, fingerprint, created_at),
            )
            self.conn.execute("UPDATE copilot_sessions SET updated_at=? WHERE session_id=?",
                             (created_at, session_id))
            self.conn.commit()
        except Exception:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise
        return self.get_message(message_id)

    def get_message(self, message_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM copilot_messages WHERE message_id=?", (message_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["attachments"] = json.loads(result.pop("attachments_json"))
        result["metadata"] = json.loads(result.pop("metadata_json"))
        return result

    def list_messages(self, *, session_id: str, after_sequence: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        if after_sequence < 0 or not 1 <= limit <= 200:
            raise ValueError("invalid cursor or limit")
        rows = self.conn.execute(
            "SELECT * FROM copilot_messages WHERE session_id=? AND sequence>? ORDER BY sequence LIMIT ?",
            (session_id, after_sequence, limit),
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["attachments"] = json.loads(item.pop("attachments_json"))
            item["metadata"] = json.loads(item.pop("metadata_json"))
            result.append(item)
        return result

    def close_session(self, session_id: str) -> bool:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            cursor = self.conn.execute(
                "UPDATE copilot_sessions SET status='CLOSED',updated_at=? WHERE session_id=? AND status='OPEN'",
                (_utc_now(), session_id),
            )
            self.conn.commit()
            return cursor.rowcount == 1
        except Exception:
            self.conn.rollback()
            raise
