#!/usr/bin/env python3
"""Primary exact audit of the PXC122 positive-demand common chamber."""
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
    solve_unique,
    tight_rows,
)


def mask(*players):
    return sum(1 << player for player in players)


RH = mask(0, 1)
RHJ = mask(0, 1, 4)
RHAK = mask(0, 1, 2, 5)
RHBK = mask(0, 1, 3, 5)
EXPECTED_X_TIGHT = (RHJ, RHBK)
EXPECTED_Z_TIGHT = (RH, mask(2), mask(0, 1, 2), RHJ,
                    mask(0, 1, 2, 4), RHAK, RHBK,
                    mask(0, 1, 2, 3, 5))
EXPECTED_COVERS = {
    (RH,),
    (RHJ, mask(0, 1, 2, 3, 5)),
    (mask(0, 1, 2, 4), RHBK),
    (mask(2), RHJ, RHBK),
    (mask(0, 1, 2), RHJ, RHBK),
}


def incidence(coalition):
    return tuple(F((coalition >> i) & 1) for i in range(6))


def normal_cone_menu(active_rows, active_zero_rows=()):
    """Enumerate 0/1 objectives in cone(active normals)+span(1)."""
    generators = tuple(active_rows) + tuple(active_zero_rows)
    answer = {}
    for coalition in range(64):
        target = incidence(coalition)
        for size in range(len(generators) + 1):
            found = None
            for chosen in itertools.combinations(generators, size):
                matrix = [[
                    *(incidence(row)[player] for row in chosen), F(1)
                ] for player in range(6)]
                solution = solve_unique(matrix, target, len(chosen) + 1)
                if solution is not None and all(value >= 0 for value in solution[:-1]):
                    found = (chosen, solution)
                    break
            if found is not None:
                answer[coalition] = found
                break
    return answer


def sample(A, B, K, M):
    C = A + 2 * B - K
    if not (0 < A and F(7, 2) * A < B):
        raise AssertionError("A/B chamber")
    if not (B + A / 2 < K < A + B):
        raise AssertionError("K chamber")
    if not (K < M < 2 * B - 3 * A):
        raise AssertionError("M chamber")
    T = 2 * M + 3 * A + 2 * B
    constraints = {
        RH: 2 * M,
        RHJ: 2 * M + 2 * A,
        RHAK: 2 * M + K,
        RHBK: 2 * M + A + 2 * B,
    }
    values, x, z = selector_pair(constraints, 6, T)
    expected_x = (M + A / 2, M + A / 2, A, B, A, B)
    expected_z = (M, M, F(0), C, 2 * A, K)
    assert x == expected_x and z == expected_z
    assert all(values[1 << i] == 0 for i in range(6))
    assert tight_rows(values, x) == EXPECTED_X_TIGHT
    assert tight_rows(values, z) == EXPECTED_Z_TIGHT

    extreme = covers(values, z)
    assert {rows for rows, _certificate in extreme} == EXPECTED_COVERS
    reduced = (M, M, F(0), B + A / 2, 2 * A, B + A / 2)
    cover_rows = []
    for rows, (weights, eta, alpha) in extreme:
        faithful, lx, lz, singleton = lift(
            values, x, z, EXPECTED_X_TIGHT, rows,
            diagnose_singletons=True,
        )
        assert not faithful and lx == x and lz == reduced and singleton
        cover_rows.append({
            "rows": list(rows),
            "weights": list(map(str, weights)),
            "eta": str(eta),
            "alpha": list(map(str, alpha)),
        })

    actual_top = {0, 1}
    BH = 2 * M + opposite_residual(x, z, actual_top)
    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    target = F(2, 3) * T
    demand = target - BH
    rectangles = (B - A, B - 2 * A)
    assert BH == 2 * M + 4 * A
    assert demand == F(2, 3) * (2 * B - M - 3 * A) > 0
    assert overlap == 2 * M + 2 * B + A
    assert overlap - target == F(1, 3) * (
        2 * (M - A) + 2 * (B - A) + A
    ) > 0
    assert sum(rectangles, F(0)) == overlap - BH == 2 * B - 3 * A
    assert sum(rectangles, F(0)) - demand == F(1, 3) * (
        2 * M + 2 * B - 3 * A
    ) > 0
    delta = K - B - A / 2
    assert delta > 0
    assert tuple(reduced[i] - z[i] for i in range(6)) == (
        F(0), F(0), F(0), delta, F(0), -delta
    )
    return {
        "parameters": {"A": str(A), "B": str(B), "K": str(K),
                       "M": str(M), "C": str(C), "T": str(T)},
        "x": list(map(str, x)),
        "z": list(map(str, z)),
        "reduced_z": list(map(str, reduced)),
        "B_H": str(BH),
        "target": str(target),
        "post_top_demand": str(demand),
        "overlap": str(overlap),
        "rectangle_prices": list(map(str, rectangles)),
        "covers": cover_rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    points = [
        (F(1), F(4), F(23, 5), F(24, 5)),
        (F(1), F(5), F(29, 5), F(6)),
        (F(1), F(6), F(27, 4), F(7)),
        (F(2), F(8), F(46, 5), F(48, 5)),
    ]
    audited = [sample(*point) for point in points]
    x_normal = normal_cone_menu((RHJ, RHBK))
    z_normal = normal_cone_menu((RH, RHJ, RHAK, RHBK), (mask(2),))
    assert tuple(x_normal) == (0, RHJ, RHBK, 63)
    assert tuple(z_normal) == (0, *EXPECTED_Z_TIGHT, 63)
    payload = {
        "claim": (
            "PXC122 open rational common-blocker chamber falsifies PXC120 "
            "but satisfies hybrid overlap by two explicit staged rectangles"
        ),
        "symbolic_formulas": {
            "T": "2M+3A+2B",
            "B_H": "2M+4A",
            "D_H": "2(2B-M-3A)/3 > 0",
            "overlap": "2M+2B+A",
            "overlap_slack": "[2(M-A)+2(B-A)+A]/3 > 0",
            "rectangle_currency": "(B-A)+(B-2A)=2B-3A",
        },
        "audited_points": audited,
        "parameter_independent_normal_cone_audit": {
            "x_minimizing_proper_rows": list(EXPECTED_X_TIGHT),
            "z_minimizing_proper_rows": list(EXPECTED_Z_TIGHT),
            "reason": (
                "complete enumeration of all 64 zero-one objectives in the "
                "active-normal cone plus the free efficiency normal"
            ),
        },
        "scope": (
            "exact audits of rational chamber points plus conventional "
            "parameter proof; not an all-common-branch theorem"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
