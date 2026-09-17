"""Deterministic UPAO-001 spatial generator (S2).

S2 generates an in-memory derived :class:`SpatialRepresentation`. It does not
persist data, expose an API, render geometry, create alternatives, or create
human decisions. UPAO-001 data in this module is explicitly synthetic and
educational.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Any, Mapping, Sequence

from .domain import SpatialScope
from .spatial import (
    DEFAULT_COORDINATE_SYSTEM,
    DEFAULT_UNITS,
    REPRESENTATION_VERSION,
    SpatialElement,
    SpatialRepresentation,
    SpatialValidationError,
    canonical_json,
    input_fingerprint,
    spatial_element_id,
)
from .v11 import Alternative

GENERATOR_VERSION = "upao001-spatial-v1"
CONTROLLED_ELEMENT_TYPES = frozenset(
    {"SiteBoundary", "BuildingFootprint", "BuildingMass", "SpatialZone", "CirculationElement"}
)
MODEL_MAX_FLOORS = 6
EPSILON = 1e-9
GEOMETRY_PARAMETER_KEYS = frozenset(
    {
        "strategy",
        "footprint_ratio",
        "floors",
        "courtyard_ratio",
        "mass_separation",
        "orientation",
        "floor_to_floor",
        "access_side",
    }
)


class SpatialGenerationError(ValueError):
    """Explicit error raised when S2 cannot generate valid geometry."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class UPAO001Site:
    """Synthetic local site model used only when a caller supplies it explicitly."""

    polygon: tuple[tuple[float, float], ...]
    north_degrees: float = 0.0
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    provenance: str = "SYNTHETIC / EDUCATIONAL / MODEL PROJECT"


# Explicit educational fixture: a 40 m x 30 m local site, not a survey or
# certified regulatory source.
DEFAULT_UPAO001_SITE = UPAO001Site(
    polygon=((0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0), (0.0, 0.0)),
    north_degrees=0.0,
)


def normalize_north(north_degrees: float) -> float:
    if isinstance(north_degrees, bool) or not isinstance(north_degrees, (int, float)):
        raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", "north_degrees must be numeric")
    if not math.isfinite(float(north_degrees)):
        raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", "north_degrees must be finite")
    return float(north_degrees) % 360.0


def _number(value: Any, name: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", f"{name} must be finite numeric")
    number = float(value)
    if minimum is not None and number < minimum:
        raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", f"{name} must be >= {minimum}")
    return number


def _ring_area(ring: Sequence[Sequence[float]]) -> float:
    if len(ring) < 4:
        raise SpatialGenerationError("INVALID_FOOTPRINT", "polygon ring requires at least three vertices and closure")
    if tuple(ring[0]) != tuple(ring[-1]):
        raise SpatialGenerationError("INVALID_FOOTPRINT", "polygon ring must be closed")
    area = 0.0
    for left, right in zip(ring, ring[1:]):
        area += float(left[0]) * float(right[1]) - float(right[0]) * float(left[1])
    return abs(area) / 2.0


def _polygon_area(geometry: Mapping[str, Any]) -> float:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type == "polygon":
        if not isinstance(coordinates, list) or len(coordinates) != 1:
            raise SpatialGenerationError("INVALID_FOOTPRINT", "S2 polygon must have one outer ring")
        return _ring_area(coordinates[0])
    if geometry_type == "multipolygon":
        if not isinstance(coordinates, list) or not coordinates:
            raise SpatialGenerationError("INVALID_FOOTPRINT", "S2 multipolygon requires polygons")
        return sum(_ring_area(polygon[0]) for polygon in coordinates)
    raise SpatialGenerationError("INVALID_FOOTPRINT", f"unsupported footprint geometry: {geometry_type!r}")


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[list[float]]:
    if x1 <= x0 or y1 <= y0:
        raise SpatialGenerationError("DEGENERATE_GEOMETRY", "rectangle has no positive area")
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]


def _polygon_geometry(ring: list[list[float]]) -> dict[str, Any]:
    return {"type": "polygon", "coordinates": [ring]}


def _multipolygon_geometry(rings: list[list[list[float]]]) -> dict[str, Any]:
    return {"type": "multipolygon", "coordinates": [[ring] for ring in rings]}


