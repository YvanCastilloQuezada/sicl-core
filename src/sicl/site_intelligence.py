from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlencode
from typing import Any
from urllib.request import Request, urlopen

from .domain import KNOWLEDGE_STATES


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class SiteObservation:
    location: str
    latitude: float
    longitude: float
    temperature_mean_c: float
    wind_speed_kmh: float
    radiation_kwh_m2_day: float
    source: str
    simulated: bool = False
    state: str = "OBSERVED"
    captured_at: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)
    method_version: str = "OPEN_METEO_DAILY_INDICATORS/1"
    evidence_url: str = ""
    evidence_hash: str = ""
    timezone: str = "America/Lima"

    def __post_init__(self) -> None:
        if self.state not in KNOWLEDGE_STATES:
            raise ValueError(f"invalid knowledge state: {self.state}")
        if not self.captured_at:
            object.__setattr__(self, "captured_at", _now_iso())
        if not self.evidence_hash and self.raw_response:
            canonical = json.dumps(self.raw_response, sort_keys=True, separators=(",", ":")).encode()
            object.__setattr__(self, "evidence_hash", hashlib.sha256(canonical).hexdigest())


FALLBACK_TRUJILLO = SiteObservation(
    location="Trujillo, Peru",
    latitude=-8.1116,
    longitude=-79.0287,
    temperature_mean_c=21.0,
    wind_speed_kmh=18.0,
    radiation_kwh_m2_day=5.5,
    source="SITE_INTELLIGENCE_FIXTURE",
    simulated=True,
    method_version="DETERMINISTIC_FIXTURE/1",
    raw_response={"fixture": "FALLBACK_TRUJILLO"},
    evidence_url="fixture://FALLBACK_TRUJILLO",
)


def _get_json(url: str, timeout: float = 5.0) -> dict:
    request = Request(url, headers={"User-Agent": "SICL/2.0"})
    with urlopen(request, timeout=timeout) as response:  # nosec B310: fixed public HTTPS endpoints below
        return json.loads(response.read().decode("utf-8"))


def fetch_open_meteo(location: str, timeout: float = 5.0) -> SiteObservation:
    """Fetch geocoding and current/forecast indicators from Open-Meteo.

    The function is deterministic with respect to the API response and has no API key.
    Callers should catch network/shape errors and use ``fallback_observation``.
    """
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({"name": location, "count": 1, "language": "en", "format": "json"})
    geo = _get_json(geo_url, timeout)
    results = geo.get("results") or []
    if not results:
        raise ValueError(f"location not found: {location}")
    place = results[0]
    latitude = float(place["latitude"])
    longitude = float(place["longitude"])
    weather_url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_mean,wind_speed_10m_max,shortwave_radiation_sum",
        "forecast_days": 7,
        "timezone": "America/Lima",
    })
    weather = _get_json(weather_url, timeout)
    daily = weather.get("daily") or {}
    temperature = [v for v in daily.get("temperature_2m_mean", []) if v is not None]
    wind = [v for v in daily.get("wind_speed_10m_max", []) if v is not None]
    radiation = [v for v in daily.get("shortwave_radiation_sum", []) if v is not None]
    if not temperature or not wind or not radiation:
        raise ValueError("Open-Meteo response lacks required daily indicators")
    return SiteObservation(
        location=location,
        latitude=latitude,
        longitude=longitude,
        temperature_mean_c=round(sum(temperature) / len(temperature), 2),
        wind_speed_kmh=round(sum(wind) / len(wind), 2),
        radiation_kwh_m2_day=round(sum(radiation) / len(radiation), 2),
        source="OPEN_METEO_API",
        raw_response={"geocoding": geo, "weather": weather},
        method_version="OPEN_METEO_GEOCODING_FORECAST/1",
        evidence_url=f"{geo_url} | {weather_url}",
        timezone=str(weather.get("timezone") or "America/Lima"),
    )


