from __future__ import annotations

from abc import ABC, abstractmethod
from re import search
from uuid import uuid4

from .domain import Project
from .v11 import Alternative, Evaluation


class BaseAgent(ABC):
    name = "BASE"

    @abstractmethod
    def evaluate(self, alternative: Alternative, project: Project) -> Evaluation:
        raise NotImplementedError


def _parameter(alternative: Alternative, key: str, default: str = "") -> str:
    return next((str(value) for name, value in alternative.parameters.items() if name.upper() == key.upper()), default)


def _number(text: str, key: str) -> float | None:
    match = search(rf"\b{key}\s*[=:]\s*(-?\d+(?:\.\d+)?)", text, flags=2)
    return float(match.group(1)) if match else None


class BioclimaticAgent(BaseAgent):
    name = "BIOCLIMATIC"

    def evaluate(self, alternative: Alternative, project: Project) -> Evaluation:
        objective = next((item for item in project.objectives.values() if item.key == "ENERGY_SAVINGS"), None)
        if objective is None:
            raise ValueError("ENERGY_SAVINGS objective is required")
        facade = str(alternative.parameters.get("facade", "")).lower()
        orientation = str(alternative.parameters.get("orientation", "")).lower()
        warm_site = any("temperatura" in fact.statement.lower() for fact in project.facts.values())
        value = 80.0
        if warm_site:
            if facade == "vidrio simple":
                value *= 0.8
            if orientation in {"norte", "sur"}:
                value += 5.0
        return Evaluation(f"EVAL-{uuid4().hex[:10]}", alternative.alternative_id, objective.objective_id, round(value, 2), "score", 0.8, "EXPERT_SYSTEM")


class StructuralAgent(BaseAgent):
    name = "STRUCTURAL"

    def evaluate(self, alternative: Alternative, project: Project) -> Evaluation:
        objective = next((item for item in project.objectives.values() if item.key == "SAFETY"), None)
        if objective is None:
            raise ValueError("SAFETY objective is required")
        floors = float(_parameter(alternative, "FLOORS", "0"))
        structure = _parameter(alternative, "STRUCTURE").lower()
        foundation = _parameter(alternative, "FOUNDATION_TYPE").lower()
        soil_soft = any(("suelo" in fact.statement.lower() or "soil_type" in fact.statement.lower()) and "blando" in fact.statement.lower() for fact in project.facts.values())
        value = 100.0
        if floors > 6 and structure == "mampostería":
            value -= 30.0
        if soil_soft and foundation != "pilotes":
            value -= 40.0
        return Evaluation(f"EVAL-{uuid4().hex[:10]}", alternative.alternative_id, objective.objective_id, value, "score", 0.85, "EXPERT_SYSTEM")


class EconomicAgent(BaseAgent):
    name = "ECONOMIC"

    def evaluate(self, alternative: Alternative, project: Project) -> Evaluation:
        objective = next((item for item in project.objectives.values() if item.key == "ESTIMATED_COST"), None)
        if objective is None:
            raise ValueError("ESTIMATED_COST objective is required")
        floors = _number(" ".join(f"{key}={value}" for key, value in alternative.parameters.items()), "FLOORS") or 0.0
        area = next((_number(item.statement, "AREA") for item in project.assumptions.values() if _number(item.statement, "AREA") is not None), None) or 0.0
        cost_per_m2 = next((_number(item.statement, "COST_PER_M2") for item in project.assumptions.values() if _number(item.statement, "COST_PER_M2") is not None), None) or 0.0
        budget = next((_number(item.value, "BUDGET") for item in project.constraints.values() if item.key.upper() == "BUDGET"), None)
        if budget is None:
            budget = next((float(item.value) for item in project.constraints.values() if item.key.upper() == "BUDGET" and item.value.replace('.', '', 1).isdigit()), None)
        estimated = floors * area * cost_per_m2
        value = -1.0 if budget is not None and estimated > budget else estimated
        return Evaluation(f"EVAL-{uuid4().hex[:10]}", alternative.alternative_id, objective.objective_id, value, "usd_or_status", 0.8, "EXPERT_SYSTEM")
