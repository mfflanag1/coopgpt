#!/usr/bin/env python3
"""Exact joint congestion audit for first-floor individual pinning certificates.

The fixture is the singleton-exactified two-packet boundary.  Its actual Lmin
bottom block is P={0,1,2,5}.  For every i in P we choose an exact individual
pinning certificate and jointly minimize the largest column sum of its
nonnegative floor-side weights q^i_j.

This is a diagnostic example, not a general congestion theorem.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402


N = 6
FULL = (1 << N) - 1
TRIAL = (F(1, 12),) * 4 + (F(7, 12), F(1, 12))
LMAX = (F(0), F(1, 4), F(0), F(1, 4), F(1, 4), F(1, 4))
WITNESSES = (
    (F(0), F(0), F(1, 4), F(3, 4), F(0), F(0)),
    (F(1, 4), F(0), F(0), F(3, 4), F(0), F(0)),
    (F(1, 4), F(0), F(0), F(0), F(3, 4), F(0)),
)
ACTUAL_LMIN = (F(1, 12), F(1, 12), F(1, 12), F(1, 3), F(1, 3), F(1, 12))


def coalition_sum(point, mask):
    return sum((point[i] for i in range(N) if mask >> i & 1), F(0))


def lower_envelope(rows):
    return tuple(
        min(coalition_sum(row, mask) for row in rows) for mask in range(1 << N)
    )


def joint_certificate(v, x, targets):
    mu = min(x)
    bottom = tuple(i for i, value in enumerate(x) if value == mu)
    tight = tuple(
        mask for mask in range(1, FULL)
        if coalition_sum(x, mask) == v[mask]
    )
    m = len(tight)
    block_width = m + len(bottom) + 1
    kappa = len(targets) * block_width
    width = kappa + 1

    def lam(i_pos, coalition_pos):
        return i_pos * block_width + coalition_pos

    def q(i_pos, j_pos):
        return i_pos * block_width + m + j_pos

    def c(i_pos):
        return i_pos * block_width + m + len(bottom)

    aeq = []
    beq = []
    for i_pos, pinned in enumerate(targets):
        for player in range(N):
            row = [F(0)] * width
            for coalition_pos, mask in enumerate(tight):
                row[lam(i_pos, coalition_pos)] = F(int(bool(mask >> player & 1)))
            if player in bottom:
                row[q(i_pos, bottom.index(player))] = F(1)
            row[c(i_pos)] = F(-1)
            aeq.append(row)
            beq.append(F(-int(player == pinned)))
        row = [F(0)] * width
        for coalition_pos, mask in enumerate(tight):
            row[lam(i_pos, coalition_pos)] = -v[mask]
        for j_pos in range(len(bottom)):
            row[q(i_pos, j_pos)] = -mu
        row[c(i_pos)] = v[FULL]
        aeq.append(row)
        beq.append(mu)

    aub = []
    bub = []
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = F(-1)
        aub.append(row)
        bub.append(F(0))
    for j_pos in range(len(bottom)):
        row = [F(0)] * width
        for i_pos in range(len(targets)):
            row[q(i_pos, j_pos)] = F(1)
        row[kappa] = F(-1)
        aub.append(row)
        bub.append(F(0))

    objective = [F(0)] * width
    objective[kappa] = F(1)
    status, optimum, solution = exact_linprog(objective, aub, bub, aeq, beq)
    if status != "optimal":
        raise RuntimeError(status)
    matrix = tuple(
        tuple(solution[q(i_pos, j_pos)] for j_pos in range(len(bottom)))
        for i_pos in range(len(targets))
    )
    column_loads = tuple(
        sum((matrix[i_pos][j_pos] for i_pos in range(len(targets))), F(0))
        for j_pos in range(len(bottom))
    )
    assert max(column_loads) == optimum
    return bottom, tight, matrix, column_loads, optimum


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    v = lower_envelope((TRIAL, LMAX) + WITNESSES)
    x = ACTUAL_LMIN
    z = LMAX
    assert all(coalition_sum(x, mask) >= v[mask] for mask in range(1, FULL))
    mu = min(x)
    targets = tuple(i for i in range(N) if x[i] == mu and z[i] > mu)
    bottom, tight, matrix, column_loads, congestion = joint_certificate(
        v, x, targets
    )
    for i_pos, player in enumerate(targets):
        rhs = sum(
            (matrix[i_pos][j_pos] * (mu - z[j]) for j_pos, j in enumerate(bottom)),
            F(0),
        )
        assert z[player] - mu <= rhs
    positive = sum((max(F(0), z[i] - mu) for i in bottom), F(0))
    deficit = sum((max(F(0), mu - z[i]) for i in bottom), F(0))
    assert positive <= congestion * deficit

    report = {
        "status": "exact joint first-floor certificate audit; example only",
        "bottom_players": list(bottom),
        "positive_lmax_surplus_targets": list(targets),
        "tight_coalition_masks": list(tight),
        "minimum_column_congestion": str(congestion),
        "q_matrix_rows_by_pinned_player": [
            [str(value) for value in row] for row in matrix
        ],
        "column_loads": [str(value) for value in column_loads],
        "lmax_surplus_on_bottom": str(positive),
        "lmax_deficit_on_bottom": str(deficit),
        "congestion_bound": str(congestion * deficit),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
