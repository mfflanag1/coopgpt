#!/usr/bin/env python3
"""Standalone exact layer-cake audit of PXC125.

This implementation imports no project selector, cover, price, or primary
PXC125 code.  It computes the opposite residual bound from threshold counts
and checks the maximal-chamber localization and declared rectangles through
dimension 69.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def coefficient(n: int) -> F:
    return F(n, (n * n) // 4)


def opposite_by_layers(x: tuple[F, ...], z: tuple[F, ...]) -> F:
    levels = sorted({F(0), *x, *z})
    m = len(x)
    answer = F(0)
    for low, high in zip(levels, levels[1:]):
        nx = sum(value >= high for value in x)
        nz = sum(value >= high for value in z)
        answer += (high - low) * max(0, nx + nz - m)
    return answer


def row(t: int, A: F, B: F, K0: F, M: F) -> dict[str, object]:
    n = t + 5
    C = A + (t + 1) * B - t * K0
    T = 2 * M + 3 * A + (t + 1) * B
    residual_x = (A, B, A, *(B for _ in range(t)))
    residual_z = (F(0), C, 2 * A, *(K0 for _ in range(t)))
    residual = opposite_by_layers(residual_x, residual_z)
    BH = 2 * M + residual
    beta = min(B, C)
    overlap = 2 * M + A + t * B + beta
    if t == 1:
        price = B - A + max(F(0), beta - 2 * A)
        u = min(A, C)
        v = max(F(0), min(B, 2 * A, C) - A)
        s = max(F(0), beta - 2 * A)
        assert u + v + s == beta
        assert residual == 2 * A + u + v
        assert BH + price == overlap
    else:
        price = B - A + max(F(0), B - 2 * A)
        assert residual == (
            (t + 1) * A
            + min(A, C)
            + (t - 2) * (B - A)
            + max(F(0), min(B, 2 * A) - A)
            + max(F(0), min(B, C) - A)
        )
        assert BH + price <= overlap
    target = coefficient(n) * T
    demand = max(F(0), target - BH)
    assert price <= overlap - BH
    assert BH + price >= target
    if t >= 3:
        assert coefficient(n) <= F(1, 2)
        coarse = 2 * M + A + (t - 3) * B
        assert 2 * (BH + price) - T >= coarse > 0
        assert demand == 0
    elif t == 2:
        assert 12 * BH - 7 * T > 0
        assert demand == 0
    elif A >= B / 3:
        assert 3 * BH - 2 * T > 0
        assert demand == 0
    elif demand > 0:
        assert B > 3 * A and beta > 2 * A
    return {
        "t": t,
        "n": n,
        "A": str(A),
        "B": str(B),
        "K0": str(K0),
        "C": str(C),
        "M": str(M),
        "B_H": str(BH),
        "demand": str(demand),
        "price": str(price),
        "margin": str(overlap - target),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for t in range(1, 65):
        for A in (F(1, 8), F(1, 4), F(1, 3), F(1, 2), F(3, 4), F(7, 8)):
            B = F(1)
            lower = B + A / (t + 1)
            upper = B + 2 * A / t
            for q in (F(1, 11), F(1, 3), F(2, 3), F(10, 11)):
                K0 = lower + q * (upper - lower)
                M = max(K0, 2 * A) + F(1, 13)
                rows.append(row(t, A, B, K0, M))

    positive = [item for item in rows if F(item["demand"]) > 0]
    assert positive
    assert all(item["t"] == 1 and F(item["B"]) > 3 * F(item["A"])
               for item in positive)

    # Fail-open control: remove the blocker/core-comparison upper endpoint
    # K0 < B+2A/t.  Positive t=2 demand then becomes possible.
    t, A, B, K0 = 2, F(1, 10), F(1), F(31, 20)
    C = A + 3 * B - 2 * K0
    M = K0 + F(1, 10000)
    residual = opposite_by_layers((A, B, A, B, B),
                                  (F(0), C, 2 * A, K0, K0))
    T = 2 * M + 3 * A + 3 * B
    fail_open_demand = F(7, 12) * T - (2 * M + residual)
    assert C == 0 and K0 > B + A and fail_open_demand > 0

    payload = {
        "claim": "independent exact threshold-layer audit of PXC125",
        "instances": len(rows),
        "maximum_t": 64,
        "positive_demand_instances": len(positive),
        "positive_demand_localization": "all have t=1 and B>3A",
        "fail_open_without_blocker_comparison": {
            "t": t,
            "A": str(A),
            "B": str(B),
            "K0": str(K0),
            "C": str(C),
            "demand": str(fail_open_demand),
        },
        "independence": (
            "standalone Fraction threshold integration; imports no project, "
            "selector, cover, primary price, or PXC125 implementation"
        ),
        "scope": (
            "exact algebra and layer-count audit; the displayed case split is "
            "the conventional all-t proof"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
