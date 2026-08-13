#!/usr/bin/env python3
"""Exact n=7 boundary between strict quota, target reserve, and a facet.

The displayed singleton-normalized lower envelope has one affordable tied
maximum-overlap root and an unaffordable two-root carrier cycle.  Every
Lmin-tight comparison containing that cycle misses the strict excluded-block
deficit quota, while one of those rows still reaches the n=7 target after
the cardinality-base reserve is retained.  The affordable root also exposes
an extreme rooted packing whose pair lift is an indecomposable
exact-game-cone facet, tight at this game.

This is an exact hostile boundary control.  It does not prove a universal
target-reserve selection theorem or a universal facet-selection theorem.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import (  # noqa: E402
    carriers,
    directed_cycles,
    full_tight_support,
)
from audit_cover_to_direct_handover import direct_witnesses  # noqa: E402
from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_n6_positive_residual_facet_atlas import (  # noqa: E402
    canonical_rooted_support,
)
from verify_excluded_block_deficit_quota import target_reserve_row  # noqa: E402
from verify_n7_root_block_budget_counterexample import (  # noqa: E402
    staged_dual_certificates,
    z3_no_improving_directions,
)
from verify_rooted_hinge_projection import (  # noqa: E402
    decomposition_witnesses,
    matrix_rank,
)


GENERATORS = (
    (F(6), F(7), F(1), F(0), F(1), F(0), F(1)),
    (F(7), F(0), F(0), F(0), F(0), F(9), F(0)),
    (F(0), F(0), F(0), F(5), F(3), F(6), F(2)),
)
LMIN = (F(3), F(7, 2), F(1), F(3), F(1), F(7, 2), F(1))
LMAX = (F(3), F(3), F(0), F(2), F(3), F(3), F(2))
TARGET = F(7, 12)


def values_from_generators():
    return tuple(
        min(coalition_sum(generator, coalition) for generator in GENERATORS)
        for coalition in range(1 << 7)
    )


def fraction_strings(values):
    return [str(value) for value in values]


def pair_lift_facet(values):
    # The root-0 packing is 1/2 on coalitions 59, 73, and 81.  Offroot
    # incidence constraints at players 3, 4, and 6 give respectively
    # a+b=1, a+c=1, b+c=1, so this packing is a vertex.
    packing = {59: F(1, 2), 73: F(1, 2), 81: F(1, 2)}
    loads = tuple(
        sum(
            (weight for coalition, weight in packing.items() if coalition >> i & 1),
            F(),
        )
        for i in range(7)
    )
    if loads != (F(3, 2), F(1, 2), F(), F(1), F(1), F(1, 2), F(1)):
        raise AssertionError(("rooted packing loads changed", loads))
    root_excess = loads[0] - 1
    deficits = tuple(F() if i == 0 else 1 - loads[i] for i in range(7))
    if root_excess != F(1, 2) or deficits != (
        F(), F(1, 2), F(1), F(), F(), F(1, 2), F()
    ):
        raise AssertionError("rooted packing deficits changed")

    # Rooted complement averaging.  For the offroot nongainer set A, the
    # packing-weighted excluded Lmax mass and cardinality are determined
    # exactly by root excess and uncovered-player deficits.
    offroot_nongainers = (1, 2, 3, 5)
    excluded = {
        coalition: tuple(i for i in offroot_nongainers if not coalition >> i & 1)
        for coalition in packing
    }
    weighted_excluded_z = sum(
        (
            weight * sum((LMAX[i] for i in excluded[coalition]), F())
            for coalition, weight in packing.items()
        ),
        F(),
    )
    weighted_excluded_size = sum(
        (weight * len(excluded[coalition]) for coalition, weight in packing.items()),
        F(),
    )
    excluded_z_rhs = root_excess * sum((LMAX[i] for i in offroot_nongainers), F())
    excluded_z_rhs += sum((deficits[i] * LMAX[i] for i in offroot_nongainers), F())
    excluded_size_rhs = root_excess * len(offroot_nongainers)
    excluded_size_rhs += sum((deficits[i] for i in offroot_nongainers), F())
    tangent_lhs = sum(
        (deficits[i] * (LMIN[i] - LMAX[i]) for i in range(1, 7)), F()
    )
    tangent_rhs = root_excess * (LMIN[0] - LMAX[0])
    if (
        weighted_excluded_z != excluded_z_rhs
        or weighted_excluded_size != excluded_size_rhs
        or tangent_lhs < tangent_rhs
    ):
        raise AssertionError("rooted complement/tangent coupling changed")

    coefficients = dict(packing)
    for i, deficit in enumerate(deficits):
        if deficit:
            coefficients[1 | (1 << i)] = deficit
    coefficients[1] = -(root_excess + sum(deficits, F()))
    incidence = tuple(
        sum(
            (coefficient for coalition, coefficient in coefficients.items() if coalition >> i & 1),
            F(),
        )
        for i in range(7)
    )
    if incidence != (F(1),) * 7:
        raise AssertionError(("pair-lift incidence failed", incidence))
    if sum((coefficient * values[coalition] for coalition, coefficient in coefficients.items()), F()) != values[127]:
        raise AssertionError("pair-lift facet is not tight at the displayed game")

    support = tuple(sorted(coefficients))
    rank = matrix_rank(support, 7)
    decompositions = decomposition_witnesses(support, 7)
    if rank != len(support) or decompositions:
        raise AssertionError(("pair lift is not indecomposable", rank, decompositions))
    canonical = canonical_rooted_support(support, 0, 7)
    if canonical != (1, 3, 5, 9, 49, 81, 103):
        raise AssertionError(("canonical support changed", canonical))
    floor = min(LMIN)
    weighted_floor_distance = sum(
        (deficits[i] * (LMIN[i] - floor) for i in range(1, 7)), F()
    )
    rooted_pair_premium = sum(
        (deficits[i] * values[1 | (1 << i)] for i in range(1, 7)), F()
    )
    alignment_penalty = max(
        F(), (weighted_floor_distance - rooted_pair_premium) / root_excess
    )
    price = sum(deficits, F()) / root_excess
    rooted_bound = F(7, price + 6)
    if (
        weighted_floor_distance != F(5, 2)
        or rooted_pair_premium != 3
        or alignment_penalty != 0
        or price != 4
        or rooted_bound != F(7, 10)
        or rooted_bound < TARGET
    ):
        raise AssertionError("rooted price/alignment replay changed")
    return {
        "root": 0,
        "extreme_packing": {str(k): str(v) for k, v in sorted(packing.items())},
        "active_vertex_equations": ["a+b=1", "a+c=1", "b+c=1"],
        "root_excess": str(root_excess),
        "deficits": fraction_strings(deficits),
        "rooted_complement_average": {
            "offroot_nongainers": list(offroot_nongainers),
            "excluded_sets": {str(k): list(v) for k, v in excluded.items()},
            "weighted_excluded_z": str(weighted_excluded_z),
            "excess_deficit_z_rhs": str(excluded_z_rhs),
            "weighted_excluded_cardinality": str(weighted_excluded_size),
            "excess_deficit_cardinality_rhs": str(excluded_size_rhs),
            "tangent_lhs": str(tangent_lhs),
            "tangent_rhs": str(tangent_rhs),
            "tangent_slack": str(tangent_lhs - tangent_rhs),
        },
        "price_Q_over_delta": str(price),
        "weighted_floor_distance": str(weighted_floor_distance),
        "rooted_pair_premium": str(rooted_pair_premium),
        "multistage_alignment_penalty": str(alignment_penalty),
        "rooted_overlap_bound": str(rooted_bound),
        "rooted_bound_reaches_target": True,
        "pair_lift": {str(k): str(v) for k, v in sorted(coefficients.items())},
        "support_rank": rank,
        "support_size": len(support),
        "decomposition_count": len(decompositions),
        "indecomposable": True,
        "canonical_support": list(canonical),
        "facet_slack_at_game": "0",
        "classification": (
            "an indecomposable rooted pair lift of an extreme marked packing; "
            "its canonical support is distinct from the five n=6 residual-atlas "
            "orbits, but this is not a novelty claim or a new facet mechanism"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values = values_from_generators()
    if any(values[1 << i] for i in range(7)) or values[127] != 16:
        raise AssertionError("singleton normalization or total failed")
    if not all(
        coalition_sum(generator, coalition) >= values[coalition]
        for generator in GENERATORS
        for coalition in range(128)
    ):
        raise AssertionError("generator outside lower-envelope core")
    if any(
        not any(coalition_sum(generator, coalition) == values[coalition] for generator in GENERATORS)
        for coalition in range(128)
    ):
        raise AssertionError("coalition minimum is unattained")
    for point in (LMIN, LMAX):
        if sum(point, F()) != 16 or any(
            coalition_sum(point, coalition) < values[coalition]
            for coalition in range(128)
        ):
            raise AssertionError("displayed selector is outside the core")

    # Two exact formulations certify both complete lexicographic selections:
    # staged Farkas multipliers and primal Z3 no-improving-direction systems.
    dual_min = staged_dual_certificates(values, LMIN, "min")
    dual_max = staged_dual_certificates(values, LMAX, "max")
    z3_min = z3_no_improving_directions(values, LMIN, "min")
    z3_max = z3_no_improving_directions(values, LMAX, "max")

    support = full_tight_support(values, LMIN)
    roots = maximum_overlap_roots(LMIN, LMAX)
    audits = tuple(solve_labelled_cover(support, root, 7) for root in roots)
    if roots != (0, 1, 5) or tuple(F(row["margin"]) for row in audits) != (1, -1, -1):
        raise AssertionError(("root boundary changed", roots, audits))
    graph = {
        row["root"]: tuple(carrier for carrier in carriers(row) if carrier in roots)
        for row in audits
    }
    if graph != {0: (), 1: (5,), 5: (1,)} or directed_cycles(graph) != ((1, 5),):
        raise AssertionError(("carrier cycle changed", graph))

    gainers = (4, 6)
    nongainers = (0, 1, 2, 3, 5)
    cycle_mask = (1 << 1) | (1 << 5)
    quota_rows = []
    for coalition in support:
        if coalition & cycle_mask != cycle_mask:
            continue
        h_set = tuple(i for i in nongainers if coalition >> i & 1)
        p_set = tuple(i for i in nongainers if i not in h_set)
        if not p_set:
            continue
        row = target_reserve_row(LMIN, LMAX, p_set, gainers, h_set, TARGET)
        row["support_coalition"] = coalition
        row["H"] = list(h_set)
        comparison_gainers = tuple(i for i in gainers if coalition >> i & 1)
        row["comparison_gainers"] = list(comparison_gainers)
        row["proper_maximal_comparison"] = len(comparison_gainers) == len(gainers) - 1
        quota_rows.append(row)
    if len(quota_rows) != 6 or any(row["closes"] for row in quota_rows):
        raise AssertionError(("expected every cycle-support quota to fail", quota_rows))
    strict_packets = direct_witnesses(LMIN, LMAX, support, TARGET)
    if strict_packets:
        raise AssertionError("unexpected strict interval-hitting direct packet")
    reserve_rows = [
        row for row in quota_rows
        if row["proper_maximal_comparison"] and row["target_reserve_closes"]
    ]
    if len(reserve_rows) != 1 or reserve_rows[0]["support_coalition"] != 59:
        raise AssertionError(("target-reserve boundary changed", reserve_rows))

    overlap = sum((min(a, b) for a, b in zip(LMIN, LMAX)), F())
    transfer = sum((LMAX[i] - LMIN[i] for i in gainers), F())
    if overlap != 13 or transfer != 3 or overlap != values[127] - transfer:
        raise AssertionError("overlap-transfer identity failed")

    report = {
        "status": "exact n=7 strict-quota/target-reserve/facet boundary verified",
        "generators": [fraction_strings(row) for row in GENERATORS],
        "total": "16",
        "Lmin": fraction_strings(LMIN),
        "Lmax": fraction_strings(LMAX),
        "overlap": str(overlap),
        "overlap_ratio": str(overlap / 16),
        "target": str(TARGET),
        "target_margin": str(overlap - TARGET * 16),
        "total_transfer_D": str(transfer),
        "identity": "O=T-D",
        "lmin_tight_support": list(support),
        "maximum_overlap_roots": list(roots),
        "labelled_root_audits": audits,
        "carrier_graph": {str(root): list(rows) for root, rows in graph.items()},
        "unaffordable_carrier_cycle": [1, 5],
        "cycle_support_quota_rows": quota_rows,
        "all_cycle_support_strict_quotas_fail": True,
        "strict_interval_hitting_direct_packets": 0,
        "target_reserve_closing_proper_rows": reserve_rows,
        "rooted_pair_lift_facet": pair_lift_facet(values),
        "selection_certificates": {
            "staged_dual_Lmin": dual_min,
            "staged_dual_Lmax": dual_max,
            "primal_Z3_Lmin": z3_min,
            "primal_Z3_Lmax": z3_max,
        },
        "scope": (
            "a fixed exact n=7 boundary theorem and hostile falsification "
            "control; not a universal target-reserve or facet selection theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
