from __future__ import annotations

import math

import pytest

from sicl.domain import SpatialScope
from sicl.spatial import (
    DEFAULT_COORDINATE_SYSTEM,
    DEFAULT_UNITS,
    REPRESENTATION_VERSION,
    SpatialElement,
    SpatialRepresentation,
    SpatialValidationError,
    canonical_json,
    input_fingerprint,
    spatial_element_id,
)


def fingerprint() -> str:
    return input_fingerprint(
        {
            "alternative_id": "ALT-A",
            "site": {"area": 1000, "origin": [0, 0, 0]},
            "constraints": ["setback-north", "height-limit"],
            "variables": {"floors": 3},
            "parameters": {"strategy": "compact"},
            "generator_version": "g1",
            "representation_version": REPRESENTATION_VERSION,
        }
    )


def element(element_id: str = "MASS-01", parent_id: str | None = None) -> SpatialElement:
    return SpatialElement(
        id=element_id,
        element_type="BuildingMass",
        geometry={"type": "volume", "coordinates": [[[0, 0, 0], [10, 10, 9]]]},
        level=1,
        parent_id=parent_id,
        labels={"es": "Masa principal"},
        metadata={"program": "mixed_use"},
    )


def representation(*elements: SpatialElement) -> SpatialRepresentation:
    return SpatialRepresentation(
        id="SR-ALT-A-v1",
        alternative_id="ALT-A",
        spatial_scope=SpatialScope.EDIFICACION,
        representation_version=REPRESENTATION_VERSION,
        generator_version="g1",
        coordinate_system=DEFAULT_COORDINATE_SYSTEM,
        units=DEFAULT_UNITS,
        input_fingerprint=fingerprint(),
        seed=None,
        elements=tuple(elements),
    )


def test_valid_spatial_representation_and_required_fields() -> None:
    item = representation(element())
    assert item.validate() is item
    payload = item.to_dict()
    assert payload["alternative_id"] == "ALT-A"
    assert payload["spatial_scope"] == "edificacion"
    assert payload["units"] == "m"
    assert payload["coordinate_system"] == "LOCAL_ENU"


def test_serialization_round_trip_preserves_domain_fields() -> None:
    original = representation(element())
    restored = SpatialRepresentation.from_dict(original.to_dict())
    assert restored == original
    assert restored.to_dict() == original.to_dict()


def test_supported_spatial_scope_is_validated() -> None:
    item = representation(element())
    assert item.spatial_scope is SpatialScope.EDIFICACION
    with pytest.raises(SpatialValidationError, match="spatial_scope"):
        SpatialRepresentation.from_dict({**item.to_dict(), "spatial_scope": "multiscale"})


def test_units_and_coordinate_system_are_explicit() -> None:
    item = representation(element())
    with pytest.raises(SpatialValidationError, match="unsupported units"):
        SpatialRepresentation.from_dict({**item.to_dict(), "units": "unknown"})
    with pytest.raises(SpatialValidationError, match="coordinate_system"):
        SpatialRepresentation.from_dict({**item.to_dict(), "coordinate_system": ""})


def test_coordinate_validation_rejects_non_finite_values() -> None:
    bad = element()
    bad = SpatialElement(
        id=bad.id,
        element_type=bad.element_type,
        geometry={"type": "volume", "coordinates": [[[0, 0, math.nan], [10, 10, 9]]]},
    )
    with pytest.raises(SpatialValidationError, match="non-finite"):
        representation(bad).validate()


def test_spatial_element_ids_are_stable_and_not_array_position_based() -> None:
    first = spatial_element_id("ALT-A", "BuildingMass", "main", generator_version="g1")
    second = spatial_element_id("ALT-A", "BuildingMass", "main", generator_version="g1")
    other_key = spatial_element_id("ALT-A", "BuildingMass", "courtyard", generator_version="g1")
    assert first == second
    assert first != other_key
    assert first.startswith("BuildingMass:main:")


def test_duplicate_spatial_ids_are_rejected() -> None:
    with pytest.raises(SpatialValidationError, match="duplicate"):
        representation(element(), element()).validate()


def test_parent_reference_must_exist() -> None:
    with pytest.raises(SpatialValidationError, match="unknown element"):
        representation(element(parent_id="SITE-UNKNOWN")).validate()
    parent = SpatialElement(
        id="SITE-01",
        element_type="SiteBoundary",
        geometry={"type": "polygon", "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 0]]]},
    )
    assert representation(parent, element(parent_id="SITE-01")).validate()


def test_invalid_geometry_and_malformed_representation_are_rejected() -> None:
    with pytest.raises(SpatialValidationError, match="unsupported"):
        representation(
            SpatialElement(id="BAD", element_type="Unknown", geometry={"type": "circle", "coordinates": [0, 0]})
        ).validate()
    with pytest.raises(SpatialValidationError, match="missing required field"):
        SpatialRepresentation.from_dict({"id": "SR-1"})


def test_fingerprint_is_deterministic_and_ignores_mapping_order() -> None:
    left = {"b": 2, "a": {"z": 1, "y": [3, 2, 1]}}
    right = {"a": {"y": [3, 2, 1], "z": 1}, "b": 2}
    assert input_fingerprint(left) == input_fingerprint(right)
    assert len(input_fingerprint(left)) == 64
    assert canonical_json(left) == canonical_json(right)


def test_fingerprint_changes_for_relevant_version_and_seed() -> None:
    base = {"alternative_id": "ALT-A", "generator_version": "g1", "representation_version": "1.0", "seed": None}
    assert input_fingerprint(base) != input_fingerprint({**base, "generator_version": "g2"})
    assert input_fingerprint(base) != input_fingerprint({**base, "seed": 7})


def test_seed_and_versions_survive_round_trip() -> None:
    item = SpatialRepresentation(
        **{**representation(element()).__dict__, "seed": 7, "generator_version": "g2"}
    )
    restored = SpatialRepresentation.from_dict(item.to_dict())
    assert restored.seed == 7
    assert restored.representation_version == REPRESENTATION_VERSION
    assert restored.generator_version == "g2"


def test_empty_representation_is_valid_when_schema_is_valid() -> None:
    assert representation().validate().elements == ()


def test_ids_reject_random_render_style_values() -> None:
    with pytest.raises(SpatialValidationError, match="non-empty"):
        representation(SpatialElement(id="", element_type="Mass", geometry={"type": "point", "coordinates": [0, 0]})).validate()
