from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

MAPPING = {
    "edificio": "edificacion",
    "ciudad_distrito": "distrito_ciudad",
    "barrio_sector": "zona_barrio_sector",
}
INVERSE_MAPPING = {new: old for old, new in MAPPING.items()}
ACTOR = "system:migration:019"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(conn: sqlite3.Connection, project_id: str, event_type: str, payload: dict) -> None:
    conn.execute(
        "INSERT INTO events(timestamp, project_id, type, payload, actor, source) VALUES (?, ?, ?, ?, ?, ?)",
        (_now(), project_id, event_type, json.dumps(payload, sort_keys=True), ACTOR, "MIGRATION"),
    )


def migrate(database: str | Path, *, dry_run: bool = False, backup: bool = True) -> dict:
    path = Path(database)
    if not path.exists():
        raise FileNotFoundError(path)
    backup_path = None
    if backup and not dry_run:
        backup_path = path.with_suffix(path.suffix + f".rfc019-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.bak")
        shutil.copy2(path, backup_path)
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute("SELECT project_id, spatial_scope FROM projects WHERE spatial_scope IS NOT NULL").fetchall()
        changes = []
        for project_id, old_scope in rows:
            new_scope = MAPPING.get(old_scope)
            if not new_scope:
                continue
            changes.append({"project_id": project_id, "from_scope": old_scope, "to_scope": new_scope})
            if not dry_run:
                conn.execute("UPDATE projects SET spatial_scope=?, version=version+1 WHERE project_id=?", (new_scope, project_id))
                _event(conn, project_id, "SCOPE_MIGRATED", changes[-1])
        if not dry_run:
            conn.commit()
        return {"database": str(path), "dry_run": dry_run, "backup": str(backup_path) if backup_path else None, "migrated": changes, "count": len(changes)}
    finally:
        conn.close()


def rollback(database: str | Path, *, backup_path: str | Path | None = None) -> dict:
    path = Path(database)
    if backup_path:
        shutil.copy2(backup_path, path)
        return {"database": str(path), "restored_backup": str(backup_path), "rolled_back": True}
    conn = sqlite3.connect(path)
    try:
        events = conn.execute("SELECT project_id, payload FROM events WHERE type='SCOPE_MIGRATED' AND actor=? ORDER BY id DESC", (ACTOR,)).fetchall()
        changes = []
        for project_id, payload_text in events:
            payload = json.loads(payload_text)
            current = conn.execute("SELECT spatial_scope FROM projects WHERE project_id=?", (project_id,)).fetchone()
            if not current or current[0] != payload.get("to_scope"):
                continue
            conn.execute("UPDATE projects SET spatial_scope=?, version=version+1 WHERE project_id=?", (payload["from_scope"], project_id))
            rollback_payload = {"from_scope": payload["to_scope"], "to_scope": payload["from_scope"], "rollback_of": payload}
            _event(conn, project_id, "SCOPE_MIGRATION_ROLLED_BACK", rollback_payload)
            changes.append({"project_id": project_id, **rollback_payload})
        conn.commit()
        return {"database": str(path), "rolled_back": changes, "count": len(changes)}
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply or roll back RFC-019 SpatialScope migration")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("migrate", "rollback"):
        command = sub.add_parser(action)
        command.add_argument("database", type=Path)
        command.add_argument("--dry-run", action="store_true") if action == "migrate" else command.add_argument("--backup", type=Path)
    args = parser.parse_args()
    result = migrate(args.database, dry_run=args.dry_run) if args.action == "migrate" else rollback(args.database, backup_path=args.backup)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
