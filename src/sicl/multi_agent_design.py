from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .advanced_evolution import advanced_evolution, design_distance
from .multiscale_generative import resolve_generative_capabilities
from .spatial_evaluation import spatial_metrics
from .spatial_generator import UPAO001SpatialGenerator
from .gdi import design_dna
from .v11 import Alternative

AGENT_PROFILES = {
    "GENERALIST": {"role": "GENERALIST", "dimensions": ["coherence", "tradeoff"], "scopes": "ALL", "state": "AVAILABLE"},
    "BIOCLIMATIC": {"role": "BIOCLIMATIC", "dimensions": ["solar_context", "open_space"], "scopes": ["parcela_sitio", "edificacion", "espacio"], "state": "AVAILABLE"},
    "URBAN_SITE": {"role": "URBAN_SITE", "dimensions": ["site_relationship", "orientation"], "scopes": ["parcela_sitio", "zona_barrio_sector", "distrito_ciudad"], "state": "PARTIAL"},
    "DEVELOPER_AREA_EFFICIENCY": {"role": "DEVELOPER_AREA_EFFICIENCY", "dimensions": ["gross_area", "open_site_area"], "scopes": ["parcela_sitio", "edificacion"], "state": "AVAILABLE"},
    "BEAUTY_HARMONY": {"role": "BEAUTY_HARMONY", "dimensions": ["massing", "proportion"], "scopes": ["edificacion", "espacio"], "state": "PARTIAL"},
}

def profiles(scope: str) -> list[dict[str, Any]]:
    result = []
    for agent_id, profile in AGENT_PROFILES.items():
        state = profile["state"] if profile["scopes"] == "ALL" or scope in profile["scopes"] else "NOT_AVAILABLE"
        result.append({"agent_id": agent_id, **profile, "capability_state": state, "provenance": "GDI-P1/P8 deterministic perspective"})
    return result

def _metrics(alternative: dict[str, Any]) -> dict[str, Any]:
    representation = UPAO001SpatialGenerator().generate(Alternative(**alternative))
    return spatial_metrics(representation, UPAO001SpatialGenerator())

def inspect_design(alternative: dict[str, Any], scope: str, active_agents: list[str] | None = None) -> dict[str, Any]:
    chosen = active_agents or list(AGENT_PROFILES)
    available = {item["agent_id"]: item for item in profiles(scope) if item["capability_state"] not in {"NOT_AVAILABLE", "REQUIRES_DATA"}}
    metrics = _metrics(alternative)
    dna = design_dna(Alternative(**alternative))
    observations = []
    for agent_id in chosen:
        profile = available.get(agent_id)
        if not profile:
            observations.append({"agent": agent_id, "state": "NOT_AVAILABLE", "classification": "UNKNOWN", "provenance": "scope capability resolver"})
            continue
        if agent_id == "DEVELOPER_AREA_EFFICIENCY":
            fact = {"metric": "gross_massing_area", "value": metrics.get("gross_massing_area"), "source": "S2 deterministic spatial metrics"}
            interpretation = "area is a descriptive trade-off, not profitability"
        elif agent_id == "BIOCLIMATIC":
            fact = {"metric": "open_site_area", "value": metrics.get("open_site_area"), "source": "S2 deterministic spatial metrics"}
            interpretation = "open area may offer spatial/environmental opportunity; performance is unknown"
        elif agent_id == "URBAN_SITE":
            fact = {"metric": "footprint_ratio", "value": alternative.get("parameters", {}).get("footprint_ratio"), "source": "SpatialRepresentation parameters"}
            interpretation = "site relationship requires context data before a stronger claim"
        elif agent_id == "BEAUTY_HARMONY":
            fact = {"metric": "composition_family", "value": dna.get("composition_family"), "source": "derived Design DNA"}
            interpretation = "massing distinction is observable; aesthetic judgment remains human"
        else:
            fact = {"metric": "composition_family", "value": dna.get("composition_family"), "source": "derived Design DNA"}
            interpretation = "the alternative has a coherent current composition"
        observations.append({"agent": agent_id, "alternative_id": alternative["alternative_id"], "scope": scope, "fact": fact, "interpretation": interpretation, "classification": "AGENT_INTERPRETATION", "provenance": "P8 deterministic evidence perspective", "confidence": "OBSERVED"})
    return {"alternative_id": alternative["alternative_id"], "scope": scope, "profiles": profiles(scope), "observations": observations, "facts": metrics, "design_dna": dna, "decision_created": False}

