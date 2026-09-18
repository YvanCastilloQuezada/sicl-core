"""Bounded, provider-neutral external spatial context.

The canonical output is normalized evidence metadata, not a GIS model. The
first adapter uses public OpenStreetMap data through Overpass; provider fields
remain adapter metadata and never become Core ontology.
"""
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable

SCOPE_QUERY_WINDOWS = {
    "edificacion": (150.0, "m"),
    "parcela_sitio": (250.0, "m"),
    "zona_barrio_sector": (750.0, "m"),
    "distrito_ciudad": (2000.0, "m"),
    "provincia_metropoli": (5000.0, "m"),
}

DEFAULT_ENDPOINT = "https://overpass-api.de/api/interpreter"
ELEVATION_ENDPOINT = "https://api.open-meteo.com/v1/forecast"


def _bounds_from_payload(payload: dict[str, Any]) -> tuple[float, float, float, float, dict[str, Any]]:
    bbox = payload.get("bbox")
    if bbox is not None:
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            raise ValueError("bbox must be [south,west,north,east]")
        south, west, north, east = (float(value) for value in bbox)
        if not (south < north and west < east):
            raise ValueError("bbox must have south<north and west<east")
        return south, west, north, east, {"type": "BBOX", "bbox": [south, west, north, east], "units": "degrees"}
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    if latitude is None or longitude is None:
        raise ValueError("bounded query requires bbox or latitude/longitude")
    scope = str(payload.get("spatial_scope", ""))
    radius_m = float(payload.get("radius_m", SCOPE_QUERY_WINDOWS.get(scope, (250.0, "m"))[0]))
    if radius_m <= 0 or radius_m > 10000:
        raise ValueError("radius_m must be greater than zero and at most 10000")
    lat = float(latitude); lon = float(longitude)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("invalid latitude/longitude")
    lat_delta = radius_m / 111_320.0
    lon_delta = radius_m / (111_320.0 * max(math.cos(math.radians(lat)), 0.1))
    return lat - lat_delta, lon - lon_delta, lat + lat_delta, lon + lon_delta, {"type": "RADIUS_WINDOW", "center": [lat, lon], "radius": radius_m, "units": "m"}


def build_bounded_overpass_query(bounds: tuple[float, float, float, float], categories: list[str]) -> str:
    south, west, north, east = bounds
    box = f"{south:.7f},{west:.7f},{north:.7f},{east:.7f}"
    clauses: list[str] = []
    requested = set(categories or ["roads", "buildings", "pois", "water", "green", "transport"])
    if "roads" in requested: clauses.append(f'way[highway]({box});')
    if "buildings" in requested: clauses.append(f'way[building]({box});')
    if "pois" in requested: clauses.append(f'nwr[amenity]({box});')
    if "water" in requested: clauses.append(f'nwr[natural=water]({box});nwr[waterway]({box});')
    if "green" in requested: clauses.append(f'nwr[leisure=park]({box});nwr[landuse=grass]({box});nwr[natural=wood]({box});')
    if "transport" in requested: clauses.append(f'nwr[public_transport]({box});nwr[railway=station]({box});')
    if not clauses: raise ValueError("at least one supported context category is required")
    return "[out:json][timeout:25];(" + "".join(clauses) + ");out body geom;"


def _geometry(element: dict[str, Any]) -> dict[str, Any] | None:
    if element.get("type") == "node":
        if "lat" not in element or "lon" not in element: return None
        return {"type": "Point", "coordinates": [float(element["lon"]), float(element["lat"])]}
    geometry = element.get("geometry") or []
    coords = [[float(point["lon"]), float(point["lat"])] for point in geometry if "lat" in point and "lon" in point]
    if len(coords) < 2: return None
    tags = element.get("tags") or {}
    closed = len(coords) >= 4 and coords[0] == coords[-1]
    if closed and ("building" in tags or tags.get("natural") in {"water", "wood"} or tags.get("leisure") == "park" or tags.get("landuse") == "grass"):
        return {"type": "Polygon", "coordinates": [coords]}
    return {"type": "LineString", "coordinates": coords}


def _category(tags: dict[str, Any]) -> str:
    if "highway" in tags: return "roads"
    if "building" in tags: return "buildings"
    if "amenity" in tags: return "pois"
    if "waterway" in tags or tags.get("natural") == "water": return "water"
    if tags.get("leisure") == "park" or tags.get("landuse") == "grass" or tags.get("natural") == "wood": return "green"
    if "public_transport" in tags or tags.get("railway") == "station": return "transport"
    return "other"


