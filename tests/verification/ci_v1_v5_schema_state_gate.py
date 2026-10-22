"""
[6.11.4] SCHEMA CHANGES — V-1..V-5 runtime verification gate.

Purpose
-------
Verify the SQLiteRepository schema-state contract for five distinct states:
V-1 LEGACY, V-2 NEW, V-3 MIGRATED, V-4 PARTIAL, V-5 UNSUPPORTED.
This is a focused verification script. It does not replace the full suite.
"""
from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import traceback
from contextlib import closing

try:
    from sicl.repository import SQLiteRepository
except ImportError as exc:  # pragma: no cover
    print(f"FATAL: cannot import SQLiteRepository: {exc}")
    sys.exit(2)


def _mk_tmp_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    return path


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def _column_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    return any(row[1] == col for row in conn.execute(f"PRAGMA table_info({table})"))


def _snapshot(conn: sqlite3.Connection) -> dict:
    return {
        "user_version": conn.execute("PRAGMA user_version").fetchone()[0],
        "has_ledger": _table_exists(conn, "developer_promotion_idempotency"),
        "has_based_on_version": (
            _table_exists(conn, "d2_snapshots")
            and _column_exists(conn, "d2_snapshots", "based_on_version")
        ),
        "has_events": _table_exists(conn, "events"),
        "has_d2_snapshots": _table_exists(conn, "d2_snapshots"),
    }


def _print_case(case: str, initial: dict, final: dict, notes: list[str]) -> None:
    print(f"── {case} ──")
    print(f"  initial: {initial}")
    print(f"  final:   {final}")
    for note in notes:
        print(f"  {note}")


def _build_legacy(path: str) -> None:
    """Build a minimal legacy schema with user_version=0."""
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project_id TEXT NOT NULL,
                type TEXT NOT NULL,
                payload TEXT NOT NULL,
                actor TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'USER_COMMAND'
            );
            CREATE TABLE d2_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            PRAGMA user_version = 0;
        """)
        conn.commit()


def _run_case(
    name: str,
    builder,
    expected_initial: dict | None,
    expected_error: str | None,
    expected_final: dict | None,
) -> bool:
    path = _mk_tmp_db()
    try:
        builder(path)
        with closing(sqlite3.connect(path)) as conn:
            initial = _snapshot(conn)
        if expected_initial is not None and initial != expected_initial:
            _print_case(name, initial, initial, ["FAIL: unexpected initial schema"])
            return False

        caught: Exception | None = None
        repo = None
        try:
            repo = SQLiteRepository(path)
        except Exception as exc:
            caught = exc
        finally:
            if repo is not None:
                repo.close()

        with closing(sqlite3.connect(path)) as conn:
            final = _snapshot(conn)

        if expected_error is None:
            ok = caught is None and (expected_final is None or final == expected_final)
        else:
            ok = caught is not None and expected_error in str(caught) and final == initial
        _print_case(
            name,
            initial,
            final,
            [
                f"exception={type(caught).__name__ if caught else None}",
                f"message={str(caught) if caught else None}",
                f"PASS={ok}",
            ],
        )
        return ok
    finally:
        os.remove(path)


def _legacy(path: str) -> None:
    _build_legacy(path)


def _new(path: str) -> None:
    # Empty file, no tables, user_version=0.
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA user_version = 0")
        conn.commit()


def _migrated(path: str) -> None:
    # Seed the exact migrated shape before opening it through the repository.
    # This prevents V-3 from accidentally testing only the NEW/bootstrap path.
    _build_legacy(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("ALTER TABLE d2_snapshots ADD COLUMN based_on_version INTEGER NULL")
        conn.execute("""
            CREATE TABLE developer_promotion_idempotency (
                project_id TEXT NOT NULL,
                proposal_id TEXT NOT NULL,
                proposal_fingerprint TEXT NOT NULL,
                human_review_id TEXT NOT NULL,
                snapshot_id TEXT NOT NULL REFERENCES d2_snapshots(snapshot_id),
                d2_version INTEGER NOT NULL,
                committed_at TEXT NOT NULL,
                PRIMARY KEY (project_id, proposal_id, proposal_fingerprint, human_review_id)
            )
        """)
        conn.execute("PRAGMA user_version = 1")
        conn.commit()


def _partial(path: str) -> None:
    _build_legacy(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("ALTER TABLE d2_snapshots ADD COLUMN based_on_version INTEGER NULL")
        conn.commit()


def _unsupported(path: str) -> None:
    _build_legacy(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA user_version = 2")
        conn.commit()


def main() -> int:
    results = {}
    results["V-1 LEGACY"] = _run_case(
        "V-1 LEGACY",
        _legacy,
        {
            "user_version": 0,
            "has_ledger": False,
            "has_based_on_version": False,
            "has_events": True,
            "has_d2_snapshots": True,
        },
        None,
        {
            "user_version": 1,
            "has_ledger": True,
            "has_based_on_version": True,
            "has_events": True,
            "has_d2_snapshots": True,
        },
    )
    results["V-2 NEW"] = _run_case(
        "V-2 NEW",
        _new,
        {
            "user_version": 0,
            "has_ledger": False,
            "has_based_on_version": False,
            "has_events": False,
            "has_d2_snapshots": False,
        },
        None,
        None,
    )
    results["V-3 MIGRATED"] = _run_case(
        "V-3 MIGRATED",
        _migrated,
        {
            "user_version": 1,
            "has_ledger": True,
            "has_based_on_version": True,
            "has_events": True,
            "has_d2_snapshots": True,
        },
        None,
        {
            "user_version": 1,
            "has_ledger": True,
            "has_based_on_version": True,
            "has_events": True,
            "has_d2_snapshots": True,
        },
    )
    results["V-4 PARTIAL"] = _run_case(
        "V-4 PARTIAL",
        _partial,
        {
            "user_version": 0,
            "has_ledger": False,
            "has_based_on_version": True,
            "has_events": True,
            "has_d2_snapshots": True,
        },
        "core schema state not supported: PARTIAL",
        None,
    )
    results["V-5 UNSUPPORTED"] = _run_case(
        "V-5 UNSUPPORTED",
        _unsupported,
        {
            "user_version": 2,
            "has_ledger": False,
            "has_based_on_version": False,
            "has_events": True,
            "has_d2_snapshots": True,
        },
        "core schema state not supported: UNSUPPORTED",
        None,
    )

    print("\n── SUMMARY ──")
    for name, passed in results.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
