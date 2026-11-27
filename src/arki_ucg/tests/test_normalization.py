"""Tests for UCG-NORM-02 Spanish semantic text normalization."""

import unicodedata
import pytest

from arki_ucg.normalization import (
    CONTRACT_VERSION,
    NormalizationError,
    normalize_semantic_text,
)


def test_contract_version():
    assert CONTRACT_VERSION == "UCG-NORM-02"


@pytest.mark.parametrize("value", [None, 12, 1.5, True, [], {}])
def test_non_string_rejected(value):
    with pytest.raises(NormalizationError):
        normalize_semantic_text(value)


@pytest.mark.parametrize("value", [
    "\x00", "\n", "\t", "\u200b", "\u200d", "\ufeff",
    "\ud800", "\ue000", "\u0378", "\u2028", "\u2029", "\u20dd",
])
def test_forbidden_characters_rejected(value):
    with pytest.raises(NormalizationError):
        normalize_semantic_text(value)


@pytest.mark.parametrize(("source", "expected"), [
    ("arquitectura", "ARQUITECTURA"),
    ("Arquitectura", "ARQUITECTURA"),
    ("ÁREA", "AREA"),
    ("área", "AREA"),
    ("café", "CAFE"),
    ("ÁRBOL", "ARBOL"),
    ("árbol", "ARBOL"),
    ("niño", "NIÑO"),
    ("NIÑO", "NIÑO"),
    ("ÑANDÚ", "ÑANDU"),
    ("ñandú", "ÑANDU"),
    ("m²", "M2"),
    ("M²", "M2"),
    ("m³", "M3"),
    ("M³", "M3"),
    ("m2", "M2"),
    ("m3", "M3"),
    ("PLANO   URBANO", "PLANO URBANO"),
    ("  plano urbano  ", "PLANO URBANO"),
    ("PLANO / F8", "PLANO / F8"),
    ("ARKI-01", "ARKI-01"),
    ("5D", "5D"),
    ("€ ∑", "€ ∑"),
])
def test_policy_examples(source, expected):
    assert normalize_semantic_text(source) == expected


def test_unicode_spaces_compacted():
    assert normalize_semantic_text("PLANO\u00a0URBANO") == "PLANO URBANO"
    assert normalize_semantic_text("PLANO\u2003URBANO") == "PLANO URBANO"


def test_nfc_equivalent_input_normalizes_identically():
    composed = "café"
    decomposed = "cafe\u0301"
    assert normalize_semantic_text(composed) == normalize_semantic_text(decomposed)


def test_nfc_output():
    value = normalize_semantic_text("cafe\u0301")
    assert unicodedata.is_normalized("NFC", value)


def test_intentional_accent_collision():
    # Accent removal is intentional in semantic text.
    assert normalize_semantic_text("ÁREA") == normalize_semantic_text("AREA")


def test_n_and_n_tilde_are_not_collapsed():
    assert normalize_semantic_text("NINO") != normalize_semantic_text("NIÑO")


def test_punctuation_is_preserved():
    assert normalize_semantic_text("A-B/C: D; E.") == "A-B/C: D; E."


def test_other_scripts_are_not_transliterated():
    value = "Привет"
    assert normalize_semantic_text(value) == value


def test_fullwidth_characters_are_not_compatibility_folded():
    value = "ＡＲＫＩ"
    assert normalize_semantic_text(value) == value


def test_normalization_is_idempotent():
    samples = [
        "ÁREA",
        "árbol",
        "niño",
        "ÑANDÚ",
        "m²",
        "m³",
        "  PLANO   URBANO  ",
        "A-B/C: D; E.",
        "Привет",
        "ＡＲＫＩ",
    ]
    for sample in samples:
        once = normalize_semantic_text(sample)
        twice = normalize_semantic_text(once)
        assert once == twice


def test_deterministic():
    value = "  área  de   diseño m²  "
    assert normalize_semantic_text(value) == normalize_semantic_text(value)
