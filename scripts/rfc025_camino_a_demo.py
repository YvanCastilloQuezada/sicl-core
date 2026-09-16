"""RFC-025 demo: Open-Meteo observation + Pareto + RFC-020 feasibility.

This is an analytical demonstration. It does not create a normative Decision.
"""
from __future__ import annotations

import json
from pathlib import Path

from sicl.domain import Objective
from sicl.feasibility import evaluate_feasibility, feasible_pareto_front
from sicl.optimization import pareto_front
from sicl.site_intelligence import get_site_observation
from sicl.v11 import Alternative, Evaluation
from sicl.regulatory_corpus import load_corpus_fixture


def main() -> None:
    fixture = load_corpus_fixture(Path(__file__).parents[1] / "data" / "regulatory" / "rne_a010_sample.json")
    observation = get_site_observation("Trujillo, Peru", timeout=15)
    alternatives = [
        Alternative("A010-A", "P-RFC025", "Passive facade", parameters={"INVESTMENT": 90}),
        Alternative("A010-B", "P-RFC025", "Large glazing", parameters={"INVESTMENT": 125}),
        Alternative("A010-C", "P-RFC025", "Balanced envelope", parameters={"INVESTMENT": 105}),
    ]
    objectives = [
        Objective("OBJ-ENERGY", "P-RFC025", "ENERGY_PERFORMANCE", "MAXIMIZE", "higher is better"),
        Objective("OBJ-COST", "P-RFC025", "INVESTMENT", "MINIMIZE", "lower is better"),
    ]
    evaluations = [
        Evaluation("E-A-ENERGY", "A010-A", "OBJ-ENERGY", 86, "score", 0.9, "FACT"), Evaluation("E-A-COST", "A010-A", "OBJ-COST", 90, "kUSD", 0.9, "USER_INPUT"),
        Evaluation("E-B-ENERGY", "A010-B", "OBJ-ENERGY", 94, "score", 0.9, "FACT"), Evaluation("E-B-COST", "A010-B", "OBJ-COST", 125, "kUSD", 0.9, "USER_INPUT"),
        Evaluation("E-C-ENERGY", "A010-C", "OBJ-ENERGY", 90, "score", 0.9, "FACT"), Evaluation("E-C-COST", "A010-C", "OBJ-COST", 105, "kUSD", 0.9, "USER_INPUT"),
    ]
    pareto = pareto_front(alternatives, evaluations, objectives)
    constraints = [{"constraint_id": "C-INVESTMENT", "key": "INVESTMENT", "operator": "<=", "value": 110, "hard": True}]
    feasibility = [evaluate_feasibility(item.alternative_id, item.parameters, constraints, evaluated_by="RFC-020") for item in alternatives]
    feasible_front = feasible_pareto_front(pareto.non_dominated, feasibility)
    result = {
        "status": "LOCAL_ANALYTICAL_DEMO",
        "project_id": "P-RFC025",
        "site_observation": {"location": observation.location, "source": observation.source, "simulated": observation.simulated, "temperature_mean_c": observation.temperature_mean_c, "wind_speed_kmh": observation.wind_speed_kmh, "radiation_kwh_m2_day": observation.radiation_kwh_m2_day, "evidence_url": observation.evidence_url, "evidence_hash": observation.evidence_hash},
        "normative_fixture": {"regulation": fixture["regulations"][0]["code"], "status": fixture["regulations"][0]["status"], "fixture_hash": fixture["fixture_hash"]},
        "pareto_front": pareto.non_dominated,
        "feasibility": [item.to_dict() for item in feasibility],
        "feasible_pareto_front": feasible_front,
        "human_authority": {"recommendation": "not created", "human_review": "not created", "decision": "not created"},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
