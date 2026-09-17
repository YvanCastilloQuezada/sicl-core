from __future__ import annotations

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository
from sicl.design_principles import PRINCIPLES
from sicl.design_intelligence import controlled_exploration, query_design_knowledge_for_intent
from sicl.design_intent import confirm_intent, interpret_intent


def _adopted_intent():
    interpretation = interpret_intent("Quiero maximizar el espacio abierto con una masa compacta.", project_id="UPAO-001", spatial_scope="edificacion")
    adopted, _ = confirm_intent("UPAO-001", interpretation, [item["intent_id"] for item in interpretation["suggestions"]], "human-architect")
    return adopted


def test_adopted_intent_links_to_existing_design_knowledge():
    knowledge = query_design_knowledge_for_intent(_adopted_intent())
    assert knowledge["applicable_items"] or knowledge["applicable_patterns"]
    assert knowledge["links"]
    assert knowledge["decision_created"] is False
    assert all(link["knowledge_match"] for link in knowledge["links"])


def test_controlled_exploration_preserves_lineage_and_exposes_tradeoffs():
    adopted = _adopted_intent()
    knowledge = query_design_knowledge_for_intent(adopted)
    result = controlled_exploration("UPAO-001-A", adopted, knowledge)
    assert result["parent_alternative_id"] == "UPAO-001-A"
    assert result["derived_alternative"]["alternative_id"] != "UPAO-001-A"
    assert result["generation_operation"] == "CONTROLLED_PARAMETER_TRANSFORMATION"
    assert result["changed_parameters"]
    assert result["intent_linkage"]
    assert result["knowledge_linkage"]
    assert result["metrics"]["deltas"]
    assert result["decision_created"] is False


def test_human_review_and_decision_close_the_existing_loop(tmp_path):
    repo = SQLiteRepository(tmp_path / "div-p0.sqlite")
    try:
        cli = CLI(repo, actor="human-architect")
        assert cli.execute('/PROJECT CREATE DIV-P0-001 "DIV P0"')['code'] == "OK"
        assert cli.execute('/PROJECT OPEN DIV-P0-001')['code'] == "OK"
        review = cli.execute('/HUMAN REVIEW human-architect 2026-09-17T12:00:00Z "ACCEPT FOR FURTHER DEVELOPMENT" "UPAO-001-D reviewed against intent" project_owner')
        assert review['code'] == "OK"
        decision = cli.execute('/DECISION RECORD "UPAO-001-D accepted for further development" human-architect project_owner')
        assert decision['code'] == "OK"
        assert repo.get_project("DIV-P0-001").decisions
        assert any(event.type == "HUMAN_REVIEW_RECORDED" for event in repo.events("DIV-P0-001"))
        assert any(event.type == "DECISION_RECORDED" for event in repo.events("DIV-P0-001"))
    finally:
        repo.close()


def configured_client(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "design.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return repo, TestClient(app)


def test_http_catalog_returns_fifteen_sourced_principles(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        response = client.get("/v1/design/principles")
        assert response.status_code == 200
        body = response.json()
        assert body["contract_version"] == "1.0"
        principles = body["data"]["principles"]
        assert len(principles) == 15
        assert all(item["source"] != "PENDING_REFERENCE" for item in principles)
        assert all(item["source"] for item in principles)
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_http_get_single_principle_and_not_found(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        response = client.get("/v1/design/principles/P-01")
        missing = client.get("/v1/design/principles/P-99")
        assert response.status_code == 200
        assert response.json()["data"]["principle"]["category"] == "PROPORCION"
        assert missing.status_code == 404
        assert missing.json()["detail"]["code"] == "PRINCIPLE_NOT_FOUND"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_http_category_filter_is_read_only(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        response = client.get("/v1/design/principles?category=LUZ")
        assert response.status_code == 200
        principles = response.json()["data"]["principles"]
        assert len(principles) == 1
        assert principles[0]["principle_id"] == "P-09"
        assert response.json()["project_id"] is None
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_cli_design_commands_are_read_only(tmp_path):
    repo = SQLiteRepository(tmp_path / "cli.sqlite")
    try:
        cli = CLI(repo)
        listed = cli.execute("/DESIGN PRINCIPLES")
        single = cli.execute("/DESIGN PRINCIPLE P-12")
        missing = cli.execute("/DESIGN PRINCIPLE P-99")
        assert len(listed["data"]["principles"]) == 15
        assert single["data"]["principle"]["name"] == "Lleno-vacío"
        assert missing["code"] == "PRINCIPLE_NOT_FOUND"
        assert repo.list_projects() == []
        assert repo.events() == []
    finally:
        repo.close()


def test_catalog_has_expected_ids_categories_and_sources():
    assert [item.principle_id for item in PRINCIPLES] == [f"P-{index:02d}" for index in range(1, 16)]
    assert all(item.category.value for item in PRINCIPLES)
    assert all(item.source != "PENDING_REFERENCE" for item in PRINCIPLES)


def test_design_principles_do_not_create_decision_or_recommendation(tmp_path):
    repo = SQLiteRepository(tmp_path / "invariants.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-DESIGN "Design"')
        before = len(repo.events("P-DESIGN"))
        cli.execute("/DESIGN PRINCIPLES")
        cli.execute("/DESIGN PRINCIPLE P-01")
        project = repo.get_project("P-DESIGN")
        assert project.decisions == {}
        assert project.recommendations == {}
        assert len(repo.events("P-DESIGN")) == before
    finally:
        repo.close()
