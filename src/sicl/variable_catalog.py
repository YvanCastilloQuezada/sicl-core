"""Immutable runtime catalogue foundation for the MV-P1 variable architecture.

The catalogue is packaged metadata. Project adoption remains represented by the
existing SuggestedVariable and ProjectVariable entities and their event log.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .domain import SpatialScope


CATALOG_VERSION = "mv-p1.1-2026-09-17"
REQUIREMENTS = frozenset({"REQUIRED", "RECOMMENDED", "OPTIONAL", "NOT_APPLICABLE"})
APPLICABILITIES = frozenset({"AVAILABLE", "REQUIRES_DATA", "NOT_AVAILABLE", "NOT_APPLICABLE"})
BASE_OR_DERIVED = frozenset({"BASE", "DERIVED"})
STATUSES = frozenset({"ACTIVE", "DRAFT", "DEPRECATED"})


@dataclass(frozen=True)
class VariableDefinition:
    canonical_variable_id: str
    canonical_name: str
    domain: str
    semantic_definition: str
    data_type: str
    unit_semantics: str
    base_or_derived: str
    definition_version: str = "1"
    status: str = "ACTIVE"
    catalog_version: str = CATALOG_VERSION

    def __post_init__(self) -> None:
        if not self.canonical_variable_id or not self.canonical_variable_id.strip():
            raise ValueError("canonical_variable_id is required")
        if not self.canonical_name or not self.semantic_definition:
            raise ValueError("canonical_name and semantic_definition are required")
        if self.base_or_derived not in BASE_OR_DERIVED:
            raise ValueError(f"invalid base_or_derived: {self.base_or_derived}")
        if self.status not in STATUSES:
            raise ValueError(f"invalid definition status: {self.status}")
        if not self.definition_version or not self.catalog_version:
            raise ValueError("definition_version and catalog_version are required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScaleVariableProfile:
    canonical_variable_id: str
    spatial_scope: SpatialScope
    requirement: str
    applicability: str
    conditional_applicability: str | None = None
    spatial_support: str = "DECLARED"
    temporal_semantics: str = "PROJECT"
    profile_version: str = "1"
    catalog_version: str = CATALOG_VERSION

    def __post_init__(self) -> None:
        if not self.canonical_variable_id:
            raise ValueError("canonical_variable_id is required")
        if not isinstance(self.spatial_scope, SpatialScope):
            raise ValueError("spatial_scope must use the canonical SpatialScope enum")
        if self.requirement not in REQUIREMENTS:
            raise ValueError(f"invalid requirement: {self.requirement}")
        if self.applicability not in APPLICABILITIES:
            raise ValueError(f"invalid applicability: {self.applicability}")
        if not self.profile_version or not self.catalog_version:
            raise ValueError("profile_version and catalog_version are required")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["spatial_scope"] = self.spatial_scope.value
        return value


@dataclass(frozen=True)
class VariableCatalog:
    catalog_version: str
    definitions: Mapping[str, VariableDefinition]
    profiles: Mapping[tuple[str, SpatialScope], ScaleVariableProfile]

    def __post_init__(self) -> None:
        if not self.catalog_version:
            raise ValueError("catalog_version is required")
        definitions = dict(self.definitions)
        profiles = dict(self.profiles)
        if set(definitions) != {item.canonical_variable_id for item in definitions.values()}:
            raise ValueError("definition identity must match canonical_variable_id")
        for key, profile in profiles.items():
            if key != (profile.canonical_variable_id, profile.spatial_scope):
                raise ValueError("profile identity must match canonical_variable_id and spatial_scope")
            if profile.canonical_variable_id not in definitions:
                raise ValueError(f"profile references unknown definition: {profile.canonical_variable_id}")
        object.__setattr__(self, "definitions", MappingProxyType(definitions))
        object.__setattr__(self, "profiles", MappingProxyType(profiles))

    def definition(self, canonical_variable_id: str) -> VariableDefinition:
        try:
            return self.definitions[canonical_variable_id]
        except KeyError as exc:
            raise KeyError(f"unknown canonical variable: {canonical_variable_id}") from exc

    def profile(self, canonical_variable_id: str, spatial_scope: SpatialScope | str) -> ScaleVariableProfile:
        scope = SpatialScope(spatial_scope)
        try:
            return self.profiles[(canonical_variable_id, scope)]
        except KeyError as exc:
            raise KeyError(f"no profile for {canonical_variable_id} at {scope.value}") from exc

    def suggested_variable_metadata(self, canonical_variable_id: str, spatial_scope: SpatialScope | str) -> dict[str, Any]:
        definition = self.definition(canonical_variable_id)
        profile = self.profile(canonical_variable_id, spatial_scope)
        return {
            "suggestion_id": f"SUGGESTED-{canonical_variable_id}-{profile.spatial_scope.value}",
            "normalized_key": canonical_variable_id,
            "label": definition.canonical_name,
            "variable_type": "PARAMETER",
            "spatial_scope": profile.spatial_scope.value,
            "normative_reference": None,
            "canonical_variable_id": definition.canonical_variable_id,
            "catalog_version": self.catalog_version,
            "definition_version": definition.definition_version,
            "profile_version": profile.profile_version,
        }


def _definition(variable_id: str, name: str, domain: str, meaning: str, data_type: str, unit: str, kind: str) -> VariableDefinition:
    return VariableDefinition(variable_id, name, domain, meaning, data_type, unit, kind)


_SEED_DEFINITIONS = (
    _definition("BUILDING_FOOTPRINT", "Building Footprint", "BUILDING", "Conceptual ground footprint occupied by the building mass.", "DECIMAL", "m²", "DERIVED"),
    _definition("BUILDING_GROSS_AREA", "Building Gross Area", "BUILDING", "Conceptual gross area represented by the building model.", "DECIMAL", "m²", "DERIVED"),
    _definition("BUILDING_MASSING", "Building Massing", "BUILDING", "Conceptual massing representation of the building alternative.", "OBJECT", "geometry", "DERIVED"),
    _definition("BUILDING_FLOORS", "Building Floors", "BUILDING", "Number of floors represented by the building alternative.", "INTEGER", "count", "BASE"),
    _definition("SITE_COORDINATE_REFERENCE", "Site Coordinate Reference", "SITE", "Declared coordinate reference for a project site.", "OBJECT", "coordinate_reference", "BASE"),
    _definition("SITE_SOIL_CONDITION", "Site Soil Condition", "SITE", "Declared soil condition relevant to site analysis.", "OBJECT", "classification", "BASE"),
    _definition("SITE_ET0", "Site ET0", "SITE", "Reference evapotranspiration associated with the site and period.", "DECIMAL", "mm/day", "DERIVED"),
    _definition("SITE_VPD", "Site VPD", "SITE", "Vapour pressure deficit associated with the site and period.", "DECIMAL", "kPa", "DERIVED"),
)


def _profile(variable_id: str, scope: SpatialScope, requirement: str, applicability: str, condition: str | None = None) -> ScaleVariableProfile:
    return ScaleVariableProfile(variable_id, scope, requirement, applicability, condition)


_SEED_PROFILES = (
    _profile("BUILDING_FOOTPRINT", SpatialScope.EDIFICACION, "RECOMMENDED", "AVAILABLE"),
    _profile("BUILDING_GROSS_AREA", SpatialScope.EDIFICACION, "RECOMMENDED", "AVAILABLE"),
    _profile("BUILDING_MASSING", SpatialScope.EDIFICACION, "REQUIRED", "AVAILABLE"),
    _profile("BUILDING_FLOORS", SpatialScope.EDIFICACION, "RECOMMENDED", "AVAILABLE"),
    _profile("SITE_COORDINATE_REFERENCE", SpatialScope.PARCELA_SITIO, "REQUIRED", "REQUIRES_DATA", "requires an explicit project location"),
    _profile("SITE_SOIL_CONDITION", SpatialScope.PARCELA_SITIO, "RECOMMENDED", "REQUIRES_DATA", "requires a site source or observation"),
    _profile("SITE_ET0", SpatialScope.PARCELA_SITIO, "OPTIONAL", "REQUIRES_DATA", "requires a declared location and time period"),
    _profile("SITE_VPD", SpatialScope.PARCELA_SITIO, "OPTIONAL", "REQUIRES_DATA", "requires a declared location and time period"),
)


def build_catalog(
    definitions: tuple[VariableDefinition, ...] | list[VariableDefinition],
    profiles: tuple[ScaleVariableProfile, ...] | list[ScaleVariableProfile],
    *,
    catalog_version: str = CATALOG_VERSION,
) -> VariableCatalog:
    definition_map: dict[str, VariableDefinition] = {}
    for item in definitions:
        if item.canonical_variable_id in definition_map:
            raise ValueError(f"duplicate canonical variable ID: {item.canonical_variable_id}")
        definition_map[item.canonical_variable_id] = item
    profile_map: dict[tuple[str, SpatialScope], ScaleVariableProfile] = {}
    for item in profiles:
        key = (item.canonical_variable_id, item.spatial_scope)
        if key in profile_map:
            raise ValueError(f"duplicate scale variable profile: {item.canonical_variable_id}:{item.spatial_scope.value}")
        profile_map[key] = item
    return VariableCatalog(catalog_version, definition_map, profile_map)


def build_seed_catalog() -> VariableCatalog:
    return build_catalog(_SEED_DEFINITIONS, _SEED_PROFILES)


SEED_CATALOG = build_seed_catalog()


def seed_catalog() -> VariableCatalog:
    """Return the immutable deterministic MV-P1.1 seed catalogue."""
    return SEED_CATALOG


__all__ = [
    "CATALOG_VERSION",
    "VariableDefinition",
    "ScaleVariableProfile",
    "VariableCatalog",
    "SEED_CATALOG",
    "build_catalog",
    "build_seed_catalog",
    "seed_catalog",
]
