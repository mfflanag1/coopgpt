"""Exact-LP replay of the realizable bridge stratum witnesses.

The witnesses were emitted by the independent tight-set/tangent-cone
enumerator.  This script does not use that enumerator or the symbolic KKT
bridge.  It checks exactness from the definition, recomputes Lmin with the
project's exact rational Maschler implementation, and checks every claimed
richer-suffix equality.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

from leximin import leximin_core_exact
from tugame import Game, exact_lp_min


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


WITNESSES = [
    {
        "composition": [1, 2],
        "phi": [1, 2, 2],
        "values": [0, 0, 0, 1, 0, 1, 4, 5],
        "suffixes": [6],
    },
    {
        "composition": [2, 2],
        "phi": [1, 1, 2, 2],
        "values": [0, 0, 0, 1, 0, 0, 2, 2, 0, 0, 2, 2, 4, 4, 4, 6],
        "suffixes": [12],
    },
    {
        "composition": [1, 3],
        "phi": [1, 2, 2, 2],
        "values": [0, 0, 0, 1, 0, 1, 3, 4, 0, 1, 3, 4, 3, 4, 6, 7],
        "suffixes": [14],
    },
    {
        "composition": [1, 1, 2],
        "phi": [1, 2, 3, 3],
        "values": [0, 0, 0, 1, 0, 0, 3, 3, 0, 0, 3, 3, 6, 6, 8, 9],
        "suffixes": [14, 12],
    },
]


def coalition_minimum(game, coalition):
    n, full = game.n, game.N
    objective = [F(1) if coalition >> i & 1 else F(0) for i in range(n)]
    inequalities = []
    bounds = []
    for proper in range(1, full):
        inequalities.append([
            F(-1) if proper >> i & 1 else F(0) for i in range(n)
        ])
        bounds.append(-game.v[proper])
    optimum, _ = exact_lp_min(
        objective,
        inequalities,
        bounds,
        [[F(1)] * n],
        [game.v[full]],
    )
    if optimum is None or optimum == "unbounded":
        raise RuntimeError(f"core LP failed for coalition {coalition}: {optimum}")
    return optimum


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = []
    for witness in WITNESSES:
        game = Game(len(witness["phi"]), witness["values"])
        phi = [F(value) for value in witness["phi"]]
        minima = {
            coalition: coalition_minimum(game, coalition)
            for coalition in range(1, game.N)
        }
        if any(minima[coalition] != game.v[coalition] for coalition in minima):
            raise RuntimeError(
                f"witness {witness['composition']} is not exact from the definition"
            )
        computed = leximin_core_exact(game)
        if computed != phi:
            raise RuntimeError(
                f"wrong Lmin for {witness['composition']}: {computed} != {phi}"
            )
        suffix_values = {}
        for suffix in witness["suffixes"]:
            payoff = game.xS(phi, suffix)
            if payoff != game.v[suffix]:
                raise RuntimeError(
                    f"slack richer suffix {suffix} in {witness['composition']}"
                )
            suffix_values[str(suffix)] = str(payoff)
        records.append({
            "player_count": game.n,
            "payoff_stratum_composition": witness["composition"],
            "phi": [str(value) for value in phi],
            "exactness_faces_checked": game.N - 1,
            "tight_richer_suffixes": suffix_values,
        })
    payload = {
        "status": "all realizable bridge stratum witnesses independently replayed",
        "method": "exact rational core LPs plus independent Maschler Lmin implementation",
        "witnesses": records,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
