#!/usr/bin/env python3
"""Fail-closed dependency audit for the restricted PXC91c frontier.

This verifier does not replace the component or human proofs.  It checks the
release-pinned exact dependencies used by restricted PXC96: the n=6
pair-slack and pair-tight branches, the unique n=7 PXC88 failure, its
indispensable repair rows, and the faithful PXC90 calibration.  The general
auxiliary-row bound remains the analytic Farkas/Caratheodory theorem PXC92c.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str) -> tuple[dict, str]:
    raw = (HERE / name).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    pxc88, h88 = load("faithful_sparse_lift_counterexample.json")
    pxc88i, h88i = load("faithful_sparse_lift_counterexample_independent.json")
    pxc90i, h90i = load("pxc89_classification_counterexample_independent.json")
    split, hsplit = load("n6_split_cover_blocker_no_go.json")
    rank, hrank = load("n6_extreme_cover_rank_fidelity.json")
    zero, hzero = load("n6_zero_loss_cover_boundaries.json")
    pair, hpair = load("n6_top_pair_blocker_no_go.json")

    x = ["6", "4", "2", "2", "2", "2", "2"]
    z = ["29/7", "29/7", "27/7", "27/7", "4/7", "12/7", "12/7"]
    zp = ["29/7", "29/7", "26/7", "26/7", "5/7", "13/7", "12/7"]
    require(pxc88["dimension"] == 7, "PXC88 dimension changed")
    require(pxc88["singleton_normalized"], "PXC88 lost singleton normalization")
    require(pxc88["ordered_saturated_single_heavy_s2"], "PXC88 left frozen domain")
    require(pxc88["frozen_domain_role_count"] ==
            {"root": 1, "gainers": 3, "outsiders": 3},
            "PXC88 frozen-domain role count changed")
    require(Fraction(pxc88["packet_margin"]) < 0,
            "PXC88 left the reserve-failing branch")
    require(not pxc88["direct_packet_exists"], "PXC88 became direct-closed")
    require(pxc88["full_lmin"] == x and pxc88["full_lmax"] == z,
            "PXC88 selectors changed")
    require(pxc88["complete_lmin_support"] == [7, 11, 13],
            "PXC88 complete Lmin row pool changed")
    require(pxc88["every_proper_lmin_row_subset_changes_lmin"] and
            len(pxc88["proper_lmin_row_subset_selectors"]) == 7,
            "PXC88 Lmin-row subset indispensability changed")
    require(pxc88["positive_extreme_top_cover_count"] == 1,
            "PXC88 positive extreme cover is no longer unique")
    require(pxc88["unique_top_cover"] == {
        "rows": [27, 39, 66],
        "weights": ["1/3", "1/3", "1/3"],
        "eta": "1/3",
        "alpha": ["1/3", "2/3"],
    }, "PXC88 exact top cover changed")
    require(pxc88["minimal_lift_lmin"] == x and pxc88["minimal_lift_lmax"] == zp,
            "PXC88 minimal-lift fidelity failure changed")
    require(pxc88["indispensable_auxiliary_rows"] == [71, 75],
            "PXC88 indispensable rows changed")
    require(pxc88["two_auxiliary_rows_restore_both_selectors"],
            "PXC88 two-row repair failed")
    require(pxc88i["unique_normalized_cover_weights"] ==
            ["1/3", "1/3", "1/3", "0", "0"],
            "independent PXC88 cover solve changed")
    require(pxc88i["reduced_lmax"] == zp and
            pxc88i["two_zero_weight_auxiliaries_necessary"],
            "independent PXC88 fidelity/repair replay changed")

    require(pxc88["pxc90_faithful_positive_calibration"],
            "primary PXC90 calibration failed")
    require(pxc90i["singleton_normalized"] and
            pxc90i["lmin_human_certificate"] and
            pxc90i["lmax_human_certificate"] and pxc90i["forked_cover"],
            "independent PXC90 calibration failed")

    require(split["feasible_complete_families"] == 0 and
            split["base_system_feasible"], "PXC93 split boundary changed")
    require(rank["labelled_covers"] == 807 and rank["colored_orbits"] == 259 and
            rank["labelled_size_counts"] ==
            {"1": 1, "2": 7, "3": 96, "4": 703} and
            rank["colored_orbit_size_counts"] ==
            {"1": 1, "2": 4, "3": 37, "4": 217},
            "PXC94 full cover census changed")
    require(rank["pair_slack_residual"]["labelled_covers"] == 806 and
            rank["pair_slack_residual"]["colored_orbits"] == 258,
            "PXC94 pair-slack census changed")
    require(rank["rank_support_theorem"]
            ["all_positive_eta_covers_have_full_outsider_incidence_column_rank"],
            "PXC94 rank theorem gate failed")
    small = rank["small_support_colored_classification"]
    require(small["support_two_transition"] == [
        {"rows": [7, 59], "scalar_status": "infeasible",
         "route": "scalar reserve/comparison no-go"},
        {"rows": [15, 51], "scalar_status": "infeasible",
         "route": "scalar reserve/comparison no-go"},
        {"rows": [19, 47], "scalar_status": "optimal",
         "route": "zero-loss outsider-partition blocker audit"},
        {"rows": [23, 43], "scalar_status": "optimal",
         "route": "PXC93 split-cover blocker audit"},
    ], "PXC94 support-two transition changed")
    require(small["support_three_orbits"] == 37 and
            small["support_three_scalar_infeasible"] == 34 and
            small["support_three_scalar_feasible"] ==
            [[5, 18, 43], [5, 19, 42], [5, 19, 43]] and
            small["support_three_root_witness_infeasible"] ==
            [[5, 18, 43], [5, 19, 43]] and
            small["support_three_root_witness_feasible"] == [[5, 19, 42]],
            "PXC94 support-three transition changed")
    require(rank["scalar_fail_open_control"]["status"] == "optimal",
            "PXC94 fail-open control changed")
    require(zero["outsider_partition"]["feasible_closing_families"] == 0 and
            zero["outsider_partition"]["base_system_feasible"],
            "PXC94 outsider-partition boundary changed")
    require(zero["h2_equality_boundary"]["feasible_candidate_blockers"] == 0 and
            zero["h2_equality_boundary"]["base_system_feasible"],
            "PXC94 H2 boundary changed")
    require(pair["allocation_direct_branches"] == 5340 and
            pair["survivors_before_root_witness"] == 642 and
            pair["survivors_after_root_witness"] == 0 and
            pair["survivors"] == [] and pair["fail_open_base"],
            "PXC95 tight-pair exclusion changed")

    payload = {
        "claim": "release dependency audit for the resolved restricted faithful sparse-lift frontier",
        "domain_minimum_dimension": 6,
        "domain_role_count": {
            "root": 1,
            "gainers": 3,
            "minimum_outsiders": 2,
        },
        "n6": {
            "pair_slack": "PXC94 selector-faithful support-four cover",
            "pair_tight_after_reserve_and_direct_failure": "infeasible by PXC95",
            "conclusion": "restricted PXC91c holds",
        },
        "n7": {
            "counterexample": "PXC88",
            "positive_extreme_top_covers": 1,
            "minimal_lift_lmax": zp,
            "indispensable_auxiliary_rows": [71, 75],
            "conclusion": "restricted PXC91c fails",
        },
        "corrected_lift": {
            "status": "analytic PXC92c theorem; not derived by this dependency script",
            "general_additional_row_bound": "n(n-2)",
            "PXC88_exact_additional_rows": 2,
        },
        "positive_calibration": "PXC90 independently preserves both selectors",
        "smallest_counterexample_in_frozen_domain": 7,
        "component_sha256": {
            "PXC88_primary": h88,
            "PXC88_independent": h88i,
            "PXC90_independent": h90i,
            "PXC93_split": hsplit,
            "PXC94_rank": hrank,
            "PXC94_zero_loss": hzero,
            "PXC95_pair_tight": hpair,
        },
        "scope": (
            "dependency audit of exact component artifacts; PXC96 is confined "
            "to the ordered saturated single-heavy s=2, k>=2, "
            "reserve/direct-failing domain; PXC98 separately proves unrestricted "
            "PXC91c false at n=6, and PXC100 proves the canonical pair cover "
            "faithful at n=5, making six the global minimum failure dimension"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
