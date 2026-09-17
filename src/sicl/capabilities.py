from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from sicl.domain import SpatialScope

CAPABILITY_PROFILE_VERSION = "multiscale-capability-s7p05-v1"
SOLAR_TEMPORAL_ANALYSIS = "SOLAR_TEMPORAL_ANALYSIS"


class ApplicabilityState(str, Enum):
    AVAILABLE = "AVAILABLE"
    REQUIRES_DATA = "REQUIRES_DATA"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class ProjectCapabilityContext:
    spatial_scope: SpatialScope | str
    typology: str | None = None
    stage: str | None = None
    available_data: frozenset[str] = field(default_factory=frozenset)
    objectives: tuple[str, ...] = ()
    context: str | None = None


@dataclass(frozen=True)
class CapabilityResolution:
    capability_id: str
    spatial_scope: str
    status: ApplicabilityState
    reason_code: str
    reason: str
    required_data: tuple[str, ...] = ()
    missing_data: tuple[str, ...] = ()
    profile_version: str = CAPABILITY_PROFILE_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "spatial_scope": self.spatial_scope,
            "status": self.status.value,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "required_data": list(self.required_data),
            "missing_data": list(self.missing_data),
            "profile_version": self.profile_version,
        }


def _scope(value: SpatialScope | str) -> SpatialScope:
    try:
        return value if isinstance(value, SpatialScope) else SpatialScope(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"INVALID_SPATIAL_SCOPE: {value}") from exc


def _data(values: Iterable[str] | None) -> frozenset[str]:
    return frozenset(item.strip().lower() for item in (values or ()) if item and item.strip())


def resolve_capability(capability_id: str, project_context: ProjectCapabilityContext) -> CapabilityResolution:
    scope = _scope(project_context.spatial_scope)
    if capability_id != SOLAR_TEMPORAL_ANALYSIS:
        raise ValueError(f"UNKNOWN_CAPABILITY: {capability_id}")
    required = ("location", "environmental_data")
    if scope is SpatialScope.EDIFICACION:
        missing = tuple(item for item in required if item not in _data(project_context.available_data))
        if missing:
            return CapabilityResolution(capability_id, scope.value, ApplicabilityState.REQUIRES_DATA, "MISSING_REQUIRED_DATA", "Solar analysis is applicable at edificación but required data are missing.", required, missing)
        return CapabilityResolution(capability_id, scope.value, ApplicabilityState.AVAILABLE, "SUPPORTED_FOR_SCALE", "The implemented S7 building-oriented solar workflow is available for this scale.", required)
    conceptually_applicable = {SpatialScope.PARCELA_SITIO, SpatialScope.ZONA_BARRIO_SECTOR, SpatialScope.DISTRITO_CIUDAD, SpatialScope.PROVINCIA_METROPOLI, SpatialScope.REGION, SpatialScope.MACRO_REGION, SpatialScope.PAIS}
    if scope in conceptually_applicable:
        return CapabilityResolution(capability_id, scope.value, ApplicabilityState.NOT_AVAILABLE, "MODEL_NOT_IMPLEMENTED_FOR_SCALE", "Solar may be meaningful at this scale, but its multiscale model is not implemented in S7-P0.5.", required)
    return CapabilityResolution(capability_id, scope.value, ApplicabilityState.NOT_APPLICABLE, "NOT_MEANINGFUL_FOR_CONTEXT", "The current default context does not establish a meaningful building-oriented solar analysis at this scale.", required)


def resolve_example_capability(example_id: str, capability_id: str, spatial_scope: SpatialScope | str, *, typology: str | None = None, stage: str | None = None, available_data: Iterable[str] | None = None, objectives: Iterable[str] | None = None, context: str | None = None) -> CapabilityResolution:
    if example_id != "UPAO-001":
        raise ValueError(f"EXAMPLE_NOT_FOUND: {example_id}")
    data = _data(available_data) or frozenset({"location", "environmental_data"})
    return resolve_capability(capability_id, ProjectCapabilityContext(spatial_scope, typology, stage, data, tuple(objectives or ()), context))


CANONICAL_SPATIAL_SCOPES = tuple(scope.value for scope in SpatialScope)
assert len(CANONICAL_SPATIAL_SCOPES) == 11

__all__ = ["ApplicabilityState", "CAPABILITY_PROFILE_VERSION", "CANONICAL_SPATIAL_SCOPES", "CapabilityResolution", "ProjectCapabilityContext", "SOLAR_TEMPORAL_ANALYSIS", "resolve_capability", "resolve_example_capability"]
