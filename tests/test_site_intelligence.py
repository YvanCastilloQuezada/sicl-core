from __future__ import annotations

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def test_site_intelligence_trujillo_records_traceable_facts_without_normative_inference(monkeypatch) -> None:
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
    assert len(project.constraints) == 0
    events = repo.events("SITE-001")
    site_events = [event for event in events if event.type == "FACT_SET"]
    assert len(site_events) == 3
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

    assert len(first["data"]["records"]) == 3
    assert second["data"]["records"] == []
    project = repo.get_project("SITE-002")
    assert project is not None
    assert len(project.facts) == 3
    assert len(project.constraints) == 0


def test_site_intelligence_unknown_location_requires_human_decision(monkeypatch) -> None:
    monkeypatch.setattr("sicl.cli.get_site_observation", lambda location: (_ for _ in ()).throw(ValueError("unknown")))
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE SITE-003 Site")

    result = cli.execute("/SITE INTELLIGENCE Cusco, Peru")

    assert result["status"] == "REQUIRES_HUMAN_DECISION"
    assert result["code"] == "LOCATION_NOT_RECOGNIZED"
    assert "Ingrese datos manualmente" in result["message"]


def test_site_observation_has_complete_traceability() -> None:
    from sicl.site_intelligence import FALLBACK_TRUJILLO

    assert FALLBACK_TRUJILLO.state == "OBSERVED"
    assert FALLBACK_TRUJILLO.captured_at
    assert FALLBACK_TRUJILLO.raw_response == {"fixture": "FALLBACK_TRUJILLO"}
    assert FALLBACK_TRUJILLO.method_version == "DETERMINISTIC_FIXTURE/1"
    assert FALLBACK_TRUJILLO.evidence_url == "fixture://FALLBACK_TRUJILLO"
    assert FALLBACK_TRUJILLO.evidence_hash
