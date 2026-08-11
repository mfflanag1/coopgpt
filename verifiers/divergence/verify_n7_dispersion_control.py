#!/usr/bin/env python3
"""Solver-free-selection audit of the explicit n=7 majorization control.

The paper proves the displayed Lmin/Lmax formulas for this two-generator exact
game.  This verifier rebuilds its characteristic function, checks both points
in the core, reconstructs both dispersion-optimal first-stage certificates by
exact rational LP, and checks compatible fractional support packing.

It does not independently recompute the two lexicographic selections.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from audit_lmax_overcover import top_certificate
from audit_paired_dispersion import bottom_certificate, compatible_optimal_packing


def coalition_sum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    g = tuple(map(F, (0, 5, 0, 3, 2, 0, 0)))
    h = tuple(map(F, (1, 0, 2, 0, 0, 5, 2)))
    n = 7
    values = tuple(
        min(coalition_sum(g, mask), coalition_sum(h, mask))
        for mask in range(1 << n)
    )
    x = tuple(map(F, (1, 2, 1, 1, 1, 3, 1)))
    z = (F(5, 6), F(5, 2), F(5, 6), F(4, 3), F(7, 6), F(5, 2), F(5, 6))
    total = F(10)
    full = (1 << n) - 1
    assert sum(x, F(0)) == total == sum(z, F(0)) == values[full]
    assert all(values[1 << i] == 0 for i in range(n))
    assert all(coalition_sum(x, mask) >= values[mask] for mask in range(1, full))
    assert all(coalition_sum(z, mask) >= values[mask] for mask in range(1, full))

    plus = top_certificate(values, z)
    minus = bottom_certificate(values, x)
    packed = compatible_optimal_packing(
        values, x, z, plus["theta"], minus["theta"]
    )
    assert packed is not None
    alpha, beta = packed
    loads = tuple(
        alpha[i] / plus["theta"] + beta[i] / minus["theta"]
        for i in range(n)
    )
    assert plus["theta"] == F(1, 2)
    assert minus["theta"] == F(1, 5)
    assert loads == (F(1),) * n
    assert 1 / plus["theta"] + 1 / minus["theta"] == n

    minimum = min(x)
    maximum = max(z)
    delta = maximum - minimum
    plus_surplus = sum((alpha[i] * x[i] for i in range(n)), F(0)) - maximum
    minus_surplus = minimum - sum((beta[i] * z[i] for i in range(n)), F(0))
    assert 1 / plus["theta"] <= (total - n * minimum) / (delta + plus_surplus)
    assert 1 / minus["theta"] <= (n * maximum - total) / (delta + minus_surplus)

    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    report = {
        "status": "exact incidence/core audit using proved selection formulas",
        "fixture": "n=7 nonuniform-generator majorization counterexample",
        "selection_dependency": "does not independently recompute Lmin/Lmax",
        "total": str(total),
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "overlap_ratio": str(overlap / total),
        "theta_plus": str(plus["theta"]),
        "theta_minus": str(minus["theta"]),
        "reciprocal_sum": str(1 / plus["theta"] + 1 / minus["theta"]),
        "packed_alpha": [str(value) for value in alpha],
        "packed_beta": [str(value) for value in beta],
        "normalized_packing_loads": [str(value) for value in loads],
        "hinge_surpluses": [str(plus_surplus), str(minus_surplus)],
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
