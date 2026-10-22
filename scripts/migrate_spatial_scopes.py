#!/usr/bin/env python3
"""Migrate legacy SpatialScope values to RFC-019 canonical values.

The migration is deliberately explicit and append-only at the event level:
project rows are updated only after a backup is created, and a migration event
is inserted when an events table is available. Use --dry-run first.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

MAPPING = {
    "edificio": "edificacion",
    "ciudad_distrito": "distrito_ciudad",
    "barrio_sector": "zona_barrio_sector",
}


def migrate(path: Path, dry_run: bool) -> int:
    if not path.exists():
        raise FileNotFoundError(path)
    backup = path.with_suffix(path.suffix + ".pre-rfc019.bak")
    if not dry_run:
        shutil.copy2(path, backup)
    conn = sqlite3.connect(path)
    try:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(projects)")}
        if "spatial_scope" not in columns:
            print("No spatial_scope column; nothing to migrate")
            return 0
        rows = conn.execute(
            "SELECT project_id, spatial_scope FROM projects "
            "WHERE spatial_scope IN (?, ?, ?)", tuple(MAPPING)
        ).fetchall()
        for project_id, old in rows:
            new = MAPPING[old]
            print(f"{project_id}: {old} -> {new}")
            if dry_run:
                continue
            conn.execute(
                "UPDATE projects SET spatial_scope=?, version=version+1 WHERE project_id=?",
                (new, project_id),
            )
            if "events" in {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}: 
                payload = (
                    '{"migration":"RFC-019","old_spatial_scope":"%s",'
                    '"new_spatial_scope":"%s"}' % (old, new)
                )
                conn.execute(
                    "INSERT INTO events(timestamp, project_id, type, payload, actor, source) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (datetime.now(timezone.utc).isoformat(), project_id, "SCOPE_MIGRATED", payload, "migration-rfc019", "MIGRATION"),
                )
        if not dry_run:
            conn.commit()
            print(f"Backup: {backup}")
        print(f"Rows affected: {len(rows)}")
        return len(rows)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    migrate(args.database, args.dry_run)


if __name__ == "__main__":
    main()
