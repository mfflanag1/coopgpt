#!/usr/bin/env python3
"""Exact rank audit for sharpness of the projected staged support bound.

After quotienting efficiency and o old pinned coordinates, m=n-o remaining
unit columns become e_1,...,e_{m-1},-(1,...,1) in a quotient basis.  Their
sum is zero and every deletion is independent, giving a positive circuit of
support m=n-o.

This checks the displayed construction only; the rank proof is in the note.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def rank(columns):
    if not columns:
        return 0
    rows = [list(map(F, row)) for row in zip(*columns)]
    row = col = 0
    while row < len(rows) and col < len(rows[0]):
        pivot = next((r for r in range(row, len(rows)) if rows[r][col]), None)
        if pivot is None:
            col += 1
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        scale = rows[row][col]
        rows[row] = [value / scale for value in rows[row]]
        for r in range(len(rows)):
            if r == row or not rows[r][col]:
                continue
            factor = rows[r][col]
            rows[r] = [a - factor * b for a, b in zip(rows[r], rows[row])]
        row += 1
        col += 1
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for n in range(2, args.max_n + 1):
        for old_size in range(n - 1):
            m = n - old_size
            columns = []
            for j in range(m - 1):
                columns.append(tuple(F(int(i == j)) for i in range(m - 1)))
            columns.append(tuple(F(-1) for _ in range(m - 1)))
            assert all(sum(column[i] for column in columns) == 0 for i in range(m - 1))
            assert rank(columns) == m - 1
            deletion_ranks = []
            for omitted in range(m):
                kept = tuple(column for j, column in enumerate(columns) if j != omitted)
                deletion_ranks.append(rank(kept))
            assert deletion_ranks == [m - 1] * m
            rows.append(
                {
                    "n": n,
                    "old_size": old_size,
                    "sharp_support": m,
                    "quotient_rank": m - 1,
                }
            )
    report = {
        "status": "exact rational rank audit of the sharp unit-column circuit",
        "max_n": args.max_n,
        "cases": len(rows),
        "support_cap_n_minus_old_minus_one_rejected": True,
        "rows": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
