#!/usr/bin/env python3
"""Exact arithmetic guard for the human starved-(4,2)x(2,4) barrier."""

from __future__ import annotations

import json

import z3


def unsat(*constraints):
    solver = z3.Solver()
    solver.add(*constraints)
    assert solver.check() == z3.unsat


def main():
    u, v, w, c = z3.Reals("u v w c")
    base = (
        u >= 0,
        v > 0,
        w >= 0,
        c >= 0,
        v == u + w,
        6 * c + 8 * v - 4 * w == 1,
    )

    # Strict failure forces the rich-side loss above half the positive gap.
    unsat(*base, v > z3.RealVal("1/6"), 2 * w <= v)

    # Under that strict inequality, every z-minus-x nonnegative coalition has
    # at least as many positive (a,d) cells as negative (b,d) cells.
    checked_count_types = []
    for poor_low in range(3):
        for poor_high in range(3):
            for rich_high in range(3):
                if poor_low + poor_high + rich_high == 0:
                    continue
                delta = poor_high * v - poor_low * u - rich_high * w
                direction = poor_high - rich_high
                if direction < 0:
                    unsat(*base, 2 * w > v, delta >= 0)
                    checked_count_types.append(
                        (poor_low, poor_high, rich_high)
                    )

    # At equality, the absence of the improving direction fixes every gap.
    unsat(*base, v == z3.RealVal("1/6"), 2 * w <= v, w != z3.RealVal("1/12"))
    unsat(*base, v == z3.RealVal("1/6"), 2 * w <= v, u != z3.RealVal("1/12"))
    unsat(*base, v == z3.RealVal("1/6"), 2 * w <= v, c != 0)

    print(
        json.dumps(
            {
                "status": "PASS",
                "scope": (
                    "exact arithmetic guard for the displayed human direction proof; "
                    "not a substitute for that proof"
                ),
                "checked_negative_direction_count_types": checked_count_types,
                "equality_gaps": {"u": "1/12", "v": "1/6", "w": "1/12", "c": "0"},
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
