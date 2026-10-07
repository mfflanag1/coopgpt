#!/usr/bin/env python3
"""Exact finite checks for uniformly averaged Bernoulli hybrid payments.

Uses only Python 3.8+'s standard library and the sibling binary_packing.py for
exact LP vertices/effective capacities.  --packing-verifier can select that
file explicitly while developing outside the verification directory.

For a fixed, report-independent vertex priority, B has deletion probability q:
  p_e = D_e E[w_e | B_e=0],
  m_e = E_{B_-e}[F(c B with e on) - F(c B with e off)],
  z_e = D_e E[w_e], r_e = q p_e + (1-q) m_e.
All masks, coalitions and polynomial coefficients use Fraction arithmetic.
The averaging law is uniform on (0,b); division by b is explicit.  Conditional
expectations are enumerated over B_-e, so no division by q is needed.
The q=0,1 checks are polynomial continuations, not conditioning on null events.

Finite tests do not prove a general/asymptotic theorem.  The Chernoff logarithmic
bound is not numerically certified here; its exact algebraic precursors are.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import importlib.util
from itertools import product
from math import comb
from pathlib import Path
import json
import sys


COUNTS = Counter()
ZERO = (Q(0),)
ONE = (Q(1),)
X = (Q(0), Q(1))
ONE_MINUS_X = (Q(1), Q(-1))
QS = (Q(0), Q(1, 7), Q(1, 3), Q(1, 2), Q(2, 3), Q(4, 5), Q(1))
BS = (Q(1, 2), Q(1, 3))
REPORTS = (Q(0), Q(1, 3), Q(1), Q(2), Q(5, 2))


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def trim(poly):
    poly = list(map(Q, poly))
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return tuple(poly) if poly else ZERO


def add(*polys):
    out = [Q(0)] * max((len(p) for p in polys), default=1)
    for poly in polys:
        for k, coefficient in enumerate(poly):
            out[k] += coefficient
    return trim(out)


def scale(poly, scalar):
    return trim(coefficient * scalar for coefficient in poly)


def subtract(left, right):
    return add(left, scale(right, -1))


def multiply(left, right):
    out = [Q(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return trim(out)


def derivative(poly):
    return trim(k * coefficient for k, coefficient in enumerate(poly) if k)


def evaluate(poly, q):
    value = Q(0)
    for coefficient in reversed(poly):
        value = q * value + coefficient
    return value


def integrate(poly, upper):
    return sum((coefficient * upper ** (k + 1) / (k + 1)
                for k, coefficient in enumerate(poly)), Q(0))


def bernstein_monomial(zeros, ones):
    """Power-basis coefficients of q**zeros * (1-q)**ones."""
    require(zeros >= 0 and ones >= 0, "negative mask exponent")
    return trim([Q(0)] * zeros
                + [Q((-1) ** k * comb(ones, k)) for k in range(ones + 1)])


def complementary_integral(zeros, ones, upper):
    """Independent exact integral: substitute u=1-q, then expand (1-u)^zeros."""
    return sum((Q((-1) ** k * comb(zeros, k), ones + k + 1)
                * (1 - (1 - upper) ** (ones + k + 1))
                for k in range(zeros + 1)), Q(0))


def mask_probability(n, mask, q, skip=None):
    """Direct product, independently of the polynomial/binomial implementation."""
    probability = Q(1)
    for e in range(n):
        if e != skip:
            probability *= 1 - q if mask & (1 << e) else q
    return probability


def popcount(mask):
    return bin(mask).count("1")


def load_packing(path):
    require(path.is_file(), "missing binary_packing.py: " + str(path))
    spec = importlib.util.spec_from_file_location("hybrid_packing_support", path)
    require(spec is not None and spec.loader is not None, "cannot load packing support")
    module = importlib.util.module_from_spec(spec)
    # Loading support is read-only even when it lives outside the current workspace.
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module


class PackingOracle:
    """General binary recipe family, including nonclutters and empty families."""
    def __init__(self, packing, name, n, recipes):
        self.support = packing
        self.name, self.n = name, n
        self.recipes = packing.canonical_recipes(n, recipes)
        self.vertices = packing.dual_vertices(n, self.recipes)
        self.restricted = tuple(packing.dual_vertices(
            n, tuple(recipe for recipe in self.recipes if e in recipe)) for e in range(n))
        self.effective_cache = {}

    def value(self, capacities):
        return min(self.support.dot(capacities, vertex) for vertex in self.vertices)

    def effective(self, capacities):
        if capacities not in self.effective_cache:
            self.effective_cache[capacities] = tuple(
                min(self.support.dot(capacities, vertex) for vertex in family)
                for family in self.restricted)
        return self.effective_cache[capacities]

    def crosscheck_primal(self, capacities):
        vertices = self.support.primal_vertices(self.n, self.recipes, capacities)
        total = max(sum(vertex, Q(0)) for vertex in vertices)
        effective = tuple(max(sum((vertex[j] for j, recipe in enumerate(self.recipes)
                                   if e in recipe), Q(0)) for vertex in vertices)
                          for e in range(self.n))
        require(total == self.value(capacities), "independent primal F: " + self.name)
        require(effective == self.effective(capacities), "independent primal D: " + self.name)
        require(vertices == self.support.primal_vertices(self.n, self.recipes, effective),
                "feasible production-polytope preservation: " + self.name)
        COUNTS["primal_dual_value_crosschecks"] += 1
        COUNTS["primal_effective_coordinate_crosschecks"] += self.n
        COUNTS["primal_polytope_vertex_set_equalities"] += 1


class HybridTechnology:
    def __init__(self, packing, name, n, recipes, reverse=False):
        self.lp = PackingOracle(packing, name, n, recipes)
        self.name = name + ("/reverse" if reverse else "/lexicographic")
        self.n = n
        self.vertices = tuple(reversed(self.lp.vertices)) if reverse else self.lp.vertices
        self.masks = tuple(range(1 << n))
        self.cache = {}
        COUNTS["technology_priority_pairs"] += 1

    def profile(self, capacities):
        capacities = tuple(map(Q, capacities))
        if capacities in self.cache:
            return self.cache[capacities]
        require(len(capacities) == self.n and all(c >= 0 for c in capacities),
                "invalid capacities")
        label = "%s c=%s" % (self.name, capacities)
        total = self.lp.value(capacities)
        effective = self.lp.effective(capacities)
        require(all(0 <= d <= min(c, total) for d, c in zip(effective, capacities)),
                "effective bounds: " + label)
        values, winners = [], []
        for mask in self.masks:
            raw = tuple(capacities[e] if mask & (1 << e) else Q(0)
                        for e in range(self.n))
            normalized = tuple(effective[e] if mask & (1 << e) else Q(0)
                               for e in range(self.n))
            scores = [sum((d * w for d, w in zip(normalized, vertex)), Q(0))
                      for vertex in self.vertices]
            minimum = min(scores)
            require(minimum == self.lp.value(raw), "masked value preservation: " + label)
            require(minimum <= total, "selected score at most T: " + label)
            values.append(minimum)
            winners.append(self.vertices[scores.index(minimum)])
            COUNTS["masked_value_preservation_checks"] += 1
        g = ZERO
        z = [ZERO] * self.n
        p, m, r = [ZERO] * self.n, [ZERO] * self.n, [ZERO] * self.n
        for mask in self.masks:
            ones = popcount(mask)
            weight = bernstein_monomial(self.n - ones, ones)
            g = add(g, scale(weight, values[mask]))
            for e in range(self.n):
                z[e] = add(z[e], scale(weight, effective[e] * winners[mask][e]))
        marginals = {}
        for e in range(self.n):
            slack_polynomial = ZERO
            for off in self.masks:
                if off & (1 << e):
                    continue
                on = off | (1 << e)
                delta = values[on] - values[off]
                marginals[e, off] = delta
                lower = effective[e] * winners[on][e]
                upper = effective[e] * winners[off][e]
                require(0 <= lower <= delta <= upper,
                        "mask marginal/dual sandwich: " + label)
                ones = popcount(off)
                conditional = bernstein_monomial(self.n - 1 - ones, ones)
                p[e] = add(p[e], scale(conditional, upper))
                m[e] = add(m[e], scale(conditional, delta))
                slack_polynomial = add(slack_polynomial,
                                       scale(multiply(ONE_MINUS_X, conditional), delta - lower))
                COUNTS["pointwise_marginal_sandwiches"] += 1
            r[e] = add(multiply(X, p[e]), multiply(ONE_MINUS_X, m[e]))
            require(subtract(r[e], z[e]) == slack_polynomial,
                    "all-q coordinate slack polynomial: " + label)
            COUNTS["all_q_domination_polynomial_identities"] += 1
        Z, P, M, R = map(lambda terms: add(*terms), (z, p, m, r))
        require(multiply(X, P) == subtract(Z, g), "q P = Z-g: " + label)
        require(M == scale(derivative(g), -1), "M = -g': " + label)
        require(R == subtract(subtract(Z, g), multiply(ONE_MINUS_X, derivative(g))),
                "R = Z-g-(1-q)g': " + label)
        require(evaluate(g, Q(0)) == total and evaluate(g, Q(1)) == 0,
                "g endpoint values: " + label)
        COUNTS["budget_polynomial_identities"] += 3
        COUNTS["g_endpoint_checks"] += 2
        result = {"c": capacities, "D": effective, "T": total, "g": g,
                  "z": tuple(z), "p": tuple(p), "m": tuple(m), "r": tuple(r),
                  "Z": Z, "R": R, "values": tuple(values), "winners": tuple(winners),
                  "marginals": marginals, "averages": {}}
        self.check_scalar_and_coalitions(result, label)
        self.check_integrated(result, label)
        self.cache[capacities] = result
        COUNTS["profiles"] += 1
        return result

    def direct_at_q(self, profile, q):
        d, winners, values = profile["D"], profile["winners"], profile["values"]
        p, m, z = [Q(0)] * self.n, [Q(0)] * self.n, [Q(0)] * self.n
        g = Q(0)
        mass = Q(0)
        for mask in self.masks:
            probability = mask_probability(self.n, mask, q)
            mass += probability
            g += probability * values[mask]
            for e in range(self.n):
                z[e] += probability * d[e] * winners[mask][e]
        require(mass == 1, "full mask probability normalization")
        for e in range(self.n):
            mass = Q(0)
            for off in self.masks:
                if off & (1 << e):
                    continue
                probability = mask_probability(self.n, off, q, skip=e)
                mass += probability
                p[e] += probability * d[e] * winners[off][e]
                m[e] += probability * (values[off | (1 << e)] - values[off])
            require(mass == 1, "conditional mask probability normalization")
        r = tuple(q * pe + (1 - q) * me for pe, me in zip(p, m))
        return {"p": tuple(p), "m": tuple(m), "z": tuple(z), "r": r, "g": g}

    def check_scalar_and_coalitions(self, profile, label):
        for q in QS:
            direct = self.direct_at_q(profile, q)
            require(evaluate(profile["g"], q) == direct["g"], "direct g: " + label)
            for name in ("p", "m", "z", "r"):
                require(tuple(evaluate(poly, q) for poly in profile[name]) == direct[name],
                        "direct/polynomial " + name + ": " + label)
                COUNTS["scalar_direct_polynomial_coordinate_checks"] += self.n
            for e in range(self.n):
                require(0 <= direct["z"][e] <= direct["r"][e], "r >= z: " + label)
                require(q * direct["p"][e] <= direct["z"][e] <= direct["p"][e],
                        "p/z sandwich: " + label)
                COUNTS["scalar_domination_checks"] += 1
            for coalition in self.masks:
                value = profile["values"][coalition]
                for name in ("z", "r"):
                    payment = sum((direct[name][e] for e in range(self.n)
                                   if coalition & (1 << e)), Q(0))
                    require(payment >= value, name + " scalar coalition coverage: " + label)
                    COUNTS["scalar_" + name + "_coalition_checks"] += 1

    def direct_average(self, profile, upper):
        """Mask integration using the independently expanded complementary variable."""
        p, m, z, r = ([Q(0)] * self.n for _ in range(4))
        g = Q(0)
        mass = Q(0)
        for mask in self.masks:
            ones = popcount(mask)
            weight = complementary_integral(self.n - ones, ones, upper) / upper
            mass += weight
            g += weight * profile["values"][mask]
            for e in range(self.n):
                z[e] += weight * profile["D"][e] * profile["winners"][mask][e]
        require(mass == 1, "averaged full mask normalization")
        for e in range(self.n):
            mass = Q(0)
            for off in self.masks:
                if off & (1 << e):
                    continue
                ones = popcount(off)
                zeros = self.n - 1 - ones
                weight = complementary_integral(zeros, ones, upper) / upper
                mass += weight
                pe = profile["D"][e] * profile["winners"][off][e]
                me = profile["marginals"][e, off]
                p[e] += weight * pe
                m[e] += weight * me
                r[e] += (complementary_integral(zeros + 1, ones, upper) * pe
                         + complementary_integral(zeros, ones + 1, upper) * me) / upper
            require(mass == 1, "averaged conditional mask normalization")
        return {"p": tuple(p), "m": tuple(m), "z": tuple(z), "r": tuple(r), "g": g}

    def check_integrated(self, profile, label):
        for upper in BS:
            direct = self.direct_average(profile, upper)
            require(integrate(profile["g"], upper) / upper == direct["g"],
                    "independent average g: " + label)
            for name in ("p", "m", "z", "r"):
                expected = tuple(integrate(poly, upper) / upper for poly in profile[name])
                require(expected == direct[name], "independent exact average " + name + ": " + label)
                COUNTS["independent_integration_coordinate_checks"] += self.n
            lhs = integrate(profile["R"], upper)
            rhs = (integrate(profile["Z"], upper) + profile["T"]
                   - (1 - upper) * evaluate(profile["g"], upper)
                   - 2 * integrate(profile["g"], upper))
            require(lhs == rhs, "integrated R identity: " + label)
            require(sum(direct["r"], Q(0)) <= profile["T"] / upper + sum(direct["z"], Q(0)),
                    "averaged budget <= T/b + average Z: " + label)
            require(all(re >= ze >= 0 for re, ze in zip(direct["r"], direct["z"])),
                    "average r >= average z: " + label)
            COUNTS["integrated_budget_identity_checks"] += 1
            COUNTS["integrated_budget_inequality_checks"] += 1
            COUNTS["integrated_domination_coordinate_checks"] += self.n
            for coalition in self.masks:
                for name in ("z", "r"):
                    payment = sum((direct[name][e] for e in range(self.n)
                                   if coalition & (1 << e)), Q(0))
                    require(payment >= profile["values"][coalition],
                            name + " average coalition coverage: " + label)
                    COUNTS["integrated_" + name + "_coalition_checks"] += 1
            profile["averages"][upper] = direct

    def own_reports(self, context, e, reports=REPORTS):
        profiles = []
        for report in reports:
            capacities = list(context)
            capacities[e] = report
            profiles.append(self.profile(capacities))
        for lower, upper in zip(profiles, profiles[1:]):
            label = "%s owner=%d %s -> %s" % (self.name, e, lower["c"][e], upper["c"][e])
            for off in self.masks:
                if off & (1 << e):
                    continue
                require(lower["D"][e] * lower["winners"][off][e]
                        <= upper["D"][e] * upper["winners"][off][e],
                        "pointwise own p monotonicity: " + label)
                require(lower["marginals"][e, off] <= upper["marginals"][e, off],
                        "pointwise own marginal monotonicity: " + label)
                COUNTS["pointwise_own_monotonicity_checks"] += 2
            for q in QS:
                for name in ("p", "m", "r"):
                    require(evaluate(lower[name][e], q) <= evaluate(upper[name][e], q),
                            "scalar own " + name + " monotonicity: " + label)
                    COUNTS["scalar_own_" + name + "_monotonicity_checks"] += 1
            for b in BS:
                for name in ("p", "m", "r"):
                    require(lower["averages"][b][name][e] <= upper["averages"][b][name][e],
                            "integrated own " + name + " monotonicity: " + label)
                    COUNTS["integrated_own_" + name + "_monotonicity_checks"] += 1
        COUNTS["own_report_families"] += 1


def expect_rejected(label, operation):
    try:
        operation()
    except VerificationError:
        COUNTS["negative_controls_rejected"] += 1
        return
    raise VerificationError("negative control was not rejected: " + label)


def calibrate():
    require(multiply((Q(1), Q(-1)), (Q(1), Q(1))) == (Q(1), Q(0), Q(-1)),
            "polynomial multiplication calibration")
    require(derivative((Q(5), Q(3), Q(-2))) == (Q(3), Q(-4)),
            "polynomial derivative calibration")
    require(integrate((Q(2), Q(3)), Q(1, 3)) == Q(5, 6),
            "polynomial integral calibration")
    for zeros in range(7):
        for ones in range(7):
            polynomial = bernstein_monomial(zeros, ones)
            for q in QS:
                require(evaluate(polynomial, q) == q ** zeros * (1 - q) ** ones,
                        "Bernstein expansion calibration")
            for b in BS:
                require(integrate(polynomial, b) == complementary_integral(zeros, ones, b),
                        "independent integral calibration")
            require(integrate(polynomial, Q(1)) == Q(1, (zeros + ones + 1) * comb(zeros + ones, zeros)),
                    "integer beta integral calibration")
    expect_rejected("always-active checker", lambda: require(False, "deliberate failure"))
    COUNTS["polynomial_calibration_checks"] += 3 + 49 * (len(QS) + len(BS) + 1)
    # With b=1/j and exp(-lambda)=1/j**2, the uniform Chernoff denominator
    # is -log(base)=log(j**3/(j**2+j-1)); check the rational algebra only.
    for j in range(2, 17):
        b = Q(1, j)
        base = b + (1-b) / j**2
        require(base == Q(j*j+j-1, j**3) and 0 < base < 1,
                "finite-K denominator algebra")
        require(all(q + (1-q) / j**2 <= base for q in (Q(0), b/2, b)),
                "uniform deletion-probability bound")
        COUNTS["finite_K_denominator_algebra_checks"] += 1


def negative_controls(single, serial):
    s = single.profile((Q(1),))
    t = serial.profile((Q(1),) * serial.n)
    expect_rejected("wrong derivative sign", lambda: require(add(*s["m"]) == derivative(s["g"]), "wrong M"))
    wrong_sign = add(subtract(s["Z"], s["g"]), multiply(ONE_MINUS_X, derivative(s["g"])))
    expect_rejected("wrong budget sign", lambda: require(s["R"] == wrong_sign, "wrong R sign"))
    swapped = add(multiply(ONE_MINUS_X, add(*t["p"])), multiply(X, add(*t["m"])))
    expect_rejected("swapped mixture", lambda: require(t["R"] == swapped, "wrong mixture"))
    q = Q(1, 3)
    missing_conditioning = q * q * evaluate(s["p"][0], q) + (1 - q) * evaluate(s["m"][0], q)
    expect_rejected("unconditional p undercovers", lambda: require(missing_conditioning >= s["T"], "coverage failed"))
    expect_rejected("flipped deletion probability", lambda: require(evaluate(s["g"], q) == evaluate(s["g"], 1-q), "q flipped"))
    b = Q(1, 2)
    wrong_integral = (integrate(s["Z"], b) + s["T"] - (1-b) * evaluate(s["g"], b)
                      - integrate(s["g"], b))
    expect_rejected("missing second g integral", lambda: require(integrate(s["R"], b) == wrong_integral, "coefficient wrong"))
    expect_rejected("missing averaging normalization", lambda: require(integrate(s["R"], b) == s["averages"][b]["r"][0], "no 1/b"))


def all_three_resource_clutters():
    recipes = tuple(tuple(e for e in range(3) if mask & (1 << e)) for mask in range(1, 8))
    for bits in range(1 << len(recipes)):
        family = tuple(recipe for i, recipe in enumerate(recipes) if bits & (1 << i))
        if all(not set(a) < set(b) for a in family for b in family):
            yield family


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packing-verifier", type=Path,
                        default=Path(__file__).resolve().with_name("binary_packing.py"))
    parser.add_argument("--skip-exhaustive", action="store_true",
                        help="skip all three-resource clutters on the three-report grid")
    args = parser.parse_args()
    packing = load_packing(args.packing_verifier.resolve())
    calibrate()
    # Independent primal/dual calibration includes a genuinely fractional vertex.
    packing.calibrate()
    specifications = (
        ("empty-family", 2, ()),
        ("single-resource", 1, ((0,),)),
        ("serial-four", 4, ((0, 1, 2, 3),)),
        ("parallel-three", 3, ((0,), (1,), (2,))),
        ("triangle-fractional", 3, ((0, 1), (0, 2), (1, 2))),
        ("tetrahedron-triples", 4, ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))),
        ("unused-resource", 4, ((0, 1), (1, 2))),
        ("five-cycle", 5, ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4))),
        ("five-mixed-clutter", 5, ((0, 1), (0, 2, 3), (1, 2, 4), (3, 4))),
        # Directed paths: s-a-t and s-b-t.
        ("dag-diamond", 4, ((0, 1), (2, 3))),
        # Edges 0=s-a, 1=a-t, 2=s-b, 3=b-t, 4=a-b.
        ("dag-wheatstone", 5, ((0, 1), (2, 3), (0, 4, 3))),
        # A shared initial edge followed by the preceding diamond.
        ("dag-bottleneck-diamond", 5, ((0, 1, 2), (0, 3, 4))),
        # Redundant supersets can affect effective usage even when they do not
        # change maximum value, so they must not silently be discarded.
        ("nonclutter-redundant-pair", 2, ((0,), (0, 1))),
        ("nonclutter-redundant-usage", 4, ((0,), (0, 1), (1, 2), (1, 2, 3))),
    )
    inventory = []
    for reverse in (False, True):
        technologies = [HybridTechnology(packing, *spec, reverse=reverse) for spec in specifications]
        negative_controls(technologies[1], technologies[2])
        for technology in technologies:
            profiles, contexts = packing.base_profiles(technology.n)
            for capacities in profiles:
                technology.profile(capacities)
            for context in contexts:
                for e in range(technology.n):
                    technology.own_reports(context, e)
            # The imported LP engine is independently checked against primal
            # vertex enumeration for every mask of one heterogeneous profile.
            if not reverse:
                primal_profiles = {packing.mask_vector(contexts[1], mask) for mask in technology.masks}
                primal_profiles.update((contexts[0], contexts[2]))
                for capacities in sorted(primal_profiles):
                    technology.lp.crosscheck_primal(capacities)
            inventory.append({"name": technology.name, "resources": technology.n,
                              "recipes": len(technology.lp.recipes),
                              "dual_vertices": len(technology.vertices),
                              "tested_profiles": len(technology.cache)})
            print("checked " + technology.name, file=sys.stderr, flush=True)
    if not args.skip_exhaustive:
        grid = (Q(0), Q(1, 2), Q(2))
        families = tuple(all_three_resource_clutters())
        require(len(families) == 19, "three-resource clutter inventory")
        for index, family in enumerate(families):
            for reverse in (False, True):
                technology = HybridTechnology(packing, "exhaustive-clutter-%02d" % index,
                                              3, family, reverse=reverse)
                for capacities in product(grid, repeat=3):
                    technology.profile(capacities)
                for e in range(3):
                    other = [h for h in range(3) if h != e]
                    for pair in product(grid, repeat=2):
                        context = [Q(0)] * 3
                        for h, value in zip(other, pair):
                            context[h] = value
                        technology.own_reports(context, e, reports=grid)
                COUNTS["exhaustive_clutter_priority_pairs"] += 1
            print("checked exhaustive three-resource clutter %d/19" % (index + 1),
                  file=sys.stderr, flush=True)
    print("PASS: exact finite uniformly averaged Bernoulli hybrid checks")
    print("Interior scalar q: 1/7, 1/3, 1/2, 2/3, 4/5; polynomial endpoints: 0, 1")
    print("Uniform averaging intervals: (0,1/2), (0,1/3)")
    print(json.dumps({"technologies": inventory, "counts": dict(sorted(COUNTS.items())),
                      "lp_support_counts": dict(sorted(packing.COUNTS.items()))}, indent=2, sort_keys=True))
    print("All arithmetic above is rational; no numerical quadrature or logarithmic approximation was used.")
    print("Finite verification only; no general, asymptotic, or novelty claim is inferred.")


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
