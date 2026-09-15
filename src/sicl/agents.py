from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import uuid4

from .domain import Project
from .v11 import Alternative, Evaluation


class BaseAgent(ABC):
    name = "BASE"

    @abstractmethod
    def evaluate(self, alternative: Alternative, project: Project) -> Evaluation:
        raise NotImplementedError


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
        reasons: list[str] = []
        if warm_site:
            reasons.append("warm-climate rule")
            if facade == "vidrio simple":
                value *= 0.8
                reasons.append("simple-glass penalty -20%")
            if orientation in {"norte", "sur"}:
                value += 5.0
                reasons.append("solar-control orientation bonus")
        return Evaluation(
            evaluation_id=f"EVAL-{uuid4().hex[:10]}",
            alternative_id=alternative.alternative_id,
            objective_id=objective.objective_id,
            value=round(value, 2),
            unit="score",
            confidence=0.8,
            source="EXPERT_SYSTEM",
        )
