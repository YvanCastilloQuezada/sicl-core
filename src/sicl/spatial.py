"""Derived spatial representation schema for the SiMS-DeI spatial pilot.

This module deliberately contains schema and validation only. It does not generate
geometry, render it, persist it, or change any canonical Core domain entity.

The common ``geometry`` field is intentionally renderer-neutral. A future 2D or
3D view derives its projection from the same element rather than maintaining
independent geometry_2d and geometry_3d sources of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import re
from typing import Any, Mapping

from .domain import SpatialScope

REPRESENTATION_VERSION = "1.0"
DEFAULT_COORDINATE_SYSTEM = "LOCAL_ENU"
DEFAULT_UNITS = "m"
SUPPORTED_UNITS = frozenset({"m"})
SUPPORTED_GEOMETRY_TYPES = frozenset(
    {"point", "line", "polygon", "multipolygon", "network", "volume", "territorial_layer"}
)
_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


class SpatialValidationError(ValueError):
    """Raised when a spatial DTO is malformed or violates its invariants."""


def _require_id(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpatialValidationError(f"{field_name} must be a non-empty string")
    if not _ID_PATTERN.fullmatch(value):
        raise SpatialValidationError(
            f"{field_name} contains unsupported characters: {value!r}"
        )
    return value


def _validate_finite_numbers(value: Any, path: str) -> None:
    if isinstance(value, bool):
        raise SpatialValidationError(f"{path} must contain finite numeric coordinates")
    if isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            raise SpatialValidationError(f"{path} contains a non-finite coordinate")
        return
    if isinstance(value, list) or isinstance(value, tuple):
        for index, item in enumerate(value):
            _validate_finite_numbers(item, f"{path}[{index}]")
        return
    raise SpatialValidationError(f"{path} contains a non-numeric coordinate")


def _canonical(value: Any) -> Any:
    """Return JSON-compatible data with stable mapping order and no UI state."""
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, SpatialScope):
        return value.value
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_canonical(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def spatial_element_id(
    alternative_id: str,
    element_type: str,
    semantic_key: str,
    *,
    generator_version: str,
    representation_version: str = REPRESENTATION_VERSION,
) -> str:
    """Derive a stable ID from semantic identity, never array position or render state."""
    payload = {
        "alternative_id": _require_id(alternative_id, "alternative_id"),
        "element_type": _require_id(element_type, "element_type"),
        "semantic_key": _require_id(semantic_key, "semantic_key"),
        "generator_version": _require_id(generator_version, "generator_version"),
        "representation_version": _require_id(representation_version, "representation_version"),
    }
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()[:16]
    return f"{element_type}:{semantic_key}:{digest}"


@dataclass(frozen=True)
class SpatialElement:
    id: str
    element_type: str
    geometry: dict[str, Any]
    level: int | None = None
    parent_id: str | None = None
    labels: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self, known_ids: set[str] | None = None) -> None:
        _require_id(self.id, "element.id")
        _require_id(self.element_type, "element.element_type")
        if not isinstance(self.geometry, Mapping):
            raise SpatialValidationError("element.geometry must be an object")
        geometry_type = self.geometry.get("type")
        if geometry_type not in SUPPORTED_GEOMETRY_TYPES:
            raise SpatialValidationError(
                f"element.geometry.type is unsupported: {geometry_type!r}"
            )
        if "coordinates" not in self.geometry:
            raise SpatialValidationError("element.geometry.coordinates is required")
        _validate_finite_numbers(self.geometry["coordinates"], f"element[{self.id}].geometry.coordinates")
        if self.level is not None and (not isinstance(self.level, int) or isinstance(self.level, bool)):
            raise SpatialValidationError("element.level must be an integer when provided")
        if self.parent_id is not None:
            _require_id(self.parent_id, "element.parent_id")
            if known_ids is not None and self.parent_id not in known_ids:
                raise SpatialValidationError(
                    f"element.parent_id references unknown element: {self.parent_id}"
                )
        if not isinstance(self.labels, Mapping) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in self.labels.items()
        ):
            raise SpatialValidationError("element.labels must map strings to strings")
        if not isinstance(self.metadata, Mapping):
            raise SpatialValidationError("element.metadata must be an object")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "element_type": self.element_type,
            "geometry": _canonical(self.geometry),
            "level": self.level,
            "parent_id": self.parent_id,
            "labels": _canonical(self.labels),
            "metadata": _canonical(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SpatialElement":
        if not isinstance(data, Mapping):
            raise SpatialValidationError("element must be an object")
        try:
            item = cls(
                id=data["id"],
                element_type=data["element_type"],
                geometry=dict(data["geometry"]),
                level=data.get("level"),
                parent_id=data.get("parent_id"),
                labels=dict(data.get("labels", {})),
                metadata=dict(data.get("metadata", {})),
            )
        except KeyError as exc:
            raise SpatialValidationError(f"element missing required field: {exc.args[0]}") from exc
        item.validate()
        return item


@dataclass(frozen=True)
class SpatialRepresentation:
    id: str
    alternative_id: str
    spatial_scope: SpatialScope
    representation_version: str
    generator_version: str
    coordinate_system: str
    units: str
    input_fingerprint: str
    seed: int | str | None = None
    elements: tuple[SpatialElement, ...] = field(default_factory=tuple)
    coordinate_origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    north_degrees: float = 0.0
    elevation_reference: str = "local_datum"

    def validate(self) -> "SpatialRepresentation":
        _require_id(self.id, "id")
        _require_id(self.alternative_id, "alternative_id")
        if not isinstance(self.spatial_scope, SpatialScope):
            try:
                SpatialScope(self.spatial_scope)
            except (TypeError, ValueError) as exc:
                raise SpatialValidationError(
                    f"spatial_scope is unsupported: {self.spatial_scope!r}"
                ) from exc
        _require_id(self.representation_version, "representation_version")
        _require_id(self.generator_version, "generator_version")
        if not isinstance(self.coordinate_system, str) or not self.coordinate_system.strip():
            raise SpatialValidationError("coordinate_system must be a non-empty string")
        if self.units not in SUPPORTED_UNITS:
            raise SpatialValidationError(f"unsupported units: {self.units!r}")
        if not isinstance(self.input_fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", self.input_fingerprint):
            raise SpatialValidationError("input_fingerprint must be a lowercase SHA-256 hex digest")
        if not isinstance(self.elevation_reference, str) or not self.elevation_reference.strip():
            raise SpatialValidationError("elevation_reference must be a non-empty string")
        _validate_finite_numbers(list(self.coordinate_origin), "coordinate_origin")
        if not isinstance(self.north_degrees, (int, float)) or isinstance(self.north_degrees, bool) or not math.isfinite(float(self.north_degrees)):
            raise SpatialValidationError("north_degrees must be a finite number")
        if not -360.0 <= float(self.north_degrees) <= 360.0:
            raise SpatialValidationError("north_degrees must be between -360 and 360")
        if self.seed is not None and not isinstance(self.seed, (str, int)):
            raise SpatialValidationError("seed must be null, a string, or an integer")
        known_ids = {element.id for element in self.elements}
        if len(known_ids) != len(self.elements):
            raise SpatialValidationError("duplicate spatial element IDs")
        for element in self.elements:
            element.validate(known_ids)
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "id": self.id,
            "alternative_id": self.alternative_id,
            "spatial_scope": self.spatial_scope.value,
            "representation_version": self.representation_version,
            "generator_version": self.generator_version,
            "coordinate_system": self.coordinate_system,
            "units": self.units,
            "input_fingerprint": self.input_fingerprint,
            "seed": self.seed,
            "coordinate_origin": list(self.coordinate_origin),
            "north_degrees": self.north_degrees,
            "elevation_reference": self.elevation_reference,
            "elements": [element.to_dict() for element in self.elements],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SpatialRepresentation":
        if not isinstance(data, Mapping):
            raise SpatialValidationError("spatial representation must be an object")
        try:
            scope = data["spatial_scope"]
            try:
                parsed_scope = scope if isinstance(scope, SpatialScope) else SpatialScope(scope)
            except (TypeError, ValueError) as exc:
                raise SpatialValidationError(
                    f"spatial_scope is unsupported: {scope!r}"
                ) from exc
            item = cls(
                id=data["id"],
                alternative_id=data["alternative_id"],
                spatial_scope=parsed_scope,
                representation_version=data["representation_version"],
                generator_version=data["generator_version"],
                coordinate_system=data["coordinate_system"],
                units=data["units"],
                input_fingerprint=data["input_fingerprint"],
                seed=data.get("seed"),
                coordinate_origin=tuple(data.get("coordinate_origin", (0.0, 0.0, 0.0))),
                north_degrees=data.get("north_degrees", 0.0),
                elevation_reference=data.get("elevation_reference", "local_datum"),
                elements=tuple(SpatialElement.from_dict(element) for element in data.get("elements", [])),
            )
        except KeyError as exc:
            raise SpatialValidationError(f"spatial representation missing required field: {exc.args[0]}") from exc
        except (TypeError, ValueError) as exc:
            raise SpatialValidationError(f"invalid spatial representation: {exc}") from exc
        return item.validate()


def input_fingerprint(inputs: Mapping[str, Any]) -> str:
    """Hash only stable, relevant inputs in canonical JSON order."""
    if not isinstance(inputs, Mapping):
        raise SpatialValidationError("fingerprint inputs must be an object")
    return hashlib.sha256(canonical_json(inputs).encode("utf-8")).hexdigest()


__all__ = [
    "DEFAULT_COORDINATE_SYSTEM",
    "DEFAULT_UNITS",
    "REPRESENTATION_VERSION",
    "SUPPORTED_GEOMETRY_TYPES",
    "SpatialElement",
    "SpatialRepresentation",
    "SpatialValidationError",
    "canonical_json",
    "input_fingerprint",
    "spatial_element_id",
]
