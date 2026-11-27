"""CP-03 static capability catalog and conservative intent routing.

The registry describes operations only; it contains no execution adapters and does
not authorize invocation. Registry entries are code-owned and immutable at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .copilot_contract import CopilotIntent


class CapabilityRisk(str, Enum):
    R0 = "R0"  # conversational/read-only local
    R1 = "R1"  # research/read
    R2 = "R2"  # prepare draft, no project mutation
    R3 = "R3"  # reversible mutation
    R4 = "R4"  # high-impact mutation


@dataclass(frozen=True)
class CapabilitySpec:
    capability_id: str
    version: str
    name: str
    description: str
    intents: tuple[CopilotIntent, ...]
    risk: CapabilityRisk
    available: bool = False
    adapter_id: str | None = None
    requires_project: bool = False
    requires_confirmation: bool = True
    permission: str = "copilot.read"
    input_schema_id: str = "none"
    output_schema_id: str = "text"
    timeout_seconds: int = 30
    idempotent: bool = True

    def __post_init__(self) -> None:
        if not self.capability_id.strip() or not self.version.strip():
            raise ValueError("capability_id and version are required")
        if self.timeout_seconds < 1 or self.timeout_seconds > 900:
            raise ValueError("timeout_seconds must be in 1..900")
        if self.risk in {CapabilityRisk.R3, CapabilityRisk.R4} and not self.requires_confirmation:
            raise ValueError("mutation capabilities cannot bypass confirmation")


# CP-03 initial catalog: metadata only. Availability remains false until a real
# adapter, health check, permission model, and tests exist.
_CATALOG = {
    "conversation.respond": CapabilitySpec(
        "conversation.respond", "1", "Conversación", "Responder y mantener diálogo contextual.",
        (CopilotIntent.CONVERSE, CopilotIntent.CONTINUE), CapabilityRisk.R0,
        available=False, adapter_id="conversation_model", requires_confirmation=False,
        permission="copilot.converse", input_schema_id="chat.v1"),
    "research.search": CapabilitySpec(
        "research.search", "1", "Investigación", "Buscar fuentes externas y sintetizar evidencia.",
        (CopilotIntent.RESEARCH,), CapabilityRisk.R1,
        adapter_id="web_research", requires_confirmation=False,
        permission="copilot.research", input_schema_id="research_query.v1"),
    "analysis.explore": CapabilitySpec(
        "analysis.explore", "1", "Exploración", "Explorar problemas, escenarios e hipótesis.",
        (CopilotIntent.EXPLORE,), CapabilityRisk.R0,
        available=False, adapter_id="reasoning_model", requires_confirmation=False,
        permission="copilot.converse", input_schema_id="exploration.v1"),
    "architecture.design": CapabilitySpec(
        "architecture.design", "1", "Diseño arquitectónico", "Desarrollar intención, programa y alternativas sin mutar el proyecto.",
        (CopilotIntent.DESIGN_INTENT,), CapabilityRisk.R2,
        available=True, adapter_id="reasoning_model", requires_confirmation=False,
        permission="copilot.design", input_schema_id="design_brief.v1"),
    "action.prepare": CapabilitySpec(
        "action.prepare", "1", "Preparación de acción", "Preparar plan, entradas y efectos esperados para una acción futura.",
        (CopilotIntent.PREPARE_ACTION,), CapabilityRisk.R2,
        available=False, adapter_id="action_planner", requires_confirmation=False,
        permission="copilot.prepare", input_schema_id="action_plan.v1"),
    "review.inspect": CapabilitySpec(
        "review.inspect", "1", "Auditoría y revisión", "Revisar resultados, archivos, evidencia y posibles inconsistencias.",
        (CopilotIntent.REVIEW,), CapabilityRisk.R1,
        adapter_id="review_pipeline", requires_confirmation=False,
        permission="copilot.review", input_schema_id="review_request.v1"),
    "operation.execute": CapabilitySpec(
        "operation.execute", "1", "Ejecución controlada", "Invocar operaciones aprobadas mediante adaptadores específicos.",
        (CopilotIntent.EXECUTE,), CapabilityRisk.R4,
        available=False, adapter_id=None, requires_confirmation=True,
        permission="copilot.execute", input_schema_id="execution_request.v1"),
}
CAPABILITY_REGISTRY: Mapping[str, CapabilitySpec] = MappingProxyType(_CATALOG)


def get_capability(capability_id: str) -> CapabilitySpec | None:
    return CAPABILITY_REGISTRY.get(capability_id)


def capabilities_for_intent(intent: CopilotIntent, *, available_only: bool = False) -> tuple[CapabilitySpec, ...]:
    matches = tuple(spec for spec in CAPABILITY_REGISTRY.values() if intent in spec.intents)
    if available_only:
        return tuple(spec for spec in matches if spec.available)
    return matches


def plan_capability_route(intent: CopilotIntent, *, ambiguous: bool = False) -> dict:
    """Suggest route candidates; never invoke or authorize any capability."""
    if ambiguous:
        return {"status": "CLARIFICATION_REQUIRED", "candidates": [], "reason": "intent_ambiguous"}
    candidates = capabilities_for_intent(intent)
    if not candidates:
        return {"status": "NO_CAPABILITY", "candidates": [], "reason": "no_registered_capability"}
    ready = [spec for spec in candidates if spec.available and spec.adapter_id]
    return {
        "status": "ROUTE_CANDIDATES",
        "intent": intent.value,
        "candidates": [spec.capability_id for spec in candidates],
        "ready_for_orchestration": [spec.capability_id for spec in ready],
        "execution_authorized": False,
        "reason": "catalog_selection_is_not_permission",
    }
