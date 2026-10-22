#!/usr/bin/env python3
"""Detect weekly master changes without adopting anything automatically."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data/master_registry/masters.json"
DEFAULT_LOG_DIR = ROOT / "data/master_registry/logs"
USER_AGENT = "ARKI-VSM/1.0 (+https://github.com/YvanCastilloQuezada/sicl-core)"


def get_json(url: str, timeout: int = 12) -> tuple[dict[str, Any] | None, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response), None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return None, str(exc)


def parse_version(value: str | None) -> tuple[int, ...]:
    if not value:
        return ()
    return tuple(int(part) for part in re.findall(r"\d+", str(value))[:6])


def latest_pypi(package: str) -> dict[str, Any]:
    package = package.strip()
    data, error = get_json(f"https://pypi.org/pypi/{urllib.parse.quote(package)}/json")
    if error or not data:
        return {"source": "pypi", "package": package, "status": "unavailable", "error": error or "empty response"}
    info = data.get("info", {})
    return {
        "source": "pypi", "package": package, "status": "ok",
        "version": info.get("version"), "released": data.get("releases", {}).get(info.get("version"), [{}])[0].get("upload_time"),
        "url": info.get("project_url") or f"https://pypi.org/project/{package}/",
        "summary": info.get("summary", "")[:180],
    }


def latest_github(repo: str) -> dict[str, Any]:
    repo = repo.strip()
    data, error = get_json(f"https://api.github.com/repos/{repo}/releases/latest")
    if error or not data or data.get("message") == "Not Found":
        # A repository may have no formal release; use its latest commit as availability evidence.
        commit, commit_error = get_json(f"https://api.github.com/repos/{repo}/commits?per_page=1")
        if commit and isinstance(commit, list) and commit:
            return {"source": "github", "repo": repo, "status": "commit_only", "version": None,
                    "released": commit[0].get("commit", {}).get("author", {}).get("date"),
                    "url": f"https://github.com/{repo}", "summary": "No latest release; latest default-branch commit observed."}
        return {"source": "github", "repo": repo, "status": "unavailable", "error": error or "repository unavailable"}
    return {"source": "github", "repo": repo, "status": "ok", "version": data.get("tag_name") or data.get("name"),
            "released": data.get("published_at"), "url": data.get("html_url") or f"https://github.com/{repo}/releases",
            "summary": (data.get("body") or "").strip().splitlines()[0][:180] if data.get("body") else "Release metadata available."}


def inspect_source(source: dict[str, Any]) -> dict[str, Any]:
    kind = source.get("type")
    if kind == "pip" and source.get("package"):
        return latest_pypi(str(source["package"]))
    if kind == "github" and source.get("repo"):
        return latest_github(str(source["repo"]))
    if kind == "npm" and source.get("package"):
        package = str(source["package"]).strip()
        data, error = get_json(f"https://registry.npmjs.org/{urllib.parse.quote(package)}/latest")
        return {"source": "npm", "package": package, "status": "ok", "version": data.get("version"), "url": f"https://www.npmjs.com/package/{package}"} if data else {"source":"npm","package":package,"status":"unavailable","error":error or "empty response"}
    return {"source": kind or "unknown", "status": "not_configured"}


def classify(master: dict[str, Any], observations: list[dict[str, Any]], as_of: str) -> tuple[str, str]:
    usable = [item for item in observations if item.get("version") or item.get("released")]
    if not master.get("fuentes_version"):
        return "not_configured", "No hay fuente pública de versión configurada."
    if not usable:
        return "unavailable", "No se pudo consultar una fuente pública."
    current = str(master.get("version_actual") or "")
    versions = [str(item["version"]) for item in usable if item.get("version")]
    if current and versions and current in versions:
        extras = [version for version in versions if version != current]
        suffix = f" Otras fuentes publican tags no equivalentes: {', '.join(extras)}; revisar manualmente." if extras else ""
        return "unchanged", f"La versión observada confirma la línea base {current}.{suffix}"
    if current and versions:
        return "changed", f"Versión registrada {current}; fuente observada: {', '.join(versions)}. Requiere evaluación manual."
    if not current and versions:
        return "baseline_candidate", f"Versión disponible {', '.join(versions)}; el registro aún no tiene línea base."
    if current and versions:
        return "unchanged", f"La versión observada coincide con la línea base {current}."
    return "observed_without_release", "Fuente consultable, pero sin release/version formal; no se adopta nada."


def render_report(registry: dict[str, Any], results: list[dict[str, Any]], as_of: str) -> str:
    groups: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        groups.setdefault(result["classification"], []).append(result)
    lines = [f"# VSM — Revisión semanal de maestros ({as_of})", "", "**Modo:** detección y reporte únicamente; no se actualizan paquetes, reglas ni runtime.", "", f"**Maestros registrados:** {len(results)}", ""]
    lines += ["## Resumen", "", "| Clasificación | Cantidad |", "|---|---:|"]
    labels = {"changed":"Cambios detectados", "unchanged":"Sin cambios", "baseline_candidate":"Candidatos a línea base", "unavailable":"No consultables", "not_configured":"Sin fuente configurada", "observed_without_release":"Observados sin release", "obsolescent":"Potencialmente obsoletos"}
    for key in ["changed","unchanged","baseline_candidate","unavailable","not_configured","observed_without_release","obsolescent"]:
        lines.append(f"| {labels[key]} | {len(groups.get(key, []))} |")
    lines += ["", "## Maestros con nueva versión o candidato a línea base", "", "| Maestro | Rama | Línea base | Observado | Acción VSM |", "|---|---|---|---|---|"]
    for result in groups.get("changed", []) + groups.get("baseline_candidate", []):
        lines.append(f"| {result['name']} | {', '.join(result['ramas'])} | {result['current'] or '—'} | {result['observed'] or '—'} | **No adoptar automáticamente; evaluar ground truth** |")
    lines += ["", "## Maestros sin cambios", ""]
    for result in groups.get("unchanged", []):
        lines.append(f"- **{result['name']}** ({', '.join(result['ramas'])}): {result['detail']}")
    lines += ["", "## Maestros no consultables o sin fuente", ""]
    for key in ["unavailable", "not_configured", "observed_without_release"]:
        for result in groups.get(key, []):
            lines.append(f"- **{result['name']}**: `{key}` — {result['detail']}")
    lines += ["", "## Maestros nuevos detectados", "", "No se realizó una búsqueda automática de tendencias como absorción. Las propuestas nuevas requieren una revisión de rama y fixture antes de agregarse al registro.", "", "## Obsolescencia", "", "La detección de obsolescencia se basa en la fecha de release observada; no se marcó ningún maestro como obsoleto sin evidencia suficiente.", "", "## Evidencia por maestro", "", "| ID | Estado registrado | Clasificación | Fuentes consultadas | Evidencia |", "|---|---|---|---|---|"]
    for result in results:
        sources = "; ".join(item.get("url", item.get("source", "")) for item in result["observations"])
        lines.append(f"| `{result['id']}` | `{result['estado']}` | `{result['classification']}` | {sources or '—'} | {result['detail']} |")
    lines += ["", "## Invariantes", "", "```text", "AUTO_ABSORPTION = FORBIDDEN", "AUTO_UPDATE = FORBIDDEN", "CORE_CHANGED = NO", "DECISION_CREATED = NO", "NAMESPACE_MIXED = NO", "```", ""]
    return "\n".join(lines)


def run(registry_path: Path, output_dir: Path, as_of: str, offline: bool = False) -> Path:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    for master in registry.get("masters", []):
        observations = [{"source": "offline", "status": "skipped"}] if offline else [inspect_source(source) for source in master.get("fuentes_version", [])]
        classification, detail = ("offline", "Network disabled; no version claims made.") if offline else classify(master, observations, as_of)
        versions = [str(item["version"]) for item in observations if item.get("version")]
        results.append({"id": master["id"], "name": master["name"], "ramas": master.get("ramas", []), "estado": master.get("estado"), "current": master.get("version_actual"), "observed": ", ".join(versions), "classification": classification, "detail": detail, "observations": observations})
    report = render_report(registry, results, as_of)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{as_of}_weekly_review.md"
    path.write_text(report, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--offline", action="store_true", help="Generate a no-network report without version claims")
    args = parser.parse_args()
    try:
        path = run(args.registry, args.output_dir, args.date, args.offline)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"VSM error: {exc}", file=sys.stderr)
        return 2
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
