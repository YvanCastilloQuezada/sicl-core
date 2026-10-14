import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.mark.parametrize(
    "configured,authorization",
    [
        (None, None),
        (None, "Bearer anything"),
        ("", None),
        ("", "Bearer anything"),
        ("correct-token", None),
        ("correct-token", "Bearer wrong-token"),
    ],
)
def test_protected_route_rejects_missing_or_invalid_service_auth(
    monkeypatch, configured, authorization
):
    if configured is None:
        monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    else:
        monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", configured)

    headers = {}
    if authorization is not None:
        headers["Authorization"] = authorization

    response = TestClient(app).get("/v1/health", headers=headers)
    assert response.status_code == 401


def test_protected_route_accepts_valid_service_token(monkeypatch):
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "correct-token")
    response = TestClient(app).get(
        "/v1/health",
        headers={"Authorization": "Bearer correct-token"},
    )
    assert response.status_code == 200
