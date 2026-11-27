import pytest

from arki_ucg import CommandDefinition
from arki_ucg.validated_identity import (
    IDENTITY_CONTRACT_VERSION,
    NORMALIZATION_VERSION,
    ValidatedSemanticIdentity,
    create_validated_identity,
    verify_validated_identity,
)


def command(**overrides):
    values = {
        "L1_domain": "ARQUITECTURA",
        "L2_family": "DOCUMENTACION",
        "L3_intent": "PRODUCIR",
        "L4_operation": "GENERAR",
        "L5_entity": "PLANO",
        "L6_type": "PLANTA",
        "L7_mode": "ARQUITECTONICA",
        "L8_output": "AMOBLADA",
    }
    values.update(overrides)
    return CommandDefinition(**values)


# ------------------------------------------------------------
# G1 — Creación y verificación
# ------------------------------------------------------------

def test_valid_identity_is_created_and_verified():
    identity = create_validated_identity(command())

    assert isinstance(identity, ValidatedSemanticIdentity)
    assert len(identity.levels) == 8
    assert verify_validated_identity(identity).valid


# ------------------------------------------------------------
# G2 — Determinismo
# ------------------------------------------------------------

def test_same_semantic_input_produces_same_identity_fingerprint():
    a = create_validated_identity(command())
    b = create_validated_identity(command())

    assert a.levels == b.levels
    assert a.fingerprint == b.fingerprint


# ------------------------------------------------------------
# G3 — Canonicalización
# ------------------------------------------------------------

def test_identity_levels_are_canonicalized():
    identity = create_validated_identity(
        command(
            L1_domain=" arquitectura ",
            L2_family="documentacion",
        )
    )

    assert identity.levels[0] == "ARQUITECTURA"
    assert identity.levels[1] == "DOCUMENTACION"
    assert verify_validated_identity(identity).valid


# ------------------------------------------------------------
# G4 — Snapshot independiente
# ------------------------------------------------------------

def test_identity_snapshot_does_not_follow_source_mutation():
    source = command()
    identity = create_validated_identity(source)

    object.__setattr__(source, "L1_domain", "ALTERADO")

    assert identity.levels[0] == "ARQUITECTURA"
    assert verify_validated_identity(identity).valid


# ------------------------------------------------------------
# G5 — Rechazo de incompleto
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "field,value",
    [
        ("L1_domain", None),
        ("L3_intent", ""),
        ("L5_entity", "   "),
        ("L8_output", None),
    ],
)
def test_incomplete_identity_is_rejected(field, value):
    with pytest.raises((ValueError, TypeError)):
        create_validated_identity(command(**{field: value}))


# ------------------------------------------------------------
# G6 — Rechazo de semántica inválida
# ------------------------------------------------------------

def test_identity_with_leading_combining_mark_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        create_validated_identity(command(L1_domain="\u0301ARKI"))


# ------------------------------------------------------------
# G7 — Objeto externo incorrecto
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        None,
        "identity",
        ("A", "B"),
        {},
        [],
    ],
)
def test_wrong_object_type_is_rejected(value):
    result = verify_validated_identity(value)

    assert not result.valid


# ------------------------------------------------------------
# G8 — Alteración del fingerprint
# ------------------------------------------------------------

def test_modified_fingerprint_is_rejected():
    identity = create_validated_identity(command())
    object.__setattr__(identity, "fingerprint", "0" * 64)

    result = verify_validated_identity(identity)

    assert not result.valid
    assert "IDENTITY_FINGERPRINT_MISMATCH" in [
        issue.code for issue in result.issues
    ]


# ------------------------------------------------------------
# G9 — Alteración del snapshot
# ------------------------------------------------------------

def test_modified_snapshot_is_rejected():
    identity = create_validated_identity(command())

    object.__setattr__(
        identity,
        "levels",
        ("DOMINIO ALTERADO",) + identity.levels[1:],
    )

    result = verify_validated_identity(identity)

    assert not result.valid


# ------------------------------------------------------------
# G10 — Versión de contrato incompatible
# ------------------------------------------------------------

def test_unsupported_identity_contract_is_rejected():
    identity = create_validated_identity(command())

    object.__setattr__(
        identity,
        "contract_version",
        "UCG-UNKNOWN-VERSION",
    )

    result = verify_validated_identity(identity)

    assert not result.valid
    assert "IDENTITY_CONTRACT_VERSION_UNSUPPORTED" in [
        issue.code for issue in result.issues
    ]


# ------------------------------------------------------------
# G11 — Versión de normalización incompatible
# ------------------------------------------------------------

def test_unsupported_normalization_version_is_rejected():
    identity = create_validated_identity(command())

    object.__setattr__(
        identity,
        "normalization_version",
        "UCG-NORM-UNKNOWN",
    )

    result = verify_validated_identity(identity)

    assert not result.valid
    assert "IDENTITY_NORMALIZATION_VERSION_UNSUPPORTED" in [
        issue.code for issue in result.issues
    ]


# ------------------------------------------------------------
# G12 — Snapshot con cantidad incorrecta de niveles
# ------------------------------------------------------------

def test_wrong_level_count_is_rejected():
    identity = create_validated_identity(command())

    object.__setattr__(identity, "levels", identity.levels[:7])

    result = verify_validated_identity(identity)

    assert not result.valid
    assert "IDENTITY_LEVELS_SHAPE_INVALID" in [
        issue.code for issue in result.issues
    ]


