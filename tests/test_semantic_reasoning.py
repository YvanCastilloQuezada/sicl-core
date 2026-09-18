from sicl.design_intelligence import query_design_knowledge_for_intent
from sicl.design_intent import confirm_intent, interpret_intent
from sicl.semantic_reasoning import build_semantic_reasoning


def adopted_intent():
    interpretation = interpret_intent("Quiero privacidad y espacio común abierto.", project_id="UPAO-001", spatial_scope="edificacion")
    adopted, _ = confirm_intent("UPAO-001", interpretation, [item["intent_id"] for item in interpretation["suggestions"]], "human-architect")
    return adopted


def test_reasoning_primitives_preserve_epistemic_boundaries():
    intent = adopted_intent()
    knowledge = query_design_knowledge_for_intent(intent)
    result = build_semantic_reasoning(intent, knowledge)
    assert len(result["forces"]) >= 2
    assert result["tensions"]
    assert len(result["hypotheses"]) == 3
    assert all(item["status"] == "PROVISIONAL" for item in result["hypotheses"])
    assert result["decision_created"] is False
    assert result["recommendation_created"] is False
    assert all(item["epistemic_status"] in {"HUMAN_STATED", "SOURCE_DERIVED", "REQUIRES_EVIDENCE"} for item in result["forces"])


def test_reasoning_does_not_require_or_create_geometry():
    result = build_semantic_reasoning(adopted_intent(), {}, None)
    assert result["spatial_relationships"]
    assert all(item["provenance"] for item in result["spatial_relationships"])
    assert all("winner" not in item["statement"].lower() for item in result["hypotheses"])


def test_unconfirmed_intent_is_rejected_by_the_api_boundary(monkeypatch):
    from fastapi.testclient import TestClient
    from api.main import app

    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    client = TestClient(app)
    response = client.post("/v1/projects/UPAO-001/gdi/semantic-reasoning", json={"payload": {"adopted_intent": {"adoption": "SUGGESTED"}}})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "HUMAN_CONFIRMATION_REQUIRED"
