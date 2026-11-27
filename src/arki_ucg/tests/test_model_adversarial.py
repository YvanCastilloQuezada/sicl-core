import math
import pytest

from arki_ucg.model import CommandParameters, CommandContext, CommandDefinition


def complete_command(**kwargs):
    levels = {
        "L1_domain": "ARCHITECTURE",
        "L2_family": "DESIGN",
        "L3_intent": "CREATE",
        "L4_operation": "GENERATE",
        "L5_entity": "BUILDING",
        "L6_type": "RESIDENTIAL",
        "L7_mode": "PARAMETRIC",
        "L8_output": "3D",
    }
    levels.update(kwargs)
    return CommandDefinition(**levels)


def test_parameters_external_mutation_is_blocked():
    source = {"a": [1, 2]}
    params = CommandParameters(source)

    source["a"].append(3)

    assert params.values["a"] == (1, 2)


def test_parameters_direct_mutation_is_blocked():
    params = CommandParameters({"a": 1})

    with pytest.raises(TypeError):
        params.values["a"] = 2


def test_context_external_mutation_is_blocked():
    source = {"nested": {"x": [1]}}
    context = CommandContext(values=source)

    source["nested"]["x"].append(2)

    assert context.values["nested"]["x"] == (1,)


def test_context_direct_mutation_is_blocked():
    context = CommandContext(values={"a": 1})

    with pytest.raises(TypeError):
        context.values["a"] = 2


def test_command_to_dict_is_deep_independent():
    command = complete_command(
        parameters=CommandParameters({"items": [{"x": 1}]}),
        context=CommandContext(values={"nested": {"a": [2]}}),
    )

    result = command.to_dict()
    result["parameters"]["items"][0]["x"] = 999
    result["context"]["values"]["nested"]["a"].append(999)

    fresh = command.to_dict()

    assert fresh["parameters"]["items"][0]["x"] == 1
    assert fresh["context"]["values"]["nested"]["a"] == [2]


def test_parameters_reject_cycle():
    source = {}
    source["cycle"] = source

    with pytest.raises(ValueError):
        CommandParameters(source)


def test_context_rejects_non_finite_float():
    with pytest.raises(ValueError):
        CommandContext(values={"value": math.nan})


def test_parameters_reject_arbitrary_object():
    with pytest.raises(ValueError):
        CommandParameters({"object": object()})


def test_semantic_identity_ignores_parameter_mutation_attempt():
    command = complete_command(parameters=CommandParameters({"x": [1]}))
    before = command.semantic_identity

    with pytest.raises(TypeError):
        command.parameters.values["x"] = [2]

    assert command.semantic_identity == before
