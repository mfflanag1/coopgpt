#!/usr/bin/env python3
"""Standalone exact vertex-enumeration replay of PXC128.

This implementation imports neither the project LP solver nor the primary
PXC128 verifier.  It independently builds the canonical carriers and solves
the fractional cut-cover primal and dual by rational vertex enumeration.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def solve_square(matrix, rhs):
    n = len(rhs)
    a = [list(map(F, row)) + [F(value)] for row, value in zip(matrix, rhs)]
    for col in range(n):
        pivot = next((row for row in range(col, n) if a[row][col]), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [value / scale for value in a[col]]
        for row in range(n):
            if row == col or not a[row][col]:
                continue
            scale = a[row][col]
            a[row] = [left - scale * right for left, right in zip(a[row], a[col])]
    return tuple(a[row][-1] for row in range(n))


def canonical_carriers(x, z, top):
    residual = tuple(i for i in range(len(x)) if i not in top)
    lo = tuple(min(x[i], z[i]) for i in range(len(x)))
    hi = tuple(max(x[i], z[i]) for i in range(len(x)))
    sources = sorted(residual, key=lambda i: (-lo[i], i))
    sinks = sorted(residual, key=lambda i: (hi[i], i))
    return tuple(
        (source, sink, lo[source] - hi[sink])
        for source, sink in zip(sources, sinks)
        if lo[source] > hi[sink]
    )


def incidence(rows, edges):
    return tuple(tuple(F(
        ((row >> source) & 1) != ((row >> sink) & 1)
    ) for row in rows) for source, sink, _ in edges)


def primal_vertices(A):
    q = len(A)
    r = len(A[0])
    constraints = []
    # Active cover rows A_e theta = 1.
    constraints += [(tuple(A[e]), F(1)) for e in range(q)]
    # Active nonnegativity theta_c = 0.
    constraints += [(
        tuple(F(int(c == d)) for c in range(r)), F(0)
    ) for d in range(r)]
    for chosen in itertools.combinations(range(q + r), r):
        point = solve_square(
            [constraints[index][0] for index in chosen],
            [constraints[index][1] for index in chosen],
        )
        if point is None or any(value < 0 for value in point):
            continue
        if any(sum(A[e][c] * point[c] for c in range(r)) < 1 for e in range(q)):
            continue
        yield point


def dual_vertices(A):
    q = len(A)
    r = len(A[0])
    constraints = []
    # Active row capacities sum_e A_ec y_e = 1.
    constraints += [(
        tuple(A[e][c] for e in range(q)), F(1)
    ) for c in range(r)]
    # Active nonnegativity y_e = 0.
    constraints += [(
        tuple(F(int(e == f)) for e in range(q)), F(0)
    ) for f in range(q)]
    for chosen in itertools.combinations(range(r + q), q):
        point = solve_square(
            [constraints[index][0] for index in chosen],
            [constraints[index][1] for index in chosen],
        )
        if point is None or any(value < 0 for value in point):
            continue
        if any(sum(A[e][c] * point[e] for e in range(q)) > 1 for c in range(r)):
            continue
        yield point


def solve_profile(name, x, z, top, rows):
    edges = canonical_carriers(x, z, top)
    A = incidence(rows, edges)
    if any(not any(line) for line in A):
        return {
            "name": name, "carriers": edges, "incidence": A,
            "chi": "infinity", "uncut_edges": tuple(
                edges[e] for e, line in enumerate(A) if not any(line)
            ),
        }
    primals = tuple(primal_vertices(A))
    duals = tuple(dual_vertices(A))
    if not primals or not duals:
        raise AssertionError((name, "missing vertex"))
    theta = min(primals, key=lambda point: (sum(point, F(0)), point))
    y = max(duals, key=lambda point: (sum(point, F(0)), point))
    chi = sum(theta, F(0))
    if sum(y, F(0)) != chi:
        raise AssertionError((name, "duality", theta, y))
    lengths = tuple(edge[2] for edge in edges)
    canonical_prices = tuple(sum((
        lengths[e] * A[e][c] for e in range(len(edges))
    ), F(0)) for c in range(len(rows)))
    if max(canonical_prices) * chi < sum(lengths, F(0)):
        raise AssertionError((name, "PXC128b"))
    return {
        "name": name, "carriers": edges, "incidence": A,
        "chi": chi, "theta": theta, "dual_y": y,
        "canonical_cut_prices": canonical_prices,
        "label_currency": sum(lengths, F(0)),
    }


def stringify(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [stringify(item) for item in value]
    if isinstance(value, dict):
        return {str(key): stringify(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    controls = (
        solve_profile(
            "PXC122_t1",
            (F(13, 2), F(13, 2), F(1), F(5), F(1), F(5)),
            (F(6), F(6), F(0), F(26, 5), F(2), F(29, 5)),
            (0, 1), (19, 43),
        ),
        solve_profile(
            "PXC127",
            (F(32, 5), F(32, 5), F(1), F(51, 10), F(1), F(51, 10)),
            (F(6), F(6), F(1, 5), F(26, 5), F(9, 5), F(29, 5)),
            (0, 1), (19, 43),
        ),
        solve_profile(
            "fractional_triangle",
            (F(6), F(0), F(5), F(1), F(4), F(2)),
            (F(6), F(0), F(5), F(1), F(4), F(2)),
            (), (5, 17, 20),
        ),
        solve_profile(
            "unseparated_carrier",
            (F(4), F(0), F(3), F(1)),
            (F(4), F(0), F(3), F(1)),
            (), (3,),
        ),
    )
    if (
        controls[0]["chi"] != 1
        or controls[1]["chi"] != 1
        or controls[2]["chi"] != F(3, 2)
        or controls[3]["chi"] != "infinity"
    ):
        raise AssertionError("standalone controls changed")
    payload = stringify({
        "claim": "standalone exact vertex-enumeration replay of PXC128",
        "controls": controls,
        "independence": (
            "independent carrier ordering, Gaussian elimination, and primal/dual "
            "vertex enumeration; imports no project LP or primary PXC128 code"
        ),
        "scope": "audits the fractional cut-cover theorem, not the open MCP--MWP extension",
    })
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
