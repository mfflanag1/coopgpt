"""Search for an exact disjoint-arm family violating a known n=5 circuit.

Exactness is encoded linearly: for every proper coalition U in every game,
the LP includes a core allocation tight at U.  Hence a feasible rationalized
solution is already a complete exactness certificate, not a float screen.
"""
from __future__ import annotations

import json
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog

from family_infeasible import farkas_certificate, is_family_feasible
from tugame import Game


N = 5
GRAND = (1 << N) - 1
A = 0b00111
B = 0b11000
PROPER = tuple(range(1, GRAND))
# Exact unit positive circuit returned by minimize_both_sensitive_support.py.
CIRCUIT_CORE_ROWS = (
    (0, 20),
    (1, 7), (1, 25), (1, 26),
    (2, 5), (2, 6), (2, 11), (2, 24),
)
EFFICIENCY_TOTAL = 4


WORTH_OFFSET = 0
D_A_INDEX = len(PROPER)
D_B_INDEX = D_A_INDEX + 1
WITNESS_OFFSET = D_B_INDEX + 1


def witness_index(game, tight_coalition, player):
    return WITNESS_OFFSET + ((game * len(PROPER) + tight_coalition - 1) * N + player)


VARIABLE_COUNT = WITNESS_OFFSET + 3 * len(PROPER) * N


def worth_index(coalition):
    return WORTH_OFFSET + coalition - 1


def bump_index(game, coalition):
    if game == 1 and coalition == A:
        return D_A_INDEX
    if game == 2 and coalition == B:
        return D_B_INDEX
    return None


def build_lp(violation=F(1, 10)):
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    for game in range(3):
        for tight in PROPER:
            efficiency = np.zeros(VARIABLE_COUNT)
            for player in range(N):
                efficiency[witness_index(game, tight, player)] = 1
            A_eq.append(efficiency)
            b_eq.append(1)

            for coalition in PROPER:
                core = np.zeros(VARIABLE_COUNT)
                core[worth_index(coalition)] = 1
                bump = bump_index(game, coalition)
                if bump is not None:
                    core[bump] = 1
                for player in range(N):
                    if coalition >> player & 1:
                        core[witness_index(game, tight, player)] = -1
                A_ub.append(core)
                b_ub.append(0)

            tightness = np.zeros(VARIABLE_COUNT)
            for player in range(N):
                if tight >> player & 1:
                    tightness[witness_index(game, tight, player)] = 1
            tightness[worth_index(tight)] = -1
            bump = bump_index(game, tight)
            if bump is not None:
                tightness[bump] = -1
            A_eq.append(tightness)
            b_eq.append(0)

    # The circuit Farkas margin is 4 - sum of its eight core-row worths.
    # Require a fixed strictly negative margin.
    violation_row = np.zeros(VARIABLE_COUNT)
    for game, coalition in CIRCUIT_CORE_ROWS:
        violation_row[worth_index(coalition)] -= 1
        bump = bump_index(game, coalition)
        if bump is not None:
            violation_row[bump] -= 1
    A_ub.append(violation_row)
    b_ub.append(-float(F(EFFICIENCY_TOTAL) + violation))

    bounds = [(None, None)] * VARIABLE_COUNT
    bounds[D_A_INDEX] = (0, None)
    bounds[D_B_INDEX] = (0, None)
    return A_ub, b_ub, A_eq, b_eq, bounds


def rationalize(values, denominator=10000):
    return [F(float(value)).limit_denominator(denominator) for value in values]


def games_from_solution(solution):
    base_values = [F(0)] * (1 << N)
    for coalition in PROPER:
        base_values[coalition] = solution[worth_index(coalition)]
    base_values[GRAND] = F(1)
    arm_A_values = list(base_values)
    arm_A_values[A] += solution[D_A_INDEX]
    arm_B_values = list(base_values)
    arm_B_values[B] += solution[D_B_INDEX]
    return tuple(Game(N, values) for values in (base_values, arm_A_values, arm_B_values))


def exact_witnesses(solution):
    return [
        [
            tuple(solution[witness_index(game, tight, player)] for player in range(N))
            for tight in PROPER
        ]
        for game in range(3)
    ]


def verify_solution(solution):
    games = games_from_solution(solution)
    witnesses = exact_witnesses(solution)
    for game, game_witnesses in zip(games, witnesses):
        for tight, point in zip(PROPER, game_witnesses):
            assert sum(point) == game.v[GRAND]
            assert not game.core_violations(point)
            assert sum(point[i] for i in range(N) if tight >> i & 1) == game.v[tight]

    supported = sum(games[game].v[coalition] for game, coalition in CIRCUIT_CORE_ROWS)
    margin = F(EFFICIENCY_TOTAL) - supported
    assert margin < 0
    edges = [(0, 1, A), (0, 2, B)]
    feasible, _point = is_family_feasible(games, edges)
    assert not feasible
    certificate = farkas_certificate(games, edges)
    assert certificate is not None and certificate["rhs"] < 0
    return games, witnesses, margin, certificate


def search():
    A_ub, b_ub, A_eq, b_eq, bounds = build_lp()
    result = linprog(
        np.zeros(VARIABLE_COUNT),
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq),
        b_eq=np.asarray(b_eq),
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        return {"status": result.message}
    solution = rationalize(result.x)
    games, witnesses, margin, certificate = verify_solution(solution)
    return {
        "status": "EXACT DISJOINT COUNTEREXAMPLE VERIFIED",
        "n": N,
        "A_mask": A,
        "B_mask": B,
        "bumps": [str(solution[D_A_INDEX]), str(solution[D_B_INDEX])],
        "farkas_margin_unit_circuit": str(margin),
        "normalized_farkas_rhs": str(certificate["rhs"]),
        "base_values": [str(value) for value in games[0].v],
        "exactness_witnesses": [
            [[str(value) for value in point] for point in game_witnesses]
            for game_witnesses in witnesses
        ],
    }


if __name__ == "__main__":
    print(json.dumps(search(), indent=2))
