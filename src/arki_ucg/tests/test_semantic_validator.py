import pytest

from arki_ucg import CommandDefinition
from arki_ucg.semantic_validator import (
    CHAR_POLICY_CONTRACT,
    validate_semantic_text,
    validate_command_semantics,
)


def valid_command(**overrides):
    data = {
        "L1_domain": "ARQUITECTURA",
        "L2_family": "DOCUMENTACION",
        "L3_intent": "PRODUCIR",
        "L4_operation": "GENERAR",
        "L5_entity": "PLANO",
        "L6_type": "PLANTA",
        "L7_mode": "ARQUITECTONICA",
        "L8_output": "AMOBLADA",
    }
    data.update(overrides)
    return CommandDefinition(**data)


def issue_codes(result):
    return {issue.code for issue in result.issues}


def test_policy_contract():
    assert CHAR_POLICY_CONTRACT == "UCG-CHAR-01-EXPERIMENTAL"


@pytest.mark.parametrize("value", [None, 12, 1.5, True, [], {}])
def test_non_string_rejected(value):
    result = validate_semantic_text(value)
    assert not result.valid
    assert "SEMANTIC_TEXT_TYPE_INVALID" in issue_codes(result)


@pytest.mark.parametrize(
    "value",
    [
        "\t",
        "\n",
        "\u200b",  # zero-width space
        "\ufeff",   # BOM
        "\ud800",   # surrogate
        "\ue000",   # private use
        "\u0378",   # unassigned
        "\u2028",   # line separator
        "\u2029",   # paragraph separator
        "\u20dd",   # enclosing mark (Me)
    ],
)
def test_forbidden_categories_rejected(value):
    result = validate_semantic_text(value)
    assert not result.valid
    assert "SEMANTIC_UNICODE_CATEGORY_FORBIDDEN" in issue_codes(result)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "\u00a0",
        "\u2003",
        " \u00a0\u2003 ",
    ],
)
def test_empty_after_normalization_rejected(value):
    result = validate_semantic_text(value)
    assert not result.valid
    assert "SEMANTIC_FIELD_EMPTY_AFTER_NORMALIZATION" in issue_codes(result)


def test_ascii_case_normalization_is_accepted():
    assert validate_semantic_text("arquitectura").valid
    assert validate_semantic_text(" ARQUITECTURA ").valid


def test_nfc_equivalent_text_accepted():
    assert validate_semantic_text("café").valid
    assert validate_semantic_text("cafe\u0301").valid


def test_leading_mn_rejected():
    result = validate_semantic_text("\u0301ARKI")
    assert not result.valid
    assert "SEMANTIC_COMBINING_MARK_LEADING" in issue_codes(result)


def test_mn_only_rejected():
    result = validate_semantic_text("\u0301")
    assert not result.valid
    assert "SEMANTIC_COMBINING_MARK_LEADING" in issue_codes(result)


def test_attached_mn_provisionally_accepted():
    assert validate_semantic_text("cafe\u0301").valid


def test_multiple_attached_mn_provisionally_accepted():
    assert validate_semantic_text("A\u0301\u0308").valid


def test_mc_accepted():
    assert validate_semantic_text("\u093e").valid


@pytest.mark.parametrize(
    "value",
    [
        "ARKI-01",
        "PLANO / F8",
        "5D",
        "€",
        "∑",
        "²",
        "ＡＲＫＩ",
        "А",  # Cyrillic A; preserved, not confusable-folded
    ],
)
def test_letters_numbers_punctuation_symbols_preserved(value):
    assert validate_semantic_text(value).valid


def test_command_semantic_validation_accepts_valid_command():
    assert validate_command_semantics(valid_command()).valid


@pytest.mark.parametrize(
    "level,value,expected_code",
    [
        ("L1_domain", "\u0301ARKI", "SEMANTIC_COMBINING_MARK_LEADING"),
        ("L2_family", "\ue000", "SEMANTIC_UNICODE_CATEGORY_FORBIDDEN"),
        ("L3_intent", "\u0378", "SEMANTIC_UNICODE_CATEGORY_FORBIDDEN"),
        ("L4_operation", "\u2028", "SEMANTIC_UNICODE_CATEGORY_FORBIDDEN"),
        ("L5_entity", "   ", "SEMANTIC_FIELD_EMPTY_AFTER_NORMALIZATION"),
    ],
)
def test_command_level_validation_reports_level(level, value, expected_code):
    result = validate_command_semantics(valid_command(**{level: value}))
    assert not result.valid
    assert expected_code in issue_codes(result)
    assert any(issue.level == level for issue in result.issues)


def test_incomplete_command_uses_existing_structural_validation():
    result = validate_command_semantics(valid_command(L8_output=None))
    assert not result.valid
    assert any(issue.code == "LEVEL_MISSING" for issue in result.issues)


def test_parameters_and_context_do_not_enter_semantic_validation():
    command = valid_command()
    result = validate_command_semantics(command)
    assert result.valid