def _point_in_ring(point: Sequence[float], ring: Sequence[Sequence[float]]) -> bool:
    x, y = point
    inside = False
    for left, right in zip(ring, ring[1:]):
        x1, y1 = left
        x2, y2 = right
        crosses = (y1 > y) != (y2 > y)
        if crosses and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def _point_in_geometry(point: Sequence[float], geometry: Mapping[str, Any]) -> bool:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])
    if geometry_type == "polygon":
        return _point_in_ring(point, coordinates[0])
    if geometry_type == "multipolygon":
        return any(_point_in_ring(point, polygon[0]) for polygon in coordinates)
    return False


def _all_vertices(geometry: Mapping[str, Any]) -> list[list[float]]:
    if geometry["type"] == "polygon":
        return [list(point) for point in geometry["coordinates"][0][:-1]]
    return [list(point) for polygon in geometry["coordinates"] for point in polygon[0][:-1]]


def _validate_site(site: UPAO001Site) -> None:
    if len(site.polygon) < 4 or site.polygon[0] != site.polygon[-1]:
        raise SpatialGenerationError("INVALID_SITE", "site polygon must be closed with at least three vertices")
    geometry = _polygon_geometry([list(point) for point in site.polygon])
    if _polygon_area(geometry) <= EPSILON:
        raise SpatialGenerationError("INVALID_SITE", "site polygon must have positive area")
    if len(site.origin) != 3 or any(not math.isfinite(float(value)) for value in site.origin):
        raise SpatialGenerationError("INVALID_SITE", "site origin must have three finite coordinates")
    normalize_north(site.north_degrees)


def _validate_footprint(geometry: Mapping[str, Any], site_geometry: Mapping[str, Any]) -> None:
    area = _polygon_area(geometry)
    if area <= EPSILON:
        raise SpatialGenerationError("DEGENERATE_GEOMETRY", "footprint area must be positive")
    for vertex in _all_vertices(geometry):
        if not _point_in_geometry(vertex, site_geometry):
            raise SpatialGenerationError("FOOTPRINT_OUTSIDE_SITE", "footprint vertex lies outside site boundary")


def _volume_from_ring(ring: list[list[float]], base: float, height: float) -> dict[str, Any]:
    bottom = [[point[0], point[1], base] for point in ring[:-1]]
    top = [[point[0], point[1], base + height] for point in ring[:-1]]
    return {"type": "volume", "coordinates": bottom + top}


def _stable_representation_id(alternative_id: str, fingerprint: str) -> str:
    digest = hashlib.sha256(
        canonical_json(
            {
                "alternative_id": alternative_id,
                "generator_version": GENERATOR_VERSION,
                "representation_version": REPRESENTATION_VERSION,
                "input_fingerprint": fingerprint,
            }
        ).encode("utf-8")
    ).hexdigest()[:16]
    return f"SR-{alternative_id}-{digest}"


def _strategy(parameters: Mapping[str, Any]) -> str:
    value = str(parameters.get("strategy", "")).strip().lower()
    if value not in {"compact", "courtyard", "articulated"}:
        raise SpatialGenerationError(
            "INVALID_PARAMETER_COMBINATION",
            "strategy must be one of compact, courtyard, articulated",
        )
    return value


def _default_parameters(strategy: str) -> dict[str, Any]:
    return {
        "strategy": strategy,
        "footprint_ratio": {"compact": 0.42, "courtyard": 0.50, "articulated": 0.36}[strategy],
        "floors": {"compact": 5, "courtyard": 4, "articulated": 3}[strategy],
        "courtyard_ratio": 0.25 if strategy == "courtyard" else 0.0,
        "mass_separation": 4.0 if strategy == "articulated" else 0.0,
        "access_side": "south",
    }


def _merge_parameters(parameters: Mapping[str, Any]) -> dict[str, Any]:
    strategy = _strategy(parameters)
    merged = _default_parameters(strategy)
    merged.update(dict(parameters))
    return merged