def fetch_open_meteo_solar_coordinates(latitude: float, longitude: float, selected_date: str, *, location_label: str = "Confirmed project location", timeout: float = 5.0) -> dict[str, Any]:
    """Fetch hourly solar source variables directly for confirmed EPSG:4326 coordinates."""
    weather_url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
        "latitude": latitude, "longitude": longitude,
        "hourly": "shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,apparent_temperature,relative_humidity_2m,dew_point_2m,precipitation,rain,showers,precipitation_probability,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,pressure_msl,surface_pressure",
        "wind_speed_unit": "ms",
        "start_date": selected_date, "end_date": selected_date,
        "timezone": "America/Lima",
    })
    weather = _get_json(weather_url, timeout)
    hourly = weather.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        raise ValueError("Open-Meteo response lacks hourly solar timestamps")
    return {
        "location": location_label, "latitude": float(latitude), "longitude": float(longitude),
        "timezone": str(weather.get("timezone") or "America/Lima"),
        "source": "OPEN_METEO_API",
        "source_model": str(weather.get("generationtime_ms", "unknown")),
        "source_variables": ["shortwave_radiation", "direct_radiation", "diffuse_radiation", "direct_normal_irradiance", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m", "precipitation", "rain", "showers", "precipitation_probability", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "pressure_msl", "surface_pressure"],
        "hourly": hourly, "selected_date": selected_date, "evidence_url": weather_url,
        "raw_response": {"weather": weather}, "captured_at": _now_iso(),
        "method_version": "OPEN_METEO_HOURLY_SOLAR_COORDINATES/1",
    }

def fetch_open_meteo_solar(location: str, selected_date: str, timeout: float = 5.0) -> dict[str, Any]:
    """Fetch hourly solar source variables for one day in local civil time.

    This is source data only. It does not calculate facade exposure, shadows,
    energy performance, or thermal comfort.
    """
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({"name": location, "count": 1, "language": "en", "format": "json"})
    geo = _get_json(geo_url, timeout)
    results = geo.get("results") or []
    if not results:
        raise ValueError(f"location not found: {location}")
    place = results[0]
    latitude = float(place["latitude"])
    longitude = float(place["longitude"])
    weather_url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,apparent_temperature,relative_humidity_2m,dew_point_2m,precipitation,rain,showers,precipitation_probability,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,pressure_msl,surface_pressure",
        "wind_speed_unit": "ms",
        "start_date": selected_date,
        "end_date": selected_date,
        "timezone": "America/Lima",
    })
    weather = _get_json(weather_url, timeout)
    hourly = weather.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        raise ValueError("Open-Meteo response lacks hourly solar timestamps")
    return {
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": str(weather.get("timezone") or "America/Lima"),
        "source": "OPEN_METEO_API",
        "source_model": str(weather.get("generationtime_ms", "unknown")),
        "source_variables": ["shortwave_radiation", "direct_radiation", "diffuse_radiation", "direct_normal_irradiance", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m", "precipitation", "rain", "showers", "precipitation_probability", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "pressure_msl", "surface_pressure"],
        "hourly": hourly,
        "selected_date": selected_date,
        "evidence_url": f"{geo_url} | {weather_url}",
        "raw_response": {"geocoding": geo, "weather": weather},
        "captured_at": _now_iso(),
        "method_version": "OPEN_METEO_HOURLY_SOLAR/1",
    }



def fetch_open_meteo_air_quality(latitude: float, longitude: float, selected_date: str, *, location_label: str = "Territorial environmental proxy", timeout: float = 5.0) -> dict[str, Any]:
    url = "https://air-quality-api.open-meteo.com/v1/air-quality?" + urlencode({"latitude": latitude, "longitude": longitude, "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,dust,aerosol_optical_depth,uv_index,european_aqi,us_aqi", "start_date": selected_date, "end_date": selected_date, "timezone": "America/Lima"})
    raw = _get_json(url, timeout)
    hourly = raw.get("hourly") or {}
    if not hourly.get("time"):
        raise ValueError("Open-Meteo Air Quality response lacks hourly timestamps")
    return {"location": location_label, "latitude": float(latitude), "longitude": float(longitude), "timezone": str(raw.get("timezone") or "America/Lima"), "source": "OPEN_METEO_AIR_QUALITY_API", "source_model": str(raw.get("model") or "CAMS"), "source_variables": [k for k in hourly if k != "time"], "hourly": hourly, "selected_date": selected_date, "evidence_url": url, "raw_response": {"air_quality": raw}, "captured_at": _now_iso(), "method_version": "OPEN_METEO_AIR_QUALITY_HOURLY/1", "spatial_resolution": "provider model grid; not local sensor"}


def fetch_open_meteo_climate(latitude: float, longitude: float, *, start_date: str = "1991-01-01", end_date: str = "2050-12-31", model: str = "EC_Earth3P_HR", location_label: str = "Territorial climate proxy", timeout: float = 5.0) -> dict[str, Any]:
    url = "https://climate-api.open-meteo.com/v1/climate?" + urlencode({"latitude": latitude, "longitude": longitude, "start_date": start_date, "end_date": end_date, "models": model, "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_mean,wind_speed_10m_max,shortwave_radiation_sum,cloud_cover_mean,relative_humidity_2m_mean,pressure_msl_mean,soil_moisture_0_to_10cm_mean,et0_fao_evapotranspiration"})
    raw = _get_json(url, timeout)
    daily = raw.get("daily") or {}
    if not daily.get("time"):
        raise ValueError("Open-Meteo Climate response lacks daily timestamps")
    return {"location": location_label, "latitude": float(latitude), "longitude": float(longitude), "timezone": str(raw.get("timezone") or "GMT"), "source": "OPEN_METEO_CLIMATE_API", "source_model": model, "source_variables": [k for k in daily if k != "time"], "daily": daily, "start_date": start_date, "end_date": end_date, "temporal_resolution": "daily", "spatial_resolution": "provider climate model cell; approximately 10-51 km depending on model", "evidence_url": url, "raw_response": {"climate": raw}, "captured_at": _now_iso(), "method_version": "OPEN_METEO_CLIMATE_DAILY_CMIP6/1", "bias_correction": "provider/model dependent; not assumed"}

def fallback_observation(location: str) -> SiteObservation:
    if "TRUJILLO" in location.upper():
        return FALLBACK_TRUJILLO
    raise ValueError(f"no deterministic site fixture available: {location}")


def get_site_observation(location: str, timeout: float = 5.0) -> SiteObservation:
    try:
        return fetch_open_meteo(location, timeout=timeout)
    except Exception:
        return fallback_observation(location)
