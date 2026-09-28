"""Deterministic minimal IFC export for D-2 architectural elements."""
from __future__ import annotations
from pathlib import Path
import ifcopenshell
from .identity import IfcGlobalId
from .model import ArchiElement, ElementKind, GeometryKind

_IFC_CLASS={ElementKind.SITE:"IfcSite",ElementKind.SPACE:"IfcSpace",ElementKind.WALL:"IfcWallStandardCase",ElementKind.SLAB:"IfcSlab",ElementKind.COLUMN:"IfcColumn",ElementKind.BEAM:"IfcBeam",ElementKind.OPENING:"IfcOpeningElement",ElementKind.DOOR:"IfcDoor",ElementKind.WINDOW:"IfcWindow"}
_IMPLEMENTED_GEOMETRY_KINDS=frozenset((GeometryKind.EXTRUDED_RECTANGLE,))

def export_ifc(elements: tuple[ArchiElement,...] | list[ArchiElement], path: str | Path | None = None) -> bytes:
    """Export supported geometry deterministically.

    ``path=None`` is a valid in-memory export. A supplied path is written
    after serialization; filesystem errors propagate so the transaction can
    fail closed. ``EXTRUDED_CIRCLE`` is declared for future use but is not
    implemented by this exporter and therefore raises explicitly.
    """
    unsupported = [e.geometry.kind.value for e in elements if e.geometry.kind not in _IMPLEMENTED_GEOMETRY_KINDS]
    if unsupported: raise ValueError(f"GEOMETRY_KIND_NOT_IMPLEMENTED:{unsupported[0]}")
    model=ifcopenshell.file(schema="IFC4")
    model.header.file_name.name="ARKI-D2.ifc"; model.header.file_name.time_stamp="1970-01-01T00:00:00"; model.header.file_name.author=["ARKI"]; model.header.file_name.organization=["ARKI"]; model.header.file_name.preprocessor_version="ARKI"; model.header.file_name.originating_system="ARKI"; model.header.file_name.authorization=""
    ordered=sorted(elements,key=lambda e:e.element_id.value)
    entities={}
    for e in ordered:
        cls=_IFC_CLASS[e.kind]; ent=model.create_entity(cls, GlobalId=IfcGlobalId.from_archi_id(e.element_id).value, Name=e.element_id.value)
        if hasattr(ent,"Description"): ent.Description=f"KIND={e.kind.value};GEOMETRY={e.geometry.kind.value};W={e.geometry.profile.width_mm};D={e.geometry.profile.depth_mm};H={e.geometry.height_mm}"
        entities[e.element_id]=ent
    # Use explicit IFC relationship entities for the required opening chain.
    for e in ordered:
        if e.kind not in (ElementKind.DOOR,ElementKind.WINDOW) or e.hosted_in is None: continue
        host=entities.get(e.hosted_in); filling=entities[e.element_id]
        opening_id=next((x.element_id for x in ordered if x.kind is ElementKind.OPENING and x.contained_in==e.element_id), None)
        opening=entities.get(opening_id) if opening_id else None
        if host is not None and opening is not None:
            model.create_entity("IfcRelVoidsElement", GlobalId=IfcGlobalId.from_archi_id(opening_id).value, RelatingBuildingElement=host, RelatedOpeningElement=opening)
            model.create_entity("IfcRelFillsElement", GlobalId=IfcGlobalId.from_archi_id(e.element_id).value, RelatingOpeningElement=opening, RelatedBuildingElement=filling)
    raw=model.to_string().encode()
    if path is not None: Path(path).write_bytes(raw)
    return raw

__all__=["export_ifc"]
