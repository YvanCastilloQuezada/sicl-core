import pytest

from sicl.copilot_contract import CopilotIntent
from sicl.copilot_intent import classify_intent


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Hola ARKI, ¿qué opinas de esta idea?", CopilotIntent.CONVERSE),
        ("Investiga centros de salud en clima tropical", CopilotIntent.RESEARCH),
        ("Explora tres alternativas de implantación", CopilotIntent.EXPLORE),
        ("Prepara un plan de análisis del terreno", CopilotIntent.PREPARE_ACTION),
        ("Quiero diseñar un centro de salud", CopilotIntent.DESIGN_INTENT),
        ("Continúa con la auditoría", CopilotIntent.CONTINUE),
        ("Revisa este plano", CopilotIntent.REVIEW),
        ("Genera 12 alternativas", CopilotIntent.EXECUTE),
    ],
)
def test_basic_intent_routes(message, expected):
    result = classify_intent(message)
    assert result.intent is expected
    assert not result.ambiguous


def test_execution_mixed_with_research_requires_clarification():
    result = classify_intent("Investiga y genera una propuesta")
    assert result.intent is CopilotIntent.EXECUTE
    assert result.ambiguous
    assert result.clarification_question


def test_mixed_non_execution_intents_require_clarification():
    result = classify_intent("Revisa e investiga este proyecto")
    assert result.ambiguous
    assert result.clarification_question


def test_empty_text_routes_to_conversation():
    result = classify_intent("")
    assert result.intent is CopilotIntent.CONVERSE
    assert not result.ambiguous


def test_classifier_does_not_authorize_execution():
    # Intent classification is not an action-gate decision.
    result = classify_intent("Genera un modelo")
    assert result.intent is CopilotIntent.EXECUTE
    assert result.confidence < 1.0
