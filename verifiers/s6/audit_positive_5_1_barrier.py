#!/usr/bin/env python3
"""Exact audit of the human barrier for the positive six-player profile.

This script checks the finite exchange-menu lemma used in
``paper5/S6_EQUALITY_CLASSIFICATION.md``.  The mathematical proof in that
note is primary; this QF_LRA audit guards the coalition enumeration, signs,
and boundary arithmetic.
"""

from __future__ import annotations

import itertools
import json

import z3


N = (0, 1)
P = (2, 3, 4)
R = 5
PROPER = tuple(range(1, (1 << 6) - 1))


def coalition_sum(point, coalition):
    terms = [point[i] for i in range(6) if coalition >> i & 1]
    return z3.Sum(terms) if terms else z3.RealVal(0)


def main() -> None:
    v, w = z3.Reals("v w")
    u = (3 * v - w) / 2
    c = (1 - 10 * v + 2 * w) / 6
    a = (1 - v - w) / 6
    d = (1 + 5 * v - w) / 6
    b = (1 + 5 * v + 5 * w) / 6
    x = [a, a, a, a, a, b]
    z = [c, c, d, d, d, d]
    q = [z3.Real(f"q{i}") for i in range(6)]

    directions = []
    # Three one-player transfers from P to the second N player.
    for i in P:
        h = [0, 1, 0, 0, 0, 0]
        h[i] = -1
        directions.append((f"single_N1_P{i}", tuple(h)))
    # Three two-player transfers from a pair in P to both N players.
    for pair in itertools.combinations(P, 2):
        h = [1, 1, 0, 0, 0, 0]
        for i in pair:
            h[i] = -1
        directions.append((f"pair_P{pair}", tuple(h)))
    # Two asymmetric transfers from all of P to N.
    directions.extend(
        [
            ("triple_P_21", (2, 1, -1, -1, -1, 0)),
            ("triple_P_12", (1, 2, -1, -1, -1, 0)),
        ]
    )

    solver = z3.Solver()
    solver.add(
        v > 0,
        w >= 0,
        u >= 0,
        c >= 0,
        w < 2 * v,
        q[R] == 0,
        z3.Sum(q) == 1,
        *[coordinate >= 0 for coordinate in q],
    )

    blocker_counts = {}
    for name, h in directions:
        blockers = []
        for coalition in PROPER:
            h_sum = sum(h[i] for i in range(6) if coalition >> i & 1)
            if h_sum >= 0:
                continue
            blockers.append(
                z3.And(
                    coalition_sum(x, coalition) >= coalition_sum(z, coalition),
                    coalition_sum(q, coalition) >= coalition_sum(z, coalition),
                )
            )
        blocker_counts[name] = len(blockers)
        # Negating feasibility of h says that at least one eligible coalition
        # blocks it.  The conjunction over all eight directions must be empty.
        solver.add(z3.Or(blockers))

    exchange_verdict = solver.check()
    assert exchange_verdict == z3.unsat

    # At w=2v, the three forced common triples and q_R=0 imply d<=2/9.
    boundary = z3.Solver()
    boundary.add(v > 0, w == 2 * v, d <= z3.RealVal("2/9"), v > z3.RealVal("1/9"))
    boundary_verdict = boundary.check()
    assert boundary_verdict == z3.unsat

    print(
        json.dumps(
            {
                "status": "PASS",
                "scope": "exact QF_LRA audit of the human exchange lemma; not an exhaustive type certificate",
                "profile": "(5,1) by (2,4), table ((2,3),(0,1))",
                "strict_w_below_2v_blocker_system": str(exchange_verdict),
                "directions": [name for name, _ in directions],
                "syntactic_negative_mask_counts": blocker_counts,
                "boundary_implication_d_le_2_9_to_v_le_1_9": str(boundary_verdict),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
