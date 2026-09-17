"""Canonical project spatial location runtime model for MV-P1.2."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4

from .domain import SpatialScope


class LocationStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    CONFIRMED = "CONFIRMED"
    SUPERSEDED = "SUPERSEDED"


class AcquisitionMethod(str, Enum):
    USER_INPUT = "USER_INPUT"
    MAP_SELECTION = "MAP_SELECTION"
    PROJECT_DOCUMENT = "PROJECT_DOCUMENT"
    GIS = "GIS"
    EXTERNAL_SOURCE = "EXTERNAL_SOURCE"
    DERIVATION = "DERIVATION"
    ASSUMPTION = "ASSUMPTION"


class LocationProvenance(str, Enum):
    USER_DECLARED = "USER_DECLARED"
    DOCUMENTED = "DOCUMENTED"
    DERIVED = "DERIVED"
    EXTERNAL = "EXTERNAL"
    ASSUMED = "ASSUMED"


@dataclass(frozen=True)
class SpatialLocation:
    location_id: str
    project_id: str
    spatial_scope: SpatialScope
    geometry_type: str
    geometry: dict[str, Any]
    crs: str = "EPSG:4326"
    place_label: str | None = None
    acquisition_method: AcquisitionMethod = AcquisitionMethod.USER_INPUT
    provenance: LocationProvenance = LocationProvenance.USER_DECLARED
    status: LocationStatus = LocationStatus.CONFIRMED
    actor_id: str = "api"
    authority: str = "project_owner"
    version: int = 1
    supersedes_location_id: str | None = None
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.location_id or not self.project_id:
            raise ValueError("location_id and project_id are required")
        if self.geometry_type not in {"Point", "LineString", "Polygon"}:
            raise ValueError("geometry_type must be Point, LineString, or Polygon")
        if self.crs not in {"EPSG:4326", "EPSG:3857"}:
            raise ValueError("unsupported CRS; use EPSG:4326 or EPSG:3857")
        self._validate_geometry()
        if self.status == LocationStatus.CONFIRMED and not self.actor_id:
            raise ValueError("confirmed locations require an actor")
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.now(timezone.utc).isoformat())

    def _validate_geometry(self) -> None:
        coordinates = self.geometry.get("coordinates")
        if self.geometry.get("type") != self.geometry_type or coordinates is None:
            raise ValueError("geometry must match geometry_type and include coordinates")
        if self.geometry_type == "Point":
            if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
                raise ValueError("Point coordinates must be [longitude, latitude]")
            lon, lat = float(coordinates[0]), float(coordinates[1])
            if not -180 <= lon <= 180 or not -90 <= lat <= 90:
                raise ValueError("Point coordinates are outside valid longitude/latitude ranges")

    @property
    def longitude(self) -> float | None:
        return float(self.geometry["coordinates"][0]) if self.geometry_type == "Point" else None

    @property
    def latitude(self) -> float | None:
        return float(self.geometry["coordinates"][1]) if self.geometry_type == "Point" else None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        for key in ("spatial_scope", "acquisition_method", "provenance", "status"):
            value[key] = getattr(self, key).value
        value["longitude"] = self.longitude
        value["latitude"] = self.latitude
        return value

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SpatialLocation":
        value = dict(data)
        value.pop("longitude", None)
        value.pop("latitude", None)
        value["spatial_scope"] = SpatialScope(value["spatial_scope"])
        value["acquisition_method"] = AcquisitionMethod(value.get("acquisition_method", "USER_INPUT"))
        value["provenance"] = LocationProvenance(value.get("provenance", "USER_DECLARED"))
        value["status"] = LocationStatus(value.get("status", "CONFIRMED"))
        return cls(**value)


def candidate_point(project_id: str, longitude: float, latitude: float, *, spatial_scope: SpatialScope | str = SpatialScope.PARCELA_SITIO, place_label: str | None = None, acquisition_method: AcquisitionMethod | str = AcquisitionMethod.MAP_SELECTION, actor_id: str = "user") -> SpatialLocation:
    return SpatialLocation(
        location_id=f"LOC-{uuid4().hex[:12]}", project_id=project_id,
        spatial_scope=SpatialScope(spatial_scope), geometry_type="Point",
        geometry={"type": "Point", "coordinates": [float(longitude), float(latitude)]},
        place_label=place_label, acquisition_method=AcquisitionMethod(acquisition_method),
        provenance=LocationProvenance.USER_DECLARED, status=LocationStatus.CANDIDATE,
        actor_id=actor_id,
    )


def location_to_dict(location: SpatialLocation) -> dict[str, Any]:
    return location.to_dict()


__all__ = ["SpatialLocation", "LocationStatus", "AcquisitionMethod", "LocationProvenance", "candidate_point", "location_to_dict"]
