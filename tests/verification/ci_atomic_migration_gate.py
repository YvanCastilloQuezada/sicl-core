"""
[6.11.5] ATOMIC MIGRATION — M-1..M-12 runtime verification gate.
"""
from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
from contextlib import closing

from sicl.repository import SQLiteRepository


def _tmp() -> str:
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    return path


def _table(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def _column(conn: sqlite3.Connection, table: str, name: str) -> bool:
    return any(row[1] == name for row in conn.execute(f"PRAGMA table_info({table})"))


def _state(path: str) -> dict:
    with closing(sqlite3.connect(path)) as conn:
        return {
            "uv": conn.execute("PRAGMA user_version").fetchone()[0],
            "ledger": _table(conn, "developer_promotion_idempotency"),
            "based_on": _column(conn, "d2_snapshots", "based_on_version"),
            "snapshots": conn.execute("SELECT COUNT(*) FROM d2_snapshots").fetchone()[0],
        }


def _legacy(path: str) -> None:
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript("""
        CREATE TABLE projects (
          project_id TEXT PRIMARY KEY, name TEXT NOT NULL,
          stage TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
          project_id TEXT NOT NULL, type TEXT NOT NULL, payload TEXT NOT NULL,
          actor TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'USER_COMMAND'
        );
        CREATE TABLE d2_snapshots (
          snapshot_id TEXT PRIMARY KEY,
          project_id TEXT NOT NULL REFERENCES projects(project_id),
          version INTEGER NOT NULL,
          elements_json TEXT NOT NULL,
          content_hash TEXT NOT NULL,
          actor TEXT NOT NULL,
          source_event_id INTEGER REFERENCES events(id),
          created_at TEXT NOT NULL,
          UNIQUE(project_id, version)
        );
        CREATE INDEX idx_d2_snapshots_project_version
        ON d2_snapshots(project_id, version DESC);
        CREATE TRIGGER d2_snapshots_no_update BEFORE UPDATE ON d2_snapshots
        BEGIN SELECT RAISE(ABORT, 'D-2 snapshots are append-only'); END;
        CREATE TRIGGER d2_snapshots_no_delete BEFORE DELETE ON d2_snapshots
        BEGIN SELECT RAISE(ABORT, 'D-2 snapshots are append-only'); END;
        INSERT INTO projects VALUES ('p1','P1','test',1);
        INSERT INTO d2_snapshots VALUES ('s1','p1',1,'[]','hash-1','tester',NULL,'2026-09-29T00:00:00');
        PRAGMA user_version = 0;
        """)
        conn.commit()


def _partial(path: str) -> None:
    _legacy(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("ALTER TABLE d2_snapshots ADD COLUMN based_on_version INTEGER NULL")
        conn.commit()


def _unsupported(path: str) -> None:
    _legacy(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA user_version = 2")
        conn.commit()


def _legacy_row(path: str) -> tuple:
    with closing(sqlite3.connect(path)) as conn:
        return tuple(conn.execute(
            "SELECT snapshot_id,project_id,version,elements_json,content_hash,actor,source_event_id,created_at "
            "FROM d2_snapshots WHERE snapshot_id='s1'"
        ).fetchone())


def _run_failure(inject: str) -> bool:
    path = _tmp()
    _legacy(path)
    before = _state(path)
    original_ledger = SQLiteRepository._ddl_create_developer_promotion_idempotency
    original_assert = SQLiteRepository._assert_migrated_v1
    try:
        if inject == "after_column":
            def fail_ledger(conn):
                raise RuntimeError("INJECT_AFTER_COLUMN")
            SQLiteRepository._ddl_create_developer_promotion_idempotency = staticmethod(fail_ledger)
        elif inject == "after_ledger":
            def ledger_then_fail(conn):
                original_ledger(conn)
                raise RuntimeError("INJECT_AFTER_LEDGER")
            SQLiteRepository._ddl_create_developer_promotion_idempotency = staticmethod(ledger_then_fail)
        elif inject == "after_user_version":
            def fail_validate(cls, conn):
                raise RuntimeError("INJECT_AFTER_USER_VERSION")
            SQLiteRepository._assert_migrated_v1 = classmethod(fail_validate)
        try:
            SQLiteRepository(path)
            return False
        except RuntimeError:
            pass
        return _state(path) == before
    finally:
        SQLiteRepository._ddl_create_developer_promotion_idempotency = staticmethod(original_ledger)
        SQLiteRepository._assert_migrated_v1 = original_assert
        os.remove(path)


def main() -> int:
    results: dict[str, bool] = {}

    path = _tmp()
    try:
        _legacy(path)
        row_before = _legacy_row(path)
        repo = SQLiteRepository(path)
        fk = repo.conn.execute("PRAGMA foreign_keys").fetchone()[0]
        repo.close()
        st = _state(path)
        row_after = _legacy_row(path)
        with closing(sqlite3.connect(path)) as conn:
            based = conn.execute("SELECT based_on_version FROM d2_snapshots WHERE snapshot_id='s1'").fetchone()[0]
            ledger_count = conn.execute("SELECT COUNT(*) FROM developer_promotion_idempotency").fetchone()[0]
        results["M-1"] = st["uv"] == 1 and st["ledger"] and st["based_on"]
        results["M-2"] = row_before == row_after
        results["M-3"] = based is None
        results["M-4"] = ledger_count == 0
        results["M-5"] = st["uv"] == 1
        results["M-12"] = fk == 1

        repo = SQLiteRepository(path)
        repo.close()
        results["M-9"] = _state(path) == st
    finally:
        os.remove(path)

    results["M-6"] = _run_failure("after_column")
    results["M-7"] = _run_failure("after_ledger")
    results["M-8"] = _run_failure("after_user_version")

    path = _tmp()
    try:
        _partial(path)
        before = _state(path)
        try:
            SQLiteRepository(path)
            results["M-10"] = False
        except RuntimeError:
            results["M-10"] = _state(path) == before
    finally:
        os.remove(path)

    path = _tmp()
    try:
        _unsupported(path)
        before = _state(path)
        try:
            SQLiteRepository(path)
            results["M-11"] = False
        except RuntimeError:
            results["M-11"] = _state(path) == before
    finally:
        os.remove(path)

    print("── [6.11.5] ATOMIC MIGRATION SUMMARY ──")
    for name in [f"M-{i}" for i in range(1, 13)]:
        print(f"  {name}: {'PASS' if results.get(name) else 'FAIL'}")
    return 0 if all(results.get(f"M-{i}", False) for i in range(1, 13)) else 1


if __name__ == "__main__":
    sys.exit(main())
