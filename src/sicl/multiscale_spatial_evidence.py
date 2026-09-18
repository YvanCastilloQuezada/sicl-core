"""Multiscale spatial evidence over the canonical Evidence/Event Log models.

This module deliberately does not introduce UrbanEvidence or a second evidence
store. Rich spatial/photo metadata is carried by the append-only event payload
and exposed as a derived view over the canonical Evidence record.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Any, Iterable

from .domain import SpatialScope

EPISTEMIC_STATES = {"USER_OBSERVED", "USER_PROVIDED", "EXTERNAL_SOURCE", "COMPUTED", "AI_PROPOSED", "HUMAN_CONFIRMED", "UNKNOWN"}
QUALIFIERS = {"EXACT", "APPROXIMATE", "RANGE", "UNKNOWN"}
RELEVANCE = {"RELEVANT", "POSSIBLE", "NOT_TYPICAL", "UNKNOWN"}

PROFILE: dict[str, tuple[str, ...]] = {
    "pais": ("settlement_systems", "territorial_networks", "infrastructure", "relief", "environmental_systems"),
    "macro_region": ("territorial_networks", "regional_infrastructure", "connectivity", "environmental_systems"),
    "region": ("settlement_systems", "regional_infrastructure", "watersheds", "connectivity"),
    "provincia_metropoli": ("metropolitan_structure", "urban_centers", "corridors", "transport", "terrain"),
    "distrito_ciudad": ("urban_structure", "centralities", "road_network", "transport", "facilities", "public_space"),
    "zona_barrio_sector": ("urban_fabric", "blocks", "lot_pattern", "predominant_heights", "street_hierarchy", "pedestrian_conditions"),
    "parcela_sitio": ("site_boundary", "access_observation", "terrain_observation", "vegetation", "views", "noise_observation"),
    "edificacion": ("building_footprint", "floor_count", "approximate_height", "observed_use", "facade_condition", "street_relationship"),
    "sistema": ("visible_system_element", "drainage_observation", "circulation_system"),
    "espacio": ("light_observation", "privacy_observation", "spatial_condition"),
    "objeto": ("existing_object", "vegetation_object", "visible_detail"),
}


def _scope(value: str | SpatialScope) -> str:
    return SpatialScope(value).value


def scale_relevance(spatial_scope: str | SpatialScope, evidence_type: str) -> str:
    scope = _scope(spatial_scope)
    if evidence_type in PROFILE.get(scope, ()):
        return "RELEVANT"
    if evidence_type in {"MANUAL_OBSERVATION", "PHOTO", "EXTERNAL_SOURCE", "STRUCTURED_VALUE"}:
        return "POSSIBLE"
    return "UNKNOWN"


def validate_observation(payload: dict[str, Any]) -> dict[str, Any]:
    scope = _scope(str(payload.get("spatial_scope", "")))
    state = str(payload.get("epistemic_state", "USER_OBSERVED"))
    qualifier = str(payload.get("qualifier", "UNKNOWN"))
    if state not in EPISTEMIC_STATES:
        raise ValueError(f"invalid epistemic_state: {state}")
    if qualifier not in QUALIFIERS:
        raise ValueError(f"invalid qualifier: {qualifier}")
    value = payload.get("value")
    if qualifier == "RANGE" and value is not None and not isinstance(value, (list, tuple, str, dict)):
        raise ValueError("RANGE value must preserve a range representation")
    if qualifier == "APPROXIMATE" and value is None:
        raise ValueError("APPROXIMATE value is required")
    return {"spatial_scope": scope, "epistemic_state": state, "qualifier": qualifier, "unit": payload.get("unit"), "relevance": scale_relevance(scope, str(payload.get("observation_type", "")))}


def _metadata_from_event(event: Any) -> dict[str, Any] | None:
    if event.type != "SPATIAL_EVIDENCE_ADDED":
        return None
    data = dict(event.payload)
    data.setdefault("event_timestamp", event.timestamp)
    data.setdefault("event_actor", event.actor)
    return data


def evidence_view(repo: Any, project_id: str, spatial_scope: str | None = None) -> list[dict[str, Any]]:
    base = {item.evidence_id: asdict(item) for item in repo.list_evidence(project_id)}
    records: list[dict[str, Any]] = []
    reviews: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in repo.events(project_id):
        if event.type == "SPATIAL_EVIDENCE_REVIEWED" and event.payload.get("evidence_id"):
            reviews[str(event.payload["evidence_id"])].append(dict(event.payload))
        metadata = _metadata_from_event(event)
        if metadata is None:
            continue
        evidence_id = str(metadata.get("evidence_id", ""))
        if evidence_id not in base:
            continue
        merged = {**base[evidence_id], **metadata, "reviews": reviews.get(evidence_id, [])}
        if spatial_scope is None or merged.get("spatial_scope") == _scope(spatial_scope):
            records.append(merged)
    records.sort(key=lambda item: (str(item.get("spatial_scope", "")), str(item.get("evidence_id", ""))))
    for record in records:
        record["reviews"] = reviews.get(str(record["evidence_id"]), [])
        record["human_review_state"] = "HUMAN_CONFIRMED" if any(item.get("status") == "APPROVED" for item in record["reviews"]) else ("REJECTED" if any(item.get("status") == "REJECTED" for item in record["reviews"]) else "UNREVIEWED")
    return records


def surface_conflicts(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = (str(record.get("spatial_scope", "")), str(record.get("observation_type", "")))
        if key[1]: groups[key].append(record)
    conflicts: list[dict[str, Any]] = []
    for (scope, observation_type), items in sorted(groups.items()):
        values = {repr(item.get("value")) for item in items if item.get("value") is not None}
        if len(values) > 1:
            conflicts.append({"spatial_scope": scope, "observation_type": observation_type, "evidence_ids": sorted(str(item["evidence_id"]) for item in items), "state": "EVIDENCE_CONFLICT / REQUIRES_HUMAN_REVIEW", "resolution": "NONE"})
    return conflicts


def multiscale_summary(repo: Any, project_id: str) -> dict[str, Any]:
    records = evidence_view(repo, project_id)
    by_scope: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records: by_scope[str(item["spatial_scope"])].append(item)
    return {"scopes": {scope: by_scope.get(scope, []) for scope in sorted(PROFILE)}, "evidence_count": len(records), "conflicts": surface_conflicts(records), "unknowns": [item["evidence_id"] for item in records if item.get("epistemic_state") == "UNKNOWN"], "decision_created": False}


__all__ = ["EPISTEMIC_STATES", "QUALIFIERS", "PROFILE", "validate_observation", "scale_relevance", "evidence_view", "surface_conflicts", "multiscale_summary"]
