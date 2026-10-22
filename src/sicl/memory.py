from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from .domain import InstitutionalMemory, MemoryConfidence, MemoryState, MemoryType, Project, SpatialScope
from .errors import SICLError


def _type_for(project: Project) -> MemoryType:
    if project.decisions:
        return MemoryType.DECISION_PATTERN
    if project.preferences:
        return MemoryType.PREFERENCE_PATTERN
    if project.evaluations:
        return MemoryType.EVALUATION_PATTERN
    if project.generated_alternatives:
        return MemoryType.GENERATION_PATTERN
    return MemoryType.LESSON_LEARNED


def extract_memory(project: Project, memory_id: str | None = None, *, anonymize: bool = True) -> InstitutionalMemory:
    if project.stage != "CLOSED":
        raise SICLError("PROJECT_NOT_CLOSED", "institutional memory requires a closed project")
    decision_text = [item.statement for item in project.decisions.values()]
    preference_text = [item.statement for item in project.preferences.values()]
    evaluation_text = [f"{item.alternative_id}:{item.objective_id}={item.value}" for item in project.evaluations.values()]
    generation_text = [f"{item.method.value}:{len(item.candidates)} candidates" for item in project.generated_alternatives.values()]
    fragments = decision_text + preference_text + evaluation_text + generation_text
    summary = " | ".join(fragments) if fragments else f"Closed project pattern: {project.name}"
    source_id = None if anonymize else project.project_id
    scope = [project.spatial_scope] if project.spatial_scope else []
    return InstitutionalMemory(
        memory_id=memory_id or f"MEM-{uuid.uuid4().hex[:12]}",
        memory_type=_type_for(project),
        scope=scope,
        project_id_source=source_id,
        summary=summary,
        evidence=list(project.evidence.keys()),
        decisions_referenced=list(project.decisions.keys()),
        state=MemoryState.ACTIVE,
        confidence=MemoryConfidence.MEDIUM if fragments else MemoryConfidence.UNKNOWN,
        anonymized=anonymize,
        created_at=datetime.now(timezone.utc),
        version=1,
    )


def memory_to_dict(memory: InstitutionalMemory) -> dict[str, Any]:
    value = asdict(memory)
    value["memory_type"] = memory.memory_type.value
    value["state"] = memory.state.value
    value["confidence"] = memory.confidence.value
    value["scope"] = [item.value for item in memory.scope]
    return value


def memory_types() -> list[str]:
    return [item.value for item in MemoryType]
