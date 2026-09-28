"""ARKI-DRAW Block 2 adapter from ARE GraphicScene to vector primitives.

This module consumes GraphicScene only. It never inspects D2, IFC, spatial DTOs,
or architectural relationships. ARE has already made the representation
selection; this module performs only graphic adaptation and serialization.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import Mapping

from ..representation import GraphicEntity, GraphicScene, GraphicTrace
from .primitives import Circle, LineWeight, Point, Rect
from .scale import Scale
from .sheet import Viewport
from .svg_export import export_view_svg

ADAPTER_VERSION = "arki-draw-scene-adapter-v1"
DEFAULT_MARGIN_MM = 10.0
SUPPORTED_GRAPHIC_ROLES = frozenset({
    "WALL_CUT", "WALL_PROJECTED", "SPACE_BOUNDARY", "OPENING_CUT",
    "OPENING_PROJECTED", "DOOR_EVIDENCE", "WINDOW_EVIDENCE",
    "COLUMN_CUT", "COLUMN_PROJECTED", "SLAB_PROJECTED", "BEAM_PROJECTED",
})


class DrawingAdapterError(ValueError):
    """Raised when GraphicScene evidence cannot be adapted safely."""


@dataclass(frozen=True)
class AdaptedGraphicScene:
    """Vector drawing state plus the entity/primitive trace closure."""

    scene_id: str
    viewport: Viewport
    primitive_sources: Mapping[str, str]
    graphic_entities: Mapping[str, GraphicEntity]
    scale: Scale
    margin_mm: float
    coordinate_policy: str = "PLAN_XY_MM->SVG_DEVICE_MM; explicit_bbox_margin"
    y_axis_policy: str = "PLAN_Y_UP_TO_SVG_Y_DOWN"

    def __post_init__(self) -> None:
        object.__setattr__(self, "primitive_sources", MappingProxyType(dict(self.primitive_sources)))
        object.__setattr__(self, "graphic_entities", MappingProxyType(dict(self.graphic_entities)))
        if self.margin_mm < 0 or not math.isfinite(self.margin_mm):
            raise DrawingAdapterError("margin_mm must be finite and non-negative")

    @property
    def primitive_ids(self) -> tuple[str, ...]:
        return tuple(element.primitive_id for element in self.viewport.elements if element.primitive_id)


def _style_weight(scene: GraphicScene, role: str) -> LineWeight:
    """Resolve lineweight exclusively from GraphicStyle, with no role hardcode."""
    values = scene.graphic_style.line_weights
    raw = values.get(role, values.get("default"))
    if raw is None:
        raise DrawingAdapterError(f"STYLE_MAPPING_REQUIRED:{role}")
    text = raw.value if isinstance(raw, LineWeight) else str(raw)
    for weight in LineWeight:
        if text in {weight.value, weight.name, weight.name.lower()}:
            return weight
    raise DrawingAdapterError(f"INVALID_STYLE_LINEWEIGHT:{role}:{raw}")


def _bounds(scene: GraphicScene) -> tuple[float, float, float, float]:
    points: list[tuple[float, float]] = []
    for entity in scene.entities:
        intent = entity.geometry_intent
        kind = intent.get("kind")
        _validate_entity(scene, entity)
        if kind == "rectangle":
            x = _number(intent, "x_mm")
            y = _number(intent, "y_mm")
            width = _positive_number(intent, "width_mm")
            depth = _positive_number(intent, "depth_mm")
            points.extend(((x, y), (x + width, y + depth)))
        elif kind == "circle":
            x = _number(intent, "center_x_mm")
            y = _number(intent, "center_y_mm")
            radius = _positive_number(intent, "radius_mm")
            points.extend(((x - radius, y - radius), (x + radius, y + radius)))
        else:
            raise DrawingAdapterError(f"UNSUPPORTED_GRAPHIC_GEOMETRY:{kind}")
    if not points:
        raise DrawingAdapterError("EMPTY_GRAPHIC_SCENE")
    return min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points), max(y for _, y in points)


def _number(intent: Mapping[str, object], key: str) -> float:
    try:
        value = float(intent[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise DrawingAdapterError(f"MALFORMED_GEOMETRY:{key}") from exc
    if not math.isfinite(value):
        raise DrawingAdapterError(f"NONFINITE_GEOMETRY:{key}")
    return value


def _positive_number(intent: Mapping[str, object], key: str) -> float:
    value = _number(intent, key)
    if value <= 0:
        raise DrawingAdapterError(f"NONPOSITIVE_GEOMETRY:{key}")
    return value


def _validate_entity(scene: GraphicScene, entity: GraphicEntity) -> None:
    if entity.role not in SUPPORTED_GRAPHIC_ROLES:
        raise DrawingAdapterError(f"UNSUPPORTED_GRAPHIC_ROLE:{entity.role}")
    if not isinstance(entity.trace, GraphicTrace):
        raise DrawingAdapterError(f"MALFORMED_GRAPHIC_TRACE:{entity.entity_id}")
    intent = entity.geometry_intent
    if intent.get("visibility") != "VISIBLE":
        raise DrawingAdapterError(f"UNRESOLVED_VISIBILITY:{entity.entity_id}")
    if intent.get("cut_relation") not in {"CUT", "BELOW_CUT"}:
        raise DrawingAdapterError(f"UNRESOLVED_CUT_RELATION:{entity.entity_id}")
    if entity.style_ref != scene.graphic_style.style_id:
        raise DrawingAdapterError(f"STYLE_REFERENCE_MISMATCH:{entity.entity_id}")


def _primitive_id(scene: GraphicScene, entity: GraphicEntity, ordinal: int) -> str:
    payload = {
        "graphic_entity_id": entity.entity_id,
        "primitive_role": entity.role,
        "ordinal": ordinal,
        "adapter_version": ADAPTER_VERSION,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "P-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _entity_geometry(
    scene: GraphicScene,
    entity: GraphicEntity,
    xmin: float,
    ymin: float,
    ymax: float,
    margin_mm: float,
    scale: Scale,
) -> tuple[object, float, float]:
    intent = entity.geometry_intent
    kind = intent.get("kind")
    denominator = scale.denominator
    # Explicit device transform. The source geometry remains PLAN_XY_MM;
    # translation only establishes a deterministic viewport margin.
    def tx(value: float) -> float:
        return value - xmin + margin_mm * denominator

    def ty(value: float) -> float:
        return value - ymin + margin_mm * denominator

    weight = _style_weight(scene, entity.role)
    primitive_id = _primitive_id(scene, entity, 0)
    source_ref = entity.entity_id
    if kind == "rectangle":
        x = _number(intent, "x_mm")
        y = _number(intent, "y_mm")
        width = _positive_number(intent, "width_mm")
        depth = _positive_number(intent, "depth_mm")
        primitive = Rect(Point(tx(x), ty(y)), width, depth, weight, entity.role, primitive_id, entity.role, source_ref)
        return primitive, width, depth
    if kind == "circle":
        x = _number(intent, "center_x_mm")
        y = _number(intent, "center_y_mm")
        radius = _positive_number(intent, "radius_mm")
        primitive = Circle(Point(tx(x), ty(y)), radius, weight, entity.role, primitive_id, entity.role, source_ref)
        return primitive, radius * 2, radius * 2
    raise DrawingAdapterError(f"UNSUPPORTED_GRAPHIC_GEOMETRY:{kind}")


def adapt_graphic_scene(scene: GraphicScene, *, scale: Scale = Scale.S_1_50, margin_mm: float = DEFAULT_MARGIN_MM) -> AdaptedGraphicScene:
    """Adapt one GraphicScene to vector primitives and a deterministic viewport."""
    if not isinstance(scene, GraphicScene):
        raise DrawingAdapterError("GRAPHICSCENE_REQUIRED")
    if margin_mm < 0 or not math.isfinite(margin_mm):
        raise DrawingAdapterError("margin_mm must be finite and non-negative")
    xmin, ymin, xmax, ymax = _bounds(scene)
    paper_width = (xmax - xmin) / scale.denominator + (2 * margin_mm)
    paper_height = (ymax - ymin) / scale.denominator + (2 * margin_mm)
    if paper_width <= 0 or paper_height <= 0:
        raise DrawingAdapterError("EMPTY_GRAPHIC_SCENE")

    primitives = []
    primitive_sources: dict[str, str] = {}
    graphic_entities: dict[str, GraphicEntity] = {}
    for entity in scene.entities:
        primitive, _, _ = _entity_geometry(scene, entity, xmin, ymin, ymax, margin_mm, scale)
        primitives.append(primitive)
        primitive_sources[primitive.primitive_id] = entity.entity_id
        graphic_entities[entity.entity_id] = entity

    # export_view_svg is standalone and intentionally ignores sheet placement;
    # keep origin neutral so there is one coordinate authority in this path.
    viewport = Viewport("GRAPHICSCENE", scale, (0.0, 0.0), tuple(primitives))
    return AdaptedGraphicScene(scene.scene_id, viewport, primitive_sources, graphic_entities, scale, margin_mm)


def export_adapted_svg(adapted: AdaptedGraphicScene) -> str:
    """Serialize adapted vector state through the existing ARKI-DRAW backend."""
    if not isinstance(adapted, AdaptedGraphicScene):
        raise DrawingAdapterError("ADAPTED_GRAPHIC_SCENE_REQUIRED")
    # Coordinates were explicitly transformed into the viewport device frame;
    # export_view_svg performs only the declared scale and Y-axis serialization.
    xmin, ymin, xmax, ymax = _bounds_from_primitives(adapted.viewport)
    width = (xmax - xmin) / adapted.scale.denominator + 2 * adapted.margin_mm
    height = (ymax - ymin) / adapted.scale.denominator + 2 * adapted.margin_mm
    return export_view_svg(adapted.viewport, width, height)


def _bounds_from_primitives(viewport: Viewport) -> tuple[float, float, float, float]:
    points: list[tuple[float, float]] = []
    for primitive in viewport.elements:
        if isinstance(primitive, Rect):
            points.extend((point.x, point.y) for point in primitive.corners())
        elif isinstance(primitive, Circle):
            points.extend(((primitive.center.x - primitive.radius, primitive.center.y - primitive.radius), (primitive.center.x + primitive.radius, primitive.center.y + primitive.radius)))
        else:
            raise DrawingAdapterError(f"UNSUPPORTED_VECTOR_PRIMITIVE:{type(primitive).__name__}")
    if not points:
        raise DrawingAdapterError("EMPTY_GRAPHIC_SCENE")
    return min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points), max(y for _, y in points)


def graphic_scene_to_svg(scene: GraphicScene, *, scale: Scale = Scale.S_1_50, margin_mm: float = DEFAULT_MARGIN_MM) -> tuple[AdaptedGraphicScene, str]:
    """Convenience E2E operation: GraphicScene → adapter → existing SVG backend."""
    adapted = adapt_graphic_scene(scene, scale=scale, margin_mm=margin_mm)
    return adapted, export_adapted_svg(adapted)


__all__ = [
    "ADAPTER_VERSION",
    "AdaptedGraphicScene",
    "DrawingAdapterError",
    "adapt_graphic_scene",
    "export_adapted_svg",
    "graphic_scene_to_svg",
]
