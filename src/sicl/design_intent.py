from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from typing import Any


@dataclass(frozen=True)
class IntentSuggestion:
    intent_id: str
    kind: str
    statement: str
    confidence: str
    evidence_terms: list[str]
    provenance: dict[str, Any]


_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("CONSTRAINT", ("evitar", "máximo", "maximo", "límite", "limite", "no ")),
    ("PREFERENCE", ("prefiero", "preferencia", "quiero", "priorizo")),
    ("OBJECTIVE", ("maximizar", "mejorar", "optimizar", "más espacio", "mas espacio")),
    ("DESIGN_IDEA", ("compact", "patio", "courtyard", "articul", "masa", "orient")),
)


def _provenance(project_id: str | None, spatial_scope: str | None) -> dict[str, Any]:
    return {
        "source": "USER_DECLARED",
        "interpreter": "SICL_DETERMINISTIC_INTENT_RULES",
        "version": "1.0",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "project_id": project_id,
        "spatial_scope": spatial_scope,
    }


def interpret_intent(text: str, *, project_id: str | None = None, spatial_scope: str | None = None) -> dict[str, Any]:
    raw = text.strip()
    if not raw:
        raise ValueError("INTENT_TEXT_REQUIRED")
    normalized = re.sub(r"\s+", " ", raw)
    provenance = _provenance(project_id, spatial_scope)
    suggestions: list[IntentSuggestion] = []
    lowered = normalized.casefold()
    for kind, terms in _RULES:
        hits = [term for term in terms if term in lowered]
        if hits:
            suggestions.append(IntentSuggestion(
                intent_id=f"INTENT-SUGGESTED-{len(suggestions) + 1}",
                kind=kind,
                statement=normalized,
                confidence="MEDIUM",
                evidence_terms=hits,
                provenance=provenance,
            ))
    if not suggestions:
        suggestions.append(IntentSuggestion(
            intent_id="INTENT-SUGGESTED-1",
            kind="DESIGN_IDEA",
            statement=normalized,
            confidence="LOW",
            evidence_terms=[],
            provenance=provenance,
        ))
    return {
        "raw_input": normalized,
        "suggestions": [asdict(item) for item in suggestions],
        "human_confirmation_required": True,
        "suggestion_creates_decision": False,
        "decision_created": False,
        "provenance": provenance,
    }


def confirm_intent(project_id: str, interpretation: dict[str, Any], approved_ids: list[str], actor: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not actor.strip() or actor.upper() == "SYSTEM":
        raise ValueError("HUMAN_AUTHORITY_REQUIRED")
    available = {item["intent_id"] for item in interpretation.get("suggestions", [])}
    selected_ids = list(dict.fromkeys(approved_ids))
    if not selected_ids or not set(selected_ids).issubset(available):
        raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
    adopted = {
        "project_id": project_id,
        "adopted_intents": [item for item in interpretation["suggestions"] if item["intent_id"] in selected_ids],
        "actor": actor,
        "adoption": "HUMAN_CONFIRMED",
        "decision_created": False,
        "provenance": {
            "source": "HUMAN_CONFIRMATION",
            "interpreter": interpretation.get("provenance", {}),
        },
    }
    event = {
        "type": "HUMAN_INTENT_ADOPTED",
        "source": "HUMAN_INTENT",
        "project_id": project_id,
        "payload": adopted,
    }
    return adopted, event


def intent_to_generation_input(adopted: dict[str, Any]) -> dict[str, Any]:
    if adopted.get("adoption") != "HUMAN_CONFIRMED":
        raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
    return {
        "intent_ids": [item["intent_id"] for item in adopted.get("adopted_intents", [])],
        "provenance": adopted.get("provenance", {}),
    }


__all__ = ["IntentSuggestion", "interpret_intent", "confirm_intent", "intent_to_generation_input"]
