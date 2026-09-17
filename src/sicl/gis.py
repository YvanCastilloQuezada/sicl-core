from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from .domain import SpatialScope

ALLOWED_GEOMETRIES = {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}


@dataclass(frozen=True)
class ParcelSnapshot:
    parcel_id: str
    project_id: str
    geometry: dict[str, Any]
    properties: dict[str, Any]
    source_url: str
    source_type: str
    jurisdiction: str
    source_crs: str
    analysis_crs: str
    retrieved_at: str
    validity_date: str | None
    response_hash: str
    review_state: str = "HUMAN_REVIEW_REQUIRED"
    spatial_scope: SpatialScope = SpatialScope.PARCELA_SITIO
    version: int = 1

    def __post_init__(self) -> None:
        if not self.parcel_id.strip() or not self.project_id.strip():
            raise ValueError("parcel_id and project_id are required")
        if self.spatial_scope is not SpatialScope.PARCELA_SITIO:
            raise ValueError("GIS parcel snapshots require parcela_sitio")
        if self.geometry.get("type") not in ALLOWED_GEOMETRIES:
            raise ValueError("unsupported or missing GeoJSON geometry type")
        if not self.source_url.startswith(("https://", "http://")):
            raise ValueError("source_url must be HTTP(S)")
        if not self.source_crs.strip() or not self.analysis_crs.strip():
            raise ValueError("source_crs and analysis_crs are required")


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def ingest_geojson(
    feature: dict[str, Any], project_id: str, source_url: str, source_type: str = "OFFICIAL",
    jurisdiction: str = "UNKNOWN", source_crs: str = "EPSG:4326", analysis_crs: str = "EPSG:4326",
    validity_date: str | None = None,
) -> ParcelSnapshot:
    if feature.get("type") != "Feature":
        raise ValueError("GeoJSON parcel must be a Feature")
    parcel_id = str(feature.get("id") or feature.get("properties", {}).get("parcel_id") or "").strip()
    if not parcel_id:
        raise ValueError("GeoJSON feature requires id or properties.parcel_id")
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("GeoJSON feature requires geometry")
    properties = feature.get("properties") or {}
    return ParcelSnapshot(parcel_id, project_id, geometry, properties, source_url, source_type, jurisdiction, source_crs, analysis_crs, datetime.now(timezone.utc).isoformat(), validity_date, canonical_hash(feature))


def fetch_ogc_features(url: str, project_id: str, source_type: str = "OFFICIAL", jurisdiction: str = "UNKNOWN", source_crs: str = "EPSG:4326", analysis_crs: str = "EPSG:4326", timeout: float = 15.0) -> list[ParcelSnapshot]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValueError("OGC URL must be HTTP(S)")
    request = urllib.request.Request(url, headers={"Accept": "application/geo+json, application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    features = payload.get("features") if payload.get("type") == "FeatureCollection" else [payload]
    if not isinstance(features, list):
        raise ValueError("OGC response must be a GeoJSON FeatureCollection")
    return [ingest_geojson(item, project_id, url, source_type, jurisdiction, source_crs, analysis_crs) for item in features]


def parcel_to_dict(item: ParcelSnapshot) -> dict[str, Any]:
    result = asdict(item)
    result["spatial_scope"] = item.spatial_scope.value
    return result


@dataclass(frozen=True)
class ParcelBoundaryConflict:
    conflict_id: str
    project_id: str
    parcel_id: str
    left_hash: str
    right_hash: str
    reason: str
    state: str = "HUMAN_REVIEW_REQUIRED"


def is_expired(snapshot: ParcelSnapshot, now: datetime | None = None) -> bool:
    if not snapshot.validity_date:
        return False
    current = (now or datetime.now(timezone.utc)).date().isoformat()
    return snapshot.validity_date < current


def reconcile_parcels(left: ParcelSnapshot, right: ParcelSnapshot) -> ParcelBoundaryConflict | None:
    if left.project_id != right.project_id or left.parcel_id != right.parcel_id:
        raise ValueError("reconciliation requires the same project and parcel")
    if left.response_hash == right.response_hash:
        return None
    conflict_id = canonical_hash({"left": left.response_hash, "right": right.response_hash})[7:23]
    return ParcelBoundaryConflict(conflict_id, left.project_id, left.parcel_id, left.response_hash, right.response_hash, "parcel boundaries or source attributes differ")


def conflict_to_dict(conflict: ParcelBoundaryConflict) -> dict[str, Any]:
    return asdict(conflict)


@dataclass(frozen=True)
class CadastralSource:
    source_id: str
    jurisdiction: str
    title: str
    collection_url: str
    source_type: str = "OFFICIAL"
    status: str = "REVIEW_REQUIRED"
    license: str | None = None


CATALOG: tuple[CadastralSource, ...] = ()


def register_cadastral_source(source: CadastralSource) -> None:
    global CATALOG
    if any(item.source_id == source.source_id for item in CATALOG):
        raise ValueError("cadastral source already exists")
    CATALOG = (*CATALOG, source)


def cadastral_catalog(jurisdiction: str | None = None) -> list[dict[str, Any]]:
    items = CATALOG if not jurisdiction else tuple(item for item in CATALOG if item.jurisdiction == jurisdiction)
    return [asdict(item) for item in items]