def normalize_overpass_response(raw: dict[str, Any], *, query: dict[str, Any], retrieved_at: str | None = None) -> dict[str, Any]:
    retrieved = retrieved_at or datetime.now(timezone.utc).isoformat()
    features: list[dict[str, Any]] = []
    for element in raw.get("elements") or []:
        tags = dict(element.get("tags") or {})
        geometry = _geometry(element)
        if geometry is None: continue
        features.append({"type": "Feature", "geometry": geometry, "properties": {"external_id": f"{element.get('type')}:{element.get('id')}", "category": _category(tags), "source_attributes": tags, "provider": "OpenStreetMap", "dataset": "OpenStreetMap/Overpass", "epistemic_state": "EXTERNAL_SOURCE", "retrieved_at": retrieved}})
    counts: dict[str, int] = {}
    for feature in features:
        category = feature["properties"]["category"]; counts[category] = counts.get(category, 0) + 1
    requested = query.get("categories") or []
    categories = {category: {"state": "AVAILABLE" if counts.get(category, 0) else "UNAVAILABLE", "count": counts.get(category, 0), "source": "OpenStreetMap", "epistemic_state": "EXTERNAL_SOURCE"} for category in requested}
    if features and any(item["state"] == "UNAVAILABLE" for item in categories.values()): state = "PARTIAL"
    elif features: state = "AVAILABLE"
    else: state = "UNAVAILABLE"
    return {"state": state, "features": features, "category_status": categories, "query": query, "provenance": {"provider": "OpenStreetMap", "dataset": "OpenStreetMap/Overpass", "retrieved_at": retrieved, "license": "ODbL; attribution required", "limitations": ["External map features are not verified project facts.", "Road data does not establish legal access.", "Building footprints do not establish verified buildings, height, use or condition."]}, "decision_created": False}


def fetch_overpass(query: str, *, endpoint: str = DEFAULT_ENDPOINT, timeout: float = 30.0, opener: Callable[..., Any] | None = None) -> dict[str, Any]:
    request = urllib.request.Request(endpoint, data=urllib.parse.urlencode({"data": query}).encode(), headers={"User-Agent": "SiMS-DeI/real-world-spatial-context-01"}, method="POST")
    open_fn = opener or urllib.request.urlopen
    with open_fn(request, timeout=timeout) as response:
        if getattr(response, "status", 200) != 200: raise RuntimeError(f"provider HTTP {getattr(response, 'status', 'unknown')}")
        body = response.read(8_000_000)
    return json.loads(body.decode("utf-8"))


def query_external_context(payload: dict[str, Any], *, fetcher: Callable[[str], dict[str, Any]] | None = None) -> dict[str, Any]:
    scope = str(payload.get("spatial_scope", ""))
    if scope not in SCOPE_QUERY_WINDOWS: raise ValueError(f"unsupported active context scope: {scope}")
    south, west, north, east, extent = _bounds_from_payload(payload)
    categories = [str(value) for value in (payload.get("categories") or ["roads", "buildings", "pois", "water", "green", "transport"])]
    query = {"spatial_scope": scope, "categories": categories, "extent": extent, "bbox": [south, west, north, east], "crs": "EPSG:4326", "provider": "OpenStreetMap / Overpass", "query_window": True}
    overpass_query = build_bounded_overpass_query((south, west, north, east), categories)
    try:
        raw = (fetcher or fetch_overpass)(overpass_query)
        return normalize_overpass_response(raw, query=query)
    except Exception as exc:
        return {"state": "UNAVAILABLE", "features": [], "category_status": {category: {"state": "UNAVAILABLE", "count": 0} for category in categories}, "query": query, "provenance": {"provider": "OpenStreetMap", "dataset": "OpenStreetMap/Overpass", "limitations": ["External provider request failed.", str(exc)]}, "error": str(exc), "decision_created": False}


def fetch_open_meteo_elevation(latitude: float, longitude: float, *, fetcher: Callable[[str], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Retrieve a point elevation estimate; it is not a topographic survey."""
    if not (-90 <= float(latitude) <= 90 and -180 <= float(longitude) <= 180):
        raise ValueError("invalid latitude/longitude")
    params = urllib.parse.urlencode({"latitude": float(latitude), "longitude": float(longitude), "current": "temperature_2m"})
    url = f"{ELEVATION_ENDPOINT}?{params}"
    raw = (fetcher or (lambda _: json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "SiMS-DeI/real-world-spatial-context-01"}), timeout=15).read(2_000_000).decode("utf-8"))))(url)
    elevation = raw.get("elevation")
    if elevation is None:
        return {"state": "UNKNOWN", "provider": "Open-Meteo", "dataset": "Open-Meteo elevation", "latitude": float(latitude), "longitude": float(longitude), "elevation_m": None, "surveyed": False, "decision_created": False}
    return {"state": "AVAILABLE", "provider": "Open-Meteo", "dataset": "Open-Meteo elevation", "latitude": float(latitude), "longitude": float(longitude), "elevation_m": float(elevation), "vertical_reference": "provider-defined elevation datum", "resolution": "provider model/grid dependent", "retrieved_at": datetime.now(timezone.utc).isoformat(), "surveyed": False, "limitations": ["Remote terrain data is not a topographic survey.", "Point elevation does not establish slope, flood risk or regulatory condition."], "decision_created": False}


__all__ = ["SCOPE_QUERY_WINDOWS", "build_bounded_overpass_query", "normalize_overpass_response", "fetch_overpass", "query_external_context", "fetch_open_meteo_elevation"]
