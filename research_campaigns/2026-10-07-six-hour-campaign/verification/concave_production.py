#!/usr/bin/env python3
"""Exact finite checks of extended-support concave-production payments.

Standalone stdlib; Python 3.8+. None denotes a +infinity coefficient; infinity
times zero is zero, and no infinities are subtracted. Tests use actual analytic
support forms, not a finite polyhedral approximation. Finite profile evidence
does not prove the general theorem. JSON stdout only; no file writes.
"""

from collections import Counter
from fractions import Fraction as Q
from itertools import product
from math import comb
import json
import sys


C = Counter()
ZERO, X, ONE_MINUS_X = (Q(0),), (Q(0), Q(1)), (Q(1), Q(-1))
QS = (Q(0), Q(1, 3), Q(1, 2), Q(2, 3), Q(1))
JS = (2, 3)
GRID = (Q(0), Q(1, 2), Q(2))


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
    out = [Q(0)]*max((len(poly) for poly in polys), default=1)
    for poly in polys:
        for k, coefficient in enumerate(poly):
            out[k] += coefficient
    return trim(out)


def scale(poly, factor):
    return trim(x*factor for x in poly)


def sub(a, b):
    return add(a, scale(b, -1))


def mul(a, b):
    out = [Q(0)]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return trim(out)


def derivative(poly):
    return trim(k*x for k, x in enumerate(poly) if k)


def evaluate(poly, q):
    result = Q(0)
    for coefficient in reversed(poly):
        result = q*result+coefficient
    return result


def integral(poly, b):
    return sum((x*b**(k+1)/(k+1) for k, x in enumerate(poly)), Q(0))


def weight(zeros, ones):
    return trim([Q(0)]*zeros+[Q((-1)**k*comb(ones, k)) for k in range(ones+1)])


def complement_integral(zeros, ones, b):
    return sum((Q((-1)**k*comb(zeros, k), ones+k+1)*(1-(1-b)**(ones+k+1))
                for k in range(zeros+1)), Q(0))


def extended_dot(coefficients, vector):
    result = Q(0)
    for coefficient, value in zip(coefficients, vector):
        require(value >= 0, "negative extended-form argument")
        if coefficient is None:
            if value > 0:
                return None
        else:
            require(coefficient >= 0, "negative support coefficient")
            result += coefficient*value
    return result


def capped(value, total):
    return total if value is None else min(value, total)


def production(name, vector):
    x, y = vector
    if name == "harmonic":
        return x*y/(x+y) if x+y else Q(0)
    if name == "boundary-jump":
        return x if y > 0 else Q(0)
    if name == "zero":
        return Q(0)
    if name == "linear":
        return 2*x+3*y
    raise VerificationError("unknown production function")


def support(name, vector):
    x, y = vector
    if name == "harmonic":
        interior = (y*y/(x+y)**2, x*x/(x+y)**2) if x*y else (Q(0), Q(0))
    elif name == "boundary-jump":
        interior = (Q(1), Q(0)) if x*y else (Q(0), Q(0))
    elif name == "zero":
        interior = (Q(0), Q(0))
    elif name == "linear":
        interior = (Q(2), Q(3))
    else:
        raise VerificationError("unknown support selector")
    return tuple(coefficient if coordinate > 0 else None
                 for coefficient, coordinate in zip(interior, vector))


