"""D-2 architectural semantic model and restricted geometry."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import hashlib, json
from .identity import ArchiElementId

class ElementKind(str, Enum):
    SITE="SITE"; SPACE="SPACE"; WALL="WALL"; SLAB="SLAB"; COLUMN="COLUMN"; BEAM="BEAM"; DOOR="DOOR"; WINDOW="WINDOW"; OPENING="OPENING"
class GeometryKind(str, Enum):
    EXTRUDED_RECTANGLE="EXTRUDED_RECTANGLE"
    EXTRUDED_CIRCLE="EXTRUDED_CIRCLE"

@dataclass(frozen=True)
class ProfileSpec:
    width_mm: int
    depth_mm: int
    radius_mm: int | None = None
    def __post_init__(self):
        if self.width_mm <= 0 or self.depth_mm <= 0: raise ValueError("profile dimensions must be positive")
        if self.radius_mm is not None and self.radius_mm <= 0: raise ValueError("radius must be positive")

@dataclass(frozen=True)
class ArchiGeometry:
    kind: GeometryKind
    profile: ProfileSpec
    x_mm: int = 0
    y_mm: int = 0
    z_mm: int = 0
    height_mm: int = 1
    def __post_init__(self):
        if self.height_mm <= 0: raise ValueError("height must be positive")
    def to_dict(self):
        return {"kind": self.kind.value, "profile": {"width_mm": self.profile.width_mm, "depth_mm": self.profile.depth_mm, "radius_mm": self.profile.radius_mm}, "x_mm": self.x_mm, "y_mm": self.y_mm, "z_mm": self.z_mm, "height_mm": self.height_mm}

PropertyValue = str | int | float | bool | None | tuple[str, ...]
def _serialize_property_value(value: PropertyValue) -> Any:
    if isinstance(value, tuple): return list(value)
    return value

@dataclass(frozen=True)
class ArchiElement:
    element_id: ArchiElementId
    project_id: str
    kind: ElementKind
    geometry: ArchiGeometry
    properties: dict[str, PropertyValue] = field(default_factory=dict)
    provenance: dict[str, Any] | None = None
    version: int = 1
    hosted_in: ArchiElementId | None = None
    contained_in: ArchiElementId | None = None
    def __post_init__(self):
        if self.hosted_in is not None and self.contained_in is not None: raise ValueError("hosting and contained_in are mutually exclusive")
        if self.version < 1: raise ValueError("version must be positive")
    def semantic_dict(self) -> dict[str, Any]:
        return {"element_id": self.element_id.value, "project_id": self.project_id, "kind": self.kind.value, "geometry": self.geometry.to_dict(), "properties": {k: _serialize_property_value(self.properties[k]) for k in sorted(self.properties)}, "version": self.version, "hosted_in": self.hosted_in.value if self.hosted_in else None, "contained_in": self.contained_in.value if self.contained_in else None}
    def content_hash(self) -> str:
        raw = json.dumps(self.semantic_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()
    def ref(self):
        from ..derivation import VersionedRef
        return VersionedRef(self.kind.value, self.element_id.value, self.version, self.content_hash())

__all__ = ["ElementKind", "GeometryKind", "ProfileSpec", "ArchiGeometry", "ArchiElement", "PropertyValue", "_serialize_property_value"]
