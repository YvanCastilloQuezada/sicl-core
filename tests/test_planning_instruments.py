from __future__ import annotations

import sqlite3
from datetime import date

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.domain import PlanningInstrument, PlanningInstrumentStatus, PlanningInstrumentType, SpatialScope
from sicl.repository import SQLiteRepository


def test_planning_minimal_and_cli_catalog(tmp_path):
    repo = SQLiteRepository(tmp_path / "planning.sqlite")
    try:
        cli = CLI(repo)
        assert cli.execute('/PROJECT CREATE P-PLAN "Planning"')["code"] == "OK"
        created = cli.execute('/PLANNING ADD PI-001 PLAN_URBANO "Plan Urbano" Trujillo')
        assert created["code"] == "OK"
        assert created["data"]["instrument"]["status"] == "UNKNOWN"
        assert cli.execute('/PLANNING SHOW PI-001')["data"]["instrument"]["instrument_id"] == "PI-001"
        assert len(cli.execute('/PLANNING LIST')["data"]["instruments"]) == 1
        assert len(cli.execute('/PLANNING TYPES')["data"]["types"]) == 10
    finally:
        repo.close()


def test_planning_all_fields_and_invalid_type(tmp_path):
    repo = SQLiteRepository(tmp_path / "planning-fields.sqlite")
    try:
        instrument = PlanningInstrument(
            "PI-FULL", None, PlanningInstrumentType.PLAN_REGIONAL, "Regional Plan", "La Libertad",
            "Authority", date(2026, 1, 2), "2026-2030", [SpatialScope.REGION, SpatialScope.CIUDAD_DISTRITO],
            PlanningInstrumentStatus.ACTIVE, ["Coordinate growth"], "https://official.example/plan", "Summary", "OFFICIAL_SOURCE",
        )
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-FULL "Full"')
        repo.insert_planning_instrument_and_event(instrument, cli._event("P-FULL", "PLANNING_INSTRUMENT_REGISTERED", {"instrument_id": instrument.instrument_id}))
        restored = repo.get_planning_instrument("PI-FULL")
        assert restored is not None
        assert restored.approval_date == date(2026, 1, 2)
        assert restored.scope_applicable == [SpatialScope.REGION, SpatialScope.CIUDAD_DISTRITO]
        assert cli.execute('/PLANNING ADD PI-BAD NOT_A_TYPE "Bad"')["code"] == "INVALID_ARGUMENT"
    finally:
        repo.close()


def test_duplicate_instrument_id_is_rejected(tmp_path):
    repo = SQLiteRepository(tmp_path / "planning-duplicate.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-DUP "Duplicate"')
        assert cli.execute('/PLANNING ADD PI-001 PLAN_LOCAL "Local"')["code"] == "OK"
        duplicate = cli.execute('/PLANNING ADD PI-001 PLAN_LOCAL "Local again"')
        assert duplicate["code"] in {"PERSISTENCE_ERROR", "CONFLICT"}
    finally:
        repo.close()


def test_link_persists_and_does_not_create_constraint(tmp_path):
    path = tmp_path / "planning-link.sqlite"
    repo = SQLiteRepository(path)
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-LINK "Link"')
    cli.execute('/PLANNING ADD PI-LINK PLAN_LOCAL "Local" Trujillo https://official.example/local')
    project = repo.get_project("P-LINK")
    project.version += 1
    repo.link_planning_instrument_and_event(project, "PI-LINK", "tester", cli._event("P-LINK", "PLANNING_INSTRUMENT_LINKED", {"instrument_id": "PI-LINK"}))
    assert len(repo.get_project("P-LINK").planning_instruments) == 1
    assert not repo.get_project("P-LINK").constraints
    repo.close()
    reopened = SQLiteRepository(path)
    try:
        assert list(reopened.get_project("P-LINK").planning_instruments) == ["PI-LINK"]
        assert any(event.type == "PLANNING_INSTRUMENT_LINKED" for event in reopened.events("P-LINK"))
    finally:
        reopened.close()


def test_planning_append_only(tmp_path):
    repo = SQLiteRepository(tmp_path / "planning-append.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-APPEND "Append"')
        cli.execute('/PLANNING ADD PI-APPEND PLAN_LOCAL "Local"')
        for statement in ["UPDATE planning_instruments SET name='changed'", "DELETE FROM planning_instruments"]:
            try:
                repo.conn.execute(statement)
                raise AssertionError("append-only trigger did not reject mutation")
            except sqlite3.IntegrityError:
                pass
    finally:
        repo.close()


def test_planning_http_catalog_filters_and_link(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "planning-http.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-HTTP "HTTP"')
        cli.execute('/PLANNING ADD PI-HTTP PLAN_URBANO "Urban" Trujillo https://official.example/urban')
        assert client.get('/v1/planning/types').status_code == 200
        assert len(client.get('/v1/planning/instruments?instrument_type=PLAN_URBANO&jurisdiction=Trujillo').json()["data"]["instruments"]) == 1
        individual = client.get('/v1/planning/instruments/PI-HTTP')
        assert individual.status_code == 200
        linked = client.post('/v1/projects/P-HTTP/planning/instruments', json={"instrument_id": "PI-HTTP"})
        assert linked.status_code == 200
        assert linked.json()["data"]["constraint_created"] is False
        listed = client.get('/v1/projects/P-HTTP/planning/instruments')
        assert listed.status_code == 200
        assert listed.json()["data"]["instruments"][0]["instrument_id"] == "PI-HTTP"
        duplicate = client.post('/v1/projects/P-HTTP/planning/instruments', json={"instrument_id": "PI-HTTP"})
        assert duplicate.status_code == 409
    finally:
        app.dependency_overrides.clear()
        repo.close()
