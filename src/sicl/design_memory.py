from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any


def _event_dict(event: Any) -> dict[str, Any]:
    return {"event_id": event.id, "timestamp": event.timestamp, "type": event.type, "actor": event.actor, "source": event.source, "payload": event.payload}


def _alternative_dict(item: Any) -> dict[str, Any]:
    value = asdict(item) if is_dataclass(item) else dict(vars(item))
    value["alternative_id"] = value.pop("alternative_id", value.get("id"))
    return value


def _candidate_records(events: list[Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for event in events:
        payload = event.payload if isinstance(event.payload, dict) else {}
        candidate = payload.get("candidate") or payload.get("derived_alternative") or payload.get("alternative")
        if isinstance(candidate, dict) and candidate.get("alternative_id"):
            records.append({"alternative": candidate, "event": _event_dict(event)})
    return records


def project_memory(repo: Any, project_id: str) -> dict[str, Any]:
    project = repo.get_project(project_id)
    if project is None:
        raise ValueError("PROJECT_NOT_FOUND")
    events = repo.events(project_id)
    alternatives = [_alternative_dict(item) for item in project.alternatives.values()]
    generated = []
    for generation in project.generated_alternatives.values():
        generated.append({"generation_id": generation.generation_id, "created_at": generation.created_at.isoformat(), "candidates": generation.candidates, "inputs": generation.inputs, "provenance": {"generator": generation.generator, "method": generation.method.value}})
    history: list[dict[str, Any]] = []
    for event in events:
        payload = event.payload if isinstance(event.payload, dict) else {}
        history.append({"sequence": len(history) + 1, "kind": _kind(event.type), "event": _event_dict(event), "alternative_id": payload.get("alternative_id") or payload.get("child_alternative_id") or payload.get("candidate", {}).get("alternative_id") if isinstance(payload.get("candidate"), dict) else payload.get("alternative_id")})
    lineage = _lineage(events, alternatives, generated)
    return {"project_id": project_id, "history": history, "alternatives": alternatives, "generations": generated, "lineage": lineage, "candidate_records": _candidate_records(events), "memory_status": "DERIVED_FROM_EVENT_LOG", "evidence_completeness": "PARTIAL" if not events else "OBSERVED", "second_historical_ledger": False}


def _kind(event_type: str) -> str:
    upper = event_type.upper()
    if "DECISION" in upper:
        return "HUMAN_DECISION"
    if "REVIEW" in upper:
        return "HUMAN_REVIEW"
    if any(token in upper for token in ("CONFIRM", "REJECT", "ABANDON", "KEEP", "CHANGE", "SELECT")):
        return "HUMAN_ACTION"
    if any(token in upper for token in ("GENERAT", "OPERAT", "EVOL", "SYNTH")):
        return "SYSTEM_ACTION"
    return "OBSERVED_EVENT"


def _lineage(events: list[Any], alternatives: list[dict[str, Any]], generations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    known = {item.get("alternative_id"): item for item in alternatives}
    for item in alternatives:
        parameters = item.get("parameters") if isinstance(item.get("parameters"), dict) else {}
        parent = parameters.get("parent_alternative_id") or item.get("parent_alternative_id")
        result.append({"alternative_id": item.get("alternative_id"), "parent_alternative_id": parent, "children": [], "status": item.get("status", "UNKNOWN"), "reason": "not recorded"})
    for record in result:
        parent = record.get("parent_alternative_id")
        for child in result:
            if child.get("parent_alternative_id") == record["alternative_id"]:
                record["children"].append(child["alternative_id"])
    for event in events:
        payload = event.payload if isinstance(event.payload, dict) else {}
        aid = payload.get("alternative_id") or payload.get("child_alternative_id")
        if aid:
            for record in result:
                if record["alternative_id"] == aid:
                    record["last_event"] = _event_dict(event)
    return result


def explain_design(memory: dict[str, Any], alternative_id: str) -> dict[str, Any]:
    alternatives = {item.get("alternative_id"): item for item in memory.get("alternatives", [])}
    selected = alternatives.get(alternative_id)
    if selected is None:
        for record in memory.get("candidate_records", []):
            if record.get("alternative", {}).get("alternative_id") == alternative_id:
                selected = record["alternative"]
                break
    if selected is None:
        raise ValueError("ALTERNATIVE_NOT_FOUND")
    parent = selected.get("parent_alternative_id") or selected.get("parameters", {}).get("parent_alternative_id")
    related = [item for item in memory.get("history", []) if item.get("alternative_id") == alternative_id]
    intents = [item for item in related if "INTENT" in item["event"]["type"].upper()]
    operations = [item for item in related if "OPERAT" in item["event"]["type"].upper() or "GENERAT" in item["event"]["type"].upper()]
    return {"alternative_id": alternative_id, "short": f"This alternative derives from {parent or 'an unrecorded parent'}.", "parent_alternative_id": parent, "intent": intents or "not recorded", "operations": operations or "not recorded", "changes": selected.get("parameters", {}), "preserved": "not recorded", "human_reason": "not recorded", "provenance": selected.get("source", "not recorded"), "evidence_references": [item["event"]["event_id"] for item in related], "decision_created": False}


def replay(memory: dict[str, Any], alternative_id: str | None = None) -> dict[str, Any]:
    steps = memory.get("history", [])
    if alternative_id:
        steps = [step for step in steps if step.get("alternative_id") in {None, alternative_id}]
    return {"project_id": memory["project_id"], "steps": steps, "current_alternative_id": alternative_id, "mutates_project": False, "creates_decision": False}


def query_memory(memory: dict[str, Any], query: str) -> dict[str, Any]:
    key = query.strip().upper().replace(" ", "_")
    mapping = {"HOW_DID_WE_GET_HERE": "history", "WHAT_CHANGED": "explanations", "WHAT_WAS_KEPT": "preserved", "WHAT_INTENT_CREATED_THIS": "intent", "SHOW_PARENT": "parent", "SHOW_CHILDREN": "children", "SHOW_BRANCH": "lineage", "SHOW_PREVIOUS_DIRECTION": "history", "SHOW_REJECTED_DIRECTIONS": "rejected", "SHOW_HUMAN_REASONS": "reasons", "INTENT_VS_RESULT": "intent_vs_result", "EXPLAIN_THIS_DESIGN": "explanations"}
    result_type = mapping.get(key, "history")
    result = {"query": query, "result_type": result_type, "evidence": memory.get("history", []), "links_to_design": memory.get("alternatives", []), "unknowns": ["human reason not recorded"]}
    if result_type == "lineage": result["evidence"] = memory.get("lineage", [])
    if result_type == "rejected": result["evidence"] = [item for item in memory.get("history", []) if item.get("event", {}).get("payload", {}).get("status") in {"REJECTED_BY_HUMAN", "ABANDONED"}]
    return result


def direction_event(project_id: str, alternative_id: str, status: str, actor: str, reason: str | None) -> dict[str, Any]:
    allowed = {"ACTIVE", "KEPT", "ABANDONED", "REJECTED_BY_HUMAN", "SUPERSEDED"}
    if status not in allowed:
        raise ValueError("INVALID_DIRECTION_STATUS")
    return {"type": "DESIGN_DIRECTION_STATUS_RECORDED", "payload": {"alternative_id": alternative_id, "status": status, "human_reason": reason or "not recorded", "reason_is_system_inferred": False}, "actor": actor, "source": "design-memory"}
