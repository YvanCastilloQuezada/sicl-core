from __future__ import annotations

from sicl.cli import CLI
from sicl.repository import SQLiteRepository
from sicl.site_intelligence import SiteObservation


def test_site_intelligence_trujillo_records_simulation_as_assumptions(monkeypatch) -> None:
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
    assert len(project.facts) == 0
    assert len(project.assumptions) == 3
    assert len(project.constraints) == 0
    assert all("simulad" in item.statement.lower() for item in project.assumptions.values())
    events = repo.events("SITE-001")
    site_events = [event for event in events if event.type == "ASSUMPTION_SET"]
    assert len(site_events) == 3
    assert all(event.source == "SITE_INTELLIGENCE_FIXTURE" for event in site_events)
    assert {item.basis for item in project.assumptions.values()} == {"SITE_INTELLIGENCE_FIXTURE"}


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
    assert len(project.facts) == 0
    assert len(project.assumptions) == 3
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

    assert FALLBACK_TRUJILLO.state == "INSUFFICIENT"
    assert FALLBACK_TRUJILLO.captured_at
    assert FALLBACK_TRUJILLO.raw_response == {"fixture": "FALLBACK_TRUJILLO"}
    assert FALLBACK_TRUJILLO.method_version == "DETERMINISTIC_FIXTURE/1"
    assert FALLBACK_TRUJILLO.evidence_url == "fixture://FALLBACK_TRUJILLO"
    assert FALLBACK_TRUJILLO.evidence_hash


def test_simulated_site_observation_cannot_claim_observed_state() -> None:
    import pytest

    with pytest.raises(ValueError, match="simulated site intelligence cannot be OBSERVED"):
        SiteObservation(
            location="Synthetic",
            latitude=0.0,
            longitude=0.0,
            temperature_mean_c=20.0,
            wind_speed_kmh=10.0,
            radiation_kwh_m2_day=5.0,
            source="SIMULATION",
            simulated=True,
            state="OBSERVED",
        )


def test_sourced_site_observation_remains_factual(monkeypatch) -> None:
    observed = SiteObservation(
        location="Observed",
        latitude=-8.0,
        longitude=-79.0,
        temperature_mean_c=22.0,
        wind_speed_kmh=12.0,
        radiation_kwh_m2_day=6.0,
        source="TEST_SOURCE",
        simulated=False,
        state="OBSERVED",
    )
    monkeypatch.setattr("sicl.cli.get_site_observation", lambda location: observed)
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE SITE-004 Site")

    result = cli.execute("/SITE INTELLIGENCE Observed")

    assert result["data"]["simulated"] is False
    assert result["data"]["state"] == "OBSERVED"
    project = repo.get_project("SITE-004")
    assert project is not None
    assert len(project.facts) == 3
    assert len(project.assumptions) == 0
    assert all("simulad" not in item.statement.lower() for item in project.facts.values())
