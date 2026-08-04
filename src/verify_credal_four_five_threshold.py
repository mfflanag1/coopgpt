"""Exact audit of the sharp four/five credal Lorenz threshold.

The theorem is proved structurally in the accompanying note.  This script
reconstructs the five-state coherent lower probability from four rational
probability distributions, recomputes both lexicographic selections from the
induced core, and checks the crossing of their Lorenz curves.  It is a
bug-detecting audit, not a substitute for the proof.  The first-stage
lexicographic optima also audit failure of a universal Schur-concave
uncertainty maximizer.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximax_core_exact, leximin_core_exact
from tugame import Game


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


N = 5
FULL = (1 << N) - 1
GENERATORS_UNSCALED = (
    (0, 0, 0, 3, 3),
    (0, 0, 3, 3, 0),
    (1, 1, 1, 0, 3),
    (1, 1, 1, 1, 2),
)
GENERATORS = tuple(
    tuple(F(value, 6) for value in point)
    for point in GENERATORS_UNSCALED
)
LMIN = (F(1, 6), F(1, 6), F(1, 6), F(1, 6), F(1, 3))
LMAX = (F(1, 8), F(1, 8), F(1, 4), F(1, 4), F(1, 4))


def coalition_sum(point, coalition):
    return sum(
        (point[player] for player in range(N) if coalition >> player & 1),
        F(0),
    )


def lower_envelope():
    values = [F(0)] * (1 << N)
    for coalition in range(1, FULL + 1):
        values[coalition] = min(
            coalition_sum(point, coalition) for point in GENERATORS
        )
    return values


def in_credal_set(values, point):
    return (
        coalition_sum(point, FULL) == 1
        and all(
            coalition_sum(point, coalition) >= values[coalition]
            for coalition in range(1, FULL)
        )
    )


def lorenz_cumulative(point):
    ordered = sorted(point)
    total = F(0)
    cumulative = []
    for value in ordered:
        total += value
        cumulative.append(total)
    return tuple(cumulative)


def strings(values):
    return [str(value) for value in values]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if any(sum(point, F(0)) != 1 for point in GENERATORS):
        raise AssertionError("a defining point is not a probability distribution")
    values = lower_envelope()
    if values[0] != 0 or values[FULL] != 1:
        raise AssertionError("lower envelope is not normalized")
    if tuple(values[1 << player] for player in range(N)) != (F(0),) * N:
        raise AssertionError("the lower probability is not atom-vacuous")
    hand_certificate_values = {
        "complement_1": values[FULL ^ (1 << 0)],
        "complement_2": values[FULL ^ (1 << 1)],
        "pair_3_5": values[(1 << 2) | (1 << 4)],
        "pair_4_5": values[(1 << 3) | (1 << 4)],
    }
    if hand_certificate_values != {
        "complement_1": F(5, 6),
        "complement_2": F(5, 6),
        "pair_3_5": F(1, 2),
        "pair_4_5": F(1, 2),
    }:
        raise AssertionError("the four-inequality hand certificate changed")

    # A lower envelope of common-total points is coherent/exact: each
    # generator satisfies every envelope inequality, and a generator attains
    # the minimum for every event.
    if not all(in_credal_set(values, point) for point in GENERATORS):
        raise AssertionError("a defining distribution left the induced credal set")
    exactifiers = {}
    for coalition in range(1, FULL + 1):
        attaining = [
            index + 1
            for index, point in enumerate(GENERATORS)
            if coalition_sum(point, coalition) == values[coalition]
        ]
        if not attaining:
            raise AssertionError(f"event {coalition} has no exactifying generator")
        exactifiers[str(coalition)] = attaining

    game = Game(N, values)
    computed_lmin = tuple(leximin_core_exact(game))
    computed_lmax = tuple(leximax_core_exact(game))
    if computed_lmin != LMIN:
        raise AssertionError(f"unexpected Lmin: {computed_lmin}")
    if computed_lmax != LMAX:
        raise AssertionError(f"unexpected Lmax: {computed_lmax}")
    if not in_credal_set(values, LMIN) or not in_credal_set(values, LMAX):
        raise AssertionError("a displayed selection is outside the credal set")
    lmax_mixture = tuple(
        F(1, 4) * GENERATORS[1][player]
        + F(3, 4) * GENERATORS[3][player]
        for player in range(N)
    )
    if lmax_mixture != LMAX:
        raise AssertionError("the displayed hand feasibility mixture is wrong")

    lmin_curve = lorenz_cumulative(LMIN)
    lmax_curve = lorenz_cumulative(LMAX)
    better_lmin = [
        rank + 1 for rank in range(N - 1)
        if lmin_curve[rank] > lmax_curve[rank]
    ]
    better_lmax = [
        rank + 1 for rank in range(N - 1)
        if lmax_curve[rank] > lmin_curve[rank]
    ]
    if not better_lmin or not better_lmax:
        raise AssertionError("the two Lorenz curves do not cross")
    if lmin_curve[0] != F(1, 6) or lmax_curve[3] != F(3, 4):
        raise AssertionError("the elementary uncertainty optima changed")

    # The richer suffix {5} at Lmin is slack: this is the exact-partition
    # obstruction transported into the atom-vacuous credal formulation.
    richest = 1 << 4
    richest_slack = coalition_sum(LMIN, richest) - values[richest]
    if richest_slack != F(1, 3):
        raise AssertionError(f"unexpected richest-suffix slack: {richest_slack}")

    payload = {
        "status": "sharp five-state credal Lorenz obstruction verified",
        "arithmetic": "exact rational lower envelope and staged LP selections",
        "state_count": N,
        "defining_distributions": [strings(point) for point in GENERATORS],
        "coherent_lower_probability": {
            "event_values_by_mask": {
                str(mask): str(value) for mask, value in enumerate(values)
            },
            "atom_lower_probabilities": [
                str(values[1 << player]) for player in range(N)
            ],
            "exactifying_generators_by_nonempty_mask": exactifiers,
        },
        "leximin_distribution": strings(computed_lmin),
        "decreasingly_minimal_distribution": strings(computed_lmax),
        "hand_certificate": {
            "event_values": {
                name: str(value)
                for name, value in hand_certificate_values.items()
            },
            "leximin": (
                "complement bounds cap the minimum at 1/6; equality and the "
                "two pair bounds pin all coordinates"
            ),
            "decreasingly_minimal": (
                "pair bounds cap the smallest possible maximum at 1/4; "
                "the feasible mixture (1/4)g2+(3/4)g4 attains it and pins "
                "the final equal split"
            ),
        },
        "leximin_lorenz_cumulative": strings(lmin_curve),
        "decreasingly_minimal_lorenz_cumulative": strings(lmax_curve),
        "strict_ranks_favoring_leximin": better_lmin,
        "strict_ranks_favoring_decreasingly_minimal": better_lmax,
        "lorenz_curves_cross": True,
        "universal_uncertainty_obstruction": {
            "max_L1": "1/6",
            "unique_L1_maximizer": strings(LMIN),
            "L1_maximizer_largest_coordinate": "1/3",
            "max_L4": "3/4",
            "an_L4_maximizer": strings(LMAX),
            "L4_maximizer_largest_coordinate": "1/4",
            "maximizer_sets_disjoint": True,
        },
        "richest_singleton_slack_at_leximin": str(richest_slack),
        "conclusion": (
            "the induced five-state credal set has no Lorenz-dominating "
            "or universally uncertainty-maximizing distribution; combined "
            "with the structural through-four theorem, the state-space "
            "threshold is sharp"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
