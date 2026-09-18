from sicl.design_intelligence import query_design_knowledge_for_intent
from sicl.semantic_reasoning import build_semantic_reasoning


def _intent():
    return {
        "project_id": "MS-001",
        "spatial_scope": "edificacion",
        "adopted_intents": [{
            "intent_id": "I-1",
            "kind": "OBJECTIVE",
            "statement": "priorizar privacidad, luz y circulación",
            "evidence_terms": ["privacidad", "luz", "circulación"],
        }],
    }


def test_multisource_contextual_retrieval_covers_five_families():
    result = query_design_knowledge_for_intent(_intent())
    source_ids = {link.get("source_id") for link in result["links"]}
    assert {
        "BOOK-ALEXANDER-PATTERN-LANGUAGE",
        "CASE-PREVI-LIMA-LAND",
        "BOOK-CHING-FORM-SPACE-ORDER",
        "BOOK-NEUFERT-ARCHITECTS-DATA",
        "BOOK-WHITE-SITE-ANALYSIS",
    }.issubset(source_ids)
    assert result["decision_created"] is False
    assert result["recommendation_created"] is False


def test_neufert_is_reference_only_and_no_regulatory_claim():
    result = query_design_knowledge_for_intent(_intent())
    neufert = [item for item in result["applicable_items"] if item["source_id"] == "BOOK-NEUFERT-ARCHITECTS-DATA"]
    assert neufert
    assert all(item["epistemic_status"] == "SOURCE_METADATA_ONLY" for item in neufert)
    assert all(item["conditions"]["regulatory_status"] == "NOT_REGULATORY" for item in neufert)


def test_semantic_reasoning_reports_complementary_families_not_consensus():
    knowledge = query_design_knowledge_for_intent(_intent())
    result = build_semantic_reasoning(_intent(), knowledge)
    families = {item["family"] for item in result["cross_source_contributions"]}
    assert {"PATTERN_RELATIONAL", "PRECEDENT_CASE", "FORM_SPACE_ORDER", "DIMENSIONAL_FUNCTIONAL", "SITE_ANALYSIS"}.issubset(families)
    assert all(item["relationship_type"] == "COMPLEMENTS" for item in result["cross_source_contributions"])
    assert result["decision_created"] is False
    assert result["human_confirmation_required"] is True
