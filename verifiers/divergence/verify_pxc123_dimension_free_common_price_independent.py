#!/usr/bin/env python3
"""Independent standalone exact incidence/algebra replay for PXC123.

This file imports no project, selector, cover, or primary PXC123 code.  It
checks the parameter-independent six-type normal cones and normalized-cover
vertices by its own rational elimination, then checks every symbolic price
identity and parity branch on exact rational samples through t=64.  The
separate PXC122 independent active-set verifier supplies the full n=6 game
and selector calibration.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def rank(rows: list[list[F]]) -> int:
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


def solve_unique(rows: list[list[F]], rhs: list[F], width: int):
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
    result = [F(0)] * width
    for i, column in enumerate(pivots):
        result[column] = augmented[i][-1]
    return tuple(result)


def incidence(mask: int) -> tuple[F, ...]:
    return tuple(F((mask >> i) & 1) for i in range(6))


def cone_menu(generators: tuple[int, ...]) -> tuple[int, ...]:
    answer = []
    for objective in range(64):
        target = incidence(objective)
        found = False
        for size in range(len(generators) + 1):
            for chosen in itertools.combinations(generators, size):
                matrix = [[*(incidence(row)[i] for row in chosen), F(1)]
                          for i in range(6)]
                picked, rhs = [], []
                for row, bound in zip(matrix, target):
                    if rank(picked + [row]) > len(picked):
                        picked.append(row)
                        rhs.append(bound)
                if len(picked) != size + 1:
                    continue
                solution = solve_unique(picked, rhs, size + 1)
                if solution is None or any(value < 0 for value in solution[:-1]):
                    continue
                if all(sum((a * b for a, b in zip(row, solution)), F(0)) == bound
                       for row, bound in zip(matrix, target)):
                    found = True
                    break
            if found:
                break
        if found:
            answer.append(objective)
    return tuple(answer)


def cover_vertices(menu: tuple[int, ...]):
    proper = tuple(mask for mask in menu if mask not in (0, 63))
    vertices = []
    for size in range(1, 5):
        for chosen in itertools.combinations(proper, size):
            equations, rhs = [], []
            for player in (2, 3, 4, 5):
                equations.append([*(incidence(row)[player] for row in chosen), F(-1)])
                rhs.append(F(0))
            equations.append([
                *(incidence(row)[0] + incidence(row)[1] for row in chosen), F(-2)
            ])
            rhs.append(F(1))
            picked, picked_rhs = [], []
            for row, bound in zip(equations, rhs):
                if rank(picked + [row]) > len(picked):
                    picked.append(row)
                    picked_rhs.append(bound)
            if len(picked) != size + 1:
                continue
            solution = solve_unique(picked, picked_rhs, size + 1)
            if solution is None:
                continue
            weights, eta = solution[:-1], solution[-1]
            if min(weights) <= 0 or eta < 0:
                continue
            if not all(sum((a * b for a, b in zip(row, solution)), F(0)) == bound
                       for row, bound in zip(equations, rhs)):
                continue
            loads = tuple(sum((weight for weight, row in zip(weights, chosen)
                               if row >> i & 1), F(0)) for i in range(6))
            alpha = (loads[0] - eta, loads[1] - eta)
            if min(alpha) > 0 and sum(alpha) == 1:
                vertices.append((chosen, weights, eta, alpha))
    return tuple(vertices)


def coefficient(n: int) -> F:
    return F(n, (n * n) // 4)


def sample(t: int, A: F, B: F, K0: F, M: F, label: str) -> dict[str, str | int]:
    C = A + (t + 1) * B - t * K0
    T = 2 * M + 3 * A + (t + 1) * B
    beta = min(B, C)
    if t == 1:
        BH = 2 * M + 4 * A
        O = 2 * M + A + B + beta
        price = (B - A) + (beta - 2 * A)
    else:
        BH = 2 * M + 4 * A + (t - 2) * B + beta
        O = 2 * M + A + t * B + beta
        price = 2 * B - 3 * A
    demand = max(F(0), coefficient(t + 5) * T - BH)
    assert 0 < A and 3 * A < B
    assert B + A / (t + 1) < K0 < B + 2 * A / t
    assert 2 * A < B and B - A < C < K0 < M
    assert O - BH == price and price >= demand and O >= coefficient(t + 5) * T
    if t == 1:
        if demand > 0:
            assert price - demand == (2 * M + 3 * beta - B - 3 * A) / 3
            assert price - demand > (4 * B - 6 * A) / 3 > 0
    elif t == 2:
        assert 12 * BH - 7 * T == 10 * M + 27 * A + 12 * beta - 21 * B
        assert 12 * BH - 7 * T > B + 15 * A > 0
        assert demand == 0
    else:
        assert coefficient(t + 5) <= F(1, 2)
        assert 2 * BH - T == 2 * M + 5 * A + (t - 5) * B + 2 * beta
        assert 2 * BH - T > (t - 1) * B + 3 * A > 0
        assert demand == 0
    return {"label": label, "t": t, "n": t + 5, "demand": str(demand),
            "price": str(price), "slack": str(O - coefficient(t + 5) * T)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    x_menu = cone_menu((19, 43))
    z_menu = cone_menu((3, 19, 39, 43, 4))
    assert x_menu == (0, 19, 43, 63)
    assert z_menu == (0, 3, 4, 7, 19, 23, 39, 43, 47, 63)
    vertices = cover_vertices(z_menu)
    expected = ((3,), (19, 47), (23, 43), (4, 19, 43), (7, 19, 43))
    assert tuple(item[0] for item in vertices) == expected
    points = [
        (1, F(1, 2), F(9, 4), F(3), F(6), "PXC116-C-below-B"),
        (1, F(1), F(5), F(29, 5), F(6), "PXC122-positive-demand-C-above-B"),
    ]
    for t in range(2, 65):
        A, B = F(1), F(5)
        K0 = B + (F(1, t + 1) + F(2, t)) / 2
        M = K0 + F(1, 2)
        points.append((t, A, B, K0, M, f"symmetric-block-t={t}"))
    samples = [sample(*entry) for entry in points]
    payload = {
        "claim": "independent typed incidence and all-t algebra audit for PXC123",
        "x_type_menu": list(x_menu),
        "z_type_menu": list(z_menu),
        "cover_vertices": [
            {"rows": list(rows), "weights": list(map(str, weights)),
             "eta": str(eta), "alpha": list(map(str, alpha))}
            for rows, weights, eta, alpha in vertices
        ],
        "samples": samples,
        "independence": (
            "standalone Fraction elimination; no project, selector, cover, "
            "or primary PXC123 imports"
        ),
        "scope": (
            "parameter-independent six-type incidence plus exact t=1..64 "
            "algebra; conventional displayed proof carries the all-t theorem"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
