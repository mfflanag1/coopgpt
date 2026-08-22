#!/usr/bin/env python3
"""Solver-free independent audit of the PXC108 calibrations.

This file imports no project LP, selector, cover, graph, or PXC108 module.
It checks the normalized-cover circuits and the exact common/cyclic/full-rank
linear-algebra witnesses directly over ``Fraction``.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def row(mask, n):
    return [F((mask >> i) & 1) for i in range(n)]


def csum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def rank(matrix):
    a = [list(map(F, q)) for q in matrix]
    if not a:
        return 0
    answer = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(answer, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[answer], a[pivot] = a[pivot], a[answer]
        scale = a[answer][col]
        a[answer] = [q / scale for q in a[answer]]
        for i in range(len(a)):
            if i != answer and a[i][col]:
                scale = a[i][col]
                a[i] = [q - scale * p for q, p in zip(a[i], a[answer])]
        answer += 1
    return answer


def transpose(columns):
    return [list(q) for q in zip(*columns)] if columns else []


def cover_audit(n, top, rows, weights, eta):
    outsiders = tuple(i for i in range(n) if i not in top)
    loads = tuple(
        sum((weight for mask, weight in zip(rows, weights) if mask >> i & 1), F(0))
        for i in range(n)
    )
    alpha = tuple(loads[i] - eta for i in top)
    if any(loads[i] != eta for i in outsiders):
        raise AssertionError((rows, "outsider balance", loads, eta))
    if min(weights) <= 0 or eta < 0 or min(alpha) <= 0 or sum(alpha) != 1:
        raise AssertionError((rows, "cover positivity", weights, eta, alpha))

    columns = [
        [F((mask >> i) & 1) for i in outsiders]
        + [F(sum((mask >> t) & 1 for t in top))]
        for mask in rows
    ]
    if eta > 0:
        columns.append([F(-1)] * len(outsiders) + [F(-2)])
    target = [F(0)] * len(outsiders) + [F(-1)]
    circuit = columns + [target]
    if rank(transpose(columns)) != len(columns):
        raise AssertionError((rows, "dependent active columns"))
    if rank(transpose(circuit)) != len(columns):
        raise AssertionError((rows, "target not dependent"))
    for omitted in range(len(circuit)):
        subset = circuit[:omitted] + circuit[omitted + 1 :]
        if rank(transpose(subset)) != len(subset):
            raise AssertionError((rows, "nonminimal circuit", omitted))
    outsider_matrix = [
        [F((mask >> i) & 1) for mask in rows] for i in outsiders
    ]
    return {
        "rows": list(rows), "weights": list(map(str, weights)),
        "eta": str(eta), "alpha": list(map(str, alpha)),
        "outsider_rank": rank(outsider_matrix),
        "circuit_size": len(circuit),
    }


def equality_rank(n, top, rows):
    equations = [[F(1)] * n]
    for player in top:
        equations.append([F(i == player) for i in range(n)])
    equations.extend(row(mask, n) for mask in rows)
    return rank(equations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # PXC101/PXC98: the same later-stage direction is tangent to both cover
    # supports and the unique transverse row 17 cuts it.
    common = tuple(map(F, (0, 0, 0, 0, -1, 1)))
    p98_covers = (
        ((3,), (F(1, 2),), F(0)),
        ((7, 11, 51), (F(1, 4),) * 3, F(1, 4)),
    )
    p98_union = tuple(sorted({q for rows, _w, _e in p98_covers for q in rows}))
    if any(csum(common, mask) for mask in p98_union) or csum(common, 17) >= 0:
        raise AssertionError("PXC101 common-blocker witness changed")
    p98_circuits = [cover_audit(6, (0, 1), *cover) for cover in p98_covers]

    # PXC104: the all-cover equality system is full rank, while the two
    # positive covers admit transverse directions cut by a row of the other.
    p104_covers = (
        ((3,), (F(1, 2),), F(0)),
        ((11, 19, 39), (F(1, 4),) * 3, F(1, 4)),
        ((11, 23, 35), (F(1, 4),) * 3, F(1, 4)),
    )
    p104_union = tuple(sorted({q for rows, _w, _e in p104_covers for q in rows}))
    left = tuple(map(F, (0, 0, -1, 0, 0, 1)))
    right = tuple(map(F, (0, 0, -1, 0, 1, 0)))
    if equality_rank(6, (0, 1), p104_union) != 6:
        raise AssertionError("PXC104 acquired a common equality direction")
    if not (
        all(csum(left, q) == 0 for q in p104_covers[1][0])
        and csum(left, 23) < 0 and 23 in p104_covers[2][0]
        and all(csum(right, q) == 0 for q in p104_covers[2][0])
        and csum(right, 39) < 0 and 39 in p104_covers[1][0]
    ):
        raise AssertionError("PXC104 invariant two-cycle changed")
    p104_circuits = [cover_audit(6, (0, 1), *cover) for cover in p104_covers]

    # PXC90: top coordinates, efficiency, and the five cover equalities have
    # rank seven, so there is no later direction at all.
    p90_cover = (
        (23, 27, 39, 75, 114),
        tuple(F(q, 7) for q in (1, 1, 2, 2, 1)),
        F(3, 7),
    )
    if equality_rank(7, (0, 1), p90_cover[0]) != 7:
        raise AssertionError("PXC90 lost full-rank fidelity")
    p90_circuit = cover_audit(7, (0, 1), *p90_cover)

    payload = {
        "claim": "independent solver-free PXC108 circuit/incidence calibration",
        "PXC101": {
            "common_direction": list(map(str, common)),
            "cover_union": list(p98_union), "forced_zero_blocker": 17,
            "circuits": p98_circuits,
        },
        "PXC104": {
            "cover_union": list(p104_union),
            "union_equality_rank": 6,
            "cycle": [
                {"source": 1, "blocker": 23, "target": 2,
                 "direction": list(map(str, left))},
                {"source": 2, "blocker": 39, "target": 1,
                 "direction": list(map(str, right))},
            ],
            "circuits": p104_circuits,
        },
        "PXC90": {
            "full_equality_rank": 7, "dimension": 7,
            "circuit": p90_circuit,
        },
        "independence": (
            "standalone Fraction row reduction; no project LP, selector, "
            "cover, graph, PXC107, or PXC108 imports"
        ),
        "scope": (
            "independent exact verification of all required theorem "
            "calibrations; the general alternative remains a symbolic proof"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
