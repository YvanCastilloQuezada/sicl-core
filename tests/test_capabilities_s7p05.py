from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from sicl.capabilities import ApplicabilityState, SOLAR_TEMPORAL_ANALYSIS, resolve_capability, ProjectCapabilityContext
from sicl.domain import SpatialScope


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "s7p05-token")
    return TestClient(create_app())


def test_resolution_distinguishes_applicability_states():
    available = resolve_capability(SOLAR_TEMPORAL_ANALYSIS, ProjectCapabilityContext(SpatialScope.EDIFICACION, available_data=frozenset({"location", "environmental_data"})))
    missing = resolve_capability(SOLAR_TEMPORAL_ANALYSIS, ProjectCapabilityContext(SpatialScope.EDIFICACION))
    unavailable = resolve_capability(SOLAR_TEMPORAL_ANALYSIS, ProjectCapabilityContext(SpatialScope.PARCELA_SITIO))
    not_applicable = resolve_capability(SOLAR_TEMPORAL_ANALYSIS, ProjectCapabilityContext(SpatialScope.OBJETO))
    assert available.status is ApplicabilityState.AVAILABLE
    assert missing.status is ApplicabilityState.REQUIRES_DATA
    assert unavailable.status is ApplicabilityState.NOT_AVAILABLE
    assert not_applicable.status is ApplicabilityState.NOT_APPLICABLE


def test_capability_endpoint_returns_canonical_payload(client):
    response = client.get(
        "/v1/examples/UPAO-001/capabilities/SOLAR_TEMPORAL_ANALYSIS",
        params={"spatial_scope": "edificacion"},
        headers={"Authorization": "Bearer s7p05-token"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["capability_id"] == SOLAR_TEMPORAL_ANALYSIS
    assert payload["spatial_scope"] == "edificacion"
    assert payload["status"] == "AVAILABLE"
    assert payload["profile_version"] == "multiscale-capability-s7p05-v1"


def test_capability_endpoint_rejects_unknown_example(client):
    response = client.get(
        "/v1/examples/UNKNOWN/capabilities/SOLAR_TEMPORAL_ANALYSIS",
        params={"spatial_scope": "edificacion"},
        headers={"Authorization": "Bearer s7p05-token"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "EXAMPLE_NOT_FOUND"


def test_capability_endpoint_requires_auth_when_token_is_configured(client):
    response = client.get(
        "/v1/examples/UPAO-001/capabilities/SOLAR_TEMPORAL_ANALYSIS",
        params={"spatial_scope": "edificacion"},
    )
    assert response.status_code == 401


def test_all_eleven_scopes_are_exposed():
    assert len(list(SpatialScope)) == 11
    assert {scope.value for scope in SpatialScope} == {
        "pais", "macro_region", "region", "provincia_metropoli", "distrito_ciudad",
        "zona_barrio_sector", "parcela_sitio", "edificacion", "sistema", "espacio", "objeto",
    }
