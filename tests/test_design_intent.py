from sicl.design_intent import confirm_intent, interpret_intent, intent_to_generation_input


def test_interpretation_is_deterministic_and_not_a_decision() -> None:
    result = interpret_intent("Quiero una masa compacta, maximizar espacio abierto y evitar patios excesivos.", project_id="UPAO-001", spatial_scope="edificacion")
    assert result["decision_created"] is False
    assert result["human_confirmation_required"] is True
    assert {item["kind"] for item in result["suggestions"]} >= {"CONSTRAINT", "OBJECTIVE", "DESIGN_IDEA"}
    assert all(item["provenance"]["interpreter"] == "SICL_DETERMINISTIC_INTENT_RULES" for item in result["suggestions"])


def test_confirmation_is_explicit_and_generation_input_requires_adoption() -> None:
    result = interpret_intent("Prefiero privacidad.", project_id="UPAO-001")
    adopted, event = confirm_intent("UPAO-001", result, [result["suggestions"][0]["intent_id"]], "human-architect")
    assert adopted["adoption"] == "HUMAN_CONFIRMED"
    assert adopted["decision_created"] is False
    assert event["type"] == "HUMAN_INTENT_ADOPTED"
    assert intent_to_generation_input(adopted)["intent_ids"]


def test_system_cannot_confirm_intent() -> None:
    result = interpret_intent("Quiero privacidad.")
    try:
        confirm_intent("UPAO-001", result, [result["suggestions"][0]["intent_id"]], "SYSTEM")
    except ValueError as error:
        assert str(error) == "HUMAN_AUTHORITY_REQUIRED"
    else:
        raise AssertionError("SYSTEM must not confirm design intent")
