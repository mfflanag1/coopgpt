"""Exact finite checks for the scarce-power scoping note; standard library only.

Nonlinear inequalities use certified rational enclosures of exponentials, not
floating-point tolerances. These checks supplement the continuous proof.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
from itertools import permutations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


@lru_cache(None)
def exp_negative_bounds(u, terms=40):
    """Enclose exp(-u) via a positive Taylor series for exp(u)."""
    u = Q(u)
    require(u >= 0, "negative exponent magnitude")
    if u == 0:
        return Q(1), Q(1)
    require(u < terms + 2, "Taylor tail ratio must be below one")
    term = total = Q(1)
    for k in range(1, terms + 1):
        term *= u / k
        total += term
    next_term = term * u / (terms + 1)
    tail_upper = next_term / (1 - u / (terms + 2))
    return 1 / (total + tail_upper), 1 / total


class Expr:
    """Exact rational linear combination of exp(-rational)."""
    def __init__(self, constant=0, terms=None):
        self.constant = Q(constant)
        self.terms = {}
        for u, coefficient in (terms or {}).items():
            u, coefficient = Q(u), Q(coefficient)
            if u == 0:
                self.constant += coefficient
            elif coefficient:
                self.terms[u] = self.terms.get(u, Q(0)) + coefficient
        self.terms = {u: c for u, c in self.terms.items() if c}

    def __add__(self, other):
        if not isinstance(other, Expr):
            other = Expr(other)
        terms = dict(self.terms)
        for u, c in other.terms.items():
            terms[u] = terms.get(u, Q(0)) + c
        return Expr(self.constant + other.constant, terms)

    __radd__ = __add__

    def __mul__(self, coefficient):
        coefficient = Q(coefficient)
        return Expr(self.constant * coefficient,
                    {u: c * coefficient for u, c in self.terms.items()})

    __rmul__ = __mul__

    def __sub__(self, other):
        return self + (other * -1 if isinstance(other, Expr) else -Q(other))

    def bounds(self, precision):
        low = high = self.constant
        for u, c in self.terms.items():
            left, right = exp_negative_bounds(u, precision)
            low += c * (left if c >= 0 else right)
            high += c * (right if c >= 0 else left)
        return low, high

    def certify_nonnegative(self, context):
        for precision in (40, 80, 160):
            low, high = self.bounds(precision)
            if low >= 0:
                return
            if high < 0:
                raise RuntimeError(f"Negative certified expression: {context}")
        raise RuntimeError(f"Unresolved interval, not a pass: {context}")


def two_payments(bundles):
    a, b = (sum(row[k] for row in bundles) for k in (0, 1))
    t = min(a, b)
    if not t:
        return tuple(Expr() for _ in bundles)
    short = 0 if a <= b else 1
    s = [Q(row[short]) for row in bundles]
    d = [min(Q(row[1-short]), t) for row in bundles]
    u = sum(d) / t - 1
    return tuple(Expr(si, {u: (di-si)/2}) for si, di in zip(s, d))


def knapsack_oracle(g, q, energy, value):
    """Independent vertex enumeration: at most one coordinate is fractional."""
    m = len(g)
    candidates = []
    for bits in product((0, 1), repeat=m):
        x = tuple(Q(g[j]) * bits[j] for j in range(m))
        used = sum(energy[j]*x[j] for j in range(m))
        if used <= q:
            candidates.append(sum(value[j]*x[j] for j in range(m)))
        for j in range(m):
            if bits[j]:
                continue
            remaining = Q(q) - used
            fractional = remaining / energy[j]
            if 0 <= fractional <= g[j]:
                candidates.append(sum(value[k]*x[k] for k in range(m))
                                  + value[j]*fractional)
    require(bool(candidates), "missing zero feasible vertex")
    return max(candidates)


def layers(energy, value):
    order = sorted(range(len(energy)), key=lambda j: -value[j]/energy[j])
    ratios = [value[j]/energy[j] for j in order] + [Q(0)]
    return order, [ratios[k]-ratios[k+1] for k in range(len(order))]


def star_value(g, q, energy, value):
    order, weights = layers(energy, value)
    prefix = Q(0)
    result = Q(0)
    for j, weight in zip(order, weights):
        prefix += energy[j]*g[j]
        result += weight*min(q, prefix)
    return result


def star_payments(bundles, energy, value):
    order, weights = layers(energy, value)
    result = [Expr() for _ in bundles]
    prefix = [Q(0) for _ in bundles]
    for j, weight in zip(order, weights):
        for i, row in enumerate(bundles):
            prefix[i] += energy[j]*row[j]
        component = two_payments(tuple((prefix[i], row[-1])
                                       for i, row in enumerate(bundles)))
        result = [y + weight*z for y, z in zip(result, component)]
    return tuple(result)


def check_profiles(n, coordinates, levels, payment_function, value_function):
    profiles = tuple(product(levels, repeat=n*coordinates))
    payments = {}
    coverage = monotonicity = budgets = 0
    for profile in profiles:
        rows = tuple(profile[i*coordinates:(i+1)*coordinates] for i in range(n))
        y = payment_function(rows)
        payments[profile] = y
        t = value_function(tuple(sum(row[j] for row in rows)
                                 for j in range(coordinates)))
        for i, yi in enumerate(y):
            yi.certify_nonnegative(("payment", profile, i))
        for mask in range(1 << n):
            coalition = tuple(i for i in range(n) if mask & (1 << i))
            aggregate = tuple(sum(rows[i][j] for i in coalition)
                              for j in range(coordinates))
            worth = value_function(aggregate)
            (sum((y[i] for i in coalition), Expr())-worth).certify_nonnegative(
                ("coverage", profile, mask))
            coverage += 1
        (Expr(t, {Q(1): t/2})-sum(y, Expr())).certify_nonnegative(
            ("budget", profile))
        budgets += 1
    for profile in profiles:
        for k in range(n*coordinates):
            index = levels.index(profile[k])
            if index + 1 == len(levels):
                continue
            bigger = list(profile)
            bigger[k] = levels[index+1]
            bigger = tuple(bigger)
            owner = k // coordinates
            (payments[bigger][owner]-payments[profile][owner]).certify_nonnegative(
                ("monotonicity", profile, k))
            monotonicity += 1
    return dict(profiles=len(profiles), coalitions=coverage,
                adjacent_own_increases=monotonicity, budgets=budgets,
                owners=n, coordinates_per_owner=coordinates,
                levels=[str(x) for x in levels])


def verify_lower_certificate():
    """Check the earlier 9/8 witness by exact constraint-vector cancellation."""
    c, a, b = (1, 1, 1, 1), (1, 1, 1, 2), (2, 1, 1, 1)
    profiles = {"c": c, "a": a, "b": b}
    total = {f"{name}{i}": Q(0) for name in profiles for i in range(4)}
    total["C"] = Q(0)
    rhs = Q(0)

    def add(coefficients, lower, weight=1):
        nonlocal rhs
        for key, coefficient in coefficients.items():
            total[key] += weight*coefficient
        rhs += weight*lower

    for name, coalitions in (("a", ((0, 2), (1, 2), (0, 1, 3))),
                             ("b", ((1, 2), (1, 3), (0, 2, 3))),
                             ("c", ((0, 3),))):
        row = profiles[name]
        for coalition in coalitions:
            worth = min(sum(row[i] for i in coalition if i < 2),
                        sum(row[i] for i in coalition if i >= 2))
            add({f"{name}{i}": 1 for i in coalition}, worth)
    require(all(c[i] == a[i] for i in range(3)) and a[3] >= c[3], "bad a transition")
    require(all(c[i] == b[i] for i in range(1, 4)) and b[0] >= c[0], "bad b transition")
    add({"a3": 1, "c3": -1}, 0)
    add({"b0": 1, "c0": -1}, 0)
    for name in ("a", "b"):
        row = profiles[name]
        t = min(sum(row[:2]), sum(row[2:]))
        coefficients = {f"{name}{i}": -1 for i in range(4)}
        coefficients["C"] = t
        add(coefficients, 0, weight=2)
    require(all(value == 0 for key, value in total.items() if key != "C"),
            "payment coefficients did not cancel")
    require(total["C"] == 8 and rhs == 9, "lower certificate mismatch")
    return dict(inequality="8 C >= 9", factor="9/8", profiles=3,
                coalition_constraints=7, own_report_constraints=2,
                weighted_budget_constraints=2, provenance="existing supplement witness")


def verify_greedy_obstruction():
    edges = ((0, 2, Q(3)), (0, 3, Q(2)), (1, 2, Q(2)))
    profiles = ((1, 0, 1, 1), (1, 1, 1, 0), (1, 1, 1, 1))
    optima = (Q(3), Q(3), Q(4))
    results = []
    for order in permutations(range(3)):
        values = []
        for profile in profiles:
            remaining = list(map(Q, profile))
            total = Q(0)
            for k in order:
                left, right, price = edges[k]
                amount = min(remaining[left], remaining[right])
                remaining[left] -= amount
                remaining[right] -= amount
                total += price*amount
            values.append(total)
        require(any(v < opt for v, opt in zip(values, optima)),
                "unexpected optimal fixed greedy order")
        results.append(dict(order=list(order), values=list(map(str, values))))
    # Independent upper certificates for the three stated optima.
    # Dual vertex weights in resource order H1,H2,P1,P2 cover each edge price.
    duals = ((Q(3), Q(2), Q(0), Q(0)),
             (Q(0), Q(0), Q(3), Q(2)),
             (Q(2), Q(1), Q(1), Q(0)))
    plans = ((Q(1), Q(0), Q(0)), (Q(1), Q(0), Q(0)),
             (Q(0), Q(1), Q(1)))
    for profile, dual, plan, optimum in zip(profiles, duals, plans, optima):
        require(all(dual[l]+dual[r] >= p for l, r, p in edges), "bad path dual")
        used = [sum(plan[k] for k, (l, r, _) in enumerate(edges) if e in (l, r))
                for e in range(4)]
        require(all(u <= c for u, c in zip(used, profile)), "bad path primal")
        require(sum(dual[e]*profile[e] for e in range(4)) == optimum,
                "path dual objective mismatch")
        require(sum(plan[k]*edges[k][2] for k in range(3)) == optimum,
                "path primal objective mismatch")
    return dict(profiles=3, activity_orders=6, certified_optima=list(map(str, optima)),
                orders=results, scope="fixed report-independent greedy order only")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    # Nontrivial rational coefficients, scrambled order and ties.
    technologies = (
        ((Q(2), Q(1)), (Q(6), Q(2))),
        ((Q(3), Q(1), Q(2)), (Q(3), Q(4), Q(4))),
        ((Q(1), Q(2), Q(3)), (Q(2), Q(4), Q(3))),
        ((Q(1, 2), Q(3, 2)), (Q(3, 2), Q(1))),
    )
    identity_checks = 0
    for energy, value in technologies:
        for capacities in product((Q(0), Q(1, 2), Q(1), Q(2)),
                                  repeat=len(energy)):
            for power in (Q(0), Q(1, 2), Q(1), Q(2), Q(4), Q(9)):
                require(star_value(capacities, power, energy, value)
                        == knapsack_oracle(capacities, power, energy, value),
                        "knapsack identity disagrees with independent vertices")
                identity_checks += 1
    two = []
    for n, levels in ((3, (Q(0), Q(1), Q(2))), (4, (Q(0), Q(1)))):
        two.append(check_profiles(n, 2, levels, two_payments,
                                  lambda row: min(row)))
    stars = []
    for energy, value in technologies[:2]:
        n = 3 if len(energy) == 2 else 2
        stars.append(check_profiles(
            n, len(energy)+1, (Q(0), Q(1)),
            lambda rows: star_payments(rows, energy, value),
            lambda row: knapsack_oracle(row[:-1], row[-1], energy, value)))
    # Interval code must fail closed; scientific checks must survive python -O.
    try:
        Expr(-1).certify_nonnegative("intentional invalid fixture")
    except RuntimeError:
        pass
    else:
        raise RuntimeError("negative-control expression accepted")
    report = dict(status="PASS", arithmetic="Fraction plus certified exponential intervals",
                  decomposition_vertex_checks=identity_checks, two_input_grids=two,
                  heterogeneous_star_grids=stars,
                  lower_certificate=verify_lower_certificate(),
                  greedy_obstruction=verify_greedy_obstruction(),
                  limitations="Finite grids do not prove the all-real-profile theorem or novelty.")
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered)


if __name__ == "__main__":
    main()
