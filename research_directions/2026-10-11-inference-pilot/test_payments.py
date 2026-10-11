"""Independent exact examples and implementation guards for payment rules."""

from fractions import Fraction as Q
from itertools import product
import unittest

from payments import RULES, aggregate, dot, integral_q_power, payments


V = ((Q(1), Q(0)), (Q(0), Q(1)))


def minimum(c):
    return min(c)


def independently_evaluated_hybrid_integrand(bundles, i, q):
    """Direct product-probability definition, without integral coefficients."""
    t = minimum(aggregate(bundles))
    others = tuple(h for h in range(len(bundles)) if h != i)
    answer = Q(0)
    for bits in product((0, 1), repeat=len(others)):
        c = [Q(0), Q(0)]
        probability = Q(1)
        for h, bit in zip(others, bits):
            probability *= (1-q) if bit else q
            if bit:
                c = [x+y for x, y in zip(c, bundles[h])]
        # Lexicographically first dual is (0,1), used also at zero and ties.
        chosen = (Q(0), Q(1)) if c[1] <= c[0] else (Q(1), Q(0))
        cap = min(dot(chosen, bundles[i]), t)
        marginal = min(x+y for x, y in zip(c, bundles[i])) - min(c)
        answer += probability * (q*cap + (1-q)*marginal)
    return answer


