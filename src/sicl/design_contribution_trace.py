"""Structured Design Contribution Trace for the human-authorized design loop.

This module is deliberately descriptive: it records lineage and computed observations,
while keeping expected effects separate from observed effects. It does not infer
causality, make recommendations, or create decisions.
"""
from __future__ import annotations

from typing import Any


def _value(data: dict[str, Any] | None, *keys: str) -> Any:
    current: Any = data or {}
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _metric_deltas(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for key in sorted(set(before) | set(after)):
        left, right = before.get(key), after.get(key)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            result.append({"metric": key, "before": left, "after": right, "delta": right - left, "classification": "COMPUTED_DETERMINISTIC"})
    return result


def _spatial_observations(representation: dict[str, Any] | None) -> dict[str, Any]:
    if not representation:
        return {"state": "NOT_AVAILABLE", "elements": "NOT_AVAILABLE"}
    elements = representation.get("elements")
    observations: dict[str, Any] = {"state": "OBSERVABLE_GEOMETRY", "elements": len(elements) if isinstance(elements, list) else "NOT_AVAILABLE"}
    for key in ("site_area", "footprint_area", "gross_massing_area", "open_site_area"):
        if key in representation:
            observations[key] = representation[key]
    return observations


def build_design_contribution_trace(
    *,
    project_id: str,
    intent: dict[str, Any],
    knowledge: dict[str, Any],
    hypotheses: list[dict[str, Any]],
    explorations: list[dict[str, Any]],
    semantic_reasoning: dict[str, Any] | None = None,
    human_confirmed: bool = True,
) -> dict[str, Any]:
    """Build one trace per bounded, human-confirmed hypothesis."""
    forces = (semantic_reasoning or {}).get("forces", [])
    tensions = (semantic_reasoning or {}).get("tensions", [])
    trace_items: list[dict[str, Any]] = []
    for index, exploration in enumerate(explorations):
        hypothesis = hypotheses[index] if index < len(hypotheses) else {}
        base = exploration.get("base_representation") or {}
        child = exploration.get("representation") or {}
        base_metrics = _value(exploration, "metrics", "base") or {}
        child_metrics = _value(exploration, "metrics", "derived") or {}
        expected = hypothesis.get("expected_effects") or ["Spatial consequence requires human inspection against the stated intent."]
        trace_items.append({
            "trace_id": f"DCT-{project_id}-{index + 1:02d}",
            "project_id": project_id,
            "parent_alternative_id": exploration.get("parent_alternative_id", "NOT_AVAILABLE"),
            "child_alternative_id": _value(exploration, "derived_alternative", "alternative_id") or "NOT_AVAILABLE",
            "hypothesis_id": hypothesis.get("hypothesis_id", f"HYPOTHESIS-{index + 1:02d}"),
            "hypothesis": hypothesis.get("statement", "Provisional hypothesis; inspect before adoption."),
            "human_confirmation": {"required": True, "received": bool(human_confirmed), "actor": "human-architect" if human_confirmed else "NOT_CONFIRMED"},
            "controlled_operation": exploration.get("generation_operation", "NOT_AVAILABLE"),
            "parameters_before": exploration.get("base_alternative", {}).get("parameters", {}),
            "parameters_after": exploration.get("derived_alternative", {}).get("parameters", {}),
            "changed_parameters": exploration.get("changed_parameters", {}),
            "spatial_relationships_before": base.get("relationships", "NOT_AVAILABLE"),
            "spatial_relationships_after": child.get("relationships", "NOT_AVAILABLE"),
            "geometric_observations_before": _spatial_observations(base),
            "geometric_observations_after": _spatial_observations(child),
            "computed_metrics_before": base_metrics or "NOT_AVAILABLE",
            "computed_metrics_after": child_metrics or "NOT_AVAILABLE",
            "metric_deltas": _metric_deltas(base_metrics, child_metrics),
            "expected_effect": {"classification": "EXPECTED_EFFECT", "statements": expected, "source": "HYPOTHESIS_INTERPRETATION"},
            "observed_effect": {"classification": "OBSERVED_GEOMETRIC_EFFECT" if child else "NOT_AVAILABLE", "statements": ["Changed parameters and deterministic geometry are observable."], "evidence": "SPATIAL_REPRESENTATION" if child else "REQUIRES_EVIDENCE"},
            "unknown_effect": ["Real-world performance, comfort, cost, compliance and causation are not established by this trace."],
            "tradeoffs": exploration.get("tradeoffs", []),
            "knowledge_contributions": knowledge.get("cross_source_relationships", []) or knowledge.get("links", []),
            "forces": forces,
            "tensions": tensions,
            "provenance": {"intent": intent, "knowledge_operation": knowledge.get("provenance", {}), "exploration": exploration.get("provenance", {}), "human_review_required": True},
            "decision_created": False,
            "recommendation_created": False,
        })
    return {
        "trace_type": "DESIGN_CONTRIBUTION_TRACE",
        "project_id": project_id,
        "trace_items": trace_items,
        "source_interaction": {
            "WHITE": "site/context and relationship investigation framing; not an autonomous site-analysis engine",
            "CHING": "form/space/order and organization framing; not a mandatory design rule",
            "interaction": "complementary contextual interpretation; no authorial consensus or automatic causality inferred",
        },
        "epistemic_boundary": {"expected_effect_distinct_from_observed": True, "computed_not_real_world_validated": True, "human_authority_preserved": True},
        "decision_created": False,
        "recommendation_created": False,
    }


__all__ = ["build_design_contribution_trace"]
