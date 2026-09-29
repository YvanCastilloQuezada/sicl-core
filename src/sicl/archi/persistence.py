"""Durable serialization contract for the canonical D-2 architectural state."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from .identity import ArchiElementId
from .model import ArchiElement, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec


@dataclass(frozen=True)
class D2Snapshot:
    snapshot_id: str
    project_id: str
    version: int
    elements: tuple[ArchiElement, ...]
    content_hash: str
    actor: str
    source_event_id: int | None
    created_at: str

    def metadata(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "project_id": self.project_id,
            "version": self.version,
            "content_hash": self.content_hash,
            "element_count": len(self.elements),
            "actor": self.actor,
            "source_event_id": self.source_event_id,
            "created_at": self.created_at,
        }


def _element_to_dict(element: ArchiElement) -> dict[str, Any]:
    value = element.semantic_dict()
    value["provenance"] = element.provenance
    return value


def serialize_elements(elements: tuple[ArchiElement, ...]) -> str:
    if not isinstance(elements, tuple):
        raise TypeError("elements must be a tuple")
    if any(not isinstance(element, ArchiElement) for element in elements):
        raise TypeError("elements must contain ArchiElement values")
    ordered = sorted(elements, key=lambda element: element.element_id.value)
    return json.dumps(
        [_element_to_dict(element) for element in ordered],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def elements_content_hash(elements_json: str) -> str:
    if not isinstance(elements_json, str):
        raise TypeError("elements_json must be a string")
    return hashlib.sha256(elements_json.encode()).hexdigest()


def deterministic_snapshot_id(project_id: str, version: int, content_hash: str) -> str:
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("project_id must be non-empty")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError("version must be positive")
    raw = f"{project_id}:{version}:{content_hash}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _property_from_json(value: Any) -> Any:
    # ArchiElement only permits immutable scalar values or tuple[str, ...].
    # JSON arrays can therefore only represent the tuple variant.
    if isinstance(value, list):
        if not all(isinstance(item, str) for item in value):
            raise ValueError("property arrays must contain strings")
        return tuple(value)
    return value


def _element_from_dict(value: Mapping[str, Any]) -> ArchiElement:
    if not isinstance(value, Mapping):
        raise ValueError("D-2 element must be an object")
    required = {
        "element_id", "project_id", "kind", "geometry", "properties", "provenance",
        "version", "hosted_in", "hosted_in_version", "contained_in", "contained_in_version",
    }
    if set(value) != required:
        raise ValueError(f"invalid D-2 element fields: {sorted(set(value) ^ required)}")
    geometry = value["geometry"]
    if not isinstance(geometry, Mapping):
        raise ValueError("geometry must be an object")
    profile = geometry.get("profile")
    if not isinstance(profile, Mapping):
        raise ValueError("geometry.profile must be an object")
    properties = value["properties"]
    if not isinstance(properties, Mapping):
        raise ValueError("properties must be an object")
    provenance = value["provenance"]
    if provenance is not None and not isinstance(provenance, dict):
        raise ValueError("provenance must be an object or null")
    return ArchiElement(
        element_id=ArchiElementId(str(value["element_id"])),
        project_id=str(value["project_id"]),
        kind=ElementKind(str(value["kind"])),
        geometry=ArchiGeometry(
            kind=GeometryKind(str(geometry["kind"])),
            profile=ProfileSpec(
                width_mm=int(profile["width_mm"]),
                depth_mm=int(profile["depth_mm"]),
                radius_mm=int(profile["radius_mm"]) if profile.get("radius_mm") is not None else None,
            ),
            x_mm=int(geometry["x_mm"]),
            y_mm=int(geometry["y_mm"]),
            z_mm=int(geometry["z_mm"]),
            height_mm=int(geometry["height_mm"]),
        ),
        properties={str(key): _property_from_json(item) for key, item in properties.items()},
        provenance=provenance,
        version=int(value["version"]),
        hosted_in=ArchiElementId(str(value["hosted_in"])) if value["hosted_in"] is not None else None,
        contained_in=ArchiElementId(str(value["contained_in"])) if value["contained_in"] is not None else None,
        hosted_in_version=int(value["hosted_in_version"]) if value["hosted_in_version"] is not None else None,
        contained_in_version=int(value["contained_in_version"]) if value["contained_in_version"] is not None else None,
    )


def deserialize_elements(raw: str) -> tuple[ArchiElement, ...]:
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid D-2 elements JSON") from exc
    if not isinstance(value, list):
        raise ValueError("D-2 elements JSON must be an array")
    elements = tuple(_element_from_dict(item) for item in value)
    ids = [element.element_id.value for element in elements]
    if ids != sorted(ids):
        raise ValueError("D-2 elements must be ordered by element_id")
    if len(ids) != len(set(ids)):
        raise ValueError("D-2 elements must have unique element_id values")
    return elements


__all__ = [
    "D2Snapshot",
    "serialize_elements",
    "deserialize_elements",
    "elements_content_hash",
    "deterministic_snapshot_id",
]
