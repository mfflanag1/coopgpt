#!/usr/bin/env python3
"""Exact facet atlas for the positive-floor n=6 residual root packets.

This is a finite structural audit, not a six-player completeness theorem.  It
extracts the witness-packing component of one exact Farkas dual for each of
the thirteen residual rows closed without Lmax support, applies the rooted
pair shear, and runs the Studeny--Kratochvil exceptional-set test.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
    specialized_root_minimum,
)
from exactlp import exact_linprog  # noqa: E402
from verify_labelled_branch_duals import branch_system, exact_dual  # noqa: E402
from verify_rooted_hinge_projection import (  # noqa: E402
    decomposition_witnesses,
    matrix_rank,
)


def one_witness_system(system: dict, root: int) -> tuple[dict, F]:
    n = system["n"]
    witness = 2 + root
    allowed = {0, 1, witness}
    columns = [generator * n + player for generator in sorted(allowed) for player in range(n)]
    inequality_rows = []
    for index, label in enumerate(system["inequality_labels"]):
        if label[0] == "nonnegative" and label[1] not in allowed:
            continue
        if label[0] == "tight" and label[3] not in allowed:
            continue
        inequality_rows.append(index)
    equality_rows = []
    for index, label in enumerate(system["equality_labels"]):
        if label[0] == "total" and label[1] not in allowed:
            continue
        if label[0] == "witness_zero" and label[1] != root:
            continue
        equality_rows.append(index)
    reduced = {
        "n": n,
        "inequalities": [
            [system["inequalities"][row][column] for column in columns]
            for row in inequality_rows
        ],
        "inequality_rhs": [system["inequality_rhs"][row] for row in inequality_rows],
        "inequality_labels": [system["inequality_labels"][row] for row in inequality_rows],
        "equalities": [
            [system["equalities"][row][column] for column in columns]
            for row in equality_rows
        ],
        "equality_rhs": [system["equality_rhs"][row] for row in equality_rows],
        "equality_labels": [system["equality_labels"][row] for row in equality_rows],
        "objective": [system["objective"][column] for column in columns],
    }
    status, optimum, _solution = exact_linprog(
        reduced["objective"],
        reduced["inequalities"],
        reduced["inequality_rhs"],
        reduced["equalities"],
        reduced["equality_rhs"],
    )
    if status != "optimal":
        raise AssertionError(f"one-witness root LP returned {status}")
    return reduced, optimum


def relabel(coalition: int, mapping: dict[int, int]) -> int:
    answer = 0
    for old, new in mapping.items():
        if coalition >> old & 1:
            answer |= 1 << new
    return answer


def canonical_rooted_support(support: tuple[int, ...], root: int, n: int) -> tuple[int, ...]:
    others = [player for player in range(n) if player != root]
    signatures = []
    for images in itertools.permutations(range(1, n)):
        mapping = {root: 0, **dict(zip(others, images))}
        signatures.append(tuple(sorted(relabel(coalition, mapping) for coalition in support)))
    return min(signatures)


def packing_facet(system: dict, root: int, optimum: F) -> dict:
    inequalities, equalities = exact_dual(system, optimum)
    witness = 2 + root
    lambdas = {
        label[2]: coefficient
        for label, coefficient in inequalities
        if label[0] == "tight" and label[1] == "x" and label[3] == witness
    }
    total_prices = {
        label[1]: coefficient
        for label, coefficient in equalities
        if label[0] == "total"
    }
    tau = -total_prices.get(witness, F(0))
    if tau <= 0 or not lambdas:
        raise AssertionError("optimal root dual has no positive witness packing")
    n = system["n"]
    weights = {coalition: coefficient / tau for coalition, coefficient in lambdas.items()}
    loads = [
        sum(
            (weight for coalition, weight in weights.items() if coalition >> player & 1),
            F(0),
        )
        for player in range(n)
    ]
    if any(loads[player] > 1 for player in range(n) if player != root):
        raise AssertionError("normalized dual is not a rooted packing")
    delta = loads[root] - 1
    deficits = [F(0) if player == root else 1 - loads[player] for player in range(n)]
    coefficients = dict(weights)
    root_mask = 1 << root
    for player, deficit in enumerate(deficits):
        if player == root or deficit == 0:
            continue
        pair = root_mask | (1 << player)
        coefficients[pair] = coefficients.get(pair, F(0)) + deficit
    exceptional_weight = delta + sum(deficits, F(0))
    coefficients[root_mask] = coefficients.get(root_mask, F(0)) - exceptional_weight
    coefficients = {
        coalition: coefficient for coalition, coefficient in coefficients.items() if coefficient
    }
    incidence = [
        sum(
            (coefficient for coalition, coefficient in coefficients.items() if coalition >> player & 1),
            F(0),
        )
        for player in range(n)
    ]
    if incidence != [F(1)] * n:
        raise AssertionError("pair-lift incidence identity failed")
    negative = [coalition for coalition, coefficient in coefficients.items() if coefficient < 0]
    if negative != [root_mask]:
        raise AssertionError("pair lift lacks the unique root exception")
    support = tuple(sorted(coefficients))
    rank = matrix_rank(support, n)
    decompositions = decomposition_witnesses(support, n)
    return {
        "dual_witness_scale": str(tau),
        "packing": {str(coalition): str(weight) for coalition, weight in sorted(weights.items())},
        "root_excess": str(delta),
        "deficits": [str(value) for value in deficits],
        "pair_lift": {
            str(coalition): str(coefficient)
            for coalition, coefficient in sorted(coefficients.items())
        },
        "support_rank": rank,
        "support_size": len(support),
        "decomposition_count": len(decompositions),
        "indecomposable": rank == len(support) and not decompositions,
        "canonical_support": list(canonical_rooted_support(support, root, n)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    target = F(2, 3)
    rows = []
    for path in args.paths:
        for source, trail, values, x, z in records(json.loads(path.read_text()), path):
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
            if optimum != lmin_only_bound:
                raise AssertionError("root LP and extracted dual optimum disagree")
            rows.append(
                {
                    "source": source.name,
                    "trail": trail,
                    "root": root,
                    "root_bound": str(optimum),
                    **packing_facet(reduced, root, optimum),
                }
            )
    if len(rows) != 13:
        raise AssertionError(f"expected 13 Lmin-only positive residuals, found {len(rows)}")
    orbit_counts = Counter(tuple(row["canonical_support"]) for row in rows)
    repair_orbits = {
        "harvest6_601.json $.records[103]": (1, 3, 5, 9, 17, 33),
        "harvest6_602.json $.records[82]": (1, 3, 5, 25, 41, 51),
        "harvest6_602.json $.records[129]": (1, 3, 5, 9, 17, 33),
    }
    if any(signature not in orbit_counts for signature in repair_orbits.values()):
        raise AssertionError("a repair facet introduced an unclassified support orbit")
    combined_orbit_counts = orbit_counts.copy()
    combined_orbit_counts.update(repair_orbits.values())
    orbit_representatives = {}
    for row in rows:
        signature = ",".join(map(str, row["canonical_support"]))
        orbit_representatives.setdefault(
            signature,
            {
                "source": row["source"],
                "trail": row["trail"],
                "root": row["root"],
                "root_bound": row["root_bound"],
                "pair_lift": row["pair_lift"],
            },
        )
    report = {
        "status": "exact n=6 positive-residual rooted pair-lift facet atlas",
        "lmin_only_residual_rows": len(rows),
        "indecomposable_rows": sum(row["indecomposable"] for row in rows),
        "decomposable_rows": sum(not row["indecomposable"] for row in rows),
        "canonical_support_orbits": len(orbit_counts),
        "orbit_multiplicities": {
            ",".join(map(str, support)): count
            for support, count in sorted(orbit_counts.items())
        },
        "repair_rows": {
            row: list(signature) for row, signature in repair_orbits.items()
        },
        "all_positive_residual_rows": 16,
        "all_positive_residual_rows_carried_by_indecomposable_facets": 16,
        "combined_support_orbits": len(combined_orbit_counts),
        "combined_orbit_multiplicities": {
            ",".join(map(str, support)): count
            for support, count in sorted(combined_orbit_counts.items())
        },
        "root_bound_distribution": dict(
            sorted(Counter(row["root_bound"] for row in rows).items())
        ),
        "pair_lift_support_size_distribution": dict(
            sorted(Counter(str(row["support_size"]) for row in rows).items())
        ),
        "orbit_representatives": orbit_representatives,
        "audited_rows": [f'{row["source"]} {row["trail"]}' for row in rows],
        "scope": (
            "thirteen archived positive-floor n=6 residual branches; one exact "
            "optimal Farkas dual per row; finite facet atlas, not a domain theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
