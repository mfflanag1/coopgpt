#!/usr/bin/env python3
"""Profile-varying falsification attack on the corrected split-top arms.

This is a design search, not a verifier.  It keeps the PXC88 Lmin point and
its three clean saturated rows, varies the two-top/two-subtop/three-outsider
Lmax profile over a rational grid, and minimally lifts sparse positive-top
cover supports.  Every retained hit is recomputed as an exact game and must
escape the top pair, PXC78, PXC87, and direct arms simultaneously.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(COOPGAMES / "src"))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

import audit_class_b_three_row_supports as base  # noqa: E402
from audit_class_b_support_alternative import coalition_minimizer  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import (  # noqa: E402
    has_direct_packet,
)
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_spectral_or_reserve import margins, selectors  # noqa: E402


def labelled_covers(
    support_size: int, symmetry_reduced: bool = False
) -> tuple[tuple[int, ...], ...]:
    compatible = tuple(
        coalition
        for coalition in range(1, (1 << base.N) - 1)
        if coalition.bit_count() >= 2
        and coalition_sum(base.X, coalition) >= coalition_sum(base.Z, coalition)
    )
    columns: dict[tuple[int, ...], list[int]] = {}
    for coalition in compatible:
        columns.setdefault(base.incidence_key(coalition), []).append(coalition)
    column_items = tuple(columns.items())
    row_covers = set()
    for indices in itertools.combinations(range(len(column_items)), support_size):
        representatives = tuple(column_items[index][1][0] for index in indices)
        if base.incidence_cover(representatives) is None:
            continue
        for rows in itertools.product(*(column_items[index][1] for index in indices)):
            rows = tuple(sorted(rows))
            cover = base.normalized_cover(rows)
            if cover is not None and min(cover[2]) > 0:
                row_covers.add(rows)
    if symmetry_reduced:
        return tuple(sorted({base.canonical_rows(rows) for rows in row_covers}))
    return tuple(sorted(row_covers))


def profiles() -> tuple[tuple[F, ...], ...]:
    """Rational denominator-seven profiles with the PXC88 role order."""
    answer = []
    for top in range(29, 42):
        for subtop in range(15, top):
            outsider_total = 140 - 2 * top - 2 * subtop
            for outsiders in itertools.product(range(15), repeat=3):
                if sum(outsiders) != outsider_total:
                    continue
                if max(outsiders) >= subtop:
                    continue
                z = tuple(F(value, 7) for value in (
                    top, top, subtop, subtop, *outsiders
                ))
                if all(
                    coalition_sum(z, row) >= bound
                    for row, bound in base.LMIN_ROWS.items()
                ):
                    answer.append(z)
    return tuple(answer)


def analyze(rows: tuple[int, ...], prescribed_z: tuple[F, ...]):
    if any(
        coalition_sum(base.X, row) < coalition_sum(prescribed_z, row)
        for row in rows
    ):
        return None
    constraints = {
        row: coalition_sum(prescribed_z, row) for row in rows
    }
    constraints.update(base.LMIN_ROWS)
    minimize = coalition_minimizer(constraints)
    if any(minimize(1 << player) for player in range(base.N)):
        return None
    values = tuple(minimize(coalition) for coalition in range(1 << base.N))
    x, z = selectors(values, base.N)
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1 or roots[0][:3] != (
        base.R, (base.H, base.A, base.B), base.OUTSIDERS
    ):
        return None
    if not (
        z[base.R] == z[base.H] == max(z)
        and z[base.A] == z[base.B] < max(z)
        and max(z[player] for player in base.OUTSIDERS) < z[base.A]
    ):
        return None
    packet_margin = margins(values, x, z)["packet_margin"]
    if packet_margin >= 0:
        return None
    direct = has_direct_packet(x, z, base.TARGET)
    pair = coalition_sum(z, base.PAIR) == values[base.PAIR]
    pxc78 = (
        coalition_sum(z, base.HEAVY_BLOCK) == values[base.HEAVY_BLOCK]
        and all(
            coalition_sum(z, row) == values[row]
            for row in base.DOUBLE_COSTARS
        )
    )
    matching = base.split_matching_tight(values, z)
    return {
        "rows": list(rows),
        "prescribed_z": [str(value) for value in prescribed_z],
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "packet_margin": str(packet_margin),
        "direct": direct,
        "top_pair_tight": pair,
        "pxc78_full": pxc78,
        "split_matching": matching,
        "classification_escape": not (direct or pair or pxc78 or matching),
        "defining_constraints": {
            str(row): str(bound) for row, bound in sorted(constraints.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--max-profile-distance", type=int, default=12)
    parser.add_argument("--symmetry-reduced", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    calibration_rows = tuple(sorted({
        base.mask(base.R, base.H, base.B, 4),
        base.mask(base.R, base.H, base.A, 5),
        base.mask(base.H, 6),
        base.mask(base.R, base.H, base.A, 6),
        base.mask(base.R, base.H, base.B, 6),
    }))
    calibration = analyze(calibration_rows, base.Z)
    if (
        calibration is None
        or calibration["packet_margin"] != "-1/7"
        or calibration["direct"]
        or not calibration["split_matching"]
        or calibration["classification_escape"]
    ):
        raise AssertionError("PXC88 calibration failed")

    supports = tuple(
        rows
        for size in (3, 4, 5)
        for rows in labelled_covers(size, args.symmetry_reduced)
    )
    all_profiles = profiles()
    base_numerators = tuple(int(7 * value) for value in base.Z)
    profile_grid = tuple(
        z for z in all_profiles
        if sum(
            abs(int(7 * value) - reference)
            for value, reference in zip(z, base_numerators)
        ) <= args.max_profile_distance
    )
    if not profile_grid:
        raise AssertionError("profile-distance filter removed the calibration")
    rng = random.Random(args.seed)
    stats = {
        "rounds": args.rounds,
        "support_covers": len(supports),
        "symmetry_reduced": args.symmetry_reduced,
        "all_profiles": len(all_profiles),
        "profiles": len(profile_grid),
        "max_profile_distance": args.max_profile_distance,
        "qualified_packet_violations": 0,
        "pair": 0,
        "pxc78": 0,
        "matching": 0,
        "direct": 0,
        "escapes": 0,
    }
    findings = []
    for _ in range(args.rounds):
        result = analyze(rng.choice(supports), rng.choice(profile_grid))
        if result is None:
            continue
        stats["qualified_packet_violations"] += 1
        stats["pair"] += int(result["top_pair_tight"])
        stats["pxc78"] += int(result["pxc78_full"])
        stats["matching"] += int(result["split_matching"])
        stats["direct"] += int(result["direct"])
        if result["classification_escape"]:
            stats["escapes"] += 1
            findings.append(result)
            print(json.dumps(result), flush=True)

    payload = {
        "claim": "profile-varying design search; not proof evidence",
        "calibration": calibration,
        "stats": stats,
        "findings": findings,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
