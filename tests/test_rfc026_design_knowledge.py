from __future__ import annotations

from sicl.design_knowledge import (
    AgentStatus,
    AuthorityLevel,
    DesignKnowledgeAgent,
    DesignKnowledgeItem,
    DesignKnowledgeQuery,
    DesignKnowledgeSource,
    DesignPattern,
    KnowledgeItemType,
    LicenseStatus,
    ReviewStatus,
    SourceClass,
    list_items,
    list_patterns,
    list_sources,
)
from sicl.domain import SpatialScope


def test_catalog_has_sources_items_patterns_and_all_scales() -> None:
    assert len(list_sources()) >= 3
    assert list_items(SpatialScope.EDIFICACION)
    assert list_patterns(SpatialScope.ESPACIO)
    assert {scope.value for scope in SpatialScope} == {
        "pais", "macro_region", "region", "provincia_metropoli", "distrito_ciudad",
        "zona_barrio_sector", "parcela_sitio", "edificacion", "sistema", "espacio", "objeto",
    }


def test_entities_require_provenance_and_applicable_scale() -> None:
    source = DesignKnowledgeSource("S-1", "Test source", ["Reviewer"], SourceClass.THEORETICAL, "BOOK", "es", license_status=LicenseStatus.USER_AUTHORIZED, review_status=ReviewStatus.APPROVED)
    assert source.source_id == "S-1"
    item = DesignKnowledgeItem("I-1", "S-1", KnowledgeItemType.DESIGN_PRINCIPLE, "Test", "A test principle", "THEORY", AuthorityLevel.THEORETICAL, [SpatialScope.ESPACIO])
    assert item.source_id == source.source_id
    pattern = DesignPattern("P-1", ["S-1"], "Test pattern", {"question": "?"}, ["context"], ["force"], {"steps": []}, {"positive": []}, [SpatialScope.ESPACIO])
    assert pattern.source_ids == [source.source_id]


def test_agent_keeps_heuristic_and_rne_separate() -> None:
    agent = DesignKnowledgeAgent([{"code": "E.030", "status": "NO_VERIFICADA"}])
    result = agent.query(DesignKnowledgeQuery(spatial_scope=SpatialScope.EDIFICACION, objectives=["privacidad"], problem_terms=["público"]))
    assert result.status is AgentStatus.CONFLICTING
    assert result.decision_created is False
    assert result.review_state == "HUMAN_REVIEW_REQUIRED"
    assert result.normative_references[0]["use"] == "reference_only"
    assert any(item["authority_level"] == "THEORETICAL" for item in result.applicable_items)
    assert any(item["source_id"].startswith("BOOK-") for item in result.applicable_items)
    assert result.conflicts[0]["type"] == "NORMATIVE_STATUS"


def test_agent_rejects_empty_context_without_inference() -> None:
    result = DesignKnowledgeAgent().query(DesignKnowledgeQuery())
    assert result.status is AgentStatus.INSUFFICIENT_CONTEXT
    assert result.missing_inputs == ["spatial_scope or problem_terms or objectives"]
    assert result.decision_created is False


def test_http_catalog_and_query_endpoints() -> None:
    import os
    from fastapi.testclient import TestClient
    from api.main import create_app

    client = TestClient(create_app())
    headers = {"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"}
    catalog = client.get("/v1/design-knowledge/catalog?scope=edificacion", headers=headers)
    assert catalog.status_code == 200
    assert len(catalog.json()["data"]["scales"]) == 11
    assert catalog.json()["data"]["patterns"]
    response = client.post("/v1/design-knowledge/query", json={"spatial_scope": "edificacion", "problem_terms": ["público"]}, headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["decision_created"] is False
    assert body["review_state"] == "HUMAN_REVIEW_REQUIRED"
