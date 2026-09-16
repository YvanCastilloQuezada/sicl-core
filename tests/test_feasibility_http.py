from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


def test_http_variables_and_feasible_pareto(tmp_path, monkeypatch):
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-token")
    repo = SQLiteRepository(tmp_path / "http.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    try:
        headers = {"Authorization": "Bearer test-token"}
        created = client.post('/v1/projects', headers=headers, json={"project_id":"P-HTTP-FEAS","name":"HTTP feasibility","spatial_scope":"edificacion","temporal_scope":"proyecto","actor":"architect"})
        assert created.status_code == 200, created.text
        variable = client.post('/v1/projects/P-HTTP-FEAS/variables', headers=headers, json={"variable_id":"V-1","normalized_key":"INVESTMENT","variable_type":"CONSTRAINT","value":90,"actor_id":"architect","authority":"PROJECT_OWNER","unit":"USD","spatial_scope":"edificacion"})
        assert variable.status_code == 200, variable.text
        listed = client.get('/v1/projects/P-HTTP-FEAS/variables', headers=headers)
        assert listed.status_code == 200
        assert listed.json()["data"]["variables"][0]["variable_id"] == "V-1"
        check = client.post('/v1/projects/P-HTTP-FEAS/feasibility', headers=headers, json={"alternative_id":"ALT-A","values":{"INVESTMENT":90}})
        assert check.status_code == 200, check.text
        assert check.json()["data"]["feasibility"]["state"] == "FEASIBLE"
        front = client.post('/v1/projects/P-HTTP-FEAS/multiobjective/feasible-pareto', headers=headers, json={"pareto_front":["ALT-A","ALT-B"]})
        assert front.status_code == 200, front.text
        assert front.json()["data"]["feasible_pareto_front"] == ["ALT-A"]
    finally:
        app.dependency_overrides.clear()
