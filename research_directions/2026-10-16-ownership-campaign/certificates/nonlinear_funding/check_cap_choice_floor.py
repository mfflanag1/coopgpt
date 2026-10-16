#!/usr/bin/env python3
"""Exact finite checks of the coverage relaxation, not an incentive proof.

All numbers are Fractions. We independently minimize the concave capped-payment
objective over every vertex of the stated small polytope, then compare the two
explicit floors and the weighted floor. Generated feasible payments are efficient
short-pool coverage allocations; this checks the abstract coalition-floor algebra,
not the exponential primitive or its all-profile response theorem.
"""
from fractions import Fraction as F
from itertools import combinations
import hashlib
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), F(0))


def solve(matrix, rhs):
    d = len(rhs)
    rows = [list(row) + [b] for row, b in zip(matrix, rhs)]
    for col in range(d):
        pivot = next((r for r in range(col, d) if rows[r][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for r in range(d):
            if r != col and rows[r][col]:
                scale = rows[r][col]
                rows[r] = [a - scale * b for a, b in zip(rows[r], rows[col])]
    return tuple(row[-1] for row in rows)


def exercise(case):
    h, ell, ceilings, headroom = case
    n = len(h)
    q = n - 1
    coal = lambda mask: min(
        sum((h[k] for k in range(n) if mask >> k & 1), F(0)),
        sum((ell[k] for k in range(n) if mask >> k & 1), F(0)),
    )
    actual = h if sum(h) <= sum(ell) else ell
    require(all(y <= u for y, u in zip(actual, ceilings)), "bad fixture ceiling")
    masks = range(1 << q)
    # All inequalities are row * v >= rhs, with the ordinary coalition at index 0.
    inequalities = set()
    for mask in masks:
        for ordinary in (0, 1):
            fullmask = (mask << 1) | ordinary
            row = tuple(F((fullmask >> k) & 1) for k in range(n))
            inequalities.add((row, coal(fullmask)))
    for k in range(n):
        row = tuple(F(j == k) for j in range(n))
        inequalities.add((row, F(0)))
        inequalities.add((tuple(-x for x in row), -ceilings[k]))
    inequalities = [(a, b) for a, b in inequalities if any(a)]
    require(all(dot(a, actual) >= b for a, b in inequalities), "fixture not covered")
    vertices = set()
    for indices in combinations(range(len(inequalities)), n):
        point = solve([inequalities[k][0] for k in indices],
                      [inequalities[k][1] for k in indices])
        if point is not None and all(dot(a, point) >= b for a, b in inequalities):
            vertices.add(point)
    require(vertices, "no polytope vertex found")
    objective = lambda v: v[0] + sum((min(v[k + 1], headroom[k]) for k in range(q)), F(0))
    optimum = min(objective(v) for v in vertices)
    # Independent enumeration of the at-most-eight linear cap choices.
    min_lps = min(
        sum((headroom[k] for k in range(q) if not (mask >> k & 1)), F(0))
        + min(v[0] + sum((v[k + 1] for k in range(q) if mask >> k & 1), F(0))
              for v in vertices)
        for mask in masks
    )
    require(optimum == min_lps, "cap-choice/vertex identity")
    basic = min(coal((mask << 1) | 1)
                + sum((headroom[k] for k in range(q) if not (mask >> k & 1)), F(0))
                for mask in masks)
    upper = min(
        sum((headroom[k] for k in range(q) if not (mask >> k & 1)), F(0))
        + max(coal(((mask | add) << 1) | 1)
              - sum((ceilings[k + 1] for k in range(q) if add >> k & 1), F(0))
              for add in masks if not (mask & add))
        for mask in masks
    )
    weights = [F(1)] + [min(F(1), headroom[k] / ceilings[k + 1])
                       if ceilings[k + 1] else F(1) for k in range(q)]
    thresholds = sorted(set([F(0), F(1)] + weights))
    weighted = sum((hi - lo) * coal(sum(1 << k for k in range(n) if weights[k] >= hi))
                   for lo, hi in zip(thresholds, thresholds[1:]))
    require(basic <= upper <= optimum <= objective(actual), "floor ordering")
    require(weighted <= optimum, "weighted domination")
    return {"exception_count": q, "vertices": len(vertices),
            "basic": str(basic), "upper": str(upper), "weighted": str(weighted),
            "lp": str(optimum), "feasible_objective": str(objective(actual))}


def main():
    # Zero capacities, empty ordinary group, zero/tied weights, and q=0,1,2,3.
    raw = [
        ([1], [1], [1], []),
        ([1, 0], [0, 1], [1, 1], [F(1, 4)]),
        ([1, 0], [0, 1], [1, F(3, 5)], [F(1, 5)]),
        ([0, 1], [0, 1], [0, 1], [0]),
        ([F(1, 2), F(1, 2)], [1, 1], [F(3, 4), 1], [F(1, 2)]),
        ([1, 0, 0], [0, F(1, 2), F(1, 2)], [1, F(3, 4), F(3, 4)], [F(1, 4), F(1, 4)]),
        ([0, F(1, 2), F(1, 2)], [0, F(1, 2), F(1, 2)], [0, 1, 1], [0, 1]),
        ([F(1, 2), F(1, 4), F(1, 4)], [F(1, 4), F(3, 4), F(1, 2)],
         [F(3, 4), F(1, 2), F(1, 2)], [F(1, 4), F(1, 3)]),
        ([1, 0, 0, 0], [0, F(1, 3), F(1, 3), F(1, 3)],
         [1, F(1, 2), F(1, 2), F(1, 2)], [0, F(1, 4), F(1, 4)]),
        ([F(1, 4)] * 4, [F(1, 4)] * 4, [F(1, 2)] * 4,
         [F(1, 4), F(1, 3), F(1, 2)]),
    ]
    cases = [[list(map(F, row)) for row in case] for case in raw]
    results = [exercise(case) for case in cases]
    directory = Path(__file__).resolve().parent
    sources = [Path(__file__).name, "THREE_CAP_RECIPIENT_REDUCTION.txt",
               "FINITE_CAP_CHOICE_COALITION_FLOOR.txt"]
    output = {"status": "PASS", "arithmetic": "exact Fraction arithmetic",
              "scope": "finite abstract coverage-relaxation checks, not all-profile incentive verification",
              "cases": results,
              "sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                         for name in sources}}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
