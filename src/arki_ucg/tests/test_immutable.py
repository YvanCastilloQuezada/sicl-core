import math
import unittest
from collections import UserDict

from arki_ucg.immutable import (
    ImmutableValueError,
    canonical_json,
    freeze,
    thaw,
)


class TestUCGImmutableFoundation(unittest.TestCase):

    def test_mapping_is_recursively_frozen(self):
        source = {"outer": {"items": [1, 2, 3]}}
        result = freeze(source)

        source["outer"]["items"].append(4)

        self.assertEqual(result["outer"]["items"], (1, 2, 3))

    def test_direct_mapping_mutation_is_blocked(self):
        result = freeze({"a": 1})

        with self.assertRaises(TypeError):
            result["a"] = 2

    def test_nested_sequence_is_frozen(self):
        result = freeze([{"x": [1, 2]}])

        self.assertEqual(result, ({"x": (1, 2)},))

    def test_shared_noncyclic_reference_is_allowed(self):
        shared = {"value": 7}
        result = freeze([shared, shared])

        self.assertEqual(result[0]["value"], 7)
        self.assertEqual(result[1]["value"], 7)

    def test_mapping_cycle_is_rejected(self):
        source = {}
        source["self"] = source

        with self.assertRaises(ImmutableValueError):
            freeze(source)

    def test_sequence_cycle_is_rejected(self):
        source = []
        source.append(source)

        with self.assertRaises(ImmutableValueError):
            freeze(source)

    def test_non_string_mapping_key_is_rejected(self):
        with self.assertRaises(ImmutableValueError):
            freeze({1: "invalid"})

    def test_arbitrary_mapping_implementation_is_supported(self):
        result = freeze(UserDict({"x": 1}))
        self.assertEqual(result["x"], 1)

    def test_arbitrary_object_is_rejected(self):
        with self.assertRaises(ImmutableValueError):
            freeze(object())

    def test_nan_is_rejected(self):
        with self.assertRaises(ImmutableValueError):
            freeze(math.nan)

    def test_positive_infinity_is_rejected(self):
        with self.assertRaises(ImmutableValueError):
            freeze(math.inf)

    def test_negative_infinity_is_rejected(self):
        with self.assertRaises(ImmutableValueError):
            freeze(-math.inf)

    def test_boolean_integer_distinction_is_preserved(self):
        frozen = freeze([True, 1])
        self.assertIs(type(frozen[0]), bool)
        self.assertIs(type(frozen[1]), int)

    def test_thaw_returns_independent_mutable_data(self):
        frozen = freeze({"items": [1, 2]})
        result = thaw(frozen)

        result["items"].append(3)

        self.assertEqual(frozen["items"], (1, 2))

    def test_set_canonicalization_is_deterministic(self):
        left = freeze({"values": {3, 1, 2}})
        right = freeze({"values": {2, 3, 1}})

        self.assertEqual(canonical_json(left), canonical_json(right))

    def test_unicode_is_preserved(self):
        result = canonical_json({"name": "ARKI — ciudad"})
        self.assertIn("ARKI — ciudad", result)

    def test_canonical_json_has_stable_key_order(self):
        a = canonical_json({"z": 1, "a": 2})
        b = canonical_json({"a": 2, "z": 1})

        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
