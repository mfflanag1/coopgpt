#!/usr/bin/env python3
"""Exact controls for the PXC120 positive-demand/faithfulness conjecture.

This is a targeted falsification audit, not a proof of the all-n statement.
It checks whether each fixed labelled spectral control has one explicit
dispersion-optimal extreme top cover whose retained lift is faithful.  It
also checks that the archived n=6 bank has no positive post-top demand, and
recomputes the actual-top demand of the four canonical PXC114 obstruction
controls directly from their selector profiles.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DIV = ROOT / "verifiers" / "divergence"
sys.path[:0] = [str(ROOT / "src"), str(DIV)]

from audit_lmax_overcover import records, top_certificate  # noqa: E402
from audit_spectral_label_currency import opposite_residual  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_pxc108_invariant_cover_blocker_circuits import recognize  # noqa: E402


def csum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def lower_envelope(g, h):
    return tuple(min(csum(g, mask), csum(h, mask)) for mask in range(1 << len(g)))


def actual_top_bound(x, z):
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    return (
        sum((min(x[i], maximum) for i in top), F(0))
        + opposite_residual(x, z, set(top))
    )


def fixed_case(case):
    g, h = tuple(map(F, case["g"])), tuple(map(F, case["h"]))
    x, z = tuple(case["x"]), tuple(case["z"])
    values = lower_envelope(g, h)
    top = tuple(i for i, value in enumerate(z) if value == max(z))
    total = sum(x, F(0))
    target = F(len(x), (len(x) * len(x)) // 4) * total
    bound = actual_top_bound(x, z)
    demand = max(F(0), target - bound)
    row = {
        "name": case["name"],
        "post_top_demand_ratio": str(demand / total),
    }
    if demand == 0:
        return row

    certificate = top_certificate(values, z)
    cover = {
        "rows": certificate["support"],
        "weights": certificate["weights"],
        "eta": certificate["eta"],
        "alpha": tuple(certificate["alpha"][i] for i in top),
    }
    full = (1 << len(z)) - 1
    menu = tuple(mask for mask in range(1, full) if csum(z, mask) == values[mask])
    verdict = recognize({
        "label": case["name"],
        "x": x,
        "z": z,
        "top": top,
        "cx": tuple(case["support_x"]),
        "menu": menu,
        "covers": (cover,),
    })
    circuit = verdict["cover_circuits"][0]
    if verdict["classification"] != "faithful":
        raise AssertionError((case["name"], verdict))
    if circuit["active_columns"] != circuit["active_rank"]:
        raise AssertionError((case["name"], "displayed cover is not basic/extreme"))
    alpha = tuple(certificate["alpha"][i] for i in top)
    if min(alpha) <= 0:
        raise AssertionError((case["name"], "positive-demand cover misses a top player"))
    row["faithful_qualifying_extreme_cover"] = {
        "rows": list(certificate["support"]),
        "weights": [str(q) for q in certificate["weights"]],
        "eta": str(certificate["eta"]),
        "alpha": [str(q) for q in alpha],
        "active_rank": circuit["active_rank"],
    }
    return row


def obstruction_controls():
    controls = {
        "PXC101_common": (
            (F(9, 2), F(9, 2), F(2), F(2), F(2), F(2)),
            (F(4), F(4), F(3), F(3), F(2), F(1)),
        ),
        "PXC104_reciprocal": (
            (F(41, 6), F(41, 6), F(7, 3), F(7, 3), F(7, 3), F(7, 3)),
            (F(6), F(6), F(5), F(4), F(1), F(1)),
        ),
        "PXC116_common": (
            (F(25, 4), F(25, 4), F(1, 2), F(9, 4), F(1, 2), F(9, 4)),
            (F(6), F(6), F(0), F(2), F(1), F(3)),
        ),
        "PXC118_reciprocal": (
            (F(41, 6), F(41, 6), F(7, 3), F(7, 3), F(7, 3), F(7, 3)),
            (F(6), F(6), F(5), F(4), F(1), F(1)),
        ),
    }
    rows = []
    for name, (x, z) in controls.items():
        total = sum(x, F(0))
        target = F(2, 3) * total
        bound = actual_top_bound(x, z)
        if bound < target:
            raise AssertionError((name, bound, target))
        rows.append({
            "name": name,
            "actual_top_bound_ratio": str(bound / total),
            "post_top_demand_ratio": "0",
        })
    return rows


def archive_summary(paths):
    records_seen = 0
    positive_demand = []
    for path in paths:
        data = json.loads(path.read_text())
        for _source, trail, _values, x, z in records(data, path):
            if len(x) != 6:
                continue
            records_seen += 1
            total = sum(x, F(0))
            bound = actual_top_bound(x, z)
            if bound < F(2, 3) * total:
                positive_demand.append({
                    "source": path.name,
                    "trail": trail,
                    "actual_top_bound_ratio": str(bound / total),
                })
    if positive_demand:
        raise AssertionError(("archive produced positive demand", positive_demand[:3]))
    return {"records": records_seen, "positive_post_top_demand": positive_demand}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = args.paths or [
        ROOT / "verifiers" / "s6" / "harvest6_601.json",
        ROOT / "verifiers" / "s6" / "harvest6_602.json",
    ]
    fixed = [fixed_case(case) for case in CASES]
    positive = [row["name"] for row in fixed if F(row["post_top_demand_ratio"]) > 0]
    if positive != ["actual_top_fixed_failure", "top_and_bottom_fixed_failure"]:
        raise AssertionError(("positive-demand controls changed", positive))
    payload = {
        "claim": "exact controls for the open fixed-Cx PXC120 positive-demand-faithfulness conjecture",
        "fixed_labelled_controls": fixed,
        "positive_demand_controls_with_faithful_cover": positive,
        "canonical_common_and_reciprocal_controls": obstruction_controls(),
        "n6_archive": archive_summary(paths),
        "scope": (
            "finite falsification evidence only; no all-n implication from positive "
            "post-top demand to faithful-cover existence is claimed"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
