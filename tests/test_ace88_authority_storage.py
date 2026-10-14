"""ACE88 — Persistence and append-only invariants."""

import sqlite3

import pytest

from sicl.repository import SQLiteRepository


def test_authority_schema_survives_reopen(tmp_path):
    path = tmp_path / "authority.db"

    repo = SQLiteRepository(path)
    repo.close()

    repo = SQLiteRepository(path)
    try:
        columns = {
            row["name"]
            for row in repo.conn.execute(
                "PRAGMA table_info(human_authority_proofs)"
            )
        }

        assert {
            "nonce",
            "project_id",
            "review_id",
            "proposal_id",
            "proposal_fingerprint",
            "actor_id",
            "key_id",
            "payload_json",
            "signature_b64",
            "verified_at",
        } <= columns
    finally:
        repo.close()


def test_authority_proofs_are_append_only(tmp_path):
    repo = SQLiteRepository(tmp_path / "authority.db")

    try:
        # Isolated fixture: satisfy foreign keys.
        repo.conn.execute(
            """
            INSERT INTO projects(
                project_id, name, stage, version,
                spatial_scope, temporal_scope
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("P", "Test", "test", 1, None, "proyecto"),
        )

        repo.conn.execute(
            """
            INSERT INTO human_reviews(
                review_id, project_id, actor, timestamp,
                review, reason, authority, status, version,
                referenced_entity_type, referenced_entity_id,
                referenced_fingerprint
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "R1", "P", "OWNER",
                "2026-10-14T12:00:00+00:00",
                "APPROVED", "test", "OWNER",
                "APPROVED", 1,
                "DEVELOPER_PROPOSAL", "PROP-1", "fp",
            ),
        )

        repo.conn.execute(
            """
            INSERT INTO human_authority_proofs(
                nonce, project_id, review_id, proposal_id,
                proposal_fingerprint, actor_id, key_id,
                payload_json, signature_b64, verified_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "nonce-1", "P", "R1", "PROP-1",
                "fp", "OWNER", "key-1",
                "{}", "test-signature",
                "2026-10-14T12:00:00+00:00",
            ),
        )

        repo.conn.commit()

        with pytest.raises(
            sqlite3.DatabaseError,
            match="authority proofs are append-only",
        ):
            repo.conn.execute(
                """
                UPDATE human_authority_proofs
                SET actor_id = 'FORGED'
                WHERE nonce = 'nonce-1'
                """
            )

        repo.conn.rollback()

        with pytest.raises(
            sqlite3.DatabaseError,
            match="authority proofs are append-only",
        ):
            repo.conn.execute(
                """
                DELETE FROM human_authority_proofs
                WHERE nonce = 'nonce-1'
                """
            )

        repo.conn.rollback()

        count = repo.conn.execute(
            "SELECT COUNT(*) FROM human_authority_proofs"
        ).fetchone()[0]

        assert count == 1

    finally:
        repo.close()
