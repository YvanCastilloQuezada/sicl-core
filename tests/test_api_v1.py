from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from api.routes.v1 import _status_for
from sicl.repository import SQLiteRepository
from sicl.archi import ArchiElement, ArchiElementId, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec


@pytest.fixture(autouse=True)
def clear_service_token(monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)


def client_for(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "v1.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app), repo


def close(repo: SQLiteRepository) -> None:
    repo.close()
    app.dependency_overrides.clear()


def test_v1_health_and_envelope(tmp_path: Path):
    client, repo = client_for(tmp_path)
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"contract_version": "1.0", "status": "OK", "service": "sicl-core-api"}
    close(repo)


def test_v1_project_snapshot_and_history(tmp_path: Path):
    client, repo = client_for(tmp_path)
    created = client.post("/v1/projects", json={"project_id": "V1-P", "name": "Canonical"})
    assert created.status_code == 200
    body = created.json()
    assert body["contract_version"] == "1.0"
    assert body["project_id"] == "V1-P"
    assert body["observed_version"] == 1
    snapshot = client.get("/v1/projects/V1-P/snapshot").json()
    assert snapshot["data"]["snapshot"]["project_id"] == "V1-P"
    history = client.get("/v1/projects/V1-P/history").json()
    assert len(history["data"]["events"]) == 1
    close(repo)


