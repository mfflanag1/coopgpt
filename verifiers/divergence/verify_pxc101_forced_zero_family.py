#!/usr/bin/env python3
"""Exact primary audit of the PXC101 forced-zero-blocker family.

The all-dimension statement is proved algebraically in the manuscript.  This
driver checks its dimension-free identities and incidence classifications,
then recomputes the actual lower envelopes and staged selectors in dimensions
6, 7, and 8 with the project's rational simplex implementation.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
ARCHIVE = HERE.parent / "search_archive"
sys.path[:0] = [str(ARCHIVE)]

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    complete_cx_subsets,
    covers,
    csum,
    lift,
    matrix_rank,
    selector_pair,
    tight_rows,
)


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


def family(k: int):
    """The integer specialization on n=k+4 players, k>=2."""
    if k < 2:
        raise ValueError("the family starts at k=2 (n=6)")
    n = k + 4
    outsiders = tuple(range(4, n))
    total = F(k + 15)
    constraints = {
        mask(0, 1, 2): F(11),
        mask(0, 1, 3): F(11),
        mask(0, 4): F(6),
        mask(0, 1, *outsiders): F(k + 9),
    }
    u = F(k + 4, k + 1)
    p = F(10 * k + 7, 2 * (k + 1))
    x = (p, p) + (u,) * (k + 2)
    z = (F(4), F(4), F(3), F(3), F(2)) + (F(1),) * (k - 1)
    average = F(k + 1, k)
    z_reduced = (F(4), F(4), F(3), F(3)) + (average,) * k
    cx = (mask(0, 1, 2), mask(0, 1, 3))
    top_pair = mask(0, 1)
    all_outsider_row = mask(0, 1, *outsiders)
    z_menu = (*((top_pair,) + cx), mask(0, 4), all_outsider_row)
    return {
        "k": k,
        "n": n,
        "total": total,
        "constraints": constraints,
        "x": x,
        "z": z,
        "z_reduced": z_reduced,
        "cx": cx,
        "z_menu": z_menu,
        "cover_rows": ((top_pair,), (*cx, all_outsider_row)),
    }


def compressed_normal_menu():
    """Enumerate every 0/1 normal in the generic six coordinate types.

    Coordinate types are r,h,a,b,j,o, where every one of the k-1 symmetric
    bottom outsiders has the same coefficient o.  Solve the overdetermined
    linear representation

      1_S = beta*1 + sum_t lambda_t 1_{C_t},  lambda_t >= 0

    exactly.  The only proper nonempty solutions must be rh and the four
    displayed defining rows.
    """
    # Columns beta,c1=rha,c2=rhb,c3=rj,c4=rhO.
    rows = (
        (1, 1, 1, 1, 1),  # r
        (1, 1, 1, 0, 1),  # h
        (1, 1, 0, 0, 0),  # a
        (1, 0, 1, 0, 0),  # b
        (1, 0, 0, 1, 1),  # j
        (1, 0, 0, 0, 1),  # every other outsider
    )

    def solve(target):
        # RREF of six equations in five unknowns.
        aug = [[F(q) for q in row] + [F(b)] for row, b in zip(rows, target)]
        pivot_row = 0
        pivots = []
        for column in range(5):
            pivot = next((i for i in range(pivot_row, 6) if aug[i][column]), None)
            if pivot is None:
                continue
            aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
            scale = aug[pivot_row][column]
            aug[pivot_row] = [q / scale for q in aug[pivot_row]]
            for i in range(6):
                if i != pivot_row and aug[i][column]:
                    scale = aug[i][column]
                    aug[i] = [a - scale * b for a, b in zip(aug[i], aug[pivot_row])]
            pivots.append(column)
            pivot_row += 1
        if any(not any(row[:5]) and row[5] for row in aug):
            return None
        if len(pivots) != 5:
            raise AssertionError("generic normal system lost rank")
        answer = [F(0)] * 5
        for i, column in enumerate(pivots):
            answer[column] = aug[i][5]
        if any(q < 0 for q in answer[1:]):
            return None
        return tuple(answer)

    solutions = {}
    for bits in range(64):
        target = tuple((bits >> i) & 1 for i in range(6))
        item = solve(target)
        if item is not None:
            solutions[bits] = tuple(map(str, item))
    expected = {
        0,       # empty
        63,      # grand coalition
        3,       # rh
        7,       # rha
        11,      # rhb
        17,      # rj
        51,      # rh plus every outsider
    }
    if set(solutions) != expected:
        raise AssertionError((solutions, expected))
    return solutions


def symbolic_checks():
    checks = []
    for k in range(2, 65):
        item = family(k)
        total = item["total"]
        if sum(item["x"], F(0)) != total or sum(item["z"], F(0)) != total:
            raise AssertionError(("efficiency", k))
        if not (item["x"][0] > item["x"][2] > 0):
            raise AssertionError(("Lmin strata", k))
        if not (item["z"][0] > item["z"][2] > item["z"][4]
                > item["z"][-1] > 0):
            raise AssertionError(("Lmax strata", k))
        if csum(item["x"], mask(0, 4)) <= 6:
            raise AssertionError(("blocker not slack at x", k))
        if csum(item["x"], item["z_menu"][-1]) <= k + 9:
            raise AssertionError(("all-outsider row not slack at x", k))
        # Explicit singleton witnesses: h=11,j=6, distribute k-2 on player 5;
        # the all-root allocation zeros every player other than r.
        root_zero = [F(0)] * item["n"]
        root_zero[1], root_zero[4] = F(11), F(6)
        root_zero[5] += F(k - 2)
        if sum(root_zero, F(0)) != total:
            raise AssertionError(("root witness total", k))
        for row, bound in item["constraints"].items():
            if csum(root_zero, row) < bound:
                raise AssertionError(("root witness", k, row))
        common_direction = [F(0)] * item["n"]
        common_direction[4] = -F(k - 1, k)
        for i in range(5, item["n"]):
            common_direction[i] = F(1, k)
        if sum(common_direction, F(0)) or csum(common_direction, mask(0, 4)) >= 0:
            raise AssertionError(("forced-zero direction", k))
        for row in (mask(0, 1), mask(0, 1, 2), mask(0, 1, 3),
                    item["z_menu"][-1]):
            if csum(common_direction, row):
                raise AssertionError(("cover sees direction", k, row))
        if k in (2, 3, 4, 8, 16, 64):
            checks.append({
                "n": item["n"],
                "total": str(total),
                "x": list(map(str, item["x"])),
                "z": list(map(str, item["z"])),
                "reduced_z": list(map(str, item["z_reduced"])),
                "blocker_slack_at_x": str(csum(item["x"], mask(0, 4)) - 6),
                "common_direction": list(map(str, common_direction)),
            })
    return checks


def exact_replays():
    answer = []
    for k in (2, 3, 4):
        expected = family(k)
        values, x, z = selector_pair(
            expected["constraints"], expected["n"], expected["total"]
        )
        if x != expected["x"] or z != expected["z"]:
            raise AssertionError(("selector replay", k, x, z))
        if any(values[1 << i] for i in range(expected["n"])):
            raise AssertionError(("singleton normalization", k))
        if tight_rows(values, x) != expected["cx"]:
            raise AssertionError(("x-tight menu", k, tight_rows(values, x)))
        if tight_rows(values, z) != expected["z_menu"]:
            raise AssertionError(("z-tight menu", k, tight_rows(values, z)))
        pool, complete = complete_cx_subsets(values, x, 8)
        if pool != expected["cx"] or complete != (expected["cx"],):
            raise AssertionError(("complete Cx", k, pool, complete))
        cover_items = covers(values, z)
        if tuple(rows for rows, _ in cover_items) != expected["cover_rows"]:
            raise AssertionError(("cover census", k, cover_items))
        lift_rows = []
        for rows, certificate in cover_items:
            faithful, lx, lz, singleton = lift(values, x, z, expected["cx"], rows, True)
            if faithful or lx != x or lz != expected["z_reduced"] or not singleton:
                raise AssertionError(("lift", k, rows, lx, lz, singleton))
            weights, eta, alpha = certificate
            lift_rows.append({
                "rows": list(rows),
                "weights": list(map(str, weights)),
                "eta": str(eta),
                "alpha": list(map(str, alpha)),
                "lmax": list(map(str, lz)),
            })
        answer.append({
            "n": expected["n"],
            "coalitions_recomputed": 1 << expected["n"],
            "x_tight": list(pool),
            "z_tight": list(tight_rows(values, z)),
            "complete_cx": [list(q) for q in complete],
            "covers": lift_rows,
        })
    return answer


def structural_controls():
    # PXC90 is the faithful full-rank calibration.  Its five outsider
    # incidence columns span all five outsider coordinates, so the equality
    # face has no nonzero later direction after the two tops are fixed.
    pxc90_rows = (23, 27, 39, 75, 114)
    pxc90_incidence = [
        [F((row >> player) & 1) for row in pxc90_rows]
        for player in range(2, 7)
    ]
    pxc90_rank = matrix_rank(pxc90_incidence)
    if pxc90_rank != 5:
        raise AssertionError(("PXC90 full-rank calibration", pxc90_rank))

    # The distinct six-generator control has five failing covers, but all of
    # them share the later direction +e_3-e_5.  Every cover-eligible row and
    # both Cx rows have derivative zero; the sole negative z-tight row is the
    # forced-zero blocker 0125 (mask 39).
    second_cx = (19, 43)
    second_covers = ((3,), (19, 47), (23, 43), (4, 19, 43), (7, 19, 43))
    second_direction = (F(0), F(0), F(0), F(1), F(0), F(-1))
    cover_union = tuple(sorted({row for support in second_covers for row in support}))
    if any(csum(second_direction, row) for row in (*second_cx, *cover_union)):
        raise AssertionError("second control lost its common direction")
    second_ztight = (3, 4, 7, 19, 23, 39, 43, 47)
    blockers = tuple(row for row in second_ztight if csum(second_direction, row) < 0)
    if blockers != (39,) or 39 in cover_union:
        raise AssertionError(("second forced-zero blocker", blockers, cover_union))
    return {
        "PXC90_faithful_full_rank": {
            "rows": list(pxc90_rows),
            "outsider_incidence_rank": pxc90_rank,
            "outsider_count": 5,
        },
        "second_n6_common_direction_control": {
            "complete_cx": list(second_cx),
            "cover_supports": [list(q) for q in second_covers],
            "cover_eligible_union": list(cover_union),
            "direction": list(map(str, second_direction)),
            "forced_zero_blockers": list(blockers),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "PXC101 positive-dimensional forced-zero family and all-n>=6 specialization",
        "generic_parameter_chamber": {
            "parameters": "k>=2 and rational M>q>J>K>0",
            "extra_conditions": [
                "q+(k-1)K>=M",
                "(k+2)q+(k-1)K>(2k+1)J",
            ],
            "rows": [
                "rha>=2M+q", "rhb>=2M+q", "rj>=M+J",
                "rhO>=2M+J+(k-1)K",
            ],
            "selectors": {
                "Lmax": "(M,M,q,q,J,K^(k-1))",
                "Lmin": "(p,p,u^(k+2)), u=(q+J+(k-1)K)/(k+1), p=(T-(k+2)u)/2",
            },
        },
        "integer_specialization": "M=4,q=3,J=2,K=1; T=k+15=n+11",
        "compressed_normal_cone": compressed_normal_menu(),
        "symbolic_integer_checks": symbolic_checks(),
        "exact_game_replays": exact_replays(),
        "structural_controls": structural_controls(),
        "scope": (
            "The exact LP replays cover n=6,7,8. The all-k statement is a conventional "
            "algebraic theorem in divergence.tex; the generic normal and cover incidence "
            "classifications are dimension-free."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
