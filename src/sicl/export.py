from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .domain import Project
from .repository import SQLiteRepository


def project_payload(repo: SQLiteRepository, project: Project) -> dict[str, Any]:
    payload = asdict(project)
    payload["events"] = [asdict(event) for event in repo.events(project.project_id)]
    return payload


def export_project_json(repo: SQLiteRepository, project: Project, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(project_payload(repo, project), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return target


def export_csv(repo: SQLiteRepository, project: Project, directory: str | Path) -> list[Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    rows_by_kind = {
        "objectives": [asdict(item) for item in project.objectives.values()],
        "constraints": [asdict(item) for item in project.constraints.values()],
        "alternatives": [asdict(item) for item in project.alternatives.values()],
        "evaluations": [asdict(item) for item in project.evaluations.values()],
    }
    for kind, rows in rows_by_kind.items():
        target = directory / f"{project.project_id}_{kind}.csv"
        keys = sorted({key for row in rows for key in row})
        with target.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys or ["id"])
            writer.writeheader()
            writer.writerows(rows)
        outputs.append(target)
    return outputs


def report_text(repo: SQLiteRepository, project: Project) -> str:
    events = repo.events(project.project_id)
    lines = [
        "=" * 64,
        f"SICL PROJECT REPORT — {project.project_id}",
        "=" * 64,
        f"Name: {project.name}",
        f"Stage: {project.stage}",
        f"Objectives: {len(project.objectives)}",
        f"Constraints: {len(project.constraints)}",
        f"Roles: {len(project.roles)}",
        f"Facts: {len(project.facts)} | Assumptions: {len(project.assumptions)}",
        f"Alternatives: {len(project.alternatives)}",
        f"Evaluations: {len(project.evaluations)}",
        f"Comparisons: {len(project.comparisons)}",
        f"Recommendations: {len(project.recommendations)}",
        f"Decisions: {len(project.decisions)}",
        f"Events: {len(events)}",
        "",
        "OBJECTIVES",
    ]
    lines.extend(f"- {item.key}: {item.direction} {item.value}" for item in project.objectives.values())
    lines.extend(["", "CONSTRAINTS"])
    lines.extend(f"- {item.key} {item.operator} {item.value} {item.unit}" for item in project.constraints.values())
    lines.extend(["", "RECOMMENDATIONS"])
    lines.extend(f"- {item.recommended_alternative_id}: {item.status} — {item.reason}" for item in project.recommendations.values())
    lines.extend(["", "DECISIONS"])
    lines.extend(f"- {item.statement} ({item.actor}, {item.authority})" for item in project.decisions.values())
    return "\n".join(lines) + "\n"


def export_report(repo: SQLiteRepository, project: Project, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report_text(repo, project), encoding="utf-8")
    return target


def tradeoffs_text(project: Project) -> str:
    lines = ["=" * 64, "SICL TRADE-OFFS", "=" * 64]
    if not project.comparisons:
        return "\n".join(lines + ["No comparisons available."]) + "\n"
    for comparison in project.comparisons.values():
        names = {alternative.alternative_id: alternative.name for alternative in project.alternatives.values()}
        labels = [names.get(alternative_id, alternative_id) for alternative_id in comparison.alternative_ids]
        lines.append(f"Comparison {comparison.comparison_id}: {', '.join(labels)}")
        scores: dict[str, list[float]] = {aid: [] for aid in comparison.alternative_ids}
        for evaluation in comparison.evaluations:
            scores.setdefault(evaluation.alternative_id, []).append(evaluation.value)
        for alternative_id, values in scores.items():
            score = sum(values) / len(values) if values else 0.0
            lines.append(f"- {names.get(alternative_id, alternative_id)}: score={score:.2f} evaluations={len(values)}")
    return "\n".join(lines) + "\n"


def dashboard_text(repo: SQLiteRepository, project: Project) -> str:
    events = repo.events(project.project_id)
    completed = sum(bool(value) for value in (project.objectives, project.constraints, project.alternatives, project.evaluations, project.comparisons))
    percent = completed * 20
    bar = "#" * (percent // 10) + "." * (10 - percent // 10)
    return "\n".join([
        "SICL DASHBOARD",
        f"[{bar}] {percent}%",
        f"Project: {project.project_id} | Stage: {project.stage}",
        f"Objectives={len(project.objectives)} Constraints={len(project.constraints)} Alternatives={len(project.alternatives)}",
        f"Evaluations={len(project.evaluations)} Comparisons={len(project.comparisons)} Recommendations={len(project.recommendations)}",
        f"Events={len(events)} | Last events: {', '.join(event.type for event in events[-5:])}",
    ]) + "\n"
