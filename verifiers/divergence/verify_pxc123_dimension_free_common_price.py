#!/usr/bin/env python3
"""Primary exact-rational audit of the dimension-free PXC123 typed chamber.

The conventional proof is symbolic.  This script replays exact lower-envelope
selectors, tight menus, complete-Cx uniqueness, every normalized extreme top
cover, reduced selectors, and the price identities for labelled instances
with one through four K-block players.
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

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    covers,
    lift,
    selector_pair,
    tight_rows,
)


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


def typed_rows(t: int) -> dict[str, int]:
    ks = tuple(range(5, 5 + t))
    return {
        "rh": mask(0, 1),
        "a": mask(2),
        "rha": mask(0, 1, 2),
        "rhj": mask(0, 1, 4),
        "rhaj": mask(0, 1, 2, 4),
        "rhaK": mask(0, 1, 2, *ks),
        "rhbK": mask(0, 1, 3, *ks),
        "rhabK": mask(0, 1, 2, 3, *ks),
    }


def point(t: int) -> tuple[F, F, F, F]:
    A, B = F(1), F(5)
    K0 = B + (F(1, t + 1) + F(2, t)) / 2
    M = K0 + F(1, 2)
    return A, B, K0, M


def coefficient(n: int) -> F:
    return F(n, (n * n) // 4)


def audit(t: int, A: F, B: F, K0: F, M: F, label: str) -> dict[str, object]:
    n = t + 5
    C = A + (t + 1) * B - t * K0
    T = 2 * M + 3 * A + (t + 1) * B
    assert 0 < A and 3 * A < B
    assert B + A / (t + 1) < K0 < B + 2 * A / t
    assert K0 < M
    assert 2 * A < B and B - A < C < K0 < M

    rows = typed_rows(t)
    defining = {
        rows["rh"]: 2 * M,
        rows["rhj"]: 2 * M + 2 * A,
        rows["rhaK"]: 2 * M + t * K0,
        rows["rhbK"]: 2 * M + A + (t + 1) * B,
    }
    values, x, z = selector_pair(defining, n, T)
    expected_x = (M + A / 2, M + A / 2, A, B, A, *(B for _ in range(t)))
    expected_z = (M, M, F(0), C, 2 * A, *(K0 for _ in range(t)))
    assert x == expected_x and z == expected_z
    assert all(values[1 << i] == 0 for i in range(n))

    cx = (rows["rhj"], rows["rhbK"])
    zmenu = tuple(rows[name] for name in (
        "rh", "a", "rha", "rhj", "rhaj", "rhaK", "rhbK", "rhabK"
    ))
    assert tight_rows(values, x) == tuple(sorted(cx))
    assert tight_rows(values, z) == tuple(sorted(zmenu))
    cx_subsets = []
    for size in range(len(cx) + 1):
        for chosen in itertools.combinations(cx, size):
            retained = {row: values[row] for row in chosen}
            _retained_values, retained_x, _retained_z = selector_pair(retained, n, T)
            assert (retained_x == x) == (chosen == cx)
            cx_subsets.append({"rows": list(chosen), "lmin": list(map(str, retained_x))})

    expected_covers = {
        (rows["rh"],),
        tuple(sorted((rows["rhj"], rows["rhabK"]))),
        tuple(sorted((rows["rhaj"], rows["rhbK"]))),
        tuple(sorted((rows["a"], rows["rhj"], rows["rhbK"]))),
        tuple(sorted((rows["rha"], rows["rhj"], rows["rhbK"]))),
    }
    extreme = covers(values, z)
    assert {cover_rows for cover_rows, _ in extreme} == expected_covers

    L = B + A / (t + 1)
    reduced = (M, M, F(0), L, 2 * A, *(L for _ in range(t)))
    cover_payload = []
    for cover_rows, (weights, eta, alpha) in extreme:
        faithful, lx, lz, singleton = lift(
            values, x, z, cx, cover_rows, diagnose_singletons=True
        )
        assert not faithful and lx == x and lz == reduced and singleton
        cover_payload.append({
            "rows": list(cover_rows),
            "weights": list(map(str, weights)),
            "eta": str(eta),
            "alpha": list(map(str, alpha)),
        })

    delta = K0 - L
    direction = (F(0), F(0), F(0), t * delta, F(0), *(-delta for _ in range(t)))
    assert delta > 0
    assert tuple(reduced[i] - z[i] for i in range(n)) == direction
    union = set().union(*(set(cover_rows) for cover_rows, _ in extreme))
    csum = lambda q, S: sum((q[i] for i in range(n) if S >> i & 1), F(0))
    assert all(csum(direction, S) == 0 for S in (*cx, *sorted(union)))
    assert csum(direction, rows["rhaK"]) == -t * delta < 0

    beta = min(B, C)
    if t == 1:
        BH = 2 * M + 4 * A
        overlap = 2 * M + A + B + beta
        rectangles = (B - A, beta - 2 * A)
    else:
        BH = 2 * M + 4 * A + (t - 2) * B + beta
        overlap = 2 * M + A + t * B + beta
        rectangles = (B - A, B - 2 * A)
    price = sum(rectangles, F(0))
    target = coefficient(n) * T
    demand = max(F(0), target - BH)
    assert overlap - BH == price > 0
    assert price >= demand and overlap >= target
    if t == 1:
        raw_demand = F(2, 3) * (2 * B - M - 3 * A)
        assert demand == max(F(0), raw_demand)
        if demand > 0:
            assert price - demand == (2 * M + 3 * beta - B - 3 * A) / 3
            assert price - demand > (4 * B - 6 * A) / 3 > 0
    elif t == 2:
        assert 12 * BH - 7 * T == 10 * M + 27 * A + 12 * beta - 21 * B
        assert 12 * BH - 7 * T > B + 15 * A > 0
        assert demand == 0
    else:
        assert 2 * BH - T == 2 * M + 5 * A + (t - 5) * B + 2 * beta
        assert 2 * BH - T > (t - 1) * B + 3 * A > 0
        assert coefficient(n) <= F(1, 2) and demand == 0

    return {
        "label": label,
        "t": t,
        "n": n,
        "parameters": {"A": str(A), "B": str(B), "K0": str(K0),
                       "M": str(M), "C": str(C), "T": str(T)},
        "x": list(map(str, x)),
        "z": list(map(str, z)),
        "reduced_z": list(map(str, reduced)),
        "B_H": str(BH),
        "target": str(target),
        "demand": str(demand),
        "rectangle_prices": list(map(str, rectangles)),
        "rectangle_price": str(price),
        "complete_Cx_subset_exhaustion": cx_subsets,
        "covers": cover_payload,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    points = [
        (1, F(1, 2), F(9, 4), F(3), F(6), "PXC116-C-below-B"),
        (1, F(1), F(5), F(29, 5), F(6), "PXC122-positive-demand-C-above-B"),
        *((t, *point(t), f"symmetric-block-t={t}") for t in range(2, 5)),
    ]
    audited = [audit(*entry) for entry in points]
    payload = {
        "claim": "PXC123 dimension-free forced-zero common-price chamber",
        "symbolic": {
            "n": "t+5",
            "T": "2M+3A+(t+1)B",
            "beta": "min(B,C)",
            "t=1": (
                "B_H=2M+4A; P_C=(B-A)+(beta-2A); "
                "if D_H>0 then P_C-D_H=(2M+3beta-B-3A)/3>0"
            ),
            "t=2": (
                "B_H=2M+4A+beta; "
                "12B_H-7T=10M+27A+12beta-21B>B+15A"
            ),
            "t>=3": (
                "B_H=2M+4A+(t-2)B+beta; "
                "2B_H-T>(t-1)B+3A and c_n<=1/2"
            ),
            "explicit_price_t>=2": "(B-A)+(B-2A)=2B-3A",
        },
        "audited_instances": audited,
        "scope": (
            "exact labelled replays through n=9 plus conventional all-t "
            "proof; an all-dimensional PXC114-common family, not the full branch"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
