"""[6.11.9] Deterministic promotion concurrency contract tests.

TC-11/12 exercise repository UNIQUE classification directly.
TC-22/23/24 exercise the public retry loop without OS scheduling races.
"""
from __future__ import annotations

import logging
import sqlite3

import pytest

import sicl.developer_promotion as dp
from sicl.derivation import DerivationLedger
from sicl.domain import Event, HumanReview, Project, now_iso
from sicl.repository import SQLiteRepository
from sicl.archi.persistence import elements_content_hash


FP = "a" * 64
PROJECT = "P"
PROPOSAL = "dev-prop-1"
REVIEW = "review-1"


def geometry():
    return {
        "kind": "EXTRUDED_RECTANGLE",
        "profile": {"width_mm": 4000, "depth_mm": 3000, "radius_mm": None},
        "x_mm": 0, "y_mm": 0, "z_mm": 0, "height_mm": 2800,
    }


def proposal():
    return {
        "proposalId": PROPOSAL,
        "parentProposalId": None,
        "sourceExecutionId": "d63-exec",
        "sourceD63": "D63-A",
        "fingerprint": FP,
        "epistemicStatus": "PROPOSAL",
        "proposedElements": [{
            "provisionalId": "space-1",
            "kind": "SPACE",
            "geometry": geometry(),
            "properties": {"name": "Space"},
            "provenance": [{"source": "test", "ref": "D63-A"}],
            "epistemicStatus": "HYPOTHESIS",
        }],
        "proposedRelations": [],
        "proposedDerivations": [],
        "unresolvedUnknowns": [],
        "requiredHumanActions": [{"action": "review", "reason": "required"}],
        "provenance": [{"source": "test", "ref": "proposal"}],
        "reviewRequired": True,
        "mutation": None,
        "rejectedBecause": None,
        "feedbackLoops": [],
    }


