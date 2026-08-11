#!/usr/bin/env python3
r"""Exact falsification audit of gauge-invariant facet affordability.

This is finite archive evidence only.  The human identity behind the audit is

  K delta - Q = sum_S (|S\{r}|+K) u_S - [(n-1)+K],

for a rooted fractional packing u, delta=sum(u)-1, Q the total uncovered
nonroot load, and K=floor(n^2/4)-n+1.  Removing rooted-pair packing mass t
preserves the completed exact-cone row but sends

  (delta,Q,K delta-Q) -> (delta-t,Q+t,K delta-Q-(K+1)t).

Thus affordability belongs to a marked packing decomposition, not to the
completed facet normal.  The archive audit below measures the information
lost by the canonical rooted-pair gauge quotient.
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

from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_n6_positive_residual_facet_atlas import (  # noqa: E402
    one_witness_system,
    packing_facet,
)
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
    specialized_root_minimum,
)
from exactlp import exact_linprog  # noqa: E402
from verify_labelled_branch_duals import branch_system  # noqa: E402


def gauge_fixed_gate(support: tuple[int, ...], root: int, n: int) -> dict:
    root_mask = 1 << root
    # This is the canonical facet-enumeration gauge, not a price-preserving gauge.
    menu = tuple(
        coalition
        for coalition in support
        if coalition & root_mask and coalition.bit_count() >= 3
    )
    if not menu:
        return {"menu_size": 0, "margin": str(-(n - 1)), "delta_on_top_face": "-1", "affordable": False}
    nonroots = tuple(player for player in range(n) if player != root)
    dimensional_price = (n * n // 4) - n + 1
    weights = [coalition.bit_count() - 1 + dimensional_price for coalition in menu]
    aub = [
        [F((coalition >> player) & 1) for coalition in menu]
        for player in nonroots
    ]
    bub = [F(1)] * len(nonroots)
    for index in range(len(menu)):
        aub.append([F(-1 if column == index else 0) for column in range(len(menu))])
        bub.append(F(0))
    status, optimum, _solution = exact_linprog([-weight for weight in weights], aub, bub)
    if status != "optimal":
        raise AssertionError((root, "affordable packing LP", status))
    top_value = -optimum
    threshold = F(n - 1 + dimensional_price)
    margin = top_value - threshold
    status, delta_objective, solution = exact_linprog(
        [F(-1)] * len(menu),
        aub,
        bub,
        [[F(weight) for weight in weights]],
        [top_value],
    )
    if status != "optimal":
        raise AssertionError((root, "top-face root-excess LP", status))
    delta = -delta_objective - 1
    loads = [
        sum(
            (solution[index] for index, coalition in enumerate(menu) if coalition >> player & 1),
            F(0),
        )
        for player in nonroots
    ]
    q_total = sum((1 - load for load in loads), F(0))
    if margin != dimensional_price * delta - q_total:
        raise AssertionError("affordable packing identity failed")
    return {
        "menu_size": len(menu),
        "margin": str(margin),
        "delta_on_top_face": str(delta),
        "q_on_top_face": str(q_total),
        "affordable": margin > 0 or (margin == 0 and delta > 0),
    }


def best_admissible_marking(
    pair_lift: dict[str, str], support_x: tuple[int, ...], root: int, n: int
) -> dict:
    """Maximize price margin over pair origins allowed by x-tightness."""
    root_mask = 1 << root
    coefficients = {int(mask): F(value) for mask, value in pair_lift.items()}
    positive = {
        coalition: coefficient
        for coalition, coefficient in coefficients.items()
        if coefficient > 0
    }
    if any(not coalition & root_mask for coalition in positive):
        raise AssertionError("best-marking input is not rooted")
    tight = set(support_x)
    eligible_pair_mass = sum(
        (
            coefficient
            for coalition, coefficient in positive.items()
            if coalition.bit_count() == 2 and coalition in tight
        ),
        F(0),
    )
    deficit_mass = sum(
        (
            coefficient
            for coalition, coefficient in positive.items()
            if coalition.bit_count() == 2 and coalition not in tight
        ),
        F(0),
    )
    nonpair_packing_mass = sum(
        (
            coefficient
            for coalition, coefficient in positive.items()
            if coalition.bit_count() >= 3
        ),
        F(0),
    )
    delta = nonpair_packing_mass + eligible_pair_mass - 1
    dimensional_price = (n * n // 4) - n + 1
    margin = dimensional_price * delta - deficit_mass
    return {
        "eligible_rooted_pair_mass": str(eligible_pair_mass),
        "forced_deficit_mass": str(deficit_mass),
        "root_excess": str(delta),
        "margin": str(margin),
        "affordable": margin >= 0 and delta > 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    counts = Counter()
    failures = []
    positive_residual_rows = []
    target = F(2, 3)
    for path in args.paths:
        data = json.loads(path.read_text())
        for _source, trail, values, x, z in records(data, path):
            if len(x) != 6:
                continue
            counts["records"] += 1
            support = complete_lmin_support(values, x)
            overlap_coordinates = tuple(min(a, b) for a, b in zip(x, z))
            roots = tuple(
                index
                for index, value in enumerate(overlap_coordinates)
                if value == max(overlap_coordinates)
            )
            gates = tuple(gauge_fixed_gate(support, root, 6) for root in roots)
            counts["maximum_overlap_roots"] += len(roots)
            counts["affordable_roots"] += sum(gate["affordable"] for gate in gates)
            if all(gate["affordable"] for gate in gates):
                counts["records_all_roots_affordable"] += 1
            if any(gate["affordable"] for gate in gates):
                counts["records_some_root_affordable"] += 1
            else:
                failures.append({
                    "source": path.name,
                    "trail": trail,
                    "roots": list(roots),
                    "gates": list(gates),
                })

            total = sum(x, F(0))
            floor = min(x)
            ceiling = max(z)
            direct = has_direct_packet(x, z, target)
            interpolation = ceiling - floor + total * floor / ceiling >= target * total
            if not direct and not interpolation and floor > 0:
                counts["positive_floor_residual_records"] += 1
                if any(gate["affordable"] for gate in gates):
                    counts["positive_residual_some_root_affordable"] += 1
                positive_residual_rows.append({
                    "source": path.name,
                    "trail": trail,
                    "roots": list(roots),
                    "gates": list(gates),
                })

    staged_rows = []
    for path in args.paths:
        data = json.loads(path.read_text())
        for _source, trail, values, x, z in records(data, path):
            if len(x) != 6:
                continue
            total, floor, ceiling = sum(x, F(0)), min(x), max(z)
            if (
                has_direct_packet(x, z, target)
                or ceiling - floor + total * floor / ceiling >= target * total
                or floor == 0
            ):
                continue
            root = next(i for i in range(6) if z[i] == ceiling and x[i] >= ceiling)
            support_x = complete_lmin_support(values, x)
            lmin_only_bound = specialized_root_minimum(x, z, support_x, (), root)
            if lmin_only_bound < target:
                continue
            case = {
                "x": x,
                "z": z,
                "g": (total,) + (F(0),) * 5,
                "support_x": support_x,
                "support_z": (),
            }
            reduced, optimum = one_witness_system(branch_system(case), root)
            facet = packing_facet(reduced, root, optimum)
            delta = F(facet["root_excess"])
            q_total = sum((F(value) for value in facet["deficits"]), F(0))
            pair_mass = sum(
                (
                    F(weight)
                    for coalition, weight in facet["packing"].items()
                    if int(coalition) & (1 << root) and int(coalition).bit_count() == 2
                ),
                F(0),
            )
            dimensional_price = 4
            margin = dimensional_price * delta - q_total
            deleted_marked_margin = margin - (dimensional_price + 1) * pair_mass
            gate = gauge_fixed_gate(support_x, root, 6)
            best_marking = best_admissible_marking(
                facet["pair_lift"], support_x, root, 6
            )
            if F(best_marking["margin"]) < margin:
                raise AssertionError("best admissible marking underperforms staged marking")
            if F(gate["margin"]) < deleted_marked_margin:
                raise AssertionError("canonical gate underperforms the deleted marked packing")
            staged_rows.append(
                {
                    "source": path.name,
                    "trail": trail,
                    "root": root,
                    "root_excess": str(delta),
                    "q_total": str(q_total),
                    "effective_price": str(q_total / delta),
                    "marked_margin": str(margin),
                    "rooted_pair_packing_mass": str(pair_mass),
                    "deleted_marked_margin": str(deleted_marked_margin),
                    "best_gauge_fixed_margin": gate["margin"],
                    "gauge_fixed_affordable": gate["affordable"],
                    "best_admissible_marking": best_marking,
                }
            )
    if len(staged_rows) != 13:
        raise AssertionError(f"expected 13 staged Lmin-only rows, found {len(staged_rows)}")
    if any(F(row["marked_margin"]) < 0 for row in staged_rows):
        raise AssertionError("a staged Lmin-only row is not target-priced")
    report = {
        "status": "exact finite marked-affordability and gauge-loss audit",
        **dict(counts),
        "records_with_no_affordable_maximum_overlap_root": len(failures),
        "first_failures": failures[:5],
        "positive_floor_residual_rows": positive_residual_rows,
        "staged_lmin_only_rows": staged_rows,
        "staged_lmin_only_affordable": sum(
            F(row["marked_margin"]) >= 0 for row in staged_rows
        ),
        "staged_rows_still_affordable_after_gauge_fixing": sum(
            row["gauge_fixed_affordable"] for row in staged_rows
        ),
        "staged_rows_losing_affordability_under_gauge_fixing": sum(
            not row["gauge_fixed_affordable"] for row in staged_rows
        ),
        "facets_with_affordable_best_admissible_marking": sum(
            row["best_admissible_marking"]["affordable"] for row in staged_rows
        ),
        "scope": (
            "374 archived n=6 pairs and one extracted complete staged Lmin support; "
            "the 13 Lmin-only residual duals are replayed in their marked packing "
            "gauge; finite falsification evidence, not a domain theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
