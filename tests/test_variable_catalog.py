from __future__ import annotations

from dataclasses import asdict

import pytest

from sicl.domain import Event, Project, SpatialScope, now_iso
from sicl.feasibility import ProjectVariable, SuggestedVariable, VariableType, project_variable_dict
from sicl.repository import SQLiteRepository
from sicl.variable_catalog import (
    CATALOG_VERSION,
    ScaleVariableProfile,
    VariableDefinition,
    build_catalog,
    seed_catalog,
)


def test_seed_catalog_has_stable_identity_and_exact_scopes() -> None:
    catalog = seed_catalog()
    assert catalog.catalog_version == CATALOG_VERSION
    assert tuple(catalog.definitions) == (
        "BUILDING_FOOTPRINT",
        "BUILDING_GROSS_AREA",
        "BUILDING_MASSING",
        "BUILDING_FLOORS",
        "SITE_COORDINATE_REFERENCE",
        "SITE_SOIL_CONDITION",
        "SITE_ET0",
        "SITE_VPD",
    )
    assert {profile.spatial_scope for profile in catalog.profiles.values()} <= {
        SpatialScope.EDIFICACION,
        SpatialScope.PARCELA_SITIO,
    }
    assert len(catalog.profiles) == 8
    assert catalog.profile("SITE_ET0", "parcela_sitio").applicability == "REQUIRES_DATA"


def test_profile_resolution_rejects_invalid_scale_and_preserves_requirement_semantics() -> None:
    catalog = seed_catalog()
    profile = catalog.profile("BUILDING_MASSING", SpatialScope.EDIFICACION)
    assert profile.requirement == "REQUIRED"
    assert profile.applicability == "AVAILABLE"
    with pytest.raises(ValueError, match="is not a valid SpatialScope"):
        catalog.profile("BUILDING_MASSING", "multiscale")
    with pytest.raises(KeyError, match="no profile"):
        catalog.profile("BUILDING_MASSING", SpatialScope.PARCELA_SITIO)


def test_catalog_rejects_duplicate_definition_and_profile_identity() -> None:
    definition = VariableDefinition("DUPLICATE", "Duplicate", "TEST", "Meaning", "DECIMAL", "m", "BASE")
    with pytest.raises(ValueError, match="duplicate canonical variable ID"):
        build_catalog([definition, definition], [])
    profile = ScaleVariableProfile("DUPLICATE", SpatialScope.EDIFICACION, "OPTIONAL", "AVAILABLE")
    with pytest.raises(ValueError, match="duplicate scale variable profile"):
        build_catalog([definition], [profile, profile])


def test_suggested_variable_references_catalog_without_creating_project_state() -> None:
    catalog = seed_catalog()
    metadata = catalog.suggested_variable_metadata("BUILDING_FOOTPRINT", "edificacion")
    suggestion = SuggestedVariable(
        metadata["suggestion_id"],
        metadata["normalized_key"],
        metadata["label"],
        VariableType(metadata["variable_type"]),
        metadata["spatial_scope"],
        canonical_variable_id=metadata["canonical_variable_id"],
        catalog_version=metadata["catalog_version"],
        definition_version=metadata["definition_version"],
        profile_version=metadata["profile_version"],
    )
    assert suggestion.canonical_variable_id == "BUILDING_FOOTPRINT"
    assert suggestion.catalog_version == CATALOG_VERSION
    assert suggestion.profile_version == "1"


def test_project_adoption_is_explicit_and_reloads_from_event_log(tmp_path) -> None:
    catalog = seed_catalog()
    metadata = catalog.suggested_variable_metadata("BUILDING_FOOTPRINT", SpatialScope.EDIFICACION)
    variable = ProjectVariable(
        "PV-FOOTPRINT-001",
        "P-MV-P1",
        "BUILDING_FOOTPRINT",
        VariableType.PARAMETER,
        120.0,
        "architect",
        "PROJECT_OWNER",
        "m²",
        "edificacion",
        "USER_INPUT",
        1,
        None,
        None,
        metadata["canonical_variable_id"],
        metadata["catalog_version"],
        metadata["definition_version"],
        metadata["profile_version"],
    )
    repo = SQLiteRepository(tmp_path / "mv-p1.sqlite")
    repo.insert_project(
        Project("P-MV-P1", "MV-P1", spatial_scope=SpatialScope.EDIFICACION),
        Event(None, now_iso(), "P-MV-P1", "PROJECT_CREATED", {}, "architect", "test"),
    )
    repo.add_event(Event(None, now_iso(), "P-MV-P1", "PROJECT_VARIABLE_RECORDED", project_variable_dict(variable), "architect", "test"))
    reopened = repo.get_project("P-MV-P1")
    assert reopened is not None
    assert reopened.objectives == {}
    assert reopened.decisions == {}
    assert reopened.project_variables[variable.variable_id]["canonical_variable_id"] == "BUILDING_FOOTPRINT"
    assert reopened.project_variables[variable.variable_id]["profile_version"] == "1"


def test_catalog_definition_change_does_not_mutate_adopted_metadata() -> None:
    catalog = seed_catalog()
    metadata = catalog.suggested_variable_metadata("BUILDING_FOOTPRINT", "edificacion")
    adopted = {
        "canonical_variable_id": metadata["canonical_variable_id"],
        "catalog_version": metadata["catalog_version"],
        "definition_version": metadata["definition_version"],
        "profile_version": metadata["profile_version"],
    }
    newer = VariableDefinition(
        "BUILDING_FOOTPRINT",
        "Building Footprint revised",
        "BUILDING",
        "Revised meaning",
        "DECIMAL",
        "m²",
        "DERIVED",
        definition_version="2",
        catalog_version="mv-p1.2-future",
    )
    assert newer.definition_version == "2"
    assert adopted == {
        "canonical_variable_id": "BUILDING_FOOTPRINT",
        "catalog_version": CATALOG_VERSION,
        "definition_version": "1",
        "profile_version": "1",
    }
    assert asdict(newer)["definition_version"] != adopted["definition_version"]
