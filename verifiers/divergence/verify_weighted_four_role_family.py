#!/usr/bin/env python3
"""Exact arithmetic audit of the weighted four-role divergence family.

The human proof is symbolic.  This script checks the five-generator lower
envelope, every coalition's attainment, the displayed core points, overlap,
and the elementary pinning inequalities for m=2..40.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(4) if coalition >> i & 1), F(0))


def row(m):
    total = F(2 * m + 4)
    generators = (
        (F(2 * m + 4), F(0), F(0), F(0)),
        (F(2 * m), F(2), F(2), F(0)),
        (F(2 * m + 2), F(0), F(2), F(0)),
        (F(2 * m + 2), F(2), F(0), F(0)),
        (F(2 * m + 3), F(0), F(0), F(1)),
    )
    if any(sum(point, F(0)) != total for point in generators):
        raise AssertionError("generator totals")
    values = tuple(
        min(coalition_sum(point, coalition) for point in generators)
        for coalition in range(16)
    )
    expected = tuple(
        map(
            F,
            (
                0,
                2 * m,
                0,
                2 * m + 2,
                0,
                2 * m + 2,
                0,
                2 * m + 3,
                0,
                2 * m,
                0,
                2 * m + 2,
                0,
                2 * m + 2,
                0,
                2 * m + 4,
            ),
        )
    )
    if values != expected:
        raise AssertionError((m, values))
    if any(
        not any(
            coalition_sum(point, coalition) == values[coalition]
            for point in generators
        )
        for coalition in range(16)
    ):
        raise AssertionError("coalition unattained")

    lmin = (F(2 * m + 1), F(1), F(1), F(1))
    lmax = (F(2 * m), F(2), F(2), F(0))
    for point in (lmin, lmax):
        if sum(point, F(0)) != total:
            raise AssertionError("selection efficiency")
        if any(
            coalition_sum(point, coalition) < values[coalition]
            for coalition in range(16)
        ):
            raise AssertionError("selection outside core")

    # Lmin floor: q_3 <= 1 follows by complementing coalition 7.
    if total - values[7] != 1:
        raise AssertionError("Lmin floor cap")
    # On the floor-one face, pair constraints plus efficiency force
    # q_0 >= 2m+1 and q_1+q_2 <= 2, hence q_1=q_2=1.
    forced_q0 = values[3] + values[5] - (total - F(1))
    if forced_q0 != 2 * m + 1:
        raise AssertionError("Lmin pair forcing")
    # Lmax ceiling: q_0/m >= 2; at ceiling two, both pair constraints
    # force q_1=q_2=2 and efficiency forces q_3=0.
    if values[1] / m != 2:
        raise AssertionError("Lmax ceiling floor")

    overlap = sum((min(a, b) for a, b in zip(lmin, lmax)), F(0))
    if overlap != 2 * m + 2 or overlap / total != F(m + 1, m + 2):
        raise AssertionError("overlap formula")
    return {
        "m": m,
        "atomic_players": m + 3,
        "total": str(total),
        "overlap": str(overlap),
        "overlap_ratio": str(overlap / total),
        "distance_ratio": str(F(2, m + 2)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = [row(m) for m in range(2, 41)]
    report = {
        "status": "exact weighted four-role family audit passed",
        "parameter_range": "m=2..40",
        "parameter_rows": len(rows),
        "human_family": (
            "weights (m,1,1,1), five displayed lower-envelope generators, "
            "weighted Lmin=(2m+1,1,1,1), weighted Lmax=(2m,2,2,0)"
        ),
        "overlap_formula": "O/T=(m+1)/(m+2)",
        "distance_formula": "||x-z||_1/T=2/(m+2)",
        "rows": rows,
        "scope": (
            "the lower-envelope and pinning inequalities are the symbolic proof; "
            "the finite grid is an exact arithmetic regression"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