class UPAO001SpatialGenerator:
    """Generate deterministic analytical geometry for the synthetic UPAO case."""

    generator_version = GENERATOR_VERSION

    def generate(
        self,
        alternative: Alternative,
        *,
        site: UPAO001Site | None = None,
        constraints: Mapping[str, Any] | None = None,
        seed: int | str | None = None,
    ) -> SpatialRepresentation:
        if not isinstance(alternative, Alternative):
            raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", "alternative must be an Alternative")
        parameters = _merge_parameters(alternative.parameters)
        site_model = site or DEFAULT_UPAO001_SITE
        _validate_site(site_model)
        normalized_north = normalize_north(parameters.get("orientation", site_model.north_degrees))
        model_constraints = dict(constraints or {})
        floor_count = int(_number(parameters["floors"], "floors", minimum=1))
        max_floors = int(model_constraints.get("max_floors", MODEL_MAX_FLOORS))
        if floor_count > max_floors:
            raise SpatialGenerationError(
                "INVALID_FLOOR_COUNT",
                f"floor count {floor_count} exceeds model constraint {max_floors}",
            )
        footprint_ratio = _number(parameters["footprint_ratio"], "footprint_ratio", minimum=0.01)
        if footprint_ratio >= 1.0:
            raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", "footprint_ratio must be below 1")
        courtyard_ratio = _number(parameters.get("courtyard_ratio", 0.0), "courtyard_ratio", minimum=0.0)
        separation = _number(parameters.get("mass_separation", 0.0), "mass_separation", minimum=0.0)

        site_geometry = _polygon_geometry([list(point) for point in site_model.polygon])
        xs = [point[0] for point in site_model.polygon[:-1]]
        ys = [point[1] for point in site_model.polygon[:-1]]
        sx0, sx1, sy0, sy1 = min(xs), max(xs), min(ys), max(ys)
        site_width, site_depth = sx1 - sx0, sy1 - sy0
        margin = min(site_width, site_depth) * 0.10
        usable_x0, usable_x1 = sx0 + margin, sx1 - margin
        usable_y0, usable_y1 = sy0 + margin, sy1 - margin
        usable_width, usable_depth = usable_x1 - usable_x0, usable_y1 - usable_y0
        footprint_width = usable_width * math.sqrt(footprint_ratio)
        footprint_depth = usable_depth * math.sqrt(footprint_ratio)
        cx, cy = (usable_x0 + usable_x1) / 2, (usable_y0 + usable_y1) / 2
        rings: list[list[list[float]]]
        if parameters["strategy"] == "compact":
            rings = [_rect(cx - footprint_width / 2, cy - footprint_depth / 2, cx + footprint_width / 2, cy + footprint_depth / 2)]
        elif parameters["strategy"] == "courtyard":
            outer = _rect(cx - footprint_width / 2, cy - footprint_depth / 2, cx + footprint_width / 2, cy + footprint_depth / 2)
            courtyard_w = footprint_width * min(courtyard_ratio, 0.55)
            courtyard_d = footprint_depth * min(courtyard_ratio, 0.55)
            if courtyard_w <= EPSILON or courtyard_d <= EPSILON:
                raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", "courtyard_ratio must be positive for courtyard strategy")
            ix0, ix1 = cx - courtyard_w / 2, cx + courtyard_w / 2
            iy0, iy1 = cy - courtyard_d / 2, cy + courtyard_d / 2
            rings = [
                _rect(outer[0][0], outer[0][1], ix0 - 0.5, outer[2][1]),
                _rect(ix1 + 0.5, outer[0][1], outer[2][0], outer[2][1]),
                _rect(ix0 - 0.5, outer[0][1], ix1 + 0.5, iy0 - 0.5),
                _rect(ix0 - 0.5, iy1 + 0.5, ix1 + 0.5, outer[2][1]),
            ]
        else:
            mass_width = footprint_width * 0.43
            mass_depth = footprint_depth * 0.85
            left_cx = cx - separation / 2 - mass_width / 2
            right_cx = cx + separation / 2 + mass_width / 2
            rings = [
                _rect(left_cx - mass_width / 2, cy - mass_depth / 2, left_cx + mass_width / 2, cy + mass_depth / 2),
                _rect(right_cx - mass_width / 2, cy - mass_depth / 2, right_cx + mass_width / 2, cy + mass_depth / 2),
            ]
        footprint_geometry = _polygon_geometry(rings[0]) if len(rings) == 1 else _multipolygon_geometry(rings)
        _validate_footprint(footprint_geometry, site_geometry)
        for ring in rings:
            _validate_footprint(_polygon_geometry(ring), site_geometry)

        floor_to_floor = _number(parameters.get("floor_to_floor", 3.2), "floor_to_floor", minimum=0.1)
        height = floor_count * floor_to_floor
        access = {
            "south": [cx, sy0 + margin / 2],
            "north": [cx, sy1 - margin / 2],
            "east": [sx1 - margin / 2, cy],
            "west": [sx0 + margin / 2, cy],
        }.get(str(parameters.get("access_side", "south")).lower())
        if access is None:
            raise SpatialGenerationError("INVALID_PARAMETER_COMBINATION", "access_side must be south, north, east, or west")

        relevant_parameters = {
            key: parameters[key]
            for key in sorted(GEOMETRY_PARAMETER_KEYS)
            if key in parameters
        }
        relevant_inputs = {
            "alternative_id": alternative.alternative_id,
            "site": {"polygon": site_model.polygon, "origin": site_model.origin, "north_degrees": normalized_north},
            "constraints": model_constraints,
            "parameters": relevant_parameters,
            "generator_version": GENERATOR_VERSION,
            "representation_version": REPRESENTATION_VERSION,
            "seed": seed,
        }
        fingerprint = input_fingerprint(relevant_inputs)
        prefix = {"compact": "compact", "courtyard": "courtyard", "articulated": "articulated"}[parameters["strategy"]]
        elements: list[SpatialElement] = []
        site_id = spatial_element_id(alternative.alternative_id, "SiteBoundary", "site", generator_version=GENERATOR_VERSION)
        site_element = SpatialElement(
            id=site_id,
            element_type="SiteBoundary",
            geometry=site_geometry,
            labels={"en": "Site boundary", "es": "Límite del sitio"},
            metadata={"semantic_key": "site", "provenance": site_model.provenance, "origin": list(site_model.origin)},
        )
        elements.append(site_element)
        footprint_id = spatial_element_id(alternative.alternative_id, "BuildingFootprint", "footprint-main", generator_version=GENERATOR_VERSION)
        elements.append(
            SpatialElement(
                id=footprint_id,
                element_type="BuildingFootprint",
                geometry=footprint_geometry,
                parent_id=site_id,
                labels={"en": "Building footprint", "es": "Huella del edificio"},
                metadata={"semantic_key": "footprint-main", "area": _polygon_area(footprint_geometry), "strategy": parameters["strategy"]},
            )
        )

        mass_ids: list[str] = []
        for index, ring in enumerate(rings):
            semantic_key = "mass-main" if len(rings) == 1 else f"mass-{index + 1:02d}"
            mass_id = spatial_element_id(alternative.alternative_id, "BuildingMass", semantic_key, generator_version=GENERATOR_VERSION)
            mass_ids.append(mass_id)
            mass_floor_count = floor_count if len(rings) == 1 else max(1, floor_count - (index % 2))
            mass_height = mass_floor_count * floor_to_floor
            elements.append(
                SpatialElement(
                    id=mass_id,
                    element_type="BuildingMass",
                    geometry=_volume_from_ring(ring, 0.0, mass_height),
                    parent_id=footprint_id,
                    labels={"en": f"Building mass {index + 1}", "es": f"Masa edificada {index + 1}"},
                    metadata={
                        "semantic_key": semantic_key,
                        "footprint_reference": footprint_id,
                        "base_elevation": 0.0,
                        "height": mass_height,
                        "floor_count": mass_floor_count,
                        "floor_to_floor_height": floor_to_floor,
                        "strategy": parameters["strategy"],
                        "provenance": "SYNTHETIC / ASSUMED",
                    },
                )
            )

        zone_specs = [
            ("commercial", "commercial", mass_ids[0], 0),
            ("residential", "residential", mass_ids[-1], max(0, floor_count - 1)),
            ("circulation-service", "circulation/service", mass_ids[0], 0),
        ]
        for semantic_key, program, parent_mass, level in zone_specs:
            ring = rings[0]
            min_x = min(point[0] for point in ring[:-1])
            max_x = max(point[0] for point in ring[:-1])
            min_y = min(point[1] for point in ring[:-1])
            max_y = max(point[1] for point in ring[:-1])
            mid_y = min_y + (max_y - min_y) * (0.33 if semantic_key == "commercial" else 0.66)
            zone_ring = _rect(min_x + 0.5, max(min_y + 0.5, mid_y - 1.5), max_x - 0.5, min(max_y - 0.5, mid_y + 1.5))
            zone_id = spatial_element_id(alternative.alternative_id, "SpatialZone", f"zone-{semantic_key}", generator_version=GENERATOR_VERSION)
            elements.append(
                SpatialElement(
                    id=zone_id,
                    element_type="SpatialZone",
                    geometry=_polygon_geometry(zone_ring),
                    level=level,
                    parent_id=parent_mass,
                    labels={"en": program, "es": program},
                    metadata={"semantic_key": f"zone-{semantic_key}", "program": program, "area": _ring_area(zone_ring), "provenance": "SYNTHETIC / ASSUMED"},
                )
            )

        circulation_id = spatial_element_id(alternative.alternative_id, "CirculationElement", "circulation-core", generator_version=GENERATOR_VERSION)
        elements.append(
            SpatialElement(
                id=circulation_id,
                element_type="CirculationElement",
                geometry={"type": "line", "coordinates": [access, [cx, cy]]},
                parent_id=site_id,
                labels={"en": "Primary access and circulation", "es": "Acceso y circulación principal"},
                metadata={"semantic_key": "circulation-core", "access_point": access, "core_point": [cx, cy], "provenance": "SYNTHETIC / ASSUMED"},
            )
        )

        representation = SpatialRepresentation(
            id=_stable_representation_id(alternative.alternative_id, fingerprint),
            alternative_id=alternative.alternative_id,
            spatial_scope=SpatialScope.EDIFICACION,
            representation_version=REPRESENTATION_VERSION,
            generator_version=GENERATOR_VERSION,
            coordinate_system=DEFAULT_COORDINATE_SYSTEM,
            units=DEFAULT_UNITS,
            input_fingerprint=fingerprint,
            seed=seed,
            elements=tuple(elements),
            coordinate_origin=site_model.origin,
            north_degrees=normalized_north,
            elevation_reference="local_datum",
        )
        try:
            return representation.validate()
        except SpatialValidationError as exc:
            raise SpatialGenerationError("INVALID_GENERATED_REPRESENTATION", str(exc)) from exc

    def metrics(self, representation: SpatialRepresentation) -> dict[str, float]:
        representation.validate()
        site = next(item for item in representation.elements if item.element_type == "SiteBoundary")
        footprint = next(item for item in representation.elements if item.element_type == "BuildingFootprint")
        masses = [item for item in representation.elements if item.element_type == "BuildingMass"]
        zones = [item for item in representation.elements if item.element_type == "SpatialZone"]
        site_area = _polygon_area(site.geometry)
        footprint_area = _polygon_area(footprint.geometry)
        gross_massing_area = sum(float(item.metadata["height"]) * _polygon_area(_polygon_geometry(_volume_footprint(item.geometry))) for item in masses)
        return {
            "site_area": site_area,
            "footprint_area": footprint_area,
            "coverage_ratio": footprint_area / site_area,
            "gross_massing_area": gross_massing_area,
            "zone_area": sum(float(item.metadata.get("area", 0.0)) for item in zones),
            "height": max(float(item.metadata["height"]) for item in masses),
            "floor_count": max(float(item.metadata["floor_count"]) for item in masses),
        }

    def explain(self, representation: SpatialRepresentation) -> dict[str, Any]:
        strategy = next(
            item.metadata["strategy"]
            for item in representation.elements
            if item.element_type == "BuildingFootprint"
        )
        return {
            "alternative_id": representation.alternative_id,
            "rules": [
                {"parameter": "strategy", "value": strategy, "effect": "selects the massing arrangement"},
                {"parameter": "footprint_ratio", "effect": "controls usable-site coverage"},
                {"parameter": "floors", "effect": "controls mass height"},
            ],
            "provenance": "SYNTHETIC / EDUCATIONAL / MODEL PROJECT",
        }


