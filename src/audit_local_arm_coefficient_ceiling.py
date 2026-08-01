"""Probe the local-circuit arm coefficient ceiling in small dimensions.

For a leaf relation

    degree(q) = alpha*1 - m*e_a

containing the distinguished arm coalition A, enumerate every positive local
circuit and test the candidate dimension-free inequality q_A <= |A| m.
The default audit exhausts n=3,4,5 and every proper arm size, using a canonical
arm and selected player.  Symmetry covers all arms and selected members.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from hunt_glued_local_circuits import coefficient, enumerate_local
from search_both_sensitive_circuits import eliminated_matrix


def audit(max_players=5):
    rows = []
    violations = []
    total_circuits = 0
    for players in range(3, max_players + 1):
        for arm_size in range(1, players):
            arm = (1 << arm_size) - 1
            other_arm = 1 << arm_size
            matrix, _ineq, _eq, rowmeta = eliminated_matrix(
                players, arm, other_arm
            )
            mono = rowmeta.index(("mono", 0, 1, 0, arm))
            arm_core = rowmeta.index(("core", 1, arm))
            circuits = enumerate_local(
                matrix,
                rowmeta,
                1,
                (mono, arm_core),
                players=players,
            )
            ratios = tuple(
                coefficient(circuit, arm_core) / coefficient(circuit, mono)
                for circuit in circuits
            )
            total_circuits += len(circuits)
            bad = [
                (index + 1, ratio) for index, ratio in enumerate(ratios)
                if ratio > arm_size
            ]
            violations.extend(
                (players, arm_size, index, ratio)
                for index, ratio in bad
            )
            rows.append({
                "players": players,
                "arm_size": arm_size,
                "circuit_count": len(circuits),
                "distinct_ratios": [str(value) for value in sorted(set(ratios))],
                "maximum_ratio": str(max(ratios)) if ratios else None,
                "candidate_bound": str(arm_size),
                "violation_count": len(bad),
            })
    return {
        "status": (
            "no small-dimension violation of q_A <= |A| m"
            if not violations else "coefficient ceiling violated"
        ),
        "dimensions_exhausted": [3, max_players],
        "symmetry_scope": (
            "one canonical arm of every proper size and one selected member"
        ),
        "total_local_circuits": total_circuits,
        "violation_count": len(violations),
        "rows": rows,
        "violations": [
            {
                "players": players,
                "arm_size": arm_size,
                "circuit_index": index,
                "ratio": str(ratio),
            }
            for players, arm_size, index, ratio in violations
        ],
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-players", type=int, default=5)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(args.max_players), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
