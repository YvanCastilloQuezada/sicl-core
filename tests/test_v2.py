from __future__ import annotations

from sicl.agents import BioclimaticAgent
from sicl.cli import CLI
from sicl.domain import Objective, Project
from sicl.optimization import pareto_front
from sicl.repository import SQLiteRepository
from sicl.site_intelligence import fetch_open_meteo
from sicl.v11 import Alternative, Evaluation


def test_open_meteo_adapter_parses_geocoding_and_weather(monkeypatch):
    responses = iter([
        {"results": [{"latitude": -8.11, "longitude": -79.03}]},
        {"daily": {"temperature_2m_mean": [20, 22], "wind_speed_10m_max": [10, 20], "shortwave_radiation_sum": [5, 6]}},
    ])
    monkeypatch.setattr("sicl.site_intelligence._get_json", lambda url, timeout: next(responses))
    observation = fetch_open_meteo("Trujillo, Peru")
    assert observation.source == "OPEN_METEO_API"
    assert observation.latitude == -8.11
    assert observation.temperature_mean_c == 21.0
    assert observation.radiation_kwh_m2_day == 5.5


def test_site_intelligence_uses_open_meteo_when_available(monkeypatch):
    from sicl.site_intelligence import SiteObservation
    monkeypatch.setattr("sicl.cli.get_site_observation", lambda location: SiteObservation(location, 1, 2, 23, 12, 5, "OPEN_METEO_API"))
    cli = CLI(SQLiteRepository())
    cli.execute("/PROJECT CREATE API-001 API")
    result = cli.execute("/SITE INTELLIGENCE Trujillo")
    assert result["code"] == "OK"
    assert result["data"]["source"] == "OPEN_METEO_API"
    assert result["data"]["simulated"] is False


def test_site_intelligence_fallback_when_network_fails(monkeypatch):
    monkeypatch.setattr("sicl.site_intelligence.fetch_open_meteo", lambda location, timeout=5: (_ for _ in ()).throw(OSError("offline")))
    from sicl.site_intelligence import get_site_observation
    observation = get_site_observation("Trujillo")
    assert observation.simulated is True
    assert observation.source == "SITE_INTELLIGENCE_FIXTURE"


def test_bioclimatic_agent_penalizes_simple_glass():
    project = Project("P", "Project")
    project.objectives["O"] = Objective("O", "P", "ENERGY_SAVINGS", "MAXIMIZE", "80")
    project.facts["F"] = type("Fact", (), {"statement": "Temperatura cálida 24 C"})()
    alternative = Alternative("A", "P", "A", parameters={"facade": "vidrio simple"})
    evaluation = BioclimaticAgent().evaluate(alternative, project)
    assert evaluation.value == 64.0
    assert evaluation.source == "EXPERT_SYSTEM"


def test_bioclimatic_agent_adds_orientation_bonus():
    project = Project("P", "Project")
    project.objectives["O"] = Objective("O", "P", "ENERGY_SAVINGS", "MAXIMIZE", "80")
    project.facts["F"] = type("Fact", (), {"statement": "Temperatura cálida"})()
    alternative = Alternative("A", "P", "A", parameters={"orientation": "norte"})
    assert BioclimaticAgent().evaluate(alternative, project).value == 85.0


def test_bioclimatic_agent_requires_energy_objective():
    project = Project("P", "Project")
    try:
        BioclimaticAgent().evaluate(Alternative("A", "P", "A"), project)
    except ValueError as error:
        assert "ENERGY_SAVINGS" in str(error)
    else:
        raise AssertionError("expected missing objective error")


def test_pareto_front_finds_non_dominated_alternatives():
    objectives = [Objective("comfort", "P", "COMFORT", "MAXIMIZE", "0"), Objective("cost", "P", "COST", "MINIMIZE", "0")]
    alternatives = [Alternative("A", "P", "A"), Alternative("B", "P", "B"), Alternative("C", "P", "C")]
    evaluations = [Evaluation("a1", "A", "comfort", 90), Evaluation("a2", "A", "cost", 100), Evaluation("b1", "B", "comfort", 80), Evaluation("b2", "B", "cost", 80), Evaluation("c1", "C", "comfort", 70), Evaluation("c2", "C", "cost", 120)]
    result = pareto_front(alternatives, evaluations, objectives)
    assert set(result.non_dominated) == {"A", "B"}
    assert result.dominated == {"C": "A"}


def test_pareto_front_marks_incomplete_data():
    objectives = [Objective("o1", "P", "A", "MAXIMIZE", "0"), Objective("o2", "P", "B", "MINIMIZE", "0")]
    result = pareto_front([Alternative("A", "P", "A")], [Evaluation("e", "A", "o1", 1)], objectives)
    assert result.incomplete == ["A"]
    assert result.non_dominated == []


def test_cli_agent_records_evaluation_without_decision():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE AG-001 Agent")
    cli.execute("/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80")
    cli.execute("/FACT SET Temperatura calida API")
    cli.execute("/ALTERNATIVE CREATE ALT-A")
    result = cli.execute("/AGENT RUN BIOCLIMATIC ALT-A")
    assert result["code"] == "OK"
    assert result["data"]["decision_created"] is False
    assert cli.execute("/STATUS")["data"]["decisions"] == {}


def test_cli_pareto_is_read_only():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE PA-001 Pareto")
    cli.execute("/OBJECTIVE SET COMFORT MAXIMIZE 80")
    cli.execute("/OBJECTIVE SET COST MINIMIZE 100")
    cli.execute("/ALTERNATIVE CREATE A")
    cli.execute("/ALTERNATIVE CREATE B")
    cli.execute("/EVALUATE A COMFORT 90")
    cli.execute("/EVALUATE A COST 100")
    cli.execute("/EVALUATE B COMFORT 80")
    cli.execute("/EVALUATE B COST 80")
    before = len(repo.events("PA-001"))
    result = cli.execute("/PARETO COMFORT COST")
    assert result["code"] == "OK"
    assert result["data"]["decision_created"] is False
    assert len(repo.events("PA-001")) == before
