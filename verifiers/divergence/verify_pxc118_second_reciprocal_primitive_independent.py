#!/usr/bin/env python3
"""Independent solver-free rational replay of PXC118.

Only the active-set kernel of the independent PXC98 audit is reused.  This
file imports no project LP, selector, cover, PXC104, PXC108, or PXC118 code.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

import verify_unrestricted_pxc91c_pxc98_independent as independent


N = 6
TOTAL = F(23)
DEFINING = {
    7: F(16), 11: F(16), 19: F(13), 23: F(18),
    35: F(13), 39: F(18), 52: F(7),
}
X = (F(41, 6), F(41, 6), F(7, 3), F(7, 3), F(7, 3), F(7, 3))
Z = tuple(map(F, (6, 6, 5, 4, 1, 1)))
XTIGHT = (7, 11, 52)
COMPLETE = ((7, 11), (7, 11, 52))
COVERS = ((3,), (11, 55), (11, 19, 39), (11, 23, 35))
REDUCED = (
    tuple(map(F, (6, 6, 4, 4, F(3, 2), F(3, 2)))),
    tuple(map(F, (6, 6, 4, 4, F(3, 2), F(3, 2)))),
    tuple(map(F, (6, 6, 4, 4, 1, 2))),
    tuple(map(F, (6, 6, 4, 4, 2, 1))),
)


def configure() -> None:
    independent.TOTAL = TOTAL
    independent.DEFINING = DEFINING
    independent.X = X
    independent.Z = Z
    independent.CX = COMPLETE[0]


def row(mask: int) -> list[F]:
    return [F((mask >> i) & 1) for i in range(N)]


def csum(point, mask: int) -> F:
    return sum((point[i] for i in range(N) if mask >> i & 1), F(0))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    configure()

    values = independent.lower_envelope(DEFINING)
    if any(values[1 << i] for i in range(N)):
        raise AssertionError("singleton normalization changed")
    if independent.sparse_selector(DEFINING, "min") != X:
        raise AssertionError("independent Lmin changed")
    if independent.sparse_selector(DEFINING, "max") != Z:
        raise AssertionError("independent Lmax changed")
    xtight = tuple(m for m in range(1, 63) if csum(X, m) == values[m])
    ztight = tuple(m for m in range(1, 63) if csum(Z, m) == values[m])
    if xtight != XTIGHT or ztight != (3, 11, 19, 23, 35, 39, 52, 55):
        raise AssertionError((xtight, ztight))

    subset_lmins = []
    for size in range(len(XTIGHT) + 1):
        for rows in itertools.combinations(XTIGHT, size):
            constraints = {m: csum(X, m) for m in rows}
            lx = independent.sparse_selector(constraints, "min")
            subset_lmins.append({
                "rows": list(rows), "lmin": list(map(str, lx)),
                "complete": lx == X,
            })
    if tuple(tuple(q["rows"]) for q in subset_lmins if q["complete"]) != COMPLETE:
        raise AssertionError("complete-Cx exhaustion changed")

    covers = independent.normalized_covers(values)
    if tuple(q[0] for q in covers) != COVERS:
        raise AssertionError(covers)
    lifts = []
    for cx in COMPLETE:
        for index, (rows, weights, eta, alpha) in enumerate(covers):
            constraints = {m: csum(X, m) for m in cx}
            constraints.update({m: csum(Z, m) for m in rows})
            lx = independent.sparse_selector(constraints, "min")
            lz = independent.sparse_selector(constraints, "max")
            if lx != X or lz != REDUCED[index]:
                raise AssertionError((cx, rows, lx, lz))
            lifts.append({
                "cx": list(cx), "rows": list(rows),
                "weights": list(map(str, weights)), "eta": str(eta),
                "alpha": list(map(str, alpha)),
                "lmin": list(map(str, lx)), "lmax": list(map(str, lz)),
            })

    inequalities = independent.base_inequalities(DEFINING)
    equalities = [([F(1)] * N, TOTAL)]
    witnesses = []
    for i in range(N):
        objective = [F(0)] * N
        objective[i] = F(1)
        optimum, point = independent.lp_active(
            objective, inequalities, equalities, False
        )
        if optimum != 0:
            raise AssertionError(("positive singleton", i, optimum))
        witnesses.append({"player": i, "allocation": list(map(str, point))})

    # The union-equality system has zero kernel after fixing the top block.
    equations = []
    for i in (0, 1):
        vector = [F(0)] * N
        vector[i] = F(1)
        equations.append(vector)
    for mask in sorted({m for cover in COVERS for m in cover}):
        equations.append(row(mask))
    only = independent.rref_unique(equations, [F(0)] * len(equations), N)
    if only != (F(0),) * N:
        raise AssertionError(("common cover kernel", only))

    directions = tuple(tuple(a - b for a, b in zip(q, Z)) for q in REDUCED)
    if not (csum(directions[2], 23) < 0 and csum(directions[2], 39) == 0):
        raise AssertionError("left cross-blocker arithmetic")
    if not (csum(directions[3], 39) < 0 and csum(directions[3], 23) == 0):
        raise AssertionError("right cross-blocker arithmetic")

    payload = {
        "claim": "independent exact PXC118 reciprocal-primitive falsifier",
        "game": {
            "n": N, "total": str(TOTAL),
            "defining_rows": {str(k): str(v) for k, v in DEFINING.items()},
            "all_coalition_values": list(map(str, values)),
            "singleton_witnesses": witnesses,
        },
        "selectors": {"lmin": list(map(str, X)), "lmax": list(map(str, Z))},
        "tight_menus": {"x": list(xtight), "z": list(ztight)},
        "complete_cx_exhaustion": subset_lmins,
        "extreme_covers": [{
            "rows": list(rows), "weights": list(map(str, weights)),
            "eta": str(eta), "alpha": list(map(str, alpha)),
        } for rows, weights, eta, alpha in covers],
        "all_complete_cx_cover_lifts": lifts,
        "common_cover_union_kernel": list(map(str, only)),
        "cover_specific_directions": [list(map(str, q)) for q in directions],
        "cross_blocker_cycle": {
            "row_23_blocks_cover_2": True,
            "row_39_blocks_cover_3": True,
        },
        "independence": (
            "solver-free rational active-set engine; no project LP, selector, "
            "game, cover, PXC104, PXC108, or PXC118 implementation"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
