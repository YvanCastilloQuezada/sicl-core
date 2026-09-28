"""ARE-003 deterministic 2D architectural plan projection.

The engine derives renderer-neutral ``GraphicScene`` objects from the D2 model.
It deliberately does not import drawing backends, create SVG/PDF, mutate D2,
or record H-001 derivations.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Sequence

from .archi.model import ArchiElement, ElementKind, GeometryKind
from .representation import (
    AnnotationProfile,
    GraphicEntity,
    GraphicScene,
    GraphicStyle,
    GraphicTrace,
    ProjectionKind,
    RepresentationError,
    RepresentationProfile,
    SourceSnapshot,
    ViewDefinition,
    ViewFamily,
    ViewType,
    build_scene,
)

PROJECTION_VERSION = "arki-plan-projection-v1"
_CUT_RE = re.compile(r"^z_mm=(?P<value>[0-9]+(?:\.[0-9]+)?)$")


class ProjectionError(RepresentationError):
    """Raised when a requested projection cannot be proven from D2 evidence."""


def canonical_d2_fingerprint(elements: Sequence[ArchiElement]) -> str:
    """Return the stable fingerprint of the supplied D2 architectural state."""
    payload = [element.semantic_dict() for element in sorted(elements, key=lambda item: item.element_id.value)]
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cut_plane_mm(view: ViewDefinition) -> float:
    if view.view_type is not ViewType.ARCHITECTURAL_PLAN:
        raise ProjectionError("UNSUPPORTED_VIEW")
    if view.view_family is not ViewFamily.GEOMETRIC:
        raise ProjectionError("INVALID_PROFILE")
    if view.projection is not ProjectionKind.ORTHOGRAPHIC:
        raise ProjectionError("UNSUPPORTED_PROJECTION")
    if not view.cut_plane:
        raise ProjectionError("MISSING_CUT_PLANE")
    match = _CUT_RE.fullmatch(view.cut_plane.strip())
    if match is None:
        raise ProjectionError("UNKNOWN_CUT_PLANE")
    return float(match.group("value"))


def _visibility(element: ArchiElement, cut_mm: float) -> str:
    bottom = element.geometry.z_mm
    top = bottom + element.geometry.height_mm
    if bottom <= cut_mm <= top:
        return "CUT"
    if bottom > cut_mm:
        return "ABOVE_BEYOND"
    return "NOT_VISIBLE"


def _geometry_intent(element: ArchiElement, visibility: str) -> dict[str, object]:
    geometry = element.geometry
    if geometry.kind is GeometryKind.EXTRUDED_RECTANGLE:
        return {
            "kind": "rectangle",
            "units": "mm",
            "x_mm": geometry.x_mm,
            "y_mm": geometry.y_mm,
            "width_mm": geometry.profile.width_mm,
            "depth_mm": geometry.profile.depth_mm,
            "visibility": visibility,
            "model_space": "D2_LOCAL_MM",
            "view_space": "PLAN_XY_MM",
        }
    if geometry.kind is GeometryKind.EXTRUDED_CIRCLE:
        if geometry.profile.radius_mm is None:
            raise ProjectionError(f"UNSUPPORTED_GEOMETRY:{element.element_id.value}")
        return {
            "kind": "circle",
            "units": "mm",
            "center_x_mm": geometry.x_mm,
            "center_y_mm": geometry.y_mm,
            "radius_mm": geometry.profile.radius_mm,
            "visibility": visibility,
            "model_space": "D2_LOCAL_MM",
            "view_space": "PLAN_XY_MM",
        }
    raise ProjectionError(f"UNSUPPORTED_GEOMETRY:{element.element_id.value}")


def _role(element: ArchiElement, visibility: str) -> str:
    if element.kind is ElementKind.WALL:
        return "WALL_CUT" if visibility == "CUT" else "WALL_PROJECTED"
    if element.kind is ElementKind.SPACE:
        return "SPACE_BOUNDARY"
    if element.kind is ElementKind.OPENING:
        return "OPENING_CUT" if visibility == "CUT" else "OPENING_PROJECTED"
    if element.kind is ElementKind.DOOR:
        return "DOOR_EVIDENCE"
    if element.kind is ElementKind.WINDOW:
        return "WINDOW_EVIDENCE"
    if element.kind is ElementKind.COLUMN:
        return "COLUMN_CUT" if visibility == "CUT" else "COLUMN_PROJECTED"
    if element.kind is ElementKind.SLAB:
        return "SLAB_PROJECTED"
    if element.kind is ElementKind.BEAM:
        return "BEAM_PROJECTED"
    raise ProjectionError(f"UNSUPPORTED_ELEMENT_KIND:{element.kind.value}")


def _entity_id(element: ArchiElement, view: ViewDefinition, role: str) -> str:
    payload = {
        "source_entity": element.element_id.value,
        "view": view.view_id,
        "operation": "CUT_PROJECTION",
        "role": role,
        "transform_version": PROJECTION_VERSION,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "G-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def project_architectural_plan(
    elements: Sequence[ArchiElement],
    source_snapshot: SourceSnapshot,
    view: ViewDefinition,
    representation_profile: RepresentationProfile,
    graphic_style: GraphicStyle,
    annotation_profile: AnnotationProfile,
    *,
    canonical_source: SourceSnapshot | None = None,
) -> GraphicScene:
    """Project supported D2 evidence into one deterministic architectural plan scene."""
    cut_mm = _cut_plane_mm(view)
    if source_snapshot.authority.value != "CANONICAL_SOURCE" and canonical_source is None:
        raise ProjectionError("SOURCE_AUTHORITY_REQUIRED")
    if not elements:
        raise ProjectionError("EMPTY_D2_SOURCE")
    project_ids = {element.project_id for element in elements}
    if len(project_ids) != 1:
        raise ProjectionError("MULTIPLE_PROJECTS")
    if source_snapshot.source_fingerprint != canonical_d2_fingerprint(elements):
        raise ProjectionError("SOURCE_FINGERPRINT_MISMATCH")

    projected: list[GraphicEntity] = []
    for element in sorted(elements, key=lambda item: item.element_id.value):
        visibility = _visibility(element, cut_mm)
        if visibility == "NOT_VISIBLE":
            continue
        role = _role(element, visibility)
        geometry_intent = _geometry_intent(element, visibility)
        projected.append(
            GraphicEntity(
                entity_id=_entity_id(element, view, role),
                role=role,
                geometry_intent=geometry_intent,
                trace=GraphicTrace(
                    source_entity_refs=(element.element_id.value,),
                    semantic_role=role,
                    operation="ARE-003:ARCHITECTURAL_PLAN:CUT_PROJECTION",
                    source_version=str(element.version),
                    source_fingerprint=element.content_hash(),
                ),
                style_ref=graphic_style.style_id,
            )
        )

    return build_scene(
        source_snapshot,
        view,
        representation_profile,
        graphic_style,
        annotation_profile,
        PROJECTION_VERSION,
        canonical_source=canonical_source,
        entities=tuple(projected),
    )


__all__ = [
    "PROJECTION_VERSION",
    "ProjectionError",
    "canonical_d2_fingerprint",
    "project_architectural_plan",
]
