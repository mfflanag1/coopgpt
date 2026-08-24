#!/usr/bin/env python3
"""Independent exact replay of the PXC127 game and cut price.

Uses the standalone Fraction active-set engine from the independent PXC122
audit, but no project game, selector, cover, PXC108, PXC126, PXC127, or
primary-verifier implementation.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from verify_pxc122_positive_common_price_independent import (  # noqa: E402
    csum,
    lower_envelope,
    rank,
    selector,
    solve_unique,
)


N = 6
TOTAL = F(25)
FULL = (1 << N) - 1
DEFINING = {3: F(12), 19: F(69, 5), 39: F(89, 5), 43: F(23), 55: F(99, 5)}
X = (F(32, 5), F(32, 5), F(1), F(51, 10), F(1), F(51, 10))
Z = (F(6), F(6), F(1, 5), F(26, 5), F(9, 5), F(29, 5))
ZP = (F(6), F(6), F(1, 5), F(11, 2), F(9, 5), F(11, 2))


def cover_census(values, z):
    tight = tuple(mask for mask in range(1, FULL) if csum(z, mask) == values[mask])
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
            chosen_rows, chosen_rhs = [], []
            for row, bound in zip(matrix, rhs):
                if rank(chosen_rows + [row]) > len(chosen_rows):
                    chosen_rows.append(row)
                    chosen_rhs.append(bound)
            if len(chosen_rows) != size + 1:
                continue
            solution = solve_unique(chosen_rows, chosen_rhs, size + 1)
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
    return tight, tuple(result)


def lift(cx, cover, x, z):
    constraints = {row: csum(x, row) for row in cx}
    constraints.update({row: csum(z, row) for row in cover})
    return selector(constraints, "min"), selector(constraints, "max")


def positive(q):
    return max(F(0), q)


def stringify(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [stringify(item) for item in value]
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, dict):
        return {str(key): stringify(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values, witnesses = lower_envelope(DEFINING)
    x, z = selector(DEFINING, "min"), selector(DEFINING, "max")
    if (x, z) != (X, Z):
        raise AssertionError((x, z))
    if any(values[1 << i] or witnesses[1 << i][i] for i in range(N)):
        raise AssertionError("singleton witness failure")
    xtight = tuple(mask for mask in range(1, FULL) if csum(x, mask) == values[mask])
    ztight, covers = cover_census(values, z)
    if xtight != (19, 43) or ztight != (3, 19, 35, 43, 55):
        raise AssertionError((xtight, ztight))
    complete = []
    subset_selectors = []
    for size in range(3):
        for cx in itertools.combinations(xtight, size):
            lx = selector({row: csum(x, row) for row in cx}, "min")
            subset_selectors.append((cx, lx))
            if lx == x:
                complete.append(cx)
    if complete != [(19, 43)]:
        raise AssertionError((complete, subset_selectors))
    if covers != (((3,), (F(1, 2),), F(0), (F(1, 2), F(1, 2))),):
        raise AssertionError(covers)
    lx, lz = lift((19, 43), (3,), x, z)
    if lx != x or lz != ZP:
        raise AssertionError((lx, lz))

    d = (F(0), F(0), F(0), F(1), F(0), F(-1))
    negative = tuple(mask for mask in ztight if csum(d, mask) < 0)
    if negative != (35, 55) or csum(d, 3) or csum(d, 19) or csum(d, 43):
        raise AssertionError((negative, d))

    a = tuple(min(p, q) for p, q in zip(x, z))
    b = tuple(max(p, q) for p, q in zip(x, z))
    overlap = sum(a, F(0))
    residual = (2, 3, 4, 5)
    BH = sum(min(x[i], F(6)) for i in (0, 1)) + sum(
        min(xi, zi) for xi, zi in zip(
            sorted((x[i] for i in residual)),
            sorted((z[i] for i in residual), reverse=True),
        )
    )
    inside, outside = (3, 5), (2, 4)
    cut = sum((positive(high - low) for high, low in zip(
        sorted((a[i] for i in inside), reverse=True),
        sorted(b[i] for i in outside),
    )), F(0))
    mixed = F(0)
    mixed_matching = ()
    for size in range(1, min(len(inside), len(outside)) + 1):
        for left in itertools.combinations(inside, size):
            for right in itertools.permutations(outside, size):
                matching = tuple(zip(left, right))
                value = sum((max(
                    positive(a[i] - b[j]), positive(a[j] - b[i])
                ) for i, j in matching), F(0))
                if value > mixed:
                    mixed, mixed_matching = value, matching
    if (overlap, BH, cut, mixed) != (
        F(117, 5), F(16), F(37, 5), F(37, 5)
    ):
        raise AssertionError((overlap, BH, cut, mixed))

    # Every C,Q pair has an empty Boolean cell, so no square exists.
    empty_cells = {}
    for C in (19, 43):
        for Q in (35, 55):
            cells = {
                f"{ec}{eq}": tuple(i for i in residual if (
                    (C >> i) & 1, (Q >> i) & 1
                ) == (ec, eq))
                for ec in (0, 1) for eq in (0, 1)
            }
            if all(cells.values()):
                raise AssertionError((C, Q, cells))
            empty_cells[f"{C},{Q}"] = cells

    payload = {
        "claim": "independent exact replay of PXC127",
        "all_coalition_values": values,
        "singleton_minimizers": tuple(witnesses[1 << i] for i in range(N)),
        "selectors": {"Lmin": x, "Lmax": z, "pair_lift_Lmax": lz},
        "tight_rows": {"x": xtight, "z": ztight},
        "complete_cx_subset_replay": subset_selectors,
        "extreme_top_covers": covers,
        "common_direction": d,
        "negative_blockers": negative,
        "boolean_cell_tables": empty_cells,
        "maximum_boolean_square": F(0),
        "overlap": overlap,
        "B_H": BH,
        "D_H": F(50, 3) - BH,
        "common_row_cut_price": cut,
        "maximum_mixed_cut_price": mixed,
        "maximum_mixed_cut_matching": mixed_matching,
        "independence": (
            "standalone Fraction active-set selector and Gaussian cover replay; "
            "no project or primary PXC127 implementation"
        ),
    }
    rendered = json.dumps(stringify(payload), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