class PaymentTests(unittest.TestCase):
    def test_known_marginals(self):
        bundles = ((2, 0), (1, 0), (0, 2))
        self.assertEqual(payments("marginal", bundles, minimum, None), (1, 0, 2))

    def test_dual_withholding_example(self):
        true = ((2, 0), (1, 0), (0, 2))
        hidden = ((Q(1, 2), 0), true[1], true[2])
        self.assertEqual(payments("dual", true, minimum, V), (0, 0, 2))
        self.assertEqual(payments("dual", hidden, minimum, V), (Q(1, 2), 1, 0))

    def test_coordinated_withholding_example(self):
        true = ((1, 0), (1, 0), (0, 1))
        hidden = ((0, 0), true[1], true[2])
        self.assertEqual(payments("marginal", true, minimum, None), (0, 0, 1))
        self.assertEqual(payments("marginal", hidden, minimum, None), (0, 1, 1))

    def test_exact_proportional_units(self):
        self.assertEqual(payments("proportional", ((2, 0), (0, 4)), minimum,
                                  None, weights=(2, 1)), (1, 1))

    def test_known_shapley(self):
        self.assertEqual(payments("shapley", ((1, 0), (1, 0), (0, 1)),
                                  minimum, None), (Q(1, 6), Q(1, 6), Q(2, 3)))

    def test_symmetry_efficiency_and_rationals(self):
        bundles = ((2, 1), (2, 1), (0, 3))
        total = minimum(aggregate(bundles))
        for rule in RULES:
            result = payments(rule, bundles, minimum, V)
            self.assertEqual(result[0], result[1])
            self.assertTrue(all(isinstance(x, Q) for x in result))
            if rule in ("proportional", "dual", "shapley"):
                self.assertEqual(sum(result), total)

    def test_zero_production_and_zero_owner(self):
        for rule in RULES:
            self.assertEqual(payments(rule, ((0, 0), (0, 0)), minimum, V), (0, 0))
            self.assertEqual(payments(rule, ((5, 0), (0, 0)), minimum, V), (0, 0))
            self.assertEqual(payments(rule, ((0, 0), (2, 2)), minimum, V)[0], 0)

    def test_fixed_dual_tie_priority(self):
        bundles = ((1, 0), (0, 1))
        self.assertEqual(payments("dual", bundles, minimum, V), (0, 1))
        self.assertEqual(payments("dual", bundles, minimum, tuple(reversed(V)) + V),
                         (0, 1))

    def test_integrals_known_values(self):
        self.assertEqual(integral_q_power(0, 0, Q(1, 2)), Q(1, 2))
        self.assertEqual(integral_q_power(1, 0, Q(1, 2)), Q(1, 8))
        self.assertEqual(integral_q_power(0, 1, Q(1, 2)), Q(3, 8))
        self.assertEqual(integral_q_power(1, 1, Q(1, 2)), Q(1, 12))
        self.assertEqual(integral_q_power(2, 3, Q(1)), Q(1, 60))

    def test_hybrid_exact_simpson_cubic(self):
        # For three owners the integrand is cubic, so Simpson is exact.
        for bundles in (((2, 0), (1, 0), (0, 2)),
                        ((2, 1), (0, 3), (1, 0)),
                        ((1, 0), (0, 1), (0, 0))):
            for j in (2, 3, 5):
                result = payments("sharp_hybrid", bundles, minimum, V, j=j)
                eta = Q(1, j)
                for i in range(3):
                    at = lambda q: independently_evaluated_hybrid_integrand(bundles, i, q)
                    expected = j * eta / 6 * (at(Q(0)) + 4*at(eta/2) + at(eta))
                    self.assertEqual(result[i], expected)

    def test_one_form_is_efficient_for_hybrid(self):
        w = (Q(2), Q(3))
        bundles = ((1, 2), (0, 4), (Q(1, 2), 1))
        value = lambda c: dot(c, w)
        self.assertEqual(payments("sharp_hybrid", bundles, value, (w,)),
                         tuple(dot(w, b) for b in bundles))

    def test_hybrid_selection_scores_are_not_capped(self):
        # With owner 1 open, raw scores are (100, 1), selecting (1,0).
        # Capping that owner's scores at T=1 would create a false priority tie.
        bundles = ((0, 1), (1, 100))
        self.assertEqual(payments("sharp_hybrid", bundles, minimum, V)[0], Q(1, 12))

    def test_resource_unit_conversion_preserves_economic_rules(self):
        bundles = ((2, 1), (0, 3), (1, 0))
        converted = tuple((10*b[0], b[1]) for b in bundles)
        forms = ((Q(1, 10), Q(0)), (Q(0), Q(1)))
        value = lambda c: min(c[0]/10, c[1])
        for rule in RULES:
            weights = (Q(1, 10), Q(1)) if rule == "proportional" else None
            self.assertEqual(payments(rule, bundles, minimum, V),
                             payments(rule, converted, value, forms, weights=weights))

    def test_hybrid_finite_grid_coverage_and_own_monotonicity(self):
        # A finite code check, explicitly not an all-real-profile proof.
        vectors = tuple(product((0, 1), repeat=2))
        table = {}
        for bundles in product(vectors, repeat=3):
            pay = payments("sharp_hybrid", bundles, minimum, V)
            table[bundles] = pay
            for mask in range(8):
                members = tuple(i for i in range(3) if mask >> i & 1)
                self.assertGreaterEqual(sum(pay[i] for i in members),
                                        minimum(aggregate(bundles, members)))
        for bundles, pay in table.items():
            for i, own in enumerate(bundles):
                for low in vectors:
                    if all(x <= y for x, y in zip(low, own)):
                        changed = bundles[:i] + (low,) + bundles[i+1:]
                        self.assertLessEqual(table[changed][i], pay[i])

    def test_invalid_inputs_raise_under_optimization_too(self):
        invalid = [
            lambda: payments("unknown", ((1, 1),), minimum, V),
            lambda: payments("dual", ((1, 1),), minimum, None),
            lambda: payments("dual", ((1, 1),), minimum, ((2, 2),)),
            lambda: payments("marginal", ((-1, 1),), minimum, None),
            lambda: payments("marginal", ((1.0, 1),), minimum, None),
            lambda: payments("marginal", ((1, 1), (1,)), minimum, None),
            lambda: payments("proportional", ((1, 1),), minimum, None, weights=(1, 0)),
            lambda: payments("sharp_hybrid", ((1, 1),), minimum, V, j=1),
            lambda: payments("sharp_hybrid", ((1, 1),), minimum, V, j=Q(2)),
            lambda: integral_q_power(-1, 0, Q(1, 2)),
            lambda: dot((1,), (1, 2)),
        ]
        for operation in invalid:
            with self.assertRaises(ValueError):
                operation()


if __name__ == "__main__":
    unittest.main()