def setup_repo(path=None):
    repo = SQLiteRepository(path) if path is not None else SQLiteRepository()
    repo.insert_project(
        Project(PROJECT, "Promotion"),
        Event(None, now_iso(), PROJECT, "PROJECT_CREATED", {}, "test", "TEST"),
    )
    repo.add_event(Event(
        None, now_iso(), PROJECT, "REASONING_EXECUTION_RECORDED",
        {"execution": {
            "execution_id": PROPOSAL,
            "kind": "DEVELOPER_PROPOSAL",
            "fingerprint": FP,
            "payload": proposal(),
        }},
        "developer", "TEST",
    ))
    review = HumanReview(
        REVIEW, PROJECT, "architect", "2026-09-29T12:00:00Z",
        "Approved", "reviewed", "PRODUCT_OWNER", "APPROVED", 1,
        "DEVELOPER_PROPOSAL", PROPOSAL, FP,
    )
    project = repo.get_project(PROJECT)
    project.human_reviews[REVIEW] = review
    project.version += 1
    repo.insert_entity_and_event(
        """INSERT INTO human_reviews(
            review_id, project_id, actor, timestamp, review, reason, authority,
            status, version, referenced_entity_type, referenced_entity_id,
            referenced_fingerprint
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            review.review_id, review.project_id, review.actor, review.timestamp,
            review.review, review.reason, review.authority, review.status,
            review.version, review.referenced_entity_type,
            review.referenced_entity_id, review.referenced_fingerprint,
        ),
        project,
        Event(None, now_iso(), PROJECT, "HUMAN_REVIEW_RECORDED",
              {}, "architect", "TEST"),
    )
    return repo


def run(repo):
    return dp.promote_developer_proposal(
        repo=repo,
        project_id=PROJECT,
        proposal_id=PROPOSAL,
        proposal_fingerprint=FP,
        human_review_id=REVIEW,
        ledger=DerivationLedger(repo),
    )


class _UniqueRaceConnectionProxy:
    """Inject snapshot UNIQUE, then expose chosen authoritative D-2 version."""

    def __init__(self, real, authoritative_version):
        self._real = real
        self._authoritative_version = authoritative_version
        self._inject_unique = True
        self._after_rollback = False

    def execute(self, sql, parameters=()):
        normalized = " ".join(sql.split())

        if (
            self._inject_unique
            and normalized.startswith("INSERT INTO d2_snapshots")
        ):
            self._inject_unique = False
            raise sqlite3.IntegrityError(
                "UNIQUE constraint failed: "
                "d2_snapshots.project_id, d2_snapshots.version"
            )

        if (
            self._after_rollback
            and "SELECT COALESCE(MAX(version), 0) AS version "
                "FROM d2_snapshots WHERE project_id=?" in normalized
        ):
            return _SingleRowCursor({"version": self._authoritative_version})

        return self._real.execute(sql, parameters)

    def rollback(self):
        self._real.rollback()
        self._after_rollback = True

    def commit(self):
        return self._real.commit()

    def __getattr__(self, name):
        return getattr(self._real, name)


class _SingleRowCursor:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


def _candidate_from_first_attempt(repo):
    captured = {}

    def capture(
        project_id, elements, actor, proposal_id, proposal_fingerprint,
        human_review_id, based_on_version,
    ):
        captured.update(
            elements=elements,
            actor=actor,
            based_on_version=based_on_version,
        )
        raise RuntimeError("CAPTURE")

    real = repo.commit_developer_promotion
    repo.commit_developer_promotion = capture
    try:
        out = run(repo)
        assert out.committed is False
        assert out.reason == "PROMOTION_PERSIST_FAILED"
    finally:
        repo.commit_developer_promotion = real

    assert captured, "promotion attempt never reached repository commit"
    return captured


def test_tc11_snapshot_unique_after_authoritative_advance_becomes_stale():
    repo = setup_repo()
    captured = _candidate_from_first_attempt(repo)
    assert captured["based_on_version"] == 0

    repo.conn = _UniqueRaceConnectionProxy(repo.conn, authoritative_version=1)

    with pytest.raises(RuntimeError, match="^STALE_BASE_VERSION$"):
        repo.commit_developer_promotion(
            PROJECT,
            captured["elements"],
            captured["actor"],
            PROPOSAL,
            FP,
            REVIEW,
            0,
        )


def test_tc11b_stale_retry_rereads_revalidates_and_rebuilds(monkeypatch):
    repo = setup_repo()

    real_validate = dp.validate_creation
    real_snapshot_for_creation = dp.snapshot_for_creation
    real_commit = repo.commit_developer_promotion

    observed = {
        "validate_calls": 0,
        "sufficiency_calls": 0,
        "commit_bases": [],
    }

    def tracked_validate(*args, **kwargs):
        observed["validate_calls"] += 1
        return real_validate(*args, **kwargs)

    def tracked_snapshot(*args, **kwargs):
        observed["sufficiency_calls"] += 1
        return real_snapshot_for_creation(*args, **kwargs)

    def stale_then_commit(
        project_id, elements, actor, proposal_id, proposal_fingerprint,
        human_review_id, based_on_version,
    ):
        observed["commit_bases"].append(based_on_version)

        if len(observed["commit_bases"]) == 1:
            # Simulate the legitimate competing winner becoming authoritative
            # before this attempt can commit.
            repo.conn.execute(
                """
                INSERT INTO d2_snapshots(
                    snapshot_id, project_id, version, elements_json,
                    content_hash, actor, source_event_id, created_at,
                    based_on_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "tc11b-competing-snapshot",
                    PROJECT,
                    1,
                    "[]",
                    elements_content_hash("[]"),
                    "competitor",
                    None,
                    "2026-09-30T00:00:00",
                    None,
                ),
            )
            repo.conn.commit()
            raise RuntimeError("STALE_BASE_VERSION")

        return real_commit(
            project_id,
            elements,
            actor,
            proposal_id,
            proposal_fingerprint,
            human_review_id,
            based_on_version,
        )

    monkeypatch.setattr(dp, "validate_creation", tracked_validate)
    monkeypatch.setattr(dp, "snapshot_for_creation", tracked_snapshot)
    monkeypatch.setattr(repo, "commit_developer_promotion", stale_then_commit)
    monkeypatch.setattr(dp, "_promotion_backoff_seconds", lambda attempts: 0.0)

    out = run(repo)

    assert out.committed is True
    assert observed["commit_bases"] == [0, 1]
    assert observed["validate_calls"] == 2
    assert observed["sufficiency_calls"] == 2
    assert out.d2_version == 2


