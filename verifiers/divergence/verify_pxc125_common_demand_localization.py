#!/usr/bin/env python3
"""Exact audit of the PXC125 maximal common-ladder price theorem.

The human proof is a layer-count argument.  This verifier checks its exact
algebra on a broad rational grid and independently replays representative
lower-envelope games outside the narrower PXC122 chamber.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIV = ROOT / "verifiers" / "divergence"
ARCHIVE = DIV / "search_archive"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(ARCHIVE)]

from audit_spectral_label_currency import opposite_residual  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    covers,
    lift,
    selector_pair,
    tight_rows,
)


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


def coefficient(n: int) -> F:
    return F(n, (n * n) // 4)


def profile(t: int, A: F, B: F, K0: F, M: F):
    C = A + (t + 1) * B - t * K0
    T = 2 * M + 3 * A + (t + 1) * B
    x = (M + A / 2, M + A / 2, A, B, A, *(B for _ in range(t)))
    z = (M, M, F(0), C, 2 * A, *(K0 for _ in range(t)))
    assert 0 < A < B
    assert B + A / (t + 1) < K0 < B + 2 * A / t
    assert M > max(K0, 2 * A)
    assert B - A < C < K0 < M
    return C, T, x, z


def layer_formula(t: int, A: F, B: F, C: F) -> F:
    if t == 1:
        return (
            2 * A
            + min(A, C)
            + max(F(0), min(B, 2 * A, C) - A)
        )
    return (
        (t + 1) * A
        + min(A, C)
        + (t - 2) * (B - A)
        + max(F(0), min(B, 2 * A) - A)
        + max(F(0), min(B, C) - A)
    )


def declared_price(t: int, A: F, B: F, C: F) -> F:
    if t == 1:
        return B - A + max(F(0), min(B, C) - 2 * A)
    return B - A + max(F(0), B - 2 * A)


def algebra_row(t: int, A: F, B: F, K0: F, M: F, label: str):
    C, T, x, z = profile(t, A, B, K0, M)
    residual = opposite_residual(x, z, {0, 1})
    formula = layer_formula(t, A, B, C)
    assert residual == formula
    BH = 2 * M + residual
    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    price = declared_price(t, A, B, C)
    demand = max(F(0), coefficient(t + 5) * T - BH)
    assert price <= overlap - BH
    assert BH + price >= coefficient(t + 5) * T
    assert overlap >= coefficient(t + 5) * T
    if t >= 2:
        assert demand == 0
    elif A >= B / 3:
        assert demand == 0
    elif demand > 0:
        assert B > 3 * A
        assert min(B, C) > 2 * A
        assert price == (B - A) + (min(B, C) - 2 * A)
    return {
        "label": label,
        "t": t,
        "A": str(A),
        "B": str(B),
        "K0": str(K0),
        "C": str(C),
        "M": str(M),
        "T": str(T),
        "B_H": str(BH),
        "demand": str(demand),
        "declared_price": str(price),
        "overlap_margin": str(overlap - coefficient(t + 5) * T),
    }


def exact_game_row(t: int, A: F, B: F, K0: F, M: F, label: str):
    C, T, expected_x, expected_z = profile(t, A, B, K0, M)
    n = t + 5
    ks = tuple(range(5, n))
    rows = {
        "rh": mask(0, 1),
        "a": mask(2),
        "rha": mask(0, 1, 2),
        "rhj": mask(0, 1, 4),
        "rhaj": mask(0, 1, 2, 4),
        "rhaK": mask(0, 1, 2, *ks),
        "rhbK": mask(0, 1, 3, *ks),
        "rhabK": mask(0, 1, 2, 3, *ks),
    }
    defining = {
        rows["rh"]: 2 * M,
        rows["rhj"]: 2 * M + 2 * A,
        rows["rhaK"]: 2 * M + t * K0,
        rows["rhbK"]: 2 * M + A + (t + 1) * B,
    }
    values, x, z = selector_pair(defining, n, T)
    assert x == expected_x and z == expected_z
    assert all(values[1 << i] == 0 for i in range(n))
    cx = tuple(sorted((rows["rhj"], rows["rhbK"])))
    assert tight_rows(values, x) == cx
    expected_menu = tuple(sorted(rows[name] for name in (
        "rh", "a", "rha", "rhj", "rhaj", "rhaK", "rhbK", "rhabK"
    )))
    assert tight_rows(values, z) == expected_menu
    extreme = covers(values, z)
    assert len(extreme) == 5
    L = B + A / (t + 1)
    reduced = (M, M, F(0), L, 2 * A, *(L for _ in range(t)))
    outcomes = []
    for cover_rows, (weights, eta, alpha) in extreme:
        faithful, lx, lz, singleton = lift(
            values, x, z, cx, cover_rows, diagnose_singletons=True
        )
        assert not faithful and lx == x and lz == reduced and singleton
        outcomes.append({
            "rows": list(cover_rows),
            "weights": list(map(str, weights)),
            "eta": str(eta),
            "alpha": list(map(str, alpha)),
        })
    blocker = rows["rhaK"]
    assert all(blocker not in cover_rows for cover_rows, _ in extreme)
    return {
        "label": label,
        "parameters": {"t": t, "A": str(A), "B": str(B),
                       "K0": str(K0), "C": str(C), "M": str(M)},
        "x": list(map(str, x)),
        "z": list(map(str, z)),
        "reduced_z": list(map(str, reduced)),
        "complete_Cx": list(cx),
        "forced_zero_blocker": blocker,
        "covers": outcomes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    grid = []
    for t in range(1, 17):
        for A in (F(1, 5), F(1, 3), F(2, 5), F(3, 5), F(4, 5)):
            B = F(1)
            low = B + A / (t + 1)
            high = B + 2 * A / t
            for q in (F(1, 5), F(1, 2), F(4, 5)):
                K0 = low + q * (high - low)
                M = max(K0, 2 * A) + F(1, 7)
                grid.append(algebra_row(
                    t, A, B, K0, M,
                    f"grid-t{t}-A{A}-q{q}",
                ))

    exact = [
        exact_game_row(1, F(1), F(5), F(29, 5), F(6),
                       "positive-demand-anchor"),
        exact_game_row(1, F(2), F(5), F(36, 5), F(8),
                       "outside-old-B>3A-chamber"),
        exact_game_row(2, F(2), F(5), F(32, 5), F(8),
                       "seven-player-broad-chamber"),
        exact_game_row(3, F(2), F(5), F(61, 10), F(8),
                       "eight-player-broad-chamber"),
    ]
    positive = [row for row in grid if F(row["demand"]) > 0]
    assert positive and all(row["t"] == 1 and F(row["B"]) > 3 * F(row["A"])
                            for row in positive)
    payload = {
        "claim": (
            "PXC125 maximal common-ladder demand localization: t>=2 and "
            "t=1,A>=B/3 are spectrally closed; every remaining demand is "
            "paid by one predeclared pair of disjoint rank rectangles"
        ),
        "symbolic": {
            "maximal_chamber": (
                "0<A<B, B+A/(t+1)<K0<B+2A/t, "
                "M>max(K0,2A), C=A+(t+1)B-tK0"
            ),
            "t=1_price": "(B-A)+(min(B,C)-2A)_+",
            "t>=2_price": "(B-A)+(B-2A)_+",
            "demand_localization": "D_H>0 implies t=1 and B>3A",
        },
        "grid_instances": len(grid),
        "positive_demand_instances": len(positive),
        "exact_games": exact,
        "scope": (
            "conventional layer-count theorem for the full natural affine "
            "common-obstruction chamber; still not the unrestricted PXC114 "
            "common branch"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
