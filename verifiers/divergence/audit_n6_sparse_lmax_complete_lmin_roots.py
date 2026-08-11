#!/usr/bin/env python3
"""Exact n=6 premise ablation for the rooted hybrid-overlap bridge.

For every archived pair, retain a complete staged Lmin support but only the
support of one sparse first-stage Lmax over-cover.  At every player maximizing
the coordinatewise overlap, minimize the hybrid overlap in the resulting
three-generator (x,z,w^r) relaxation.  Repeat after deleting every Lmax row
except coalitions shared with the complete Lmin support, and replay one exact
negative control with all Lmax rows deleted.

The specialized three-generator LP below is formulated independently of the
general labelled-branch constructor.  Every optimum is cross-checked against
that constructor.  This remains a finite archive regression, not an all-n
proof and not an exhaustive theorem for n=6.
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

from exactlp import exact_linprog  # noqa: E402

from audit_lmax_overcover import coalition_sum, records, top_certificate  # noqa: E402
from audit_n6_equality_one_witness_roots import stage_support  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from verify_labelled_branch_duals import branch_system, one_witness_minimum  # noqa: E402


def complete_lmin_support(values, x):
    support = set()
    for stage, block in enumerate(payoff_blocks(x, "min")):
        for player in block:
            support.update(stage_support(values, x, "min", stage, player))
    return tuple(sorted(support))


def specialized_root_minimum(x, z, support_x, support_z, root):
    """Solve the sparse/full three-generator LP without branch_system()."""
    n = len(x)
    total = sum(x, F(0))
    normalized_x = tuple(q / total for q in x)
    normalized_z = tuple(q / total for q in z)
    generator_count = 3  # 0=x, 1=z, 2=w^root
    width = generator_count * n

    def index(generator, player):
        return generator * n + player

    inequalities, inequality_rhs = [], []
    equalities, equality_rhs = [], []

    for generator in range(generator_count):
        for player in range(n):
            row = [F(0)] * width
            row[index(generator, player)] = -1
            inequalities.append(row)
            inequality_rhs.append(F(0))
        row = [F(0)] * width
        for player in range(n):
            row[index(generator, player)] = 1
        equalities.append(row)
        equality_rhs.append(F(1))

    row = [F(0)] * width
    row[index(2, root)] = 1
    equalities.append(row)
    equality_rhs.append(F(0))

    for selected, support in ((0, support_x), (1, support_z)):
        for coalition in support:
            for other in range(generator_count):
                if other == selected:
                    continue
                row = [F(0)] * width
                for player in range(n):
                    if coalition >> player & 1:
                        row[index(selected, player)] += 1
                        row[index(other, player)] -= 1
                inequalities.append(row)
                inequality_rhs.append(F(0))

    for generator, point, mode in (
        (0, normalized_x, "min"),
        (1, normalized_z, "max"),
    ):
        blocks = payoff_blocks(point, mode)
        for block in blocks:
            for player in block[1:]:
                row = [F(0)] * width
                row[index(generator, player)] = 1
                row[index(generator, block[0])] = -1
                equalities.append(row)
                equality_rhs.append(F(0))
        for first, second in zip(blocks, blocks[1:]):
            row = [F(0)] * width
            if mode == "min":
                row[index(generator, first[0])] = 1
                row[index(generator, second[0])] = -1
            else:
                row[index(generator, second[0])] = 1
                row[index(generator, first[0])] = -1
            inequalities.append(row)
            inequality_rhs.append(F(0))

    sign_cut = {player for player in range(n) if normalized_z[player] > normalized_x[player]}
    for player in range(n):
        row = [F(0)] * width
        if player in sign_cut:
            row[index(0, player)] = 1
            row[index(1, player)] = -1
        else:
            row[index(1, player)] = 1
            row[index(0, player)] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))

    objective = [F(0)] * width
    for player in range(n):
        objective[index(0 if player in sign_cut else 1, player)] = 1

    status, optimum, _solution = exact_linprog(
        objective, inequalities, inequality_rhs, equalities, equality_rhs
    )
    if status != "optimal":
        raise AssertionError(f"specialized root LP returned {status}")
    return optimum


def audit_record(source, trail, values, x, z):
    n = len(x)
    total = sum(x, F(0))
    if total <= 0 or total != sum(z, F(0)):
        raise AssertionError("invalid common total")
    full = (1 << n) - 1
    for point in (x, z):
        if any(q < 0 for q in point):
            raise AssertionError("negative core coordinate")
        if any(coalition_sum(point, coalition) < values[coalition] for coalition in range(1, full)):
            raise AssertionError("archived selection is not in the core")

    support_x = complete_lmin_support(values, x)
    overcover = top_certificate(values, z)
    support_z = tuple(overcover["support"])
    if not support_z or len(support_z) > n:
        raise AssertionError("Lmax over-cover is not nonempty and sparse")
    if any(coalition_sum(z, coalition) != values[coalition] for coalition in support_z):
        raise AssertionError("Lmax over-cover support is not z-tight")

    coordinate_overlap = tuple(min(x[i], z[i]) for i in range(n))
    roots = tuple(
        i for i, value in enumerate(coordinate_overlap) if value == max(coordinate_overlap)
    )
    case = {
        "x": x,
        "z": z,
        "g": (total,) + (F(0),) * (n - 1),
        "support_x": support_x,
        "support_z": support_z,
    }
    general_system = branch_system(case)
    common_support = tuple(sorted(set(support_x).intersection(support_z)))
    bounds = []
    common_hinge_bounds = []
    for root in roots:
        specialized = specialized_root_minimum(x, z, support_x, support_z, root)
        general = one_witness_minimum(general_system, root)
        if specialized != general:
            raise AssertionError(
                f"independent LP mismatch at {source.name} {trail} root {root}: "
                f"{specialized} != {general}"
            )
        bounds.append(specialized)
        common_hinge_bounds.append(
            specialized_root_minimum(x, z, support_x, common_support, root)
        )

    target = F(2, 3)
    if any(bound < target for bound in bounds):
        raise AssertionError(f"sparse/full rooted bound failed at {source.name} {trail}")
    if any(bound < target for bound in common_hinge_bounds):
        raise AssertionError(f"common-hinge rooted bound failed at {source.name} {trail}")
    no_lmax_bounds = None
    if source.name == "harvest6_602.json" and trail == "$.records[82]":
        no_lmax_bounds = tuple(
            specialized_root_minimum(x, z, support_x, (), root) for root in roots
        )
        if no_lmax_bounds != (F(5, 8),):
            raise AssertionError("no-Lmax negative control changed")
        if tuple(bounds) != (F(3, 4),) or tuple(common_hinge_bounds) != (F(3, 4),):
            raise AssertionError("common-hinge repair control changed")
    return {
        "source": source.name,
        "trail": trail,
        "roots": roots,
        "bounds": tuple(bounds),
        "common_hinge_bounds": tuple(common_hinge_bounds),
        "actual_overlap": sum(coordinate_overlap, F(0)) / total,
        "lmin_support_size": len(support_x),
        "lmax_overcover_support_size": len(support_z),
        "common_hinge_support_size": len(common_support),
        "no_lmax_bounds": no_lmax_bounds,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for source in args.paths:
        data = json.loads(source.read_text())
        for parsed_source, trail, values, x, z in records(data, source):
            if len(x) == 6:
                rows.append(audit_record(parsed_source, trail, values, x, z))
    if len(rows) != 374:
        raise AssertionError(f"expected 374 archived n=6 pairs, found {len(rows)}")

    bounds = [bound for row in rows for bound in row["bounds"]]
    common_hinge_bounds = [
        bound for row in rows for bound in row["common_hinge_bounds"]
    ]
    target = F(2, 3)
    report = {
        "status": "exact rational premise-ablation audit; no sparse-Lmax/full-Lmin root failures",
        "archive_records": len(rows),
        "exact_root_lps": len(bounds),
        "independent_encoding_agreements": len(bounds),
        "failures": 0,
        "minimum_root_bound": str(min(bounds)),
        "sharp_target": str(target),
        "root_bound_distribution": dict(
            sorted(Counter(str(bound) for bound in bounds).items())
        ),
        "common_hinge_exact_root_lps": len(common_hinge_bounds),
        "common_hinge_failures": 0,
        "minimum_common_hinge_root_bound": str(min(common_hinge_bounds)),
        "common_hinge_root_bound_distribution": dict(
            sorted(Counter(str(bound) for bound in common_hinge_bounds).items())
        ),
        "maximum_complete_lmin_support_size": max(
            row["lmin_support_size"] for row in rows
        ),
        "maximum_sparse_lmax_overcover_support_size": max(
            row["lmax_overcover_support_size"] for row in rows
        ),
        "maximum_common_hinge_support_size": max(
            row["common_hinge_support_size"] for row in rows
        ),
        "records_with_empty_common_hinge_support": sum(
            row["common_hinge_support_size"] == 0 for row in rows
        ),
        "records_with_some_floor_root": sum(
            any(bound == target for bound in row["bounds"]) for row in rows
        ),
        "records_where_every_tested_root_matches_actual_overlap": sum(
            all(bound == row["actual_overlap"] for bound in row["bounds"])
            for row in rows
        ),
        "no_lmax_negative_control": {
            "source": "harvest6_602.json",
            "trail": "$.records[82]",
            "actual_overlap": "7/9",
            "no_lmax_root_bound": "5/8",
            "common_hinge_root_bound": "3/4",
            "sparse_lmax_root_bound": "3/4",
            "common_coalition": 35,
        },
        "scope": (
            "374 archived n=6 pairs; one extracted complete staged Lmin support and "
            "one exact sparse first-stage Lmax over-cover per pair; every maximum-overlap "
            "root; both the full sparse support and only its intersection with the Lmin "
            "support; finite regression evidence only, not a domain theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
