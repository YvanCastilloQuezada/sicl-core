"""Derived hierarchical design state over existing canonical spatial surfaces.

This module deliberately defines no new canonical alternative or graph entity.
It derives site -> building -> mass -> space dependency data from existing
Alternative, SpatialRepresentation and P3 outputs.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def _element_kind(element: dict[str, Any]) -> str:
    return str(element.get("element_type", "")).upper()


def _node(node_id: str, scope: str, kind: str, state: str, parent_id: str | None, source_ids: list[str], **extra: Any) -> dict[str, Any]:
    return {"id": node_id, "spatial_scope": scope, "kind": kind, "state": state, "parent_id": parent_id, "source_ids": source_ids, **extra}


def derive_hierarchical_state(alternative: dict[str, Any], representation: dict[str, Any], space_layout: dict[str, Any] | None = None, *, downstream_state: str = "RECOMPUTED") -> dict[str, Any]:
    """Derive a coherent site/building/mass/space state from existing data."""
    alternative_id = str(alternative.get("alternative_id"))
    elements = list(representation.get("elements", []))
    site = next((item for item in elements if "SITE" in _element_kind(item)), None)
    footprint = next((item for item in elements if "FOOTPRINT" in _element_kind(item)), None)
    masses = [item for item in elements if "MASS" in _element_kind(item)]
    site_id = f"{alternative_id}:SITE"
    building_id = f"{alternative_id}:BUILDING"
    site_node = _node(site_id, "parcela_sitio", "SITE", "PRESERVED", None, [str(site.get("id"))] if site else [], geometry=site.get("geometry") if site else None)
    building_node = _node(building_id, "edificacion", "BUILDING", downstream_state, site_id, [str(footprint.get("id"))] if footprint else [], geometry=footprint.get("geometry") if footprint else None, depends_on=[site_id])
    mass_nodes = []
    for index, mass in enumerate(masses, 1):
        mass_id = f"{alternative_id}:MASS:{index}"
        mass_nodes.append(_node(mass_id, "edificacion", "MASS", downstream_state, building_id, [str(mass.get("id"))], geometry=mass.get("geometry"), depends_on=[building_id]))
    space_nodes = []
    relationships: list[dict[str, Any]] = []
    if space_layout:
        space_rep = space_layout.get("representation", {})
        for index, item in enumerate(space_rep.get("elements", []), 1):
            if "ZONE" not in _element_kind(item):
                continue
            sid = str(item.get("id") or f"{alternative_id}:SPACE:{index}")
            space_nodes.append(_node(sid, "espacio", "SPACE", downstream_state, building_id, [sid], geometry=item.get("geometry"), depends_on=[building_id], program_requirement_id=item.get("metadata", {}).get("program_requirement_id")))
        relationships = [deepcopy(edge) for edge in (space_layout.get("relationship_evaluation") or [])]
    return {"alternative_id": alternative_id, "validity": "VALID_DERIVED_STATE", "provenance": "DERIVED_FROM_SPATIAL_REPRESENTATION_AND_P3", "nodes": [site_node, building_node, *mass_nodes, *space_nodes], "dependencies": [{"source": building_id, "target": site_id, "type": "DEPENDS_ON", "state": downstream_state}, *[{"source": node["id"], "target": building_id, "type": "DEPENDS_ON", "state": downstream_state} for node in mass_nodes], *[{"source": node["id"], "target": building_id, "type": "DEPENDS_ON", "state": downstream_state} for node in space_nodes]], "relationships": relationships, "unsupported_levels": ["sistema", "objeto"], "unknowns": ["Regulatory compliance, buildability, structural performance, comfort and energy performance are not computed."], "hierarchical_distance_readiness": "PARTIAL"}


def hierarchical_compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Compare supported derived levels without inventing unsupported semantics."""
    def by_kind(state: dict[str, Any], kind: str) -> list[dict[str, Any]]:
        return [node for node in state.get("nodes", []) if node.get("kind") == kind]
    levels: dict[str, Any] = {}
    for kind, label in (("SITE", "SITE"), ("BUILDING", "BUILDING"), ("MASS", "MASS"), ("SPACE", "SPACE")):
        a, b = by_kind(left, kind), by_kind(right, kind)
        levels[label] = {"left_count": len(a), "right_count": len(b), "count_changed": len(a) != len(b), "status": "SUPPORTED" if a or b else "UNKNOWN / NOT_CURRENTLY_REPRESENTED"}
    return {"left_alternative_id": left.get("alternative_id"), "right_alternative_id": right.get("alternative_id"), "levels": levels, "no_winner": True, "recommendation_created": False, "decision_created": False, "hierarchical_distance_readiness": "PARTIAL", "relational_distance_readiness": "INSUFFICIENT"}


def propagate_upstream_change(parent_state: dict[str, Any], child_state: dict[str, Any], changed_level: str) -> dict[str, Any]:
    changed = str(changed_level).upper()
    affected = [node["id"] for node in child_state.get("nodes", []) if node.get("spatial_scope") in {"edificacion", "espacio"}] if changed in {"SITE", "BUILDING"} else []
    return {"changed_level": changed, "affected_nodes": affected, "recomputed": affected, "preserved": [node["id"] for node in child_state.get("nodes", []) if node["id"] not in affected], "invalidated": [], "requires_human_review": bool(affected), "unknown": ["Real-world performance and regulatory consequences remain unknown."], "status": "RECOMPUTED" if affected else "PRESERVED"}


def propagate_space_geometry_change(parent_state: dict[str, Any], child_state: dict[str, Any], changed_node_id: str, changed_parameters: dict[str, Any]) -> dict[str, Any]:
    """Propagate a lower block/mass geometry change into dependent spaces.

    The function never silently preserves stale space state. It recomputes
    dependent spaces when they are represented, preserves unrelated nodes, and
    marks relationships for human review because geometric relationship
    satisfaction is not claimed without a validated spatial solver.
    """
    nodes = child_state.get("nodes", [])
    changed = next((node for node in nodes if node.get("id") == changed_node_id), None)
    if changed is None:
        return {"status": "UNKNOWN", "changed_node_id": changed_node_id, "affected_nodes": [], "recomputed": [], "preserved": [node.get("id") for node in nodes], "invalidated": [], "requires_human_review": True, "unknown": ["Changed node is not represented in the derived state."]}
    dependent_space_ids = [node.get("id") for node in nodes if node.get("kind") == "SPACE" and (changed_node_id in node.get("depends_on", []) or changed.get("kind") in {"MASS", "BUILDING"})]
    affected_relationships = list(child_state.get("relationships", [])) if dependent_space_ids else []
    preserved = [node.get("id") for node in nodes if node.get("id") not in dependent_space_ids and node.get("id") != changed_node_id]
    return {"status": "REQUIRES_HUMAN_REVIEW" if affected_relationships else "RECOMPUTED", "changed_node_id": changed_node_id, "changed_level": changed.get("kind"), "changed_parameters": dict(changed_parameters), "affected_nodes": dependent_space_ids, "recomputed": dependent_space_ids, "preserved": [changed_node_id, *preserved], "invalidated": [], "relationships_requiring_review": affected_relationships, "requires_human_review": bool(affected_relationships), "unknown": ["Adjacency, connectivity and functional performance are not recomputed as validated architectural facts."]}


__all__ = ["derive_hierarchical_state", "hierarchical_compare", "propagate_upstream_change", "propagate_space_geometry_change"]
