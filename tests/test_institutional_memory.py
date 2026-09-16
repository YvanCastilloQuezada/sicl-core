from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


@pytest.fixture(autouse=True)
def clear_service_token(monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)


def prepare_closed(repo: SQLiteRepository, project_id: str = "MEM-SOURCE") -> CLI:
    cli = CLI(repo, actor="architect")
    assert cli.execute(f'/PROJECT CREATE {project_id} "Source"')["code"] == "OK"
    assert cli.execute(f'/PROJECT OPEN {project_id}')["code"] == "OK"
    cli.execute('/PREFERENCE SET "Prefer low energy" OWNER')
    cli.execute('/FACT SET "Site area is 2000 m2" CATASTRO')
    assert cli.execute('/STAGE SET CLOSED')["code"] == "OK"
    return cli


def test_extract_requires_closed_project_and_anonymizes(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory.sqlite")
    cli = prepare_closed(repo)
    extracted = cli.execute('/MEMORY EXTRACT MEM-SOURCE Yvan PRODUCT_OWNER')
    assert extracted["code"] == "OK"
    memory = extracted["data"]["memory"]
    assert memory["anonymized"] is True
    assert memory["project_id_source"] is None
    assert memory["memory_type"] == "LESSON_LEARNED"
    assert memory["state"] == "ACTIVE"
    repo.close()


def test_extract_open_project_is_rejected(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE OPEN "Open"')
    cli.execute('/PROJECT OPEN OPEN')
    result = cli.execute('/MEMORY EXTRACT OPEN Yvan PRODUCT_OWNER')
    assert result["code"] == "PROJECT_NOT_CLOSED"
    repo.close()


def test_memory_list_show_and_types(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory.sqlite")
    cli = prepare_closed(repo)
    created = cli.execute('/MEMORY EXTRACT MEM-SOURCE Yvan PRODUCT_OWNER')
    memory_id = created["data"]["memory"]["memory_id"]
    assert cli.execute('/MEMORY LIST')["data"]["memories"][0]["memory_id"] == memory_id
    assert cli.execute(f'/MEMORY SHOW {memory_id}')["data"]["memory"]["memory_id"] == memory_id
    assert set(cli.execute('/MEMORY TYPES')["data"]["types"]) == {"DECISION_PATTERN", "PREFERENCE_PATTERN", "EVALUATION_PATTERN", "GENERATION_PATTERN", "LESSON_LEARNED"}
    repo.close()


def test_revoke_requires_authority_and_creates_new_version(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory.sqlite")
    cli = prepare_closed(repo)
    memory_id = cli.execute('/MEMORY EXTRACT MEM-SOURCE Yvan PRODUCT_OWNER')["data"]["memory"]["memory_id"]
    assert cli.execute(f'/MEMORY REVOKE {memory_id} Yvan')["code"] == "HUMAN_AUTHORITY_REQUIRED"
    revoked = cli.execute(f'/MEMORY REVOKE {memory_id} Yvan PRODUCT_OWNER')
    assert revoked["code"] == "OK"
    assert revoked["data"]["memory"]["state"] == "REVOKED"
    assert revoked["data"]["memory"]["version"] == 2
    repo.close()


def test_revoked_memory_cannot_apply(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory.sqlite")
    cli = prepare_closed(repo)
    memory_id = cli.execute('/MEMORY EXTRACT MEM-SOURCE Yvan PRODUCT_OWNER')["data"]["memory"]["memory_id"]
    cli.execute(f'/MEMORY REVOKE {memory_id} Yvan PRODUCT_OWNER')
    cli.execute('/PROJECT CREATE TARGET "Target"')
    result = cli.execute(f'/MEMORY APPLY {memory_id} TARGET')
    assert result["code"] == "MEMORY_REVOKED"
    repo.close()


def test_apply_requires_explicit_actor_and_does_not_change_canonical_facts(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory.sqlite")
    cli = prepare_closed(repo)
    memory_id = cli.execute('/MEMORY EXTRACT MEM-SOURCE Yvan PRODUCT_OWNER')["data"]["memory"]["memory_id"]
    cli.execute('/PROJECT CREATE TARGET "Target"')
    cli.execute('/PROJECT OPEN TARGET')
    before = repo.get_project("TARGET")
    applied = cli.execute(f'/MEMORY APPLY {memory_id} TARGET')
    after = repo.get_project("TARGET")
    assert applied["code"] == "OK"
    assert applied["data"]["canonical_state_changed"] is False
    assert before and after and after.facts == before.facts
    assert after.preferences == before.preferences
    assert repo.events("TARGET")[-1].type == "INSTITUTIONAL_MEMORY_APPLIED"
    repo.close()


def test_memory_does_not_create_decision(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory.sqlite")
    cli = prepare_closed(repo)
    memory_id = cli.execute('/MEMORY EXTRACT MEM-SOURCE Yvan PRODUCT_OWNER')["data"]["memory"]["memory_id"]
    project = repo.get_project("MEM-SOURCE")
    assert project and not project.decisions
    assert cli.execute('/MEMORY SHOW ' + memory_id)["data"]["memory"]["decisions_referenced"] == []
    repo.close()


def test_memory_is_persistent_and_append_only(tmp_path: Path):
    db = tmp_path / "memory.sqlite"
    repo = SQLiteRepository(db)
    prepare_closed(repo)
    memory_id = CLI(repo).execute('/MEMORY EXTRACT MEM-SOURCE Yvan PRODUCT_OWNER')["data"]["memory"]["memory_id"]
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("UPDATE institutional_memory SET summary='tampered'")
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("DELETE FROM institutional_memory")
    repo.close()
    reopened = SQLiteRepository(db)
    memory = reopened.get_memory(memory_id)
    assert memory and memory.memory_id == memory_id
    reopened.close()


def test_http_memory_endpoints(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "memory-api.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    assert client.post('/v1/projects', json={"project_id": "HTTP-MEM", "name": "Source"}).status_code == 200
    client.post('/v1/projects/HTTP-MEM/commands', json={"command": "/PREFERENCE SET \"Prefer low energy\" OWNER"})
    client.post('/v1/projects/HTTP-MEM/commands', json={"command": "/STAGE SET CLOSED"})
    extracted = client.post('/v1/memory/extract', json={"project_id": "HTTP-MEM", "actor": "Yvan", "authority": "PRODUCT_OWNER"})
    assert extracted.status_code == 200
    memory_id = extracted.json()["data"]["memory"]["memory_id"]
    assert client.get('/v1/memory').status_code == 200
    assert client.get('/v1/memory/types').status_code == 200
    assert client.get(f'/v1/memory/{memory_id}').status_code == 200
    assert client.post(f'/v1/memory/{memory_id}/revoke', json={"actor": "Yvan", "authority": "PRODUCT_OWNER"}).status_code == 200
    app.dependency_overrides.clear()
    repo.close()
