from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.archi import ArchiElementId, ElementKind, GeometryKind
from sicl.repository import SQLiteRepository


@pytest.fixture(autouse=True)
def clear_service_token(monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)


PROJECT_ID = "ARK-DEV-001-001"
PROPOSAL_ID = "dev-prop-microcase-001"
FINGERPRINT = "d" * 64


def _client(repo: SQLiteRepository) -> TestClient:
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app)


def _proposal() -> dict:
    def space(provisional_id: str, width_mm: int, depth_mm: int, x_mm: int) -> dict:
        return {
            "provisionalId": provisional_id,
            "kind": "SPACE",
            "geometry": {
                "kind": "EXTRUDED_RECTANGLE",
                "profile": {
                    "width_mm": width_mm,
                    "depth_mm": depth_mm,
                    "radius_mm": None,
                },
                "x_mm": x_mm,
                "y_mm": 0,
                "z_mm": 0,
                "height_mm": 3000,
            },
            "properties": {},
            "provenance": [{"source": "MICROCASE-DEV-001", "ref": provisional_id}],
            "epistemicStatus": "HYPOTHESIS",
        }

    return {
        "proposalId": PROPOSAL_ID,
        "parentProposalId": None,
        "sourceExecutionId": "microcase-d63-execution",
        "sourceD63": "MICROCASE-D63-001",
        "fingerprint": FINGERPRINT,
        "epistemicStatus": "PROPOSAL",
        "proposedElements": [
            space("SPACE-1", 5000, 10000, 0),
            space("SPACE-2", 1500, 2000, 5000),
        ],
        "proposedRelations": [],
        "proposedDerivations": [],
        "unresolvedUnknowns": [],
        "requiredHumanActions": [{"action": "review", "reason": "E2E verification"}],
        "provenance": [{"source": "MICROCASE-DEV-001", "ref": "explicit-fixture"}],
        "reviewRequired": True,
        "mutation": None,
        "rejectedBecause": None,
        "feedbackLoops": [],
    }


def _record_proposal(client: TestClient) -> None:
    response = client.post(
        f"/v1/projects/{PROJECT_ID}/reasoning-executions",
        json={
            "execution_id": PROPOSAL_ID,
            "kind": "DEVELOPER_PROPOSAL",
            "fingerprint": FINGERPRINT,
            "input_fingerprint": None,
            "payload": _proposal(),
            "epistemic_status": "PROPOSAL",
            "human_authority_ref": None,
            "source_refs": [],
            "actor": "ARKI_DEVELOPER",
            "created_at": "2026-09-29T12:00:00Z",
        },
    )
    assert response.status_code == 200