class Verifier:
    def __init__(self, name, owners):
        self.name, self.n = name, owners
        self.masks = tuple(range(1 << owners))
        self.cache = {}

    def profile(self, flat):
        flat = tuple(map(Q, flat))
        if flat in self.cache:
            return self.cache[flat]
        require(len(flat) == 2*self.n and all(x >= 0 for x in flat), "report dimension/domain")
        bundles = tuple(flat[2*i:2*i+2] for i in range(self.n))
        aggregates = tuple(tuple(sum((bundles[i][h] for i in range(self.n) if mask & (1 << i)), Q(0))
                                 for h in range(2)) for mask in self.masks)
        values = tuple(production(self.name, x) for x in aggregates)
        total = values[-1]
        forms = tuple(support(self.name, x) for x in aggregates)
        contributions = []
        for mask in self.masks:
            require(extended_dot(forms[mask], aggregates[mask]) == values[mask], "selected support touching")
            a = []
            for i, bundle in enumerate(bundles):
                raw = extended_dot(forms[mask], bundle)
                a.append(capped(raw, total))
                require(0 <= a[-1] <= total, "finite capped coordinate bound")
                if raw is None:
                    C["infinite_uncapped_owner_contributions"] += 1
                if mask & (1 << i):
                    require(raw is not None and a[-1] == raw, "open owner cap/finite identity")
                    C["selected_open_finite_coordinate_checks"] += 1
            require(sum((a[i] for i in range(self.n) if mask & (1 << i)), Q(0)) == values[mask],
                    "selected OPEN sum identity")
            C["selected_open_sum_identities"] += 1
            for coalition in self.masks:
                raw_value = extended_dot(forms[mask], aggregates[coalition])
                require(raw_value is None or raw_value >= values[coalition], "extended support majorization")
                require(sum((a[i] for i in range(self.n) if coalition & (1 << i)), Q(0)) >= values[coalition],
                        "maskwise capped coalition certificate")
                C["maskwise_support_and_coverage_checks"] += 1
            contributions.append(tuple(a))
        g, z, p, marginal = ZERO, [ZERO]*self.n, [ZERO]*self.n, [ZERO]*self.n
        for mask in self.masks:
            ones = bin(mask).count("1")
            poly = weight(self.n-ones, ones)
            g = add(g, scale(poly, values[mask]))
            for i in range(self.n):
                z[i] = add(z[i], scale(poly, contributions[mask][i]))
        deltas, hybrid = {}, []
        for i in range(self.n):
            slack = ZERO
            for off in self.masks:
                if off & (1 << i):
                    continue
                on = off | (1 << i)
                delta = values[on]-values[off]
                deltas[i, off] = delta
                require(0 <= contributions[on][i] <= delta <= contributions[off][i] <= total,
                        "endpoint capped sandwich")
                ones = bin(off).count("1")
                poly = weight(self.n-1-ones, ones)
                p[i] = add(p[i], scale(poly, contributions[off][i]))
                marginal[i] = add(marginal[i], scale(poly, delta))
                slack = add(slack, scale(mul(ONE_MINUS_X, poly), delta-contributions[on][i]))
                C["endpoint_sandwich_checks"] += 1
            hybrid.append(add(mul(X, p[i]), mul(ONE_MINUS_X, marginal[i])))
            require(sub(hybrid[i], z[i]) == slack, "all-q domination polynomial")
            C["all_q_domination_polynomial_identities"] += 1
        Z, P, M, R = (add(*items) for items in (z, p, marginal, hybrid))
        require(mul(X, P) == sub(Z, g), "qP=Z-g")
        require(M == scale(derivative(g), -1), "M=-g'")
        require(R == sub(sub(Z, g), mul(ONE_MINUS_X, derivative(g))), "hybrid polynomial budget")
        require(evaluate(g, Q(0)) == total and evaluate(g, Q(1)) == 0, "g endpoints")
        C["budget_polynomial_identities"] += 3
        result = {"flat": flat, "T": total, "values": values, "forms": forms,
                  "a": tuple(contributions), "deltas": deltas, "g": g, "Z": Z, "R": R,
                  "z": tuple(z), "p": tuple(p), "m": tuple(marginal), "r": tuple(hybrid), "avg": {}}
        for q in QS:
            direct_p, direct_m, direct_z = [Q(0)]*self.n, [Q(0)]*self.n, [Q(0)]*self.n
            for mask in self.masks:
                probability = Q(1)
                for i in range(self.n):
                    probability *= 1-q if mask & (1 << i) else q
                for i in range(self.n):
                    direct_z[i] += probability*contributions[mask][i]
            for i in range(self.n):
                for off in self.masks:
                    if off & (1 << i):
                        continue
                    probability = Q(1)
                    for h in range(self.n):
                        if h != i:
                            probability *= 1-q if off & (1 << h) else q
                    direct_p[i] += probability*contributions[off][i]
                    direct_m[i] += probability*deltas[i, off]
            direct_r = tuple(q*pe+(1-q)*me for pe, me in zip(direct_p, direct_m))
            for key, direct in (("p", direct_p), ("m", direct_m), ("z", direct_z), ("r", direct_r)):
                require(tuple(evaluate(poly, q) for poly in result[key]) == tuple(direct), "direct scalar expectation")
                C["scalar_coordinate_crosschecks"] += self.n
            require(all(0 <= ze <= re <= total for ze, re in zip(direct_z, direct_r)), "scalar domination and owner bound")
            for coalition in self.masks:
                require(sum((direct_r[i] for i in range(self.n) if coalition & (1 << i)), Q(0)) >= values[coalition], "scalar coalition coverage")
                C["scalar_coalition_checks"] += 1
        for j in JS:
            b = Q(1, j)
            averaged = tuple(integral(poly, b)/b for poly in hybrid)
            independent = [Q(0)]*self.n
            for i in range(self.n):
                for off in self.masks:
                    if off & (1 << i):
                        continue
                    ones = bin(off).count("1")
                    zeros = self.n-1-ones
                    independent[i] += (complement_integral(zeros+1, ones, b)*contributions[off][i]
                                       +complement_integral(zeros, ones+1, b)*deltas[i, off])/b
            require(averaged == tuple(independent), "independent exact q integration")
            require(integral(R, b) == integral(Z, b)+total-(1-b)*evaluate(g, b)-2*integral(g, b), "integrated budget identity")
            require(sum(averaged, Q(0)) <= j*total+integral(Z, b)/b, "integrated T/b budget")
            require(all(0 <= value <= total for value in averaged), "averaged individual bound")
            require(sum(averaged, Q(0)) <= self.n*total, "owner-count budget")
            for coalition in self.masks:
                require(sum((averaged[i] for i in range(self.n) if coalition & (1 << i)), Q(0)) >= values[coalition], "averaged coalition coverage")
                C["averaged_coalition_checks"] += 1
            result["avg"][j] = averaged
            C["independent_integral_coordinate_checks"] += self.n
            C["integrated_budget_identities"] += 1
        if total == 0:
            require(all(all(value == 0 for value in a) for a in contributions), "T=0 capped contributions")
            require(all(poly == ZERO for poly in hybrid), "T=0 hybrid")
            C["zero_grand_value_profiles"] += 1
        self.cache[flat] = result
        C["profiles"] += 1
        return result

    def compare(self, low, high, owner):
        a, b = self.profile(low), self.profile(high)
        require(a["T"] <= b["T"], "own grand monotonicity")
        for off in self.masks:
            if off & (1 << owner):
                continue
            require(a["forms"][off] == b["forms"][off], "off relative support depends on own report")
            require(a["a"][off][owner] <= b["a"][off][owner], "off capped own monotonicity")
            require(a["deltas"][owner, off] <= b["deltas"][owner, off], "endpoint own monotonicity")
            old_bundle, new_bundle = tuple(low[2*owner:2*owner+2]), tuple(high[2*owner:2*owner+2])
            old_raw = extended_dot(a["forms"][off], old_bundle)
            new_raw = extended_dot(b["forms"][off], new_bundle)
            if old_raw is not None and new_raw is None:
                C["finite_to_infinite_own_support_crossings"] += 1
            C["pointwise_own_monotonicity_checks"] += 2
        for q in QS:
            for key in ("p", "m", "r"):
                require(evaluate(a[key][owner], q) <= evaluate(b[key][owner], q), "scalar own monotonicity")
                C["scalar_own_monotonicity_checks"] += 1
        for j in JS:
            require(a["avg"][j][owner] <= b["avg"][j][owner], "integrated own monotonicity")
            C["averaged_own_monotonicity_checks"] += 1
        C["own_coordinate_comparisons"] += 1


