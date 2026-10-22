import hashlib, ifcopenshell, pytest
from sicl.archi import *
def elements():
    w=ArchiElementId.compute('P','WALL','w'); o=ArchiElementId.compute('P','OPENING','o'); d=ArchiElementId.compute('P','DOOR','d')
    g=ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800)
    return (ArchiElement(w,'P',ElementKind.WALL,g), ArchiElement(o,'P',ElementKind.OPENING,g,contained_in=d), ArchiElement(d,'P',ElementKind.DOOR,g,hosted_in=w))
def test_ifc_mapping_relations_and_determinism(tmp_path):
    a=export_ifc(elements()); b=export_ifc(elements()); assert hashlib.sha256(a).hexdigest()==hashlib.sha256(b).hexdigest(); p=tmp_path/'x.ifc'; export_ifc(elements(),p); f=ifcopenshell.open(str(p)); assert len(f.by_type('IfcDoor'))==1 and len(f.by_type('IfcOpeningElement'))==1; assert len(f.by_type('IfcRelVoidsElement'))==1 and len(f.by_type('IfcRelFillsElement'))==1

def test_ifc_none_path_is_in_memory_and_invalid_path_fails_closed(tmp_path):
    assert export_ifc(elements(), None)
    with pytest.raises(FileNotFoundError): export_ifc(elements(), tmp_path/'missing'/'x.ifc')

def test_declared_circle_geometry_is_not_silently_exported():
    w=ArchiElementId.compute('P','WALL','circle')
    circle=ArchiElement(w,'P',ElementKind.WALL,ArchiGeometry(GeometryKind.EXTRUDED_CIRCLE,ProfileSpec(200,200,100),height_mm=2800))
    with pytest.raises(ValueError, match='GEOMETRY_KIND_NOT_IMPLEMENTED'):
        export_ifc((circle,))

from sicl.archi.integrity import ReferentialIntegrityError


def test_ifc_export_rejects_orphan_reference():
    missing=ArchiElementId.compute('P','WALL','missing-host')
    d=ArchiElementId.compute('P','DOOR','orphan-door')
    g=ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800)
    door=ArchiElement(d,'P',ElementKind.DOOR,g,hosted_in=missing)
    with pytest.raises(ReferentialIntegrityError,match='IFC_EXPORT_REFERENTIAL_INTEGRITY_VIOLATION'):
        export_ifc((door,))


def test_ifc_export_valid_references_remain_supported():
    assert export_ifc(elements())

