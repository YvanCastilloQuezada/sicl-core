from __future__ import annotations

import os

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import create_app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def _client(repo: SQLiteRepository) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app, headers={"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"})


def _snapshot_payload() -> dict:
    return {
        "exchange_id": "BIM-EX-001",
        "format": "IFC",
        "source_application": "Revit",
        "source_version": "2027",
        "spatial_scope": "edificacion",
        "coordinate_reference_system": "EPSG:4326",
        "units": "SI",
        "model_hash": "sha256:model-001",
        "elements": [{
            "global_id": "WALL-001",
            "entity": "IfcWall",
            "parameters": {"height": 3.2},
            "provenance": {"source": "USER_PROVIDED", "evidence_id": "EV-BIM-001"},
        }],
    }


def test_bim_snapshot_and_preview_change_set_are_persisted(tmp_path) -> None:
    repo = SQLiteRepository(tmp_path / "bim.sqlite", check_same_thread=False)
    assert CLI(repo, actor="test").execute('/PROJECT CREATE BIM-001 "BIM project"')['code'] == 'OK'
    with _client(repo) as client:
        created = client.post('/v1/projects/BIM-001/bim/snapshots', json=_snapshot_payload())
        assert created.status_code == 200
        assert created.json()['data']['snapshot']['review_state'] == 'HUMAN_REVIEW_REQUIRED'
        preview = client.post('/v1/projects/BIM-001/bim/change-sets', json={
            "change_set_id": "CS-001",
            "snapshot_id": "BIM-EX-001",
            "changes": [{"global_id": "WALL-001", "parameter": "height", "from": 3.2, "to": 3.5}],
            "requested_by": "architect",
        })
        assert preview.status_code == 200
        assert preview.json()['data']['change_set']['mode'] == 'PREVIEW'
        assert preview.json()['data']['applied'] is False
        assert client.get('/v1/projects/BIM-001/bim/snapshots').json()['data']['snapshots']
        assert client.get('/v1/projects/BIM-001/bim/change-sets').json()['data']['change_sets']
    repo.close()
    restarted = SQLiteRepository(tmp_path / "bim.sqlite", check_same_thread=False)
    assert restarted.list_bim_snapshots('BIM-001')[0].exchange_id == 'BIM-EX-001'
    assert restarted.list_bim_change_sets('BIM-001')[0].mode.value == 'PREVIEW'
    restarted.close()


def test_bim_rejects_non_preview_and_invalid_scope(tmp_path) -> None:
    repo = SQLiteRepository(tmp_path / "bim-errors.sqlite", check_same_thread=False)
    CLI(repo, actor="test").execute('/PROJECT CREATE BIM-ERR "BIM errors"')
    with _client(repo) as client:
        invalid = client.post('/v1/projects/BIM-ERR/bim/snapshots', json={**_snapshot_payload(), "spatial_scope": "invalid"})
        assert invalid.status_code == 400
        valid = client.post('/v1/projects/BIM-ERR/bim/snapshots', json=_snapshot_payload())
        assert valid.status_code == 200
        denied = client.post('/v1/projects/BIM-ERR/bim/change-sets', json={
            "change_set_id": "CS-DENIED", "snapshot_id": "BIM-EX-001", "changes": [], "requested_by": "architect", "mode": "APPLIED"
        })
        assert denied.status_code == 422
        assert denied.json()['detail']['code'] == 'BIM_PREVIEW_ONLY'
    repo.close()
