from __future__ import annotations

import math

import pytest

from sicl.domain import SpatialScope
from sicl.spatial import canonical_json
from sicl.spatial_generator import (
    CONTROLLED_ELEMENT_TYPES,
    DEFAULT_UPAO001_SITE,
    GENERATOR_VERSION,
    SpatialGenerationError,
    UPAO001Site,
    UPAO001SpatialGenerator,
    generate_upao001_alternatives,
    normalize_north,
)


def test_valid_upao_site_generation() -> None:
    generator = UPAO001SpatialGenerator()
    result = generator.generate(generate_upao001_alternatives()[0])
    assert result.spatial_scope is SpatialScope.EDIFICACION
    assert result.units == "m"
    assert result.coordinate_system == "LOCAL_ENU"
    assert {item.element_type for item in result.elements} == CONTROLLED_ELEMENT_TYPES


def test_three_alternatives_are_deterministic_and_spatially_distinct() -> None:
    generator = UPAO001SpatialGenerator()
    alternatives = generate_upao001_alternatives()
    first = [generator.generate(item) for item in alternatives]
    second = [generator.generate(item) for item in alternatives]
    assert [item.to_dict() for item in first] == [item.to_dict() for item in second]
    assert len({canonical_json(item.to_dict()) for item in first}) == 3
    assert len({item.input_fingerprint for item in first}) == 3


def test_representation_and_element_ids_are_stable() -> None:
    generator = UPAO001SpatialGenerator()
    left = generator.generate(generate_upao001_alternatives()[0])
    right = generator.generate(generate_upao001_alternatives()[0])
    assert left.id == right.id
    assert [item.id for item in left.elements] == [item.id for item in right.elements]
    assert left.generator_version == GENERATOR_VERSION


def test_north_normalization_and_generation_use_canonical_orientation() -> None:
    assert normalize_north(360) == 0
    assert normalize_north(720) == 0
    assert normalize_north(-360) == 0
    assert normalize_north(-90) == 270
    generator = UPAO001SpatialGenerator()
    alternative = generate_upao001_alternatives()[0]
    zero = generator.generate(alternative, site=UPAO001Site(DEFAULT_UPAO001_SITE.polygon, north_degrees=0))
    three_sixty = generator.generate(alternative, site=UPAO001Site(DEFAULT_UPAO001_SITE.polygon, north_degrees=360))
    assert zero.north_degrees == three_sixty.north_degrees == 0
    assert zero.to_dict() == three_sixty.to_dict()


def test_footprint_is_valid_and_contained_in_site() -> None:
    generator = UPAO001SpatialGenerator()
    result = generator.generate(generate_upao001_alternatives()[1])
    site = next(item for item in result.elements if item.element_type == "SiteBoundary")
    footprint = next(item for item in result.elements if item.element_type == "BuildingFootprint")
    assert site.geometry["type"] in {"polygon", "multipolygon"}
    assert footprint.geometry["type"] in {"polygon", "multipolygon"}
    assert generator.metrics(result)["site_area"] > 0
    assert generator.metrics(result)["footprint_area"] > 0
    assert generator.metrics(result)["coverage_ratio"] < 1


def test_building_mass_has_explicit_semantics_and_height_is_derived() -> None:
    generator = UPAO001SpatialGenerator()
    result = generator.generate(generate_upao001_alternatives()[0])
    mass = next(item for item in result.elements if item.element_type == "BuildingMass")
    assert mass.metadata["footprint_reference"]
    assert mass.metadata["base_elevation"] == 0.0
    assert mass.metadata["floor_count"] == 5
    assert mass.metadata["floor_to_floor_height"] == 3.2
    assert mass.metadata["height"] == pytest.approx(16.0)
    assert generator.metrics(result)["gross_massing_area"] > 0


def test_zones_and_circulation_have_valid_parent_references() -> None:
    result = UPAO001SpatialGenerator().generate(generate_upao001_alternatives()[2])
    ids = {item.id for item in result.elements}
    zones = [item for item in result.elements if item.element_type == "SpatialZone"]
    circulation = next(item for item in result.elements if item.element_type == "CirculationElement")
    assert len(zones) == 3
    assert all(item.parent_id in ids for item in zones)
    assert circulation.parent_id in ids
    assert circulation.geometry["type"] == "line"


def test_floor_limit_is_model_constraint_not_universal_regulation() -> None:
    alternative = generate_upao001_alternatives()[0]
    alternative.parameters["floors"] = 7
    with pytest.raises(SpatialGenerationError, match="INVALID_FLOOR_COUNT"):
        UPAO001SpatialGenerator().generate(alternative)
    result = UPAO001SpatialGenerator().generate(alternative, constraints={"max_floors": 8})
    assert UPAO001SpatialGenerator().metrics(result)["floor_count"] == 7


def test_outside_site_and_invalid_parameters_fail_without_silent_correction() -> None:
    site = UPAO001Site(((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)))
    alternative = generate_upao001_alternatives()[0]
    alternative.parameters["footprint_ratio"] = 1.2
    with pytest.raises(SpatialGenerationError, match="footprint_ratio"):
        UPAO001SpatialGenerator().generate(alternative, site=site)
    with pytest.raises(SpatialGenerationError, match="INVALID_SITE"):
        UPAO001SpatialGenerator().generate(alternative, site=UPAO001Site(((0.0, 0.0), (1.0, 0.0), (0.0, 0.0))))


def test_controlled_types_and_explainability_are_available() -> None:
    result = UPAO001SpatialGenerator().generate(generate_upao001_alternatives()[0])
    assert {item.element_type for item in result.elements} <= CONTROLLED_ELEMENT_TYPES
    explanation = UPAO001SpatialGenerator().explain(result)
    assert explanation["alternative_id"] == "UPAO-001-A"
    assert explanation["provenance"] == "SYNTHETIC / EDUCATIONAL / MODEL PROJECT"
    assert {rule["parameter"] for rule in explanation["rules"]} >= {"strategy", "footprint_ratio", "floors"}


def test_relevant_parameter_changes_fingerprint_and_geometry() -> None:
    generator = UPAO001SpatialGenerator()
    alternative = generate_upao001_alternatives()[0]
    first = generator.generate(alternative)
    alternative.parameters["footprint_ratio"] = 0.30
    second = generator.generate(alternative)
    assert first.input_fingerprint != second.input_fingerprint
    assert first.to_dict() != second.to_dict()


def test_irrelevant_alternative_metadata_does_not_change_geometry() -> None:
    generator = UPAO001SpatialGenerator()
    first_alt = generate_upao001_alternatives()[0]
    second_alt = generate_upao001_alternatives()[0]
    second_alt.description = "Documentation-only description"
    second_alt.status = "PROPOSED"
    second_alt.version = 99
    left = generator.generate(first_alt)
    right = generator.generate(second_alt)
    assert left.to_dict() == right.to_dict()


def test_malformed_orientation_is_rejected() -> None:
    alternative = generate_upao001_alternatives()[0]
    alternative.parameters["orientation"] = math.nan
    with pytest.raises(SpatialGenerationError, match="north_degrees"):
        UPAO001SpatialGenerator().generate(alternative)


def test_empty_or_minimum_inputs_are_explicit() -> None:
    alternative = generate_upao001_alternatives()[0]
    alternative.parameters["strategy"] = "unknown"
    with pytest.raises(SpatialGenerationError, match="strategy"):
        UPAO001SpatialGenerator().generate(alternative)
