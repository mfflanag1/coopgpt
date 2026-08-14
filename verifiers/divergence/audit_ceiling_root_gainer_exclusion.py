#!/usr/bin/env python3
r"""Exact controls for ceiling-root gainer exclusion and packing duality.

The dimension-free proof is by Lmin carrier monotonicity and rooted
packing/cover duality.  Finite scans check the exact partition and arithmetic;
they are not the proof of universal selection or target pricing.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from exactlp import exact_linprog  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def rooted_packing(support, n, root):
    rooted = tuple(coalition for coalition in support if coalition >> root & 1)
    inequalities = []
    rhs = []
    for player in range(n):
        if player == root:
            continue
        inequalities.append(
            [F((coalition >> player) & 1) for coalition in rooted]
        )
        rhs.append(F(1))
    for variable in range(len(rooted)):
        inequalities.append(
            [F(-1 if other == variable else 0) for other in range(len(rooted))]
        )
        rhs.append(F(0))
    status, negative_load, weights = exact_linprog(
        [F(-1)] * len(rooted), inequalities, rhs
    )
    if status != "optimal":
        raise AssertionError("ceiling-root packing did not optimize")
    maximum_load = -negative_load

    offroot = tuple(player for player in range(n) if player != root)
    cover_inequalities = [
        [-F((coalition >> player) & 1) for player in offroot]
        for coalition in rooted
    ]
    cover_rhs = [F(-1)] * len(rooted)
    for variable in range(len(offroot)):
        cover_inequalities.append(
            [F(-1 if other == variable else 0) for other in range(len(offroot))]
        )
        cover_rhs.append(F(0))
    cover_status, cover_value, cover = exact_linprog(
        [F(1)] * len(offroot), cover_inequalities, cover_rhs
    )
    if cover_status != "optimal" or cover_value != maximum_load:
        raise AssertionError("ceiling-root packing/cover duality failed")
    return rooted, maximum_load, weights, tuple(zip(offroot, cover))


def audit_case(name, trail, values, x, z):
    n = len(x)
    ceiling = max(z)
    roots = tuple(
        player for player in range(n) if z[player] == ceiling and x[player] >= ceiling
    )
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    support = tuple(full_tight_support(values, x))
    rows = []
    for root in roots:
        if any(not (x[gainer] < x[root]) for gainer in gainers):
            raise AssertionError("ceiling root is not strictly above every gainer")
        rooted, maximum_load, weights, cover = rooted_packing(support, n, root)
        common_carriers = tuple(
            player
            for player in range(n)
            if player != root
            and all(coalition >> player & 1 for coalition in rooted)
        )
        if set(common_carriers) & set(gainers):
            raise AssertionError("a ceiling root has a gainer common carrier")
        omitted_rows = {
            str(gainer): next(
                (
                    coalition
                    for coalition in rooted
                    if not (coalition >> gainer & 1)
                ),
                None,
            )
            for gainer in gainers
        }
        if any(coalition is None for coalition in omitted_rows.values()):
            raise AssertionError("carrier monotonicity gainer omission failed")
        if maximum_load == 1:
            positive_cover = tuple(
                player for player, value in cover if value > 0
            )
            if not common_carriers or not positive_cover:
                raise AssertionError("tied rooted cover lacks a common carrier")
            if not set(positive_cover) <= set(common_carriers):
                raise AssertionError("unit cover uses a noncommon player")
        loads = tuple(
            sum(
                (
                    weight
                    for coalition, weight in zip(rooted, weights)
                    if coalition >> player & 1
                ),
                F(0),
            )
            for player in range(n)
        )
        rows.append(
            {
                "root": root,
                "gainers": list(gainers),
                "root_x": str(x[root]),
                "ceiling": str(ceiling),
                "maximum_root_load": str(maximum_load),
                "root_excess": str(maximum_load - 1),
                "common_carriers": list(common_carriers),
                "gainer_omitting_rows": omitted_rows,
                "positive_packing_support": [
                    {"coalition": coalition, "weight": str(weight)}
                    for coalition, weight in zip(rooted, weights)
                    if weight
                ],
                "player_loads": [str(value) for value in loads],
                "positive_cover": {
                    str(player): str(value) for player, value in cover if value
                },
            }
        )
    return {"name": name, "trail": trail, "roots": rows}


def lower_envelope_case(case):
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
    return (
        lower_envelope(generators),
        tuple(map(F, case["x"])),
        tuple(map(F, case["z"])),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive_rows = []
    residual_rows = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            row = audit_case(source.name, trail, values, x, z)
            archive_rows.append(row)
            total = sum(x, F(0))
            floor = min(x)
            ceiling = max(z)
            if (
                not has_direct_packet(x, z, F(2, 3))
                and ceiling - floor + total * floor / ceiling < F(2, 3) * total
                and floor > 0
            ):
                residual_rows.append(row)

    fixed_rows = []
    for case in CASES:
        values, x, z = lower_envelope_case(case)
        fixed_rows.append(audit_case(case["name"], "fixed-control", values, x, z))

    all_roots = tuple(root for row in archive_rows for root in row["roots"])
    residual_roots = tuple(root for row in residual_rows for root in row["roots"])
    fixed_roots = tuple(root for row in fixed_rows for root in row["roots"])
    counts = {
        "archive_records": len(archive_rows),
        "archive_ceiling_roots": len(all_roots),
        "archive_positive_root_excess": sum(
            F(root["root_excess"]) > 0 for root in all_roots
        ),
        "archive_tied_root_load": sum(
            F(root["root_excess"]) == 0 for root in all_roots
        ),
        "positive_residual_records": len(residual_rows),
        "positive_residual_ceiling_roots": len(residual_roots),
        "positive_residual_positive_root_excess": sum(
            F(root["root_excess"]) > 0 for root in residual_roots
        ),
        "positive_residual_tied_root_load": sum(
            F(root["root_excess"]) == 0 for root in residual_roots
        ),
        "fixed_controls": len(fixed_rows),
        "fixed_ceiling_roots": len(fixed_roots),
    }
    expected = {
        "archive_records": 374,
        "archive_ceiling_roots": 703,
        "archive_positive_root_excess": 149,
        "archive_tied_root_load": 554,
        "positive_residual_records": 16,
        "positive_residual_ceiling_roots": 16,
        "positive_residual_positive_root_excess": 16,
        "positive_residual_tied_root_load": 0,
        "fixed_controls": 7,
        "fixed_ceiling_roots": 10,
    }
    if counts != expected:
        raise AssertionError(("ceiling-root exclusion partition changed", counts))

    report = {
        "status": "exact ceiling-root gainer-exclusion controls verified",
        "human_theorem": (
            "every gainer is omitted by some Lmin-tight row containing a "
            "ceiling root; a tied full-menu rooted packing has a common "
            "nongainer carrier, while positive excess gives a rooted packet"
        ),
        "counts": counts,
        "positive_residual_rows": residual_rows,
        "fixed_controls": fixed_rows,
        "scope": (
            "dimension-free carrier monotonicity and LP duality; finite rows "
            "audit arithmetic only and do not prove packet target pricing"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
