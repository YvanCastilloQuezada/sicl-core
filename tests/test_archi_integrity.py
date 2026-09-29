from dataclasses import replace

import pytest

from sicl.archi.identity import ArchiElementId
from sicl.archi.integrity import ReferentialIntegrityError, validate_references
from sicl.archi.model import ArchiElement, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec


def element(nonce: str, *, kind=ElementKind.SPACE, hosted_in=None, contained_in=None):
    eid=ArchiElementId.compute("P",kind.value,nonce)
    geometry=ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800)
    return ArchiElement(eid,"P",kind,geometry,hosted_in=hosted_in,contained_in=contained_in)


def test_valid_references_return_empty_tuple():
    wall=element("wall",kind=ElementKind.WALL)
    door=element("door",kind=ElementKind.DOOR,hosted_in=wall.element_id)
    assert validate_references((wall,door)) == ()


def test_orphan_hosted_in_detected():
    missing=ArchiElementId.compute("P","WALL","missing")
    door=element("door",kind=ElementKind.DOOR,hosted_in=missing)
    assert validate_references((door,))[0].startswith("ORPHAN_HOSTED_IN:")


def test_orphan_contained_in_detected():
    missing=ArchiElementId.compute("P","DOOR","missing")
    opening=element("opening",kind=ElementKind.OPENING,contained_in=missing)
    assert validate_references((opening,))[0].startswith("ORPHAN_CONTAINED_IN:")


def test_self_hosted_in_detected():
    door=element("door",kind=ElementKind.DOOR)
    door=replace(door,hosted_in=door.element_id)
    assert validate_references((door,))[0].startswith("SELF_HOSTED_IN:")


def test_self_contained_in_detected():
    opening=element("opening",kind=ElementKind.OPENING)
    opening=replace(opening,contained_in=opening.element_id)
    assert validate_references((opening,))[0].startswith("SELF_CONTAINED_IN:")


def test_known_ids_none_is_derived_from_elements():
    wall=element("wall",kind=ElementKind.WALL)
    door=element("door",kind=ElementKind.DOOR,hosted_in=wall.element_id)
    assert validate_references((wall,door),known_ids=None) == ()


def test_multiple_errors_are_reported():
    missing=ArchiElementId.compute("P","WALL","missing")
    a=element("a",kind=ElementKind.DOOR,hosted_in=missing)
    b=element("b",kind=ElementKind.OPENING,contained_in=missing)
    errors=validate_references((a,b))
    assert len(errors)==2
    assert errors[0].startswith("ORPHAN_HOSTED_IN:")
    assert errors[1].startswith("ORPHAN_CONTAINED_IN:")


def test_external_known_id_is_valid_target():
    external=ArchiElementId.compute("P","SITE","existing")
    item=element("space",contained_in=external)
    assert validate_references((item,),known_ids={item.element_id,external}) == ()


def test_referential_integrity_error_is_value_error():
    assert issubclass(ReferentialIntegrityError,ValueError)
