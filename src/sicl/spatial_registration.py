"""Canonical frame-to-frame spatial registration.

This module is deliberately independent of AR.  Control correspondences and
reference-frame metadata are the source of truth; the derived 2D similarity
transform is reproducible and never replaces those inputs.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from math import atan2, cos, hypot, sin
from typing import Any, Mapping


SUPPORTED_METHOD = "MANUAL_TWO_POINT"
VALID_STATUSES = {"DRAFT", "HUMAN_CONFIRMED", "LOCKED", "RECALIBRATION"}


def _point(value: Mapping[str, Any], label: str) -> tuple[float, float]:
    try:
        x, y = float(value["x"]), float(value["y"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain numeric x and y") from exc
    if not all(abs(v) < 1e15 for v in (x, y)):
        raise ValueError(f"{label} contains an invalid coordinate")
    return x, y


def derive_registration_transform(control_correspondences: list[Mapping[str, Any]]) -> dict[str, Any]:
    if len(control_correspondences) < 2:
        raise ValueError("TWO_POINT_CORRESPONDENCE_REQUIRED")
    a, b = control_correspondences[0], control_correspondences[1]
    pa, pb = _point(a["project_point"], "project_point A/B") , _point(b["project_point"], "project_point A/B")
    ta, tb = _point(a["target_point"], "target_point A/B"), _point(b["target_point"], "target_point A/B")
    pv = (pb[0] - pa[0], pb[1] - pa[1])
    tv = (tb[0] - ta[0], tb[1] - ta[1])
    project_length, target_length = hypot(*pv), hypot(*tv)
    if project_length <= 1e-9 or target_length <= 1e-9:
        raise ValueError("DEGENERATE_CONTROL_BASELINE")
    project_angle, target_angle = atan2(pv[1], pv[0]), atan2(tv[1], tv[0])
    rotation = target_angle - project_angle
    scale = target_length / project_length
    c, s = cos(rotation), sin(rotation)
    translation = {"x": ta[0] - scale * (c * pa[0] - s * pa[1]), "y": ta[1] - scale * (s * pa[0] + c * pa[1])}
    return {
        "type": "2D_SIMILARITY",
        "translation": translation,
        "rotation_radians": rotation,
        "rotation_degrees": rotation * 180.0 / 3.141592653589793,
        "scale": scale,
        "units": "m",
        "derived_from": [str(a.get("id", "CONTROL_A")), str(b.get("id", "CONTROL_B"))],
        "provenance": "DETERMINISTIC_DERIVED",
    }


@dataclass
class SpatialRegistration:
    registration_id: str
    project_id: str
    source_frame: dict[str, Any]
    target_frame: dict[str, Any]
    control_correspondences: list[dict[str, Any]]
    registration_method: str
    units: str
    coordinate_systems: dict[str, Any]
    site_side_confirmation: dict[str, Any] | None
    actor: str
    timestamp: str
    status: str
    uncertainty: dict[str, Any]
    provenance: dict[str, Any]
    derived_transform: dict[str, Any] | None = None
    version: int = 1

    def __post_init__(self) -> None:
        if self.registration_method != SUPPORTED_METHOD:
            raise ValueError("UNSUPPORTED_REGISTRATION_METHOD")
        if self.status not in VALID_STATUSES:
            raise ValueError("INVALID_REGISTRATION_STATUS")
        if self.units != "m":
            raise ValueError("UNITS_M_REQUIRED_FOR_MANUAL_TWO_POINT")
        if len(self.control_correspondences) < 2:
            raise ValueError("TWO_POINT_CORRESPONDENCE_REQUIRED")
        self.derived_transform = derive_registration_transform(self.control_correspondences)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SpatialRegistration":
        return cls(
            registration_id=str(value["registration_id"]), project_id=str(value["project_id"]),
            source_frame=dict(value["source_frame"]), target_frame=dict(value["target_frame"]),
            control_correspondences=[dict(item) for item in value["control_correspondences"]],
            registration_method=str(value.get("registration_method", SUPPORTED_METHOD)), units=str(value.get("units", "m")),
            coordinate_systems=dict(value.get("coordinate_systems", {})),
            site_side_confirmation=dict(value["site_side_confirmation"]) if value.get("site_side_confirmation") else None,
            actor=str(value.get("actor", "unknown")), timestamp=str(value.get("timestamp") or datetime.now(timezone.utc).isoformat()),
            status=str(value.get("status", "DRAFT")), uncertainty=dict(value.get("uncertainty", {"state": "UNKNOWN"})),
            provenance=dict(value.get("provenance", {})), derived_transform=dict(value["derived_transform"]) if value.get("derived_transform") else None,
            version=int(value.get("version", 1)),
        )


def propose_registration(project_id: str, payload: Mapping[str, Any], *, registration_id: str, actor: str) -> SpatialRegistration:
    side = payload.get("site_side_confirmation")
    if not isinstance(side, dict) or side.get("confirmed") is not True:
        raise ValueError("SITE_SIDE_CONFIRMATION_REQUIRED")
    return SpatialRegistration(
        registration_id=registration_id, project_id=project_id,
        source_frame=dict(payload.get("source_frame") or {"id": "PROJECT_LOCAL", "type": "PROJECT_LOCAL"}),
        target_frame=dict(payload.get("target_frame") or {"id": "FIELD_LOCAL", "type": "TARGET_LOCAL"}),
        control_correspondences=[dict(item) for item in payload.get("control_correspondences", [])],
        registration_method=str(payload.get("registration_method", SUPPORTED_METHOD)), units=str(payload.get("units", "m")),
        coordinate_systems=dict(payload.get("coordinate_systems") or {"source": "PROJECT_LOCAL", "target": "TARGET_LOCAL"}),
        site_side_confirmation=side, actor=actor, timestamp=str(payload.get("timestamp") or datetime.now(timezone.utc).isoformat()),
        status="DRAFT", uncertainty=dict(payload.get("uncertainty") or {"state": "UNKNOWN"}),
        provenance=dict(payload.get("provenance") or {"kind": "HUMAN_DECLARED_CONTROL_CORRESPONDENCE"}),
    )


__all__ = ["SpatialRegistration", "SUPPORTED_METHOD", "derive_registration_transform", "propose_registration", "VALID_STATUSES"]


def registration_transition(registration: SpatialRegistration, action: str, *, actor: str, side_confirmation: dict[str, Any] | None = None) -> SpatialRegistration:
    next_status = {"CONFIRM": "HUMAN_CONFIRMED", "LOCK": "LOCKED", "UNLOCK": "RECALIBRATION", "RECALIBRATE": "RECALIBRATION"}.get(action)
    if next_status is None:
        raise ValueError("INVALID_REGISTRATION_ACTION")
    if action == "LOCK" and registration.status not in {"HUMAN_CONFIRMED", "RECALIBRATION"}:
        raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
    if action == "CONFIRM" and registration.status not in {"DRAFT", "RECALIBRATION"}:
        raise ValueError("INVALID_REGISTRATION_TRANSITION")
    if action == "LOCK" and registration.site_side_confirmation is None and side_confirmation is None:
        raise ValueError("SITE_SIDE_CONFIRMATION_REQUIRED")
    updated = SpatialRegistration.from_dict(registration.to_dict())
    updated.status = next_status
    updated.actor = actor
    updated.timestamp = datetime.now(timezone.utc).isoformat()
    if side_confirmation is not None:
        updated.site_side_confirmation = dict(side_confirmation)
    updated.version += 1
    return updated
