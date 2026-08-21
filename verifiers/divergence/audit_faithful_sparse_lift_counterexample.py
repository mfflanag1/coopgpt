#!/usr/bin/env python3
"""Exact refutation of the faithful sparse-lift conjecture PXC91c.

The direct-failing PXC88 game is reused as a hostile calibration.  The audit
recomputes its lower envelope and both selectors, extracts a complete staged
Lmin support, exhausts every strictly-positive extreme top-cover support, and
recomputes the selector after retaining only that support.  It also checks the
faithful PXC90 forked-cover control and the two auxiliary rows that repair
PXC88.  All scientific decisions are made over Fraction arithmetic.
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

from exactlp import exact_linprog  # noqa: E402

from audit_class_b_support_alternative import mask  # noqa: E402
from audit_class_b_three_row_supports import normalized_cover  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_n6_equality_one_witness_roots import stage_support  # noqa: E402
from audit_pxc89_classification_counterexample import (  # noqa: E402
    CONSTRAINTS as PXC90_CONSTRAINTS,
    TOP_ROWS as PXC90_TOP_ROWS,
    Z as PXC90_Z,
)
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from audit_spectral_or_reserve import margins, selectors  # noqa: E402


N = 7
TOTAL = F(20)
FULL = (1 << N) - 1
TARGET = F(7, 12)
X = (F(6), F(4), F(2), F(2), F(2), F(2), F(2))
Z = (F(29, 7), F(29, 7), F(27, 7), F(27, 7), F(4, 7), F(12, 7), F(12, 7))
Z_REDUCED = (
    F(29, 7), F(29, 7), F(26, 7), F(26, 7),
    F(5, 7), F(13, 7), F(12, 7),
)

LMIN_ROWS = (mask(0, 1, 2), mask(0, 1, 3), mask(0, 2, 3))
TOP_ROWS = (mask(0, 1, 3, 4), mask(0, 1, 2, 5), mask(1, 6))
AUXILIARY_ROWS = (mask(0, 1, 2, 6), mask(0, 1, 3, 6))
CONSTRAINTS = {
    TOP_ROWS[0]: F(89, 7),
    TOP_ROWS[1]: F(97, 7),
    TOP_ROWS[2]: F(41, 7),
    LMIN_ROWS[0]: F(12),
    LMIN_ROWS[1]: F(12),
    LMIN_ROWS[2]: F(10),
    AUXILIARY_ROWS[0]: F(97, 7),
    AUXILIARY_ROWS[1]: F(97, 7),
}


def coalition_minimizer(constraints: dict[int, F]):
    inequalities: list[list[F]] = []
    rhs: list[F] = []
    for coalition, bound in constraints.items():
        inequalities.append([
            -F(int(bool(coalition >> player & 1))) for player in range(N)
        ])
        rhs.append(-bound)
    for player in range(N):
        row = [F(0)] * N
        row[player] = -1
        inequalities.append(row)
        rhs.append(F(0))

    def minimize(coalition: int) -> F:
        objective = [F(int(bool(coalition >> player & 1))) for player in range(N)]
        status, optimum, _point = exact_linprog(
            objective, inequalities, rhs, [[F(1)] * N], [TOTAL]
        )
        if status != "optimal":
            raise AssertionError(("coalition minimum failed", coalition, status))
        return optimum

    return minimize


def lower_envelope(constraints: dict[int, F]) -> tuple[F, ...]:
    minimize = coalition_minimizer(constraints)
    return tuple(minimize(coalition) for coalition in range(1 << N))


def complete_lmin_support(values: tuple[F, ...], x: tuple[F, ...]) -> tuple[int, ...]:
    support: set[int] = set()
    for stage, block in enumerate(payoff_blocks(x, "min")):
        for player in block:
            support.update(stage_support(values, x, "min", stage, player))
    return tuple(sorted(support))


def tight_rows(values: tuple[F, ...], point: tuple[F, ...]) -> tuple[int, ...]:
    return tuple(
        coalition for coalition in range(1, FULL)
        if coalition.bit_count() >= 2
        and coalition_sum(point, coalition) == values[coalition]
    )


def positive_extreme_top_supports(
    values: tuple[F, ...], z: tuple[F, ...]
) -> tuple[dict, ...]:
    tight = tight_rows(values, z)
    answers = []
    for size in range(1, min(N - 2, len(tight)) + 1):
        for rows in itertools.combinations(tight, size):
            cover = normalized_cover(rows)
            if cover is None or min(cover[2]) <= 0:
                continue
            weights, eta, alpha = cover
            answers.append({
                "rows": rows,
                "weights": weights,
                "eta": eta,
                "alpha": alpha,
            })
    return tuple(answers)


def selector_pair(constraints: dict[int, F]):
    values = lower_envelope(constraints)
    return values, *selectors(values, N)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values, x, z = selector_pair(CONSTRAINTS)
    if x != X or z != Z or any(values[1 << player] for player in range(N)):
        raise AssertionError(("PXC88 calibration changed", x, z))
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1 or roots[0][:3] != (0, (1, 2, 3), (4, 5, 6)):
        raise AssertionError(("ordered saturated root changed", roots))
    packet_margin = margins(values, x, z)["packet_margin"]
    if packet_margin != F(-1, 7) or has_direct_packet(x, z, TARGET):
        raise AssertionError("PXC88 left the reserve/direct-failing branch")

    x_tight = tight_rows(values, x)
    z_tight = tight_rows(values, z)
    support_x = complete_lmin_support(values, x)
    if x_tight != LMIN_ROWS or support_x != LMIN_ROWS:
        raise AssertionError(("complete Lmin support changed", x_tight, support_x))
    proper_subset_lmins = []
    for size in range(len(LMIN_ROWS)):
        for rows in itertools.combinations(LMIN_ROWS, size):
            subset_constraints = {
                row: coalition_sum(X, row) for row in rows
            }
            _subset_values, subset_x, _subset_z = selector_pair(subset_constraints)
            if subset_x == X:
                raise AssertionError(("proper Lmin-row subset still pins X", rows))
            proper_subset_lmins.append({
                "rows": list(rows),
                "lmin": [str(value) for value in subset_x],
            })
    if z_tight != tuple(sorted((*TOP_ROWS, *AUXILIARY_ROWS))):
        raise AssertionError(("PXC88 z-tight menu changed", z_tight))

    covers = positive_extreme_top_supports(values, z)
    if len(covers) != 1:
        raise AssertionError(("expected unique positive extreme cover", covers))
    cover = covers[0]
    if (
        cover["rows"] != TOP_ROWS
        or cover["weights"] != (F(1, 3),) * 3
        or cover["eta"] != F(1, 3)
        or cover["alpha"] != (F(1, 3), F(2, 3))
    ):
        raise AssertionError(("unique PXC88 cover changed", cover))

    reduced_constraints = {
        row: coalition_sum(X, row) for row in support_x
    }
    reduced_constraints.update({
        row: coalition_sum(Z, row) for row in cover["rows"]
    })
    reduced_values, reduced_x, reduced_z = selector_pair(reduced_constraints)
    if (
        reduced_x != X
        or reduced_z != Z_REDUCED
        or any(reduced_values[1 << player] for player in range(N))
    ):
        raise AssertionError(("nonfaithful minimal lift changed", reduced_x, reduced_z))

    tangent = tuple(left - right for left, right in zip(Z_REDUCED, Z))
    if (
        sum(tangent, F(0))
        or tangent[:2] != (F(0), F(0))
        or tangent[2:4] != (F(-1, 7), F(-1, 7))
        or any(
            coalition_sum(tangent, row) < 0
            for row in reduced_constraints
            if coalition_sum(Z, row) == reduced_constraints[row]
        )
    ):
        raise AssertionError(("explicit later-stage tangent changed", tangent))

    one_auxiliary_lmax = []
    for retained in AUXILIARY_ROWS:
        constraints = dict(reduced_constraints)
        constraints[retained] = coalition_sum(Z, retained)
        _partial_values, partial_x, partial_z = selector_pair(constraints)
        if partial_x != X or partial_z == Z:
            raise AssertionError(("one auxiliary unexpectedly sufficed", retained, partial_z))
        one_auxiliary_lmax.append(partial_z)

    repaired_constraints = dict(reduced_constraints)
    repaired_constraints.update({row: coalition_sum(Z, row) for row in AUXILIARY_ROWS})
    _repaired_values, repaired_x, repaired_z = selector_pair(repaired_constraints)
    if repaired_x != X or repaired_z != Z:
        raise AssertionError(("two-row correction failed", repaired_x, repaired_z))

    _pxc90_values, pxc90_x, pxc90_z = selector_pair(dict(PXC90_CONSTRAINTS))
    if pxc90_x != X or pxc90_z != PXC90_Z:
        raise AssertionError("PXC90 full-game calibration changed")
    pxc90_reduced = {
        row: coalition_sum(X, row) for row in LMIN_ROWS
    }
    pxc90_reduced.update({row: coalition_sum(PXC90_Z, row) for row in PXC90_TOP_ROWS})
    _pxc90_minimal_values, pxc90_minimal_x, pxc90_minimal_z = selector_pair(
        pxc90_reduced
    )
    if pxc90_minimal_x != X or pxc90_minimal_z != PXC90_Z:
        raise AssertionError("PXC90 stopped being a faithful positive calibration")

    payload = {
        "claim": "exact refutation of the faithful sparse-lift conjecture PXC91c",
        "dimension": N,
        "full_lmin": [str(value) for value in x],
        "full_lmax": [str(value) for value in z],
        "singleton_normalized": True,
        "ordered_saturated_single_heavy_s2": True,
        "frozen_domain_role_count": {
            "root": 1,
            "gainers": len(roots[0][1]),
            "outsiders": len(roots[0][2]),
        },
        "packet_margin": str(packet_margin),
        "direct_packet_exists": False,
        "complete_lmin_support": list(support_x),
        "every_proper_lmin_row_subset_changes_lmin": True,
        "proper_lmin_row_subset_selectors": proper_subset_lmins,
        "all_proper_nonsingleton_z_tight_rows": list(z_tight),
        "positive_extreme_top_cover_count": 1,
        "unique_top_cover": {
            "rows": list(cover["rows"]),
            "weights": [str(value) for value in cover["weights"]],
            "eta": str(cover["eta"]),
            "alpha": [str(value) for value in cover["alpha"]],
        },
        "minimal_lift_lmin": [str(value) for value in reduced_x],
        "minimal_lift_lmax": [str(value) for value in reduced_z],
        "later_stage_improving_tangent": [str(value) for value in tangent],
        "indispensable_auxiliary_rows": list(AUXILIARY_ROWS),
        "one_auxiliary_lmax": [
            [str(value) for value in point] for point in one_auxiliary_lmax
        ],
        "two_auxiliary_rows_restore_both_selectors": True,
        "pxc90_faithful_positive_calibration": True,
        "scope": (
            "refutes PXC91c at an exact seven-player game; it does not prove "
            "that seven is the minimum possible dimension"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
