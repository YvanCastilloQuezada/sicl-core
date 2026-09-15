from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen


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


FALLBACK_TRUJILLO = SiteObservation(
    location="Trujillo, Peru",
    latitude=-8.1116,
    longitude=-79.0287,
    temperature_mean_c=21.0,
    wind_speed_kmh=18.0,
    radiation_kwh_m2_day=5.5,
    source="SITE_INTELLIGENCE_FIXTURE",
    simulated=True,
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
        "timezone": "UTC",
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
    )


def fallback_observation(location: str) -> SiteObservation:
    if "TRUJILLO" in location.upper():
        return FALLBACK_TRUJILLO
    raise ValueError(f"no deterministic site fixture available: {location}")


def get_site_observation(location: str, timeout: float = 5.0) -> SiteObservation:
    try:
        return fetch_open_meteo(location, timeout=timeout)
    except Exception:
        return fallback_observation(location)
