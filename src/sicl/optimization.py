from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .domain import Objective
from .v11 import Alternative, Evaluation


@dataclass(frozen=True)
class ParetoResult:
    non_dominated: list[str]
    dominated: dict[str, str]
    incomplete: list[str]


def _dominates(values_a: list[float], values_b: list[float], directions: list[str]) -> bool:
    no_worse = all(
        a >= b if direction == "MAXIMIZE" else a <= b
        for a, b, direction in zip(values_a, values_b, directions)
    )
    strictly_better = any(
        a > b if direction == "MAXIMIZE" else a < b
        for a, b, direction in zip(values_a, values_b, directions)
    )
    return no_worse and strictly_better


def pareto_front(alternatives: Iterable[Alternative], evaluations: Iterable[Evaluation], objectives: list[Objective]) -> ParetoResult:
    alternatives = list(alternatives)
    evaluation_map = {(item.alternative_id, item.objective_id): item.value for item in evaluations}
    vectors: dict[str, list[float]] = {}
    incomplete: list[str] = []
    for alternative in alternatives:
        vector = [evaluation_map.get((alternative.alternative_id, objective.objective_id)) for objective in objectives]
        if any(value is None for value in vector):
            incomplete.append(alternative.alternative_id)
        else:
            vectors[alternative.alternative_id] = [float(value) for value in vector]
    non_dominated: list[str] = []
    dominated: dict[str, str] = {}
    directions = [objective.direction for objective in objectives]
    for alternative_id, vector in vectors.items():
        dominator = next(
            (other_id for other_id, other_vector in vectors.items() if other_id != alternative_id and _dominates(other_vector, vector, directions)),
            None,
        )
        if dominator:
            dominated[alternative_id] = dominator
        else:
            non_dominated.append(alternative_id)
    return ParetoResult(non_dominated, dominated, incomplete)
