#!/usr/bin/env python3
"""Exact, stdlib-only checks of the owned price-charge note.

This does not test an unrestricted upper theorem. It verifies static/edge
lemmas on one finite technology, actual-coordinate dual balances in the
changed-owner charging fixture, and the rational repair counterexamples.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json


def dot(x, y):
    return sum((a * b for a, b in zip(x, y)), Q(0))


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def sub(x, y):
    return tuple(a - b for a, b in zip(x, y))


def total(profile, coalition=None):
    if coalition is None:
        coalition = range(len(profile))
    out = (Q(0),) * len(profile[0])
    for i in coalition:
        out = add(out, profile[i])
    return out


def technology(capacity, epsilon=Q(1, 2)):
    """Resources K,A,B,C; old KAB profit1, new KC profit1+epsilon."""
    K, A, B, C = capacity
    new = min(K, C)
    old = min(K - new, A, B)
    x = (old, new)
    profit = (Q(1), Q(1) + epsilon)
    value = dot(x, profit)
    prices = (
        (Q(1) + epsilon, Q(0), Q(0), Q(0)),
        (Q(1), Q(0), Q(0), epsilon),
        (Q(0), Q(1), Q(0), Q(1) + epsilon),
        (Q(0), Q(0), Q(1), Q(1) + epsilon),
    )
    p = min(prices, key=lambda price: dot(price, capacity))
    assert old >= 0 and new >= 0
    assert old + new <= K and old <= A and old <= B and new <= C
    assert p[0] + p[1] + p[2] >= 1
    assert p[0] + p[3] >= 1 + epsilon
    assert dot(p, capacity) == value
    return value, x, p, profit


def state(profile, epsilon=Q(1, 2)):
    cap = total(profile)
    value, x, p, profit = technology(cap, epsilon)
    supports = ((0, 1, 2), (0, 3))
    u = tuple(dot(p, owner) for owner in profile)
    h = tuple(
        sum(
            (
                profit[j] * x[j]
                * sum((owner[a] / cap[a] if cap[a] else Q(0)
                       for a in supports[j]), Q(0))
                for j in range(2)
            ), Q(0)
        )
        for owner in profile
    )
    zeta = tuple(hi - ui for hi, ui in zip(h, u))
    assert sum(u) == value
    assert all(z >= 0 for z in zeta)
    assert sum(h) == 3 * x[0] + 2 * profit[1] * x[1]
    assert sum(zeta) <= 2 * value
    return {"value": value, "x": x, "p": p, "u": u, "h": h, "zeta": zeta}


def named_counterexample(t, epsilon):
    return state(((Q(0), Q(1), Q(1), t),
                  (Q(1), Q(0), Q(0), Q(0))), epsilon)


def main():
    bundles = tuple(tuple(Q(x) for x in b) for b in product((0, 1), repeat=4))
    profiles = tuple(product(bundles, repeat=2))
    states = {p: state(p) for p in profiles}
    coverage_checks = 0
    for profile in profiles:
        st = states[profile]
        for coalition in ((), (0,), (1,), (0, 1)):
            own = total(profile, coalition)
            rest = sub(total(profile), own)
            loss = st["value"] - technology(rest)[0]
            charge = sum((st["h"][i] for i in coalition), Q(0))
            assert technology(own)[0] <= loss <= charge
            coverage_checks += 1

    bundle_pairs = tuple((lo, hi) for lo in bundles for hi in bundles
                         if all(x <= y for x, y in zip(lo, hi)))
    edge_counts = {}
    for coalition in ((0,), (1,), (0, 1)):
        count = 0
        for choices in product(*(bundle_pairs if i in coalition else
                                 tuple((b, b) for b in bundles) for i in range(2))):
            low = tuple(x[0] for x in choices)
            high = tuple(x[1] for x in choices)
            delta = sub(total(high), total(low))
            out = technology(delta)[0]
            defect = sum((states[low]["u"][i] - states[high]["u"][i]
                          for i in coalition), Q(0)) + out
            charge = sum((states[high]["zeta"][i] for i in coalition), Q(0))
            assert defect <= charge
            count += 1
        edge_counts[str(coalition)] = count

    repairs = []
    for A0 in map(Q, (1, 2, 3, 10)):
        for B0 in (Q(1, 100), Q(1, 10), Q(1), Q(2), Q(10)):
            epsilon = min(B0 / (2 * A0), Q(1, 2))
            lo = named_counterexample(Q(1, 4), epsilon)
            hi = named_counterexample(Q(3, 4), epsilon)
            low_pay = A0 * lo["u"][0] + B0 * lo["zeta"][0]
            high_pay = A0 * hi["u"][0] + B0 * hi["zeta"][0]
            assert high_pay - low_pay == (A0 * epsilon - B0) / 2 < 0
            # The actual singleton outside production is zero.
            assert technology((Q(0), Q(0), Q(0), Q(1, 2)), epsilon)[0] == 0
            repairs.append({"A0": A0, "B0": B0, "epsilon": epsilon,
                            "payment_change": high_pay - low_pay})

    price_only = []
    for A0 in map(Q, (1, 2, 3, 10)):
        # min(A,B), owner0 restores A from1/4 to3/4, other owner B=1/2.
        low_total, high_total = (Q(1, 4), Q(1, 2)), (Q(3, 4), Q(1, 2))
        p_low, p_high = (Q(1), Q(0)), (Q(0), Q(1))
        assert dot(p_low, low_total) == min(low_total)
        assert dot(p_high, high_total) == min(high_total)
        low_pay, high_pay = A0 / 4, Q(0)
        assert high_pay < low_pay
        price_only.append({"A0": A0, "payment_change": high_pay - low_pay})

    balanced = []
    for epsilon in (Q(1, 4), Q(1, 16), Q(1, 64), Q(1, 256), Q(1, 1024)):
        low = ((Q(1), Q(0), Q(0)), (Q(0), Q(0), Q(0)),
               (Q(0), 1 + epsilon, Q(2)))
        high = (low[0], (2 * epsilon, Q(0), Q(0)), low[2])
        protected, changed = (0, 1), (1,)
        v_low, v_high = min(total(low)), min(total(high))
        assert v_low == 1 and v_high == 1 + epsilon
        p_low, p_high = (Q(1), Q(0), Q(0)), (Q(0), Q(1), Q(0))
        u_low = tuple(dot(p_low, owner) for owner in low)
        u_high = tuple(dot(p_high, owner) for owner in high)
        out = min(sub(total(high), total(low)))
        defect = sum((u_low[i] - u_high[i] for i in protected), Q(0)) + out
        assert defect == 1 and out == 0
        h_high = tuple(v_high * sum((owner[a] / total(high)[a]
                                    for a in range(3)), Q(0)) for owner in high)
        zeta_high = tuple(h - u for h, u in zip(h_high, u_high))
        assert zeta_high[1] == (1 + epsilon) * 2 * epsilon / (1 + 2 * epsilon)
        assert sum(zeta_high[i] for i in protected) == 1 + epsilon
        # One shared comparison multiplier, low grand-coverage weight1,
        # and one budget multiplier at each profile. Construct rather than
        # insert the expected balances.
        g = {"low": [Q(1)] * 3, "high": [Q(0)] * 3}
        for i in protected:
            g["low"][i] -= 1
            g["high"][i] += 1
        nu = {"low": Q(1), "high": Q(1)}
        sigma = {p: [nu[p] - x for x in row] for p, row in g.items()}
        assert all(x >= 0 for row in sigma.values() for x in row)
        assert all(g[p][i] - nu[p] + sigma[p][i] == 0
                   for p in g for i in range(3))
        assert g["low"] == [0, 0, 1] and g["high"] == [1, 1, 0]
        M, w = Q(1), (Q(1), Q(1), Q(0))
        assert all(w[i] == M for i in changed)
        assert all(0 <= wi <= M for wi in w)
        assert sum(w[i] for i in range(3) if i not in changed) == M
        L, D = v_low + out, v_low + v_high
        exact_price_identity = defect - sum(sigma["low"][i] * u_low[i]
                                            + sigma["high"][i] * u_high[i]
                                            for i in range(3))
        assert L - D == exact_price_identity
        balanced.append({"epsilon": epsilon, "L": L, "D": D,
                         "ratio": L / D, "price_defect": defect,
                         "changed_surplus": zeta_high[1],
                         "defect_over_changed_surplus": defect / zeta_high[1],
                         "g": g, "sigma": sigma})

    named_lo = named_counterexample(Q(1, 4), Q(1, 2))
    named_hi = named_counterexample(Q(3, 4), Q(1, 2))
    result = {
        "status": "PASS",
        "scope": "Exact finite checks; no unrestricted funding upper bound tested or proved.",
        "binary_owner_profiles": len(profiles),
        "coalition_deletion_and_cover_checks": coverage_checks,
        "full_OUT_price_defect_checks_by_actual_coalition": edge_counts,
        "full_OUT_price_defect_checks_total": sum(edge_counts.values()),
        "fixed_surplus_repair_counterexamples": repairs,
        "price_only_counterexamples": price_only,
        "balanced_changed_owner_obstructions": balanced,
        "named_rational_fixture_low": named_lo,
        "named_rational_fixture_high": named_hi,
    }
    output = Path(__file__).with_suffix(".json")
    output.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps({"status": result["status"], "profiles": len(profiles),
                      "coalition_checks": coverage_checks,
                      "OUT_edge_checks": sum(edge_counts.values()),
                      "repair_failures": len(repairs) + len(price_only),
                      "balanced_duals": len(balanced), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
