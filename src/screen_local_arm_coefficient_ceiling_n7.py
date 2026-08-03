"""Deterministic exact n=7 screen for the local arm coefficient ceiling.

Randomly samples supports containing the leaf monotonicity column and the arm
core column.  Rank modulo 223 is exact here: every relevant square minor is
at most 6^3=216 by Hadamard.  Positive nullity-one kernels are recovered by
integer cofactors and checked against the full block.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from fractions import Fraction as F
from pathlib import Path

from hunt_glued_local_circuits import (
    coefficient,
    primitive_positive_kernel,
    rank_mod_prime,
)
from search_both_sensitive_circuits import eliminated_matrix


N = 7
PRIME = 223


def screen(samples_per_size=20_000, seed=20260801):
    rng = random.Random(seed)
    rows = []
    violations = []
    total_supports = 0
    total_positive = 0
    for arm_size in range(2, N):
        arm = (1 << arm_size) - 1
        other_arm = 1 << arm_size
        matrix, _ineq, _eq, rowmeta = eliminated_matrix(N, arm, other_arm)
        mono = rowmeta.index(("mono", 0, 1, 0, arm))
        arm_core = rowmeta.index(("core", 1, arm))
        width = N - 1
        block = matrix[width:2 * width, :].astype(int)
        pool = [
            index for index, meta in enumerate(rowmeta)
            if meta[0] == "core" and meta[1] == 1 and index != arm_core
        ]
        maximum = None
        maximum_record = None
        positive_count = 0
        sampled = set()
        for support_size in range(3, N + 1):
            extra_size = support_size - 2
            target = min(samples_per_size, math.comb(len(pool), extra_size))
            sampled_at_size = 0
            while sampled_at_size < target:
                extra = tuple(sorted(rng.sample(pool, extra_size)))
                key = (support_size, extra)
                if key in sampled:
                    continue
                sampled.add(key)
                sampled_at_size += 1
                support = (mono, arm_core, *extra)
                restricted = block[:, support]
                if rank_mod_prime(restricted, prime=PRIME) != support_size - 1:
                    continue
                weights = primitive_positive_kernel(restricted)
                if weights is None:
                    continue
                positive_count += 1
                circuit = support, weights
                ratio = coefficient(circuit, arm_core) / coefficient(circuit, mono)
                if maximum is None or ratio > maximum:
                    maximum = ratio
                    maximum_record = {
                        "support": [list(rowmeta[index]) for index in support],
                        "weights": list(weights),
                        "ratio": str(ratio),
                    }
                if ratio > arm_size and not any(
                    item["arm_size"] == arm_size for item in violations
                ):
                    violations.append({
                        "arm_size": arm_size,
                        "candidate_bound": str(arm_size),
                        "circuit": maximum_record,
                    })
        total_supports += len(sampled)
        total_positive += positive_count
        rows.append({
            "arm_size": arm_size,
            "supports_sampled": len(sampled),
            "positive_circuits": positive_count,
            "maximum_ratio": str(maximum) if maximum is not None else None,
            "candidate_bound": str(arm_size),
            "maximum_record": maximum_record,
        })
    return {
        "status": (
            "candidate coefficient ceiling violated"
            if violations else "no violation in exact n=7 support screen"
        ),
        "players": N,
        "seed": seed,
        "samples_per_support_size": samples_per_size,
        "rank_prime": PRIME,
        "hadamard_minor_bound": 216,
        "supports_sampled": total_supports,
        "positive_circuits": total_positive,
        "violation_count": len(violations),
        "rows": rows,
        "violations": violations,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-per-size", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(
        screen(args.samples_per_size, args.seed), indent=2
    ) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
