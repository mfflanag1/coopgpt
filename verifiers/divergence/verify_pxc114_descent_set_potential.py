#!/usr/bin/env python3
"""Exact audit of the PXC114 descent-set inclusion theorem.

The conventional proof is dimension-free.  If R' has no edge to R, every
R-row derivative is nonnegative on every d in D_R'.  The positive normalized
cover identity has zero derivative, so every one of those derivatives is
zero.  The remaining tangent and staged conditions are common to the fixed
certificate fiber, hence D_R' is contained in D_R.  A one-way R->R' edge
makes the inclusion strict.

This audit pins the elementary positive-sum implication and replays the three
load-bearing exact graph calibrations without importing LP or selector code.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()


def load(name):
    return json.loads((HERE.parent / name).read_text())


def positive_sum_collapse(weights, derivatives):
    weights = tuple(map(F, weights))
    derivatives = tuple(map(F, derivatives))
    if not weights or len(weights) != len(derivatives) or min(weights) <= 0:
        raise ValueError("strictly positive conformable support required")
    if min(derivatives) < 0:
        raise ValueError("nonnegative derivatives required")
    if sum(w * d for w, d in zip(weights, derivatives)) != 0:
        raise ValueError("cover identity derivative is not zero")
    return all(d == 0 for d in derivatives)


def coalition_sum(vector, mask):
    return sum(value for i, value in enumerate(vector) if mask >> i & 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # Exact rational sign-collapse controls at every support size allowed by
    # the six-player four-outsider cover bound, plus two larger dimensions.
    collapse = {}
    for size in range(1, 7):
        weights = tuple(F(i + 1, size * (size + 1) // 2) for i in range(size))
        derivatives = (F(0),) * size
        collapse[str(size)] = {
            "weights": list(map(str, weights)),
            "derivatives": list(map(str, derivatives)),
            "all_derivatives_zero": positive_sum_collapse(weights, derivatives),
        }

    pxc108 = load("pxc108_invariant_cover_blocker_circuits.json")
    common = pxc108["calibrations"]["PXC101/PXC98 common blocker"]
    cross = pxc108["calibrations"]["PXC104 cross-cover cycle"]
    if common["common_descent_slots"] == [] or common["shortest_induced_cycle"] is not None:
        raise AssertionError("common-branch calibration changed")
    if cross["shortest_induced_cycle"] != [1, 2]:
        raise AssertionError("reciprocal-pair calibration changed")
    edges = {int(k): set(v) for k, v in cross["invariant_edges"].items()}
    if 2 not in edges[1] or 1 not in edges[2]:
        raise AssertionError("PXC104 reciprocal edges missing")

    pxc112 = load("pxc112_certificate_dependence.json")
    pxc112_independent = load("pxc112_certificate_dependence_independent.json")
    mixed = pxc112["complete_cx_lift_matrix"][1]["outcomes"]
    if mixed[0]["faithful"] or not mixed[1]["faithful"]:
        raise AssertionError("PXC112 one-way/empty-descent calibration changed")
    mixed_direction = tuple(map(
        F,
        pxc112_independent["explicit_bad_directions"][
            "Cx_11_23_pair_only_failure"
        ],
    ))
    if not (
        coalition_sum(mixed_direction, 7) < 0
        and coalition_sum(mixed_direction, 3) == 0
    ):
        raise AssertionError("PXC112 one-way edge witness changed")
    faithful = pxc112["complete_cx_lift_matrix"][2]["outcomes"]
    if not all(q["faithful"] for q in faithful):
        raise AssertionError("PXC112 faithful-fiber calibration changed")

    complete = json.loads(
        (HERE.parent / "search_archive" / "pxc108_both_top_complete.json").read_text()
    )
    aggregate = complete["aggregate"]
    if aggregate != {
        "universal_failure_menus": 42440,
        "cyclic_menus": 29420,
        "common_by_sink_menus": 13020,
    }:
        raise AssertionError(aggregate)
    if complete["pure_shortest_cycles_length_at_least_3"] != []:
        raise AssertionError("old finite census contains a pure long cycle")

    payload = {
        "claim": "dimension-free descent-set potential and primitive two-mechanism theorem",
        "theorem": {
            "nonedge_inclusion": "R' not-> R implies D_R' subseteq D_R",
            "one_way_strictness": (
                "R->R' and R' not->R implies D_R' proper-subset D_R"
            ),
            "cycle_consequence": (
                "every directed cycle contains a reciprocal edge; whenever a "
                "cycle exists, a two-cycle exists"
            ),
            "universal_failure_decomposition": (
                "common staged descent with an outside-union blocker, or, when "
                "the common intersection is empty, a reciprocal two-cover cycle"
            ),
        },
        "positive_sum_collapse_certificates": collapse,
        "exact_calibrations": {
            "PXC101/PXC98": "nonempty common branch and no cover cycle",
            "PXC104": "reciprocal pair [1,2]",
            "PXC112_C2": "pair cover fails while positive cover is faithful",
            "PXC112_C3": "both descent sets empty",
        },
        "n6_no_common_cx_census": aggregate | {
            "pure_shortest_cycles_length_at_least_3": len(
                complete["pure_shortest_cycles_length_at_least_3"]
            ),
        },
        "fail_open_controls": {
            "common_branch_nonempty": bool(common["common_descent_slots"]),
            "reciprocal_pair_nonempty": 2 in edges[1] and 1 in edges[2],
            "one_way_empty_descent_example_nonempty": (
                not mixed[0]["faithful"] and mixed[1]["faithful"]
                and coalition_sum(mixed_direction, 7) < 0
            ),
        },
        "scope": (
            "human theorem for every fixed tangent-cone certificate class, all "
            "payoff strata including ties, active common-Cx inequalities and "
            "zero-coordinate normals, and arbitrary strictly positive cover "
            "support weights; finite artifacts are exact regression controls"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
