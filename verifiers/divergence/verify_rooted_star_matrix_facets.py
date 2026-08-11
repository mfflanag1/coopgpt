#!/usr/bin/env python3
"""Exact matrix criterion for saturated rooted-star facet systems.

For n players, remove the exceptional root from n-1 positive coalitions that
all contain it.  Their incidence columns form a square 0/1 matrix A.  This
script checks the closed inverse-matrix decomposition criterion proved in the
research note, compares it with the primary exact-LP counts, and replays a
finite sharp-family grid.  The general criterion is a human theorem; the
finite rows below are exact arithmetic bug audits.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve().parent


def inverse(matrix):
    n = len(matrix)
    rows = [list(map(F, row)) + [F(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None:
            raise AssertionError("root-deleted incidence matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [q / scale for q in rows[column]]
        for i in range(n):
            if i == column or not rows[i][column]:
                continue
            scale = rows[i][column]
            rows[i] = [a - scale * b for a, b in zip(rows[i], rows[column])]
    return [row[n:] for row in rows]


def determinant(matrix):
    rows = [list(map(F, row)) for row in matrix]
    det = F(1)
    for column in range(len(rows)):
        pivot = next((i for i in range(column, len(rows)) if rows[i][column]), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            det = -det
        scale = rows[column][column]
        det *= scale
        rows[column] = [q / scale for q in rows[column]]
        for i in range(column + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [a - scale * b for a, b in zip(rows[i], rows[column])]
    return det


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), F(0)) for row in matrix]


def rooted_star_audit(n, root, positive_support, expected_count=None):
    players = [i for i in range(n) if i != root]
    if len(positive_support) != n - 1:
        raise AssertionError("rooted-star system is not saturated")
    if not all(coalition >> root & 1 for coalition in positive_support):
        raise AssertionError("positive support is not rooted-star")
    matrix = [
        [F(coalition >> player & 1) for coalition in positive_support]
        for player in players
    ]
    inv = inverse(matrix)
    weights = matvec(inv, [F(1)] * (n - 1))
    if any(weight <= 0 for weight in weights):
        raise AssertionError("rooted-star balanced weights are not strictly positive")
    exceptional_weight = sum(weights, F(0)) - 1
    if exceptional_weight <= 0:
        raise AssertionError("rooted-star root is not a negative exceptional column")

    full = (1 << n) - 1
    support = set(positive_support) | {1 << root}
    decompositions = []
    strict_gaps = []
    for exceptional in range(1, full):
        if exceptional in support:
            continue
        b = [F(exceptional >> player & 1) for player in players]
        beta = F(exceptional >> root & 1)
        u = matvec(inv, b)
        lower = max(-u[j] / weights[j] for j in range(n - 1))
        upper = (beta - sum(u, F(0))) / exceptional_weight
        gap = lower - upper
        if gap <= 0:
            decompositions.append(
                {
                    "new_exceptional": exceptional,
                    "lower": str(lower),
                    "upper": str(upper),
                }
            )
        else:
            strict_gaps.append(gap)
    if expected_count is not None and len(decompositions) != expected_count:
        raise AssertionError((root, positive_support, len(decompositions), expected_count))
    return {
        "n": n,
        "root": root,
        "positive_support": list(positive_support),
        "root_deleted_matrix": [[str(q) for q in row] for row in matrix],
        "determinant": str(determinant(matrix)),
        "inverse": [[str(q) for q in row] for row in inv],
        "balanced_weights": [str(q) for q in weights],
        "exceptional_root_weight": str(exceptional_weight),
        "tested_new_exceptional_coalitions": (full - 1) - len(support),
        "decomposition_count": len(decompositions),
        "indecomposable": not decompositions,
        "minimum_strict_gap": str(min(strict_gaps)) if strict_gaps else None,
        "strict_gap_distribution": dict(
            sorted(Counter(str(q) for q in strict_gaps).items())
        ),
        "first_decomposition": decompositions[0] if decompositions else None,
    }


def sharp_support(p, k):
    n = 1 + p + k
    root = 0
    outside = tuple(range(1, p + 1))
    block = tuple(range(p + 1, n))
    positive = []
    for player in outside:
        positive.append((1 << root) | (1 << player))
    for omitted in block:
        coalition = 1 << root
        for player in block:
            if player != omitted:
                coalition |= 1 << player
        positive.append(coalition)
    return n, root, tuple(positive)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=HERE / "mixed_witness_projection.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    primary = json.loads(args.input.read_text())
    extracted = []
    for case in primary["cases"]:
        for root in case["roots"]:
            for cut_number, cut in enumerate(root["cuts"], start=1):
                shear = cut["rooted_pair_shear"]
                positive = tuple(
                    row["coalition"]
                    for row in shear["completion"]
                    if not row["coefficient"].startswith("-")
                )
                if len(positive) != case["n"] - 1:
                    continue
                if not all(coalition >> root["root"] & 1 for coalition in positive):
                    continue
                audit = rooted_star_audit(
                    case["n"],
                    root["root"],
                    positive,
                    shear["decomposition_count"],
                )
                emitted_weights = {
                    row["coalition"]: F(row["coefficient"])
                    for row in shear["completion"]
                }
                if [emitted_weights[coalition] for coalition in positive] != [
                    F(q) for q in audit["balanced_weights"]
                ]:
                    raise AssertionError("inverse-matrix and emitted weights differ")
                audit.update(
                    {
                        "case": case["name"],
                        "cut": cut_number,
                        "exact_lp_count_agreement": True,
                    }
                )
                extracted.append(audit)
    mixed = [row for row in extracted if row["case"] == "optimized_label_free_spectral_failure"]
    if len(mixed) != 1 or not mixed[0]["indecomposable"]:
        raise AssertionError("mixed rooted-star facet control changed")

    sharp_grid = []
    for p in range(1, 6):
        for k in range(2, 7):
            n, root, positive = sharp_support(p, k)
            audit = rooted_star_audit(n, root, positive, 0)
            sharp_grid.append(
                {
                    "p": p,
                    "k": k,
                    "n": n,
                    "balanced_weights": audit["balanced_weights"],
                    "exceptional_root_weight": audit["exceptional_root_weight"],
                    "decomposition_count": audit["decomposition_count"],
                    "indecomposable": audit["indecomposable"],
                }
            )
    report = {
        "status": "exact saturated rooted-star inverse-matrix facet criterion",
        "criterion": (
            "for u=A^{-1}b, decomposition at exceptional (beta,b) exists iff "
            "max_j(-u_j/lambda_j) <= (beta-1.u)/(1.lambda-1)"
        ),
        "extracted_saturated_systems": extracted,
        "all_primary_counts_agree": all(row["exact_lp_count_agreement"] for row in extracted),
        "mixed_facet_identified": True,
        "sharp_family_finite_grid": sharp_grid,
        "sharp_grid_is_bug_audit_not_proof": True,
        "scope": (
            "human criterion characterizes saturated rooted-star systems in every "
            "dimension; emitted rows are finite exact controls"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
