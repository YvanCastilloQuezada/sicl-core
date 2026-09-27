"""Sandbox Ledger — LAB-001: trazabilidad absoluta."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class SandboxEventType(str, Enum):
    GENERATION_REQUESTED = "GENERATION_REQUESTED"
    ALTERNATIVE_GENERATED = "ALTERNATIVE_GENERATED"
    CORPUS_VALIDATED = "CORPUS_VALIDATED"
    CORPUS_INSUFFICIENT = "CORPUS_INSUFFICIENT"
    COMPLIANCE_CHECKED = "COMPLIANCE_CHECKED"
    PROMOTED_TO_CANONICAL = "PROMOTED_TO_CANONICAL"


@dataclass(frozen=True)
class SandboxEvent:
    event_type: SandboxEventType
    timestamp: str
    project_id: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: hashlib.sha256(f"{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16])

    def to_dict(self) -> dict[str, Any]:
        return {"eventId": self.event_id, "eventType": self.event_type.value, "timestamp": self.timestamp, "projectId": self.project_id, "payload": self.payload}


class SandboxLedger:
    """Ledger del Laboratorio. Los eventos se agregan y se persisten."""

    def __init__(self, storage_path: Path | None = None):
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent.parent / "data" / "sandbox_ledger.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._events: list[SandboxEvent] = []
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            raw = self.storage_path.read_text(encoding="utf-8").strip()
            data = json.loads(raw) if raw else []
            self._events = [SandboxEvent(event_type=SandboxEventType(item["eventType"]), timestamp=item["timestamp"], project_id=item["projectId"], payload=item["payload"], event_id=item["eventId"]) for item in data]

    def record(self, event: SandboxEvent) -> None:
        self._events.append(event)
        self.storage_path.write_text(json.dumps([item.to_dict() for item in self._events], indent=2), encoding="utf-8")

    def list_events(self, project_id: str | None = None) -> list[SandboxEvent]:
        return list(self._events) if project_id is None else [event for event in self._events if event.project_id == project_id]

    def why(self, alternative_id: str) -> list[SandboxEvent]:
        return [event for event in self._events if event.payload.get("alternativeId") == alternative_id]


__all__ = ["SandboxLedger", "SandboxEvent", "SandboxEventType"]
