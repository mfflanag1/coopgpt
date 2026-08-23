#!/usr/bin/env python3
"""Independent active-set replay of the PXC112 certificate falsifier.

This uses the standalone rational vertex enumerator previously used for the
independent PXC98 audit.  It imports no project game, selector, cover, or LP
implementation and shares no code with the PXC112 primary verifier.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from verify_unrestricted_pxc91c_pxc98_independent import (
    N,
    TOTAL,
    X,
    Z,
    base_inequalities,
    csum,
    lower_envelope,
    lp_active,
    normalized_covers,
    sparse_selector,
)


DEFINING = {7: F(11), 11: F(11), 17: F(6), 23: F(13), 51: F(11)}
CX_POOL = (7, 11, 23)
COVERS = ((3,), (7, 11, 51))


def singleton_witnesses(constraints):
    inequalities = base_inequalities(constraints)
    equalities = [([F(1)] * N, TOTAL)]
    answer = []
    for player in range(N):
        objective = [F(0)] * N
        objective[player] = F(1)
        optimum, point = lp_active(objective, inequalities, equalities, False)
        if optimum != 0:
            raise AssertionError(("positive singleton", player, optimum))
        answer.append({"player": player, "allocation": list(map(str, point))})
    return answer


def lift(cx, cover):
    constraints = {mask: csum(X, mask) for mask in cx}
    constraints.update({mask: csum(Z, mask) for mask in cover})
    return {
        "lmin": list(map(str, sparse_selector(constraints, "min"))),
        "lmax": list(map(str, sparse_selector(constraints, "max"))),
        "singleton_witnesses": singleton_witnesses(constraints),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values = lower_envelope(DEFINING)
    if sparse_selector(DEFINING, "min") != X or sparse_selector(DEFINING, "max") != Z:
        raise AssertionError("full selectors changed")
    full_witnesses = singleton_witnesses(DEFINING)
    xtight = tuple(mask for mask in range(1, (1 << N) - 1)
                   if csum(X, mask) == values[mask])
    ztight = tuple(mask for mask in range(1, (1 << N) - 1)
                   if csum(Z, mask) == values[mask])
    if xtight != CX_POOL or ztight != (3, 7, 11, 17, 23, 51):
        raise AssertionError((xtight, ztight))

    covers = normalized_covers(values)
    if tuple(q[0] for q in covers) != COVERS:
        raise AssertionError(covers)

    subset_audit = []
    complete = []
    for size in range(len(CX_POOL) + 1):
        for cx in itertools.combinations(CX_POOL, size):
            constraints = {mask: csum(X, mask) for mask in cx}
            lx = sparse_selector(constraints, "min")
            is_complete = lx == X
            subset_audit.append({
                "cx": list(cx), "lmin": list(map(str, lx)),
                "complete": is_complete,
            })
            if is_complete:
                complete.append(cx)
    if tuple(complete) != ((7, 11), (11, 23), (7, 11, 23)):
        raise AssertionError(complete)

    matrix = []
    for cx in complete:
        matrix.append({"cx": list(cx), "covers": [lift(cx, cover) for cover in COVERS]})
    expected = (
        (("4", "4", "3", "3", "3/2", "3/2"),) * 2,
        (("4", "4", "5/2", "3", "5/2", "1"),
         ("4", "4", "3", "3", "2", "1")),
        (("4", "4", "3", "3", "2", "1"),) * 2,
    )
    observed = tuple(
        tuple(tuple(outcome["lmax"]) for outcome in row["covers"])
        for row in matrix
    )
    if observed != expected:
        raise AssertionError(observed)
    if any(tuple(outcome["lmin"]) != tuple(map(str, X))
           for row in matrix for outcome in row["covers"]):
        raise AssertionError("reduced Lmin changed")

    directions = {
        "Cx_7_11_common_failure": ["0", "0", "0", "0", "-1/2", "1/2"],
        "Cx_11_23_pair_only_failure": ["0", "0", "-1/2", "0", "1/2", "0"],
    }
    d1 = tuple(map(F, directions["Cx_7_11_common_failure"]))
    d2 = tuple(map(F, directions["Cx_11_23_pair_only_failure"]))
    if not (csum(d1, 17) < 0 and csum(d1, 23) < 0
            and all(csum(d1, q) == 0 for q in (3, 7, 11, 51))):
        raise AssertionError("common direction arithmetic")
    if not (csum(d2, 7) < 0 and csum(d2, 23) == 0
            and all(csum(d2, q) == 0 for q in (3, 11))):
        raise AssertionError("pair-only direction arithmetic")

    payload = {
        "claim": "independent exact replay of PXC112 certificate dependence",
        "game": {
            "defining_rows": {str(k): str(v) for k, v in DEFINING.items()},
            "all_coalition_values": list(map(str, values)),
            "singleton_witnesses": full_witnesses,
        },
        "selectors": {"lmin": list(map(str, X)), "lmax": list(map(str, Z))},
        "tight_rows": {"x": list(xtight), "z": list(ztight)},
        "complete_cx_exhaustion": subset_audit,
        "extreme_cover_rows": [list(q[0]) for q in covers],
        "lift_matrix": matrix,
        "explicit_bad_directions": directions,
        "fail_open_controls": {
            "first_certificate_universal_failure": True,
            "second_certificate_mixed": True,
            "third_certificate_faithful": True,
        },
        "independence": (
            "standalone Fraction active-set vertex enumeration; no project game, "
            "selector, cover, exactlp, PXC108, or PXC112 implementation"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
