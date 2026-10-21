"""
[6.11.6] ledger_binding_guard correctness + >100,000 snapshot benchmark.

This is an isolated reproducible SQLite benchmark. It does not modify
promotion concurrency or write the idempotency ledger.
"""
from __future__ import annotations

import platform
import sqlite3
import statistics
import sys
import time

from sicl.repository import SQLiteRepository

SNAPSHOT_COUNT = 100_001
LOOKUPS_PER_POSITION = 2_000
MAX_POSITION_MEDIAN_RATIO = 3.0


def percentile(values: list[int], p: float) -> int:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * p))))
    return ordered[index]


def stats_ns(values: list[int]) -> dict[str, float]:
    return {
        "median_us": statistics.median(values) / 1_000,
        "max_us": max(values) / 1_000,
        "p95_us": percentile(values, 0.95) / 1_000,
        "p99_us": percentile(values, 0.99) / 1_000,
    }


def main() -> int:
    repo = SQLiteRepository(":memory:")
    try:
        repo.conn.execute(
            "INSERT INTO projects(project_id,name,stage,version,temporal_scope) "
            "VALUES ('bench-project','Benchmark','test',1,'proyecto')"
        )
        repo.conn.commit()

        insert_ns: list[int] = []
        repo.conn.execute("BEGIN")
        for version in range(1, SNAPSHOT_COUNT + 1):
            started = time.perf_counter_ns()
            repo.conn.execute(
                """INSERT INTO d2_snapshots(
                    snapshot_id,project_id,version,elements_json,content_hash,
                    actor,source_event_id,created_at,based_on_version
                ) VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    f"s-{version}", "bench-project", version, "[]",
                    f"h-{version}", "BENCH", None,
                    "2026-09-29T00:00:00", None,
                ),
            )
            insert_ns.append(time.perf_counter_ns() - started)
        repo.conn.commit()

        correctness: dict[str, bool] = {}
        repo.ledger_binding_guard("bench-project", "s-1", 1)
        correctness["exact_binding"] = True

        for name, args, expected in (
            ("missing_snapshot", ("bench-project", "missing", 1), "LEDGER_BINDING_SNAPSHOT_NOT_FOUND"),
            ("project_mismatch", ("wrong-project", "s-1", 1), "LEDGER_BINDING_PROJECT_MISMATCH"),
            ("version_mismatch", ("bench-project", "s-1", 2), "LEDGER_BINDING_VERSION_MISMATCH"),
        ):
            try:
                repo.ledger_binding_guard(*args)
                correctness[name] = False
            except RuntimeError as exc:
                correctness[name] = str(exc) == expected

        positions = {
            "early": ("s-1", 1),
            "middle": (f"s-{SNAPSHOT_COUNT // 2}", SNAPSHOT_COUNT // 2),
            "late": (f"s-{SNAPSHOT_COUNT}", SNAPSHOT_COUNT),
        }
        lookup_stats: dict[str, dict[str, float]] = {}
        for label, (snapshot_id, version) in positions.items():
            samples: list[int] = []
            for _ in range(LOOKUPS_PER_POSITION):
                started = time.perf_counter_ns()
                repo.ledger_binding_guard("bench-project", snapshot_id, version)
                samples.append(time.perf_counter_ns() - started)
            lookup_stats[label] = stats_ns(samples)

        medians = [item["median_us"] for item in lookup_stats.values()]
        ratio = max(medians) / min(medians) if min(medians) else float("inf")
        count = repo.conn.execute("SELECT COUNT(*) FROM d2_snapshots").fetchone()[0]

        print("── [6.11.6] LEDGER BINDING GUARD BENCHMARK ──")
        print(f"python={platform.python_version()} platform={platform.platform()}")
        print(f"sqlite={sqlite3.sqlite_version}")
        print(f"snapshots={count} lookups_per_position={LOOKUPS_PER_POSITION}")
        print(f"insert_timing={stats_ns(insert_ns)}")
        for label in ("early", "middle", "late"):
            print(f"guard_{label}={lookup_stats[label]}")
        print(f"position_median_ratio={ratio:.3f} limit={MAX_POSITION_MEDIAN_RATIO:.3f}")
        for name, passed in correctness.items():
            print(f"{name}={'PASS' if passed else 'FAIL'}")
        scale_pass = count > 100_000 and ratio <= MAX_POSITION_MEDIAN_RATIO
        print(f"scale_independence={'PASS' if scale_pass else 'FAIL'}")
        return 0 if scale_pass and all(correctness.values()) else 1
    finally:
        repo.close()


if __name__ == "__main__":
    sys.exit(main())