def test_tc12_snapshot_unique_without_advance_is_terminal_integrity():
    repo = setup_repo()
    captured = _candidate_from_first_attempt(repo)
    repo.conn = _UniqueRaceConnectionProxy(repo.conn, authoritative_version=0)

    with pytest.raises(
        RuntimeError,
        match="^PROMOTION_SNAPSHOT_UNIQUE_INTEGRITY_FAILURE$",
    ):
        repo.commit_developer_promotion(
            PROJECT,
            captured["elements"],
            captured["actor"],
            PROPOSAL,
            FP,
            REVIEW,
            0,
        )


def test_tc12b_unknown_unique_message_is_not_misclassified():
    repo = setup_repo()
    captured = _candidate_from_first_attempt(repo)

    class UnknownUniqueConnectionProxy(_UniqueRaceConnectionProxy):
        def execute(self, sql, parameters=()):
            normalized = " ".join(sql.split())

            if (
                self._inject_unique
                and normalized.startswith("INSERT INTO d2_snapshots")
            ):
                self._inject_unique = False
                raise sqlite3.IntegrityError(
                    "UNIQUE constraint failed: "
                    "d2_snapshots.project_id, d2_snapshots.version "
                    "[unexpected variant]"
                )

            return self._real.execute(sql, parameters)

    repo.conn = UnknownUniqueConnectionProxy(
        repo.conn,
        authoritative_version=1,
    )

    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        repo.commit_developer_promotion(
            PROJECT,
            captured["elements"],
            captured["actor"],
            PROPOSAL,
            FP,
            REVIEW,
            0,
        )

    message = str(exc_info.value)
    assert message.endswith("[unexpected variant]")
    assert message != (
        "UNIQUE constraint failed: "
        "d2_snapshots.project_id, d2_snapshots.version"
    )


def test_tc22_integrity_failure_is_not_retried(monkeypatch):
    repo = setup_repo()
    calls = {"n": 0}

    def terminal(*args, **kwargs):
        calls["n"] += 1
        raise RuntimeError("PROMOTION_SNAPSHOT_UNIQUE_INTEGRITY_FAILURE")

    monkeypatch.setattr(repo, "commit_developer_promotion", terminal)

    out = run(repo)

    assert calls["n"] == 1
    assert out.committed is False
    assert out.effects_status == "NOT_ATTEMPTED"
    assert out.reason == "INTEGRITY_FAILURE"


def test_tc23_safety_cap_logs_and_terminates(monkeypatch, caplog):
    repo = setup_repo()
    attempts = {"n": 0}

    monkeypatch.setattr(dp, "SAFETY_MAX_ATTEMPTS", 3)
    monkeypatch.setattr(dp.time, "monotonic", lambda: 1000.0)
    monkeypatch.setattr(dp.time, "sleep", lambda _seconds: None)

    def stale(*args, **kwargs):
        attempts["n"] += 1
        raise RuntimeError("STALE_BASE_VERSION")

    monkeypatch.setattr(repo, "commit_developer_promotion", stale)

    with caplog.at_level(logging.ERROR, logger=dp.__name__):
        out = run(repo)

    assert attempts["n"] == 3
    assert out.committed is False
    assert out.reason == "RETRIABLE_BUSY_EXHAUSTED"
    assert any(
        "SAFETY_MAX_ATTEMPTS triggered" in record.getMessage()
        for record in caplog.records
    )


