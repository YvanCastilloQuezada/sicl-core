from __future__ import annotations

from typing import Any


def normalize_design_candidate(value: dict[str, Any], project_id: str | None = None) -> dict[str, Any]:
    """Adapt a P3 spatial synthesis result to the canonical Alternative shape.

    The adapter preserves the P3 identity and provenance while deriving only the
    small parameter set already consumed by the deterministic GDI engines.
    Canonical Alternative payloads pass through unchanged.
    """
    if not isinstance(value, dict):
        raise ValueError("INVALID_DESIGN_CANDIDATE")

    nested = value.get("alternative")
    if isinstance(nested, dict) and "representation" not in nested and "parameters" in nested and "alternative_id" in nested:
        return nested
    if "representation" not in value and "parameters" in value and "alternative_id" in value:
        return value
    if isinstance(nested, dict):
        value = nested

    representation = value.get("representation")
    if not isinstance(representation, dict):
        raise ValueError("CANONICAL_ALTERNATIVE_REQUIRED")

    alternative_id = str(value.get("alternative_id") or representation.get("alternative_id") or "")
    if not alternative_id:
        raise ValueError("P3_ALTERNATIVE_ID_REQUIRED")
    family = str(value.get("family") or representation.get("seed") or "COURTYARD").upper()
    strategy = family.lower().replace(" ", "_")
    parameters: dict[str, Any] = {
        "strategy": strategy,
        "footprint_ratio": 0.42,
        "floors": 1,
        "courtyard_ratio": 0.30 if family == "COURTYARD" else 0.0,
        "mass_separation": 10 if family in {"CLUSTERED", "SEPARATED", "ARTICULATED"} else 0,
    }
    elements = representation.get("elements")
    if isinstance(elements, list):
        heights = [
            float(item.get("metadata", {}).get("height"))
            for item in elements
            if isinstance(item, dict) and isinstance(item.get("metadata", {}).get("height"), (int, float))
        ]
        if heights:
            parameters["floors"] = max(1, round(max(heights) / 3.2))

    return {
        "alternative_id": alternative_id,
        "project_id": str(value.get("project_id") or project_id or ""),
        "name": family,
        "description": "P3 synthetic spatial synthesis candidate adapted for deterministic GDI exploration",
        "parameters": parameters,
        "status": "GENERATED",
        "version": int(value.get("version", 1)),
        "source": "GDI-P3-ADAPTER",
    }


__all__ = ["normalize_design_candidate"]
