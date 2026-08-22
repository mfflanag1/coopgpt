#!/usr/bin/env python3
"""Independent exact audit of a second unrestricted PXC91c n=6 obstruction.

This discovery control is distinct from the total-17 PXC98 witness and is not
used as its release evidence.  It does not import the primary search or simplex.  It uses direct
integer-envelope evaluation, rectangular Gaussian elimination for covers,
and exact active-set vertex enumeration for every sparse lifted selector.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

N = 6
FULL = (1 << N) - 1
TOTAL = F(18)
GENERATORS = tuple(tuple(map(F, row)) for row in (
    (0, 13, 1, 3, 0, 1), (12, 0, 0, 1, 1, 4),
    (12, 5, 0, 0, 0, 1), (4, 10, 1, 0, 0, 3),
    (11, 3, 0, 1, 0, 3), (3, 11, 1, 3, 0, 0),
))
X = (F(25, 4), F(25, 4), F(1, 2), F(9, 4), F(1, 2), F(9, 4))
Z = tuple(map(F, (6, 6, 0, 2, 1, 3)))
ZPRIME = (F(6), F(6), F(0), F(5, 2), F(1), F(5, 2))
CX = (19, 43)


def csum(point, mask):
    return sum((point[i] for i in range(N) if mask >> i & 1), F(0))


VALUES = tuple(min(csum(g, mask) for g in GENERATORS) for mask in range(1 << N))


def rref_unique(matrix, rhs, width):
    aug = [list(map(F, row)) + [F(b)] for row, b in zip(matrix, rhs)]
    cursor = 0; pivots = []
    for column in range(width):
        pivot = next((r for r in range(cursor, len(aug)) if aug[r][column]), None)
        if pivot is None: continue
        aug[cursor], aug[pivot] = aug[pivot], aug[cursor]
        q = aug[cursor][column]
        aug[cursor] = [v / q for v in aug[cursor]]
        for r in range(len(aug)):
            if r != cursor and aug[r][column]:
                q = aug[r][column]
                aug[r] = [a - q*b for a, b in zip(aug[r], aug[cursor])]
        pivots.append(column); cursor += 1
    if any(not any(row[:width]) and row[-1] for row in aug): return None
    if len(pivots) != width: return None
    out = [F(0)] * width
    for r, column in enumerate(pivots): out[column] = aug[r][-1]
    return tuple(out)


def covers(include_singletons):
    top = (0, 1); outsiders = (2, 3, 4, 5)
    tight = tuple(mask for mask in range(1, FULL)
                  if csum(Z, mask) == VALUES[mask]
                  and (include_singletons or mask.bit_count() >= 2))
    answer = []
    for size in range(1, N - 1):
        for rows in itertools.combinations(tight, size):
            matrix = [] ; rhs = []
            for i in outsiders:
                matrix.append([*(F((row >> i) & 1) for row in rows), F(-1)])
                rhs.append(F(0))
            matrix.append([*(F(((row >> 0) & 1) + ((row >> 1) & 1))
                               for row in rows), F(-2)])
            rhs.append(F(1))
            solution = rref_unique(matrix, rhs, size + 1)
            if solution is None: continue
            weights, eta = solution[:-1], solution[-1]
            loads = tuple(sum((w for w, row in zip(weights, rows)
                               if row >> i & 1), F(0)) for i in range(N))
            alpha = (loads[0] - eta, loads[1] - eta)
            if min(weights) > 0 and eta >= 0 and min(alpha) > 0 and sum(alpha) == 1:
                answer.append((rows, weights, eta, alpha))
    return tuple(answer)


def solve_square(rows, rhs, width):
    if len(rows) != width: return None
    return rref_unique(rows, rhs, width)


def lp_active(objective, inequalities, equalities, maximize):
    """Exact LP by exhaustive active sets; sparse lifted systems only."""
    width = len(objective)
    # Retain an independent equality basis.
    basis_rows = []; basis_rhs = []
    for row, bound in equalities:
        trial = rref_unique(basis_rows + [row], basis_rhs + [bound], width)
        # A rectangular system is unique only at full rank, so use rank below.
        work = [list(map(F, q)) for q in basis_rows + [row]]
        rank = 0
        for column in range(width):
            pivot = next((r for r in range(rank, len(work)) if work[r][column]), None)
            if pivot is None: continue
            work[rank], work[pivot] = work[pivot], work[rank]
            q = work[rank][column]; work[rank] = [v/q for v in work[rank]]
            for r in range(rank + 1, len(work)):
                if work[r][column]:
                    q = work[r][column]
                    work[r] = [a-q*b for a,b in zip(work[r],work[rank])]
            rank += 1
        if rank > len(basis_rows):
            basis_rows.append(list(map(F, row))); basis_rhs.append(F(bound))
    need = width - len(basis_rows); best = None; best_point = None
    for chosen in itertools.combinations(range(len(inequalities)), need):
        rows = basis_rows + [list(inequalities[i][0]) for i in chosen]
        rhs = basis_rhs + [inequalities[i][1] for i in chosen]
        point = solve_square(rows, rhs, width)
        if point is None: continue
        if any(sum(a*b for a,b in zip(row, point)) < bound
               for row, bound in inequalities):
            continue
        value = sum(a*b for a,b in zip(objective, point))
        if best is None or (value > best if maximize else value < best):
            best, best_point = value, point
    if best is None: raise AssertionError("active-set LP found no vertex")
    return best, best_point


def sparse_selector(constraints, mode):
    pinned = {}; free = set(range(N))
    base_ineq = []
    for mask, bound in constraints.items():
        base_ineq.append(([F((mask >> i) & 1) for i in range(N)], F(bound)))
    for i in range(N):
        row = [F(0)] * N; row[i] = F(1); base_ineq.append((row, F(0)))
    while free:
        # Stage LP in variables (y,t), using >= inequalities.
        inequalities = [(row + [F(0)], bound) for row, bound in base_ineq]
        equalities = [([F(1)] * N + [F(0)], TOTAL)]
        for i, value in pinned.items():
            row = [F(0)] * (N + 1); row[i] = F(1)
            equalities.append((row, value))
        for i in free:
            row = [F(0)] * (N + 1)
            if mode == "min": row[i], row[N] = F(1), F(-1)
            else: row[i], row[N] = F(-1), F(1)
            inequalities.append((row, F(0)))
        objective = [F(0)] * (N + 1); objective[N] = F(1)
        level, _ = lp_active(objective, inequalities, equalities, mode == "min")

        inequalities2 = list(base_ineq)
        equalities2 = [([F(1)] * N, TOTAL)]
        for i, value in pinned.items():
            row = [F(0)] * N; row[i] = F(1); equalities2.append((row, value))
        for i in free:
            row = [F(0)] * N; row[i] = F(1 if mode == "min" else -1)
            inequalities2.append((row, level if mode == "min" else -level))
        newly = []
        for i in sorted(free):
            objective = [F(0)] * N; objective[i] = F(1)
            extreme, _ = lp_active(objective, inequalities2, equalities2, mode == "min")
            if extreme == level: newly.append(i)
        if not newly: raise AssertionError(("no pin", mode, level))
        for i in newly: pinned[i] = level; free.remove(i)
    return tuple(pinned[i] for i in range(N))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if any(sum(g) != TOTAL for g in GENERATORS): raise AssertionError("generator total")
    if any(VALUES[1 << i] != 0 for i in range(N)): raise AssertionError("normalization")
    # Each coalition minimum is attained by a displayed core allocation.
    if any(csum(g, mask) < VALUES[mask] for g in GENERATORS for mask in range(1 << N)):
        raise AssertionError("generator left core")
    if any(csum(X, m) < VALUES[m] or csum(Z, m) < VALUES[m] for m in range(1 << N)):
        raise AssertionError("selector candidate left core")
    xtight = tuple(m for m in range(1, FULL) if csum(X, m) == VALUES[m])
    ztight = tuple(m for m in range(1, FULL) if csum(Z, m) == VALUES[m])
    if xtight != CX or ztight != (3, 4, 7, 19, 23, 39, 43, 47):
        raise AssertionError((xtight, ztight))
    # Human inequality certificates described in the output are arithmetically checked.
    if not (VALUES[19] == 13 and VALUES[43] == 17 and VALUES[3] == 12
            and VALUES[39] == 15):
        raise AssertionError("selector certificate rows changed")
    all_covers = covers(True); nonsingleton_covers = covers(False)
    expected_all = ((3,), (19, 47), (23, 43), (4, 19, 43), (7, 19, 43))
    expected_non = ((3,), (19, 47), (23, 43), (7, 19, 43))
    if tuple(q[0] for q in all_covers) != expected_all: raise AssertionError(all_covers)
    if tuple(q[0] for q in nonsingleton_covers) != expected_non: raise AssertionError(nonsingleton_covers)
    # Both x-tight rows are necessary, and every cover has the same wrong Lmax.
    subset_lmins = {}
    for size in range(3):
        for rows in itertools.combinations(CX, size):
            constraints = {m: csum(X, m) for m in rows}
            subset_lmins[rows] = sparse_selector(constraints, "min")
    if subset_lmins[CX] != X or any(subset_lmins[q] == X for q in subset_lmins if q != CX):
        raise AssertionError("complete-Cx uniqueness failed")
    lift_results = []
    for rows, weights, eta, alpha in all_covers:
        constraints = {m: csum(X, m) for m in CX}
        constraints.update({m: csum(Z, m) for m in rows})
        lx = sparse_selector(constraints, "min")
        lz = sparse_selector(constraints, "max")
        if lx != X or lz != ZPRIME: raise AssertionError((rows, lx, lz))
        lift_results.append({"rows": list(rows), "weights": list(map(str, weights)),
                             "eta": str(eta), "alpha": list(map(str, alpha)),
                             "lmin": list(map(str, lx)), "lmax": list(map(str, lz))})
    payload = {
        "claim": "independent exact active-set audit of a second n=6 PXC91c counterexample",
        "exact_game_reason": "v is the lower envelope of six displayed core allocations, one attaining every coalition minimum",
        "lmin_human_certificate": (
            "19 gives y2+y3+y5<=5; 43 gives y2+y4<=1, successively pinning "
            "{2,4}=1/2, {3,5}=9/4, {0,1}=25/4"
        ),
        "lmax_human_certificate": (
            "3 pins top {0,1}=6; rows 19,39,43 imply y4>=1 and y5-y4>=2, "
            "then pin y5=3, y3=2, y4=1, y2=0"
        ),
        "x_tight_rows": list(xtight), "z_tight_rows": list(ztight),
        "all_cover_count": len(all_covers),
        "proper_nonsingleton_cover_count": len(nonsingleton_covers),
        "unique_complete_cx": list(CX), "lift_results": lift_results,
        "common_wrong_lmax": list(map(str, ZPRIME)),
        "fixed_cx_refuted": True, "existential_cx_refuted": True,
        "scope": (
            "coherent discovery control for a total-18 generator-envelope witness; "
            "distinct from PXC98 and not used as PXC98 or PXC100 release evidence"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__": main()