def _volume_footprint(volume_geometry: Mapping[str, Any]) -> list[list[float]]:
    coordinates = volume_geometry["coordinates"]
    unique_xy: list[list[float]] = []
    for point in coordinates:
        xy = [point[0], point[1]]
        if xy not in unique_xy:
            unique_xy.append(xy)
    if unique_xy[0] != unique_xy[-1]:
        unique_xy.append(unique_xy[0])
    return unique_xy


def generate_upao001_alternatives() -> tuple[Alternative, Alternative, Alternative]:
    """Return the three explicit synthetic parameter sets used by S2 tests."""
    common = {"floor_to_floor": 3.2, "access_side": "south"}
    return (
        Alternative("UPAO-001-A", "UPAO-001", "COMPACT", parameters={**common, "strategy": "compact", "footprint_ratio": 0.42, "floors": 5}),
        Alternative("UPAO-001-B", "UPAO-001", "COURTYARD", parameters={**common, "strategy": "courtyard", "footprint_ratio": 0.50, "courtyard_ratio": 0.25, "floors": 4}),
        Alternative("UPAO-001-C", "UPAO-001", "ARTICULATED", parameters={**common, "strategy": "articulated", "footprint_ratio": 0.36, "mass_separation": 4.0, "floors": 3}),
    )


__all__ = [
    "CONTROLLED_ELEMENT_TYPES",
    "DEFAULT_UPAO001_SITE",
    "GENERATOR_VERSION",
    "MODEL_MAX_FLOORS",
    "SpatialGenerationError",
    "UPAO001Site",
    "UPAO001SpatialGenerator",
    "generate_upao001_alternatives",
    "normalize_north",
]
