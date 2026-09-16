from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def project(repo: SQLiteRepository) -> CLI:
    cli = CLI(repo, actor="owner")
    assert cli.execute('/PROJECT CREATE P-12 "Multi actor"')["status"] == "OK"
    return cli


def test_actor_roles_authority_and_persistence(tmp_path):
    repo = SQLiteRepository(tmp_path / "actors.sqlite")
    cli = project(repo)
    created = cli.execute('/ACTOR ADD A-CLIENT CLIENT Client ADVISORY')
    assert created["status"] == "OK"
    cli.execute('/ACTOR ADD A-ARCH ARCHITECT Architect CONTRIBUTORY')
    cli.execute('/ACTOR ADD A-DEC ARCHITECT "Lead Architect" DECISIONAL')
    assert len(cli.execute('/ACTOR LIST')["data"]["actors"]) == 3
    reopened = SQLiteRepository(tmp_path / "actors.sqlite")
    loaded = reopened.get_project("P-12")
    assert loaded is not None
    assert loaded.actors["A-DEC"].authority_level.value == "DECISIONAL"


def test_positions_record_disagreement_and_filter(tmp_path):
    repo = SQLiteRepository(tmp_path / "positions.sqlite")
    cli = project(repo)
    cli.execute('/ACTOR ADD A-1 CLIENT Client CONTRIBUTORY')
    cli.execute('/ACTOR ADD A-2 ENGINEER Engineer CONTRIBUTORY')
    first = cli.execute('/POSITION ADD A-1 ALTERNATIVE ALT-1 SUPPORT "Supports daylight"')
    second = cli.execute('/POSITION ADD A-2 ALTERNATIVE ALT-1 OPPOSE "Rejects cost"')
    assert first["status"] == second["status"] == "OK"
    positions = cli.execute('/POSITION LIST ALT-1')["data"]["positions"]
    assert {item["stance"] for item in positions} == {"SUPPORT", "OPPOSE"}


def test_advisory_actor_cannot_decide(tmp_path):
    repo = SQLiteRepository(tmp_path / "advisory.sqlite")
    cli = project(repo)
    cli.execute('/ACTOR ADD A-1 CLIENT Client ADVISORY')
    cli.execute('/HUMAN REVIEW A-1 2026-09-15T00:00:00Z "Reviewed" "Reason" BOARD')
    result = cli.execute('/DECISION RECORD "Proceed" A-1 BOARD')
    assert result["code"] == "DECISIONAL_ACTOR_REQUIRED"


def test_veto_blocks_decision(tmp_path):
    repo = SQLiteRepository(tmp_path / "veto.sqlite")
    cli = project(repo)
    cli.execute('/ACTOR ADD A-DEC ARCHITECT Architect DECISIONAL')
    cli.execute('/ACTOR ADD A-VETO REGULATOR Regulator VETO')
    cli.execute('/POSITION ADD A-VETO DECISION_PROPOSED D-1 OPPOSE "Regulatory objection"')
    cli.execute('/HUMAN REVIEW A-DEC 2026-09-15T00:00:00Z "Reviewed" "Reason" BOARD')
    result = cli.execute('/DECISION RECORD "Proceed" A-DEC BOARD')
    assert result["code"] == "VETO_BLOCKED"


def test_decisional_actor_requires_human_review(tmp_path):
    repo = SQLiteRepository(tmp_path / "review.sqlite")
    cli = project(repo)
    cli.execute('/ACTOR ADD A-DEC ARCHITECT Architect DECISIONAL')
    result = cli.execute('/DECISION RECORD "Proceed" A-DEC BOARD')
    assert result["code"] == "HUMAN_REVIEW_REQUIRED"


def test_actor_tables_are_append_only(tmp_path):
    repo = SQLiteRepository(tmp_path / "append.sqlite")
    cli = project(repo)
    cli.execute('/ACTOR ADD A-1 CLIENT Client ADVISORY')
    position = cli.execute('/POSITION ADD A-1 ALTERNATIVE ALT-1 NEUTRAL "Undecided"')["data"]["position"]
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("DELETE FROM actors WHERE actor_id='A-1'")
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("DELETE FROM actor_positions WHERE position_id=?", (position["position_id"],))


def test_multi_actor_http_endpoints(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "http.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        client = TestClient(app)
        created = client.post('/v1/projects', json={"project_id": "HTTP-ACT", "name": "HTTP actors"})
        assert created.status_code == 200
        actor = client.post('/v1/projects/HTTP-ACT/actors', json={"actor_id": "A-1", "role": "CLIENT", "name": "Client", "authority_level": "ADVISORY", "interests": ["cost"]})
        assert actor.status_code == 200
        assert actor.json()["data"]["actor"]["interests"] == ["cost"]
        position = client.post('/v1/projects/HTTP-ACT/positions', json={"actor_id": "A-1", "subject_type": "ALTERNATIVE", "subject_id": "ALT-1", "stance": "SUPPORT", "reason": "Good fit", "conditions": ["budget"]})
        assert position.status_code == 200
        assert len(client.get('/v1/projects/HTTP-ACT/actors').json()["data"]["actors"]) == 1
        assert len(client.get('/v1/projects/HTTP-ACT/positions', params={"subject_id": "ALT-1"}).json()["data"]["positions"]) == 1
    finally:
        app.dependency_overrides.clear()
