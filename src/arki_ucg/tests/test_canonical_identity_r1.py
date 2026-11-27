"""Adversarial contract tests for UCG Canonical Identity R1.

These tests define the strict identity contract.
They intentionally do not modify or replace legacy identity behavior.
"""

from dataclasses import replace

import pytest

from arki_ucg.canonical_identity import (
    CANONICAL_IDENTITY_CONTRACT_VERSION,
    FINGERPRINT_CONTRACT_VERSION,
    CanonicalSemanticIdentity,
    create_canonical_identity,
    verify_canonical_identity,
)


VALID_LEVELS = (
    "ARQUITECTURA",
    "URBANISMO",
    "PRODUCIR",
    "GENERAR",
    "PLANO",
    "PLANTA",
    "ARQUITECTONICA",
    "AMOBLADA",
)


@pytest.mark.parametrize(
    "levels",
    [
        VALID_LEVELS,
        (
            "NIÑO",
            "URBANISMO",
            "PRODUCIR",
            "GENERAR",
            "PLANO",
            "PLANTA",
            "ARQUITECTONICA",
            "AMOBLADA",
        ),
        (
            "NINO",
            "URBANISMO",
            "PRODUCIR",
            "GENERAR",
            "PLANO",
            "PLANTA",
            "ARQUITECTONICA",
            "AMOBLADA",
        ),
        (
            "PLANO URBANO",
            "URBANISMO",
            "PRODUCIR",
            "GENERAR",
            "PLANO",
            "PLANTA",
            "ARQUITECTONICA",
            "AMOBLADA",
        ),
        (
            "AÑO 2026",
            "URBANISMO",
            "PRODUCIR",
            "GENERAR",
            "PLANO",
            "PLANTA",
            "ARQUITECTONICA",
            "AMOBLADA",
        ),
    ],
)
def test_valid_canonical_identity_is_created_and_verified(levels):
    identity = create_canonical_identity(levels)

    assert type(identity) is CanonicalSemanticIdentity
    assert identity.levels == levels
    assert identity.contract_version == CANONICAL_IDENTITY_CONTRACT_VERSION
    assert identity.fingerprint_version == FINGERPRINT_CONTRACT_VERSION
    assert verify_canonical_identity(identity).valid


def test_identity_requires_exactly_eight_levels():
    with pytest.raises(ValueError):
        create_canonical_identity(VALID_LEVELS[:7])

    with pytest.raises(ValueError):
        create_canonical_identity(VALID_LEVELS + ("EXTRA",))


@pytest.mark.parametrize(
    "bad_text",
    [
        "",
        " ",
        " ARQUITECTURA",
        "ARQUITECTURA ",
        "PLANO  URBANO",
        "arquitectura",
        "ÁREA",
        "Ü",
        "PLANO-URBANO",
        "PLANO/URBANO",
        "PLANO.URBANO",
        "PLANO+URBANO",
        "M²",
        "M³",
        "ＡＲＫＩ",
        "АRKI",       # Cyrillic A
        "ΑRKI",       # Greek Alpha
        "N\u0303INO",  # N + combining tilde
        "ARQUI\tTECTURA",
        "ARQUI\nTECTURA",
        "PLANO\u00A0URBANO",  # NBSP
        "AR\u200BKI",           # zero-width space
        "\ufeffARKI",          # BOM
    ],
)
def test_noncanonical_level_is_rejected(bad_text):
    levels = list(VALID_LEVELS)
    levels[0] = bad_text

    with pytest.raises(ValueError):
        create_canonical_identity(tuple(levels))


@pytest.mark.parametrize(
    "bad_value",
    [
        None,
        12,
        1.5,
        True,
        [],
        {},
    ],
)
def test_non_string_level_is_rejected(bad_value):
    levels = list(VALID_LEVELS)
    levels[0] = bad_value

    with pytest.raises(ValueError):
        create_canonical_identity(tuple(levels))


def test_nino_and_nino_with_tilde_are_distinct_identities():
    a = list(VALID_LEVELS)
    b = list(VALID_LEVELS)

    a[0] = "NIÑO"
    b[0] = "NINO"

    identity_a = create_canonical_identity(tuple(a))
    identity_b = create_canonical_identity(tuple(b))

    assert identity_a.levels != identity_b.levels
    assert identity_a.fingerprint != identity_b.fingerprint


def test_identical_identity_has_identical_fingerprint():
    first = create_canonical_identity(VALID_LEVELS)
    second = create_canonical_identity(tuple(VALID_LEVELS))

    assert first.levels == second.levels
    assert first.fingerprint == second.fingerprint


def test_single_level_change_changes_fingerprint():
    original = create_canonical_identity(VALID_LEVELS)

    changed_levels = list(VALID_LEVELS)
    changed_levels[7] = "SIN AMOBLAR"

    changed = create_canonical_identity(tuple(changed_levels))

    assert original.fingerprint != changed.fingerprint


def test_level_order_is_identity_significant():
    original = create_canonical_identity(VALID_LEVELS)

    reordered_levels = (
        VALID_LEVELS[1],
        VALID_LEVELS[0],
        *VALID_LEVELS[2:],
    )

    reordered = create_canonical_identity(reordered_levels)

    assert original.levels != reordered.levels
    assert original.fingerprint != reordered.fingerprint


def test_fingerprint_tampering_is_detected():
    identity = create_canonical_identity(VALID_LEVELS)
    tampered = replace(identity, fingerprint="0" * 64)

    assert not verify_canonical_identity(tampered).valid


def test_level_tampering_is_detected():
    identity = create_canonical_identity(VALID_LEVELS)

    altered_levels = list(identity.levels)
    altered_levels[0] = "URBANISMO"

    tampered = replace(identity, levels=tuple(altered_levels))

    assert not verify_canonical_identity(tampered).valid


def test_contract_version_tampering_is_detected():
    identity = create_canonical_identity(VALID_LEVELS)
    tampered = replace(identity, contract_version="UNKNOWN-CONTRACT")

    assert not verify_canonical_identity(tampered).valid


def test_fingerprint_version_tampering_is_detected():
    identity = create_canonical_identity(VALID_LEVELS)
    tampered = replace(identity, fingerprint_version="UNKNOWN-FINGERPRINT")

    assert not verify_canonical_identity(tampered).valid


def test_wrong_identity_object_type_is_rejected():
    assert not verify_canonical_identity(None).valid
    assert not verify_canonical_identity({}).valid
    assert not verify_canonical_identity("identity").valid


def test_identity_has_exactly_eight_semantic_levels():
    identity = create_canonical_identity(VALID_LEVELS)

    assert type(identity.levels) is tuple
    assert len(identity.levels) == 8
    assert all(type(level) is str for level in identity.levels)
