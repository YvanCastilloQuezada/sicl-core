#!/usr/bin/env python3
"""ARKI Mapa Vivo V1: observador determinista, sin mutaciones canónicas."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PHASES = [f"F{i}" for i in range(1, 11)]
REQUIRED = [
    ("ACE88", "Autorización humana D2", "docs/ace88/ACE88_ROOT_INTEGRATION.md", ["F8"]),
    ("AUTO_V0", "Contrato de automejora", "docs/arki-automejora/ARKI_AUTONOMOUS_IMPROVEMENT_CONTRACT_V0.md", ["F8"]),
    ("INVENTORY", "Inventario de solo lectura", "tools/arki_automejora_inventario.py", ["AUTO_V0"]),
    ("START", "Continuidad 00-start", "00-start.md", ["INVENTORY"]),
]
def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=15)
    return p.stdout.strip() if p.returncode == 0 else None

def build(root):
    head = git(root, "rev-parse", "HEAD")
    if head is None:
        raise SystemExit("BLOCKED: no es un repositorio Git accesible")
    tracked = set((git(root, "ls-files") or "").splitlines())
    nodes = []
    for i, phase in enumerate(PHASES):
        nodes.append(dict(id=phase, kind="phase", label=phase,
            dependencies=([PHASES[i-1]] if i else []),
            evidence=[], status="UNKNOWN", approval="NOT_ASSESSED",
            note="La existencia de la fase no demuestra cumplimiento"))
    for ident, label, path, deps in REQUIRED:
        exists = path in tracked and (root / path).is_file()
        sha = hashlib.sha256((root/path).read_bytes()).hexdigest() if exists else None
        nodes.append(dict(id=ident, kind="evidence", label=label,
            dependencies=deps, evidence=([dict(path=path, sha256=sha)] if exists else []),
            status=("SOURCE_PRESENT_NOT_VALIDATED" if exists else "MISSING"),
            approval="NOT_ASSESSED"))
    index = {n["id"]: n for n in nodes}
    edges = [{"from":dep, "to":n["id"], "kind":"prerequisite"}
             for n in nodes for dep in n["dependencies"]]
    # Structural cycles and dangling edges are safety findings, not silent fixes.
    dangling = [e for e in edges if e["from"] not in index]
    colors = {"UNKNOWN":"red", "MISSING":"red",
              "SOURCE_PRESENT_NOT_VALIDATED":"violet"}
    for n in nodes:
        n["visual_color"] = colors.get(n["status"], "red")
    return dict(schema="arki.mapa_vivo.v1", generated_at=datetime.now(timezone.utc).isoformat(),
        repository=str(root), head=head, canonical_mutations=0,
        validation_scope="source-presence-only", nodes=nodes, edges=edges,
        findings=[{"code":"DANGLING_DEPENDENCY","edge":e} for e in dangling],
        limitations=[
            "F1-F10 se mantienen UNKNOWN hasta obtener evidencia de pruebas por fase",
            "Los vínculos F1-F10 son precedencias provisionales para visualización, no contratos canónicos",
            "SOURCE_PRESENT_NOT_VALIDATED no equivale a PASS ni FROZEN",
            "No ejecuta normas, AGK, gemelo predictivo, aprendizaje ni autocorrección",
            "No escribe en SQLite ni en el estado canónico del proyecto"])
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--output",default=None)
    a=p.parse_args()
    root=Path(a.root).resolve()
    obj=build(root)
    data=json.dumps(obj,ensure_ascii=False,indent=2)+"\n"
    if a.output:
        out=Path(a.output).resolve()
        if root==out or root in out.parents:
            raise SystemExit("BLOCKED: salida debe estar fuera del repositorio")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(data,encoding="utf-8")
        print(f"MAPA_VIVO_OUTPUT={out}")
    else:
        print(data,end="")
    print("MAPA_VIVO_READ_ONLY=YES",file=__import__("sys").stderr)
if __name__=="__main__":
    main()
