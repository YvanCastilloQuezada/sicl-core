from __future__ import annotations

import os

from fastapi.testclient import TestClient

from api.main import create_app
from sicl.environmental import EnvironmentalAnalysisError, EnvironmentalLocation, build_solar_analysis, parse_local_datetime, solar_position


def test_location_preserves_approved_educational_provenance() -> None:
    location = EnvironmentalLocation("Trujillo, Peru", -8.1116, -79.0287)
    assert location.timezone == "America/Lima"
    assert location.role == "ENVIRONMENTAL_REFERENCE"
    assert location.location_class == "EDUCATIONAL_PROXY"
    assert location.surveyed_site is False
    assert location.cadastral_location is False
    assert location.verified_upao_site is False


def test_solar_position_is_deterministic_and_timezone_aware() -> None:
    first = solar_position(parse_local_datetime("2026-09-17", "15:00"), -8.1116, -79.0287)
    second = solar_position(parse_local_datetime("2026-09-17", "15:00"), -8.1116, -79.0287)
    assert first == second
    assert 0 <= first.azimuth_degrees < 360
    assert -90 <= first.elevation_degrees <= 90
    assert len(first.solar_vector) == 3


def test_invalid_time_and_location_are_controlled() -> None:
    try:
        parse_local_datetime("2026-09-17", "15:30")
    except EnvironmentalAnalysisError as exc:
        assert exc.code == "INVALID_DATE_TIME"
    else:
        raise AssertionError("invalid time was accepted")
    try:
        EnvironmentalLocation("bad", 91, 0)
    except EnvironmentalAnalysisError as exc:
        assert exc.code == "INVALID_LOCATION"
    else:
        raise AssertionError("invalid location was accepted")


def test_analysis_separates_source_radiation_from_derived_position() -> None:
    result = build_solar_analysis(
        example_id="UPAO-001",
        alternative_id="UPAO-001-A",
        selected_date="2026-09-17",
        selected_time="15:00",
        location=EnvironmentalLocation("Trujillo, Peru", -8.1116, -79.0287),
        source_values={"shortwave_radiation": 120.0, "direct_radiation": 90.0, "diffuse_radiation": 30.0, "wind_speed_10m": 4.2, "wind_direction_10m": 270, "temperature_2m": 27.0},
        source="OPEN_METEO_API",
        source_model="test",
        source_retrieved_at="2026-09-17T00:00:00+00:00",
        source_variables=("shortwave_radiation", "direct_radiation", "diffuse_radiation", "direct_normal_irradiance", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m", "precipitation", "rain", "showers", "precipitation_probability", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "pressure_msl", "surface_pressure"),
    ).to_dict()
    assert result["source_values"]["shortwave_radiation"] == 120.0
    assert "solar_azimuth_degrees" in result["derived_metrics"]
    assert result["derived_metrics"]["air_temperature_c"] == 27.0
    assert result["provenance"]["source_data"] != result["provenance"]["derived_spatial_analysis"]
    assert result["location"]["timezone"] == "America/Lima"


def test_environmental_endpoint_uses_same_time_for_abc(monkeypatch) -> None:
    os.environ["SICL_CORE_SERVICE_TOKEN"] = "test-token"
    source = {
        "timezone": "America/Lima",
        "source": "OPEN_METEO_API",
        "source_model": "test",
        "captured_at": "2026-09-17T00:00:00+00:00",
        "source_variables": ["shortwave_radiation", "direct_radiation", "diffuse_radiation", "direct_normal_irradiance", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m", "precipitation", "rain", "showers", "precipitation_probability", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "pressure_msl", "surface_pressure"],
        "hourly": {"time": ["2026-09-17T15:00"], "shortwave_radiation": [120], "direct_radiation": [90], "diffuse_radiation": [30], "direct_normal_irradiance": [110], "wind_speed_10m": [4.2], "wind_direction_10m": [270], "wind_gusts_10m": [7.5], "temperature_2m": [27.0], "apparent_temperature": [27.5], "relative_humidity_2m": [65], "dew_point_2m": [20.0], "precipitation": [0.0], "rain": [0.0], "showers": [0.0], "precipitation_probability": [10], "cloud_cover": [25], "cloud_cover_low": [10], "cloud_cover_mid": [20], "cloud_cover_high": [30], "pressure_msl": [1012], "surface_pressure": [1008]},
    }
    monkeypatch.setattr("api.routes.v1.fetch_open_meteo_solar", lambda location, selected_date: source)
    client = TestClient(create_app())
    response = client.get("/v1/examples/UPAO-001/environmental-analysis?selected_date=2026-09-17&selected_time=15:00", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    body = response.json()["data"]
    assert [item["alternative_id"] for item in body["analyses"]] == ["UPAO-001-A", "UPAO-001-B", "UPAO-001-C"]
    assert {item["local_timestamp"] for item in body["analyses"]} == {"2026-09-17T15:00:00-05:00"}
    assert body["location"]["role"] == "ENVIRONMENTAL_REFERENCE"
    assert body["decision_created"] is False


def test_environmental_endpoint_rejects_non_hourly_time() -> None:
    os.environ["SICL_CORE_SERVICE_TOKEN"] = "test-token"
    client = TestClient(create_app())
    response = client.get("/v1/examples/UPAO-001/environmental-analysis?selected_date=2026-09-17&selected_time=15:30", headers={"Authorization": "Bearer test-token"})
    assert response.status_code in {400, 422}
