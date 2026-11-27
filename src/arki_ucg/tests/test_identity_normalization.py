"""R5-H-07 — Semantic identity uses UCG-NORM-02."""

import pytest

from arki_ucg.model import CommandDefinition
from arki_ucg.normalization import NormalizationError


def make_command(**overrides):
    levels = {
        "L1_domain": "ARQUITECTURA",
        "L2_family": "MODELADO",
        "L3_intent": "GENERAR",
        "L4_operation": "CREAR",
        "L5_entity": "AREA",
        "L6_type": "SUPERFICIE",
        "L7_mode": "SINGLE",
        "L8_output": "M2",
    }
    levels.update(overrides)
    return CommandDefinition(**levels)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("ÁREA", "AREA"),
        ("área", "AREA"),
        ("m²", "M2"),
        ("m³", "M3"),
        ("niño", "NIÑO"),
        ("PLANO   URBANO", " plano urbano "),
    ],
)
def test_semantic_identity_uses_ucg_norm_02(left, right):
    a = make_command(L5_entity=left)
    b = make_command(L5_entity=right)
    assert a.semantic_identity == b.semantic_identity


def test_nino_and_nino_without_enye_are_distinct():
    a = make_command(L5_entity="NIÑO")
    b = make_command(L5_entity="NINO")
    assert a.semantic_identity != b.semantic_identity


def test_identity_normalizes_all_eight_levels():
    a = make_command(
        L1_domain="área",
        L2_family=" niño ",
        L3_intent="GENERAR",
        L4_operation="crear",
        L5_entity="m²",
        L6_type="superficie",
        L7_mode="single",
        L8_output="m³",
    )
    b = make_command(
        L1_domain="AREA",
        L2_family="NIÑO",
        L3_intent="GENERAR",
        L4_operation="CREAR",
        L5_entity="M2",
        L6_type="SUPERFICIE",
        L7_mode="SINGLE",
        L8_output="M3",
    )
    assert a.semantic_identity == b.semantic_identity


def test_parameters_do_not_change_identity():
    from arki_ucg.model import CommandParameters

    a = make_command()
    b = make_command(
        parameters=CommandParameters(
            {"area": 120.0, "height": 10.0}
        )
    )
    assert a.semantic_identity == b.semantic_identity


def test_context_does_not_change_identity():
    from arki_ucg.model import CommandContext

    a = make_command()
    b = make_command(
        context=CommandContext(
            project_id="PROJECT-001",
            lifecycle_phase="PREINVERSIÓN",
            scale="EDIFICIO",
            selection="ZONA-A",
        )
    )
    assert a.semantic_identity == b.semantic_identity


def test_identity_rejects_forbidden_unicode():
    a = make_command(L5_entity="AREA\u200b")
    with pytest.raises(NormalizationError):
        _ = a.semantic_identity


def test_incomplete_identity_still_fails():
    a = CommandDefinition(
        L1_domain="ARQUITECTURA",
        L2_family="MODELADO",
        L3_intent="GENERAR",
        L4_operation="CREAR",
        L5_entity="AREA",
        L6_type="SUPERFICIE",
        L7_mode="SINGLE",
        L8_output=None,
    )
    with pytest.raises(ValueError):
        _ = a.semantic_identity


def test_semantic_identity_is_idempotent():
    from arki_ucg.model import LEVELS

    a = make_command(L5_entity="área   m²")
    first = a.semantic_identity

    normalized_command = CommandDefinition(
        **dict(zip(LEVELS, first))
    )
    second = normalized_command.semantic_identity

    assert first == second
