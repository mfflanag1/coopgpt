#!/usr/bin/env python3
"""Exact PXC114 classification of the named spectral-deficit controls.

This is a discovery/audit bridge, not evidence for the all-n overlap theorem.
It answers a narrower question needed before attempting a mechanism-price
lemma: do the existing controls on which the sharpened spectral bound misses
the target actually enter the common-direction or reciprocal-cover branch?

The game values are reconstructed directly from the two displayed lower-
envelope generators.  Qualifying extreme top covers are exhaustively
enumerated from the full proper z-tight menu by exact rational elimination;
the invariant PXC108/PXC114 graph is then recomputed from exact tangent LPs.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DIV = ROOT / "verifiers" / "divergence"
sys.path[:0] = [str(ROOT / "src"), str(DIV)]

from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_pxc101_forced_zero_family_independent import unique_solution  # noqa: E402
from verify_pxc108_invariant_cover_blocker_circuits import recognize  # noqa: E402


NAMES = {
    "optimized_label_free_spectral_failure",
    "actual_top_fixed_failure",
    "top_and_bottom_fixed_failure",
}


def csum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def lower_envelope(g, h):
    n = len(g)
    return tuple(min(csum(g, mask), csum(h, mask)) for mask in range(1 << n))


def cover_census(values, z, top):
    n = len(z)
    full = (1 << n) - 1
    outsiders = tuple(i for i in range(n) if i not in top)
    tight = tuple(mask for mask in range(1, full) if csum(z, mask) == values[mask])
    found = []
    # An extreme normalized cover has at most n-2 positive coalition rows in
    # the two-top cell.  All three named controls have exactly two top players.
    if len(top) != 2:
        raise AssertionError(("unexpected top size", top))
    for size in range(1, n - 1):
        for support in itertools.combinations(tight, size):
            matrix, rhs = [], []
            for i in outsiders:
                matrix.append([
                    *(F((row >> i) & 1) for row in support),
                    F(-1),
                ])
                rhs.append(F(0))
            matrix.append([
                *(F(sum((row >> i) & 1 for i in top)) for row in support),
                F(-len(top)),
            ])
            rhs.append(F(1))
            solution = unique_solution(matrix, rhs, size + 1)
            if solution is None:
                continue
            weights, eta = tuple(solution[:-1]), solution[-1]
            if min(weights) <= 0 or eta < 0:
                continue
            loads = tuple(
                sum((weight for row, weight in zip(support, weights)
                     if row >> i & 1), F(0))
                for i in range(n)
            )
            alpha = tuple(loads[i] - eta for i in top)
            if min(alpha) <= 0 or sum(alpha, F(0)) != 1:
                continue
            found.append({
                "rows": support,
                "weights": weights,
                "eta": eta,
                "alpha": alpha,
            })
    return tight, tuple(found)


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
    parser.add_argument(
        "--case",
        action="append",
        choices=sorted(NAMES),
        help="restrict the exact audit to one or more named controls",
    )
    args = parser.parse_args()

    currency = json.loads((DIV / "spectral_label_currency_audit.json").read_text())
    currency_by_name = {case["name"]: case for case in currency["cases"]}
    results = []
    for case in CASES:
        if case["name"] not in NAMES:
            continue
        if args.case and case["name"] not in args.case:
            continue
        g, h = tuple(map(F, case["g"])), tuple(map(F, case["h"]))
        x, z = tuple(case["x"]), tuple(case["z"])
        values = lower_envelope(g, h)
        top_value = max(z)
        top = tuple(i for i, value in enumerate(z) if value == top_value)
        tight, covers = cover_census(values, z, top)
        instance = {
            "label": case["name"],
            "x": x,
            "z": z,
            "top": top,
            "cx": tuple(case["support_x"]),
            "menu": tight,
            "covers": covers,
        }
        verdict = recognize(instance)
        cur = currency_by_name[case["name"]]
        results.append({
            "name": case["name"],
            "total": sum(g, F(0)),
            "x": x,
            "z": z,
            "top": top,
            "complete_cx_used": tuple(case["support_x"]),
            "proper_z_tight_menu": tight,
            "extreme_covers": covers,
            "pxc114": verdict,
            "currencies": {
                "spectral_deficit_ratio": cur["spectral_deficit_ratio"],
                "post_top_deficit_ratio": cur["post_top_deficit_ratio"],
                "top_selection_currency_ratio": cur["top_selection_currency_ratio"],
                "label_currency_ratio": cur["label_currency_ratio"],
            },
        })

    payload = {
        "claim": (
            f"exact PXC114 classification of {len(results)} named "
            "spectral-deficit controls"
        ),
        "results": results,
        "scope": (
            f"discovery bridge only: {len(results)} fixed exact games and the displayed "
            "complete Cx supports; not an all-n mechanism-price theorem"
        ),
    }
    rendered = json.dumps(stringify(payload), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
