#!/usr/bin/env python3
"""Independent exact replay of the PXC101 all-dimension family.

This file imports no project LP, game, selector, cover, or family code.  It
uses a small rational active-set enumerator for the six-player anchor and
separately checks the generic incidence/weight algebra through n=44.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def mask(*players):
    return sum(1 << i for i in players)


def csum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def unique_solution(matrix, rhs, width):
    work = [list(map(F, row)) + [F(b)] for row, b in zip(matrix, rhs)]
    cursor = 0
    pivots = []
    for column in range(width):
        pivot = next((i for i in range(cursor, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[cursor], work[pivot] = work[pivot], work[cursor]
        scale = work[cursor][column]
        work[cursor] = [q / scale for q in work[cursor]]
        for i in range(len(work)):
            if i != cursor and work[i][column]:
                scale = work[i][column]
                work[i] = [a - scale * b for a, b in zip(work[i], work[cursor])]
        pivots.append(column)
        cursor += 1
    if any(not any(row[:width]) and row[width] for row in work):
        return None
    if len(pivots) != width:
        return None
    answer = [F(0)] * width
    for i, column in enumerate(pivots):
        answer[column] = work[i][width]
    return tuple(answer)


def active_lp(objective, inequalities, equalities, maximize=False):
    width = len(objective)
    need = width - len(equalities)
    best = None
    best_point = None
    for selected in itertools.combinations(range(len(inequalities)), need):
        matrix = [row for row, _ in equalities]
        rhs = [bound for _, bound in equalities]
        matrix += [inequalities[i][0] for i in selected]
        rhs += [inequalities[i][1] for i in selected]
        point = unique_solution(matrix, rhs, width)
        if point is None:
            continue
        if any(sum(a * b for a, b in zip(row, point)) < bound
               for row, bound in inequalities):
            continue
        value = sum(a * b for a, b in zip(objective, point))
        if best is None or (value > best if maximize else value < best):
            best, best_point = value, point
    if best is None:
        raise AssertionError("active-set LP has no feasible vertex")
    return best, best_point


def inequalities(constraints, n, width=None):
    width = n if width is None else width
    answer = []
    for coalition, bound in constraints.items():
        row = [F((coalition >> i) & 1) for i in range(n)] + [F(0)] * (width - n)
        answer.append((row, bound))
    for i in range(n):
        row = [F(0)] * width
        row[i] = F(1)
        answer.append((row, F(0)))
    return answer


def lower_envelope(constraints, n, total):
    lower = inequalities(constraints, n)
    equal = [([F(1)] * n, total)]
    values = []
    witnesses = []
    for coalition in range(1 << n):
        objective = [F((coalition >> i) & 1) for i in range(n)]
        value, point = active_lp(objective, lower, equal)
        values.append(value)
        witnesses.append(point)
    return tuple(values), tuple(witnesses)


def selector(constraints, n, total, mode):
    pinned = {}
    free = set(range(n))
    while free:
        width = n + 1
        lower = inequalities(constraints, n, width)
        equal = [([F(1)] * n + [F(0)], total)]
        for i, value in pinned.items():
            row = [F(0)] * width
            row[i] = F(1)
            equal.append((row, value))
        for i in free:
            row = [F(0)] * width
            row[i] = F(1 if mode == "min" else -1)
            row[n] = F(-1 if mode == "min" else 1)
            lower.append((row, F(0)))
        objective = [F(0)] * width
        objective[n] = F(1)
        level, _ = active_lp(objective, lower, equal, mode == "min")

        lower = inequalities(constraints, n)
        equal = [([F(1)] * n, total)]
        for i, value in pinned.items():
            row = [F(0)] * n
            row[i] = F(1)
            equal.append((row, value))
        for i in free:
            row = [F(0)] * n
            row[i] = F(1 if mode == "min" else -1)
            lower.append((row, level if mode == "min" else -level))
        newly = []
        for i in sorted(free):
            objective = [F(0)] * n
            objective[i] = F(1)
            extreme, _ = active_lp(objective, lower, equal, mode == "min")
            if extreme == level:
                newly.append(i)
        if not newly:
            raise AssertionError(("empty selector stage", mode, level))
        for i in newly:
            pinned[i] = level
            free.remove(i)
    return tuple(pinned[i] for i in range(n))


def family(k):
    n = k + 4
    outsiders = tuple(range(4, n))
    constraints = {
        mask(0, 1, 2): F(11), mask(0, 1, 3): F(11),
        mask(0, 4): F(6), mask(0, 1, *outsiders): F(k + 9),
    }
    total = F(k + 15)
    u = F(k + 4, k + 1)
    p = F(10 * k + 7, 2 * (k + 1))
    x = (p, p) + (u,) * (k + 2)
    z = (F(4), F(4), F(3), F(3), F(2)) + (F(1),) * (k - 1)
    reduced = (F(4), F(4), F(3), F(3)) + (F(k + 1, k),) * k
    return n, total, constraints, x, z, reduced


def cover_census(ztight, n, z):
    top = (0, 1)
    outsiders = tuple(range(2, n))
    found = []
    for size in range(1, n - 1):
        for support in itertools.combinations(ztight, size):
            matrix = []
            rhs = []
            for i in outsiders:
                matrix.append([*(F((row >> i) & 1) for row in support), F(-1)])
                rhs.append(F(0))
            matrix.append([
                *(F(((row >> 0) & 1) + ((row >> 1) & 1)) for row in support),
                F(-2),
            ])
            rhs.append(F(1))
            solution = unique_solution(matrix, rhs, size + 1)
            if solution is None:
                continue
            weights, eta = solution[:-1], solution[-1]
            if min(weights) <= 0 or eta < 0:
                continue
            loads = tuple(sum((weight for row, weight in zip(support, weights)
                               if row >> i & 1), F(0)) for i in range(n))
            alpha = (loads[0] - eta, loads[1] - eta)
            if min(alpha) > 0 and sum(alpha, F(0)) == 1:
                found.append((support, weights, eta, alpha))
    return tuple(found)


def replay(k):
    n, total, constraints, expected_x, expected_z, expected_reduced = family(k)
    values, witnesses = lower_envelope(constraints, n, total)
    if any(values[1 << i] for i in range(n)):
        raise AssertionError(("normalization", k))
    x = selector(constraints, n, total, "min")
    z = selector(constraints, n, total, "max")
    if x != expected_x or z != expected_z:
        raise AssertionError(("selectors", k, x, z))
    full = (1 << n) - 1
    xtight = tuple(s for s in range(1, full) if csum(x, s) == values[s])
    ztight = tuple(s for s in range(1, full) if csum(z, s) == values[s])
    cx = (mask(0, 1, 2), mask(0, 1, 3))
    all_out = mask(0, 1, *range(4, n))
    if xtight != cx or ztight != (mask(0, 1), *cx, mask(0, 4), all_out):
        raise AssertionError(("tight menus", k, xtight, ztight))
    complete = []
    for size in range(3):
        for rows in itertools.combinations(cx, size):
            retained = {row: csum(x, row) for row in rows}
            if selector(retained, n, total, "min") == x:
                complete.append(rows)
    if complete != [cx]:
        raise AssertionError(("Cx", k, complete))
    covers = cover_census(ztight, n, z)
    expected_supports = ((mask(0, 1),), (*cx, all_out))
    if tuple(q[0] for q in covers) != expected_supports:
        raise AssertionError(("covers", k, covers))
    lifts = []
    for support, weights, eta, alpha in covers:
        retained = {row: csum(x, row) for row in cx}
        retained.update({row: csum(z, row) for row in support})
        lx = selector(retained, n, total, "min")
        lz = selector(retained, n, total, "max")
        if lx != x or lz != expected_reduced:
            raise AssertionError(("lift", k, support, lx, lz))
        lifts.append({
            "support": list(support), "weights": list(map(str, weights)),
            "eta": str(eta), "alpha": list(map(str, alpha)),
            "lmax": list(map(str, lz)),
        })
    return {
        "n": n,
        "selectors": {"lmin": list(map(str, x)), "lmax": list(map(str, z))},
        "tight_menus": {"x": list(xtight), "z": list(ztight)},
        "singleton_minimizers": [list(map(str, witnesses[1 << i])) for i in range(n)],
        "covers": lifts,
    }


def generic_algebra():
    records = []
    for k in range(2, 41):
        n, total, constraints, x, z, reduced = family(k)
        if sum(x, F(0)) != total or sum(z, F(0)) != total or sum(reduced, F(0)) != total:
            raise AssertionError(("generic efficiency", k))
        direction = tuple(a - b for a, b in zip(reduced, z))
        cover_rows = (mask(0, 1), mask(0, 1, 2), mask(0, 1, 3),
                      mask(0, 1, *range(4, n)))
        if any(csum(direction, row) for row in cover_rows):
            raise AssertionError(("generic visibility", k))
        if csum(direction, mask(0, 4)) >= 0:
            raise AssertionError(("generic blocker", k))
        if k in (2, 3, 8, 16, 40):
            records.append({"n": n, "direction": list(map(str, direction))})
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "independent exact replay of the PXC101 forced-zero family",
        "generic_algebra": generic_algebra(),
        "exact_active_set_replays": [replay(2)],
        "independence": "imports no project LP, selector, cover, game, or family implementation",
        "scope": "independent exact lower-envelope replay at n=6 plus dimension-free rational identities",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
