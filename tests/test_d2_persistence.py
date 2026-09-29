import hashlib
import json
import sqlite3

import pytest

from sicl.archi.identity import ArchiElementId
from sicl.archi.model import ArchiElement, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec
from sicl.archi.persistence import deserialize_elements, elements_content_hash, serialize_elements
from sicl.domain import Event, Project, now_iso
from sicl.repository import SQLiteRepository


def aid(project_id: str, kind: str, nonce: str) -> ArchiElementId:
    return ArchiElementId.compute(project_id, kind, nonce)


def geometry(x: int = 0) -> ArchiGeometry:
    return ArchiGeometry(
        GeometryKind.EXTRUDED_RECTANGLE,
        ProfileSpec(200, 100),
        x_mm=x,
        y_mm=20,
        z_mm=30,
        height_mm=2800,
    )


def elements(project_id: str = "P") -> tuple[ArchiElement, ...]:
    wall_id = aid(project_id, "WALL", "wall")
    door_id = aid(project_id, "DOOR", "door")
    opening_id = aid(project_id, "OPENING", "opening")
    return (
        ArchiElement(
            wall_id, project_id, ElementKind.WALL, geometry(),
            {"name": "Wall", "tags": ("external", "rated")},
            {"source": "test", "nested": {"confidence": 1.0}},
        ),
        ArchiElement(
            door_id, project_id, ElementKind.DOOR, geometry(100),
            {"name": "Door"}, {"source": "test"}, hosted_in=wall_id, hosted_in_version=1,
        ),
        ArchiElement(
            opening_id, project_id, ElementKind.OPENING, geometry(100),
            {"name": "Opening"}, None, contained_in=door_id, contained_in_version=1,
        ),
    )


def project(repo: SQLiteRepository, project_id: str = "P") -> Project:
    value = Project(project_id, "D2 persistence")
    repo.insert_project(value, Event(None, now_iso(), project_id, "PROJECT_CREATED", {}, "test", "TEST"))
    return value


def test_serialization_round_trip_complex_element():
    original = elements()
    restored = deserialize_elements(serialize_elements(original))
    assert restored == tuple(sorted(original, key=lambda item: item.element_id.value))
    assert dict(restored[0].properties) == dict(sorted(original, key=lambda item: item.element_id.value)[0].properties)


def test_serialization_is_deterministic_and_orders_by_element_id():
    original = elements()
    one = serialize_elements(original)
    two = serialize_elements(tuple(reversed(original)))
    assert one == two
    ids = [item["element_id"] for item in json.loads(one)]
    assert ids == sorted(ids)
    assert elements_content_hash(one) == hashlib.sha256(one.encode()).hexdigest()


def test_initial_and_second_snapshot_are_versioned_and_current_is_latest():
    repo = SQLiteRepository()
    project(repo)
    first = repo.insert_d2_snapshot_and_event("P", elements(), "architect", "TEST")
    changed = tuple(
        ArchiElement(
            item.element_id, item.project_id, item.kind,
            geometry(item.geometry.x_mm + 1), dict(item.properties), item.provenance,
            item.version + 1, item.hosted_in, item.contained_in,
            item.hosted_in_version, item.contained_in_version,
        )
        for item in elements()
    )
    second = repo.insert_d2_snapshot_and_event("P", changed, "architect", "TEST")
    assert first.version == 1
    assert second.version == 2
    assert repo.get_d2("P") == second.elements
    assert repo.get_d2_snapshot("P", 1) == first
    assert [item["version"] for item in repo.get_d2_history("P")] == [1, 2]


def test_get_d2_without_snapshot_returns_none():
    repo = SQLiteRepository()
    project(repo)
    assert repo.get_d2("P") is None
    assert repo.get_d2_current_snapshot("P") is None


def test_snapshot_and_event_are_atomic_when_snapshot_insert_fails():
    repo = SQLiteRepository()
    project(repo)
    repo.conn.executescript("""
    CREATE TRIGGER force_d2_insert_failure
    BEFORE INSERT ON d2_snapshots
    BEGIN SELECT RAISE(ABORT, 'forced D-2 failure'); END;
    """)
    before = len(repo.events("P"))
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert_d2_snapshot_and_event("P", elements(), "architect", "TEST")
    assert repo.get_d2("P") is None
    assert len(repo.events("P")) == before


def test_snapshot_and_event_are_atomic_when_event_insert_fails(monkeypatch):
    repo = SQLiteRepository()
    project(repo)
    before = len(repo.events("P"))

    def fail_event(_event):
        raise RuntimeError("forced event failure")

    monkeypatch.setattr(repo, "_insert_event", fail_event)
    with pytest.raises(RuntimeError):
        repo.insert_d2_snapshot_and_event("P", elements(), "architect", "TEST")
    assert repo.get_d2("P") is None
    assert len(repo.events("P")) == before


def test_restart_durability(tmp_path):
    path = tmp_path / "arki.sqlite"
    first_repo = SQLiteRepository(path)
    project(first_repo)
    committed = first_repo.insert_d2_snapshot_and_event("P", elements(), "architect", "TEST")
    first_repo.close()

    second_repo = SQLiteRepository(path)
    assert second_repo.get_d2("P") == committed.elements
    assert second_repo.get_d2_current_snapshot("P").content_hash == committed.content_hash
    second_repo.close()


def test_d2_snapshots_are_append_only():
    repo = SQLiteRepository()
    project(repo)
    committed = repo.insert_d2_snapshot_and_event("P", elements(), "architect", "TEST")
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("UPDATE d2_snapshots SET actor='x' WHERE snapshot_id=?", (committed.snapshot_id,))
    repo.conn.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("DELETE FROM d2_snapshots WHERE snapshot_id=?", (committed.snapshot_id,))
    repo.conn.rollback()


def test_d2_snapshot_does_not_change_project_version():
    repo = SQLiteRepository()
    project(repo)
    before = repo.get_project("P").version
    repo.insert_d2_snapshot_and_event("P", elements(), "architect", "TEST")
    assert repo.get_project("P").version == before


def test_snapshot_event_binding_and_stable_hash():
    repo = SQLiteRepository()
    project(repo)
    committed = repo.insert_d2_snapshot_and_event("P", elements(), "architect", "TEST")
    event = next(item for item in repo.events("P") if item.type == "D2_SNAPSHOT_COMMITTED")
    assert event.id == committed.source_event_id
    assert event.payload["snapshot_id"] == committed.snapshot_id
    assert event.payload["content_hash"] == committed.content_hash
    assert committed.content_hash == elements_content_hash(serialize_elements(elements()))


def test_nullable_relations_round_trip():
    item = ArchiElement(aid("P", "SITE", "site"), "P", ElementKind.SITE, geometry())
    restored = deserialize_elements(serialize_elements((item,)))[0]
    assert restored.hosted_in is None
    assert restored.contained_in is None
    assert restored.hosted_in_version is None
    assert restored.contained_in_version is None


def test_malformed_json_fails_explicitly():
    with pytest.raises(ValueError, match="invalid D-2 elements JSON"):
        deserialize_elements("{not-json")


def test_existing_database_gets_d2_schema_without_data_loss(tmp_path):
    path = tmp_path / "legacy.sqlite"
    repo = SQLiteRepository(path)
    project(repo)
    repo.close()
    reopened = SQLiteRepository(path)
    names = {row["name"] for row in reopened.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "d2_snapshots" in names
    assert reopened.get_project("P") is not None
