"""Exact replay of a minimal five-player unique-richest Lmin obstruction.

The game is the lower envelope of four common-total integer allocations.  The
generator representation proves exactness directly.  Exact core LPs, staged
Lmin recomputation, the four inequalities in the human proof, and the
exact-balanced slack circuit are checked independently.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hunt_sd import core_min_xS
from leximin import leximin_core_exact
from tugame import Game


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


GENERATORS = (
    (0, 0, 0, 3, 3),
    (0, 0, 3, 3, 0),
    (1, 1, 1, 0, 3),
    (1, 1, 1, 1, 2),
)
PHI = GENERATORS[-1]


def coalition_sum(vector, coalition):
    return sum(
        vector[player]
        for player in range(len(vector))
        if coalition >> player & 1
    )


def lower_envelope(generators):
    n = len(generators[0])
    full = (1 << n) - 1
    values = [0] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(
            coalition_sum(point, coalition) for point in generators
        )
    values[full] = sum(generators[0])
    return values


def members(coalition, n=5):
    return [player + 1 for player in range(n) if coalition >> player & 1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    n = 5
    full = (1 << n) - 1
    richest = 1 << 4
    values = lower_envelope(GENERATORS)
    game = Game(n, values)
    if any(sum(point) != 6 for point in GENERATORS):
        raise RuntimeError("the generators lack common total six")
    if any(not game.in_core(point) for point in GENERATORS):
        raise RuntimeError("a lower-envelope generator is not in the core")

    face_minima = {
        coalition: core_min_xS(game, coalition)
        for coalition in range(1, full)
    }
    failures = [
        coalition
        for coalition, minimum in face_minima.items()
        if minimum != game.v[coalition]
    ]
    if failures:
        raise RuntimeError(f"independent exactness replay failed at {failures}")

    recomputed_phi = tuple(leximin_core_exact(game))
    if recomputed_phi != PHI:
        raise RuntimeError(f"Lmin replay disagrees: {recomputed_phi} != {PHI}")
    human_constraints = {
        0b11110: 5,  # N\{1}
        0b11101: 5,  # N\{2}
        0b10100: 3,  # {3,5}
        0b11000: 3,  # {4,5}
    }
    if any(game.v[coalition] != value for coalition, value in human_constraints.items()):
        raise RuntimeError("a load-bearing human-proof coalition has the wrong value")
    if game.v[richest] != 0 or PHI[4] != 2:
        raise RuntimeError("the richest singleton does not have slack two")

    weights = {
        0b10100: 1,  # {3,5}
        0b11000: 1,  # {4,5}
        0b00001: 1,  # {1}
        0b00010: 1,  # {2}
        richest: -1,
    }
    coverage = [
        sum(
            weight
            for coalition, weight in weights.items()
            if coalition >> player & 1
        )
        for player in range(n)
    ]
    if coverage != [1] * n:
        raise RuntimeError(f"bad exact-balanced incidence circuit: {coverage}")
    slacks = {
        coalition: coalition_sum(PHI, coalition) - game.v[coalition]
        for coalition in weights
    }
    weighted_slack = sum(
        weight * slacks[coalition]
        for coalition, weight in weights.items()
    )
    if weighted_slack != 0:
        raise RuntimeError(f"the slack circuit does not balance: {weighted_slack}")

    payload = {
        "status": "five-player unique-richest exact Lmin obstruction verified",
        "exactness_certificate": "lower envelope of common-total core generators",
        "generators": [list(point) for point in GENERATORS],
        "independent_replay": (
            "all 30 proper exact faces recomputed by exact LP; Lmin recomputed by exact staged LP"
        ),
        "lmin": list(PHI),
        "payoff_strata": [[1, 2, 3, 4], [5]],
        "richest_singleton_value": str(game.v[richest]),
        "richest_singleton_payoff": str(PHI[4]),
        "richest_singleton_slack": str(PHI[4] - game.v[richest]),
        "human_lmin_proof_coalition_values": {
            str(coalition): str(value)
            for coalition, value in human_constraints.items()
        },
        "exact_balanced_circuit": {
            "identity": "1_{35}+1_{45}+1_{1}+1_{2}-1_{5}=1_N",
            "player_coverage": coverage,
            "coalition_slacks": {
                str(members(coalition)): str(slack)
                for coalition, slack in slacks.items()
            },
            "weighted_slack_total": str(weighted_slack),
            "fractional_protector_packing_equality": "2 = 1 + 1",
        },
        "characteristic_function": {
            str(coalition): str(game.v[coalition])
            for coalition in range(1, full + 1)
        },
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
