from dataclasses import replace
import pytest
from sicl.archi import *

def wall():
    return ArchiElement(ArchiElementId.compute('P','WALL','W-01'),'P',ElementKind.WALL,ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800),{'name':'W-01'}, {'source':'x'})

def test_content_hash_semantics():
    w=wall(); assert w.content_hash()==replace(w).content_hash(); assert w.content_hash()!=replace(w, geometry=replace(w.geometry,x_mm=100)).content_hash(); assert w.content_hash()!=replace(w, properties={'name':'W-02'}).content_hash(); assert w.content_hash()==replace(w, provenance={'source':'y'}).content_hash()

def test_hosting_containment_exclusive():
    a=ArchiElementId.compute('P','WALL','a'); b=ArchiElementId.compute('P','SPACE','b')
    with pytest.raises(ValueError): ArchiElement(ArchiElementId.compute('P','DOOR','d'),'P',ElementKind.DOOR,wall().geometry,hosted_in=a,contained_in=b)