def test_tc24_busy_and_stale_consume_one_shared_deadline(monkeypatch):
    repo = setup_repo()

    # One shared fake clock. Sleep advances the same clock used by deadline.
    clock = {"now": 100.0}
    sleeps = []
    attempts = {"n": 0}

    monkeypatch.setattr(dp, "PROMOTION_DEADLINE_MS", 1000)
    monkeypatch.setattr(dp, "BACKOFF_BASE_MS", 400)
    monkeypatch.setattr(dp, "BACKOFF_FACTOR", 1)
    monkeypatch.setattr(dp, "BACKOFF_CAP_MS", 400)
    monkeypatch.setattr(dp, "SAFETY_MAX_ATTEMPTS", 100)
    monkeypatch.setattr(dp.time, "monotonic", lambda: clock["now"])

    def sleep(seconds):
        sleeps.append(seconds)
        clock["now"] += seconds

    monkeypatch.setattr(dp.time, "sleep", sleep)

    def busy_then_stale(*args, **kwargs):
        attempts["n"] += 1
        if attempts["n"] == 1:
            exc = sqlite3.OperationalError("database is locked")
            exc.sqlite_errorcode = sqlite3.SQLITE_BUSY
            raise exc
        raise RuntimeError("STALE_BASE_VERSION")

    monkeypatch.setattr(repo, "commit_developer_promotion", busy_then_stale)

    out = run(repo)

    assert out.committed is False
    assert out.reason == "RETRIABLE_BUSY_EXHAUSTED"

    # BUSY consumes 0.4 s, STALE consumes another 0.4 s, and the final
    # backoff is truncated to the SAME remaining 0.2 s budget.
    assert sleeps == pytest.approx([0.4, 0.4, 0.2])
    assert sum(sleeps) == pytest.approx(1.0)
    assert clock["now"] == pytest.approx(101.0)
    assert attempts["n"] == 3


