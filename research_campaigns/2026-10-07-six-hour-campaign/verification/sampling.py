#!/usr/bin/env python3
"""Exact finite checks for the raw-capped sampler; stdlib, no file writes.

Run with Python 3.8+ normally or with -O.  Fraction/binomial distribution
formulas are crosschecked against independently multiplied polynomials.
All checks use explicit exceptions.  No finite test establishes an all-profile
concentration theorem or simultaneous coverage of an uncountable domain.
"""

from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from math import comb, factorial
import json
import sys


COUNTS = Counter()
REJECTED = []


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def expect_rejection(label, operation):
    try:
        operation()
    except VerificationError:
        REJECTED.append(label)
        return
    raise VerificationError("corruption was accepted: " + label)


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q(0))


def pmul(a, b):
    result = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for k, y in enumerate(b):
            result[i + k] += x * y
    return tuple(result)


def padd(a, b):
    return tuple((a[i] if i < len(a) else Q(0))
                 + (b[i] if i < len(b) else Q(0))
                 for i in range(max(len(a), len(b))))


def pscale(a, factor):
    return tuple(factor * value for value in a)


def pintegral(poly, endpoint):
    return sum((coefficient * endpoint ** (power + 1) / (power + 1)
                for power, coefficient in enumerate(poly)), Q(0))


def probability_polynomial(bits):
    result = (Q(1),)
    for bit in bits:
        result = pmul(result, (Q(1), Q(-1)) if bit else (Q(0), Q(1)))
    return result


def beta_expansion(a, k, j):
    endpoint = Q(1, j)
    return sum(((-1) ** h * comb(k, h) * endpoint ** (a + h + 1)
                / (a + h + 1) for h in range(k + 1)), Q(0))


def validate_distribution(n, j, probabilities, posteriors):
    require(n >= 1 and j >= 2, "distribution parameters")
    require(len(probabilities) == n + 1 and len(posteriors) == n + 1,
            "distribution lengths")
    require(sum(comb(n, k) * probabilities[k] for k in range(n + 1)) == 1,
            "cardinality normalization")
    denominator = factorial(n + 2) * j ** (n + 2)
    total_integer_mass = 0
    for k in range(n + 1):
        polynomial = probability_polynomial((0,) * (n - k) + (1,) * k)
        expected_probability = j * pintegral(polynomial, Q(1, j))
        expected_q_mass = j * pintegral(pmul(polynomial, (Q(0), Q(1))), Q(1, j))
        require(probabilities[k] == expected_probability, "individual mask probability")
        require(Q(0) < posteriors[k] < Q(1, j), "posterior range")
        require(probabilities[k] * posteriors[k] == expected_q_mass,
                "posterior conditional first moment")
        require(probabilities[k] * (1 - posteriors[k])
                == j * pintegral(pmul(polynomial, (Q(1), Q(-1))), Q(1, j)),
                "posterior complementary first moment")
        integer_mass = denominator * probabilities[k]
        integer_q_mass = denominator * probabilities[k] * posteriors[k]
        require(integer_mass.denominator == integer_q_mass.denominator == 1,
                "claimed common denominator")
        total_integer_mass += comb(n, k) * integer_mass
        COUNTS["posterior_moment_checks"] += 2
        COUNTS["common_denominator_checks"] += 2
    require(total_integer_mass == denominator, "integer cardinality normalization")
    require(sum(comb(n, k) * probabilities[k] * posteriors[k]
                for k in range(n + 1)) == Q(1, 2 * j), "unconditional q mean")
    COUNTS["distribution_checks"] += 1


@lru_cache(maxsize=None)
def distribution(n, j):
    probabilities = tuple(j * beta_expansion(n - k, k, j) for k in range(n + 1))
    posteriors = tuple(beta_expansion(n - k + 1, k, j)
                       / beta_expansion(n - k, k, j) for k in range(n + 1))
    validate_distribution(n, j, probabilities, posteriors)
    return probabilities, posteriors


def changed_bundle(bundles, owner, coordinate, value):
    result = [list(bundle) for bundle in bundles]
    result[owner][coordinate] = Q(value)
    return tuple(tuple(bundle) for bundle in result)


def scaled_owner(bundles, owner, scale):
    return tuple(tuple(scale * value for value in bundle) if i == owner else bundle
                 for i, bundle in enumerate(bundles))


