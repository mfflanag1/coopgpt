#!/usr/bin/env python3
"""Exact algebraic feasibility/sign check, not telemetry or an economic pilot."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
import math

B = [(Q(1), (Q(0), Q(1))),
     (Q(2), (Q(1), Q(-1))),
     (Q(3, 2), (Q(1), Q(0)))]
D = (Q(1, 2), (Q(3, 10), Q(2, 5)))


def add(items):
    return (sum(t for t, x in items), tuple(sum(x[j] for t, x in items) for j in range(2)))


def norm2(x):
    return sum(v * v for v in x)


def cone(b):
    t, x = b
    return t >= 0 and t * t >= norm2(x)


def main():
    restored = B.copy()
    restored[0] = add([B[0], D])
    assert all(cone(b) for b in B + restored + [D])
    assert D[0] ** 2 == norm2(D[1])  # F(D)=0 exactly.
    no_veto = []
    for pair in combinations(range(3), 2):
        t, x = add([B[i] for i in pair])
        gap = t * t - norm2(x)
        assert t > 0 and gap > 0  # F of every pair is strictly positive.
        no_veto.append({"owners": [i + 1 for i in pair], "t_squared_minus_norm_squared": str(gap)})
    old_t, old_x = add(B)
    new_t, new_x = add(restored)
    assert old_x == (Q(2), Q(0))
    assert new_x == (Q(23, 10), Q(2, 5))
    assert norm2(new_x) == Q(545, 100)
    numerator = sum(a * b for a, b in zip(restored[0][1], new_x))
    assert numerator == Q(5, 4)
    # New y1=3/2 - 25/(2 sqrt545) < 1 iff 25 > sqrt545.
    assert 25 ** 2 > 545
    old_y1 = Q(1)
    new_y1 = 1.5 - 25 / (2 * math.sqrt(545))
    report = {"scope": "Synthetic cone witness only; no necessity-of-subsidy or real-rights claim",
              "cone_checks": "PASS", "all_owner_pairs_have_positive_production": no_veto,
              "withdrawn_bundle_outside_production": "0 exactly",
              "old_gradient_y1": str(old_y1),
              "new_gradient_y1_exact": "3/2 - 25/(2*sqrt(545))",
              "new_gradient_y1_decimal": new_y1,
              "loss_exact": "(25/sqrt(545)-1)/2",
              "strict_loss_sign_certificate": "625 > 545",
              "verdict": "This efficient coalition-covering allocation fails individual TCWM despite three fixed non-veto owners; coverage holds at both profiles"}
    out = Path(__file__).resolve().parent / "three_owner_witness.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
