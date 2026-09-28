"""ARKI-ARE-002 executable representation foundation.

This module defines immutable, renderer-neutral contracts only. It does not
project geometry, render, serialize to SVG/sheets, persist, mutate D2, or call
external providers.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
import hashlib
import json
import math
import re
from types import MappingProxyType
from typing import Any, Mapping, Sequence

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class RepresentationError(ValueError):
    """Base error for malformed or unsafe ARE contracts."""


class SourceConflictError(RepresentationError):
    """Raised when relevant source snapshots cannot be reconciled safely."""


class SourceAuthority(str, Enum):
    CANONICAL_SOURCE = "CANONICAL_SOURCE"
    DERIVED_SOURCE = "DERIVED_SOURCE"
    EXCHANGE_SOURCE = "EXCHANGE_SOURCE"


class ExchangeRole(str, Enum):
    AUTHORITATIVE_IMPORT = "AUTHORITATIVE_IMPORT"
    REFERENCE_IMPORT = "REFERENCE_IMPORT"
    DERIVED_EXPORT = "DERIVED_EXPORT"


class Freshness(str, Enum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class ViewFamily(str, Enum):
    KNOWLEDGE = "KNOWLEDGE"
    GEOMETRIC = "GEOMETRIC"
    VISUALIZATION = "VISUALIZATION"


class ViewType(str, Enum):
    RELATIONSHIP_DIAGRAM = "RELATIONSHIP_DIAGRAM"
    FLOW_CIRCULATION_DIAGRAM = "FLOW_CIRCULATION_DIAGRAM"
    ZONING_SCHEMATIC = "ZONING_SCHEMATIC"
    ADJACENCY_VIEW = "ADJACENCY_VIEW"
    FUNCTIONAL_TOPOLOGY_VIEW = "FUNCTIONAL_TOPOLOGY_VIEW"
    ARCHITECTURAL_PLAN = "ARCHITECTURAL_PLAN"
    SECTION = "SECTION"
    ELEVATION = "ELEVATION"
    AXONOMETRIC = "AXONOMETRIC"
    ANALYTICAL_3D = "ANALYTICAL_3D"
    CONCEPTUAL_RENDER = "CONCEPTUAL_RENDER"
    MATERIAL_RENDER = "MATERIAL_RENDER"
    INTERIOR_RENDER = "INTERIOR_RENDER"
    EXTERIOR_RENDER = "EXTERIOR_RENDER"
    AERIAL_RENDER = "AERIAL_RENDER"
    NIGHT_RENDER = "NIGHT_RENDER"
    PHOTOREALISTIC_RENDER = "PHOTOREALISTIC_RENDER"


class ProjectionKind(str, Enum):
    NONE = "NONE"
    ORTHOGRAPHIC = "ORTHOGRAPHIC"
    PERSPECTIVE = "PERSPECTIVE"
    GRAPH = "GRAPH"


class ProfileKind(str, Enum):
    CONCEPTUAL = "CONCEPTUAL"
    UNDIMENSIONED = "UNDIMENSIONED"
    DIMENSIONED = "DIMENSIONED"
    PROFESSIONAL = "PROFESSIONAL"
    PRESENTATION = "PRESENTATION"
    REGULATORY = "REGULATORY"
    ANALYTICAL = "ANALYTICAL"


class DiagnosticCode(str, Enum):
    STALE_SOURCE = "STALE_SOURCE"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    UNSUPPORTED_VIEW = "UNSUPPORTED_VIEW"
    INVALID_PROFILE = "INVALID_PROFILE"
    INVALID_SOURCE = "INVALID_SOURCE"
    MISSING_REQUIRED_EVIDENCE = "MISSING_REQUIRED_EVIDENCE"


_VIEW_FAMILY_BY_TYPE = {
    ViewType.RELATIONSHIP_DIAGRAM: ViewFamily.KNOWLEDGE,
    ViewType.FLOW_CIRCULATION_DIAGRAM: ViewFamily.KNOWLEDGE,
    ViewType.ZONING_SCHEMATIC: ViewFamily.KNOWLEDGE,
    ViewType.ADJACENCY_VIEW: ViewFamily.KNOWLEDGE,
    ViewType.FUNCTIONAL_TOPOLOGY_VIEW: ViewFamily.KNOWLEDGE,
    ViewType.ARCHITECTURAL_PLAN: ViewFamily.GEOMETRIC,
    ViewType.SECTION: ViewFamily.GEOMETRIC,
    ViewType.ELEVATION: ViewFamily.GEOMETRIC,
    ViewType.AXONOMETRIC: ViewFamily.GEOMETRIC,
    ViewType.ANALYTICAL_3D: ViewFamily.GEOMETRIC,
    ViewType.CONCEPTUAL_RENDER: ViewFamily.VISUALIZATION,
    ViewType.MATERIAL_RENDER: ViewFamily.VISUALIZATION,
    ViewType.INTERIOR_RENDER: ViewFamily.VISUALIZATION,
    ViewType.EXTERIOR_RENDER: ViewFamily.VISUALIZATION,
    ViewType.AERIAL_RENDER: ViewFamily.VISUALIZATION,
    ViewType.NIGHT_RENDER: ViewFamily.VISUALIZATION,
    ViewType.PHOTOREALISTIC_RENDER: ViewFamily.VISUALIZATION,
}


def _freeze(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise RepresentationError("ARE numeric values must be finite")
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(value[k]) for k in sorted(value, key=str)})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze(item) for item in value), key=repr))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported mutable/opaque ARE value: {type(value).__name__}")


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {item.name: _plain(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_plain(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RepresentationError(f"{name} must be a non-empty string")
    return value


def _fingerprint(value: str, name: str) -> str:
    value = _text(value, name).lower()
    if not _HEX64.fullmatch(value):
        raise RepresentationError(f"{name} must be a lowercase SHA-256 hex digest")
    return value


@dataclass(frozen=True)
class SourceSnapshot:
    source_id: str
    source_type: str
    source_version: str
    source_fingerprint: str
    authority: SourceAuthority
    exchange_role: ExchangeRole | None = None
    freshness: Freshness = Freshness.UNKNOWN
    lineage: "SourceLineage | None" = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.source_id, "source_id")
        _text(self.source_type, "source_type")
        _text(self.source_version, "source_version")
        object.__setattr__(self, "source_fingerprint", _fingerprint(self.source_fingerprint, "source_fingerprint"))
        if not isinstance(self.authority, SourceAuthority):
            raise RepresentationError("authority must be SourceAuthority")
        if self.authority is SourceAuthority.EXCHANGE_SOURCE and self.exchange_role is None:
            raise RepresentationError("exchange sources require an exchange_role")
        if self.authority is not SourceAuthority.EXCHANGE_SOURCE and self.exchange_role is not None:
            raise RepresentationError("exchange_role is only valid for exchange sources")
        if not isinstance(self.freshness, Freshness):
            raise RepresentationError("freshness must be Freshness")
        if self.authority is SourceAuthority.DERIVED_SOURCE and self.lineage is None:
            raise RepresentationError("derived sources require explicit lineage")
        if self.exchange_role is ExchangeRole.DERIVED_EXPORT and self.lineage is None:
            raise RepresentationError("DERIVED_EXPORT sources require explicit lineage")
        if self.authority is SourceAuthority.CANONICAL_SOURCE and self.lineage is not None:
            raise RepresentationError("canonical sources cannot declare derived lineage")
        if self.lineage is not None and not isinstance(self.lineage, SourceLineage):
            raise RepresentationError("lineage must be SourceLineage")
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "source_version": self.source_version,
            "source_fingerprint": self.source_fingerprint,
            "authority": self.authority.value,
            "exchange_role": self.exchange_role.value if self.exchange_role else None,
            "freshness": self.freshness.value,
            "lineage": self.lineage.canonical_dict() if self.lineage else None,
            "metadata": _plain(self.metadata),
        }


@dataclass(frozen=True)
class SourceLineage:
    source_id: str
    source_version: str
    source_fingerprint: str

    def __post_init__(self) -> None:
        _text(self.source_id, "lineage.source_id")
        _text(self.source_version, "lineage.source_version")
        object.__setattr__(self, "source_fingerprint", _fingerprint(self.source_fingerprint, "lineage.source_fingerprint"))

    def canonical_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "source_version": self.source_version,
            "source_fingerprint": self.source_fingerprint,
        }


def evaluate_freshness(derived: SourceSnapshot, canonical: SourceSnapshot) -> Freshness:
    if derived.authority is not SourceAuthority.DERIVED_SOURCE:
        raise RepresentationError("derived snapshot must have DERIVED_SOURCE authority")
    if canonical.authority is not SourceAuthority.CANONICAL_SOURCE:
        raise RepresentationError("canonical snapshot must have CANONICAL_SOURCE authority")
    if derived.lineage is None:
        return Freshness.UNKNOWN
    if derived.lineage.source_id != canonical.source_id:
        return Freshness.UNKNOWN
    if derived.lineage.source_version == canonical.source_version and derived.lineage.source_fingerprint == canonical.source_fingerprint:
        return Freshness.CURRENT
    return Freshness.STALE


def detect_source_conflict(left: SourceSnapshot, right: SourceSnapshot) -> bool:
    """Return true only for relevant snapshots that cannot be selected safely."""
    if left.source_id != right.source_id:
        return False
    if left.authority is right.authority and left.source_version == right.source_version:
        return left.source_fingerprint != right.source_fingerprint
    if {left.authority, right.authority} == {SourceAuthority.CANONICAL_SOURCE, SourceAuthority.DERIVED_SOURCE}:
        return left.source_version == right.source_version and left.source_fingerprint != right.source_fingerprint
    return left.source_version != right.source_version or left.source_fingerprint != right.source_fingerprint


def require_no_source_conflict(*sources: SourceSnapshot) -> None:
    for index, left in enumerate(sources):
        for right in sources[index + 1 :]:
            if detect_source_conflict(left, right):
                raise SourceConflictError(
                    f"SOURCE_CONFLICT: {left.source_id} has incompatible snapshots"
                )


@dataclass(frozen=True)
class ViewDefinition:
    view_id: str
    view_type: ViewType
    view_family: ViewFamily
    source_scope: str
    projection: ProjectionKind = ProjectionKind.NONE
    orientation: str | None = None
    cut_plane: str | None = None
    view_direction: str | None = None
    visibility: tuple[str, ...] = ()
    filters: Mapping[str, Any] = field(default_factory=dict)
    semantic_scope: tuple[str, ...] = ()
    level_scope: str | None = None
    scale_intent: str | None = None
    representation_purpose: str | None = None

    def __post_init__(self) -> None:
        _text(self.view_id, "view_id")
        _text(self.source_scope, "source_scope")
        if not isinstance(self.view_type, ViewType) or not isinstance(self.view_family, ViewFamily):
            raise RepresentationError("view_type and view_family must use ARE enums")
        if _VIEW_FAMILY_BY_TYPE[self.view_type] is not self.view_family:
            raise RepresentationError(
                f"INVALID_PROFILE: {self.view_type.value} requires {_VIEW_FAMILY_BY_TYPE[self.view_type].value} family"
            )
        if not isinstance(self.projection, ProjectionKind):
            raise RepresentationError("projection must use ProjectionKind")
        object.__setattr__(self, "visibility", tuple(_text(v, "visibility item") for v in self.visibility))
        object.__setattr__(self, "semantic_scope", tuple(_text(v, "semantic_scope item") for v in self.semantic_scope))
        object.__setattr__(self, "filters", _freeze(self.filters))
        if self.view_family is ViewFamily.GEOMETRIC and self.view_type in {ViewType.ARCHITECTURAL_PLAN, ViewType.SECTION, ViewType.ELEVATION}:
            if self.view_type is ViewType.SECTION and not self.cut_plane:
                raise RepresentationError("section views require cut_plane evidence")

    def canonical_dict(self) -> dict[str, Any]:
        return _plain(self)


@dataclass(frozen=True)
class RepresentationProfile:
    profile_id: str
    kind: ProfileKind
    view_family: ViewFamily
    semantic_detail: str = "DEFAULT"
    geometric_fidelity: str = "DEFAULT"
    annotation_intent: str = "NONE"
    output_intent: str = "SCENE"
    validation_evidence_required: bool = False
    cost_class: str = "DEFAULT"

    def __post_init__(self) -> None:
        _text(self.profile_id, "profile_id")
        for name in ("semantic_detail", "geometric_fidelity", "annotation_intent", "output_intent", "cost_class"):
            _text(getattr(self, name), name)
        if not isinstance(self.kind, ProfileKind) or not isinstance(self.view_family, ViewFamily):
            raise RepresentationError("kind and view_family must use ARE enums")
        if not isinstance(self.validation_evidence_required, bool):
            raise RepresentationError("validation_evidence_required must be bool")

    def canonical_dict(self) -> dict[str, Any]:
        return _plain(self)


@dataclass(frozen=True)
class GraphicStyle:
    style_id: str
    line_weights: Mapping[str, str] = field(default_factory=dict)
    line_types: Mapping[str, str] = field(default_factory=dict)
    hatches: Mapping[str, str] = field(default_factory=dict)
    text_conventions: Mapping[str, str] = field(default_factory=dict)
    graphic_hierarchy: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.style_id, "style_id")
        for name in ("line_weights", "line_types", "hatches", "text_conventions"):
            object.__setattr__(self, name, _freeze(getattr(self, name)))
        object.__setattr__(self, "graphic_hierarchy", tuple(_text(v, "graphic_hierarchy item") for v in self.graphic_hierarchy))

    def canonical_dict(self) -> dict[str, Any]:
        return _plain(self)


@dataclass(frozen=True)
class AnnotationProfile:
    profile_id: str
    dimensions: tuple[str, ...] = ()
    room_labels: bool = False
    door_tags: bool = False
    window_tags: bool = False
    levels: bool = False
    axes: bool = False
    notes: bool = False

    def __post_init__(self) -> None:
        _text(self.profile_id, "profile_id")
        object.__setattr__(self, "dimensions", tuple(_text(v, "dimension item") for v in self.dimensions))
        for name in ("room_labels", "door_tags", "window_tags", "levels", "axes", "notes"):
            if not isinstance(getattr(self, name), bool):
                raise RepresentationError(f"{name} must be bool")

    def canonical_dict(self) -> dict[str, Any]:
        return _plain(self)


@dataclass(frozen=True)
class GraphicTrace:
    source_entity_refs: tuple[str, ...]
    semantic_role: str
    operation: str
    source_version: str | None = None
    source_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if not self.source_entity_refs:
            raise RepresentationError("graphic trace requires source_entity_refs")
        object.__setattr__(self, "source_entity_refs", tuple(_text(v, "source_entity_ref") for v in self.source_entity_refs))
        _text(self.semantic_role, "semantic_role")
        _text(self.operation, "operation")
        if self.source_fingerprint is not None:
            object.__setattr__(self, "source_fingerprint", _fingerprint(self.source_fingerprint, "source_fingerprint"))


@dataclass(frozen=True)
class GraphicEntity:
    entity_id: str
    role: str
    geometry_intent: Mapping[str, Any]
    trace: GraphicTrace
    style_ref: str | None = None
    annotation_ref: str | None = None

    def __post_init__(self) -> None:
        _text(self.entity_id, "entity_id")
        _text(self.role, "role")
        object.__setattr__(self, "geometry_intent", _freeze(self.geometry_intent))
        if self.style_ref is not None:
            _text(self.style_ref, "style_ref")
        if self.annotation_ref is not None:
            _text(self.annotation_ref, "annotation_ref")


@dataclass(frozen=True)
class GraphicScene:
    scene_id: str
    source_snapshot: SourceSnapshot
    view: ViewDefinition
    representation_profile: RepresentationProfile
    graphic_style: GraphicStyle
    annotation_profile: AnnotationProfile
    transform_version: str
    entities: tuple[GraphicEntity, ...] = ()
    diagnostics: tuple[DiagnosticCode, ...] = ()
    scene_fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        _text(self.scene_id, "scene_id")
        _text(self.transform_version, "transform_version")
        if not isinstance(self.source_snapshot, SourceSnapshot):
            raise RepresentationError("source_snapshot must be SourceSnapshot")
        for name in ("view", "representation_profile", "graphic_style", "annotation_profile"):
            if not isinstance(getattr(self, name), (ViewDefinition, RepresentationProfile, GraphicStyle, AnnotationProfile)):
                raise RepresentationError(f"{name} has an invalid ARE contract type")
        if self.view.view_family is not self.representation_profile.view_family:
            raise RepresentationError("INVALID_PROFILE: view/profile families are incompatible")
        object.__setattr__(self, "entities", tuple(self.entities))
        if len({entity.entity_id for entity in self.entities}) != len(self.entities):
            raise RepresentationError("GraphicScene entity IDs must be unique")
        if any(not isinstance(code, DiagnosticCode) for code in self.diagnostics):
            raise RepresentationError("diagnostics must use DiagnosticCode")
        payload = self.fingerprint_payload()
        object.__setattr__(self, "scene_fingerprint", fingerprint(payload))

    def fingerprint_payload(self) -> dict[str, Any]:
        return {
            "source_snapshot": self.source_snapshot.canonical_dict(),
            "view": self.view.canonical_dict(),
            "representation_profile": self.representation_profile.canonical_dict(),
            "graphic_style": self.graphic_style.canonical_dict(),
            "annotation_profile": self.annotation_profile.canonical_dict(),
            "transform_version": self.transform_version,
            "entities": [_plain(entity) for entity in self.entities],
            "diagnostics": [code.value for code in self.diagnostics],
        }

    def canonical_dict(self) -> dict[str, Any]:
        return {**self.fingerprint_payload(), "scene_id": self.scene_id, "scene_fingerprint": self.scene_fingerprint, "diagnostics": [code.value for code in self.diagnostics]}


def build_scene(
    source_snapshot: SourceSnapshot,
    view: ViewDefinition,
    representation_profile: RepresentationProfile,
    graphic_style: GraphicStyle,
    annotation_profile: AnnotationProfile,
    transform_version: str,
    *,
    entities: Sequence[GraphicEntity] = (),
    diagnostics: Sequence[DiagnosticCode] = (),
) -> GraphicScene:
    """Construct a scene without projecting or inventing architectural data."""
    if source_snapshot.freshness is Freshness.STALE:
        raise RepresentationError(DiagnosticCode.STALE_SOURCE.value)
    if source_snapshot.freshness is Freshness.UNKNOWN:
        if representation_profile.validation_evidence_required:
            raise RepresentationError(DiagnosticCode.MISSING_REQUIRED_EVIDENCE.value)
        diagnostics = tuple(diagnostics) + (DiagnosticCode.MISSING_REQUIRED_EVIDENCE,)
    require_no_source_conflict(source_snapshot)
    scene_id = fingerprint({
        "source": source_snapshot.canonical_dict(),
        "view": view.canonical_dict(),
        "profile": representation_profile.canonical_dict(),
        "style": graphic_style.canonical_dict(),
        "annotation": annotation_profile.canonical_dict(),
        "transform_version": transform_version,
    })
    return GraphicScene(
        scene_id=scene_id,
        source_snapshot=source_snapshot,
        view=view,
        representation_profile=representation_profile,
        graphic_style=graphic_style,
        annotation_profile=annotation_profile,
        transform_version=transform_version,
        entities=tuple(entities),
        diagnostics=tuple(diagnostics),
    )


__all__ = [
    "AnnotationProfile", "DiagnosticCode", "ExchangeRole", "Freshness", "GraphicEntity",
    "GraphicScene", "GraphicStyle", "GraphicTrace", "ProfileKind", "RepresentationError",
    "RepresentationProfile", "ProjectionKind", "SourceAuthority", "SourceConflictError",
    "SourceLineage", "SourceSnapshot", "ViewDefinition", "ViewFamily", "ViewType", "build_scene", "canonical_json",
    "detect_source_conflict", "evaluate_freshness", "fingerprint", "require_no_source_conflict",
]