class Model:
    def __init__(self, name, forms, owners):
        self.name = name
        self.forms = tuple(tuple(Q(x) for x in form) for form in forms)
        self.d = len(self.forms[0])
        self.n = owners
        require(self.n >= 1 and self.d >= 1 and self.forms, "model dimensions")
        require(all(len(w) == self.d and all(x >= 0 for x in w) for w in self.forms),
                "nonnegative equal-dimension forms")
        self.masks = tuple(range(1 << self.n))
        self.js = (2, 3, 7)
        self.cache = {}
        COUNTS["form_families"] += 1

    def direct_oracle(self, bundles, mask):
        # Independent reference path: sum RESOURCE bundles first, then price.
        aggregate = tuple(sum((bundles[i][e] for i in range(self.n)
                               if mask & (1 << i)), Q(0)) for e in range(self.d))
        scores = tuple(dot(aggregate, w) for w in self.forms)
        value = min(scores)
        family = tuple(k for k, score in enumerate(scores) if score == value)
        return value, family[0], family

    def reference_polynomials(self, bundles):
        # Enumerates only the OTHER-owner masks, expands Bernoulli factors by
        # polynomial multiplication, and integrates coefficients directly.
        total = self.direct_oracle(bundles, (1 << self.n) - 1)[0]
        result = []
        for owner in range(self.n):
            others = tuple(i for i in range(self.n) if i != owner)
            polynomial = (Q(0),)
            for bits in product((0, 1), repeat=len(others)):
                off = sum((1 << i) for i, bit in zip(others, bits) if bit)
                off_value, winner, _ = self.direct_oracle(bundles, off)
                on_value = self.direct_oracle(bundles, off | (1 << owner))[0]
                cap = min(dot(bundles[owner], self.forms[winner]), total)
                marginal = on_value - off_value
                payoff_poly = (marginal, cap - marginal)
                polynomial = padd(polynomial, pmul(probability_polynomial(bits), payoff_poly))
            require(len(polynomial) <= self.n + 1, "hybrid polynomial degree")
            result.append(polynomial)
        return tuple(result)

    def profile(self, bundles):
        bundles = tuple(tuple(Q(value) for value in b) for b in bundles)
        if bundles in self.cache:
            return self.cache[bundles]
        require(len(bundles) == self.n and all(len(b) == self.d for b in bundles),
                "bundle dimensions")
        require(all(x >= 0 for bundle in bundles for x in bundle), "negative bundle")
        # Sampler oracle path: price OWNERS separately, then sum scores.
        contributions = tuple(tuple(dot(bundle, w) for w in self.forms) for bundle in bundles)
        queries = []
        for mask in self.masks:
            scores = tuple(sum((contributions[i][k] for i in range(self.n)
                                if mask & (1 << i)), Q(0)) for k in range(len(self.forms)))
            value = min(scores)
            family = tuple(k for k, score in enumerate(scores) if score == value)
            query = (value, family[0], family)
            require(query == self.direct_oracle(bundles, mask), "independent oracle comparison")
            queries.append(query)
            COUNTS["oracle_crosschecks"] += 1
            if value > 0 and len(family) > 1:
                COUNTS["positive_value_tie_masks"] += 1
        total = queries[-1][0]
        if total == 0:
            COUNTS["zero_value_profiles"] += 1
        polynomials = self.reference_polynomials(bundles)
        samples = {}
        expectations = {}
        for j in self.js:
            probabilities, posteriors = distribution(self.n, j)
            values_by_mask = []
            average = [Q(0)] * self.n
            for mask in self.masks:
                queried = set()
                k = bin(mask).count("1")
                theta = posteriors[k]
                sample = []
                for i in range(self.n):
                    off, on = mask & ~(1 << i), mask | (1 << i)
                    queried.update((off, on))
                    cap = min(contributions[i][queries[off][1]], total)
                    marginal = queries[on][0] - queries[off][0]
                    value = theta * cap + (1 - theta) * marginal
                    require(0 <= cap <= total and 0 <= marginal <= total and 0 <= value <= total,
                            "fixed-mask estimator range")
                    sample.append(value)
                    average[i] += probabilities[k] * value
                    COUNTS["sample_coordinate_range_checks"] += 1
                expected_queries = {mask} | {mask ^ (1 << i) for i in range(self.n)}
                require(queried == expected_queries and len(queried) <= self.n + 1,
                        "n+1 distinct oracle query bound")
                COUNTS["mask_query_set_checks"] += 1
                values_by_mask.append(tuple(sample))
            independent = tuple(j * pintegral(poly, Q(1, j)) for poly in polynomials)
            require(tuple(average) == independent, "sampler/reference integrated expectations")
            COUNTS["independent_expectation_coordinate_checks"] += self.n
            for coalition in self.masks:
                require(sum(independent[i] for i in range(self.n) if coalition & (1 << i))
                        >= queries[coalition][0], "exact expectation coalition coverage")
                COUNTS["exact_expectation_coalition_checks"] += 1
            for eta in (Q(1, 5), Q(3, 2)):
                expected_cushioned = sum(average) + eta * total
                require(expected_cushioned == sum(independent) + eta * total,
                        "expected cushion total identity")
                COUNTS["expected_cushion_budget_checks"] += 1
                sequences = tuple((mask,) for mask in self.masks) + (
                    (0, self.masks[-1]), (self.masks[-1], self.masks[-1]),
                    (self.masks[-1] // 3, self.masks[-1] ^ (self.masks[-1] // 3)))
                for sequence in sequences:
                    mean = tuple(sum(values_by_mask[mask][i] for mask in sequence) / len(sequence)
                                 for i in range(self.n))
                    if all(abs(mean[i] - independent[i]) <= eta * total / self.n
                           for i in range(self.n)):
                        paid = tuple(value + eta * total / self.n for value in mean)
                        check_good_error_consequences(mean, independent, paid, total, eta,
                                                      tuple(query[0] for query in queries))
                        COUNTS["good_error_event_implications"] += 1
                    else:
                        COUNTS["sequences_outside_good_error_event"] += 1
            samples[j] = tuple(values_by_mask)
            expectations[j] = independent
        result = {"T": total, "queries": tuple(queries), "samples": samples,
                  "expectations": expectations}
        self.cache[bundles] = result
        COUNTS["profiles"] += 1
        return result

    def compare(self, lower, higher, owner):
        require(all(x <= y for x, y in zip(lower[owner], higher[owner])), "comparison order")
        require(all(lower[i] == higher[i] for i in range(self.n) if i != owner),
                "comparison changes another owner")
        low, high = self.profile(lower), self.profile(higher)
        require(low["T"] <= high["T"], "grand value monotonicity")
        for mask in self.masks:
            off = mask & ~(1 << owner)
            require(low["queries"][off] == high["queries"][off], "entire off family independence")
            COUNTS["off_family_independence_checks"] += 1
            for j in self.js:
                lo = low["samples"][j][mask][owner]
                hi = high["samples"][j][mask][owner]
                require(lo <= hi, "fixed-mask own-component monotonicity")
                COUNTS["fixed_mask_own_monotonicity_checks"] += 1
                for eta in (Q(1, 5), Q(3, 2)):
                    require(lo + eta * low["T"] / self.n <= hi + eta * high["T"] / self.n,
                            "cushioned fixed-mask own monotonicity")
                    COUNTS["cushioned_own_monotonicity_checks"] += 1
        COUNTS["own_report_comparisons"] += 1


def check_good_error_consequences(mean, target, payments, total, eta, coalition_values):
    n = len(mean)
    require(all(abs(a - b) <= eta * total / n for a, b in zip(mean, target)),
            "good-error precondition does not hold")
    require(all(paid >= exact for paid, exact in zip(payments, target)),
            "cushion failed coordinate domination")
    for coalition, value in enumerate(coalition_values):
        require(sum(payments[i] for i in range(n) if coalition & (1 << i)) >= value,
                "cushion failed coalition coverage")
    require(sum(payments) <= sum(target) + 2 * eta * total,
            "cushion exceeded conditional budget")


def make_profiles(model):
    n, d = model.n, model.d
    ones = tuple((Q(1),) * d for _ in range(n))
    pattern = (Q(0), Q(1, 3), Q(1), Q(5, 2), Q(2, 5), Q(3), Q(0), Q(7, 4))
    heterogeneous = tuple(tuple(pattern[(3 * i + e) % len(pattern)] for e in range(d))
                          for i in range(n))
    zero = tuple((Q(0),) * d for _ in range(n))
    first_only = tuple(tuple(Q(i + 1) if e == 0 else Q(0) for e in range(d))
                       for i in range(n))
    diagonal = tuple(tuple(Q(int(e == i % d)) for e in range(d)) for i in range(n))
    return (zero, ones, heterogeneous, first_only, diagonal), (ones, heterogeneous)


def negative_controls():
    probabilities, posteriors = distribution(3, 2)
    expect_rejection("posterior replaced by unconditional q mean", lambda: validate_distribution(
        3, 2, probabilities, (Q(1, 4),) * 4))
    wrong = list(posteriors)
    wrong[0] /= 2
    expect_rejection("one posterior halved", lambda: validate_distribution(3, 2, probabilities, tuple(wrong)))
    expect_rejection("mask probabilities missing density factor j", lambda: validate_distribution(
        3, 2, tuple(p / 2 for p in probabilities), posteriors))
    expect_rejection("cardinality mass used as individual mask mass", lambda: validate_distribution(
        3, 2, tuple(comb(3, k) * probabilities[k] for k in range(4)), posteriors))
    swapped = list(probabilities)
    swapped[0], swapped[3] = swapped[3], swapped[0]
    expect_rejection("normalization-preserving endpoint mass swap", lambda: validate_distribution(
        3, 2, tuple(swapped), posteriors))
    model = Model("cushion-calibration", ((1, 0), (0, 1)), 2)
    profile = model.profile(((Q(1), Q(0)), (Q(0), Q(1))))
    mean = profile["samples"][2][0]
    exact = profile["expectations"][2]
    require(mean == (Q(3, 8), Q(0)) and exact == (Q(5, 6), Q(3, 4)),
            "independent cushion calibration values")
    eta, total = Q(3, 2), profile["T"]
    values = tuple(query[0] for query in profile["queries"])
    good = tuple(value + eta * total / 2 for value in mean)
    check_good_error_consequences(mean, exact, good, total, eta, values)
    expect_rejection("omitted cushion on actual good-error sample", lambda:
                     check_good_error_consequences(mean, exact, mean, total, eta, values))
    undersized = tuple(value + eta * total / 8 for value in mean)
    expect_rejection("quarter-sized cushion on actual good-error sample", lambda:
                     check_good_error_consequences(mean, exact, undersized, total, eta, values))
    oversized = tuple(value + 3 * eta * total / 2 for value in mean)
    expect_rejection("oversized cushion violates claimed budget", lambda:
                     check_good_error_consequences(mean, exact, oversized, total, eta, values))
    expect_rejection("always-active require calibration", lambda: require(False, "intentional"))


def main():
    for n in range(1, 9):
        for j in (2, 3, 7, 31):
            distribution(n, j)
    specifications = (
        ("single-form-overlap", ((Q(2, 3), 3),), 3),
        ("two-complementary-forms", ((1, 0), (0, 1)), 3),
        ("two-form-large-intensity", ((1, 0), (Q(1, 7), Q(6, 7))), 3),
        ("fractional-three-resource", ((Q(1, 2), 3, 0), (2, 0, Q(1, 3)),
                                       (0, Q(4, 3), 2), (1, 1, 1)), 3),
        ("zero-form", ((0, 0), (1, 3)), 2),
        ("duplicate-priority-ties", ((1, 0, 2), (1, 0, 2), (0, 2, 1)), 3),
        ("four-resource-overlap", ((0, 3, Q(1, 5), 1), (2, 0, 1, 4),
                                    (1, 1, 0, 2), (5, Q(1, 7), 3, 0),
                                    (Q(1, 2), 2, 2, 1)), 4),
        ("single-owner-bundle", ((1, 0), (0, 2), (Q(1, 3), Q(1, 2))), 1),
    )
    inventory = []
    for specification in specifications:
        model = Model(*specification)
        profiles, contexts = make_profiles(model)
        for profile in profiles:
            model.profile(profile)
        for context in contexts:
            for owner in range(model.n):
                for coordinate in range(model.d):
                    reports = tuple(changed_bundle(context, owner, coordinate, value)
                                    for value in (Q(0), Q(1, 4), Q(1), Q(3, 2)))
                    for lower, higher in zip(reports, reports[1:]):
                        model.compare(lower, higher, owner)
                reports = tuple(scaled_owner(context, owner, scale)
                                for scale in (Q(0), Q(1, 3), Q(1), Q(2)))
                for lower, higher in zip(reports, reports[1:]):
                    model.compare(lower, higher, owner)
                    COUNTS["simultaneous_bundle_report_comparisons"] += 1
        inventory.append({"name": model.name, "owners": model.n, "resources": model.d,
                          "forms": len(model.forms), "profiles": len(model.cache)})
    negative_controls()
    require(COUNTS["positive_value_tie_masks"] > 0 and COUNTS["zero_value_profiles"] > 0,
            "zero/tie test coverage")
    require(COUNTS["good_error_event_implications"] > 0
            and COUNTS["sequences_outside_good_error_event"] > 0,
            "good-error tests must distinguish qualifying samples")
    print("PASS: exact finite raw-capped sampling verification")
    print(json.dumps({"counts": dict(sorted(COUNTS.items())), "families": inventory,
                      "rejected_corruptions": REJECTED}, indent=2, sort_keys=True))
    print("Finite exact checks only; no all-profile concentration claim is inferred.")


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
