"""Independent adversarial checks for canonical UCG identity R1."""

from dataclasses import replace

import pytest

from arki_ucg.canonical_identity import (
    CanonicalSemanticIdentity,
    create_canonical_identity,
    verify_canonical_identity,
)


LEVELS_VECTOR = (
    "ARQUITECTURA",
    "URBANISMO",
    "PRODUCIR",
    "GENERAR",
    "PLANO",
    "PLANTA",
    "ARQUITECTONICA",
    "AMOBLADA",
)

EXPECTED_FINGERPRINT = (
    "6d7799d9d21de85cf48e5142523a71168ac90e31f1817a58067f0b0ba96e9401"
)


def test_fingerprint_matches_independent_golden_vector():
    identity = create_canonical_identity(LEVELS_VECTOR)
    assert identity.fingerprint == EXPECTED_FINGERPRINT


@pytest.mark.parametrize(
    "field,value",
    [
        ("levels", list(LEVELS_VECTOR)),
        ("levels", None),
        ("levels", "NOT-A-TUPLE"),
        ("fingerprint", None),
        ("fingerprint", 123),
        ("fingerprint", True),
        ("contract_version", None),
        ("contract_version", 99),
        ("fingerprint_version", None),
        ("fingerprint_version", []),
    ],
)
def test_malformed_fields_fail_closed(field, value):
    identity = create_canonical_identity(LEVELS_VECTOR)
    malformed = replace(identity, **{field: value})
    assert not verify_canonical_identity(malformed).valid


def test_short_fingerprint_rejected():
    identity = create_canonical_identity(LEVELS_VECTOR)
    tampered = replace(identity, fingerprint="abc")
    assert not verify_canonical_identity(tampered).valid


def test_uppercase_hex_but_wrong_fingerprint_rejected():
    identity = create_canonical_identity(LEVELS_VECTOR)
    tampered = replace(identity, fingerprint="A" * 64)
    assert not verify_canonical_identity(tampered).valid


def test_frozen_dataclass_bypass_tampering_is_detected():
    identity = create_canonical_identity(LEVELS_VECTOR)

    # Simulate hostile mutation bypassing dataclass frozen protection.
    object.__setattr__(identity, "levels", ("ALTERED",) + identity.levels[1:])

    assert not verify_canonical_identity(identity).valid


def test_frozen_dataclass_fingerprint_bypass_is_detected():
    identity = create_canonical_identity(LEVELS_VECTOR)

    object.__setattr__(identity, "fingerprint", "f" * 64)

    assert not verify_canonical_identity(identity).valid


def test_recomputed_fingerprint_cannot_make_noncanonical_levels_valid():
    identity = create_canonical_identity(LEVELS_VECTOR)

    altered_levels = ("arquitectura",) + identity.levels[1:]
    forged = replace(identity, levels=altered_levels)

    # Even if the attacker knows the object structure, canonical validation
    # must reject the altered text before accepting the fingerprint.
    assert not verify_canonical_identity(forged).valid


def test_exact_identity_type_boundary():
    class DerivedIdentity(CanonicalSemanticIdentity):
        pass

    identity = create_canonical_identity(LEVELS_VECTOR)

    derived = DerivedIdentity(
        levels=identity.levels,
        contract_version=identity.contract_version,
        fingerprint_version=identity.fingerprint_version,
        fingerprint=identity.fingerprint,
    )

    assert not verify_canonical_identity(derived).valid


def test_recalculated_fingerprint_still_rejects_noncanonical_identity():
    import hashlib
    import json

    identity = create_canonical_identity(LEVELS_VECTOR)

    altered_levels = ("arquitectura",) + identity.levels[1:]

    payload = {
        "levels": list(altered_levels),
        "contract_version": identity.contract_version,
        "fingerprint_version": identity.fingerprint_version,
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    independently_recalculated_fingerprint = hashlib.sha256(encoded).hexdigest()

    forged = replace(
        identity,
        levels=altered_levels,
        fingerprint=independently_recalculated_fingerprint,
    )

    assert len(independently_recalculated_fingerprint) == 64
    assert not verify_canonical_identity(forged).valid
