from __future__ import annotations
from .drawing_rules import load_rule_set
from .ifc_synthetic import create_synthetic_ifc, import_ifc_snapshot, validate_ifc
from .composer import compose_drawing_set
from .pdf_export import export_drawing_set

class DrawingHttpService:
    """Boundary HTTP independiente; no se registra en api/main.py para preservar el Core."""
    def __init__(self): self.sets = {}; self.snapshots = {}
    def handle(self, method: str, path: str, payload: dict | None = None):
        parts=[p for p in path.split('?')[0].split('/') if p]; body=payload or {}
        if method=='GET' and path.rstrip('/')=='/v1/drawing/rule-sets': return 200, [load_rule_set('data/drawing_rules/iso128_nte_peru.json').to_dict()]
        if len(parts)>=4 and parts[:3]==['v1','projects',parts[2]] and parts[3]=='drawings':
            project_id=parts[2]
            if method=='POST' and len(parts)==5 and parts[4]=='ifc-import':
                path_ifc=body.get('path') or create_synthetic_ifc(); snap=import_ifc_snapshot(project_id,path_ifc); self.snapshots[snap.snapshot_id]=snap; return 201,snap.to_dict()
            if method=='POST' and len(parts)==5 and parts[4]=='ifc-validate': return 200,dict(zip(('valid','errors'),validate_ifc(body['path'])))
            if method=='POST' and len(parts)==5 and parts[4]=='generate':
                snap=self.snapshots[body['bim_snapshot_id']]; ds=compose_drawing_set(project_id,snap,body.get('layout','SINGLE_VIEW_PER_SHEET')); self.sets[ds.drawing_set_id]=ds; return 201,ds.to_dict()
            if method=='GET' and len(parts)==6 and parts[4]=='sets': return 200,self.sets.get(parts[5]).to_dict()
        return 404,{"error":"route not found"}
