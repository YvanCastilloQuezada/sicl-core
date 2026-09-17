import os
from fastapi.testclient import TestClient
from api.main import create_app


def _aq():
    return {"timezone": "America/Lima", "model": "CAMS", "hourly": {"time": ["2026-09-17T12:00"], "pm2_5": [12.3], "pm10": [22.0], "nitrogen_dioxide": [8.0], "ozone": [55.0], "sulphur_dioxide": [1.0], "carbon_monoxide": [220.0], "dust": [3.0], "aerosol_optical_depth": [0.1], "uv_index": [5.0], "european_aqi": [31], "us_aqi": [28]}}


def _climate():
    return {"daily": {"time": ["2026-09-17"], "temperature_2m_mean": [22.0], "precipitation_sum": [0.2], "wind_speed_10m_mean": [12.0], "shortwave_radiation_sum": [18.0], "cloud_cover_mean": [30.0], "relative_humidity_2m_mean": [70.0], "pressure_msl_mean": [1010.0], "soil_moisture_0_to_10cm_mean": [0.2], "et0_fao_evapotranspiration": [3.1]}}


def test_territorial_endpoint_separates_air_quality_and_climate(monkeypatch):
    os.environ["SICL_CORE_SERVICE_TOKEN"] = "test-token"
    monkeypatch.setattr("api.routes.v1.fetch_open_meteo_air_quality", lambda *args, **kwargs: {"source": "OPEN_METEO_AIR_QUALITY_API", "source_model": "CAMS", "spatial_resolution": "provider grid", "evidence_url": "https://air-quality-api.open-meteo.com", "hourly": _aq()["hourly"]})
    monkeypatch.setattr("api.routes.v1.fetch_open_meteo_climate", lambda *args, **kwargs: {"source": "OPEN_METEO_CLIMATE_API", "source_model": "EC_Earth3P_HR", "spatial_resolution": "10-51 km model cell", "evidence_url": "https://climate-api.open-meteo.com", "start_date": "2026-09-17", "end_date": "2026-09-17", "temporal_resolution": "daily", "bias_correction": "not assumed", "daily": _climate()["daily"]})
    response = TestClient(create_app()).get("/v1/examples/UPAO-001/territorial-environment?selected_date=2026-09-17&selected_time=12:00", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    body = response.json()["data"]
    assert {layer["family"] for layer in body["layers"]} == {"AIR_QUALITY", "CLIMATE"}
    assert body["weather_vs_climate_separated"] is True
    assert body["location"]["provenance"].startswith("Open-Meteo")
    assert body["decision_created"] is False


def test_territorial_endpoint_rejects_non_authorized_scope():
    os.environ["SICL_CORE_SERVICE_TOKEN"] = "test-token"
    response = TestClient(create_app()).get("/v1/examples/UPAO-001/territorial-environment?selected_date=2026-09-17&spatial_scope=objeto", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 400


def test_tesu_scopes_share_shell_but_change_capability_profile(monkeypatch):
    os.environ["SICL_CORE_SERVICE_TOKEN"] = "test-token"
    monkeypatch.setattr("api.routes.v1.fetch_open_meteo_air_quality", lambda *args, **kwargs: {"source": "AQ", "source_model": "CAMS", "spatial_resolution": "provider grid", "evidence_url": "aq", "hourly": _aq()["hourly"]})
    monkeypatch.setattr("api.routes.v1.fetch_open_meteo_climate", lambda *args, **kwargs: {"source": "CLIMATE", "source_model": "MODEL", "spatial_resolution": "model cell", "evidence_url": "climate", "start_date": "2026-09-17", "end_date": "2026-09-17", "temporal_resolution": "daily", "bias_correction": "not assumed", "daily": _climate()["daily"]})
    client = TestClient(create_app())
    for scope in ("provincia_metropoli", "region", "macro_region", "pais"):
        r = client.get(f"/v1/examples/UPAO-001/territorial-environment?selected_date=2026-09-17&selected_time=12:00&spatial_scope={scope}", headers={"Authorization": "Bearer test-token"})
        assert r.status_code == 200
        body = r.json()["data"]
        assert body["spatial_scope"] == scope
        assert body["capability_profile"]["visual"] != "POINT_CONTEXT + PROVIDER_MODEL_GRID"
        assert body["cross_scale"]["containment_asserted"] is False
