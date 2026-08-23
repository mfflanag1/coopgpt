#!/usr/bin/env python3
"""Discovery search for complete-Cx dependence of sparse top-cover fidelity.

The base is the PXC98 six-player exact lower-envelope game.  We add rows
tight at its Lmin point and feasible at its Lmax point.  Shrinking the core
while retaining both selector points preserves both selectors, so every
singleton-normalized augmentation is again an exact calibration.  The search
then exhausts complete Cx subsets and qualifying extreme top covers, looking
for two complete certificates with different faithful-cover sets.

The completeness prefilter is floating; every retained candidate is replayed
with exact project selectors.  This is not an exhaustive no-hit theorem.
Any retained witness must be independently replayed before promotion.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DIV = ROOT / "verifiers" / "divergence"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(HERE.parent)]

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    coalition_minimum,
    csum,
    selector_from_constraints,
    selector_pair,
)


N = 6
TOTAL = F(17)
X = tuple(map(F, (F(9, 2), F(9, 2), 2, 2, 2, 2)))
Z = tuple(map(F, (4, 4, 3, 3, 2, 1)))
BASE = {7: F(11), 11: F(11), 17: F(6), 51: F(11)}


def singleton_normalized(constraints):
    return all(
        coalition_minimum(constraints, N, TOTAL, 1 << i) == 0
        for i in range(N)
    )


def tangent_complete(rows):
    """Fast incidence-only Lmin completeness filter at the fixed X."""
    blocks = ((2, 3, 4, 5), (0, 1))
    for stage, block in enumerate(blocks):
        earlier = tuple(i for old in blocks[:stage] for i in old)
        for designated in block:
            aub = []
            bub = []
            for mask in rows:
                aub.append([-float((mask >> i) & 1) for i in range(N)])
                bub.append(0.0)
            for i in block:
                coeff = [0.0] * N
                coeff[i] = -1.0
                aub.append(coeff)
                bub.append(-1.0 if i == designated else 0.0)
            aeq = [[1.0] * N]
            beq = [0.0]
            for i in earlier:
                coeff = [0.0] * N
                coeff[i] = 1.0
                aeq.append(coeff)
                beq.append(0.0)
            answer = linprog(
                np.zeros(N), A_ub=np.asarray(aub), b_ub=np.asarray(bub),
                A_eq=np.asarray(aeq), b_eq=np.asarray(beq),
                bounds=[(None, None)] * N, method="highs",
            )
            if answer.success:
                return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subset-max", type=int, default=3)
    parser.add_argument("--augmentation-max", type=int, default=2)
    parser.add_argument("--stop-after", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    replay, x, z = selector_pair(BASE, N, TOTAL)
    if x != X or z != Z:
        raise AssertionError((x, z))

    feasible_rows = tuple(
        mask for mask in range(1, (1 << N) - 1)
        if csum(X, mask) <= csum(Z, mask)
    )
    complete_sparse = []
    for size in range(args.subset_max + 1):
        for rows in itertools.combinations(feasible_rows, size):
            if not tangent_complete(rows):
                continue
            constraints = {mask: csum(X, mask) for mask in rows}
            if selector_from_constraints(constraints, N, TOTAL, "min") == X:
                complete_sparse.append(rows)

    # Only rows outside the base game can create a new certificate choice.
    new_rows = tuple(mask for mask in feasible_rows if mask not in BASE)
    witnesses = []
    checked = 0
    singleton_pass = 0
    multi_cx = 0
    for size in range(1, args.augmentation_max + 1):
        for added in itertools.combinations(new_rows, size):
            augmented_rows = set(BASE) | set(added)
            if not any(
                rows != (7, 11) and set(rows).issubset(augmented_rows)
                for rows in complete_sparse
            ):
                continue
            constraints = dict(BASE)
            constraints.update({mask: csum(X, mask) for mask in added})
            checked += 1
            if not singleton_normalized(constraints):
                continue
            singleton_pass += 1
            values, lx, lz = selector_pair(constraints, N, TOTAL)
            if lx != X or lz != Z:
                raise AssertionError((added, lx, lz))
            item = audit_game(
                f"pxc98_augmented_{'_'.join(map(str, added))}",
                values,
                lx,
                lz,
                pool_max=18,
                replay_exact=False,
            )
            if item is None or not item["cx_subsets_exhausted"]:
                continue
            if item["complete_cx_count"] < 2:
                continue
            multi_cx += 1
            signatures = {
                tuple(row["faithful_cover_indices"])
                for row in item["complete_cx_cover_matrix"]
            }
            if len(signatures) < 2:
                continue
            witnesses.append({
                "added_rows": list(added),
                "constraints": {str(k): str(v) for k, v in constraints.items()},
                "complete_cx_count": item["complete_cx_count"],
                "cover_count": item["cover_count"],
                "complete_cx_cover_matrix": item["complete_cx_cover_matrix"],
                "x_tight_rows": item["tight_x_rows"],
                "covers": item["covers"],
            })
            if len(witnesses) >= args.stop_after:
                break
        if len(witnesses) >= args.stop_after:
            break

    payload = {
        "claim": "PXC98-augmentation discovery search for complete-Cx dependence",
        "parameters": vars(args) | {
            "output": str(args.output) if args.output else None,
        },
        "base_selectors": {
            "x": list(map(str, X)), "z": list(map(str, Z)),
        },
        "candidate_feasible_rows": len(feasible_rows),
        "complete_sparse_subsets_through_bound": [list(q) for q in complete_sparse],
        "augmentation_cells_checked": checked,
        "singleton_normalized_augmentations": singleton_pass,
        "augmentations_with_multiple_complete_cx": multi_cx,
        "certificate_dependent_witnesses": witnesses,
        "scope": (
            "PXC98 base plus at most the stated number of added x-tight, "
            "z-feasible rows; floating tangent prefilter followed by exact replay "
            "of retained candidates; discovery provenance, not exhaustive proof"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
