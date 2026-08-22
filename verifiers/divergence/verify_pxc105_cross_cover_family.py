#!/usr/bin/env python3
"""Primary exact audit of the PXC105 rational cross-cover family.

The conventional proof is affine on 4 < A < 11/2.  This verifier checks
the symbolic lower-envelope formula, endpoint interpolation certificates,
and five interior rational anchors with exhaustive complete-Cx and extreme-
cover enumeration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
DIV = HERE.parent
ARCHIVE = DIV / "search_archive"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(ARCHIVE)]

from exactlp import exact_linprog  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    csum,
    selector_pair,
    tight_rows,
)
from search_pxc103_cover_dependent_failure import (  # noqa: E402
    common_staged_direction_xz,
)

N = 6
LO = F(4)
HI = F(11, 2)
ANCHORS = (F(17, 4), F(9, 2), F(5), F(21, 4), F(27, 5))
CX = (7, 11)
EXPECTED_COVERS = ((3,), (11, 19, 39), (11, 23, 35))


def data(A: F):
    total = F(18) + A
    constraints = {
        7: F(16), 11: F(16), 19: F(13),
        23: F(13) + A, 35: F(13), 39: F(13) + A,
    }
    u = (A + 2) / 3
    p = (46 - A) / 6
    x = (p, p, u, u, u, u)
    z = (F(6), F(6), A, F(4), F(1), F(1))
    h = (A - 2) / 2
    reduced = (
        (F(6), F(6), F(4), F(4), h, h),
        (F(6), F(6), F(4), F(4), F(1), A - 3),
        (F(6), F(6), F(4), F(4), A - 3, F(1)),
    )
    return total, constraints, x, z, reduced


def expected_value(A: F, coalition: int):
    if coalition == (1 << N) - 1:
        return F(18) + A
    if coalition & 3 != 3:
        return F(0)
    trace = coalition >> 2
    candidates = [F(12)]
    if trace & 0b0011:  # a or b
        candidates.append(F(16))
    if trace & 0b1100:  # j or k
        candidates.append(F(13))
    if trace & 0b0001 and trace & 0b1100:  # a with j or k
        candidates.append(F(13) + A)
    return max(candidates)


def lower_envelope_with_points(A: F):
    total, constraints, _x, _z, _reduced = data(A)
    aub, bub = [], []
    for coalition, bound in constraints.items():
        aub.append([-F((coalition >> i) & 1) for i in range(N)])
        bub.append(-bound)
    for player in range(N):
        row = [F(0)] * N
        row[player] = -1
        aub.append(row)
        bub.append(F(0))
    values, points = [], []
    for coalition in range(1 << N):
        objective = [F((coalition >> i) & 1) for i in range(N)]
        status, value, point = exact_linprog(
            objective, aub, bub, [[F(1)] * N], [total]
        )
        if status != "optimal" or value != expected_value(A, coalition):
            raise AssertionError((A, coalition, status, value,
                                  expected_value(A, coalition)))
        values.append(value)
        points.append(tuple(point))
    return tuple(values), tuple(points)


def point_digest(endpoint_points):
    rendered = json.dumps(
        [[[str(q) for q in point] for point in points]
         for points in endpoint_points],
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(rendered).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    endpoint_values, endpoint_points = [], []
    for endpoint in (LO, HI):
        values, points = lower_envelope_with_points(endpoint)
        endpoint_values.append(values)
        endpoint_points.append(points)

    # Each expected coalition value is affine on the closed endpoint interval.
    # Interpolating the two exact endpoint minimizers supplies a feasible point
    # attaining that value for every intermediate A; the displayed max formula
    # supplies the matching lower bound.
    for coalition in range(1 << N):
        midpoint = (LO + HI) / 2
        if expected_value(midpoint, coalition) != (
            endpoint_values[0][coalition] + endpoint_values[1][coalition]
        ) / 2:
            raise AssertionError(("nonaffine coalition value", coalition))

    audits = []
    for A in ANCHORS:
        if not LO < A < HI:
            raise AssertionError(A)
        total, constraints, expected_x, expected_z, expected_reduced = data(A)
        values, x, z = selector_pair(constraints, N, total)
        if any(values[coalition] != expected_value(A, coalition)
               for coalition in range(1 << N)):
            raise AssertionError(("lower envelope", A))
        if x != expected_x or z != expected_z:
            raise AssertionError((A, x, z))
        item = audit_game(f"PXC105_A={A}", values, x, z,
                          pool_max=10, replay_exact=False)
        if item is None:
            raise AssertionError(("left target domain", A))
        if item["tight_x_rows"] != list(CX):
            raise AssertionError((A, item["tight_x_rows"]))
        if item["complete_cx_count"] != 1 or item["canonical_cx"] != list(CX):
            raise AssertionError(("complete Cx", A, item["complete_cx_count"]))
        covers = tuple(tuple(q["rows"]) for q in item["covers"])
        if covers != EXPECTED_COVERS:
            raise AssertionError((A, covers))
        reduced = tuple(tuple(map(F, q["fixed_lmax"])) for q in item["covers"])
        if reduced != expected_reduced or any(q["fixed_faithful"]
                                               for q in item["covers"]):
            raise AssertionError(("reduced selectors", A, reduced))
        if common_staged_direction_xz(x, z, CX, item["covers"]) is not None:
            raise AssertionError(("common direction", A))
        directions = tuple(tuple(q - w for q, w in zip(rz, z))
                           for rz in reduced)
        if not (csum(directions[1], 23) < 0
                and csum(directions[1], 39) == 0
                and csum(directions[2], 39) < 0
                and csum(directions[2], 23) == 0):
            raise AssertionError(("cross cycle", A, directions))
        forced_zero = tuple(
            row for row in tight_rows(values, z)
            if all(row not in cover for cover in covers)
        )
        if forced_zero:
            raise AssertionError(("forced-zero row appeared", A, forced_zero))
        audits.append({
            "A": str(A),
            "total": str(total),
            "lmin": list(map(str, x)),
            "lmax": list(map(str, z)),
            "tight_x": item["tight_x_rows"],
            "tight_z": list(tight_rows(values, z)),
            "complete_cx_count": item["complete_cx_count"],
            "covers": item["covers"],
            "reduced_lmax": [list(map(str, q)) for q in reduced],
        })

    payload = {
        "claim": "PXC105 positive-dimensional rational cross-cover family",
        "parameter": {"symbol": "A", "domain": "4 < A < 11/2", "rational": True},
        "formulas": {
            "total": "18+A",
            "defining_rows": {
                "7": "16", "11": "16", "19": "13",
                "23": "13+A", "35": "13", "39": "13+A",
            },
            "lmin": ["(46-A)/6", "(46-A)/6",
                     "(A+2)/3", "(A+2)/3", "(A+2)/3", "(A+2)/3"],
            "lmax": ["6", "6", "A", "4", "1", "1"],
            "complete_cx": [7, 11],
            "extreme_covers": [list(q) for q in EXPECTED_COVERS],
            "reduced_lmax": [
                ["6", "6", "4", "4", "(A-2)/2", "(A-2)/2"],
                ["6", "6", "4", "4", "1", "A-3"],
                ["6", "6", "4", "4", "A-3", "1"],
            ],
        },
        "continuum_certificate": {
            "endpoint_A": [str(LO), str(HI)],
            "coalitions_checked": 64,
            "lower_bound": (
                "max of nonnegativity, the six defining rows, and the "
                "three-row top-cover bound R>=12"
            ),
            "upper_bound": (
                "exact endpoint minimizers interpolate affinely for every "
                "coalition and every A in [4,11/2]"
            ),
            "endpoint_minimizer_sha256": point_digest(endpoint_points),
        },
        "interior_exact_anchors": audits,
        "boundaries": {
            "A=4": "a/b residual-stratum tie; excluded",
            "A=11/2": "cross rows become x-tight; excluded",
        },
        "scope": (
            "conventional affine family proof plus exact endpoint certificates "
            "and five exhaustive rational interior audits"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
