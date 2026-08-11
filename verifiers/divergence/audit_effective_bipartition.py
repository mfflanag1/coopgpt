#!/usr/bin/env python3
"""Exact controls for the clipped effective-bipartition conjecture.

For a nonuniform Lmax point let theta be the minimum maximum load in a
first-stage top over-cover and put

    a = min(1/theta, floor(n/2)).

The candidate inequality is

    overlap/T >= 1/a + 1/(n-a).

This script audits actual selected pairs only.  Passing finite archives is
not a proof.  It also records the n=5 failures and an exact n=6 branch showing
that the stronger record-specific bound is not implied by the one-witness
common-hinge relaxation, even though the fully exactified branch preserves
the candidate after its dispersion changes.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from audit_lmax_overcover import coalition_sum, records, top_certificate  # noqa: E402
from audit_n6_equality_one_witness_roots import stage_support  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import complete_lmin_support  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from verify_labelled_branch_duals import (  # noqa: E402
    CASES,
    branch_system,
    one_witness_minimum,
)


def characteristic_function(g, h):
    n = len(g)
    return tuple(
        min(coalition_sum(g, coalition), coalition_sum(h, coalition))
        for coalition in range(1 << n)
    )


def evaluate(values, x, z):
    n = len(x)
    total = sum(x, F(0))
    if total <= 0 or total != sum(z, F(0)):
        raise AssertionError("invalid common total")
    overlap = sum((min(x[i], z[i]) for i in range(n)), F(0)) / total
    if len(set(z)) == 1:
        return {
            "overlap": overlap,
            "theta": None,
            "a_max": F(n),
            "a_clipped": F(n // 2),
            "unclipped_bound": F(1),
            "clipped_bound": F(n, (n // 2) * (n - n // 2)),
        }
    certificate = top_certificate(values, z)
    a_max = 1 / certificate["theta"]
    if not (F(0) < a_max < n):
        raise AssertionError("nonuniform effective mass is outside (0,n)")
    a = min(a_max, F(n // 2))
    return {
        "overlap": overlap,
        "theta": certificate["theta"],
        "a_max": a_max,
        "a_clipped": a,
        "unclipped_bound": 1 / a_max + 1 / (F(n) - a_max),
        "clipped_bound": 1 / a + 1 / (F(n) - a),
        "support": certificate["support"],
    }


def n6_archive(paths):
    rows = []
    for source in paths:
        data = json.loads(source.read_text())
        for parsed_source, trail, values, x, z in records(data, source):
            if len(x) == 6:
                rows.append((parsed_source, trail, evaluate(values, x, z)))
    if len(rows) != 374:
        raise AssertionError(f"expected 374 archived n=6 pairs, found {len(rows)}")
    clipped_failures = [row for row in rows if row[2]["overlap"] < row[2]["clipped_bound"]]
    unclipped_failures = [row for row in rows if row[2]["overlap"] < row[2]["unclipped_bound"]]
    if clipped_failures:
        raise AssertionError("clipped effective-bipartition audit failed")
    expected_unclipped = {
        ("harvest6_602.json", "$.records[119]"),
        ("harvest6_602.json", "$.records[158]"),
    }
    found_unclipped = {(row[0].name, row[1]) for row in unclipped_failures}
    if found_unclipped != expected_unclipped:
        raise AssertionError(f"unclipped failure set changed: {found_unclipped}")
    return {
        "records": len(rows),
        "clipped_failures": 0,
        "minimum_clipped_margin": str(
            min(row[2]["overlap"] - row[2]["clipped_bound"] for row in rows)
        ),
        "unclipped_failures": [
            {
                "source": row[0].name,
                "trail": row[1],
                "overlap": str(row[2]["overlap"]),
                "unclipped_bound": str(row[2]["unclipped_bound"]),
                "a_max": str(row[2]["a_max"]),
            }
            for row in unclipped_failures
        ],
    }


def n5_boundary(path):
    seen, rows = set(), []
    for source in sorted(path.rglob("*.json")):
        try:
            data = json.loads(source.read_text())
        except json.JSONDecodeError:
            continue
        for parsed_source, trail, values, x, z in records(data, source):
            if len(x) != 5 or sum(x, F(0)) <= 0 or sum(x, F(0)) != sum(z, F(0)):
                continue
            key = (values, x, z)
            if key in seen:
                continue
            seen.add(key)
            rows.append((parsed_source, trail, evaluate(values, x, z)))
    failures = [row for row in rows if row[2]["overlap"] < row[2]["clipped_bound"]]
    if len(rows) != 124 or len(failures) != 12:
        raise AssertionError(f"n=5 boundary counts changed: {len(rows)}, {len(failures)}")
    worst = min(failures, key=lambda row: row[2]["overlap"] - row[2]["clipped_bound"])
    if worst[2]["overlap"] != F(3, 4) or worst[2]["clipped_bound"] != F(5, 6):
        raise AssertionError("n=5 extremal boundary changed")
    return {
        "distinct_records": len(rows),
        "failures": len(failures),
        "worst_margin": str(worst[2]["overlap"] - worst[2]["clipped_bound"]),
        "worst_overlap": str(worst[2]["overlap"]),
        "worst_bound": str(worst[2]["clipped_bound"]),
        "interpretation": "the candidate is deliberately an n>=6 statement",
    }


def hostile_cases():
    rows = []
    for case in CASES:
        g = tuple(map(F, case["g"]))
        h = tuple(map(F, case["h"]))
        values = characteristic_function(g, h)
        result = evaluate(values, tuple(case["x"]), tuple(case["z"]))
        if result["overlap"] < result["clipped_bound"]:
            raise AssertionError(f"hostile control failed: {case['name']}")
        rows.append(
            {
                "name": case["name"],
                "n": len(case["x"]),
                "overlap": str(result["overlap"]),
                "theta": str(result["theta"]),
                "a_clipped": str(result["a_clipped"]),
                "bound": str(result["clipped_bound"]),
                "margin": str(result["overlap"] - result["clipped_bound"]),
            }
        )

    g = tuple(map(F, (0, 5, 0, 3, 2, 0, 0)))
    h = tuple(map(F, (1, 0, 2, 0, 0, 5, 2)))
    x = tuple(map(F, (1, 2, 1, 1, 1, 3, 1)))
    z = (F(5, 6), F(5, 2), F(5, 6), F(4, 3), F(7, 6), F(5, 2), F(5, 6))
    result = evaluate(characteristic_function(g, h), x, z)
    if result["overlap"] < result["clipped_bound"]:
        raise AssertionError("nonuniform n=7 control failed")
    rows.append(
        {
            "name": "nonuniform_generator_majorization_control",
            "n": 7,
            "overlap": str(result["overlap"]),
            "theta": str(result["theta"]),
            "a_clipped": str(result["a_clipped"]),
            "bound": str(result["clipped_bound"]),
            "margin": str(result["overlap"] - result["clipped_bound"]),
        }
    )
    return rows


def complete_lmax_support(values, z):
    support = set()
    for stage, block in enumerate(payoff_blocks(z, "max")):
        for player in block:
            support.update(stage_support(values, z, "max", stage, player))
    return tuple(sorted(support))


def branch_boundary(path):
    data = json.loads(path.read_text())
    selected = None
    for source, trail, values, x, z in records(data, path):
        if trail == "$.records[13]":
            selected = (values, x, z)
            break
    if selected is None:
        raise AssertionError("record 13 not found")
    values, x, z = selected
    original = evaluate(values, x, z)
    if original["overlap"] != F(13, 17) or original["clipped_bound"] != F(3, 4):
        raise AssertionError("record 13 changed")

    support_x = complete_lmin_support(values, x)
    support_z = complete_lmax_support(values, z)
    total = sum(x, F(0))
    common = tuple(sorted(set(support_x).intersection(original["support"])))
    common_case = {
        "x": x,
        "z": z,
        "g": (total,) + (F(0),) * 5,
        "support_x": support_x,
        "support_z": common,
    }
    coordinate_overlap = tuple(min(x[i], z[i]) for i in range(6))
    roots = tuple(i for i, q in enumerate(coordinate_overlap) if q == max(coordinate_overlap))
    common_system = branch_system(common_case)
    common_bounds = tuple(one_witness_minimum(common_system, root) for root in roots)
    if common_bounds != (F(2, 3), F(2, 3)):
        raise AssertionError("record 13 common-hinge boundary changed")

    full_case = dict(common_case)
    full_case["support_z"] = support_z
    system = branch_system(full_case)
    status, optimum, solution = exact_linprog(
        system["objective"],
        system["inequalities"],
        system["inequality_rhs"],
        system["equalities"],
        system["equality_rhs"],
    )
    if status != "optimal" or optimum != F(2, 3):
        raise AssertionError("record 13 full branch optimum changed")
    n = 6
    generators = tuple(
        tuple(solution[generator * n + player] for player in range(n))
        for generator in range(n + 2)
    )
    generated_values = tuple(
        min(coalition_sum(generator, coalition) for generator in generators)
        for coalition in range(1 << n)
    )
    generated = evaluate(generated_values, generators[0], generators[1])
    if generated["overlap"] != F(2, 3) or generated["theta"] != F(1, 3):
        raise AssertionError("record 13 exactified minimizer changed")
    if generated["overlap"] != generated["clipped_bound"]:
        raise AssertionError("exactified minimizer does not preserve candidate equality")
    return {
        "source": path.name,
        "trail": "$.records[13]",
        "original_overlap": str(original["overlap"]),
        "original_theta": str(original["theta"]),
        "original_candidate_bound": str(original["clipped_bound"]),
        "common_hinge_one_witness_bounds": [str(q) for q in common_bounds],
        "fully_exactified_branch_minimum": str(optimum),
        "minimizer_recomputed_theta": str(generated["theta"]),
        "minimizer_recomputed_candidate_bound": str(generated["clipped_bound"]),
        "lesson": (
            "the record-specific candidate is stronger than the one-witness reduction, "
            "but full exactification moves theta and preserves candidate equality"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n6_paths", nargs=2, type=Path)
    parser.add_argument("--n5-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact finite controls for the clipped effective-bipartition conjecture",
        "formula": "O/T >= 1/a + 1/(n-a), a=min(1/theta_plus,floor(n/2))",
        "n6_archive": n6_archive(args.n6_paths),
        "n5_boundary": n5_boundary(args.n5_dir),
        "hostile_controls": hostile_cases(),
        "full_branch_boundary": branch_boundary(args.n6_paths[0]),
        "scope": (
            "actual selected pairs from finite archives and named exact controls; discovery "
            "and falsification evidence only, not a proof for n>=6"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
