"""Provider-neutral georeferenced site foundation.

This module intentionally uses only the Python standard library. It normalizes
reference points, coordinate polygons and KML/KMZ into the existing
SpatialLocation representation; it does not create a second site model.
"""
from __future__ import annotations

import io
import math
import zipfile
from datetime import datetime, timezone
from typing import Any
from xml.etree import ElementTree

EARTH_RADIUS_M = 6_378_137.0
SUPPORTED_CRS = {"EPSG:4326", "EPSG:3857"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coordinates(text: str) -> list[list[float]]:
    result: list[list[float]] = []
    for token in text.replace("\n", " ").split():
        values = token.split(",")
        if len(values) < 2:
            continue
        result.append([float(values[0]), float(values[1]), float(values[2]) if len(values) > 2 and values[2] else 0.0])
    return result


def _polygon_area(points: list[list[float]]) -> float:
    return abs(sum(points[index][0] * points[(index + 1) % len(points)][1] - points[(index + 1) % len(points)][0] * points[index][1] for index in range(len(points))) / 2.0)


def _segments_intersect(a: list[float], b: list[float], c: list[float], d: list[float]) -> bool:
    def orientation(p: list[float], q: list[float], r: list[float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    def on_segment(p: list[float], q: list[float], r: list[float]) -> bool:
        return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])
    o1, o2, o3, o4 = orientation(a, b, c), orientation(a, b, d), orientation(c, d, a), orientation(c, d, b)
    if o1 == 0 and on_segment(a, c, b): return True
    if o2 == 0 and on_segment(a, d, b): return True
    if o3 == 0 and on_segment(c, a, d): return True
    if o4 == 0 and on_segment(c, b, d): return True
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def validate_polygon(coordinates: list[list[float]], crs: str = "EPSG:4326") -> dict[str, Any]:
    errors: list[str] = []
    observations: list[str] = []
    if crs not in SUPPORTED_CRS:
        errors.append("UNKNOWN_OR_UNSUPPORTED_CRS")
    if len(coordinates) < 4:
        errors.append("MINIMUM_VERTEX_COUNT")
    if coordinates and coordinates[0][:2] != coordinates[-1][:2]:
        errors.append("BOUNDARY_NOT_CLOSED")
    if len({tuple(point[:2]) for point in coordinates}) < 3:
        errors.append("DUPLICATE_OR_DEGENERATE_VERTICES")
    if coordinates and _polygon_area(coordinates) == 0:
        errors.append("ZERO_AREA")
    for index in range(max(0, len(coordinates) - 1)):
        for other in range(index + 1, max(0, len(coordinates) - 1)):
            if abs(index - other) <= 1 or {index, other} == {0, len(coordinates) - 2}:
                continue
            if _segments_intersect(coordinates[index], coordinates[index + 1], coordinates[other], coordinates[other + 1]):
                errors.append("SELF_INTERSECTION")
                break
        if "SELF_INTERSECTION" in errors:
            break
    if crs == "EPSG:4326":
        if any(not -180 <= point[0] <= 180 or not -90 <= point[1] <= 90 for point in coordinates):
            errors.append("COORDINATE_RANGE")
    if errors:
        state = "INVALID"
    elif observations:
        state = "VALID_WITH_OBSERVATIONS"
    else:
        state = "VALID"
    return {"state": state, "errors": sorted(set(errors)), "observations": observations, "vertex_count": len(coordinates), "area_source_units": "CRS units"}


def _extract_kml(data: bytes, filename: str = "site.kml") -> tuple[bytes, dict[str, Any]]:
    if filename.lower().endswith(".kmz") or data[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = archive.namelist()
                if any(name.startswith("/") or ".." in name.replace("\\", "/").split("/") for name in names):
                    raise ValueError("KMZ_PATH_TRAVERSAL")
                if len(names) > 100 or sum(info.file_size for info in archive.infolist()) > 20 * 1024 * 1024:
                    raise ValueError("KMZ_RESOURCE_LIMIT")
                kml_names = [name for name in names if name.lower().endswith(".kml")]
                if not kml_names:
                    raise ValueError("KMZ_NO_KML")
                return archive.read(kml_names[0]), {"archive_entries": len(names), "kml_member": kml_names[0]}
        except zipfile.BadZipFile as exc:
            raise ValueError("INVALID_KMZ") from exc
    return data, {"archive_entries": 0, "kml_member": None}


def parse_kml(data: bytes, filename: str = "site.kml") -> dict[str, Any]:
    raw, archive = _extract_kml(data, filename)
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError as exc:
        raise ValueError("INVALID_KML_XML") from exc
    polygons: list[dict[str, Any]] = []
    points: list[dict[str, Any]] = []
    lines: list[dict[str, Any]] = []
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "Polygon":
            coord = next((child.text for child in element.iter() if child.tag.rsplit("}", 1)[-1] == "coordinates" and child.text), None)
            if coord:
                polygons.append({"type": "Polygon", "coordinates": [_coordinates(coord)], "name": next((child.text for child in element.iter() if child.tag.rsplit("}", 1)[-1] == "name"), None)})
        elif tag == "Point":
            coord = next((child.text for child in element.iter() if child.tag.rsplit("}", 1)[-1] == "coordinates" and child.text), None)
            if coord:
                points.append({"type": "Point", "coordinates": _coordinates(coord)[:1]})
        elif tag == "LineString":
            coord = next((child.text for child in element.iter() if child.tag.rsplit("}", 1)[-1] == "coordinates" and child.text), None)
            if coord:
                lines.append({"type": "LineString", "coordinates": [_coordinates(coord)]})
    geometries = polygons + points + lines
    if len(polygons) == 1 and not points and not lines:
        classification = "VALID_SINGLE_POLYGON"
    elif len(polygons) > 1:
        classification = "MULTIPLE_POLYGONS" if not points and not lines else "AMBIGUOUS_SITE_BOUNDARY"
    elif points and not polygons and not lines:
        classification = "POINT_ONLY"
    elif lines and not polygons and not points:
        classification = "LINE_ONLY"
    elif geometries:
        classification = "MIXED_GEOMETRY"
    else:
        classification = "UNSUPPORTED_CONTENT"
    validation = validate_polygon(polygons[0]["coordinates"][0]) if len(polygons) == 1 else None
    return {"classification": classification, "geometries": geometries, "polygon_count": len(polygons), "point_count": len(points), "line_count": len(lines), "validation": validation, "source": {"filename": filename, "retrieved_at": _now(), "source_crs": "EPSG:4326", "archive": archive, "external_references_retrieved": False}}


def normalize_reference_point(longitude: float, latitude: float, *, crs: str = "EPSG:4326", elevation: float | None = None, source: str = "USER_INPUT", accuracy: float | None = None, actor_id: str = "user", human_confirmed: bool = False) -> dict[str, Any]:
    if crs != "EPSG:4326":
        raise ValueError("PROJECTED_REFERENCE_POINT_REQUIRES_EXPLICIT_TRANSFORMATION")
    if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
        raise ValueError("INVALID_REFERENCE_POINT_OR_CRS")
    return {"geometry": {"type": "Point", "coordinates": [float(longitude), float(latitude)]}, "latitude": float(latitude), "longitude": float(longitude), "elevation": elevation, "crs": crs, "source": source, "accuracy": accuracy, "provenance": "USER_DECLARED" if source == "USER_INPUT" else "EXTERNAL", "human_confirmed": bool(human_confirmed), "actor_id": actor_id, "boundary_state": "UNKNOWN", "retrieved_at": _now()}


def local_project_frame(coordinates: list[list[float]], origin: list[float] | None = None, crs: str = "EPSG:4326") -> dict[str, Any]:
    if crs != "EPSG:4326":
        return {"status": "UNKNOWN", "reason": "PROJECTED_CRS_TRANSFORMATION_REQUIRES_EXPLICIT_PROVIDER", "crs": crs}
    origin = origin or coordinates[0]
    lon0, lat0 = float(origin[0]), float(origin[1])
    cos_lat = math.cos(math.radians(lat0))
    local = [[(point[0] - lon0) * math.pi / 180 * EARTH_RADIUS_M * cos_lat, (point[1] - lat0) * math.pi / 180 * EARTH_RADIUS_M, point[2] if len(point) > 2 else 0.0] for point in coordinates]
    return {"status": "DERIVED", "source_crs": crs, "working_crs": "LOCAL_PROJECT_METRIC", "origin": [lon0, lat0], "units": "m", "transformation": "equirectangular_local_frame", "coordinates": local, "provenance": "DERIVED_COMPUTATION"}


def polygon_metrics(coordinates: list[list[float]], crs: str = "EPSG:4326") -> dict[str, Any]:
    frame = local_project_frame(coordinates, crs=crs)
    if frame.get("status") != "DERIVED": return {"status": "UNKNOWN", "reason": frame.get("reason")}
    local = frame["coordinates"]
    area = _polygon_area(local)
    perimeter = sum(math.dist(local[index][:2], local[index + 1][:2]) for index in range(len(local) - 1))
    min_x, max_x = min(point[0] for point in local), max(point[0] for point in local)
    min_y, max_y = min(point[1] for point in local), max(point[1] for point in local)
    centroid_x = sum(point[0] for point in local[:-1]) / max(1, len(local) - 1)
    centroid_y = sum(point[1] for point in local[:-1]) / max(1, len(local) - 1)
    return {"status": "DERIVED", "area_m2": round(area, 3), "perimeter_m": round(perimeter, 3), "centroid_local_m": [round(centroid_x, 3), round(centroid_y, 3)], "bounding_box_local_m": [round(min_x, 3), round(min_y, 3), round(max_x, 3), round(max_y, 3)], "vertex_count": len(coordinates), "true_north_degrees": 0.0, "units": "m", "crs": crs, "method": "local_project_frame_equirectangular", "provenance": "DERIVED_COMPUTATION"}


def site_intelligence(*, terrain_available: bool = False, context_available: bool = False) -> dict[str, Any]:
    return {"terrain": {"state": "AVAILABLE" if terrain_available else "UNAVAILABLE / UNKNOWN", "source": None if not terrain_available else "EXTERNAL_PROVIDER", "surveyed": False}, "context": {"state": "AVAILABLE" if context_available else "UNAVAILABLE / UNKNOWN", "source": None if not context_available else "EXTERNAL_PROVIDER"}, "limitations": ["No terrain provider is configured for this local proof.", "No context provider is configured for this local proof.", "Remote terrain data would not constitute a topographic survey.", "External roads do not establish legal access."]}


def point_in_polygon(point: list[float], ring: list[list[float]]) -> bool:
    inside = False
    for index in range(len(ring) - 1):
        x1, y1 = ring[index][:2]; x2, y2 = ring[index + 1][:2]
        if ((y1 > point[1]) != (y2 > point[1])) and point[0] < (x2 - x1) * (point[1] - y1) / ((y2 - y1) or 1e-12) + x1:
            inside = not inside
    return inside


def site_fit(site_geometry: dict[str, Any], building_geometry: dict[str, Any]) -> dict[str, Any]:
    """Classify only geometric fit; never infer buildability or compliance."""
    site_ring = site_geometry.get("coordinates", [[]])[0] if site_geometry.get("type") == "Polygon" else []
    building_ring = building_geometry.get("coordinates", [[]])[0] if building_geometry.get("type") == "Polygon" else []
    if len(site_ring) < 4 or len(building_ring) < 4:
        return {"state": "UNKNOWN", "reason": "SUPPORTED_POLYGON_GEOMETRY_REQUIRED", "regulatory_compliance": "UNKNOWN", "buildability": "UNKNOWN"}
    inside = [point_in_polygon(point, site_ring) for point in building_ring[:-1]]
    if all(inside): state = "INSIDE"
    elif any(inside): state = "INTERSECTING"
    else:
        state = "OUTSIDE"
    return {"state": state, "regulatory_compliance": "UNKNOWN", "setback_compliance": "UNKNOWN", "buildability": "UNKNOWN", "method": "point_in_polygon_only", "provenance": "DERIVED_COMPUTATION"}


def terrain_query(*, provider: Any = None, site_geometry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Provider-neutral terrain hook; unavailable terrain never invalidates a site."""
    if provider is None:
        return {"state": "UNAVAILABLE / UNKNOWN", "provider": None, "samples": [], "limitations": ["No terrain provider configured.", "Remote terrain data is not a topographic survey."]}
    try:
        return {"state": "AVAILABLE", "provider": getattr(provider, "name", "EXTERNAL_PROVIDER"), "result": provider(site_geometry), "surveyed": False}
    except Exception as exc:
        return {"state": "UNAVAILABLE / UNKNOWN", "provider": getattr(provider, "name", "EXTERNAL_PROVIDER"), "error": str(exc), "surveyed": False}


def context_query(*, provider: Any = None, site_geometry: dict[str, Any] | None = None, extent: str = "IMMEDIATE") -> dict[str, Any]:
    """Bounded context hook; external context is never treated as verified fact."""
    if provider is None:
        return {"state": "UNAVAILABLE / UNKNOWN", "extent": extent, "features": [], "limitations": ["No context provider configured.", "External roads do not establish legal access.", "Map buildings are not verified buildings."]}
    try:
        return {"state": "AVAILABLE", "extent": extent, "features": provider(site_geometry, extent), "source_type": "EXTERNAL_SOURCE"}
    except Exception as exc:
        return {"state": "UNAVAILABLE / UNKNOWN", "extent": extent, "error": str(exc)}


__all__ = ["parse_kml", "validate_polygon", "normalize_reference_point", "local_project_frame", "polygon_metrics", "site_intelligence", "point_in_polygon", "site_fit", "terrain_query", "context_query"]
