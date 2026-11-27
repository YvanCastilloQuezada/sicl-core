"""Conservative, deterministic intent classifier for ARKI Copilot CP-01.

This is a baseline routing aid, not an LLM, and must never authorize execution.
"""
from __future__ import annotations

import re

from sicl.copilot_contract import CopilotIntent, IntentAssessment


_RULES: tuple[tuple[CopilotIntent, tuple[str, ...]], ...] = (
    (CopilotIntent.CONTINUE, (r"\bcontin[uú]a\b", r"\bcontinuar\b", r"\bretoma\b", r"\bseguimos\b")),
    (CopilotIntent.REVIEW, (r"\b(?:revisa|revisar|audita|auditar|verifica|verificar|eval[uú]a|critica|analiza|analizar)\b",)),
    (CopilotIntent.RESEARCH, (r"\b(?:investiga|investigar|busca|buscar|documenta|documentar|fuentes|referencias)\b",)),
    (CopilotIntent.EXPLORE, (r"\b(?:explora|explorar|alternativas|opciones|escenarios|ideas|posibilidades)\b",)),
    (CopilotIntent.PREPARE_ACTION, (r"\b(?:prepara|preparar|planifica|planificar|organiza|organizar|propuesta de plan)\b",)),
    (CopilotIntent.DESIGN_INTENT, (r"\b(?:diseña|diseñar|diseño|proyecta|proyectar|plantea|plantear|conceptualiza|conceptualizar)\b",)),
    (CopilotIntent.EXECUTE, (r"\b(?:ejecuta|ejecutar|genera|generar|crea|crear|construye|construir|produce|producir|lanza|correr|corre)\b",)),
)

def classify_intent(text: str) -> IntentAssessment:
    """Classify user text conservatively; mixed action signals become clarification."""
    normalized = (text or "").strip().lower()
    if not normalized:
        return IntentAssessment(
            intent=CopilotIntent.CONVERSE,
            confidence=1.0,
            rationale="empty_input_defaults_to_conversation",
        )

    # Explicit continuation should resume the current task rather than be
    # confused by descriptive words such as "audit" or "review" in its scope.
    continue_patterns = _RULES[0][1]
    if any(re.search(pattern, normalized) for pattern in continue_patterns):
        return IntentAssessment(
            intent=CopilotIntent.CONTINUE,
            confidence=0.90,
            rationale="explicit_continue_command",
        )

    matched: list[CopilotIntent] = []
    for intent, patterns in _RULES[1:]:
        if any(re.search(pattern, normalized) for pattern in patterns):
            matched.append(intent)

    if not matched:
        return IntentAssessment(
            intent=CopilotIntent.CONVERSE,
            confidence=0.70,
            rationale="no_action_pattern_detected",
        )

    # Execution paired with non-execution requests is deliberately ambiguous.
    if CopilotIntent.EXECUTE in matched and len(matched) > 1:
        return IntentAssessment(
            intent=CopilotIntent.EXECUTE,
            confidence=0.45,
            ambiguous=True,
            clarification_question="¿Quieres que ejecute la operación ahora o primero que investigue, revise o prepare la propuesta?",
            rationale="mixed_execution_and_other_intent_signals",
        )

    # If multiple non-execution signals are present, route to the strongest
    # conservative review/prepare path and expose the mixed intent.
    if len(matched) > 1:
        selected = matched[0]
        return IntentAssessment(
            intent=selected,
            confidence=0.50,
            ambiguous=True,
            clarification_question="¿Qué quieres que haga primero: continuar, revisar, investigar, explorar o preparar?",
            rationale="multiple_non_execution_intent_signals",
        )

    return IntentAssessment(
        intent=matched[0],
        confidence=0.85,
        rationale="single_rule_match",
    )
