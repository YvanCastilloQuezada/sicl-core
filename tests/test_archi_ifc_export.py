import hashlib, ifcopenshell
from sicl.archi import *
def elements():
    w=ArchiElementId.compute('P','WALL','w'); o=ArchiElementId.compute('P','OPENING','o'); d=ArchiElementId.compute('P','DOOR','d')
    g=ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800)
    return (ArchiElement(w,'P',ElementKind.WALL,g), ArchiElement(o,'P',ElementKind.OPENING,g,contained_in=d), ArchiElement(d,'P',ElementKind.DOOR,g,hosted_in=w))
def test_ifc_mapping_relations_and_determinism(tmp_path):
    a=export_ifc(elements()); b=export_ifc(elements()); assert hashlib.sha256(a).hexdigest()==hashlib.sha256(b).hexdigest(); p=tmp_path/'x.ifc'; export_ifc(elements(),p); f=ifcopenshell.open(str(p)); assert len(f.by_type('IfcDoor'))==1 and len(f.by_type('IfcOpeningElement'))==1; assert len(f.by_type('IfcRelVoidsElement'))==1 and len(f.by_type('IfcRelFillsElement'))==1