def position_matrix(exploration: dict[str, Any]) -> dict[str, Any]:
    observations = exploration.get("observations", [])
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in observations:
        if "fact" in item: groups.setdefault(item["fact"]["metric"], []).append(item)
    matrix = []
    for issue, positions in groups.items():
        values = {str(item["fact"].get("value")) for item in positions}
        matrix.append({"issue": issue, "positions": positions, "agreement": len(values) <= 1, "disagreement": len(values) > 1, "consensus_is_not_truth": True})
    return {"issues": matrix, "disagreement_preserved": True, "majority_vote_decision": False}

def design_critic(exploration: dict[str, Any], intent: dict[str, Any] | None = None) -> dict[str, Any]:
    metrics = exploration.get("facts", {})
    findings = []
    if metrics.get("gross_massing_area") is not None and metrics.get("open_site_area") is not None:
        findings.append({"category": "TRADEOFF", "question": "Gross massing area and open site area should be inspected together; increasing one may affect the other.", "evidence": ["gross_massing_area", "open_site_area"], "classification": "AGENT_PROPOSAL"})
    if not intent:
        findings.append({"category": "MISSING_EVIDENCE", "question": "No adopted Human Intent was supplied for this inspection.", "evidence": [], "classification": "REQUIRES_EVIDENCE"})
    return {"findings": findings, "automatic_decision": False, "critic_is_insult": False, "decision_created": False}

def strategies(alternative: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    return [{"agent": "BIOCLIMATIC", "concern": "open_space", "candidate_intent": "preserve or increase open space", "operation": "MODIFY_OPEN_SPACE", "preserved": ["strategy"], "mutable": ["footprint_ratio"], "expected_tradeoff": "proposal", "evidence": ["open_site_area"], "provenance": "P8 strategy proposal", "scope": scope}, {"agent": "DEVELOPER_AREA_EFFICIENCY", "concern": "gross_area", "candidate_intent": "inspect gross massing trade-off", "operation": "COMPACT", "preserved": ["strategy"], "mutable": ["footprint_ratio"], "expected_tradeoff": "proposal", "evidence": ["gross_massing_area"], "provenance": "P8 strategy proposal", "scope": scope}]

def debate(issue: str, exploration: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    related = [item for item in matrix.get("issues", []) if item["issue"] in issue]
    state = "DISAGREEMENT" if any(item.get("disagreement") for item in related) else ("AGREEMENT" if related else "INSUFFICIENT_EVIDENCE")
    return {"issue": issue, "rounds": [{"agent": item.get("agent"), "position": item.get("interpretation"), "evidence": item.get("fact")} for item in exploration.get("observations", []) if "fact" in item], "state": state, "unresolved_allowed": True, "human_review_required": True, "decision_created": False}

def multi_agent_exploration(alternative: dict[str, Any], scope: str, active_agents: list[str] | None = None, intent: dict[str, Any] | None = None) -> dict[str, Any]:
    exploration = inspect_design(alternative, scope, active_agents)
    matrix = position_matrix(exploration)
    critic = design_critic(exploration, intent)
    return {"exploration": exploration, "position_matrix": matrix, "critic": critic, "strategies": strategies(alternative, scope), "agent_winner": None, "decision_created": False, "human_confirmation_required": True}
