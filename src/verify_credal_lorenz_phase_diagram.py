"""Exact audit of the four-state half of the credal Lorenz phase diagram.

The human theorem proves that every coherent lower probability on at most
three states has a Lorenz-dominating induced distribution because its credal
set is a box-slice base polytope.  This script checks the sharp four-state
lower-envelope witness, including hand certificates for its ordinary
increasingly maximal and decreasingly minimal distributions.  It is a
bug-detecting audit, not proof evidence.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximax_core_exact
from tugame import Game, exact_lp_min


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


N = 4
FULL = (1 << N) - 1
GENERATORS = (
    (F(23, 48), F(7, 48), F(9, 48), F(9, 48)),
    (F(13, 48), F(13, 48), F(2, 48), F(20, 48)),
)
INCREASINGLY_MAXIMAL = (F(3, 8), F(1, 6), F(1, 6), F(7, 24))
DECREASINGLY_MINIMAL = (F(1, 3), F(5, 24), F(1, 8), F(1, 3))


def coalition_sum(point, coalition):
    return sum(
        (point[player] for player in range(N) if coalition >> player & 1),
        F(0),
    )


def lower_envelope():
    return [
        min(coalition_sum(point, coalition) for point in GENERATORS)
        for coalition in range(FULL + 1)
    ]


def in_credal_set(values, point):
    return (
        sum(point, F(0)) == 1
        and all(
            coalition_sum(point, coalition) >= values[coalition]
            for coalition in range(1, FULL)
        )
    )


def increasingly_maximal_core_exact(game):
    """Ordinary inc-max core point, without Lmin's singleton-floor shift."""
    n, full, values = game.n, game.N, game.v
    fixed = {}
    free = list(range(n))

    def solve_level():
        level = n
        inequalities, bounds = [], []
        for coalition in range(1, full):
            row = [F(0)] * (n + 1)
            for player in range(n):
                if coalition >> player & 1:
                    row[player] = F(-1)
            inequalities.append(row)
            bounds.append(-values[coalition])
        for player in free:
            row = [F(0)] * (n + 1)
            row[player] = F(-1)
            row[level] = F(1)
            inequalities.append(row)
            bounds.append(F(0))
        equalities = [[F(1)] * n + [F(0)]]
        equality_bounds = [values[full]]
        for player, value in fixed.items():
            row = [F(0)] * (n + 1)
            row[player] = F(1)
            equalities.append(row)
            equality_bounds.append(value)
        objective = [F(0)] * (n + 1)
        objective[level] = F(-1)
        return exact_lp_min(
            objective,
            inequalities,
            bounds,
            equalities,
            equality_bounds,
        )

    def max_player(player, level):
        inequalities, bounds = [], []
        for coalition in range(1, full):
            inequalities.append([
                F(-1) if coalition >> other & 1 else F(0)
                for other in range(n)
            ])
            bounds.append(-values[coalition])
        for other in free:
            row = [F(0)] * n
            row[other] = F(-1)
            inequalities.append(row)
            bounds.append(-level)
        equalities = [[F(1)] * n]
        equality_bounds = [values[full]]
        for other, value in fixed.items():
            row = [F(0)] * n
            row[other] = F(1)
            equalities.append(row)
            equality_bounds.append(value)
        objective = [F(0)] * n
        objective[player] = F(-1)
        optimum, _ = exact_lp_min(
            objective,
            inequalities,
            bounds,
            equalities,
            equality_bounds,
        )
        return -optimum

    while free:
        optimum, _ = solve_level()
        if optimum is None or optimum == "unbounded":
            raise AssertionError("ordinary inc-max stage is infeasible")
        level = -optimum
        pinned = [
            player for player in free
            if max_player(player, level) == level
        ]
        if not pinned:
            raise AssertionError("ordinary inc-max stage pinned no coordinate")
        for player in pinned:
            fixed[player] = level
            free.remove(player)
    return tuple(fixed[player] for player in range(n))


def lorenz_cumulative(point):
    total = F(0)
    answer = []
    for value in sorted(point):
        total += value
        answer.append(total)
    return tuple(answer)


def strings(values):
    return [str(value) for value in values]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if any(sum(point, F(0)) != 1 for point in GENERATORS):
        raise AssertionError("a generator is not a probability distribution")
    values = lower_envelope()
    if not all(in_credal_set(values, point) for point in GENERATORS):
        raise AssertionError("a lower-envelope generator left the credal set")
    exactifiers = {
        str(coalition): [
            index + 1
            for index, point in enumerate(GENERATORS)
            if coalition_sum(point, coalition) == values[coalition]
        ]
        for coalition in range(1, FULL + 1)
    }
    if any(not indices for indices in exactifiers.values()):
        raise AssertionError("the lower envelope is not exactified eventwise")

    game = Game(N, values)
    computed_incmax = increasingly_maximal_core_exact(game)
    computed_decmin = tuple(leximax_core_exact(game))
    if computed_incmax != INCREASINGLY_MAXIMAL:
        raise AssertionError(f"unexpected ordinary inc-max: {computed_incmax}")
    if computed_decmin != DECREASINGLY_MINIMAL:
        raise AssertionError(f"unexpected dec-min: {computed_decmin}")
    if not in_credal_set(values, computed_incmax):
        raise AssertionError("ordinary inc-max point is infeasible")
    if not in_credal_set(values, computed_decmin):
        raise AssertionError("dec-min point is infeasible")

    # The two hand certificates use only these two event bounds and
    # efficiency. They imply p2+p3<=1/3, p1+p2>=13/24, and p1+p4>=2/3.
    if values[0b0011] != F(13, 24) or values[0b1001] != F(2, 3):
        raise AssertionError("the hand-certificate event values changed")

    inc_curve = lorenz_cumulative(computed_incmax)
    dec_curve = lorenz_cumulative(computed_decmin)
    if not (inc_curve[0] > dec_curve[0] and inc_curve[2] < dec_curve[2]):
        raise AssertionError("the four-state Lorenz curves do not cross")

    payload = {
        "status": "sharp four-state general credal Lorenz obstruction verified",
        "arithmetic": "exact rational lower envelope and staged LP selections",
        "state_count": N,
        "defining_distributions": [strings(point) for point in GENERATORS],
        "event_values_by_mask": {
            str(mask): str(value) for mask, value in enumerate(values)
        },
        "exactifying_generators_by_nonempty_mask": exactifiers,
        "ordinary_increasingly_maximal_distribution": strings(computed_incmax),
        "decreasingly_minimal_distribution": strings(computed_decmin),
        "ordinary_increasingly_maximal_lorenz_cumulative": strings(inc_curve),
        "decreasingly_minimal_lorenz_cumulative": strings(dec_curve),
        "hand_certificate": {
            "event_1_2_lower_bound": "13/24",
            "event_1_4_lower_bound": "2/3",
            "incmax": (
                "p2+p3<=1/3 caps the minimum at 1/6; equality pins p2,p3, "
                "then p1+p2>=13/24 caps and pins the next coordinate p4"
            ),
            "decmin": (
                "p1+p4>=2/3 caps the smallest maximum at 1/3; equality pins "
                "p1,p4, then p1+p2>=13/24 pins the next dec-min stage"
            ),
        },
        "lorenz_curves_cross": True,
        "conclusion": (
            "arbitrary coherent lower probabilities can first lack a "
            "Lorenz-dominating induced distribution on four states"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
