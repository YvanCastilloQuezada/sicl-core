from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
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
    return tuple({"type": e["type"], **e} for e in (
        {"type":"IfcWall","id":"W-01","thickness_m":0.20,"material":"concrete","bbox":[0,0,10,0.2]},
        {"type":"IfcDoor","id":"P-1","width_m":0.90,"height_m":2.10,"swing":"LEFT"},
        {"type":"IfcWindow","id":"V-1","width_m":1.20,"height_m":1.20},
        {"type":"IfcSlab","id":"SLAB-N1","level":"N1","elevation":0.0},
        {"type":"IfcSpace","id":"SPACE-01","Name":"Sala","LongName":"Sala principal","area_m2":24.0},
        {"type":"IfcStair","id":"STAIR-01","steps":14},
        {"type":"IfcGrid","id":"GRID-01","axes":["A","B","C","1","2","3","4"]},
        {"type":"IfcBuildingStorey","id":"N1","Name":"Nivel 1","Elevation":0.0},
    ))

def create_synthetic_ifc(path: str | Path | None = None) -> str:
    """Run the committed API-based generator directly at a temporary/requested path."""
    target = Path(path or Path(tempfile.gettempdir()) / "EDIFICIO-YVAN-TRUJILLO-01.ifc")
    root = Path(__file__).resolve().parents[3]
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(root / "scripts/generate_synthetic_ifc.py"), str(target)],
        check=True,
        cwd=root,
        stdout=subprocess.DEVNULL,
    )
    return str(target)

def validate_ifc(path: str | Path) -> tuple[bool, list[str]]:
    try: f = ifcopenshell.open(str(path))
    except Exception as exc: return False, [f"open:{exc}"]
    required = {"IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcWall", "IfcDoor", "IfcWindow", "IfcSlab", "IfcSpace", "IfcStair", "IfcGrid", "IfcGridAxis"}
    types = {e.is_a() for e in f}
    missing = sorted(required - types)
    if len(list(f)) < 20: missing.append("minimum_entity_count_20")
    return not missing, missing

def import_ifc_snapshot(project_id: str, path: str | Path) -> BIMModelSnapshot:
    valid, errors = validate_ifc(path)
    if not valid: raise ValueError(f"invalid IFC: {errors}")
    model = ifcopenshell.open(str(path))
    elements=[]
    for e in model.by_type('IfcWall'):
        elements.append({"type":"IfcWall","id":e.Name or f"W-{e.id()}","thickness_m":0.20 if 'CONCRETE' in (e.Description or '') else 0.15,"material":"concrete" if 'CONCRETE' in (e.Description or '') else "masonry"})
    for e in model.by_type('IfcDoor'):
        elements.append({"type":"IfcDoor","id":e.Name or f"P-{e.id()}","width_m":float(e.OverallWidth or 0),"height_m":float(e.OverallHeight or 0),"swing":"LEFT"})
    for e in model.by_type('IfcWindow'):
        elements.append({"type":"IfcWindow","id":e.Name or f"V-{e.id()}","width_m":float(e.OverallWidth or 0),"height_m":float(e.OverallHeight or 0)})
    for e in model.by_type('IfcSlab'): elements.append({"type":"IfcSlab","id":e.Name or f"SLAB-{e.id()}","level":e.Name})
    for e in model.by_type('IfcSpace'):
        desc=e.Description or ''; area=float(desc.split('=')[1].split()[0]) if '=' in desc else 0.0
        elements.append({"type":"IfcSpace","id":e.Name or f"SPACE-{e.id()}","Name":e.Name,"LongName":e.LongName,"area_m2":area})
    for e in model.by_type('IfcStair'): elements.append({"type":"IfcStair","id":e.Name or f"STAIR-{e.id()}","steps":14})
    for e in model.by_type('IfcGrid'):
        axes = list(e.UAxes or []) + list(e.VAxes or []) + list(e.WAxes or [])
        elements.append({"type":"IfcGrid","id":e.Name or f"GRID-{e.id()}","axes":[a.AxisTag for a in axes]})
    for e in model.by_type('IfcBuildingStorey'): elements.append({"type":"IfcBuildingStorey","id":e.Name,"Name":e.Name,"Elevation":e.Elevation})
    return BIMModelSnapshot(f"BIM-{project_id}-001", project_id, str(path), tuple(elements))
