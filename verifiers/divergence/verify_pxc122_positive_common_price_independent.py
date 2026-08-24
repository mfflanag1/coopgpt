#!/usr/bin/env python3
"""Independent solver-free exact-rational replay of the PXC122 anchor.

No project game, simplex, selector, cover, or primary PXC122 code is used.
All coalition minima and sparse selectors are computed by exhaustive exact
active-set enumeration; normalized covers use separate Gaussian elimination.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

N = 6
FULL = 63
A, B, K, M = F(1), F(5), F(29, 5), F(6)
C = A + 2 * B - K
TOTAL = 2 * M + 3 * A + 2 * B
X = (M + A / 2, M + A / 2, A, B, A, B)
Z = (M, M, F(0), C, 2 * A, K)
ZP = (M, M, F(0), B + A / 2, 2 * A, B + A / 2)
DEFINING = {3: 2 * M, 19: 2 * M + 2 * A,
            39: 2 * M + K, 43: 2 * M + A + 2 * B}
CX = (19, 43)


def csum(point, coalition):
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def rank(rows):
    work = [list(map(F, row)) for row in rows]
    cursor = 0
    for column in range(len(work[0]) if work else 0):
        pivot = next((i for i in range(cursor, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[cursor], work[pivot] = work[pivot], work[cursor]
        scale = work[cursor][column]
        work[cursor] = [value / scale for value in work[cursor]]
        for i in range(len(work)):
            if i != cursor and work[i][column]:
                scale = work[i][column]
                work[i] = [a - scale * b for a, b in zip(work[i], work[cursor])]
        cursor += 1
    return cursor


def solve_unique(rows, rhs, width):
    if len(rows) != width:
        return None
    augmented = [list(map(F, row)) + [F(bound)] for row, bound in zip(rows, rhs)]
    cursor = 0
    pivots = []
    for column in range(width):
        pivot = next((i for i in range(cursor, len(augmented))
                      if augmented[i][column]), None)
        if pivot is None:
            continue
        augmented[cursor], augmented[pivot] = augmented[pivot], augmented[cursor]
        scale = augmented[cursor][column]
        augmented[cursor] = [value / scale for value in augmented[cursor]]
        for i in range(len(augmented)):
            if i != cursor and augmented[i][column]:
                scale = augmented[i][column]
                augmented[i] = [a - scale * b
                                for a, b in zip(augmented[i], augmented[cursor])]
        pivots.append(column)
        cursor += 1
    if len(pivots) != width:
        return None
    answer = [F(0)] * width
    for i, column in enumerate(pivots):
        answer[column] = augmented[i][-1]
    return tuple(answer)


def active_lp(objective, inequalities, equalities, maximize=False):
    width = len(objective)
    basis_rows, basis_rhs = [], []
    for row, bound in equalities:
        if rank(basis_rows + [row]) > len(basis_rows):
            basis_rows.append(list(map(F, row)))
            basis_rhs.append(F(bound))
    need = width - len(basis_rows)
    best = None
    best_point = None
    for chosen in itertools.combinations(range(len(inequalities)), need):
        rows = basis_rows + [list(inequalities[i][0]) for i in chosen]
        rhs = basis_rhs + [inequalities[i][1] for i in chosen]
        point = solve_unique(rows, rhs, width)
        if point is None:
            continue
        if any(sum((a * b for a, b in zip(row, point)), F(0)) < bound
               for row, bound in inequalities):
            continue
        value = sum((a * b for a, b in zip(objective, point)), F(0))
        if best is None or (value > best if maximize else value < best):
            best, best_point = value, point
    if best is None:
        raise AssertionError("no feasible active-set vertex")
    return best, best_point


def inequalities(constraints, width=N):
    result = []
    for coalition, bound in constraints.items():
        result.append(([
            F((coalition >> i) & 1) for i in range(width)
        ], F(bound)))
    for player in range(width):
        row = [F(0)] * width
        row[player] = F(1)
        result.append((row, F(0)))
    return result


def lower_envelope(constraints):
    lower = inequalities(constraints)
    equality = [([F(1)] * N, TOTAL)]
    values, witnesses = [], []
    for coalition in range(64):
        objective = [F((coalition >> i) & 1) for i in range(N)]
        value, point = active_lp(objective, lower, equality)
        values.append(value)
        witnesses.append(point)
    return tuple(values), tuple(witnesses)


def selector(constraints, mode):
    pinned = {}
    free = set(range(N))
    base = inequalities(constraints)
    while free:
        stage_ineq = [(row + [F(0)], bound) for row, bound in base]
        stage_eq = [([F(1)] * N + [F(0)], TOTAL)]
        for player, value in pinned.items():
            row = [F(0)] * (N + 1)
            row[player] = F(1)
            stage_eq.append((row, value))
        for player in free:
            row = [F(0)] * (N + 1)
            row[player] = F(1 if mode == "min" else -1)
            row[N] = F(-1 if mode == "min" else 1)
            stage_ineq.append((row, F(0)))
        objective = [F(0)] * (N + 1)
        objective[N] = F(1)
        level, _ = active_lp(
            objective, stage_ineq, stage_eq, maximize=(mode == "min")
        )

        face_ineq = list(base)
        face_eq = [([F(1)] * N, TOTAL)]
        for player, value in pinned.items():
            row = [F(0)] * N
            row[player] = F(1)
            face_eq.append((row, value))
        for player in free:
            row = [F(0)] * N
            row[player] = F(1 if mode == "min" else -1)
            face_ineq.append((row, level if mode == "min" else -level))
        newly = []
        for player in sorted(free):
            objective = [F(0)] * N
            objective[player] = F(1)
            extreme, _ = active_lp(
                objective, face_ineq, face_eq, maximize=(mode == "min")
            )
            if extreme == level:
                newly.append(player)
        if not newly:
            raise AssertionError(("stage failed to pin", mode, level))
        for player in newly:
            pinned[player] = level
            free.remove(player)
    return tuple(pinned[i] for i in range(N))


def cover_census(values):
    tight = tuple(mask for mask in range(1, FULL) if csum(Z, mask) == values[mask])
    result = []
    for size in range(1, N - 1):
        for rows in itertools.combinations(tight, size):
            matrix, rhs = [], []
            for player in (2, 3, 4, 5):
                matrix.append([*(F((row >> player) & 1) for row in rows), F(-1)])
                rhs.append(F(0))
            matrix.append([*(F(((row >> 0) & 1) + ((row >> 1) & 1))
                               for row in rows), F(-2)])
            rhs.append(F(1))
            selected_rows, selected_rhs = [], []
            for row, bound in zip(matrix, rhs):
                if rank(selected_rows + [row]) > len(selected_rows):
                    selected_rows.append(row)
                    selected_rhs.append(bound)
            if len(selected_rows) != size + 1:
                continue
            solution = solve_unique(selected_rows, selected_rhs, size + 1)
            if solution is None:
                continue
            weights, eta = solution[:-1], solution[-1]
            if min(weights) <= 0 or eta < 0:
                continue
            loads = tuple(sum((weight for weight, row in zip(weights, rows)
                               if row >> i & 1), F(0)) for i in range(N))
            alpha = (loads[0] - eta, loads[1] - eta)
            if min(alpha) > 0 and sum(alpha) == 1 and all(
                loads[i] == eta for i in (2, 3, 4, 5)
            ):
                result.append((rows, weights, eta, alpha))
    return tuple(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values, witnesses = lower_envelope(DEFINING)
    if any(values[1 << i] for i in range(N)):
        raise AssertionError("singleton normalization")
    if selector(DEFINING, "min") != X or selector(DEFINING, "max") != Z:
        raise AssertionError("full selectors")
    xtight = tuple(mask for mask in range(1, FULL) if csum(X, mask) == values[mask])
    ztight = tuple(mask for mask in range(1, FULL) if csum(Z, mask) == values[mask])
    if xtight != CX or ztight != (3, 4, 7, 19, 23, 39, 43, 47):
        raise AssertionError((xtight, ztight))
    all_covers = cover_census(values)
    expected = ((3,), (19, 47), (23, 43), (4, 19, 43), (7, 19, 43))
    if tuple(item[0] for item in all_covers) != expected:
        raise AssertionError(all_covers)
    subset_results = {}
    for size in range(3):
        for rows in itertools.combinations(CX, size):
            retained = {row: csum(X, row) for row in rows}
            subset_results[rows] = selector(retained, "min")
    if subset_results[CX] != X or any(
        result == X for rows, result in subset_results.items() if rows != CX
    ):
        raise AssertionError("Cx not uniquely complete")
    lifts = []
    for rows, weights, eta, alpha in all_covers:
        retained = {row: csum(X, row) for row in CX}
        retained.update({row: csum(Z, row) for row in rows})
        lx, lz = selector(retained, "min"), selector(retained, "max")
        if lx != X or lz != ZP:
            raise AssertionError((rows, lx, lz))
        lifts.append({"rows": list(rows), "weights": list(map(str, weights)),
                      "eta": str(eta), "alpha": list(map(str, alpha))})

    bound = 2 * M + 4 * A
    target = F(2, 3) * TOTAL
    overlap = sum((min(a, b) for a, b in zip(X, Z)), F(0))
    if not (target - bound == F(2, 3) > 0 and overlap > target):
        raise AssertionError((bound, target, overlap))
    direction = tuple(ZP[i] - Z[i] for i in range(N))
    union = set().union(*(set(rows) for rows, *_rest in all_covers))
    if any(csum(direction, row) for row in (*CX, *union)):
        raise AssertionError("common tangent changed")
    negative = tuple(row for row in ztight if csum(direction, row) < 0)
    if negative != (39,) or 39 in union:
        raise AssertionError((negative, union))

    payload = {
        "claim": "independent exact active-set replay of the PXC122 anchor",
        "parameters": {"A": str(A), "B": str(B), "K": str(K),
                       "M": str(M), "C": str(C), "T": str(TOTAL)},
        "all_64_coalition_minima": list(map(str, values)),
        "singleton_minimizers": [list(map(str, witnesses[1 << i])) for i in range(N)],
        "x": list(map(str, X)), "z": list(map(str, Z)),
        "unique_complete_cx": list(CX),
        "covers": lifts,
        "common_wrong_lmax": list(map(str, ZP)),
        "forced_zero_blocker": 39,
        "B_H": str(bound), "target": str(target),
        "positive_post_top_demand": str(target - bound),
        "overlap": str(overlap),
        "independence": (
            "standalone exact active-set LP, Gaussian cover census, and staged "
            "selector; imports no project or primary PXC122 implementation"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
