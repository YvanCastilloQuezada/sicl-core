from sicl.design_intelligence import query_design_knowledge_for_intent
from sicl.design_knowledge import LicenseStatus, ReviewStatus, DesignKnowledgeAgent, DesignKnowledgeQuery, list_items, list_sources
from sicl.domain import SpatialScope


def test_alexander_ces_sources_are_metadata_verified_and_rights_conservative():
    sources = {item["source_id"]: item for item in list_sources()}
    expected = {
        "BOOK-ALEXANDER-TIMELESS-WAY",
        "BOOK-ALEXANDER-PATTERN-LANGUAGE",
        "BOOK-ALEXANDER-OREGON-EXPERIMENT",
        "CASE-PREVI-LIMA-LAND",
        "CASE-HOUSES-GENERATED-BY-PATTERNS",
    }
    assert expected.issubset(sources)
    for source_id in expected:
        source = sources[source_id]
        assert source["review_status"] == ReviewStatus.BIBLIOGRAPHICALLY_VERIFIED.value
        assert source["license_status"] == LicenseStatus.LICENSE_REVIEW_REQUIRED.value
        assert source["url"]


def test_pilot_items_preserve_scales_and_are_not_requirements():
    items = list_items(SpatialScope.EDIFICACION)
    pilot = [item for item in items if item["source_id"] != "BOOK-CHING-FORM-SPACE-ORDER"]
    assert pilot
    assert all(item["authority_level"] in {"THEORETICAL", "EXPERIENTIAL"} for item in pilot)
    assert all(item["item_type"] != "REGULATORY_RULE" for item in pilot)
    assert all("norm" not in item["statement"].casefold() or item["authority_level"] != "LEGAL" for item in pilot)


def test_contextual_match_preserves_source_traceability_and_no_decision():
    result = query_design_knowledge_for_intent({
        "project_id": "UPAO-001",
        "spatial_scope": "edificacion",
        "adopted_intents": [{"intent_id": "I-1", "kind": "PREFERENCE", "statement": "quiero privacidad y espacio común", "evidence_terms": ["privacidad", "espacio"]}],
    })
    assert result["sources"]
    assert any(source["source_id"] == "BOOK-ALEXANDER-PATTERN-LANGUAGE" for source in result["sources"])
    assert result["decision_created"] is False
    assert result["recommendation_created"] is False
    assert all(link["knowledge_match"] for link in result["links"])


def test_knowledge_match_does_not_create_intent_or_hard_constraint():
    result = DesignKnowledgeAgent().query(DesignKnowledgeQuery(spatial_scope=SpatialScope.EDIFICACION, problem_terms=["privacidad"]))
    assert result.decision_created is False
    assert result.review_state == "HUMAN_REVIEW_REQUIRED"
    assert all("constraint" not in item.get("outputs", []) for item in result.applicable_items)
