from __future__ import annotations

from dataclasses import asdict

from .domain import NormativeInterpretation, Regulation, NormativeSnapshot

LEGAL_DISCLAIMER = "No constituye certificación legal ni reemplaza revisión profesional."


def regulation_to_dict(value: Regulation) -> dict:
    result = asdict(value)
    result["status"] = value.status.value
    result["source_type"] = value.source_type.value
    result["scope_applicable"] = [scope.value for scope in value.scope_applicable]
    result["publication_date"] = value.publication_date.isoformat() if value.publication_date else None
    result["effective_date"] = value.effective_date.isoformat() if value.effective_date else None
    return result


def interpretation_to_dict(value: NormativeInterpretation) -> dict:
    result = asdict(value)
    result["confidence"] = value.confidence.value
    result["state"] = value.state.value
    result["interpretation_date"] = value.interpretation_date.isoformat()
    return result


def snapshot_to_dict(value: NormativeSnapshot) -> dict:
    result = asdict(value)
    result["state"] = value.state.value
    result["cut_date"] = value.cut_date.isoformat()
    result["created_at"] = value.created_at.isoformat()
    return result