# ------------------------------------------------------------
# G13 — Nivel no-string
# ------------------------------------------------------------

def test_non_string_level_is_rejected():
    identity = create_validated_identity(command())

    altered = list(identity.levels)
    altered[4] = 123
    object.__setattr__(identity, "levels", tuple(altered))

    result = verify_validated_identity(identity)

    assert not result.valid
    assert "IDENTITY_LEVEL_TYPE_INVALID" in [
        issue.code for issue in result.issues
    ]


# ------------------------------------------------------------
# G14 — Falsificación directa
# ------------------------------------------------------------

def test_directly_constructed_identity_with_fake_fingerprint_is_rejected():
    forged = ValidatedSemanticIdentity(
        levels=(
            "ARQUITECTURA",
            "DOCUMENTACION",
            "PRODUCIR",
            "GENERAR",
            "PLANO",
            "PLANTA",
            "ARQUITECTONICA",
            "AMOBLADA",
        ),
        normalization_version=NORMALIZATION_VERSION,
        contract_version=IDENTITY_CONTRACT_VERSION,
        fingerprint="FAKE",
    )

    result = verify_validated_identity(forged)

    assert not result.valid
    assert "IDENTITY_FINGERPRINT_MISMATCH" in [
        issue.code for issue in result.issues
    ]


# ------------------------------------------------------------
# G15 — Verificación repetible
# ------------------------------------------------------------

def test_identity_verification_is_repeatable():
    identity = create_validated_identity(command())

    a = verify_validated_identity(identity)
    b = verify_validated_identity(identity)

    assert a.valid == b.valid
    assert a.valid


# H-12G-04-R1 — RT006: reject hostile str subclasses at trust boundary.

def test_rt006_subclasses_rejected_regression():
    from arki_ucg import CommandDefinition
    from arki_ucg.validated_identity import (
        create_validated_identity,
        verify_validated_identity,
    )

    BASE = {
        "L1_domain": "ARQUITECTURA",
        "L2_family": "DOCUMENTACION",
        "L3_intent": "PRODUCIR",
        "L4_operation": "GENERAR",
        "L5_entity": "PLANO",
        "L6_type": "PLANTA",
        "L7_mode": "ARQUITECTONICA",
        "L8_output": "AMOBLADA",
    }

    class EvilTranslate(str):
        def translate(self, table):
            return "ARQUITECTURA"

    class EvilIterator(str):
        def __iter__(self):
            return iter("ARQUITECTURA")

    # RT006-A: factory must reject translate-overriding subclasses.
    values_a = dict(BASE)
    values_a["L1_domain"] = EvilTranslate("basura")

    with pytest.raises(ValueError, match="IDENTITY_LEVEL_TYPE_INVALID"):
        create_validated_identity(CommandDefinition(**values_a))

    # RT006-B: factory must reject iterator-overriding subclasses.
    values_b = dict(BASE)
    values_b["L1_domain"] = EvilIterator("basura")

    with pytest.raises(ValueError, match="IDENTITY_LEVEL_TYPE_INVALID"):
        create_validated_identity(CommandDefinition(**values_b))

    # Verifier: altered identity must reject exact-type violations.
    identity = create_validated_identity(CommandDefinition(**BASE))
    altered = list(identity.levels)
    altered[0] = EvilTranslate("basura")

    object.__setattr__(identity, "levels", tuple(altered))

    result = verify_validated_identity(identity)
    assert not result.valid
    assert "IDENTITY_LEVEL_TYPE_INVALID" in [
        issue.code for issue in result.issues
    ]


# RT008 — hostile mutation/type boundaries in identity verification.

def test_rt008_rejects_identity_tuple_subclass():
    identity = create_validated_identity(command())

    class EvilTuple(tuple):
        def __iter__(self):
            raise RuntimeError("hostile iterator")

    object.__setattr__(identity, "levels", EvilTuple(identity.levels))

    result = verify_validated_identity(identity)
    assert not result.valid
    assert "IDENTITY_LEVELS_SHAPE_INVALID" in [
        issue.code for issue in result.issues
    ]


def test_rt008_rejects_hostile_fingerprint_string_subclass():
    identity = create_validated_identity(command())

    class EvilFingerprint(str):
        def __eq__(self, other):
            raise RuntimeError("hostile equality")

    object.__setattr__(identity, "fingerprint", EvilFingerprint("0" * 64))

    result = verify_validated_identity(identity)
    assert not result.valid
    assert "IDENTITY_FINGERPRINT_MISMATCH" in [
        issue.code for issue in result.issues
    ]


def test_rt008_rejects_wrong_contract_version_type():
    identity = create_validated_identity(command())
    object.__setattr__(identity, "contract_version", 123)

    result = verify_validated_identity(identity)
    assert not result.valid
    assert "IDENTITY_CONTRACT_VERSION_TYPE_INVALID" in [
        issue.code for issue in result.issues
    ]


def test_rt008_rejects_wrong_normalization_version_type():
    identity = create_validated_identity(command())
    object.__setattr__(identity, "normalization_version", None)

    result = verify_validated_identity(identity)
    assert not result.valid
    assert "IDENTITY_NORMALIZATION_VERSION_TYPE_INVALID" in [
        issue.code for issue in result.issues
    ]
