#!/usr/bin/env python3
"""Independent exact active-set audit of the PXC98 n=6 obstruction.

No project game, LP, selector, or cover implementation is imported.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

N = 6; FULL = (1 << N) - 1; TOTAL = F(17)
DEFINING = {7: F(11), 11: F(11), 17: F(6), 51: F(11)}
X = (F(9, 2), F(9, 2), F(2), F(2), F(2), F(2))
Z = tuple(map(F, (4, 4, 3, 3, 2, 1)))
ZPRIME = (F(4), F(4), F(3), F(3), F(3, 2), F(3, 2))
CX = (7, 11)


def csum(point, mask):
    return sum((point[i] for i in range(N) if mask >> i & 1), F(0))


def rref_unique(matrix, rhs, width):
    aug = [list(map(F, row)) + [F(b)] for row, b in zip(matrix, rhs)]
    cursor = 0; pivots = []
    for column in range(width):
        pivot = next((r for r in range(cursor, len(aug)) if aug[r][column]), None)
        if pivot is None: continue
        aug[cursor], aug[pivot] = aug[pivot], aug[cursor]
        q = aug[cursor][column]; aug[cursor] = [v / q for v in aug[cursor]]
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


def lp_active(objective, inequalities, equalities, maximize):
    width = len(objective); need = width - len(equalities)
    eq_rows = [list(q[0]) for q in equalities]; eq_rhs = [F(q[1]) for q in equalities]
    best = None; best_point = None
    for chosen in itertools.combinations(range(len(inequalities)), need):
        rows = eq_rows + [list(inequalities[i][0]) for i in chosen]
        rhs = eq_rhs + [inequalities[i][1] for i in chosen]
        point = rref_unique(rows, rhs, width)
        if point is None: continue
        if any(sum(a*b for a, b in zip(row, point)) < bound
               for row, bound in inequalities): continue
        value = sum(a*b for a, b in zip(objective, point))
        if best is None or (value > best if maximize else value < best):
            best, best_point = value, point
    if best is None: raise AssertionError("active-set LP found no vertex")
    return best, best_point


def base_inequalities(constraints, width=N):
    answer = []
    for mask, bound in constraints.items():
        answer.append(([F((mask >> i) & 1) for i in range(N)]
                       + [F(0)] * (width - N), F(bound)))
    for i in range(N):
        row = [F(0)] * width; row[i] = F(1); answer.append((row, F(0)))
    return answer


def lower_envelope(constraints):
    inequalities = base_inequalities(constraints); equalities = [([F(1)] * N, TOTAL)]
    values = []
    for mask in range(1 << N):
        objective = [F((mask >> i) & 1) for i in range(N)]
        optimum, _ = lp_active(objective, inequalities, equalities, False)
        values.append(optimum)
    return tuple(values)


def sparse_selector(constraints, mode):
    pinned = {}; free = set(range(N)); base = base_inequalities(constraints)
    while free:
        inequalities = [(row + [F(0)], bound) for row, bound in base]
        equalities = [([F(1)] * N + [F(0)], TOTAL)]
        for i, value in pinned.items():
            row = [F(0)] * (N + 1); row[i] = F(1); equalities.append((row, value))
        for i in free:
            row = [F(0)] * (N + 1)
            if mode == "min": row[i], row[N] = F(1), F(-1)
            else: row[i], row[N] = F(-1), F(1)
            inequalities.append((row, F(0)))
        objective = [F(0)] * (N + 1); objective[N] = F(1)
        level, _ = lp_active(objective, inequalities, equalities, mode == "min")
        inequalities2 = list(base); equalities2 = [([F(1)] * N, TOTAL)]
        for i, value in pinned.items():
            row = [F(0)] * N; row[i] = F(1); equalities2.append((row, value))
        for i in free:
            row = [F(0)] * N; row[i] = F(1 if mode == "min" else -1)
            inequalities2.append((row, level if mode == "min" else -level))
        newly = []
        for i in sorted(free):
            objective = [F(0)] * N; objective[i] = F(1)
            extreme, _ = lp_active(objective, inequalities2, equalities2,
                                   mode == "min")
            if extreme == level: newly.append(i)
        if not newly: raise AssertionError(("no staged pin", mode, level))
        for i in newly: pinned[i] = level; free.remove(i)
    return tuple(pinned[i] for i in range(N))


def normalized_covers(values):
    tight = tuple(mask for mask in range(1, FULL) if csum(Z, mask) == values[mask])
    answer = []
    for size in range(1, N - 1):
        for rows in itertools.combinations(tight, size):
            matrix = []; rhs = []
            for i in (2, 3, 4, 5):
                matrix.append([*(F((row >> i) & 1) for row in rows), F(-1)]); rhs.append(F(0))
            matrix.append([*(F(((row >> 0) & 1) + ((row >> 1) & 1))
                               for row in rows), F(-2)]); rhs.append(F(1))
            solution = rref_unique(matrix, rhs, size + 1)
            if solution is None: continue
            weights, eta = solution[:-1], solution[-1]
            loads = tuple(sum((w for w, row in zip(weights, rows) if row >> i & 1), F(0))
                          for i in range(N))
            alpha = (loads[0] - eta, loads[1] - eta)
            if min(weights) > 0 and eta >= 0 and min(alpha) > 0 and sum(alpha) == 1:
                answer.append((rows, weights, eta, alpha))
    return tuple(answer)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); values = lower_envelope(DEFINING)
    if any(values[1 << i] != 0 for i in range(N)): raise AssertionError("normalization")
    if sparse_selector(DEFINING, "min") != X or sparse_selector(DEFINING, "max") != Z:
        raise AssertionError("full selectors changed")
    xtight = tuple(m for m in range(1, FULL) if csum(X, m) == values[m])
    ztight = tuple(m for m in range(1, FULL) if csum(Z, m) == values[m])
    if xtight != CX or ztight != (3, 7, 11, 17, 51): raise AssertionError((xtight, ztight))
    covers = normalized_covers(values)
    if tuple(q[0] for q in covers) != ((3,), (7, 11, 51)): raise AssertionError(covers)
    subset_lmins = []
    for size in range(3):
        for rows in itertools.combinations(CX, size):
            lx = sparse_selector({m: csum(X, m) for m in rows}, "min")
            subset_lmins.append({"rows": list(rows), "lmin": list(map(str, lx)),
                                 "complete": lx == X})
    if [q["rows"] for q in subset_lmins if q["complete"]] != [[7, 11]]:
        raise AssertionError("complete-Cx uniqueness failed")
    lifts = []
    for rows, weights, eta, alpha in covers:
        constraints = {m: csum(X, m) for m in CX}
        constraints.update({m: csum(Z, m) for m in rows})
        lx = sparse_selector(constraints, "min"); lz = sparse_selector(constraints, "max")
        if lx != X or lz != ZPRIME: raise AssertionError((rows, lx, lz))
        lifts.append({"rows": list(rows), "weights": list(map(str, weights)),
                      "eta": str(eta), "alpha": list(map(str, alpha)),
                      "lmin": list(map(str, lx)), "lmax": list(map(str, lz))})
    inequalities = base_inequalities(DEFINING); equalities = [([F(1)] * N, TOTAL)]
    witnesses = []
    for i in range(N):
        objective = [F(0)] * N; objective[i] = F(1)
        optimum, point = lp_active(objective, inequalities, equalities, False)
        if optimum != 0: raise AssertionError(("positive singleton", i, optimum))
        witnesses.append({"player": i, "allocation": list(map(str, point))})
    payload = {
        "claim": "exact unrestricted six-player PXC91c counterexample",
        "game": {"n": N, "total": str(TOTAL),
                 "defining_rows": {str(k): str(v) for k, v in DEFINING.items()},
                 "all_coalition_values": list(map(str, values)),
                 "singleton_normalized": True, "singleton_witnesses": witnesses,
                 "exactness": "lower envelope of the displayed nonempty compact polytope"},
        "selectors": {"lmin": list(map(str, X)), "lmax": list(map(str, Z))},
        "tight_menus": {"x": list(xtight), "z": list(ztight)},
        "complete_cx_exhaustion": subset_lmins, "extreme_covers": lifts,
        "common_reduced_lmax": list(map(str, ZPRIME)),
        "fixed_cx_refuted": True, "existential_cx_refuted": True,
        "independence": "no project LP, selector, cover, or game implementation imported",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__": main()
