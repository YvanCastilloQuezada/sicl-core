"""Canonical deterministic evaluation dataset for the UPAO-001 spatial pilot.

This module is intentionally an adapter over the existing S2 spatial generator
and the existing Objective/Evaluation/Pareto models. It does not persist data,
create decisions, or synchronize the Web spatial viewer.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Iterable, Mapping

from .domain import Objective
from .optimization import ParetoResult, pareto_front
from .spatial import SpatialRepresentation
from .spatial_generator import UPAO001SpatialGenerator
from .v11 import Alternative, Evaluation

UPAO001_PROJECT_ID = "UPAO-001"
GROSS_MASSING_AREA = "GROSS_MASSING_AREA"
OPEN_SITE_AREA = "OPEN_SITE_AREA"
OBJECTIVE_DIRECTION = "MAXIMIZE"
AREA_UNIT = "m²"
# Evaluation.source is the existing canonical provenance field. The model has
# no SYNTHETIC/DETERMINISTIC_DERIVED enum; SIMULATION is the closest value.
EVALUATION_SOURCE = "SIMULATION"
PROVENANCE = ("SYNTHETIC", "DETERMINISTIC_DERIVED", "EDUCATIONAL")


class SpatialEvaluationIncomplete(ValueError):
    """Raised when an authorized metric cannot be derived without substitution."""


@dataclass(frozen=True)
class SpatialEvaluationDataset:
    objectives: tuple[Objective, ...]
    evaluations: tuple[Evaluation, ...]
    metrics: Mapping[str, Mapping[str, float]]
    pareto: ParetoResult
    provenance: tuple[str, ...] = PROVENANCE
    decision_created: bool = False
    recommendation_created: bool = False
    human_review_created: bool = False


def _finite_number(metrics: Mapping[str, object], key: str) -> float | None:
    value = metrics.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    return numeric if math.isfinite(numeric) else None


def open_site_area(metrics: Mapping[str, object]) -> float | None:
    """Derive OPEN_SITE_AREA, returning None for incomplete/invalid inputs."""
    site_area = _finite_number(metrics, "site_area")
    footprint_area = _finite_number(metrics, "footprint_area")
    if site_area is None or footprint_area is None:
        return None
    value = site_area - footprint_area
    if value < 0:
        return None
    return value


def spatial_metrics(representation: SpatialRepresentation, generator: UPAO001SpatialGenerator | None = None) -> dict[str, float]:
    """Return the existing S2 metrics plus the authorized OPEN_SITE_AREA."""
    active_generator = generator or UPAO001SpatialGenerator()
    raw = active_generator.metrics(representation)
    required = ("site_area", "footprint_area", "gross_massing_area")
    if any(_finite_number(raw, key) is None for key in required):
        raise SpatialEvaluationIncomplete(
            f"incomplete S2 metrics for {representation.alternative_id}"
        )
    derived_open = open_site_area(raw)
    if derived_open is None:
        raise SpatialEvaluationIncomplete(
            f"OPEN_SITE_AREA incomplete for {representation.alternative_id}"
        )
    return {
        "site_area": float(raw["site_area"]),
        "footprint_area": float(raw["footprint_area"]),
        "gross_massing_area": float(raw["gross_massing_area"]),
        "open_site_area": float(derived_open),
    }


def canonical_objectives(project_id: str = UPAO001_PROJECT_ID) -> tuple[Objective, Objective]:
    return (
        Objective("OBJ-GROSS-MASSING-AREA", project_id, GROSS_MASSING_AREA, OBJECTIVE_DIRECTION, AREA_UNIT),
        Objective("OBJ-OPEN-SITE-AREA", project_id, OPEN_SITE_AREA, OBJECTIVE_DIRECTION, AREA_UNIT),
    )


def _evaluation_id(alternative_id: str, objective_id: str, representation: SpatialRepresentation) -> str:
    payload = json.dumps(
        {
            "alternative_id": alternative_id,
            "objective_id": objective_id,
            "input_fingerprint": representation.input_fingerprint,
            "generator_version": representation.generator_version,
            "representation_version": representation.representation_version,
            "seed": representation.seed,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return "EVAL-SPATIAL-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def canonical_evaluations(
    representations: Iterable[SpatialRepresentation],
    objectives: tuple[Objective, Objective] | None = None,
) -> tuple[tuple[Evaluation, ...], dict[str, dict[str, float]]]:
    """Build exactly six deterministic evaluations for valid UPAO A/B/C data."""
    ordered = tuple(representations)
    expected = ("UPAO-001-A", "UPAO-001-B", "UPAO-001-C")
    if tuple(item.alternative_id for item in ordered) != expected:
        raise ValueError("representations must be ordered as canonical UPAO-001-A/B/C")
    if len({item.alternative_id for item in ordered}) != 3:
        raise ValueError("canonical alternative IDs must be unique")
    active_objectives = objectives or canonical_objectives()
    if tuple(item.key for item in active_objectives) != (GROSS_MASSING_AREA, OPEN_SITE_AREA):
        raise ValueError("S6-P0.1 requires exactly the two authorized objectives")

    all_metrics: dict[str, dict[str, float]] = {}
    values: list[Evaluation] = []
    for representation in ordered:
        metrics = spatial_metrics(representation)
        all_metrics[representation.alternative_id] = metrics
        by_key = {
            GROSS_MASSING_AREA: metrics["gross_massing_area"],
            OPEN_SITE_AREA: metrics["open_site_area"],
        }
        for objective in active_objectives:
            values.append(
                Evaluation(
                    _evaluation_id(representation.alternative_id, objective.objective_id, representation),
                    representation.alternative_id,
                    objective.objective_id,
                    by_key[objective.key],
                    AREA_UNIT,
                    1.0,
                    EVALUATION_SOURCE,
                )
            )
    if len(values) != 6:
        raise AssertionError("S6-P0.1 must produce exactly six evaluations")
    return tuple(values), all_metrics


def build_upao001_dataset(
    representations: Iterable[SpatialRepresentation],
) -> SpatialEvaluationDataset:
    objectives = canonical_objectives()
    evaluations, metrics = canonical_evaluations(representations, objectives)
    alternatives = tuple(
        Alternative(item.alternative_id, UPAO001_PROJECT_ID, item.alternative_id)
        for item in representations
    )
    result = pareto_front(alternatives, evaluations, list(objectives))
    return SpatialEvaluationDataset(objectives, evaluations, metrics, result)


__all__ = [
    "AREA_UNIT",
    "EVALUATION_SOURCE",
    "GROSS_MASSING_AREA",
    "OPEN_SITE_AREA",
    "PROVENANCE",
    "SpatialEvaluationDataset",
    "SpatialEvaluationIncomplete",
    "build_upao001_dataset",
    "canonical_evaluations",
    "canonical_objectives",
    "open_site_area",
    "spatial_metrics",
]
