from __future__ import annotations

from typing import Any
from .domain import SpatialScope
from .multiscale import SCALE_ORDER, compatible_scopes

_BASE: dict[str, dict[str, Any]] = {
    "pais": {"generate": ["ALLOCATE", "DISTRIBUTE", "PRESERVE_REGION"], "modify": ["CONCENTRATE", "DISPERSE"], "evolve": ["PARTIAL"], "compare": ["SAME_SCOPE_INDICATORS"], "visualize": ["ABSTRACT_SPATIAL_DIAGRAM", "RELATIONSHIPS"], "data": ["TERRITORIAL_DATA"], "state": "REQUIRES_DATA"},
    "macro_region": {"generate": ["ALLOCATE", "DISTRIBUTE", "CONNECT"], "modify": ["CONCENTRATE", "DISPERSE"], "evolve": ["PARTIAL"], "compare": ["SAME_SCOPE_RELATIONSHIPS"], "visualize": ["ABSTRACT_SPATIAL_DIAGRAM", "NETWORK"], "data": ["REGIONAL_DATA"], "state": "REQUIRES_DATA"},
    "region": {"generate": ["ALLOCATE", "DISTRIBUTE", "PRESERVE_REGION"], "modify": ["CONCENTRATE", "DISPERSE"], "evolve": ["PARTIAL"], "compare": ["SAME_SCOPE_RELATIONSHIPS"], "visualize": ["ABSTRACT_SPATIAL_DIAGRAM", "NETWORK"], "data": ["REGIONAL_DATA"], "state": "REQUIRES_DATA"},
    "provincia_metropoli": {"generate": ["ALLOCATE", "DISTRIBUTE", "CONNECT"], "modify": ["CONCENTRATE", "DISPERSE"], "evolve": ["PARTIAL"], "compare": ["SAME_SCOPE_RELATIONSHIPS"], "visualize": ["ABSTRACT_SPATIAL_DIAGRAM", "NETWORK"], "data": ["METROPOLITAN_DATA"], "state": "REQUIRES_DATA"},
    "distrito_ciudad": {"generate": ["ALLOCATE", "DISTRIBUTE", "CONNECT"], "modify": ["CONCENTRATE", "DISPERSE"], "evolve": ["PARTIAL"], "compare": ["SAME_SCOPE_RELATIONSHIPS"], "visualize": ["ABSTRACT_SPATIAL_DIAGRAM", "NETWORK"], "data": ["URBAN_DATA"], "state": "REQUIRES_DATA"},
    "zona_barrio_sector": {"generate": ["ALLOCATE", "DISTRIBUTE", "PRESERVE_REGION"], "modify": ["CONCENTRATE", "DISPERSE", "SEPARATE"], "evolve": ["PARTIAL"], "compare": ["SAME_SCOPE_RELATIONSHIPS"], "visualize": ["ABSTRACT_SPATIAL_DIAGRAM", "NETWORK"], "data": ["SECTOR_DATA"], "state": "REQUIRES_DATA"},
    "parcela_sitio": {"generate": ["IMPLANTATION", "MASS_PLACEMENT", "OPEN_VOID_ZONE"], "modify": ["ORIENTATION", "SEPARATION", "OCCUPATION"], "evolve": ["INHERITANCE", "MUTATION", "SEED"], "compare": ["2D", "3D", "METRICS"], "visualize": ["SITE_PLAN_2D", "SITE_CONTEXT_3D"], "data": ["SITE_REPRESENTATION"], "state": "AVAILABLE"},
    "edificacion": {"generate": ["MASSING", "FORM_SPACE", "COURTYARD", "CIRCULATION"], "modify": ["SEPARATION", "HEIGHT", "SPATIAL_ORGANIZATION"], "evolve": ["INHERITANCE", "MUTATION", "SEED", "EXTREME"], "compare": ["2D", "3D", "METRICS", "DISTANCE"], "visualize": ["2D", "3D"], "data": ["SPATIAL_REPRESENTATION", "PROGRAM"], "state": "AVAILABLE"},
    "sistema": {"generate": [], "modify": [], "evolve": ["PARTIAL"], "compare": ["SAME_SCOPE"], "visualize": ["CONTEXT_ONLY"], "data": ["SYSTEM_DEFINITION"], "state": "REQUIRES_DATA"},
    "espacio": {"generate": ["ZONE_LAYOUT", "RELATIONSHIP"], "modify": ["DIMENSION", "RELATIVE_POSITION", "SPACE_RELATIONSHIP"], "evolve": ["INHERITANCE", "MUTATION"], "compare": ["2D", "3D", "SPACE_METRICS"], "visualize": ["SPACE_2D", "SPACE_3D"], "data": ["PROGRAM_REQUIREMENT", "SPACE_IDENTITY"], "state": "PARTIAL"},
    "objeto": {"generate": [], "modify": ["SUPPORTED_GEOMETRY_ONLY"], "evolve": [], "compare": ["SAME_SCOPE"], "visualize": ["SUPPORTED_GEOMETRY_ONLY"], "data": ["OBJECT_GEOMETRY"], "state": "NOT_AVAILABLE"},
}

def resolve_generative_capabilities(spatial_scope: SpatialScope | str, typology: str | None = None, stage: str | None = None, available_data: list[str] | None = None, intent: dict[str, Any] | None = None) -> dict[str, Any]:
    scope = spatial_scope.value if isinstance(spatial_scope, SpatialScope) else str(spatial_scope).lower()
    if scope not in _BASE: raise ValueError("UNKNOWN_SPATIAL_SCOPE")
    base = {key: list(value) if isinstance(value, list) else value for key, value in _BASE[scope].items()}
    data = set(available_data or [])
    required = set(base["data"])
    if base["state"] == "REQUIRES_DATA" and required & data:
        base["state"] = "PARTIAL"
    return {"spatial_scope": scope, "typology": typology, "stage": stage, "capability_state": base.pop("state"), "capabilities": base, "available_data": sorted(data), "missing_data": sorted(required - data), "intent_scope_aware": bool(intent is not None), "truthful": True, "camera_zoom_is_not_scope": True}

def capability_matrix() -> list[dict[str, Any]]:
    return [resolve_generative_capabilities(scope) for scope in SCALE_ORDER]

def cross_scale_context(source_scope: SpatialScope | str, source_alternative_id: str, target_scope: SpatialScope | str, target_alternative_id: str | None = None, relationship: str = "DERIVED_WITH_CONTEXT_FROM") -> dict[str, Any]:
    source = source_scope.value if isinstance(source_scope, SpatialScope) else str(source_scope)
    target = target_scope.value if isinstance(target_scope, SpatialScope) else str(target_scope)
    if not compatible_scopes(source, target): raise ValueError("INCOMPATIBLE_SCOPE_RELATIONSHIP")
    return {"relationship": relationship, "source_scope": source, "source_alternative_id": source_alternative_id, "target_scope": target, "target_alternative_id": target_alternative_id, "containment_asserted": False, "provenance": "P7 cross-scale context", "decision_created": False}
