"""Exact replay of a fixed n=6 two-poorer suffix obstruction.

The game is the lower envelope of six common-total integer allocations, so
exactness has an immediate generator proof.  Exact core LPs for every
coalition, a staged exact-rational Lmin computation, and the inequalities used
in the short human Lmin proof are checked independently.
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
    (0, 1, 3, 3, 1, 2),
    (1, 0, 3, 2, 1, 3),
    (1, 0, 3, 3, 0, 3),
    (1, 0, 3, 3, 3, 0),
    (4, 0, 0, 0, 3, 3),
    (1, 1, 2, 2, 2, 2),
)
PHI = GENERATORS[-1]


def coalition_sum(vector, coalition):
    return sum(
        vector[player]
        for player in range(len(vector))
        if coalition >> player & 1
    )


def members(coalition, n=6):
    return [player + 1 for player in range(n) if coalition >> player & 1]


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    n = 6
    full = (1 << n) - 1
    poorer = 0b000011
    richer = full ^ poorer
    if any(sum(point) != 10 for point in GENERATORS):
        raise RuntimeError("the lower-envelope generators lack common total 10")
    values = lower_envelope(GENERATORS)

    game = Game(n, values)
    if any(not game.in_core(point) for point in GENERATORS):
        raise RuntimeError("a lower-envelope generator is not in the core")
    if any(
        min(coalition_sum(point, coalition) for point in GENERATORS)
        != game.v[coalition]
        for coalition in range(1, full)
    ):
        raise RuntimeError("a coalition lacks a generator attaining its worth")
    exact_face_minima = {
        coalition: core_min_xS(game, coalition)
        for coalition in range(1, full)
    }
    failures = [
        coalition
        for coalition, minimum in exact_face_minima.items()
        if minimum != game.v[coalition]
    ]
    if failures:
        raise RuntimeError(f"independent exactness replay failed at {failures}")

    recomputed_phi = tuple(leximin_core_exact(game))
    if recomputed_phi != PHI:
        raise RuntimeError(
            f"independent Lmin replay disagrees: {recomputed_phi} != {PHI}"
        )
    # Load-bearing values in the human max-min proof.
    human_constraints = {
        0b111101: 9,  # N\{2}
        0b110100: 6,  # {3,5,6}
        0b111000: 6,  # {4,5,6}
        0b011101: 7,  # {1,3,4,5}
        0b101101: 7,  # {1,3,4,6}
    }
    if any(game.v[coalition] != value for coalition, value in human_constraints.items()):
        raise RuntimeError("a load-bearing human-proof coalition has the wrong value")
    suffix_slack = coalition_sum(PHI, richer) - game.v[richer]
    if suffix_slack <= 0:
        raise RuntimeError("the richer four-player suffix is not slack")

    tight = [
        coalition
        for coalition in range(1, full)
        if coalition_sum(PHI, coalition) == game.v[coalition]
    ]
    payload = {
        "status": "exact six-player 2|4 Lmin suffix obstruction verified",
        "exactness_certificate": "lower envelope of common-total core generators",
        "independent_replay": (
            "all 62 exact faces recomputed by exact LP; Lmin recomputed by exact staged LP"
        ),
        "generators": [list(point) for point in GENERATORS],
        "human_lmin_proof_coalition_values": {
            str(coalition): str(value)
            for coalition, value in human_constraints.items()
        },
        "lmin": [str(value) for value in PHI],
        "poorer": members(poorer),
        "richer": members(richer),
        "richer_suffix_value": str(game.v[richer]),
        "richer_suffix_payoff": str(coalition_sum(PHI, richer)),
        "richer_suffix_slack": str(suffix_slack),
        "tight_proper_coalitions_at_lmin": [members(coalition) for coalition in tight],
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
