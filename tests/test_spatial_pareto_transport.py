from __future__ import annotations

import os

from fastapi.testclient import TestClient

from api.main import create_app
from sicl.spatial_evaluation import build_upao001_dataset
from sicl.spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"}


def test_upao001_pareto_transport_matches_canonical_runtime_dataset() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/examples/UPAO-001/pareto", headers=_headers())
    assert response.status_code == 200
    data = response.json()["data"]

    representations = [
        UPAO001SpatialGenerator().generate(item)
        for item in generate_upao001_alternatives()
    ]
    dataset = build_upao001_dataset(representations)
    expected_values = {
        (item.alternative_id, item.objective_id): item.value
        for item in dataset.evaluations
    }
    expected_status = {
        item: "NON_DOMINATED" for item in dataset.pareto.non_dominated
    }
    expected_status.update({item: "DOMINATED" for item in dataset.pareto.dominated})
    expected_status.update({item: "INCOMPLETE" for item in dataset.pareto.incomplete})

    assert data["example_id"] == "UPAO-001"
    assert data["read_only"] is True
    assert data["feasible_pareto_used"] is False
    assert data["decision_created"] is False
    assert data["recommendation_created"] is False
    assert data["human_review_created"] is False
    assert data["provenance"] == ["SYNTHETIC", "DETERMINISTIC_DERIVED", "EDUCATIONAL"]
    assert data["objectives"] == ["GROSS_MASSING_AREA", "OPEN_SITE_AREA"]
    assert len(data["alternatives"]) == 3
    assert {item["alternative_id"] for item in data["alternatives"]} == {
        "UPAO-001-A", "UPAO-001-B", "UPAO-001-C"
    }
    assert all("ALT-1" not in item["alternative_id"] for item in data["alternatives"])
    assert all("ALT-A" not in item["alternative_id"] for item in data["alternatives"])

    for item in data["alternatives"]:
        alternative_id = item["alternative_id"]
        assert item["gross_massing_area_unit"] == "m²"
        assert item["open_site_area_unit"] == "m²"
        assert item["gross_massing_area"] == expected_values[(alternative_id, "OBJ-GROSS-MASSING-AREA")]
        assert item["open_site_area"] == expected_values[(alternative_id, "OBJ-OPEN-SITE-AREA")]
        assert item["raw_pareto_status"] == expected_status[alternative_id]


def test_upao001_pareto_transport_rejects_unsupported_example() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/examples/OTHER/pareto", headers=_headers())
    assert response.status_code == 404
    assert "EXAMPLE_NOT_FOUND" in str(response.json())


def test_upao001_pareto_transport_is_read_only_and_does_not_persist() -> None:
    client = TestClient(create_app())
    first = client.get("/v1/examples/UPAO-001/pareto", headers=_headers())
    second = client.get("/v1/examples/UPAO-001/pareto", headers=_headers())
    assert first.status_code == second.status_code == 200
    assert first.json()["data"] == second.json()["data"]
    assert "multiobjectives" not in first.json()["data"]
    assert "evaluations_persisted" in first.json()["data"]
    assert first.json()["data"]["evaluations_persisted"] is False


def test_no_generic_project_pareto_route_is_replaced() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/v1/projects/UNKNOWN/multiobjective/pareto",
        json={"objectives": ["GROSS_MASSING_AREA", "OPEN_SITE_AREA"]},
        headers=_headers(),
    )
    assert response.status_code in {400, 404}
    assert "EXAMPLE_NOT_FOUND" not in str(response.json())


def test_upao001_pareto_transport_has_no_decision_side_effects() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/examples/UPAO-001/pareto", headers=_headers())
    data = response.json()["data"]
    assert data["decision_created"] is False
    assert data["recommendation_created"] is False
    assert data["human_review_created"] is False
    assert data["feasible_pareto_used"] is False


__all__ = []