def _insert_d2_lineage_snapshot(
    repo,
    *,
    snapshot_id,
    version,
    based_on_version,
):
    repo.conn.execute(
        """
        INSERT INTO d2_snapshots(
            snapshot_id, project_id, version, elements_json, content_hash,
            actor, source_event_id, created_at, based_on_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            snapshot_id,
            PROJECT,
            version,
            "[]",
            f"hash-{snapshot_id}",
            "tester",
            None,
            "2026-09-30T00:00:00",
            based_on_version,
        ),
    )
    repo.conn.commit()


@pytest.mark.parametrize(
    ("version", "based_on_version"),
    [
        (2, 2),
        (2, 3),
    ],
)
def test_tc14_startup_rejects_based_on_version_not_predecessor(
    tmp_path, version, based_on_version
):
    db = tmp_path / f"tc14-{version}-{based_on_version}.sqlite"
    repo = SQLiteRepository(str(db))
    repo.conn.execute(
        """
        INSERT INTO projects(project_id, name, stage, version)
        VALUES (?, ?, ?, ?)
        """,
        (PROJECT, "P", "test", 1),
    )
    repo.conn.commit()
    _insert_d2_lineage_snapshot(
        repo,
        snapshot_id="tc14-invalid",
        version=version,
        based_on_version=based_on_version,
    )
    repo.close()

    with pytest.raises(
        RuntimeError,
        match="^D2_BASED_ON_VERSION_NOT_PREDECESSOR$",
    ):
        SQLiteRepository(str(db))


def test_tc15_startup_rejects_zero_base_for_version_gt_one(tmp_path):
    db = tmp_path / "tc15.sqlite"
    repo = SQLiteRepository(str(db))
    repo.conn.execute(
        """
        INSERT INTO projects(project_id, name, stage, version)
        VALUES (?, ?, ?, ?)
        """,
        (PROJECT, "P", "test", 1),
    )
    repo.conn.commit()
    _insert_d2_lineage_snapshot(
        repo,
        snapshot_id="tc15-invalid",
        version=2,
        based_on_version=0,
    )
    repo.close()

    with pytest.raises(
        RuntimeError,
        match="^D2_BASED_ON_ZERO_INVALID_FOR_VERSION$",
    ):
        SQLiteRepository(str(db))


def test_tc16_startup_rejects_missing_positive_base_snapshot(tmp_path):
    db = tmp_path / "tc16.sqlite"
    repo = SQLiteRepository(str(db))
    repo.conn.execute(
        """
        INSERT INTO projects(project_id, name, stage, version)
        VALUES (?, ?, ?, ?)
        """,
        (PROJECT, "P", "test", 1),
    )
    repo.conn.commit()
    _insert_d2_lineage_snapshot(
        repo,
        snapshot_id="tc16-invalid",
        version=3,
        based_on_version=1,
    )
    repo.close()

    with pytest.raises(
        RuntimeError,
        match="^D2_BASED_ON_SNAPSHOT_NOT_FOUND$",
    ):
        SQLiteRepository(str(db))


def _tc_schema_seed(path):
    import sqlite3

    conn = sqlite3.connect(path)
    conn.executescript(
        """
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
        INSERT INTO projects VALUES ('p1','P1','test',1);
        INSERT INTO d2_snapshots
        VALUES ('s1','p1',1,'[]','hash-1','tester',NULL,'2026-09-30T00:00:00');
        PRAGMA user_version = 0;
        """
    )
    conn.commit()
    return conn


def test_tc17_user_version_zero_with_existing_ledger_fails_closed(tmp_path):
    db = tmp_path / "tc17.sqlite"
    conn = _tc_schema_seed(str(db))
    conn.execute(
        """
        CREATE TABLE developer_promotion_idempotency (
          project_id TEXT NOT NULL,
          proposal_id TEXT NOT NULL,
          proposal_fingerprint TEXT NOT NULL,
          human_review_id TEXT NOT NULL,
          snapshot_id TEXT NOT NULL REFERENCES d2_snapshots(snapshot_id),
          d2_version INTEGER NOT NULL,
          committed_at TEXT NOT NULL,
          PRIMARY KEY (
            project_id, proposal_id, proposal_fingerprint, human_review_id
          )
        )
        """
    )
    conn.commit()
    conn.close()

    with pytest.raises(
        RuntimeError,
        match="^core schema state not supported: PARTIAL$",
    ):
        SQLiteRepository(str(db))


def test_tc18_user_version_zero_with_existing_based_on_column_fails_closed(tmp_path):
    db = tmp_path / "tc18.sqlite"
    conn = _tc_schema_seed(str(db))
    conn.execute(
        "ALTER TABLE d2_snapshots ADD COLUMN based_on_version INTEGER NULL"
    )
    conn.commit()
    conn.close()

    with pytest.raises(
        RuntimeError,
        match="^core schema state not supported: PARTIAL$",
    ):
        SQLiteRepository(str(db))


def test_tc19_user_version_one_with_missing_ledger_fails_closed(tmp_path):
    db = tmp_path / "tc19.sqlite"
    conn = _tc_schema_seed(str(db))
    conn.execute(
        "ALTER TABLE d2_snapshots ADD COLUMN based_on_version INTEGER NULL"
    )
    conn.execute("PRAGMA user_version = 1")
    conn.commit()
    conn.close()

    with pytest.raises(
        RuntimeError,
        match="^core schema state not supported: PARTIAL$",
    ):
        SQLiteRepository(str(db))


def test_tc20_user_version_one_with_missing_based_on_column_fails_closed(tmp_path):
    db = tmp_path / "tc20.sqlite"
    conn = _tc_schema_seed(str(db))
    conn.execute(
        """
        CREATE TABLE developer_promotion_idempotency (
          project_id TEXT NOT NULL,
          proposal_id TEXT NOT NULL,
          proposal_fingerprint TEXT NOT NULL,
          human_review_id TEXT NOT NULL,
          snapshot_id TEXT NOT NULL REFERENCES d2_snapshots(snapshot_id),
          d2_version INTEGER NOT NULL,
          committed_at TEXT NOT NULL,
          PRIMARY KEY (
            project_id, proposal_id, proposal_fingerprint, human_review_id
          )
        )
        """
    )
    conn.execute("PRAGMA user_version = 1")
    conn.commit()
    conn.close()

    with pytest.raises(
        RuntimeError,
        match="^core schema state not supported: PARTIAL$",
    ):
        SQLiteRepository(str(db))


@pytest.mark.parametrize("user_version", [2, 7, 99])
def test_tc21_unsupported_user_version_fails_closed(tmp_path, user_version):
    db = tmp_path / f"tc21-{user_version}.sqlite"
    conn = _tc_schema_seed(str(db))
    conn.execute(f"PRAGMA user_version = {user_version}")
    conn.commit()
    conn.close()

    with pytest.raises(
        RuntimeError,
        match="^core schema state not supported: UNSUPPORTED$",
    ):
        SQLiteRepository(str(db))


def test_tc08_busy_exhaustion_returns_no_snapshot(monkeypatch):
    repo = setup_repo()

    monkeypatch.setattr(dp, "PROMOTION_DEADLINE_MS", 1)
    monkeypatch.setattr(dp, "BUSY_TIMEOUT_CAP_MS", 1)
    monkeypatch.setattr(dp, "BACKOFF_BASE_MS", 1)
    monkeypatch.setattr(dp, "BACKOFF_FACTOR", 1)
    monkeypatch.setattr(dp, "BACKOFF_CAP_MS", 1)

    def always_busy(*args, **kwargs):
        exc = sqlite3.OperationalError("database is locked")
        exc.sqlite_errorcode = sqlite3.SQLITE_BUSY
        raise exc

    repo.commit_developer_promotion = always_busy

    out = run(repo)

    assert out.committed is False
    assert out.reason == "RETRIABLE_BUSY_EXHAUSTED"
    assert out.snapshot_id is None
    assert out.d2_version is None


def test_tc09_stale_base_version_is_internal_and_retry_succeeds(monkeypatch):
    repo = setup_repo()
    real = repo.commit_developer_promotion
    calls = 0

    def stale_once(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("STALE_BASE_VERSION")
        return real(*args, **kwargs)

    repo.commit_developer_promotion = stale_once
    monkeypatch.setattr(dp, "BACKOFF_BASE_MS", 0)
    monkeypatch.setattr(dp, "BACKOFF_CAP_MS", 0)

    out = run(repo)

    assert calls == 2
    assert out.committed is True
    assert out.reason != "STALE_BASE_VERSION"
    assert out.snapshot_id is not None
    assert out.d2_version == 1


def test_tc10_real_external_writer_lock_exhausts_retry_budget(tmp_path, monkeypatch):
    db = tmp_path / "tc10.sqlite"
    repo = setup_repo(path=str(db))
    blocker = SQLiteRepository(str(db))

    blocker.conn.execute("BEGIN IMMEDIATE")

    monkeypatch.setattr(dp, "PROMOTION_DEADLINE_MS", 80)
    monkeypatch.setattr(dp, "BUSY_TIMEOUT_CAP_MS", 20)
    monkeypatch.setattr(dp, "BACKOFF_BASE_MS", 5)
    monkeypatch.setattr(dp, "BACKOFF_FACTOR", 1)
    monkeypatch.setattr(dp, "BACKOFF_CAP_MS", 5)

    try:
        out = run(repo)
    finally:
        blocker.conn.rollback()
        blocker.close()

    assert out.committed is False
    assert out.reason == "RETRIABLE_BUSY_EXHAUSTED"
    assert out.snapshot_id is None
    assert out.d2_version is None
    assert repo.get_d2_current_snapshot(PROJECT) is None


@pytest.mark.parametrize(
    "binding_error",
    [
        "LEDGER_BINDING_SNAPSHOT_NOT_FOUND",
        "LEDGER_BINDING_PROJECT_MISMATCH",
        "LEDGER_BINDING_VERSION_MISMATCH",
    ],
)
def test_tc13_inconsistent_ledger_fast_path_is_integrity_failure(
    monkeypatch, binding_error
):
    repo = setup_repo()
    calls = 0

    def inconsistent_ledger(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError(binding_error)

    monkeypatch.setattr(
        repo,
        "get_developer_promotion_commit",
        inconsistent_ledger,
    )

    out = run(repo)

    assert calls == 1
    assert out.committed is False
    assert out.reason == "INTEGRITY_FAILURE"
    assert out.effects_status == "NOT_ATTEMPTED"
    assert out.snapshot_id is None
    assert out.d2_version is None


def test_tc13b_real_persisted_ledger_corruption_hits_fast_path_integrity_failure():
    repo = setup_repo()

    first = run(repo)
    assert first.committed is True
    assert first.snapshot_id is not None
    assert first.d2_version is not None

    snapshot_count_before = repo.conn.execute(
        "SELECT COUNT(*) FROM d2_snapshots WHERE project_id=?",
        (PROJECT,),
    ).fetchone()[0]

    repo.conn.execute(
        """
        UPDATE developer_promotion_idempotency
        SET d2_version = d2_version + 1
        WHERE project_id=?
          AND proposal_id=?
          AND proposal_fingerprint=?
          AND human_review_id=?
        """,
        (PROJECT, PROPOSAL, FP, REVIEW),
    )
    repo.conn.commit()

    second = run(repo)

    snapshot_count_after = repo.conn.execute(
        "SELECT COUNT(*) FROM d2_snapshots WHERE project_id=?",
        (PROJECT,),
    ).fetchone()[0]

    assert second.committed is False
    assert second.reason == "INTEGRITY_FAILURE"
    assert second.effects_status == "NOT_ATTEMPTED"
    assert second.snapshot_id is None
    assert second.d2_version is None
    assert snapshot_count_after == snapshot_count_before


def test_tc04_migrated_schema_with_inconsistent_ledger_fails_closed_at_startup(tmp_path):
    db = tmp_path / "tc04.sqlite"

    repo = SQLiteRepository(str(db))
    repo.conn.execute(
        """
        INSERT INTO projects(project_id, name, stage, version)
        VALUES (?, ?, ?, ?)
        """,
        (PROJECT, "P", "test", 1),
    )
    repo.conn.execute(
        """
        INSERT INTO d2_snapshots(
            snapshot_id, project_id, version, elements_json,
            content_hash, actor, source_event_id, created_at,
            based_on_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "tc04-snapshot",
            PROJECT,
            1,
            "[]",
            "tc04-hash",
            "tester",
            None,
            "2026-09-30T00:00:00",
            None,
        ),
    )
    repo.conn.execute(
        """
        INSERT INTO developer_promotion_idempotency(
            project_id, proposal_id, proposal_fingerprint,
            human_review_id, snapshot_id, d2_version, committed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            PROJECT,
            PROPOSAL,
            FP,
            REVIEW,
            "tc04-snapshot",
            2,
            "2026-09-30T00:00:01",
        ),
    )
    repo.conn.commit()
    repo.close()

    with pytest.raises(
        RuntimeError,
        match="^PROMOTION_LEDGER_BINDING_INTEGRITY_FAILURE$",
    ):
        SQLiteRepository(str(db))
