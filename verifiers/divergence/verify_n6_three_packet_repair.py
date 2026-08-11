#!/usr/bin/env python3
"""Exact checks for the irregular six-player three-packet repair identity."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


SUPPORT = (1, 5, 9, 27, 35, 49)


def matrix_rank(columns: tuple[int, ...], n: int) -> int:
    rows = [[F(column >> player & 1) for column in columns] for player in range(n)]
    rank = 0
    for column in range(len(columns)):
        pivot = next((row for row in range(rank, n) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(n):
            if row == rank or rows[row][column] == 0:
                continue
            scale = rows[row][column]
            rows[row] = [a - scale * b for a, b in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def facet_audit() -> dict:
    """Closed-form Studeny--Kratochvil exceptional-set test."""
    # Player order: r,u,l1,l2,g,j.  The pair-lift identity is
    # 1_27+1_35+1_49+1_9+2*1_5-4*1_1=2*1_N.
    coefficients = {27: F(1), 35: F(1), 49: F(1), 9: F(1), 5: F(2), 1: F(-4)}
    loads = [
        sum(
            (weight for coalition, weight in coefficients.items() if coalition >> player & 1),
            F(0),
        )
        for player in range(6)
    ]
    if loads != [F(2)] * 6 or matrix_rank(SUPPORT, 6) != 6:
        raise AssertionError("three-packet pair lift lost identity or minimality")

    # For a candidate exceptional coalition K with indicator
    # (kr,ku,kl1,kl2,kg,kj), the unique support weights are nonnegative
    # exactly when L(K)<=rho<=U(K), where:
    #
    # L=max(-ku-kg+kj, -ku-kj+kg, -kg-kj+ku,
    #       -2kl2+ku+kg-kj, -kl1),
    # U=(kr-kj-kl2-kl1)/2.
    feasible = []
    intervals = {}
    for coalition in range(1, 1 << 6):
        kr, ku, kl1, kl2, kg, kj = (
            F(coalition >> player & 1) for player in range(6)
        )
        lower = max(
            -ku - kg + kj,
            -ku - kj + kg,
            -kg - kj + ku,
            -2 * kl2 + ku + kg - kj,
            -kl1,
        )
        upper = (kr - kj - kl2 - kl1) / 2
        if lower <= upper:
            feasible.append(coalition)
            intervals[str(coalition)] = [str(lower), str(upper)]
    expected = list(SUPPORT) + [63]
    if feasible != expected:
        raise AssertionError({"exceptional-set classification changed": feasible})
    return {
        "pair_lift_identity": "1_27+1_35+1_49+1_9+2*1_5-4*1_1=2*1_N",
        "support_rank": 6,
        "support_size": 6,
        "feasible_exceptional_sets": feasible,
        "feasible_rho_intervals": intervals,
        "new_proper_exceptional_sets": 0,
        "classification": "indecomposable purely min-semi-balanced exact-cone facet",
        "criterion": "Studeny--Kratochvil exceptional-set indecomposability test",
    }


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
        "exact_cone_facet": facet_audit(),
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
