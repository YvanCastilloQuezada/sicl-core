from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from typing import Iterable

from .domain import Objective
from .v11 import Alternative, Evaluation


@dataclass(frozen=True)
class ParetoResult:
    non_dominated: list[str]
    dominated: dict[str, str]
    incomplete: list[str]


class GenerativeOptimizer:
    """Deterministic proposal generator; it never creates decisions."""

    source = "GENERATIVE_OPTIMIZER"

    def generate(self, alternative: Alternative, evaluations: Iterable[Evaluation]) -> list[Alternative]:
        evaluations = list(evaluations)
        proposals: list[Alternative] = []
        over_budget = any(item.value < 0 and item.source == "EXPERT_SYSTEM" for item in evaluations)
        poor_energy = any(0 <= item.value < 70 and item.source == "EXPERT_SYSTEM" for item in evaluations)
        if over_budget:
            parameters = dict(alternative.parameters)
            floors = float(parameters.get("FLOORS", 0))
            if floors > 1:
                parameters["FLOORS"] = str(int(floors - 1))
            elif "AREA" in parameters:
                parameters["AREA"] = str(round(float(parameters["AREA"]) * 0.9, 2))
            proposals.append(Alternative(f"ALT-{uuid4().hex[:10]}", alternative.project_id, f"{alternative.name}_OPT_1", "Budget-reduced proposal", parameters, "PROPOSED", 1, self.source))
        if poor_energy:
            parameters = dict(alternative.parameters)
            parameters["facade"] = "doble piel"
            proposals.append(Alternative(f"ALT-{uuid4().hex[:10]}", alternative.project_id, f"{alternative.name}_OPT_2", "Energy-improved proposal", parameters, "PROPOSED", 1, self.source))
        return proposals


def tradeoff_matrix(alternatives: Iterable[Alternative], evaluations: Iterable[Evaluation], objectives: list[Objective]) -> str:
    alternatives = list(alternatives)
    evaluations = list(evaluations)
    result = pareto_front(alternatives, evaluations, objectives)
    values = {(item.alternative_id, item.objective_id): item.value for item in evaluations}
    lines = ["TRADE-OFF MATRIX", "Alternative | " + " | ".join(objective.key for objective in objectives) + " | Pareto"]
    baseline = alternatives[0] if alternatives else None
    for alternative in alternatives:
        cells = [values.get((alternative.alternative_id, objective.objective_id), "INCOMPLETE") for objective in objectives]
        marker = "YES" if alternative.alternative_id in result.non_dominated else "NO"
        lines.append(f"{alternative.name} | " + " | ".join(str(cell) for cell in cells) + f" | {marker}")
    if baseline:
        lines.append("")
        for alternative in alternatives[1:]:
            deltas = []
            for objective in objectives:
                base_value = values.get((baseline.alternative_id, objective.objective_id))
                candidate_value = values.get((alternative.alternative_id, objective.objective_id))
                if base_value is not None and candidate_value is not None and base_value != 0:
                    deltas.append(f"{objective.key} delta {((candidate_value - base_value) / abs(base_value) * 100):+.1f}%")
            if deltas:
                lines.append(f"{alternative.name} vs {baseline.name}: " + ", ".join(deltas))
    lines.append("Pareto front: " + ", ".join(result.non_dominated) if result.non_dominated else "Pareto front: none")
    return "\n".join(lines) + "\n"


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
