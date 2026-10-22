"""Append-only JSONL persistence for A-002 sufficiency results."""
from __future__ import annotations
from pathlib import Path
import json
from typing import Any
from .model import SufficiencyResult


class SufficiencyStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._closed = False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def append(self, result: SufficiencyResult) -> None:
        if self._closed:
            raise RuntimeError("A-002 store is closed")
        payload = result.to_dict()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()

    def list_results(self, project_id: str | None = None) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if project_id is None or row.get("projectId") == project_id:
                rows.append(row)
        return rows

    def close(self) -> None:
        self._closed = True

    @classmethod
    def reopen(cls, path: str | Path) -> "SufficiencyStateStore":
        return cls(path)

    def __enter__(self) -> "SufficiencyStateStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
