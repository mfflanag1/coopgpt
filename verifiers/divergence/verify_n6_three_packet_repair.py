#!/usr/bin/env python3
"""Exact checks for the irregular six-player three-packet repair identity."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def audit_row(a: F, b: F, c: F, A: F, D: F, E: F) -> None:
    total_x = c + b + 4 * a
    total_z = 3 * A + D + 2 * E
    if total_x != total_z:
        raise AssertionError("totals differ")
    root_price_slack = 3 * a - c
    hinge_slack = c + b + a - 2 * A - D
    if min(a, b - a, c - b, A - b, c - A, D - a, a - E) < 0:
        raise AssertionError("payoff/sign order failed")
    if min(root_price_slack, hinge_slack) < 0:
        raise AssertionError("packet premise failed")
    overlap = A + b + 2 * a + 2 * E
    identity = hinge_slack + F(a + b, 3) + F(2, 3) * root_price_slack
    if overlap - F(2, 3) * total_x != identity or identity < 0:
        raise AssertionError("three-packet repair identity failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # Rational grid satisfying the common-total equation.  The identity is
    # the proof; this enumeration is a hostile arithmetic regression only.
    rows = 0
    for a_num in range(1, 7):
        a = F(a_num)
        for b_num in range(a_num, 3 * a_num + 1):
            b = F(b_num)
            for c_num in range(b_num, 3 * a_num + 1):
                c = F(c_num)
                total = c + b + 4 * a
                for A_num in range(b_num, c_num + 1):
                    A = F(A_num)
                    for D_num in range(a_num, 3 * a_num + 1):
                        D = F(D_num)
                        E = F(total - 3 * A - D, 2)
                        if F(0) <= E <= a and 2 * A + D <= c + b + a:
                            audit_row(a, b, c, A, D, E)
                            rows += 1

    # harvest6_602.json $.records[82], with roles
    # r=0,u=1,g=4,j=5 and the two low players 2,3.
    control = {
        "a": F(1),
        "b": F(2),
        "c": F(3),
        "A": F(11, 5),
        "D": F(8, 5),
        "E": F(2, 5),
    }
    audit_row(**control)
    total = control["c"] + control["b"] + 4 * control["a"]
    overlap = control["A"] + control["b"] + 2 * control["a"] + 2 * control["E"]
    report = {
        "status": "exact six-player three-packet repair identity verified",
        "exact_parameter_rows": rows,
        "theorem_bound": "O/T >= 2/3",
        "archived_control": {
            "source": "harvest6_602.json $.records[82]",
            "normalized_overlap": str(overlap / total),
            "root_price_slack": str(3 * control["a"] - control["c"]),
            "common_hinge_slack": str(
                control["c"] + control["b"] + control["a"]
                - 2 * control["A"] - control["D"]
            ),
        },
        "scope": (
            "the displayed rational identity is the proof; this is a fixed-six-player "
            "branch theorem, not a universal residual-classification theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