def test_v1_project_scoped_command_has_observed_version(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-C", "name": "Command"})
    response = client.post("/v1/projects/V1-C/commands", json={"command": "/OBJECTIVE SET CLIMATE MAXIMIZE 80", "actor": "architect"})
    assert response.status_code == 200
    assert response.json()["observed_version"] == 2
    assert response.json()["data"]["key"] == "CLIMATE"
    close(repo)


def test_v1_preference_is_separate_and_emits_event(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-PREF", "name": "Preference"})
    response = client.post("/v1/projects/V1-PREF/preferences", json={"statement": "Prefer low operational energy", "actor": "owner"})
    assert response.status_code == 200
    preference = response.json()["data"]["preference"]
    assert preference["statement"] == "Prefer low operational energy"
    assert "preferences" in response.json()["data"] or preference["preference_id"].startswith("PREF-")
    events = client.get("/v1/projects/V1-PREF/history").json()["data"]["events"]
    assert events[-1]["type"] == "PREFERENCE_RECORDED"
    close(repo)


def test_v1_human_review_then_decision(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-D", "name": "Decision"})
    review = client.post("/v1/projects/V1-D/human-reviews", json={"actor": "Yvan", "timestamp": "2026-09-15T20:00:00Z", "review": "Reviewed recommendation", "reason": "Architecture review", "authority": "PRODUCT_OWNER"})
    assert review.status_code == 200
    decision = client.post("/v1/projects/V1-D/decisions", json={"statement": "Proceed", "actor": "Yvan", "authority": "PRODUCT_OWNER"})
    assert decision.status_code == 200
    assert decision.json()["data"]["decision"]["actor"] == "Yvan"
    close(repo)


def test_v1_decision_without_review_is_semantic_error(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-NO-REVIEW", "name": "Decision"})
    response = client.post("/v1/projects/V1-NO-REVIEW/decisions", json={"statement": "Proceed", "actor": "Yvan", "authority": "PRODUCT_OWNER"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "HUMAN_REVIEW_REQUIRED"
    close(repo)


def test_v1_read_only_debate_does_not_create_decision(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-DEBATE", "name": "Debate"})
    client.post("/v1/projects/V1-DEBATE/commands", json={"command": "/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80"})
    alternative = client.post("/v1/projects/V1-DEBATE/commands", json={"command": "/ALTERNATIVE CREATE CONVENCIONAL_A"}).json()["data"]["alternative_id"]
    response = client.post("/v1/projects/V1-DEBATE/debate", json={"alternative_id": alternative})
    assert response.status_code == 200
    assert response.json()["data"]["decision_created"] is False
    close(repo)


def test_v1_auth_rejects_invalid_token(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "secret-for-test")
    client, repo = client_for(tmp_path)
    assert client.get("/v1/health").status_code == 401
    assert client.get("/v1/health", headers={"Authorization": "Bearer secret-for-test"}).status_code == 200
    close(repo)
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN")


def test_legacy_endpoints_remain_available(tmp_path: Path):
    client, repo = client_for(tmp_path)
    response = client.post("/projects", json={"project_id": "LEGACY", "name": "Legacy"})
    assert response.status_code == 201
    assert client.get("/projects/LEGACY").status_code == 200
    close(repo)


def _api_d2_element(project_id: str, nonce: str = "site") -> ArchiElement:
    return ArchiElement(
        ArchiElementId.compute(project_id, "SITE", nonce),
        project_id,
        ElementKind.SITE,
        ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE, ProfileSpec(1000, 1000), height_mm=1),
        {"name": "Site"},
        {"source": "api-test"},
    )


def test_v1_d2_without_snapshot_is_404(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-D2-EMPTY", "name": "D2"})
    response = client.get("/v1/projects/V1-D2-EMPTY/d2")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "D2_NOT_COMMITTED"
    close(repo)


def test_v1_d2_reads_current_history_and_specific_version(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-D2", "name": "D2"})
    first = repo.insert_d2_snapshot_and_event("V1-D2", (_api_d2_element("V1-D2", "one"),), "architect", "TEST")
    second = repo.insert_d2_snapshot_and_event("V1-D2", (_api_d2_element("V1-D2", "two"),), "architect", "TEST")

    current = client.get("/v1/projects/V1-D2/d2")
    assert current.status_code == 200
    assert current.json()["data"]["snapshot"]["version"] == 2
    assert current.json()["data"]["snapshot"]["snapshot_id"] == second.snapshot_id
    assert current.json()["observed_version"] == 1

    history = client.get("/v1/projects/V1-D2/d2/history")
    assert history.status_code == 200
    assert [item["version"] for item in history.json()["data"]["snapshots"]] == [1, 2]

    old = client.get("/v1/projects/V1-D2/d2/snapshots/1")
    assert old.status_code == 200
    assert old.json()["data"]["snapshot"]["snapshot_id"] == first.snapshot_id
    assert len(old.json()["data"]["snapshot"]["elements"]) == 1

    missing = client.get("/v1/projects/V1-D2/d2/snapshots/99")
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "D2_SNAPSHOT_NOT_FOUND"
    close(repo)


def test_v1_d2_has_no_public_write_endpoint(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-D2-NO-WRITE", "name": "D2"})
    response = client.post("/v1/projects/V1-D2-NO-WRITE/d2", json={"elements": []})
    assert response.status_code in {404, 405}
    assert repo.get_d2("V1-D2-NO-WRITE") is None
    close(repo)


def _record_developer_proposal(client, project_id: str, execution_id: str, fingerprint: str):
    return client.post(
        f"/v1/projects/{project_id}/reasoning-executions",
        json={
            "execution_id": execution_id,
            "kind": "DEVELOPER_PROPOSAL",
            "fingerprint": fingerprint,
            "input_fingerprint": None,
            "payload": {"proposal_id": execution_id},
            "epistemic_status": "PROPOSAL",
            "human_authority_ref": None,
            "source_refs": [],
            "actor": "ARKI_DEVELOPER",
            "created_at": "2026-09-29T12:00:00Z",
        },
    )


def test_v1_bound_human_review_round_trip_and_event(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-HRB", "name": "Review binding"})
    fingerprint = "a" * 64
    proposal = _record_developer_proposal(client, "V1-HRB", "dev-prop-1", fingerprint)
    assert proposal.status_code == 200

    review = client.post("/v1/projects/V1-HRB/human-reviews", json={
        "actor": "Yvan",
        "timestamp": "2026-09-29T12:01:00Z",
        "review": "Approved proposal",
        "reason": "Architecture review",
        "authority": "PRODUCT_OWNER",
        "referenced_entity_type": "DEVELOPER_PROPOSAL",
        "referenced_entity_id": "dev-prop-1",
        "referenced_fingerprint": fingerprint,
    })
    assert review.status_code == 200
    data = review.json()["data"]["human_review"]
    assert data["referenced_entity_type"] == "DEVELOPER_PROPOSAL"
    assert data["referenced_entity_id"] == "dev-prop-1"
    assert data["referenced_fingerprint"] == fingerprint

    hydrated = repo.get_project("V1-HRB").human_reviews[data["review_id"]]
    assert hydrated.referenced_entity_id == "dev-prop-1"
    event = next(item for item in repo.events("V1-HRB") if item.type == "HUMAN_REVIEW_RECORDED")
    assert event.payload["referenced_fingerprint"] == fingerprint
    close(repo)


def test_v1_bound_human_review_rejects_missing_proposal_without_persistence(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-HRB-MISSING", "name": "Review binding"})
    before = len(repo.events("V1-HRB-MISSING"))
    response = client.post("/v1/projects/V1-HRB-MISSING/human-reviews", json={
        "actor": "Yvan", "timestamp": "2026-09-29T12:01:00Z",
        "review": "Approved", "reason": "Review", "authority": "PRODUCT_OWNER",
        "referenced_entity_type": "DEVELOPER_PROPOSAL",
        "referenced_entity_id": "missing", "referenced_fingerprint": "a" * 64,
    })
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "REVIEW_TARGET_NOT_FOUND"
    assert repo.get_project("V1-HRB-MISSING").human_reviews == {}
    assert len(repo.events("V1-HRB-MISSING")) == before
    close(repo)


def test_v1_bound_human_review_rejects_fingerprint_mismatch_without_persistence(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-HRB-FP", "name": "Review binding"})
    assert _record_developer_proposal(client, "V1-HRB-FP", "dev-prop-2", "a" * 64).status_code == 200
    before = len(repo.events("V1-HRB-FP"))
    response = client.post("/v1/projects/V1-HRB-FP/human-reviews", json={
        "actor": "Yvan", "timestamp": "2026-09-29T12:01:00Z",
        "review": "Approved", "reason": "Review", "authority": "PRODUCT_OWNER",
        "referenced_entity_type": "DEVELOPER_PROPOSAL",
        "referenced_entity_id": "dev-prop-2", "referenced_fingerprint": "b" * 64,
    })
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "REVIEW_TARGET_FINGERPRINT_MISMATCH"
    assert repo.get_project("V1-HRB-FP").human_reviews == {}
    assert len(repo.events("V1-HRB-FP")) == before
    close(repo)


def test_v1_bound_human_review_rejects_partial_or_malformed_binding(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-HRB-BAD", "name": "Review binding"})
    common = {
        "actor": "Yvan", "timestamp": "2026-09-29T12:01:00Z",
        "review": "Approved", "reason": "Review", "authority": "PRODUCT_OWNER",
    }
    partial = client.post("/v1/projects/V1-HRB-BAD/human-reviews", json={
        **common, "referenced_entity_type": "DEVELOPER_PROPOSAL",
    })
    assert partial.status_code == 400
    malformed = client.post("/v1/projects/V1-HRB-BAD/human-reviews", json={
        **common,
        "referenced_entity_type": "DEVELOPER_PROPOSAL",
        "referenced_entity_id": "dev-prop",
        "referenced_fingerprint": "NOT-SHA256",
    })
    assert malformed.status_code == 400
    assert repo.get_project("V1-HRB-BAD").human_reviews == {}
    close(repo)


def test_v1_legacy_human_review_remains_valid_for_decision_after_binding_migration(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-HRB-LEGACY", "name": "Legacy"})
    review = client.post("/v1/projects/V1-HRB-LEGACY/human-reviews", json={
        "actor": "Yvan", "timestamp": "2026-09-29T12:00:00Z",
        "review": "Reviewed", "reason": "Legacy", "authority": "PRODUCT_OWNER",
    })
    assert review.status_code == 200
    data = review.json()["data"]["human_review"]
    assert data["referenced_entity_type"] is None
    decision = client.post("/v1/projects/V1-HRB-LEGACY/decisions", json={
        "statement": "Proceed", "actor": "Yvan", "authority": "PRODUCT_OWNER",
    })
    assert decision.status_code == 200
    close(repo)

PROMOTION_FP = "c" * 64


def _record_promotable_developer_proposal(client, project_id: str, proposal_id: str = "dev-promote-1"):
    payload = {
        "proposalId": proposal_id,
        "parentProposalId": None,
        "sourceExecutionId": "d63-exec",
        "sourceD63": "D63-A",
        "fingerprint": PROMOTION_FP,
        "epistemicStatus": "PROPOSAL",
        "proposedElements": [{
            "provisionalId": "space-1",
            "kind": "SPACE",
            "geometry": {
                "kind": "EXTRUDED_RECTANGLE",
                "profile": {"width_mm": 4000, "depth_mm": 3000, "radius_mm": None},
                "x_mm": 0,
                "y_mm": 0,
                "z_mm": 0,
                "height_mm": 2800,
            },
            "properties": {"name": "Space"},
            "provenance": [{"source": "test", "ref": "D63-A"}],
            "epistemicStatus": "HYPOTHESIS",
        }],
        "proposedRelations": [],
        "proposedDerivations": [],
        "unresolvedUnknowns": [],
        "requiredHumanActions": [{"action": "review", "reason": "required"}],
        "provenance": [{"source": "test", "ref": "proposal"}],
        "reviewRequired": True,
        "mutation": None,
        "rejectedBecause": None,
        "feedbackLoops": [],
    }
    response = client.post(
        f"/v1/projects/{project_id}/reasoning-executions",
        json={
            "execution_id": proposal_id,
            "kind": "DEVELOPER_PROPOSAL",
            "fingerprint": PROMOTION_FP,
            "input_fingerprint": None,
            "payload": payload,
            "epistemic_status": "PROPOSAL",
            "human_authority_ref": None,
            "source_refs": [],
            "actor": "ARKI_DEVELOPER",
            "created_at": "2026-09-29T12:00:00Z",
        },
    )
    assert response.status_code == 200


def _approve_promotable_developer_proposal(client, project_id: str, proposal_id: str = "dev-promote-1") -> str:
    response = client.post(
        f"/v1/projects/{project_id}/human-reviews",
        json={
            "actor": "architect",
            "timestamp": "2026-09-29T12:01:00Z",
            "review": "Approved proposal",
            "reason": "Architecture review",
            "authority": "PRODUCT_OWNER",
            "referenced_entity_type": "DEVELOPER_PROPOSAL",
            "referenced_entity_id": proposal_id,
            "referenced_fingerprint": PROMOTION_FP,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["human_review"]["review_id"]


def _promotion_body(review_id: str, proposal_id: str = "dev-promote-1") -> dict:
    return {
        "proposal_id": proposal_id,
        "proposal_fingerprint": PROMOTION_FP,
        "human_review_id": review_id,
    }


@pytest.mark.parametrize(
    "code,status",
    [
        ("PROJECT_NOT_FOUND", 404),
        ("PROPOSAL_NOT_FOUND", 404),
        ("HUMAN_REVIEW_NOT_FOUND", 404),
        ("PROPOSAL_FINGERPRINT_MISMATCH", 409),
        ("PROPOSAL_FINGERPRINT_INCONSISTENT", 409),
        ("HUMAN_REVIEW_BINDING_MISMATCH", 409),
        ("SUFFICIENCY_NOT_PERMITTED", 409),
        ("INVALID_DEVELOPER_PROPOSAL", 400),
        ("STRUCTURAL_VALIDATION_FAILED", 400),
        ("RELATIONS_NOT_YET_SUPPORTED", 400),
        ("DERIVATIONS_NOT_YET_SUPPORTED", 400),
        ("UNKNOWN_ELEMENT_KIND", 400),
        ("MISSING_GEOMETRY", 400),
        ("GEOMETRY_CONTRACT_NOT_MAPPED", 400),
        ("GEOMETRY_CONTRACT_NOT_MAPPED:x_mm", 400),
        ("UNSUPPORTED_PROPERTY_VALUE:d63_labels", 400),
        ("PROMOTION_PERSIST_FAILED", 500),
        ("PROMOTION_FAILED", 500),
    ],
)
def test_v1_developer_promotion_status_mapping(code, status):
    assert _status_for(code) == status


def test_v1_developer_promotion_commits_d2_without_advancing_project_version(tmp_path: Path):
    client, repo = client_for(tmp_path)
    project_id = "V1-PROMOTE"
    client.post("/v1/projects", json={"project_id": project_id, "name": "Promotion"})
    _record_promotable_developer_proposal(client, project_id)
    review_id = _approve_promotable_developer_proposal(client, project_id)
    before = repo.get_project(project_id).version

    response = client.post(
        f"/v1/projects/{project_id}/developer-promotions",
        json=_promotion_body(review_id),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["observed_version"] == before
    assert body["data"]["status"] == "COMMITTED"
    assert body["data"]["proposal_id"] == "dev-promote-1"
    assert body["data"]["d2_version"] == 1
    assert body["data"]["effects_status"] == "COMPLETE"
    assert repo.get_project(project_id).version == before
    assert repo.get_d2(project_id) is not None
    close(repo)


def test_v1_developer_promotion_is_idempotent_over_http(tmp_path: Path):
    client, repo = client_for(tmp_path)
    project_id = "V1-PROMOTE-IDEMP"
    client.post("/v1/projects", json={"project_id": project_id, "name": "Promotion"})
    _record_promotable_developer_proposal(client, project_id)
    review_id = _approve_promotable_developer_proposal(client, project_id)
    body = _promotion_body(review_id)

    first = client.post(f"/v1/projects/{project_id}/developer-promotions", json=body)
    second = client.post(f"/v1/projects/{project_id}/developer-promotions", json=body)

    assert first.status_code == second.status_code == 200
    assert second.json()["data"]["snapshot_id"] == first.json()["data"]["snapshot_id"]
    assert second.json()["data"]["d2_version"] == first.json()["data"]["d2_version"]
    assert second.json()["data"]["effects_status"] == "NOT_ATTEMPTED"
    assert second.json()["data"]["reason"] == "ALREADY_COMMITTED"
    assert len([e for e in repo.events(project_id) if e.type == "DEVELOPER_PROMOTION_COMMITTED"]) == 1
    close(repo)


def test_v1_developer_promotion_restart_durability(tmp_path: Path):
    db_path = tmp_path / "promotion-restart.sqlite"
    repo = SQLiteRepository(db_path, check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    project_id = "V1-PROMOTE-RESTART"
    client.post("/v1/projects", json={"project_id": project_id, "name": "Promotion"})
    _record_promotable_developer_proposal(client, project_id)
    review_id = _approve_promotable_developer_proposal(client, project_id)
    request = _promotion_body(review_id)
    first = client.post(f"/v1/projects/{project_id}/developer-promotions", json=request)
    assert first.status_code == 200
    snapshot_id = first.json()["data"]["snapshot_id"]
    observed_version = first.json()["observed_version"]
    repo.close()

    reopened = SQLiteRepository(db_path, check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: reopened
    restarted_client = TestClient(app)
    replay = restarted_client.post(
        f"/v1/projects/{project_id}/developer-promotions",
        json=request,
    )

    assert replay.status_code == 200
    assert replay.json()["data"]["snapshot_id"] == snapshot_id
    assert replay.json()["data"]["d2_version"] == 1
    assert replay.json()["data"]["effects_status"] == "NOT_ATTEMPTED"
    assert replay.json()["observed_version"] == observed_version
    assert reopened.get_d2(project_id) is not None
    close(reopened)


def test_v1_developer_promotion_rejection_uses_error_envelope(tmp_path: Path):
    client, repo = client_for(tmp_path)
    project_id = "V1-PROMOTE-REJECT"
    client.post("/v1/projects", json={"project_id": project_id, "name": "Promotion"})
    response = client.post(
        f"/v1/projects/{project_id}/developer-promotions",
        json={
            "proposal_id": "missing",
            "proposal_fingerprint": PROMOTION_FP,
            "human_review_id": "missing-review",
        },
    )
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "PROPOSAL_NOT_FOUND"
    assert detail["data"]["status"] == "REJECTED"
    assert repo.get_d2(project_id) is None
    close(repo)


def test_v1_developer_promotion_request_is_strict(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-PROMOTE-STRICT", "name": "Promotion"})
    response = client.post(
        "/v1/projects/V1-PROMOTE-STRICT/developer-promotions",
        json={
            "proposal_id": "p",
            "proposal_fingerprint": "A" * 64,
            "human_review_id": "r",
            "unexpected": True,
        },
    )
    assert response.status_code == 422
    assert repo.get_d2("V1-PROMOTE-STRICT") is None
    close(repo)

