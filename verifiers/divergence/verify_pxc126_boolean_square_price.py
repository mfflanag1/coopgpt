#!/usr/bin/env python3
"""Exact primary audit of the PXC126 Boolean-square subpacking.

The proof in the paper is the threshold-counting argument.  This program
checks its arithmetic on deterministic rational profiles, checks the exact
PXC125 specialization, and retains a fail-open control showing that vertex
disjointness is load-bearing.  It is not used as a substitute for the
dimension-free proof.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def positive(q: F) -> F:
    return max(F(0), q)


def label_currency(a: tuple[F, ...], b: tuple[F, ...]) -> F:
    """Canonical layer currency, equal to O-B_H on the residual block."""
    return sum(
        (positive(high - low) for high, low in zip(
            sorted(a, reverse=True), sorted(b)
        )),
        F(0),
    )


def threshold_currency(a: tuple[F, ...], b: tuple[F, ...]) -> F:
    cuts = sorted(set((F(0), *a, *b)))
    total = F(0)
    for lo, hi in zip(cuts, cuts[1:]):
        if hi == lo:
            continue
        probe = hi
        high_high = sum(value >= probe for value in a)
        low_low = sum(value < probe for value in b)
        total += (hi - lo) * min(high_high, low_low)
    return total


def square(a: tuple[F, ...], b: tuple[F, ...], u: tuple[int, int, int, int]) -> F:
    u11, u01, u10, u00 = u
    if len(set(u)) != 4:
        raise ValueError("PXC126 requires four distinct representatives")
    return positive(a[u11] - b[u01]) + positive(a[u10] - b[u00])


def square_optimum(a, b, cell_of):
    cells = {
        key: tuple(i for i, cell in enumerate(cell_of) if cell == key)
        for key in ((1, 1), (0, 1), (1, 0), (0, 0))
    }
    if any(not cell for cell in cells.values()):
        return None
    formula = positive(max(a[i] for i in cells[1, 1]) - min(
        b[i] for i in cells[0, 1]
    )) + positive(max(a[i] for i in cells[1, 0]) - min(
        b[i] for i in cells[0, 0]
    ))
    brute = max(
        square(a, b, (u11, u01, u10, u00))
        for u11 in cells[1, 1]
        for u01 in cells[0, 1]
        for u10 in cells[1, 0]
        for u00 in cells[0, 0]
    )
    if formula != brute:
        raise AssertionError((formula, brute, cells))
    return formula


def pxc125(t: int, A: F, B: F, K0: F, M: F):
    C = A + (t + 1) * B - t * K0
    if not (
        0 < A < B
        and B + A / (t + 1) < K0 < B + 2 * A / t
        and M > max(K0, 2 * A)
    ):
        raise AssertionError(("outside PXC125 chamber", t, A, B, K0, M))
    x = (M + A / 2, M + A / 2, A, B, A, *(B for _ in range(t)))
    z = (M, M, F(0), C, 2 * A, *(K0 for _ in range(t)))
    # Residual order is a,b,j,K.  Relative to C=rhbK and Q=rhaK the
    # representatives are K in V11, a in V01, b in V10, j in V00.  This
    # is exactly PXC125's charged price when t=1, the only positive-demand
    # case.  For t>=2 it is a smaller valid subpacking; PXC125 instead uses
    # two distinct K coordinates, but its spectral demand is already zero.
    residual_x = x[2:]
    residual_z = z[2:]
    aa = tuple(min(p, q) for p, q in zip(residual_x, residual_z))
    bb = tuple(max(p, q) for p, q in zip(residual_x, residual_z))
    u = (3, 0, 1, 2)
    actual = square(aa, bb, u)
    expected = (B - A) + positive(min(B, C) - 2 * A)
    if actual != expected or actual > label_currency(aa, bb):
        raise AssertionError((t, A, B, K0, M, actual, expected))
    return {
        "t": t,
        "A": A,
        "B": B,
        "K0": K0,
        "M": M,
        "C": C,
        "square": actual,
        "label_currency": label_currency(aa, bb),
    }


def stringify(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [stringify(item) for item in value]
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    profiles = []
    closed_form_checks = 0
    for seed in range(1, 97):
        a = tuple(F((seed * (i + 3) + i * i) % 17, 3 + (i % 3)) for i in range(7))
        gaps = tuple(F((seed + 2 * i) % 11, 4 + (i % 2)) for i in range(7))
        b = tuple(p + q for p, q in zip(a, gaps))
        u = tuple((seed + offset) % 7 for offset in (0, 1, 3, 5))
        if len(set(u)) != 4:
            raise AssertionError((seed, u))
        canonical = label_currency(a, b)
        layered = threshold_currency(a, b)
        paid = square(a, b, u)
        if canonical != layered or paid > canonical:
            raise AssertionError((seed, canonical, layered, paid))
        pattern = ((1, 1), (0, 1), (1, 0), (0, 0))
        cells = tuple(pattern[(i + seed) % 4] for i in range(7))
        optimum = square_optimum(a, b, cells)
        if optimum is None or optimum > canonical:
            raise AssertionError((seed, cells, optimum, canonical))
        closed_form_checks += 1
        profiles.append({"seed": seed, "square": paid, "currency": canonical})

    anchors = [
        pxc125(1, F(1), F(5), F(29, 5), F(6)),
        pxc125(1, F(2), F(5), F(36, 5), F(8)),
        pxc125(2, F(1), F(3), F(15, 4), F(5)),
        pxc125(3, F(1), F(4), F(9, 2), F(6)),
    ]

    # If the same high and low endpoints are charged twice, the asserted
    # subpacking bound fails.  PXC126 forbids precisely this reuse.
    a = (F(5), F(0))
    b = (F(5), F(1))
    currency = label_currency(a, b)
    duplicated = 2 * positive(a[0] - b[1])
    if not duplicated > currency:
        raise AssertionError((duplicated, currency))

    payload = {
        "claim": "exact arithmetic audit of the PXC126 Boolean-square label subpacking",
        "deterministic_rational_profiles": len(profiles),
        "closed_form_optimum_checks": closed_form_checks,
        "profile_digest_data": profiles,
        "pxc125_boolean_square_specializations": anchors,
        "fail_open": {
            "drop_vertex_disjointness": {
                "duplicated_price": duplicated,
                "label_currency": currency,
                "violates_bound": duplicated > currency,
            }
        },
        "scope": (
            "the conventional threshold proof is dimension-free; this exact "
            "audit checks arithmetic and the PXC125 identification, not the open "
            "PXC126 square-extraction implication"
        ),
    }
    rendered = json.dumps(stringify(payload), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
