#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from sicl.drawing import load_rule_set, validate_rule_set, create_synthetic_ifc, validate_ifc, import_ifc_snapshot, compose_drawing_set, export_drawing_set

def main():
 p=argparse.ArgumentParser(prog="/DRAWING"); p.add_argument("command",nargs="+"); p.add_argument("--scale",default="1:50"); p.add_argument("--lod",type=int,default=300); p.add_argument("--mode",default="SINGLE_VIEW_PER_SHEET"); p.add_argument("--out",default="drawing.pdf"); a=p.parse_args(); cmd=[x.upper() for x in a.command]
 if cmd[:2]==["RULE-SET","LOAD"]:
  r=load_rule_set(a.command[2],a.scale,a.lod); print(json.dumps(r.to_dict(),indent=2)); return
 if cmd[:2]==["RULE-SET","SHOW"]: print("RULE SET",a.command[2]); return
 if cmd[:2]==["IFC","IMPORT"]:
  s=import_ifc_snapshot(a.command[2],a.command[3]); print(json.dumps(s.to_dict(),indent=2)); return
 if cmd[:2]==["IFC","VALIDATE"]: print(json.dumps({"valid":validate_ifc(a.command[2])[0],"errors":validate_ifc(a.command[2])[1]})); return
 if cmd[0]=="GENERATE":
  path=create_synthetic_ifc(); s=import_ifc_snapshot(a.command[1],path); ds=compose_drawing_set(a.command[1],s,a.mode); export_drawing_set(ds,a.out); print(json.dumps(ds.to_dict(),indent=2)); return
 p.error("unsupported /DRAWING command")
if __name__=="__main__": main()
