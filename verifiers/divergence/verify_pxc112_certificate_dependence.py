#!/usr/bin/env python3
"""Exact primary audit of PXC112 complete-certificate dependence.

The game is the PXC98 lower envelope with the additional common-tight row
``rhaj >= 13``.  It has the same Lmin/Lmax pair but three complete proper-row
Cx choices.  Their sparse-cover fidelity outcomes differ, disproving any
game-only PXC108 graph that forgets the retained certificate.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(HERE.parent), str(HERE.parent / "search_archive")]

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    csum,
    lift,
    selector_pair,
)


N = 6
TOTAL = F(17)
DEFINING = {7: F(11), 11: F(11), 17: F(6), 23: F(13), 51: F(11)}
X = (F(9, 2), F(9, 2), F(2), F(2), F(2), F(2))
Z = tuple(map(F, (4, 4, 3, 3, 2, 1)))
EXPECTED_CX = ((7, 11), (11, 23), (7, 11, 23))
EXPECTED_COVERS = ((3,), (7, 11, 51))


def row(mask):
    return [F((mask >> i) & 1) for i in range(N)]


def rank(matrix):
    a = [list(map(F, q)) for q in matrix]
    cursor = 0
    for column in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(cursor, len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[cursor], a[pivot] = a[pivot], a[cursor]
        scale = a[cursor][column]
        a[cursor] = [q / scale for q in a[cursor]]
        for i in range(len(a)):
            if i != cursor and a[i][column]:
                scale = a[i][column]
                a[i] = [q - scale * p for q, p in zip(a[i], a[cursor])]
        cursor += 1
    return cursor


def common_trace_signature(cx):
    common = tuple(mask for mask in cx if csum(X, mask) == csum(Z, mask))
    # Rank is only a compact regression statistic.  The theorem uses equality
    # of generated tangent cones, not equality of ranks.
    return {"common_rows": list(common), "normal_rank": rank([row(q) for q in common])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values, x, z = selector_pair(DEFINING, N, TOTAL)
    if x != X or z != Z:
        raise AssertionError((x, z))
    item = audit_game("PXC112", values, x, z, pool_max=12, replay_exact=True)
    if item is None or not item["cx_subsets_exhausted"]:
        raise AssertionError("complete-Cx exhaustion failed")
    matrix = item["complete_cx_cover_matrix"]
    if tuple(tuple(q["cx_rows"]) for q in matrix) != EXPECTED_CX:
        raise AssertionError(matrix)
    covers = tuple(tuple(q["rows"]) for q in item["covers"])
    if covers != EXPECTED_COVERS:
        raise AssertionError(covers)
    cover_payload = [
        {
            key: cover[key]
            for key in ("index", "rows", "weights", "eta", "alpha")
        }
        for cover in item["covers"]
    ]
    faithful_sets = tuple(tuple(q["faithful_cover_indices"]) for q in matrix)
    if faithful_sets != ((), (1,), (0, 1)):
        raise AssertionError(faithful_sets)

    lift_matrix = []
    for cx in EXPECTED_CX:
        outcomes = []
        for cover in EXPECTED_COVERS:
            faithful, lx, lz, singleton = lift(
                values, X, Z, cx, cover, diagnose_singletons=True
            )
            outcomes.append({
                "cover": list(cover), "faithful": faithful,
                "lmin": list(map(str, lx)), "lmax": list(map(str, lz)),
                "singleton_normalized": singleton,
            })
        lift_matrix.append({
            "cx": list(cx), "tangent_signature": common_trace_signature(cx),
            "outcomes": outcomes,
        })

    expected_lmax = (
        (("4", "4", "3", "3", "3/2", "3/2"),) * 2,
        (("4", "4", "5/2", "3", "5/2", "1"),
         ("4", "4", "3", "3", "2", "1")),
        (("4", "4", "3", "3", "2", "1"),) * 2,
    )
    observed = tuple(
        tuple(tuple(q["lmax"]) for q in row_["outcomes"])
        for row_ in lift_matrix
    )
    if observed != expected_lmax:
        raise AssertionError(observed)
    if not all(q["singleton_normalized"] for r in lift_matrix for q in r["outcomes"]):
        raise AssertionError("a reduced lift lost singleton normalization")

    payload = {
        "claim": "exact six-player falsifier of game-only certificate-independent PXC108 canonicality",
        "game": {
            "n": N, "total": str(TOTAL),
            "defining_rows": {str(k): str(v) for k, v in DEFINING.items()},
            "all_coalition_values": list(map(str, values)),
            "exactness": "lower envelope of the displayed compact nonnegative polytope",
            "singleton_normalized": all(values[1 << i] == 0 for i in range(N)),
        },
        "selectors": {"lmin": list(map(str, X)), "lmax": list(map(str, Z))},
        "tight_rows": {"x": item["tight_x_rows"],
                       "z": [q for q in range(1, (1 << N) - 1)
                             if csum(Z, q) == values[q]]},
        # Fidelity is certificate-relative and therefore appears only in the
        # explicit Cx-by-cover matrix below.  Do not inherit the discovery
        # helper's fixed-Cx diagnostic fields into this promoted artifact.
        "extreme_covers": cover_payload,
        "complete_cx_lift_matrix": lift_matrix,
        "classification_by_cx": [
            "universal failure: common-direction forced-zero branch",
            "mixed: pair cover fails, positive-ambient cover is faithful",
            "both covers faithful",
        ],
        "correct_invariant": (
            "the PXC108 graph is invariant on equivalence classes of complete Cx "
            "having the same staged tangent cones at x and z; it is not an invariant "
            "of the game and selector pair alone; the quotient fixes candidate-selector "
            "fidelity, not the eventual altered selector after failure"
        ),
        "fail_open_controls": {
            "three_distinct_faithful_sets": len(set(faithful_sets)) == 3,
            "same_game_and_selectors": True,
            "every_sparse_lift_retains_lmin": all(
                tuple(q["lmin"]) == tuple(map(str, X))
                for r in lift_matrix for q in r["outcomes"]
            ),
        },
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
