#!/usr/bin/env python3
"""Exact finite audit of the dimension-free complement-star facet theorem.

The human proof classifies every possible exceptional set algebraically.
This script independently applies the generic Studeny--Kratochvil
exceptional-set LP test on a parameter grid and checks the incidence
identity, support rank, and balanced equality parameters.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from verify_rooted_hinge_projection import (  # noqa: E402
    decomposition_witnesses,
    matrix_rank,
)


def complement_star(t: int, p: int):
    """Return the scaled complement-star support and coefficients."""
    n = 1 + t + p
    root = 1
    witnesses = tuple(range(1, t + 1))
    outside = tuple(range(t + 1, n))
    caps = []
    for omitted in witnesses:
        coalition = root
        for player in witnesses:
            if player != omitted:
                coalition |= 1 << player
        caps.append(coalition)
    pairs = [root | (1 << player) for player in outside]
    support = (root, *caps, *pairs)
    coefficients = (
        -(p * (t - 1) + 1),
        *((1,) * t),
        *((t - 1,) * p),
    )
    loads = tuple(
        sum(
            coefficient
            for coalition, coefficient in zip(support, coefficients)
            if coalition >> player & 1
        )
        for player in range(n)
    )
    if loads != (t - 1,) * n:
        raise AssertionError((t, p, "incidence identity", loads))
    if len(support) != n or matrix_rank(support, n) != n:
        raise AssertionError((t, p, "support is not saturated"))
    decompositions = decomposition_witnesses(support, n)
    if decompositions:
        raise AssertionError((t, p, "decomposable", decompositions[0]))
    return {
        "t": t,
        "p": p,
        "n": n,
        "support": list(support),
        "scaled_coefficients": list(coefficients),
        "common_load": t - 1,
        "support_rank": n,
        "unsupported_proper_exceptional_sets": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = [
        complement_star(t, p)
        for t in range(2, 6)
        for p in range(1, 4)
        if 3 <= 1 + t + p <= 8
    ]
    balanced = []
    for n in range(6, 13):
        m = n - 1
        K = (m - 1) * (m - 1) // 4
        for t in range(2, m + 1):
            p = m - t
            if (t - 1) * p == K:
                balanced.append(
                    {
                        "n": n,
                        "t": t,
                        "p": p,
                        "K": K,
                        "target_denominator": K + m,
                    }
                )

    p0_support = (1, 13, 11, 7)
    p0_decompositions = decomposition_witnesses(p0_support, 4)
    if not p0_decompositions:
        raise AssertionError("p=0,t=3 negative control unexpectedly indecomposable")

    report = {
        "status": "exact complement-star facet regression passed",
        "human_theorem": (
            "for every t>=2 and p>=1, the displayed saturated rooted "
            "complement-star system is indecomposable by the explicit "
            "exceptional-set classification"
        ),
        "generic_lp_parameter_rows": len(rows),
        "rows": rows,
        "excluded_p0_t3_negative_control": {
            "support": list(p0_support),
            "first_new_exceptional_set": p0_decompositions[0],
            "classification": "decomposable",
        },
        "balanced_equality_parameters": balanced,
        "scope": (
            "generic exact-LP exceptional-set replay through n=8 and exact "
            "balanced arithmetic through n=12; the dimension-free algebraic "
            "classification is the proof; p=0 is excluded and can be decomposable"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
