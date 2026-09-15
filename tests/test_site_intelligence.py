from __future__ import annotations

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def test_site_intelligence_trujillo_records_traceable_facts_and_constraint(monkeypatch) -> None:
    from sicl.site_intelligence import FALLBACK_TRUJILLO
    monkeypatch.setattr("sicl.cli.get_site_observation", lambda location: FALLBACK_TRUJILLO)
    repo = SQLiteRepository()
    cli = CLI(repo, actor="architect")
    cli.execute("/PROJECT CREATE SITE-001 Site")

    result = cli.execute("/SITE INTELLIGENCE Trujillo, Peru")

    assert result["status"] == "OK"
    assert result["data"]["source"] == "SITE_INTELLIGENCE_FIXTURE"
    assert result["data"]["simulated"] is True
    project = repo.get_project("SITE-001")
    assert project is not None
    assert len(project.facts) == 3
    assert len(project.constraints) == 1
    events = repo.events("SITE-001")
    site_events = [event for event in events if event.type in {"FACT_SET", "CONSTRAINT_SET"}]
    assert len(site_events) == 4
    assert all(event.source == "SITE_INTELLIGENCE_FIXTURE" for event in site_events)
    assert {fact.source for fact in project.facts.values()} == {"SITE_INTELLIGENCE_FIXTURE"}


def test_site_intelligence_is_idempotent_for_same_location(monkeypatch) -> None:
    from sicl.site_intelligence import FALLBACK_TRUJILLO
    monkeypatch.setattr("sicl.cli.get_site_observation", lambda location: FALLBACK_TRUJILLO)
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE SITE-002 Site")

    first = cli.execute("/SITE INTELLIGENCE Trujillo")
    second = cli.execute("/SITE INTELLIGENCE Trujillo")

    assert len(first["data"]["records"]) == 4
    assert second["data"]["records"] == []
    project = repo.get_project("SITE-002")
    assert project is not None
    assert len(project.facts) == 3
    assert len(project.constraints) == 1


def test_site_intelligence_unknown_location_requires_human_decision(monkeypatch) -> None:
    monkeypatch.setattr("sicl.cli.get_site_observation", lambda location: (_ for _ in ()).throw(ValueError("unknown")))
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE SITE-003 Site")

    result = cli.execute("/SITE INTELLIGENCE Cusco, Peru")

    assert result["status"] == "REQUIRES_HUMAN_DECISION"
    assert result["code"] == "LOCATION_NOT_RECOGNIZED"
    assert "Ingrese datos manualmente" in result["message"]
