#!/usr/bin/env python3
"""Independent rational active-set audit of PXC104.

The script reuses only the solver-free active-set kernel of the independent
PXC98 verifier.  It imports no project LP, game, selector, cover, family, or
PXC103 implementation.
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
    7: F(16), 11: F(16), 19: F(13),
    23: F(18), 35: F(13), 39: F(18),
}
X = (F(41, 6), F(41, 6), F(7, 3), F(7, 3), F(7, 3), F(7, 3))
Z = tuple(map(F, (6, 6, 5, 4, 1, 1)))
CX = (7, 11)
COVER_ROWS = ((3,), (11, 19, 39), (11, 23, 35))
REDUCED = (
    tuple(map(F, (6, 6, 4, 4, F(3, 2), F(3, 2)))),
    tuple(map(F, (6, 6, 4, 4, 1, 2))),
    tuple(map(F, (6, 6, 4, 4, 2, 1))),
)


def configure_engine():
    independent.TOTAL = TOTAL
    independent.DEFINING = DEFINING
    independent.X = X
    independent.Z = Z
    independent.CX = CX


def row(mask):
    return [F((mask >> i) & 1) for i in range(N)]


def csum(point, mask):
    return sum((point[i] for i in range(N) if mask >> i & 1), F(0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    configure_engine()
    values = independent.lower_envelope(DEFINING)
    if any(values[1 << i] for i in range(N)):
        raise AssertionError("singleton normalization changed")
    if independent.sparse_selector(DEFINING, "min") != X:
        raise AssertionError("independent Lmin changed")
    if independent.sparse_selector(DEFINING, "max") != Z:
        raise AssertionError("independent Lmax changed")
    xtight = tuple(mask for mask in range(1, 63) if csum(X, mask) == values[mask])
    ztight = tuple(mask for mask in range(1, 63) if csum(Z, mask) == values[mask])
    if xtight != CX or ztight != (3, 11, 19, 23, 35, 39):
        raise AssertionError((xtight, ztight))

    subset_lmins = []
    for size in range(len(CX) + 1):
        for rows in itertools.combinations(CX, size):
            constraints = {mask: csum(X, mask) for mask in rows}
            lx = independent.sparse_selector(constraints, "min")
            subset_lmins.append({
                "rows": list(rows), "lmin": list(map(str, lx)),
                "complete": lx == X,
            })
    if [q["rows"] for q in subset_lmins if q["complete"]] != [[7, 11]]:
        raise AssertionError("complete-Cx uniqueness changed")

    covers = independent.normalized_covers(values)
    if tuple(q[0] for q in covers) != COVER_ROWS:
        raise AssertionError(covers)
    lifts = []
    for index, (rows, weights, eta, alpha) in enumerate(covers):
        constraints = {mask: csum(X, mask) for mask in CX}
        constraints.update({mask: csum(Z, mask) for mask in rows})
        lx = independent.sparse_selector(constraints, "min")
        lz = independent.sparse_selector(constraints, "max")
        if lx != X or lz != REDUCED[index]:
            raise AssertionError((rows, lx, lz))
        lifts.append({
            "rows": list(rows), "weights": list(map(str, weights)),
            "eta": str(eta), "alpha": list(map(str, alpha)),
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

    # Independent common-direction exclusion: top coordinates and every row in
    # the cover union have zero derivative.  The resulting linear system has
    # only the zero solution.
    equations = []
    for player in (0, 1):
        vector = [F(0)] * N
        vector[player] = F(1)
        equations.append(vector)
    for mask in sorted({row for cover in COVER_ROWS for row in cover}):
        equations.append(row(mask))
    only = independent.rref_unique(equations, [F(0)] * len(equations), N)
    if only != (F(0),) * N:
        raise AssertionError(("common kernel nontrivial", only))

    directions = tuple(tuple(a - b for a, b in zip(reduced, Z))
                       for reduced in REDUCED)
    if not (csum(directions[1], 23) < 0 and csum(directions[1], 39) == 0):
        raise AssertionError("left cross-blocker changed")
    if not (csum(directions[2], 39) < 0 and csum(directions[2], 23) == 0):
        raise AssertionError("right cross-blocker changed")

    payload = {
        "claim": "independent exact PXC104 cover-dependent obstruction audit",
        "game": {
            "n": N, "total": str(TOTAL),
            "defining_rows": {str(k): str(v) for k, v in DEFINING.items()},
            "all_coalition_values": list(map(str, values)),
            "singleton_witnesses": witnesses,
        },
        "selectors": {"lmin": list(map(str, X)), "lmax": list(map(str, Z))},
        "tight_menus": {"x": list(xtight), "z": list(ztight)},
        "complete_cx_exhaustion": subset_lmins,
        "extreme_covers_and_lifts": lifts,
        "common_cover_union_kernel": list(map(str, only)),
        "cover_specific_directions": [list(map(str, q)) for q in directions],
        "cross_blocker_cycle": {"row_23_blocks_left": True,
                                "row_39_blocks_right": True},
        "independence": (
            "solver-free rational active-set engine; no project LP, selector, "
            "game, cover, family, or PXC103 implementation"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