def rejected(operation):
    try:
        operation()
    except VerificationError:
        C["negative_controls_rejected"] += 1
        return
    raise VerificationError("negative control did not fail")


def main():
    require(extended_dot((None, Q(0)), (Q(0), Q(2))) == 0, "infinity times zero convention")
    require(extended_dot((None, Q(0)), (Q(1), Q(0))) is None, "positive outside support")
    require(capped(None, Q(0)) == 0, "infinite contribution at T=0")
    require(support("harmonic", (Q(1), Q(2))) == (Q(4, 9), Q(1, 9)), "harmonic gradient calibration")
    require(production("boundary-jump", (Q(1), Q(0))) == 0, "boundary jump calibration")
    rejected(lambda: require(False, "always-active calibration"))
    rejected(lambda: require(extended_dot((Q(1, 9), Q(4, 9)), (Q(1), Q(2))) == Q(2, 3), "wrong harmonic gradient"))
    rejected(lambda: require(production("boundary-jump", (Q(1), Q(0))) == Q(1), "false boundary continuity"))
    rejected(lambda: require(Q(0) >= production("harmonic", (Q(1), Q(1))), "replacing infinity by zero loses coverage"))
    inventory = []
    for name in ("harmonic", "boundary-jump", "zero", "linear"):
        for n in (1, 2, 3):
            verifier = Verifier(name, n)
            for flat in product(GRID, repeat=2*n):
                verifier.profile(flat)
            for coordinate in range(2*n):
                for others in product(GRID, repeat=2*n-1):
                    context = list(others)
                    context.insert(coordinate, Q(0))
                    for lower, upper in zip(GRID, GRID[1:]):
                        low, high = list(context), list(context)
                        low[coordinate], high[coordinate] = lower, upper
                        verifier.compare(low, high, coordinate//2)
                # Tiny positive jumps supplement the exhaustive coarse grid.
                for context in ((Q(0),)*(2*n), (Q(1),)*(2*n), tuple(Q(h % 2) for h in range(2*n))):
                    low, high = list(context), list(context)
                    low[coordinate], high[coordinate] = Q(0), Q(1, 1000)
                    verifier.compare(low, high, coordinate//2)
            if name == "harmonic" and n == 1:
                sample = verifier.profile((Q(1), Q(1)))
                rejected(lambda: require(add(*sample["m"]) == derivative(sample["g"]), "wrong derivative sign"))
                rejected(lambda: require(sample["R"] == add(sub(sample["Z"], sample["g"]), mul(ONE_MINUS_X, derivative(sample["g"]))), "wrong hybrid sign"))
            inventory.append({"function": name, "owners": n, "profiles": len(verifier.cache)})
    require(C["finite_to_infinite_own_support_crossings"] > 0, "support crossing tests vacuous")
    require(C["zero_grand_value_profiles"] > 0, "zero-value tests vacuous")
    print(json.dumps({"status": "PASS", "functions": {"harmonic": "xy/(x+y), zero at origin; genuinely nonpolyhedral",
        "boundary-jump": "x if y>0, otherwise 0; boundary-discontinuous", "zero": "0", "linear": "2x+3y"},
        "report_grid": list(map(str, GRID)), "extra_positive_jump": "1/1000", "scalar_q": list(map(str, QS)),
        "averaging_j": JS, "inventory": inventory, "counts": dict(sorted(C.items())),
        "scope": "Exact finite profile verification with analytic extended supports; not a proof of the general theorem or asymptotic bound."}, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        sys.exit(1)
