from dataclasses import replace

from sicl.archi import ArchiElement, ArchiElementId, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec
from sicl.archi.creation_validation import validate_creation


def element(
    nonce: str,
    *,
    project_id: str = "P",
    kind: ElementKind = ElementKind.SPACE,
    properties=None,
    provenance=None,
    hosted_in=None,
    contained_in=None,
):
    geometry = ArchiGeometry(
        GeometryKind.EXTRUDED_RECTANGLE,
        ProfileSpec(3000, 3000),
        height_mm=2800,
    )
    return ArchiElement(
        ArchiElementId.compute(project_id, kind.value, nonce),
        project_id,
        kind,
        geometry,
        properties={} if properties is None else properties,
        provenance={"source": "developer-proposal"} if provenance is None else provenance,
        hosted_in=hosted_in,
        contained_in=contained_in,
    )


def test_valid_batch_without_references():
    result = validate_creation(project_id="P", candidate_elements=(element("a"),), existing_canonical=())
    assert result.valid and result.errors == () and result.warnings == ()


def test_valid_hosted_in_existing_canonical():
    wall = element("wall", kind=ElementKind.WALL)
    door = element("door", kind=ElementKind.DOOR, hosted_in=wall.element_id)
    assert validate_creation(project_id="P", candidate_elements=(door,), existing_canonical=(wall,)).valid


def test_valid_hosted_in_same_candidate_batch():
    wall = element("wall", kind=ElementKind.WALL)
    door = element("door", kind=ElementKind.DOOR, hosted_in=wall.element_id)
    assert validate_creation(project_id="P", candidate_elements=(wall, door), existing_canonical=()).valid


def test_empty_batch_is_invalid():
    result = validate_creation(project_id="P", candidate_elements=(), existing_canonical=())
    assert not result.valid and result.errors == ("CANDIDATE_ELEMENTS_EMPTY",)


def test_project_id_mismatch_is_invalid():
    wrong = element("a", project_id="OTHER")
    result = validate_creation(project_id="P", candidate_elements=(wrong,), existing_canonical=())
    assert not result.valid and any(error.startswith("PROJECT_ID_MISMATCH:") for error in result.errors)


def test_duplicate_id_in_batch_is_invalid():
    item = element("same")
    result = validate_creation(project_id="P", candidate_elements=(item, item), existing_canonical=())
    assert not result.valid and any(error.startswith("DUPLICATE_ELEMENT_ID_IN_BATCH:") for error in result.errors)


def test_collision_with_canonical_is_invalid():
    item = element("same")
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=(item,))
    assert not result.valid and any(error.startswith("ELEMENT_ID_COLLIDES_WITH_CANONICAL:") for error in result.errors)


def test_canonical_true_property_is_invalid():
    item = element("a", properties={"canonical": True})
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=())
    assert not result.valid and any(error.startswith("PROPERTIES_DECLARE_CANONICAL_TRUE:") for error in result.errors)


def test_missing_provenance_is_invalid():
    item = element("a", provenance={})
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=())
    assert not result.valid and any(error.startswith("PROVENANCE_MISSING:") for error in result.errors)


def test_orphan_hosted_in_is_invalid():
    missing = ArchiElementId.compute("P", "WALL", "missing")
    item = element("door", kind=ElementKind.DOOR, hosted_in=missing)
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=())
    assert not result.valid and any(error.startswith("ORPHAN_HOSTED_IN:") for error in result.errors)


def test_orphan_contained_in_is_invalid():
    missing = ArchiElementId.compute("P", "DOOR", "missing")
    item = element("opening", kind=ElementKind.OPENING, contained_in=missing)
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=())
    assert not result.valid and any(error.startswith("ORPHAN_CONTAINED_IN:") for error in result.errors)


def test_self_hosted_in_is_invalid():
    item = element("door", kind=ElementKind.DOOR)
    item = replace(item, hosted_in=item.element_id)
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=())
    assert not result.valid and any(error.startswith("SELF_HOSTED_IN:") for error in result.errors)


def test_self_contained_in_is_invalid():
    item = element("opening", kind=ElementKind.OPENING)
    item = replace(item, contained_in=item.element_id)
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=())
    assert not result.valid and any(error.startswith("SELF_CONTAINED_IN:") for error in result.errors)


def test_multiple_errors_are_reported_together():
    missing = ArchiElementId.compute("P", "WALL", "missing")
    item = element("a", project_id="OTHER", properties={"canonical": True}, provenance={}, hosted_in=missing)
    result = validate_creation(project_id="P", candidate_elements=(item, item), existing_canonical=())
    assert not result.valid
    assert any(error.startswith("PROJECT_ID_MISMATCH:") for error in result.errors)
    assert any(error.startswith("DUPLICATE_ELEMENT_ID_IN_BATCH:") for error in result.errors)
    assert any(error.startswith("PROPERTIES_DECLARE_CANONICAL_TRUE:") for error in result.errors)
    assert any(error.startswith("PROVENANCE_MISSING:") for error in result.errors)
    assert any(error.startswith("ORPHAN_HOSTED_IN:") for error in result.errors)


def test_runtime_non_archielement_is_rejected_before_attribute_access():
    result = validate_creation(project_id="P", candidate_elements=("not-an-element",), existing_canonical=())  # type: ignore[arg-type]
    assert not result.valid and result.errors == ("CANDIDATE_NOT_ARCHIELEMENT@0",)


def test_model_local_invariants_are_not_revalidated():
    item = element("a")
    result = validate_creation(project_id="P", candidate_elements=(item,), existing_canonical=())
    assert result.valid
