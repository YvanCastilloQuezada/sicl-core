import unittest

from arki_ucg import (
    COMMAND_SCHEMA,
    LEVELS,
    CODE_LENGTH,
    ValidationIssue,
    ValidationResult,
    CommandParameters,
    CommandContext,
    CommandDefinition,
    validate_definition,
)


class TestUCG00CFoundation(unittest.TestCase):

    def valid_command(self, **overrides):
        data = {
            "L1_domain": "EXPEDIENTE",
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

    def test_exactly_eight_levels(self):
        self.assertEqual(len(LEVELS), 8)
        self.assertEqual(CODE_LENGTH, 8)

    def test_level_order_is_stable(self):
        self.assertEqual(
            LEVELS,
            (
                "L1_domain",
                "L2_family",
                "L3_intent",
                "L4_operation",
                "L5_entity",
                "L6_type",
                "L7_mode",
                "L8_output",
            ),
        )

    def test_valid_definition_passes(self):
        result = validate_definition(self.valid_command())
        self.assertTrue(result.valid)
        self.assertEqual(result.issues, ())

    def test_missing_level_fails(self):
        command = self.valid_command(L8_output=None)
        result = validate_definition(command)
        self.assertFalse(result.valid)
        self.assertTrue(
            any(issue.level == "L8_output" for issue in result.issues)
        )

    def test_empty_level_fails(self):
        result = validate_definition(
            self.valid_command(L4_operation="   ")
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any(issue.code == "LEVEL_EMPTY" for issue in result.issues)
        )

    def test_non_string_level_fails(self):
        result = validate_definition(
            self.valid_command(L5_entity=123)
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any(issue.code == "LEVEL_TYPE_INVALID" for issue in result.issues)
        )

    def test_semantic_identity_normalizes_case_and_whitespace(self):
        a = self.valid_command(L1_domain=" expediente ")
        b = self.valid_command(L1_domain="EXPEDIENTE")
        self.assertEqual(a.semantic_tuple, b.semantic_tuple)
        self.assertEqual(a.semantic_identity, b.semantic_identity)

    def test_parameters_do_not_change_semantic_identity(self):
        a = self.valid_command()
        b = CommandDefinition(
            **{
                **a.__dict__,
                "parameters": CommandParameters(
                    {"floor": 3, "scale": "1:100"}
                ),
            }
        )
        self.assertEqual(a.semantic_identity, b.semantic_identity)

    def test_context_does_not_change_semantic_identity(self):
        a = self.valid_command()
        b = CommandDefinition(
            **{
                **a.__dict__,
                "context": CommandContext(
                    project_id="P-001",
                    lifecycle_phase="ESTUDIOS",
                    scale="BUILDING",
                    selection="ROOM-02",
                ),
            }
        )
        self.assertEqual(a.semantic_identity, b.semantic_identity)

    def test_incomplete_definition_has_eight_positions(self):
        command = CommandDefinition(L1_domain="ARQUITECTURA")
        self.assertEqual(len(command.level_values), 8)
        self.assertFalse(command.is_complete)

    def test_incomplete_semantic_tuple_raises(self):
        command = CommandDefinition(L1_domain="ARQUITECTURA")
        with self.assertRaises(ValueError):
            _ = command.semantic_tuple

    def test_parameters_are_structured(self):
        command = self.valid_command()
        self.assertIsInstance(command.parameters, CommandParameters)

    def test_context_is_structured(self):
        command = self.valid_command()
        self.assertIsInstance(command.context, CommandContext)

    def test_serialization_schema_and_levels(self):
        command = self.valid_command()
        data = command.to_dict()
        self.assertEqual(data["schema"], COMMAND_SCHEMA)
        self.assertEqual(len(data["levels"]), 8)
        self.assertTrue(data["complete"])
        self.assertIn("parameters", data)
        self.assertIn("context", data)

    def test_serialization_preserves_runtime_data(self):
        command = CommandDefinition(
            **{
                **self.valid_command().__dict__,
                "parameters": CommandParameters({"floor": 2}),
                "context": CommandContext(
                    project_id="PROJECT-TEST",
                    scale="BUILDING",
                    values={"region": "TEST"},
                ),
            }
        )
        data = command.to_dict()
        self.assertEqual(data["parameters"]["floor"], 2)
        self.assertEqual(data["context"]["project_id"], "PROJECT-TEST")
        self.assertEqual(data["context"]["values"]["region"], "TEST")

    def test_validation_result_success_factory(self):
        result = ValidationResult.success()
        self.assertTrue(result.valid)
        self.assertEqual(result.issues, ())

    def test_validation_result_failure_factory(self):
        issue = ValidationIssue("TEST", "Test issue")
        result = ValidationResult.failure(issue)
        self.assertFalse(result.valid)
        self.assertEqual(result.issues, (issue,))
        self.assertEqual(result.errors, result.issues)


if __name__ == "__main__":
    unittest.main()