def _approve(client: TestClient) -> str:
    response = client.post(
        f"/v1/projects/{PROJECT_ID}/human-reviews",
        json={
            "actor": "architect",
            "timestamp": "2026-09-29T12:01:00Z",
            "review": "MICROCASE-DEV-001 approved",
            "reason": "Controlled E2E verification",
            "authority": "PRODUCT_OWNER",
            "referenced_entity_type": "DEVELOPER_PROPOSAL",
            "referenced_entity_id": PROPOSAL_ID,
            "referenced_fingerprint": FINGERPRINT,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["human_review"]["review_id"]


def _promotion_body(review_id: str, fingerprint: str = FINGERPRINT) -> dict:
    return {
        "proposal_id": PROPOSAL_ID,
        "proposal_fingerprint": fingerprint,
        "human_review_id": review_id,
    }


def test_microcase_dev_001_full_promotion_chain_and_restart(tmp_path: Path):
    db_path = tmp_path / "microcase-dev-001.sqlite"
    repo = SQLiteRepository(db_path, check_same_thread=False)
    client = _client(repo)

    created = client.post(
        "/v1/projects",
        json={"project_id": PROJECT_ID, "name": "MICROCASE-DEV-001"},
    )
    assert created.status_code == 200
    _record_proposal(client)
    review_id = _approve(client)
    project_version_before_promotion = repo.get_project(PROJECT_ID).version

    first = client.post(
        f"/v1/projects/{PROJECT_ID}/developer-promotions",
        json=_promotion_body(review_id),
    )
    assert first.status_code == 200
    first_data = first.json()["data"]
    assert first_data["status"] == "COMMITTED"
    assert first_data["snapshot_id"]
    assert first_data["d2_version"] == 1
    assert first_data["effects_status"] in {"COMPLETE", "PARTIAL"}
    assert first.json()["observed_version"] == project_version_before_promotion
    assert repo.get_project(PROJECT_ID).version == project_version_before_promotion

    d2 = repo.get_d2(PROJECT_ID)
    assert d2 is not None
    assert len(d2) == 2
    by_id = {element.element_id: element for element in d2}
    expected_1 = ArchiElementId.compute(PROJECT_ID, "SPACE", "SPACE-1")
    expected_2 = ArchiElementId.compute(PROJECT_ID, "SPACE", "SPACE-2")
    assert set(by_id) == {expected_1, expected_2}

    first_space = by_id[expected_1]
    assert first_space.kind is ElementKind.SPACE
    assert first_space.geometry.kind is GeometryKind.EXTRUDED_RECTANGLE
    assert first_space.geometry.profile.width_mm == 5000
    assert first_space.geometry.profile.depth_mm == 10000
    assert first_space.geometry.x_mm == 0
    assert first_space.geometry.y_mm == 0
    assert first_space.geometry.z_mm == 0
    assert first_space.geometry.height_mm == 3000
    assert first_space.version == 1
    assert first_space.hosted_in is None
    assert first_space.contained_in is None

    second_space = by_id[expected_2]
    assert second_space.geometry.profile.width_mm == 1500
    assert second_space.geometry.profile.depth_mm == 2000
    assert second_space.geometry.x_mm == 5000
    assert second_space.geometry.height_mm == 3000
    assert second_space.version == 1
    assert second_space.hosted_in is None
    assert second_space.contained_in is None

    events = repo.events(PROJECT_ID)
    reasoning = [
        event for event in events
        if event.type == "REASONING_EXECUTION_RECORDED"
        and event.payload.get("execution", {}).get("kind") == "DEVELOPER_PROPOSAL"
    ]
    committed = [event for event in events if event.type == "DEVELOPER_PROMOTION_COMMITTED"]
    assert len(reasoning) == 1
    assert len(committed) == 1
    assert committed[0].payload["snapshot_id"] == first_data["snapshot_id"]
    assert not [event for event in events if event.type == "DEVELOPER_PROMOTION_REJECTED"]
    assert not [event for event in events if event.type == "D2_EFFECTS_FAILED"]

    wrong_fingerprint = client.post(
        f"/v1/projects/{PROJECT_ID}/developer-promotions",
        json=_promotion_body(review_id, "e" * 64),
    )
    assert wrong_fingerprint.status_code == 409
    assert repo.get_d2(PROJECT_ID) == d2

    missing_review = client.post(
        f"/v1/projects/{PROJECT_ID}/developer-promotions",
        json=_promotion_body("REV-MISSING"),
    )
    assert missing_review.status_code == 404
    assert repo.get_d2(PROJECT_ID) == d2

    repo.close()
    app.dependency_overrides.clear()

    reopened = SQLiteRepository(db_path, check_same_thread=False)
    restarted_client = _client(reopened)
    restored = reopened.get_d2(PROJECT_ID)
    assert restored == d2

    replay = restarted_client.post(
        f"/v1/projects/{PROJECT_ID}/developer-promotions",
        json=_promotion_body(review_id),
    )
    assert replay.status_code == 200
    replay_data = replay.json()["data"]
    assert replay_data["snapshot_id"] == first_data["snapshot_id"]
    assert replay_data["d2_version"] == first_data["d2_version"]
    assert replay_data["effects_status"] == "NOT_ATTEMPTED"
    assert replay_data["reason"] == "ALREADY_COMMITTED"
    assert reopened.get_project(PROJECT_ID).version == project_version_before_promotion
    assert len([
        event for event in reopened.events(PROJECT_ID)
        if event.type == "DEVELOPER_PROMOTION_COMMITTED"
    ]) == 1

    reopened.close()
    app.dependency_overrides.clear()
