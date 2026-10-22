from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.domain import EvidenceType, SourceType
from sicl.repository import SQLiteRepository


def test_evidence_add_minimum_fields_and_hash():
    repo = SQLiteRepository()
    cli = CLI(repo, actor="architect")
    assert cli.execute('/PROJECT CREATE P-E1 "Evidence"')["code"] == "OK"
    result = cli.execute('/EVIDENCE ADD E-1 "Measured area is 2000 m2" MEASUREMENT')
    assert result["code"] == "OK"
    evidence = repo.get_evidence("P-E1", "E-1")
    assert evidence.evidence_type is EvidenceType.MEASUREMENT
    assert evidence.evidence_hash == hashlib.sha256(b"Measured area is 2000 m2").hexdigest()
    assert evidence.state == "OBSERVED"
    assert repo.events("P-E1")[-1].type == "EVIDENCE_ADDED"


def test_evidence_add_all_fields_and_cli_list_show():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-E2 "Evidence"')
    result = cli.execute('/EVIDENCE ADD E-2 "Official plan" DOCUMENT SRC-1 https://example.test/plan')
    assert result["code"] == "OK"
    listed = cli.execute('/EVIDENCE LIST')
    shown = cli.execute('/EVIDENCE SHOW E-2')
    assert listed["code"] == shown["code"] == "OK"
    assert listed["data"]["evidence"][0]["evidence_id"] == "E-2"
    assert shown["data"]["evidence_id"] == "E-2"
    assert shown["data"]["source_id"] == "SRC-1"
    assert shown["data"]["evidence_url"] == "https://example.test/plan"


def test_evidence_duplicate_id_is_rejected():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-E3 "Evidence"')
    assert cli.execute('/EVIDENCE ADD E-3 "First" DOCUMENT')["code"] == "OK"
    duplicate = cli.execute('/EVIDENCE ADD E-3 "Second" DOCUMENT')
    assert duplicate["code"] == "EVIDENCE_ALREADY_EXISTS"
    assert len(repo.list_evidence("P-E3")) == 1


def test_evidence_invalid_type_is_rejected():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-E4 "Evidence"')
    result = cli.execute('/EVIDENCE ADD E-4 "Unknown" NOT_A_TYPE')
    assert result["code"] == "INVALID_EVIDENCE_TYPE"


def test_evidence_persists_after_restart(tmp_path):
    db = tmp_path / "evidence.sqlite"
    first = SQLiteRepository(db)
    cli = CLI(first)
    cli.execute('/PROJECT CREATE P-E5 "Evidence"')
    cli.execute('/EVIDENCE ADD E-5 "Persisted" OBSERVATION')
    first.close()
    second = SQLiteRepository(db)
    evidence = second.get_evidence("P-E5", "E-5")
    assert evidence is not None
    assert evidence.statement == "Persisted"
    assert evidence.evidence_type is EvidenceType.OBSERVATION


def test_evidence_does_not_create_fact_automatically():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-E6 "Evidence"')
    cli.execute('/EVIDENCE ADD E-6 "Observed statement" OBSERVATION')
    project = repo.get_project("P-E6")
    assert project.facts == {}
    assert set(project.evidence) == {"E-6"}


def test_evidence_is_append_only():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-E7 "Evidence"')
    cli.execute('/EVIDENCE ADD E-7 "Immutable" DOCUMENT')
    try:
        repo.conn.execute("UPDATE evidence SET statement='changed' WHERE project_id='P-E7' AND evidence_id='E-7'")
        assert False, "Evidence UPDATE should be rejected"
    except Exception as exc:
        assert "append-only" in str(exc)
    try:
        repo.conn.execute("DELETE FROM evidence WHERE project_id='P-E7' AND evidence_id='E-7'")
        assert False, "Evidence DELETE should be rejected"
    except Exception as exc:
        assert "append-only" in str(exc)


def test_source_table_has_canonical_shape():
    repo = SQLiteRepository()
    columns = {row["name"] for row in repo.conn.execute("PRAGMA table_info(sources)")}
    assert columns == {"source_id", "project_id", "source_type", "title", "url", "version"}
    assert SourceType.OFFICIAL.value == "OFFICIAL"


def test_http_evidence_create_list_get_and_hash(tmp_path, monkeypatch):
    repo = SQLiteRepository(tmp_path / "api-evidence.sqlite", check_same_thread=False)
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            created_project = client.post("/v1/projects", json={"project_id": "P-API-E", "name": "API Evidence"})
            assert created_project.status_code == 200
            created = client.post("/v1/projects/P-API-E/evidence", json={"evidence_id": "E-API", "statement": "API observation", "evidence_type": "OBSERVATION"})
            assert created.status_code == 200
            body = created.json()
            assert body["contract_version"] == "1.0"
            assert body["project_id"] == "P-API-E"
            assert body["observed_version"] == 2
            assert body["data"]["evidence"]["evidence_hash"] == hashlib.sha256(b"API observation").hexdigest()
            listed = client.get("/v1/projects/P-API-E/evidence")
            individual = client.get("/v1/projects/P-API-E/evidence/E-API")
            assert listed.status_code == individual.status_code == 200
            assert len(listed.json()["data"]["evidence"]) == 1
            assert individual.json()["data"]["evidence"]["evidence_id"] == "E-API"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_http_evidence_invalid_type_and_duplicate_are_rejected(tmp_path, monkeypatch):
    repo = SQLiteRepository(tmp_path / "api-evidence-errors.sqlite", check_same_thread=False)
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            client.post("/v1/projects", json={"project_id": "P-API-ERR", "name": "API Evidence"})
            invalid = client.post("/v1/projects/P-API-ERR/evidence", json={"evidence_id": "E-ERR", "statement": "Bad", "evidence_type": "BAD"})
            assert invalid.status_code == 400
            assert invalid.json()["detail"]["code"] == "INVALID_EVIDENCE_TYPE"
            client.post("/v1/projects/P-API-ERR/evidence", json={"evidence_id": "E-ERR", "statement": "Good", "evidence_type": "DOCUMENT"})
            duplicate = client.post("/v1/projects/P-API-ERR/evidence", json={"evidence_id": "E-ERR", "statement": "Again", "evidence_type": "DOCUMENT"})
            assert duplicate.status_code == 400
            assert duplicate.json()["detail"]["code"] == "EVIDENCE_ALREADY_EXISTS"
    finally:
        app.dependency_overrides.clear()
        repo.close()
