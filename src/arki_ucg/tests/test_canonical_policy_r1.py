import pytest

from arki_ucg.canonical_policy import (
    CANONICAL_POLICY_VERSION,
    CanonicalTextError,
    is_canonical_text,
    validate_canonical_text,
)


@pytest.mark.parametrize(
    "value",
    [
        "ARKI",
        "ARQUITECTURA",
        "PLAN URBANO",
        "ÑANDU",
        "N",
        "Ñ",
        "PLAN 2026",
        "5D",
        "L1 DOMAIN",
        "A B C",
    ],
)
def test_r1_accepts_canonical_text(value):
    assert validate_canonical_text(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        " ARKI",
        "ARKI ",
        "A  B",
        "a",
        "arquitectura",
        "ÁREA",
        "É",
        "Í",
        "Ó",
        "Ú",
        "N\u0303",
        "M²",
        "M³",
        "PLAN-URBANO",
        "A+B",
        "A.B",
        "A/B",
        "Ａ",
        "Ж",
        "Α",
        "A\u00A0B",
        "A\u2003B",
        "A\nB",
        "\t",
    ],
)
def test_r1_rejects_noncanonical_text(value):
    with pytest.raises(CanonicalTextError):
        validate_canonical_text(value)


@pytest.mark.parametrize(
    "value",
    [
        None,
        123,
        1.5,
        True,
        [],
        {},
        ("ARKI",),
    ],
)
def test_r1_rejects_non_exact_string_types(value):
    with pytest.raises(CanonicalTextError):
        validate_canonical_text(value)


def test_r1_preserves_enye_as_distinct_character():
    assert validate_canonical_text("N") == "N"
    assert validate_canonical_text("Ñ") == "Ñ"
    assert "N" != "Ñ"


def test_r1_does_not_normalize_input():
    with pytest.raises(CanonicalTextError):
        validate_canonical_text("arquitectura")

    with pytest.raises(CanonicalTextError):
        validate_canonical_text("ÁREA")


def test_r1_boolean_helper():
    assert is_canonical_text("ARKI")
    assert is_canonical_text("ÑANDU")
    assert not is_canonical_text("arki")
    assert not is_canonical_text("ÁREA")
    assert not is_canonical_text("A  B")
    assert not is_canonical_text(None)


def test_r1_policy_version_is_explicit():
    assert CANONICAL_POLICY_VERSION == "UCG-CANONICAL-POLICY-R1"
