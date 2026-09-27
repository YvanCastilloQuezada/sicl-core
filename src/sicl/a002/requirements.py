"""Operation-specific A-002 requirement policies."""
from __future__ import annotations
from .model import KnowledgeState, OperationRequirement
from ..domain import SpatialScope


def preliminary_building_massing_requirements() -> tuple[OperationRequirement, ...]:
    return (
        OperationRequirement("site_geometry", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED), True, (SpatialScope.PARCELA_SITIO,), reason="massing requires a bounded site"),
        OperationRequirement("program", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED), True, (SpatialScope.EDIFICACION,), reason="massing requires an explicit program"),
        OperationRequirement("target_floor_area", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED), True, (SpatialScope.EDIFICACION,), reason="massing requires a target floor area"),
        OperationRequirement("orientation", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED, KnowledgeState.ASSUMED), False, (SpatialScope.PARCELA_SITIO,), reason="orientation may remain an explicit assumption", allow_assumed=True),
        OperationRequirement("jurisdiction", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED), True, (SpatialScope.DISTRITO_CIUDAD, SpatialScope.PARCELA_SITIO), jurisdiction_required=True, reason="normative applicability requires jurisdiction"),
        OperationRequirement("height_limit", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED), True, (SpatialScope.EDIFICACION,), jurisdiction_required=True, reason="height limit is required for safe massing"),
        OperationRequirement("budget", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED, KnowledgeState.ASSUMED), False, (SpatialScope.EDIFICACION,), reason="budget affects feasibility but does not block conceptual massing", allow_assumed=True),
        OperationRequirement("client_preferences", (KnowledgeState.KNOWN, KnowledgeState.OBSERVED, KnowledgeState.ASSUMED), False, (SpatialScope.EDIFICACION,), reason="preferences refine the proposal", allow_assumed=True),
    )


def requirements_for(operation: str) -> tuple[OperationRequirement, ...]:
    if operation == "preliminary building massing":
        return preliminary_building_massing_requirements()
    raise KeyError(f"no A-002 policy registered for operation: {operation}")
