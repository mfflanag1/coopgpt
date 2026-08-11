#!/usr/bin/env python3
"""Exact n=7 counterexamples to three progressively label-aware relaxations.

Each game is the lower envelope of two common-total allocations and is exact.
Exact rational staged incidence LPs independently certify the displayed Lmin
and Lmax points.  The counterexamples refute only intermediate rearrangement
bounds; their true hybrid overlaps remain far above the conjectured floor.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_sign_coherent_staged_lifts import audit_pair  # noqa: E402
from audit_spectral_threshold_oracle import spectral_radius, subset_bound  # noqa: E402


CASES = (
    {
        "name": "optimized_label_free_spectral_failure",
        "g": (0, 0, 3, 17, 0, 9, 1),
        "h": (14, 4, 0, 0, 12, 0, 0),
        "x": (F(25, 4), F(3, 2), F(3, 2), F(37, 4), F(21, 4), F(21, 4), F(1)),
        "z": (F(64, 9), F(32, 9), F(2, 9), F(64, 9), F(19, 3), F(49, 9), F(2, 9)),
        "failed_relaxation": "B_spec >= sharp floor",
    },
    {
        "name": "actual_top_fixed_failure",
        "g": (18, 17, 0, 0, 1, 0, 0),
        "h": (0, 0, 24, 10, 0, 1, 1),
        "x": (F(9), F(8), F(19, 2), F(8), F(1, 2), F(1, 2), F(1, 2)),
        "z": (F(9), F(17, 2), F(9), F(17, 2), F(1), F(0), F(0)),
        "failed_relaxation": "actual Lmax top fixed, lower labels freely rearranged",
    },
    {
        "name": "top_and_bottom_fixed_failure",
        "g": (10, 1, 0, 1, 21, 0, 9),
        "h": (0, 0, 1, 0, 0, 41, 0),
        "x": (F(19, 2), F(1, 2), F(1, 2), F(1, 2), F(45, 4), F(45, 4), F(17, 2)),
        "z": (F(10), F(1), F(0), F(1), F(21, 2), F(21, 2), F(9)),
        "failed_relaxation": "actual Lmax top and bottom fixed, middle labels freely rearranged",
    },
)


def extreme_fixed_bound(x: tuple[F, ...], z: tuple[F, ...]) -> F:
    maximum = max(z)
    minimum = min(z)
    fixed = {i for i, q in enumerate(z) if q in (minimum, maximum)}
    exact = sum((min(x[i], z[i]) for i in fixed), F(0))
    remaining_x = sorted(x[i] for i in range(len(x)) if i not in fixed)
    remaining_z = sorted((z[i] for i in range(len(z)) if i not in fixed), reverse=True)
    return exact + sum((min(a, b) for a, b in zip(remaining_x, remaining_z)), F(0))


def audit_case(raw: dict) -> dict:
    g = tuple(map(F, raw["g"]))
    h = tuple(map(F, raw["h"]))
    x = tuple(raw["x"])
    z = tuple(raw["z"])
    n = len(x)
    full = (1 << n) - 1
    values = tuple(
        min(coalition_sum(g, mask), coalition_sum(h, mask))
        for mask in range(1 << n)
    )
    assert sum(g, F(0)) == sum(h, F(0)) == values[full]
    assert all(values[1 << i] == 0 for i in range(n))
    for generator in (g, h):
        assert all(coalition_sum(generator, mask) >= values[mask] for mask in range(1, full))
    for point in (x, z):
        assert sum(point, F(0)) == values[full]
        assert all(coalition_sum(point, mask) >= values[mask] for mask in range(1, full))
    checked, failures = audit_pair(values, x, z)
    assert checked == 2 * n and not failures

    threshold = F(4 * n, n * n - (n % 2)) * values[full]
    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    assert overlap > threshold
    top = tuple(i for i, q in enumerate(z) if q == max(z))
    actual_top_bound = subset_bound(x, z, top)
    extreme_bound = extreme_fixed_bound(x, z)

    radius = spectral_radius(values, x, z)
    subsets = tuple(itertools.combinations(range(n), len(top)))
    eligible = tuple(
        chosen
        for chosen in subsets
        if sum((x[i] - min(x) for i in chosen), F(0)) >= radius["radius"]
    )
    optimized_spectral = min(subset_bound(x, z, chosen) for chosen in eligible)

    if raw["name"] == "optimized_label_free_spectral_failure":
        assert radius["radius"] == F(237, 20)
        assert optimized_spectral == F(605, 36) < threshold == F(35, 2)
        assert actual_top_bound == F(641, 36) > threshold
    elif raw["name"] == "actual_top_fixed_failure":
        assert actual_top_bound == F(39, 2) < threshold == F(21)
        assert extreme_bound > threshold
    else:
        assert extreme_bound == F(24) < threshold == F(49, 2)

    return {
        "name": raw["name"],
        "failed_relaxation": raw["failed_relaxation"],
        "generators": [[str(q) for q in g], [str(q) for q in h]],
        "total": str(values[full]),
        "lmin": [str(q) for q in x],
        "lmax": [str(q) for q in z],
        "selection_check": "14 exact rational staged incidence LP certificates",
        "spectral_radius": str(radius["radius"]),
        "optimized_label_free_bound": str(optimized_spectral),
        "actual_top_fixed_bound": str(actual_top_bound),
        "top_and_bottom_fixed_bound": str(extreme_bound),
        "sharp_floor": str(threshold),
        "true_overlap": str(overlap),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact rational hierarchy of label-relaxation counterexamples",
        "cases": [audit_case(case) for case in CASES],
        "scope": (
            "refutes partial relabeling proof bridges only; the all-n hybrid-overlap "
            "conjecture survives with large slack in every case"
        ),
        "evidence": (
            "exact lower-envelope exactness, core membership, and staged rational "
            "certificate LPs; sparse hand identities remain a possible hardening step"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
