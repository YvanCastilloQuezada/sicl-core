"""
[6.11.4] SCHEMA CHANGES — V-1..V-5 runtime verification gate.

Purpose
-------
Verify, at runtime, that SQLiteRepository._create_schema()
behaves correctly against five distinct schema states:

    V-1  LEGACY user_version=0
    V-2  NEW
    V-3  MIGRATED user_version=1
    V-4  PARTIAL
    V-5  UNSUPPORTED

This module exercises only the schema-state behavior of
[6.11.4]. It does not implement, test, or anticipate any of
[6.11.5]..[6.11.9].

Exit code is non-zero if any V-* case fails.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import traceback
from contextlib import closing


# ─── import target under test ────────────────────────────────────

try:
    from sicl.repository import SQLiteRepository
except ImportError as exc:  # pragma: no cover
    print(f"FATAL: cannot import SQLiteRepository: {exc}")
    sys.exit(2)


# ─── helpers ─────────────────────────────────────────────────────

def _mk_tmp_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    return path


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master "
        "WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    return any(
        r[1] == col
        for r in conn.execute(f"PRAGMA table_info({table})")
    )


def _user_version(conn: sqlite3.Connection) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def _snapshot(conn: sqlite3.Connection) -> dict:
    return {
        "user_version": _user_version(conn),
        "has_ledger": _table_exists(
            conn, "developer_promotion_idempotency"
        ),
        "has_based_on_version": (
            _table_exists(conn, "d2_snapshots")
            and _column_exists(conn, "d2_snapshots", "based_on_version")
        ),
        "has_events": _table_exists(conn, "events"),
        "has_d2_snapshots": _table_exists(conn, "d2_snapshots"),
    }


def _print_case(case: str, initial: dict, final: dict, notes: list[str]):
    print(f"── {case} ──")
    print(f"  initial: {initial}")
    print(f"  final:   {final}")
    for n in notes:
        print(f"  {n}")


# ─── V-1 LEGACY ──────────────────────────────────────────────────

def _build_legacy(path: str) -> None:
    """Legacy DB: events + d2_snapshots + append-only triggers, uv=0."""
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript(
            """
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
            """
        )
        conn.commit()


def v1_legacy() -> bool:
    path = _mk_tmp_db()
    try:
        _build_legacy(path)
        with closing(sqlite3.connect(path)) as conn:
            initial = _snapshot(conn)

        try:
            SQLiteRepository(path)
        except Exception as exc:
            _print_case(
                "V-1 LEGACY uv=0",
                initial, initial,
                [f"UNEXPECTED EXCEPTION: {exc!r}"],
            )
            return False

        with closing(sqlite3.connect(path)) as conn:
            final = _snapshot(conn)

        ok = (
            initial["user_version"] == 0
            and final["user_version"] == 0
            and not initial["has_ledger"]
            and not final["has_ledger"]
            and not initial["has_based_on_version"]
            and not final["has_based_on_version"]
            and initial["has_events"]
            and final["has_events"]
            and initial["has_d2_snapshots"]
            and final["has_d2_snapshots"]
        )
        _print_case("V-1 LEGACY uv=0", initial, final,
                    [f"PASS={ok}"])
        return ok
    finally:
        os.remove(path)


# ─── V-2 NEW ─────────────────────────────────────────────────────

def v2_new() -> bool:
    path = _mk_tmp_db()
    try:
        # Crear el archivo vacío pero sin esquema.
        # SQLiteRepository debe construirlo.
        try:
            SQLiteRepository(path)
        except Exception as exc:
            _print_case(
                "V-2 NEW",
                {}, {},
                [f"UNEXPECTED EXCEPTION: {exc!r}"],
            )
            return False

        with closing(sqlite3.connect(path)) as conn:
            final = _snapshot(conn)

        ok = (
            final["user_version"] == 1
            and final["has_ledger"]
            and final["has_based_on_version"]
            and final["has_events"]
            and final["has_d2_snapshots"]
        )
        _print_case("V-2 NEW", {}, final, [f"PASS={ok}"])
        return ok
    finally:
        os.remove(path)


# ─── V-3 MIGRATED ────────────────────────────────────────────────

def v3_migrated() -> bool:
    path = _mk_tmp_db()
    try:
        try:
            SQLiteRepository(path)
        except Exception as exc:
            _print_case(
                "V-3 MIGRATED",
                {}, {},
                [f"FIRST OPEN EXCEPTION: {exc!r}"],
            )
            return False

        with closing(sqlite3.connect(path)) as conn:
            before = _snapshot(conn)

        # Segunda apertura: idempotente
        try:
            SQLiteRepository(path)
        except Exception as exc:
            _print_case(
                "V-3 MIGRATED",
                before, before,
                [f"SECOND OPEN EXCEPTION: {exc!r}"],
            )
            return False

        with closing(sqlite3.connect(path)) as conn:
            after = _snapshot(conn)

        ok = before == after and after["user_version"] == 1
        _print_case("V-3 MIGRATED", before, after, [f"PASS={ok}"])
        return ok
    finally:
        os.remove(path)


# ─── V-4 PARTIAL ─────────────────────────────────────────────────

def _build_partial(path: str) -> None:
    """
    PARTIAL: uv=0 pero con developer_promotion_idempotency ya
    presente, o columna based_on_version ya presente sin uv=1.
    Representación elegida: columna based_on_version ya existe
    pero user_version sigue siendo 0.
    """
    _build_legacy(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute(
            "ALTER TABLE d2_snapshots "
            "ADD COLUMN based_on_version INTEGER NULL"
        )
        conn.commit()


def v4_partial() -> bool:
    path = _mk_tmp_db()
    try:
        _build_partial(path)
        with closing(sqlite3.connect(path)) as conn:
            initial = _snapshot(conn)

        caught: Exception | None = None
        try:
            SQLiteRepository(path)
        except Exception as exc:
            caught = exc

        with closing(sqlite3.connect(path)) as conn:
            final = _snapshot(conn)

        ok = (
            caught is not None
            and initial == final
        )
        _print_case(
            "V-4 PARTIAL",
            initial, final,
            [
                f"exception={type(caught).__name__ if caught else None}",
                f"msg={str(caught) if caught else None}",
                f"PASS={ok}",
            ],
        )
        return ok
    finally:
        os.remove(path)


# ─── V-5 UNSUPPORTED ─────────────────────────────────────────────

def _build_unsupported(path: str) -> None:
    _build_legacy(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA user_version = 2")
        conn.commit()


def v5_unsupported() -> bool:
    path = _mk_tmp_db()
    try:
        _build_unsupported(path)
        with closing(sqlite3.connect(path)) as conn:
            initial = _snapshot(conn)

        caught: Exception | None = None
        try:
            SQLiteRepository(path)
        except Exception as exc:
            caught = exc

        with closing(sqlite3.connect(path)) as conn:
            final = _snapshot(conn)

        ok = (
            caught is not None
            and initial == final
        )
        _print_case(
            "V-5 UNSUPPORTED",
            initial, final,
            [
                f"exception={type(caught).__name__ if caught else None}",
                f"msg={str(caught) if caught else None}",
                f"PASS={ok}",
            ],
        )
        return ok
    finally:
        os.remove(path)


# ─── main ────────────────────────────────────────────────────────

def main() -> int:
    results: dict[str, bool] = {}
    for name, fn in [
        ("V-1", v1_legacy),
        ("V-2", v2_new),
        ("V-3", v3_migrated),
        ("V-4", v4_partial),
        ("V-5", v5_unsupported),
    ]:
        try:
            results[name] = bool(fn())
        except Exception:
            print(f"── {name} ──")
            traceback.print_exc()
            results[name] = False

    print()
    print("── SUMMARY ──")
    for k in sorted(results):
        print(f"  {k}: {'PASS' if results[k] else 'FAIL'}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())