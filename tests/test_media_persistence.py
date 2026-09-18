import io

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


def _payload(evidence_id="E-MEDIA-1"):
    return {
        "evidence_id": evidence_id,
        "statement": "Field photo captured by architect",
        "actor": "architect",
        "spatial_scope": "edificacion",
        "observation_type": "FIELD_PHOTO",
        "epistemic_state": "USER_PROVIDED",
        "evidence_state": "OBSERVED",
        "qualifier": "UNKNOWN",
        "unknowns": ["photo_direction"],
    }


def test_media_persists_reloads_retrieves_and_preserves_provenance(tmp_path, monkeypatch):
    repo = SQLiteRepository(tmp_path / "media.sqlite", check_same_thread=False)
    monkeypatch.setenv("SICL_MEDIA_ROOT", str(tmp_path / "media"))
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            assert client.post("/v1/projects", json={"project_id": "P-MEDIA", "name": "Media Pilot"}).status_code == 200
            upload = client.post(
                "/v1/projects/P-MEDIA/spatial-evidence/media",
                files={"file": ("field.png", b"\x89PNG\r\n\x1a\nsynthetic", "image/png")},
                data={"payload_json": __import__("json").dumps(_payload())},
            )
            assert upload.status_code == 200, upload.text
            evidence = upload.json()["data"]["evidence"]
            assert evidence["photo_reference"].startswith("MED-")
            assert evidence["media_content_type"] == "image/png"
            assert evidence["media_byte_size"] > 0
            assert evidence["decision_created"] is False
            media_id = evidence["photo_reference"]
            # New request simulates reload; no browser object URL is involved.
            retrieved = client.get(f"/v1/projects/P-MEDIA/spatial-evidence/media/{media_id}")
            assert retrieved.status_code == 200
            assert retrieved.headers["content-type"].startswith("image/png")
            assert retrieved.content.startswith(b"\x89PNG")
            with TestClient(app) as client_b:
                client_b_retrieved = client_b.get(f"/v1/projects/P-MEDIA/spatial-evidence/media/{media_id}")
                assert client_b_retrieved.status_code == 200
                assert client_b_retrieved.content == retrieved.content
            listed = client.get("/v1/projects/P-MEDIA/evidence")
            assert listed.status_code == 200
            stored = listed.json()["data"]["evidence"][0]
            assert stored["evidence_hash"] == evidence["evidence_hash"]
            assert repo.events("P-MEDIA")[-1].type == "SPATIAL_EVIDENCE_ADDED"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_media_rejects_invalid_mime_oversize_and_wrong_project(tmp_path, monkeypatch):
    repo = SQLiteRepository(tmp_path / "media-errors.sqlite", check_same_thread=False)
    monkeypatch.setenv("SICL_MEDIA_ROOT", str(tmp_path / "media"))
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            assert client.post("/v1/projects", json={"project_id": "P-MEDIA", "name": "Media Pilot"}).status_code == 200
            bad = client.post("/v1/projects/P-MEDIA/spatial-evidence/media", files={"file": ("x.exe", b"bad", "application/octet-stream")}, data={"payload_json": __import__("json").dumps(_payload())})
            assert bad.status_code == 400
            too_large = client.post("/v1/projects/P-MEDIA/spatial-evidence/media", files={"file": ("x.png", b"x" * (10 * 1024 * 1024 + 1), "image/png")}, data={"payload_json": __import__("json").dumps(_payload("E-MEDIA-2"))})
            assert too_large.status_code == 400
            missing = client.get("/v1/projects/OTHER/spatial-evidence/media/MED-unknown")
            assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()
        repo.close()
