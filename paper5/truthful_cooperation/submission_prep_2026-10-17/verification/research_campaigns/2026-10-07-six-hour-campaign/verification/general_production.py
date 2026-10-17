#!/usr/bin/env python3
"""Exact finite verifier for the RAW-capacity capped Bernoulli hybrid rule.

Python 3.8+, standard library plus sibling binary_packing.py (only its exact
linear-system solver is reused). --packing-verifier overrides the sibling path.
For F(c)=max r.x subject to A x<=c,x>=0, enumerate primal AND dual vertices.
Every activity column of A>=0 is nonzero; profits and reports are nonnegative.
Select a fixed-priority dual vertex w minimizing (c*B).w, with deletion q.
Use a_e(w)=min(c_e*w_e,F(c)), z_e=E[a_e], p_e=E[a_e|B_e=0],
m_e=E[F(c*B with e on)-F(c*B with e off)], r_e=q*p_e+(1-q)*m_e.

Masks, all coalitions, polynomials, integration, and logarithm enclosures use
Fraction arithmetic. Averaging is uniform on (0,1/j), j=2,3. Endpoint q=0,1
tests refer to polynomial continuation, not conditioning on null events.
Additional fixtures let owners report overlapping nonnegative resource bundles;
one mask removes one entire owner bundle, and reports increase componentwise.
Finite checks are not a proof of a general or asymptotic theorem.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util
from itertools import combinations
from math import comb
from pathlib import Path
import json
import random
import sys


COUNTS = Counter()
ZERO, X, ONE_MINUS_X = (Q(0),), (Q(0), Q(1)), (Q(1), Q(-1))
QS = (Q(0), Q(1, 7), Q(1, 3), Q(1, 2), Q(2, 3), Q(4, 5), Q(1))
JS = (2, 3)
REPORTS = (Q(0), Q(1, 3), Q(1), Q(2), Q(5, 2))
SOLVE = None


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def dot(left, right):
    return sum((a*b for a, b in zip(left, right)), Q(0))


def trim(poly):
    values = list(map(Q, poly))
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values) if values else ZERO


def add(*polys):
    out = [Q(0)] * max((len(poly) for poly in polys), default=1)
    for poly in polys:
        for k, coefficient in enumerate(poly):
            out[k] += coefficient
    return trim(out)


def scale(poly, scalar):
    return trim(coefficient*scalar for coefficient in poly)


def subtract(left, right):
    return add(left, scale(right, -1))


def multiply(left, right):
    out = [Q(0)] * (len(left)+len(right)-1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i+j] += a*b
    return trim(out)


def derivative(poly):
    return trim(k*coefficient for k, coefficient in enumerate(poly) if k)


def evaluate(poly, q):
    value = Q(0)
    for coefficient in reversed(poly):
        value = q*value+coefficient
    return value


def integrate(poly, b):
    return sum((coefficient*b**(k+1)/(k+1)
                for k, coefficient in enumerate(poly)), Q(0))


def weight_poly(zeros, ones):
    return trim([Q(0)]*zeros + [Q((-1)**k*comb(ones, k)) for k in range(ones+1)])


def complementary_integral(zeros, ones, b):
    # Independent integration in u=1-q, expanding (1-u)**zeros.
    return sum((Q((-1)**k*comb(zeros, k), ones+k+1)
                * (1-(1-b)**(ones+k+1)) for k in range(zeros+1)), Q(0))


def popcount(mask):
    return bin(mask).count("1")


def probability(n, mask, q, skip=None):
    value = Q(1)
    for e in range(n):
        if e != skip:
            value *= 1-q if mask & (1 << e) else q
    return value


@lru_cache(maxsize=None)
def dual_vertices(matrix, profits):
    n = len(matrix)
    rows = [(tuple(Q(int(e == h)) for h in range(n)), Q(0)) for e in range(n)]
    rows += [(tuple(matrix[e][j] for e in range(n)), profits[j])
             for j in range(len(profits))]
    vertices = set()
    for active in combinations(rows, n):
        w = SOLVE([row for row, _ in active], [bound for _, bound in active])
        if w is not None and all(dot(row, w) >= bound for row, bound in rows):
            vertices.add(w)
    require(vertices, "dual vertex enumeration empty")
    COUNTS["dual_systems_enumerated"] += 1
    COUNTS["dual_vertices_enumerated"] += len(vertices)
    return tuple(sorted(vertices))


@lru_cache(maxsize=None)
def primal_vertices(matrix, capacities):
    m = len(matrix[0])
    rows = [(tuple(Q(-int(j == h)) for h in range(m)), Q(0)) for j in range(m)]
    rows += list(zip(matrix, capacities))
    vertices = set()
    for active in combinations(rows, m):
        x = SOLVE([row for row, _ in active], [bound for _, bound in active])
        if x is not None and all(dot(row, x) <= bound for row, bound in rows):
            vertices.add(x)
    require(vertices, "primal vertex enumeration empty")
    COUNTS["primal_systems_enumerated"] += 1
    COUNTS["primal_vertices_enumerated"] += len(vertices)
    return tuple(sorted(vertices))


@lru_cache(maxsize=None)
def log_enclosure(x, terms=24):
    """Rational lower/upper enclosure of log(x), x>=1, using atanh series."""
    x = Q(x)
    require(x >= 1, "log enclosure needs x>=1")
    y = (x-1)/(x+1)
    lower = 2*sum((y**(2*k+1)/(2*k+1) for k in range(terms)), Q(0))
    tail_bound = 2*y**(2*terms+1)/((2*terms+1)*(1-y*y))
    return lower, lower+tail_bound


@lru_cache(maxsize=None)
def finite_bound_enclosure(k, j):
    lo_k, hi_k = log_enclosure(Q(k))
    lo_j, hi_j = log_enclosure(Q(j))
    denominator = Q(j**3, j*j+j-1)
    lo_d, hi_d = log_enclosure(denominator)
    require(lo_d > 0, "positive Chernoff denominator")
    return (j+(lo_k+2*lo_j+1)/hi_d, j+(hi_k+2*hi_j+1)/lo_d)


class Technology:
    def __init__(self, name, matrix, profits, reverse=False):
        self.name = name + ("/reverse" if reverse else "/lexicographic")
        self.matrix = tuple(tuple(map(Q, row)) for row in matrix)
        self.profits = tuple(map(Q, profits))
        self.n, self.m = len(self.matrix), len(self.profits)
        require(self.n >= 1 and all(len(row) == self.m for row in self.matrix), "matrix dimensions")
        require(all(a >= 0 for row in self.matrix for a in row), "negative consumption")
        require(all(r >= 0 for r in self.profits), "negative profit")
        require(all(any(self.matrix[e][j] > 0 for e in range(self.n))
                    for j in range(self.m)), "zero activity column")
        vertices = dual_vertices(self.matrix, self.profits)
        self.vertices = tuple(reversed(vertices)) if reverse else vertices
        self.masks = tuple(range(1 << self.n))
        self.value_cache, self.cache = {}, {}
        COUNTS["technology_priority_pairs"] += 1

    def value(self, capacities):
        if capacities not in self.value_cache:
            primal = max(dot(self.profits, x) for x in primal_vertices(self.matrix, capacities))
            dual = min(dot(capacities, w) for w in self.vertices)
            require(primal == dual, "primal/dual disagreement: " + self.name)
            self.value_cache[capacities] = primal
            COUNTS["primal_dual_value_crosschecks"] += 1
        return self.value_cache[capacities]

    def owner_contributions(self, reports, vertex):
        return tuple(reports[e]*vertex[e] for e in range(self.n))

    def profile(self, capacities):
        c = tuple(map(Q, capacities))
        if c in self.cache:
            return self.cache[c]
        require(len(c) == self.n and all(value >= 0 for value in c), "invalid capacities")
        label = "%s c=%s" % (self.name, c)
        total = self.value(c)
        values, winners, payments = [], [], []
        for mask in self.masks:
            masked = tuple(c[e] if mask & (1 << e) else Q(0) for e in range(self.n))
            scores = [dot(masked, vertex) for vertex in self.vertices]
            value = min(scores)
            require(value == self.value(masked), "masked primal/dual equality: " + label)
            require(value <= total, "masked value at most T: " + label)
            winner = self.vertices[scores.index(value)]
            a = tuple(min(c[e]*winner[e], total) for e in range(self.n))
            for e in range(self.n):
                require(0 <= a[e] <= total, "capped coefficient bound: " + label)
                if mask & (1 << e):
                    require(a[e] == c[e]*winner[e], "selected open contribution changed by cap: " + label)
                    COUNTS["open_selected_cap_inactive_checks"] += 1
                elif a[e] < c[e]*winner[e]:
                    COUNTS["selected_closed_cap_active_coordinates"] += 1
            require(sum((a[e] for e in range(self.n) if mask & (1 << e)), Q(0)) == value,
                    "open capped sum equals masked value: " + label)
            values.append(value)
            winners.append(winner)
            payments.append(a)
            COUNTS["masked_value_checks"] += 1
        # Check coverage for EVERY dual vertex, including vertices never selected.
        for vertex in self.vertices:
            a = tuple(min(c[e]*vertex[e], total) for e in range(self.n))
            for coalition in self.masks:
                require(sum((a[e] for e in range(self.n) if coalition & (1 << e)), Q(0))
                        >= values[coalition], "capped vertex coalition coverage: " + label)
                COUNTS["capped_vertex_coalition_certificates"] += 1
        return self.finish_profile(c, total, values, winners, payments, label)

    def finish_profile(self, c, total, values, winners, payments, label):
        """Common owner-mask algebra for scalar resources and vector bundles."""
        g = ZERO
        z, p, m = ([ZERO]*self.n for _ in range(3))
        for mask in self.masks:
            ones = popcount(mask)
            weight = weight_poly(self.n-ones, ones)
            g = add(g, scale(weight, values[mask]))
            for e in range(self.n):
                z[e] = add(z[e], scale(weight, payments[mask][e]))
        marginals, r = {}, []
        for e in range(self.n):
            slack = ZERO
            for off in self.masks:
                if off & (1 << e):
                    continue
                on = off | (1 << e)
                delta = values[on]-values[off]
                marginals[e, off] = delta
                require(0 <= payments[on][e] <= delta <= payments[off][e],
                        "capped marginal sandwich: " + label)
                ones = popcount(off)
                weight = weight_poly(self.n-1-ones, ones)
                p[e] = add(p[e], scale(weight, payments[off][e]))
                m[e] = add(m[e], scale(weight, delta))
                slack = add(slack, scale(multiply(ONE_MINUS_X, weight), delta-payments[on][e]))
                COUNTS["pointwise_capped_marginal_sandwiches"] += 1
            r.append(add(multiply(X, p[e]), multiply(ONE_MINUS_X, m[e])))
            require(subtract(r[e], z[e]) == slack, "all-q domination polynomial: " + label)
            COUNTS["all_q_domination_polynomial_identities"] += 1
        Z, P, M, R = (add(*items) for items in (z, p, m, r))
        require(multiply(X, P) == subtract(Z, g), "qP=Z-g: " + label)
        require(M == scale(derivative(g), -1), "M=-g': " + label)
        require(R == subtract(subtract(Z, g), multiply(ONE_MINUS_X, derivative(g))),
                "R=Z-g-(1-q)g': " + label)
        require(evaluate(g, Q(0)) == total and evaluate(g, Q(1)) == 0, "g endpoints: " + label)
        COUNTS["budget_polynomial_identities"] += 3
        result = {"c": c, "T": total, "g": g, "Z": Z, "R": R,
                  "p": tuple(p), "m": tuple(m), "z": tuple(z), "r": tuple(r),
                  "values": tuple(values), "winners": tuple(winners), "a": tuple(payments),
                  "marginals": marginals, "averages": {}}
        for q in QS:
            direct = self.direct(result, q=q)
            require(direct["g"] == evaluate(g, q), "direct scalar g")
            for name in ("p", "m", "z", "r"):
                require(direct[name] == tuple(evaluate(poly, q) for poly in result[name]), "direct scalar " + name)
                COUNTS["scalar_direct_polynomial_coordinate_checks"] += self.n
            self.check_domination_and_coalitions(result, direct, "scalar", label)
        for j in JS:
            b = Q(1, j)
            direct = self.direct(result, b=b)
            require(direct["g"] == integrate(g, b)/b, "direct averaged g")
            for name in ("p", "m", "z", "r"):
                require(direct[name] == tuple(integrate(poly, b)/b for poly in result[name]), "independent average " + name)
                COUNTS["independent_integration_coordinate_checks"] += self.n
            self.check_domination_and_coalitions(result, direct, "integrated", label)
            require(integrate(R, b) == integrate(Z, b)+total-(1-b)*evaluate(g, b)-2*integrate(g, b),
                    "integrated hybrid identity: " + label)
            require(sum(direct["r"], Q(0)) <= j*total+sum(direct["z"], Q(0)), "T/b plus average Z budget")
            # Compare to a LOWER enclosure of the stated bound, so passing is a
            # rational certificate of the true logarithmic inequality.
            lower_bound, _ = finite_bound_enclosure(len(self.vertices), j)
            require(sum(direct["r"], Q(0)) <= total*lower_bound, "certified finite-K logarithmic budget")
            result["averages"][j] = direct
            COUNTS["integrated_budget_identity_checks"] += 1
            COUNTS["certified_finite_K_budget_checks"] += 1
        COUNTS["profiles"] += 1
        self.cache[c] = result
        return result

    def direct(self, profile, q=None, b=None, uncapped=False):
        require((q is None) != (b is None), "choose scalar OR averaged probability")
        p, m, z, r = ([Q(0)]*self.n for _ in range(4))
        g, mass = Q(0), Q(0)
        a = (tuple(self.owner_contributions(profile["c"], w) for w in profile["winners"])
             if uncapped else profile["a"])
        for mask in self.masks:
            ones = popcount(mask)
            weight = (probability(self.n, mask, q) if q is not None
                      else complementary_integral(self.n-ones, ones, b)/b)
            mass += weight
            g += weight*profile["values"][mask]
            for e in range(self.n):
                z[e] += weight*a[mask][e]
        require(mass == 1, "full probability normalization")
        for e in range(self.n):
            mass = Q(0)
            for off in self.masks:
                if off & (1 << e):
                    continue
                ones, zeros = popcount(off), self.n-1-popcount(off)
                weight = (probability(self.n, off, q, skip=e) if q is not None
                          else complementary_integral(zeros, ones, b)/b)
                mass += weight
                pe, me = a[off][e], profile["marginals"][e, off]
                p[e] += weight*pe
                m[e] += weight*me
                if b is not None:
                    r[e] += (complementary_integral(zeros+1, ones, b)*pe
                             + complementary_integral(zeros, ones+1, b)*me)/b
            require(mass == 1, "conditional probability normalization")
            if q is not None:
                r[e] = q*p[e]+(1-q)*m[e]
        return {"p": tuple(p), "m": tuple(m), "z": tuple(z), "r": tuple(r), "g": g}

    def check_domination_and_coalitions(self, profile, direct, mode, label):
        require(all(re >= ze >= 0 for re, ze in zip(direct["r"], direct["z"])), "r>=z: " + label)
        COUNTS[mode+"_domination_coordinate_checks"] += self.n
        for coalition in self.masks:
            for name in ("z", "r"):
                payment = sum((direct[name][e] for e in range(self.n) if coalition & (1 << e)), Q(0))
                require(payment >= profile["values"][coalition], name+" coalition coverage: " + label)
                COUNTS[mode+"_"+name+"_coalition_checks"] += 1

    def own_reports(self, context, e, reports=REPORTS):
        profiles = []
        for report in reports:
            capacities = list(context)
            capacities[e] = report
            profiles.append(self.profile(capacities))
        self.check_ordered_profiles(profiles, e)

    def check_ordered_profiles(self, profiles, e):
        for lower, upper in zip(profiles, profiles[1:]):
            require(lower["T"] <= upper["T"], "own T monotonicity")
            for off in self.masks:
                if off & (1 << e):
                    continue
                require(lower["winners"][off] == upper["winners"][off], "off-mask winner own-report invariance")
                require(lower["a"][off][e] <= upper["a"][off][e], "pointwise capped p own monotonicity")
                require(lower["marginals"][e, off] <= upper["marginals"][e, off], "pointwise marginal own monotonicity")
                COUNTS["off_winner_invariance_checks"] += 1
                COUNTS["pointwise_own_monotonicity_checks"] += 2
            for q in QS:
                for name in ("p", "m", "r"):
                    require(evaluate(lower[name][e], q) <= evaluate(upper[name][e], q), "scalar own monotonicity " + name)
                    COUNTS["scalar_own_"+name+"_monotonicity_checks"] += 1
            for j in JS:
                for name in ("p", "m", "r"):
                    require(lower["averages"][j][name][e] <= upper["averages"][j][name][e], "averaged own monotonicity " + name)
                    COUNTS["integrated_own_"+name+"_monotonicity_checks"] += 1
        COUNTS["own_report_families"] += 1


class BundleTechnology(Technology):
    """Owners report nonnegative vectors; masks remove whole owner bundles."""
    def __init__(self, name, matrix, profits, owners, reverse=False):
        super().__init__(name, matrix, profits, reverse=reverse)
        self.resource_count = self.n
        self.n = owners
        self.masks = tuple(range(1 << owners))

    def owner_contributions(self, reports, vertex):
        return tuple(dot(bundle, vertex) for bundle in reports)

    def profile(self, bundles):
        bundles = tuple(tuple(map(Q, bundle)) for bundle in bundles)
        if bundles in self.cache:
            return self.cache[bundles]
        require(len(bundles) == self.n and all(len(bundle) == self.resource_count for bundle in bundles),
                "owner bundle dimensions")
        require(all(value >= 0 for bundle in bundles for value in bundle), "negative bundle report")
        label = "%s bundles=%s" % (self.name, bundles)
        capacities = tuple(sum((bundle[h] for bundle in bundles), Q(0)) for h in range(self.resource_count))
        total = self.value(capacities)
        values, winners, payments = [], [], []
        for mask in self.masks:
            masked = tuple(sum((bundles[e][h] for e in range(self.n) if mask & (1 << e)), Q(0))
                           for h in range(self.resource_count))
            scores = [dot(masked, vertex) for vertex in self.vertices]
            minimum = min(scores)
            require(minimum == self.value(masked) and minimum <= total, "bundle mask primal/dual value")
            winner = self.vertices[scores.index(minimum)]
            contributions = tuple(dot(bundle, winner) for bundle in bundles)
            a = tuple(min(contribution, total) for contribution in contributions)
            for e in range(self.n):
                require(0 <= a[e] <= total, "capped owner-bundle coefficient")
                if mask & (1 << e):
                    require(a[e] == contributions[e], "open bundle contribution changed by cap")
                    COUNTS["open_selected_cap_inactive_checks"] += 1
                elif a[e] < contributions[e]:
                    COUNTS["selected_closed_cap_active_coordinates"] += 1
            require(sum((a[e] for e in range(self.n) if mask & (1 << e)), Q(0)) == minimum,
                    "sum of open bundle contributions")
            values.append(minimum)
            winners.append(winner)
            payments.append(a)
            COUNTS["bundle_masked_value_checks"] += 1
        for vertex in self.vertices:
            a = tuple(min(dot(bundle, vertex), total) for bundle in bundles)
            for coalition in self.masks:
                require(sum((a[e] for e in range(self.n) if coalition & (1 << e)), Q(0)) >= values[coalition],
                        "capped dual vertex covers owner-bundle coalition")
                COUNTS["capped_vertex_coalition_certificates"] += 1
        COUNTS["bundle_profiles"] += 1
        return self.finish_profile(bundles, total, values, winners, payments, label)

    def own_component_reports(self, context, owner, resource, reports=REPORTS):
        profiles = []
        for report in reports:
            bundles = [list(bundle) for bundle in context]
            bundles[owner][resource] = report
            profiles.append(self.profile(bundles))
        self.check_ordered_profiles(profiles, owner)
        COUNTS["bundle_own_component_report_families"] += 1


def expect_rejected(label, operation):
    try:
        operation()
    except VerificationError:
        COUNTS["negative_controls_rejected"] += 1
        return
    raise VerificationError("negative control accepted: " + label)


def calibrate():
    require(SOLVE(((2, 1), (1, -1)), (1, 2)) == (Q(1), Q(-1)), "linear solver calibration")
    require(SOLVE(((1, 1), (2, 2)), (1, 2)) is None, "singular solver calibration")
    for zeros in range(6):
        for ones in range(6):
            poly = weight_poly(zeros, ones)
            for q in QS:
                require(evaluate(poly, q) == q**zeros*(1-q)**ones, "mask polynomial calibration")
            for j in JS:
                require(integrate(poly, Q(1, j)) == complementary_integral(zeros, ones, Q(1, j)), "integration calibration")
            require(integrate(poly, Q(1)) == Q(1, (zeros+ones+1)*comb(zeros+ones, zeros)), "beta integral calibration")
    lo2, hi2 = log_enclosure(Q(2))
    lo4, hi4 = log_enclosure(Q(4))
    require(lo2 <= hi2 and max(2*lo2, lo4) <= min(2*hi2, hi4), "log doubling enclosure consistency")
    require(log_enclosure(Q(1)) == (Q(0), Q(0)), "log one")
    expect_rejected("always-active checks", lambda: require(False, "deliberate"))
    expect_rejected("zero activity column", lambda: Technology("invalid", ((1, 0), (0, 0)), (1, 1)))
    COUNTS["calibration_checks"] += 4+36*(len(QS)+len(JS)+1)


def negative_controls(single, serial):
    s, t = single.profile((Q(1),)), serial.profile((Q(1),)*serial.n)
    expect_rejected("wrong derivative sign", lambda: require(add(*s["m"]) == derivative(s["g"]), "wrong M sign"))
    expect_rejected("wrong budget sign", lambda: require(s["R"] == add(subtract(s["Z"], s["g"]), multiply(ONE_MINUS_X, derivative(s["g"]))), "wrong R sign"))
    expect_rejected("swapped mixing weights", lambda: require(t["R"] == add(multiply(ONE_MINUS_X, add(*t["p"])), multiply(X, add(*t["m"]))), "wrong mixture"))
    q = Q(1, 3)
    expect_rejected("unconditional p undercovers", lambda: require(q*q*evaluate(s["p"][0], q)+(1-q)*evaluate(s["m"][0], q) >= s["T"], "undercoverage"))
    b = Q(1, 2)
    expect_rejected("missing second g integral", lambda: require(integrate(s["R"], b) == integrate(s["Z"], b)+s["T"]-(1-b)*evaluate(s["g"], b)-integrate(s["g"], b), "wrong integral"))
    expect_rejected("missing normalization", lambda: require(integrate(s["R"], b) == s["averages"][2]["r"][0], "wrong normalization"))


def profiles_and_contexts(n):
    zero, unit = (Q(0),)*n, (Q(1),)*n
    positive = tuple((Q(1, 5), Q(7, 6), Q(3), Q(2, 3))[e % 4] for e in range(n))
    mixed = tuple((Q(0), Q(2), Q(5, 4), Q(0))[e % 4] for e in range(n))
    profiles = {zero, unit, positive, mixed, (Q(1, 2),)*n}
    for e in range(n):
        singleton, deletion = list(zero), list(unit)
        singleton[e], deletion[e] = Q(1), Q(0)
        profiles.update((tuple(singleton), tuple(deletion)))
    return tuple(sorted(profiles)), (unit, positive, mixed)


def random_specifications():
    rng = random.Random(20261007)
    coefficients = (Q(0), Q(1, 3), Q(1, 2), Q(1), Q(2), Q(3))
    profits = (Q(0), Q(1, 2), Q(1), Q(3, 2), Q(3))
    for n, count in ((2, 12), (3, 8)):
        for index in range(count):
            matrix = [[rng.choice(coefficients) for _ in range(n)] for _ in range(n)]
            for j in range(n):
                if not any(matrix[e][j] for e in range(n)):
                    matrix[rng.randrange(n)][j] = Q(1)
            yield ("seeded-%dx%d-%02d" % (n, n, index), tuple(map(tuple, matrix)),
                   tuple(rng.choice(profits) for _ in range(n)))


def main():
    global SOLVE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packing-verifier", type=Path,
                        default=Path(__file__).resolve().with_name("binary_packing.py"))
    args = parser.parse_args()
    path = args.packing_verifier.resolve()
    require(path.is_file(), "missing solver support: " + str(path))
    spec = importlib.util.spec_from_file_location("general_hybrid_solver", path)
    require(spec is not None and spec.loader is not None, "solver import")
    support = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(support)
    SOLVE = support.solve_square
    calibrate()
    fixtures = (
        ("single-resource", ((1,),), (1,)),
        ("serial-three", ((1,), (1,), (1,)), (1,)),
        ("fractional-triangle", ((1, 1, 0), (1, 0, 1), (0, 1, 1)), (1, 1, 1)),
        ("heterogeneous-profits", ((1, 1, 0), (1, 0, 1), (0, 1, 1)), (Q(1, 2), 2, 3)),
        ("heterogeneous-coefficients", ((Q(1, 2), 2), (3, Q(1, 3))), (Q(3, 2), Q(5, 4))),
        ("zero-profit-activity", ((1, 3), (1, 0)), (1, 0)),
        ("all-zero-profits", ((1, 2), (3, Q(1, 2))), (0, 0)),
        ("unused-resource", ((1, 0), (0, 2), (0, 0)), (1, 3)),
        ("nonclutter-equivalent", ((1, 1, 0), (0, 1, 1), (0, 0, 1)), (1, 1, 1)),
        ("empty-activity-family", ((), ()), ()),
    )
    obstruction_specs = tuple(("uncapped-obstruction-M%d" % m, ((1, m), (1, 0)), (1, 1))
                              for m in (2, 3, 10, 100))
    specifications = fixtures + obstruction_specs + tuple(random_specifications())
    inventory, obstruction_results = [], []
    for reverse in (False, True):
        technologies = [Technology(*item, reverse=reverse) for item in specifications]
        negative_controls(technologies[0], technologies[1])
        for technology in technologies:
            profiles, contexts = profiles_and_contexts(technology.n)
            for capacities in profiles:
                technology.profile(capacities)
            for context in contexts:
                for e in range(technology.n):
                    technology.own_reports(context, e)
            if technology.name.startswith("uncapped-obstruction-M"):
                m = technology.matrix[0][1]
                profile = technology.profile((m, Q(1)))
                expected = tuple(sorted(((Q(1), Q(0)), (1/m, 1-1/m))))
                require(tuple(sorted(technology.vertices)) == expected, "obstruction dual vertices")
                require(profile["T"] == 2-1/m, "obstruction primal value")
                expect_rejected("uncapped coefficient bound", lambda: require(
                    all(profile["c"][e]*w[e] <= profile["T"] for w in technology.vertices
                        for e in range(technology.n)), "uncapped coefficient exceeds T"))
                uncapped = technology.direct(profile, b=Q(1, 2), uncapped=True)
                capped_total = sum(profile["averages"][2]["r"], Q(0))
                uncapped_total = sum(uncapped["r"], Q(0))
                require(capped_total == (31*m-19)/(12*m), "closed-form capped obstruction budget")
                expected_uncapped = (m/4+Q(25, 12)-Q(4, 3)/m if reverse
                                     else m/6+Q(9, 4)-Q(17, 12)/m)
                require(uncapped_total == expected_uncapped, "closed-form uncapped obstruction budget")
                COUNTS["obstruction_closed_form_budget_checks"] += 2
                if m == 100:
                    _, upper_bound = finite_bound_enclosure(2, 2)
                    require(uncapped_total > profile["T"]*upper_bound,
                            "M=100 must violate the former uncapped finite-K bound")
                    expect_rejected("old uncapped budget claim", lambda: require(
                        uncapped_total <= profile["T"]*upper_bound, "uncapped finite-K bound false"))
                    COUNTS["certified_uncapped_finite_K_counterexamples"] += 1
                technology.own_reports((m, Q(1)), 0, reports=(Q(0), Q(1), m, 2*m))
                technology.own_reports((m, Q(1)), 1, reports=(Q(0), Q(1, 2), Q(1), Q(2)))
                obstruction_results.append({"name": technology.name, "T": str(profile["T"]),
                    "averaged_capped_total": str(capped_total), "averaged_uncapped_total": str(uncapped_total),
                    "capped_ratio": str(capped_total/profile["T"]), "uncapped_ratio": str(uncapped_total/profile["T"])})
            inventory.append({"name": technology.name, "resources": technology.n,
                "activities": technology.m, "dual_vertices": len(technology.vertices),
                "profiles": len(technology.cache), "A": [[str(a) for a in row] for row in technology.matrix],
                "profits": list(map(str, technology.profits))})
            print("checked " + technology.name, file=sys.stderr, flush=True)
    bundle_specs = (
        ("bundle-overlapping-obstruction", ((1, 3), (1, 0)), (1, 1), 2,
         (((1, 1), (2, 0)), ((Q(1, 2), 2), (3, Q(1, 2))))),
        ("bundle-three-owners-two-types", ((1, 0), (0, 1)), (1, 2), 3,
         (((1, 1), (2, 0), (0, 2)), ((0, 0), (Q(1, 2), 1), (2, Q(1, 3))))),
        ("bundle-fractional-triangle", ((1, 1, 0), (1, 0, 1), (0, 1, 1)), (1, 2, Q(3, 2)), 3,
         (((1, 0, 1), (0, 1, 1), (1, 1, 0)), ((0, 0, 0), (2, 1, 0), (Q(1, 2), 0, 2)))),
    )
    for reverse in (False, True):
        for name, matrix, profits, owners, contexts in bundle_specs:
            technology = BundleTechnology(name, matrix, profits, owners, reverse=reverse)
            technology.profile(tuple((Q(0),)*technology.resource_count for _ in range(owners)))
            for context in contexts:
                technology.profile(context)
                for owner in range(owners):
                    for resource in range(technology.resource_count):
                        technology.own_component_reports(context, owner, resource)
            inventory.append({"name": technology.name, "owners": owners,
                "resource_types": technology.resource_count, "activities": technology.m,
                "dual_vertices": len(technology.vertices), "profiles": len(technology.cache),
                "A": [[str(a) for a in row] for row in technology.matrix],
                "profits": list(map(str, technology.profits))})
            print("checked " + technology.name, file=sys.stderr, flush=True)
    print("PASS: exact finite raw-capacity capped general-LP hybrid checks, including owner bundles")
    print("Interior q=1/7,1/3,1/2,2/3,4/5; endpoint polynomial continuations 0,1; averaging b=1/2,1/3")
    print(json.dumps({"counts": dict(sorted(COUNTS.items())), "uncapped_obstructions": obstruction_results,
                      "technologies": inventory}, indent=2, sort_keys=True))
    print("All arithmetic, including budget comparisons, uses exact rationals and rigorous log enclosures.")
    print("Finite verification only; no general/asymptotic/novelty claim is inferred.")


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
