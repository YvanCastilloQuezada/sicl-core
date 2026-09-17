"""Space × time × environment analysis primitives for S7-P0.

This module deliberately separates astronomical solar position from
meteorological radiation supplied by an environmental source. It contains no
building-energy, comfort, compliance, CFD, or decision logic.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time
import math
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any, Mapping

ENVIRONMENTAL_TIMEZONE = "America/Lima"
ANALYSIS_VERSION = "S7-P0-SOLAR/1"
LOCATION_ROLE = "ENVIRONMENTAL_REFERENCE"
LOCATION_CLASS = "EDUCATIONAL_PROXY"
LOCATION_PROVENANCE = "SYNTHETIC / EDUCATIONAL_REFERENCE"


class EnvironmentalAnalysisError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class EnvironmentalLocation:
    name: str
    latitude: float
    longitude: float
    timezone: str = ENVIRONMENTAL_TIMEZONE
    role: str = LOCATION_ROLE
    location_class: str = LOCATION_CLASS
    provenance: str = LOCATION_PROVENANCE
    surveyed_site: bool = False
    cadastral_location: bool = False
    verified_upao_site: bool = False

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise EnvironmentalAnalysisError("INVALID_LOCATION", "latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise EnvironmentalAnalysisError("INVALID_LOCATION", "longitude must be between -180 and 180")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise EnvironmentalAnalysisError("INVALID_TIMEZONE", self.timezone) from exc
        if self.surveyed_site or self.cadastral_location or self.verified_upao_site:
            raise EnvironmentalAnalysisError("INVALID_LOCATION_ROLE", "S7 educational proxy cannot claim surveyed or verified site status")


@dataclass(frozen=True)
class SolarPosition:
    azimuth_degrees: float
    elevation_degrees: float
    solar_vector: tuple[float, float, float]
    derivation: str = "NOAA_APPROXIMATION/1"


@dataclass(frozen=True)
class EnvironmentalAnalysis:
    analysis_id: str
    example_id: str
    alternative_id: str
    analysis_type: str
    spatial_representation_version: str
    location: EnvironmentalLocation
    temporal_mode: str
    local_timestamp: str
    utc_timestamp: str
    source: str
    source_model: str
    source_retrieved_at: str
    source_variables: tuple[str, ...]
    source_values: Mapping[str, Any]
    derived_metrics: Mapping[str, Any]
    units: Mapping[str, str]
    provenance: Mapping[str, Any]
    analysis_version: str = ANALYSIS_VERSION

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["location"] = asdict(self.location)
        result["source_variables"] = list(self.source_variables)
        return result


def parse_local_datetime(selected_date: str, selected_time: str, timezone: str = ENVIRONMENTAL_TIMEZONE) -> datetime:
    try:
        day = date.fromisoformat(selected_date)
        clock = time.fromisoformat(selected_time)
        if clock.minute != 0 or clock.second != 0 or clock.microsecond != 0:
            raise EnvironmentalAnalysisError("INVALID_DATE_TIME", "selected_time must be an hourly HH:00 value")
        return datetime.combine(day, clock, tzinfo=ZoneInfo(timezone))
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise EnvironmentalAnalysisError("INVALID_DATE_TIME", "date must be YYYY-MM-DD and time must be HH:MM[:SS] in the declared timezone") from exc


def solar_position(local_dt: datetime, latitude: float, longitude: float) -> SolarPosition:
    """Return deterministic astronomical solar position, not radiation."""
    if local_dt.tzinfo is None:
        raise EnvironmentalAnalysisError("INVALID_DATE_TIME", "solar position requires timezone-aware datetime")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise EnvironmentalAnalysisError("INVALID_LOCATION", "invalid latitude or longitude")
    utc = local_dt.astimezone(ZoneInfo("UTC"))
    n = utc.timetuple().tm_yday
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    gamma = 2 * math.pi / 365 * (n - 1 + (hour - 12) / 24)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma) - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma))
    decl = 0.006918 - 0.399912 * math.cos(gamma) + 0.070257 * math.sin(gamma) - 0.006758 * math.cos(2 * gamma) + 0.000907 * math.sin(2 * gamma) - 0.002697 * math.cos(3 * gamma) + 0.00148 * math.sin(3 * gamma)
    offset_minutes = utc.utcoffset().total_seconds() / 60 if utc.utcoffset() else 0
    true_solar_minutes = utc.hour * 60 + utc.minute + utc.second / 60 + eqtime + 4 * longitude - offset_minutes
    hour_angle = math.radians(true_solar_minutes / 4 - 180)
    lat = math.radians(latitude)
    elevation = math.degrees(math.asin(math.sin(lat) * math.sin(decl) + math.cos(lat) * math.cos(decl) * math.cos(hour_angle)))
    azimuth = (math.degrees(math.atan2(math.sin(hour_angle), math.cos(hour_angle) * math.sin(lat) - math.tan(decl) * math.cos(lat))) + 180) % 360
    elev_rad = math.radians(elevation)
    az_rad = math.radians(azimuth)
    vector = (math.cos(elev_rad) * math.sin(az_rad), math.cos(elev_rad) * math.cos(az_rad), math.sin(elev_rad))
    return SolarPosition(round(azimuth, 6), round(elevation, 6), tuple(round(v, 6) for v in vector))


def build_solar_analysis(
    *, example_id: str, alternative_id: str, selected_date: str, selected_time: str,
    location: EnvironmentalLocation, source_values: Mapping[str, Any], source: str,
    source_model: str, source_retrieved_at: str, source_variables: tuple[str, ...],
    spatial_representation_version: str = "1.0",
) -> EnvironmentalAnalysis:
    local_dt = parse_local_datetime(selected_date, selected_time, location.timezone)
    position = solar_position(local_dt, location.latitude, location.longitude)
    analysis_id = f"{example_id}:{alternative_id}:{local_dt.isoformat()}:{ANALYSIS_VERSION}"
    return EnvironmentalAnalysis(
        analysis_id=analysis_id,
        example_id=example_id,
        alternative_id=alternative_id,
        analysis_type="SOLAR",
        spatial_representation_version=spatial_representation_version,
        location=location,
        temporal_mode="INSTANT",
        local_timestamp=local_dt.isoformat(),
        utc_timestamp=local_dt.astimezone(ZoneInfo("UTC")).isoformat(),
        source=source,
        source_model=source_model,
        source_retrieved_at=source_retrieved_at,
        source_variables=source_variables,
        source_values=dict(source_values),
        derived_metrics={"solar_azimuth_degrees": position.azimuth_degrees, "solar_elevation_degrees": position.elevation_degrees, "solar_vector_local_enu": position.solar_vector, "wind_speed_m_s": source_values.get("wind_speed_10m"), "wind_direction_degrees": source_values.get("wind_direction_10m")},
        units={"solar_azimuth_degrees": "degrees", "solar_elevation_degrees": "degrees", "solar_vector_local_enu": "unitless direction vector", "wind_speed_m_s": "m/s", "wind_direction_degrees": "degrees FROM (meteorological)"},
        provenance={"source_data": "meteorological input only", "derived_spatial_analysis": "astronomical solar position from location/date/time", "location_role": location.role, "location_class": location.location_class, "location_provenance": location.provenance, "surveyed_site": False, "cadastral_location": False, "verified_upao_site": False},
    )


__all__ = ["ANALYSIS_VERSION", "ENVIRONMENTAL_TIMEZONE", "EnvironmentalAnalysis", "EnvironmentalAnalysisError", "EnvironmentalLocation", "SolarPosition", "build_solar_analysis", "parse_local_datetime", "solar_position"]
