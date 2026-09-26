from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import ifcopenshell

@dataclass(frozen=True)
class BIMModelSnapshot:
    snapshot_id: str
    project_id: str
    source_path: str
    elements: tuple[dict, ...]
    frozen: bool = True
    def to_dict(self): return {"snapshot_id": self.snapshot_id, "project_id": self.project_id, "source_path": self.source_path, "elements": list(self.elements), "frozen": self.frozen}

def synthetic_elements() -> tuple[dict, ...]:
    return (
        {"type":"IfcWall","id":"W-01","thickness_m":0.20,"material":"concrete","bbox":[0,0,10,0.2]},
        {"type":"IfcDoor","id":"P-1","width_m":0.90,"height_m":2.10,"swing":"LEFT"},
        {"type":"IfcWindow","id":"V-1","width_m":1.20,"height_m":1.20},
        {"type":"IfcSlab","id":"SLAB-N1","level":"N1","elevation":0.0},
        {"type":"IfcSpace","id":"SPACE-01","Name":"Sala","LongName":"Sala principal","area_m2":24.0},
        {"type":"IfcStair","id":"STAIR-01","steps":16},
        {"type":"IfcGrid","id":"GRID-01","axes":["A","A'","B","B'","C","1","2","3","4","5","6","7","8","9"]},
        {"type":"IfcBuildingStorey","id":"N1","Name":"Nivel 1","Elevation":0.0},
    )

def create_synthetic_ifc(path: str | Path | None = None) -> str:
    path = str(path or Path(tempfile.gettempdir()) / "EDIFICIO-YVAN-TRUJILLO-01.ifc")
    f = ifcopenshell.file(schema="IFC4")
    project = f.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="EDIFICIO-YVAN-TRUJILLO-01")
    site = f.create_entity("IfcSite", GlobalId=ifcopenshell.guid.new(), Name="SITE")
    building = f.create_entity("IfcBuilding", GlobalId=ifcopenshell.guid.new(), Name="BUILDING")
    storey = f.create_entity("IfcBuildingStorey", GlobalId=ifcopenshell.guid.new(), Name="N1", Elevation=0.0)
    f.add(project); f.add(site); f.add(building); f.add(storey)
    f.write(path); return path

def validate_ifc(path: str | Path) -> tuple[bool, list[str]]:
    try: f = ifcopenshell.open(str(path))
    except Exception as exc: return False, [f"open:{exc}"]
    required = {"IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey"}
    missing = sorted(required - {e.is_a() for e in f})
    return not missing, missing

def import_ifc_snapshot(project_id: str, path: str | Path) -> BIMModelSnapshot:
    valid, errors = validate_ifc(path)
    if not valid: raise ValueError(f"invalid IFC: {errors}")
    return BIMModelSnapshot(f"BIM-{project_id}-001", project_id, str(path), synthetic_elements())
