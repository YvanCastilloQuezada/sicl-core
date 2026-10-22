from __future__ import annotations

import os

import ifcopenshell
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import create_app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def _ifc_bytes() -> bytes:
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId="2Hwall00000000002", OwnerHistory=None, Name="Wall")
    model.create_entity("IfcSpace", GlobalId="2Hspace000000002", OwnerHistory=None, Name="Space")
    return model.to_string().encode("utf-8")


def test_http_ifc_import_is_read_only(tmp_path) -> None:
    repo = SQLiteRepository(tmp_path / "ifc-http.sqlite", check_same_thread=False)
    assert CLI(repo, actor="test").execute('/PROJECT CREATE IFC-HTTP "IFC HTTP"')['code'] == 'OK'
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: repo
    headers = {"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"}
    with TestClient(app, headers=headers) as client:
        response = client.post(
            "/v1/projects/IFC-HTTP/bim/ifc-import?spatial_scope=edificacion&coordinate_reference_system=EPSG:4326",
            files={"file": ("sample.ifc", _ifc_bytes(), "application/octet-stream")},
        )
        assert response.status_code == 200
        body = response.json()["data"]
        assert body["read_only"] is True
        assert body["export_applied"] is False
        assert body["rne_validation"]
        assert all(item["result"] == "REVIEW_REQUIRED" for item in body["rne_validation"])
    repo.close()
