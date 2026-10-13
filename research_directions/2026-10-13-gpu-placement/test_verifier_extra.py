"""Additional malformed-input and boundary coverage independent of the suite."""

import copy
import unittest

from test_verifier import fixture
from verifier import strict_loads, validate_manifest, verify_plan


class AdditionalVerifierTests(unittest.TestCase):
    def test_exponent_overflow_rejected(self):
        for token in ("1e9999", "-1e9999", '{"nested":[1e9999]}'):
            with self.subTest(token=token), self.assertRaises(ValueError):
                strict_loads(token)

    def test_finite_json_numbers_allowed_before_schema_validation(self):
        self.assertEqual(strict_loads('[0.5,1e3,1]'), [0.5, 1000.0, 1])

    def test_nested_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            strict_loads('{"nested":[{"a":1,"a":2}]}')

    def test_json_input_type_and_malformed_json_fail_as_value_error(self):
        for value in (None, b"{}", [], "{", "[", '{"a":}'):
            with self.assertRaises(ValueError):
                strict_loads(value)

    def test_none_plan_fails_closed(self):
        manifest, _ = fixture()
        self.assertFalse(verify_plan(manifest, None)["valid"])

    def test_exact_namespace_boundaries(self):
        manifest, plan = fixture()
        manifest["jobs"][0]["id"] = "n1"
        manifest["nodes"][0]["gpus"][0]["id"] = "n1"
        plan["placements"][0].update(job="n1", gpus=["n1"])
        self.assertTrue(verify_plan(manifest, plan)["valid"])

    def test_unicode_and_newline_ids(self):
        for identifier in ("é", "n１", "n\n", "n☃", "A" * 33):
            manifest, _ = fixture()
            manifest["nodes"][0]["id"] = identifier
            with self.assertRaises(ValueError):
                validate_manifest(manifest)

    def test_plan_nested_fields_reject_wrong_types(self):
        manifest, original = fixture()
        for field in ("job", "node", "gpus"):
            for malformed in (None, 0, True, {}, [], [None], [["g1"]]):
                plan = copy.deepcopy(original)
                plan["placements"][0][field] = malformed
                with self.subTest(field=field, malformed=malformed):
                    self.assertFalse(verify_plan(manifest, plan)["valid"])

    def test_manifest_gpu_and_policy_malformed_values(self):
        for target in ("gpu", "allowed_families", "allowed_owners"):
            for malformed in (None, 0, True, {}, "A", [None], [["A"]]):
                manifest, _ = fixture()
                if target == "gpu":
                    manifest["nodes"][0]["gpus"][0] = malformed
                else:
                    manifest["jobs"][0][target] = malformed
                with self.subTest(target=target, malformed=malformed):
                    with self.assertRaises(ValueError):
                        validate_manifest(manifest)

    def test_non_string_keys_fail_closed(self):
        manifest, plan = fixture()
        plan[7] = "unexpected"
        self.assertFalse(verify_plan(manifest, plan)["valid"])
        manifest[7] = "unexpected"
        with self.assertRaises(ValueError):
            validate_manifest(manifest)

    def test_invalid_manifest_rejected_even_for_defer_all(self):
        manifest, _ = fixture()
        manifest["jobs"][0]["priority"] = True
        with self.assertRaises(ValueError):
            verify_plan(manifest, {"schema_version": 1, "placements": [],
                                   "deferred": ["j1", "j2"]})


if __name__ == "__main__":
    unittest.main()
