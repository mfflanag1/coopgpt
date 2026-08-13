#!/usr/bin/env python3
"""Independent rational audit of weighted max-min/min-max fairness.

The finite common-two theorem defines weighted Lmin and Lmax by universal
fairness implications instead of staged lexicographic LPs.  This script
constructs deterministic exact lower-envelope four-role games, computes both
selectors with the staged rational implementation, and independently asks an
LP for a violating fairness direction at every role and selector.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

from exactlp import exact_linprog  # noqa: E402
import explore_weighted_four_role_faces as faces  # noqa: E402


def random_composition(rng, total):
    cuts = sorted(rng.sample(range(total + 3), 3))
    return (
        cuts[0],
        cuts[1] - cuts[0] - 1,
        cuts[2] - cuts[1] - 1,
        total + 2 - cuts[2],
    )


def fairness_extreme(values, weights, point, role, mode):
    """Optimize the challenged coordinate subject to absence of a repair."""

    aub, bub = [], []
    for coalition in range(1, 15):
        aub.append([F(-1 if coalition >> j & 1 else 0) for j in range(4)])
        bub.append(-values[coalition])
    challenged_level = F(point[role], weights[role])
    for other in range(4):
        other_level = F(point[other], weights[other])
        relevant = (
            other_level <= challenged_level
            if mode == "min"
            else other_level >= challenged_level
        )
        if not relevant:
            continue
        row = [F(0)] * 4
        row[other] = F(-1 if mode == "min" else 1)
        aub.append(row)
        bub.append(-point[other] if mode == "min" else point[other])
    objective = [F(0)] * 4
    objective[role] = F(-1 if mode == "min" else 1)
    status, optimum, _ = exact_linprog(
        objective,
        aub,
        bub,
        [[F(1)] * 4],
        [values[15]],
    )
    if status != "optimal":
        raise AssertionError(("fairness LP", mode, role, status))
    return -optimum if mode == "min" else optimum


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260813)
    parser.add_argument("--games-per-n", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    games = selectors = role_implications = 0
    by_n = []
    for n in range(4, 9):
        accepted = 0
        for _ in range(args.games_per_n):
            weight_cuts = sorted(rng.sample(range(1, n), 3))
            weights = (
                weight_cuts[0],
                weight_cuts[1] - weight_cuts[0],
                weight_cuts[2] - weight_cuts[1],
                n - weight_cuts[2],
            )
            total = rng.randint(3, 10)
            generators = tuple(
                random_composition(rng, total) for _ in range(6)
            )
            values = faces.role_values(generators)
            if any(
                weights[role] == 1 and values[1 << role] != 0
                for role in range(4)
            ):
                continue
            accepted += 1
            games += 1
            for mode in ("min", "max"):
                point, _ = faces.weighted_lex_point(values, weights, mode)
                selectors += 1
                for role in range(4):
                    extreme = fairness_extreme(
                        values, weights, point, role, mode
                    )
                    if mode == "min" and extreme > point[role]:
                        raise AssertionError(
                            ("max-min fairness violation", weights, point, role, extreme)
                        )
                    if mode == "max" and extreme < point[role]:
                        raise AssertionError(
                            ("min-max fairness violation", weights, point, role, extreme)
                        )
                    role_implications += 1
        by_n.append({"n": n, "exact_games_checked": accepted})
    report = {
        "status": "weighted fairness selector characterization audited exactly",
        "seed": args.seed,
        "games_per_n_attempted": args.games_per_n,
        "exact_lower_envelope_games_checked": games,
        "staged_selectors_checked": selectors,
        "role_fairness_implications_checked": role_implications,
        "rows": by_n,
        "scope": (
            "independent rational regression for the human max-min/min-max "
            "fairness characterization; finite controls are not its proof"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
