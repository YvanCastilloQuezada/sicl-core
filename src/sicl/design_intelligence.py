from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any

from .design_knowledge import DesignKnowledgeAgent, DesignKnowledgeQuery, list_sources
from .domain import SpatialScope
from .spatial_evaluation import spatial_metrics
from .spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives
from .v11 import Alternative


def _id(prefix: str, payload: Any) -> str:
    digest = sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _intent_terms(adopted_intent: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    for item in adopted_intent.get("adopted_intents", []):
        terms.extend(item.get("evidence_terms", []))
        terms.extend(item.get("kind", "").lower().split())
        terms.extend(item.get("statement", "").casefold().split())
    return list(dict.fromkeys(term for term in terms if len(term) > 2))


def query_design_knowledge_for_intent(adopted_intent: dict[str, Any], *, regulations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    scope_value = adopted_intent.get("spatial_scope") or adopted_intent.get("provenance", {}).get("spatial_scope") or "edificacion"
    try:
        scope = SpatialScope(scope_value)
    except ValueError:
        scope = SpatialScope.EDIFICACION
    terms = _intent_terms(adopted_intent)
    response = DesignKnowledgeAgent(regulations or []).query(DesignKnowledgeQuery(
        spatial_scope=scope,
        problem_terms=terms,
        objectives=[item.get("kind", "") for item in adopted_intent.get("adopted_intents", [])],
        preferences=terms,
        requested_operation="DIV_P0_INTENT_LINK",
    ))
    items = response.applicable_items
    patterns = response.applicable_patterns
    source_map = {source["source_id"]: source for source in list_sources()}
    links = [{
        "intent_ids": [item.get("intent_id") for item in adopted_intent.get("adopted_intents", [])],
        "knowledge_item_id": item.get("knowledge_item_id"),
        "source_id": item.get("source_id"),
        "possible_effect": item.get("outputs", []),
        "possible_tradeoff": item.get("limitations", []),
        "knowledge_match": True,
        "recommendation_created": False,
        "decision_created": False,
    } for item in items]
    links.extend({
        "intent_ids": [item.get("intent_id") for item in adopted_intent.get("adopted_intents", [])],
        "pattern_id": pattern.get("pattern_id"),
        "source_ids": pattern.get("source_ids", []),
        "possible_effect": pattern.get("consequences", {}).get("positive", []),
        "possible_tradeoff": pattern.get("consequences", {}).get("negative", []),
        "knowledge_match": True,
        "recommendation_created": False,
        "decision_created": False,
    } for pattern in patterns)
    return {
        "query": asdict(response),
        "links": links,
        "applicable_items": items,
        "applicable_patterns": patterns,
        "sources": [source_map[source_id] for source_id in response.source_ids if source_id in source_map],
        "possible_effects": [effect for link in links for effect in link.get("possible_effect", [])],
        "possible_tradeoffs": [tradeoff for link in links for tradeoff in link.get("possible_tradeoff", [])],
        "decision_created": False,
        "recommendation_created": False,
        "provenance": {"agent": DesignKnowledgeAgent.name, "operation": "DIV_P0_INTENT_LINK"},
    }


def _base_alternative(alternative_id: str) -> Alternative:
    for alternative in generate_upao001_alternatives():
        if alternative.alternative_id == alternative_id:
            return alternative
    raise ValueError("BASE_ALTERNATIVE_NOT_FOUND")


def controlled_exploration(base_alternative_id: str, adopted_intent: dict[str, Any], knowledge: dict[str, Any]) -> dict[str, Any]:
    base = _base_alternative(base_alternative_id)
    parameters = dict(base.parameters)
    terms = " ".join(_intent_terms(adopted_intent)).casefold()
    changed: dict[str, Any] = {}
    if "espacio" in terms or "open" in terms or "objective" in terms:
        parameters["footprint_ratio"] = max(0.20, float(parameters.get("footprint_ratio", 0.42)) - 0.06)
        changed["footprint_ratio"] = {"from": base.parameters.get("footprint_ratio"), "to": parameters["footprint_ratio"]}
    elif "compact" in terms or "compactness" in terms:
        parameters["footprint_ratio"] = min(0.70, float(parameters.get("footprint_ratio", 0.42)) + 0.04)
        changed["footprint_ratio"] = {"from": base.parameters.get("footprint_ratio"), "to": parameters["footprint_ratio"]}
    else:
        parameters["orientation_degrees"] = 15.0
        changed["orientation_degrees"] = {"from": 0.0, "to": 15.0}
    derived_id = _id("UPAO-001-D", {"base": base.alternative_id, "parameters": parameters, "intent": adopted_intent.get("adopted_intents", [])})
    derived = Alternative(derived_id, base.project_id, f"DIV-P0-{base.name}", "Controlled DIV-P0 derivative", parameters, "GENERATED", 1, "DIV_P0_CONTROLLED")
    generator = UPAO001SpatialGenerator()
    base_representation = generator.generate(base)
    derived_representation = generator.generate(derived)
    base_metrics = spatial_metrics(base_representation, generator)
    derived_metrics = spatial_metrics(derived_representation, generator)
    deltas = {key: derived_metrics[key] - base_metrics[key] for key in derived_metrics if key in base_metrics}
    tradeoffs = [{"metric": key, "base": base_metrics[key], "derived": derived_metrics[key], "delta": deltas[key], "interpretation": "descriptive_only"} for key in deltas]
    return {
        "base_alternative": asdict(base),
        "derived_alternative": asdict(derived),
        "representation": derived_representation.to_dict(),
        "base_representation": base_representation.to_dict(),
        "changed_parameters": changed,
        "unchanged_parameters": {key: value for key, value in base.parameters.items() if key not in changed},
        "parent_alternative_id": base.alternative_id,
        "generation_operation": "CONTROLLED_PARAMETER_TRANSFORMATION",
        "generation_method": "DIV_P0_DETERMINISTIC",
        "intent_linkage": [item.get("intent_id") for item in adopted_intent.get("adopted_intents", [])],
        "knowledge_linkage": [link.get("knowledge_item_id", link.get("pattern_id")) for link in knowledge.get("links", [])],
        "known_constraint_state": "UNKNOWN_UNLESS_EXPLICITLY_SUPPLIED",
        "metrics": {"base": base_metrics, "derived": derived_metrics, "deltas": deltas},
        "tradeoffs": tradeoffs,
        "decision_created": False,
        "recommendation_created": False,
        "provenance": {"project": "UPAO-001", "classification": ["SYNTHETIC", "DETERMINISTIC_DERIVED", "EDUCATIONAL"]},
    }


__all__ = ["query_design_knowledge_for_intent", "controlled_exploration"]
