import sqlite3

import pytest

from sicl.domain import Event, HumanReview, Project, now_iso
from sicl.repository import SQLiteRepository


def review(**overrides):
    values = {
        "review_id": "REV-1",
        "project_id": "P",
        "actor": "Yvan",
        "timestamp": "2026-09-29T12:00:00Z",
        "review": "Reviewed",
        "reason": "Architecture review",
        "authority": "PRODUCT_OWNER",
    }
    values.update(overrides)
    return HumanReview(**values)


def test_human_review_legacy_reference_fields_are_none():
    value = review()
    assert value.referenced_entity_type is None
    assert value.referenced_entity_id is None
    assert value.referenced_fingerprint is None


def test_human_review_requires_complete_supported_binding():
    with pytest.raises(ValueError):
        review(referenced_entity_type="DEVELOPER_PROPOSAL")
    with pytest.raises(ValueError):
        review(referenced_entity_id="dev-prop", referenced_fingerprint="a" * 64)
    with pytest.raises(ValueError):
        review(
            referenced_entity_type="OTHER",
            referenced_entity_id="entity",
            referenced_fingerprint="a" * 64,
        )


@pytest.mark.parametrize("fingerprint", ["A" * 64, "a" * 63, "z" * 64, ""])
def test_human_review_requires_lowercase_sha256_fingerprint(fingerprint):
    with pytest.raises(ValueError):
        review(
            referenced_entity_type="DEVELOPER_PROPOSAL",
            referenced_entity_id="dev-prop",
            referenced_fingerprint=fingerprint,
        )


def test_human_review_accepts_developer_proposal_binding():
    value = review(
        referenced_entity_type="DEVELOPER_PROPOSAL",
        referenced_entity_id="dev-prop",
        referenced_fingerprint="a" * 64,
    )
    assert value.referenced_entity_id == "dev-prop"


def test_repository_migrates_legacy_human_reviews_and_round_trips_binding(tmp_path):
    path = tmp_path / "legacy.sqlite"
    conn = sqlite3.connect(path)
    conn.executescript("""
    CREATE TABLE projects (
      project_id TEXT PRIMARY KEY, name TEXT NOT NULL, stage TEXT NOT NULL, version INTEGER NOT NULL,
      spatial_scope TEXT NULL, temporal_scope TEXT NOT NULL DEFAULT 'proyecto'
    );
    CREATE TABLE human_reviews (
      review_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
      actor TEXT NOT NULL, timestamp TEXT NOT NULL, review TEXT NOT NULL, reason TEXT NOT NULL,
      authority TEXT NOT NULL, status TEXT NOT NULL, version INTEGER NOT NULL
    );
    INSERT INTO projects(project_id,name,stage,version) VALUES ('P','Legacy','ANTEPROYECTO',1);
    INSERT INTO human_reviews VALUES ('REV-OLD','P','Yvan','2026-09-29T12:00:00Z','Reviewed','Legacy','PRODUCT_OWNER','APPROVED',1);
    """)
    conn.commit()
    conn.close()

    repo = SQLiteRepository(path)
    old = repo.get_project("P").human_reviews["REV-OLD"]
    assert old.referenced_entity_type is None
    assert old.referenced_entity_id is None
    assert old.referenced_fingerprint is None

    bound = review(
        review_id="REV-NEW",
        referenced_entity_type="DEVELOPER_PROPOSAL",
        referenced_entity_id="dev-prop",
        referenced_fingerprint="a" * 64,
    )
    project = repo.get_project("P")
    project.human_reviews[bound.review_id] = bound
    project.version += 1
    repo.insert_entity_and_event(
        """INSERT INTO human_reviews(
            review_id, project_id, actor, timestamp, review, reason, authority, status, version,
            referenced_entity_type, referenced_entity_id, referenced_fingerprint
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            bound.review_id, bound.project_id, bound.actor, bound.timestamp, bound.review,
            bound.reason, bound.authority, bound.status, bound.version,
            bound.referenced_entity_type, bound.referenced_entity_id, bound.referenced_fingerprint,
        ),
        project,
        Event(None, now_iso(), "P", "HUMAN_REVIEW_RECORDED", {}, "Yvan", "TEST"),
    )
    hydrated = repo.get_project("P").human_reviews["REV-NEW"]
    assert hydrated == bound
