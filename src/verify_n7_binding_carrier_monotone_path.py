"""Solver-free certificate for a bumpable carrier failure with monotone path.

This exact seven-player lower-envelope game violates eta>=gamma at its
leximin point, but has exact bump capacity 10 > sigma=9.  Every admissible
target bump is nevertheless coalitionally monotone.  All checks below use
integer or Fraction arithmetic and no optimizer.
"""
from __future__ import annotations

import json
from fractions import Fraction as F


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


N = 7
FULL = (1 << N) - 1
S = 15  # 1234
P = FULL ^ S
ZERO = (0, 0, 0, 0, 0, 0, 0)
A = (-215, 53, 104, 103, -56, 51, -40)
B = (108, -55, -4, -1, 50, -60, -38)
C = (10, 0, 0, 0, 0, -10, 0)
D = (-72, 18, 36, 28, -18, 18, -10)
BASE_GENERATORS = (ZERO, A, B)
ENDPOINT_GENERATORS = (A, B, C, D)
PHI = (-75, 17, 32, 35, -20, 15, -4)
PHI_10 = (-74, 17, 32, 35, -20, 14, -4)
ETA_SUPPORT = {48: 2, 84: 1, 88: 1, 109: 2}
ETA_WITNESS = (-75, 17, 51, 51, -17, 7, -34)


def payoff(allocation, coalition):
    return sum(
        allocation[player]
        for player in range(N)
        if coalition >> player & 1
    )


def members(coalition):
    return [player + 1 for player in range(N) if coalition >> player & 1]


def lower_envelope(generators):
    return tuple(
        min(payoff(generator, coalition) for generator in generators)
        for coalition in range(1 << N)
    )


def in_core(value, allocation):
    return (
        payoff(allocation, FULL) == value[FULL]
        and all(
            payoff(allocation, coalition) >= value[coalition]
            for coalition in range(1 << N)
        )
    )


def main():
    assert all(sum(generator) == 0 for generator in BASE_GENERATORS)
    assert all(sum(generator) == 0 for generator in ENDPOINT_GENERATORS)
    value = lower_envelope(BASE_GENERATORS)
    endpoint = list(value)
    endpoint[S] = 10
    endpoint = tuple(endpoint)

    # Both endpoints are exact lower-envelope games.  At d=10 the alternate
    # four-generator representation proves exactness coalition by coalition.
    assert endpoint == lower_envelope(ENDPOINT_GENERATORS)
    assert all(in_core(value, generator) for generator in BASE_GENERATORS)
    assert all(in_core(endpoint, generator) for generator in ENDPOINT_GENERATORS)
    assert all(
        value[coalition]
        in {payoff(generator, coalition) for generator in BASE_GENERATORS}
        for coalition in range(1 << N)
    )
    assert all(
        endpoint[coalition]
        in {payoff(generator, coalition) for generator in ENDPOINT_GENERATORS}
        for coalition in range(1 << N)
    )

    assert in_core(value, PHI)
    floors = tuple(value[1 << player] for player in range(N))
    assert floors == (-215, -55, -4, -1, -56, -60, -40)
    gains = tuple(PHI[player] - floors[player] for player in range(N))
    assert gains == (140, 72, 36, 36, 36, 75, 36)

    # Compact Maschler certificate for the base point.
    # v(1236)=-11 and v(1246)=-8 imply x(457)<=11 and x(357)<=8.
    # The corresponding floor sums are -97 and -100, so the first common
    # gain is at most 36 and pins 3,4,5,7.
    assert value[39] == -11 and value[43] == -8
    assert payoff(PHI, 39) == value[39] and payoff(PHI, 43) == value[43]
    assert sum(floors[player] for player in (3, 4, 6)) == -97
    assert sum(floors[player] for player in (2, 4, 6)) == -100
    assert all(gains[player] == 36 for player in (2, 3, 4, 6))

    # On the first face, v(13456)=-13 gives x(27)<=13 and pins player 2.
    assert value[61] == -13 and payoff(PHI, 61) == -13
    assert PHI[1] == 13 - PHI[6] == 17
    assert gains[1] == 72

    # Then v(134)=-8 gives x(2567)<=8 and pins player 6; efficiency pins 1.
    assert value[13] == -8 and payoff(PHI, 13) == -8
    assert PHI[5] == 8 - PHI[1] - PHI[4] - PHI[6] == 15
    assert gains[5] == 75 and gains[0] == 140

    slack = tuple(
        payoff(PHI, coalition) - value[coalition]
        for coalition in range(1 << N)
    )
    differences = tuple(
        slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    )
    assert set(differences) == {36, 39}
    gamma = min(differences)

    # Exact eta upper certificate plus matching feasible witness.
    degree = [
        int(S >> player & 1)
        + int(player == 0)
        + 3 * int(player == 1)
        + sum(
            weight * int(coalition >> player & 1)
            for coalition, weight in ETA_SUPPORT.items()
        )
        for player in range(N)
    ]
    assert degree == [4] * N
    eta_upper = sum(weight * slack[coalition] for coalition, weight in ETA_SUPPORT.items())
    assert eta_upper == 35
    assert in_core(value, ETA_WITNESS)
    assert all(ETA_WITNESS[player] >= PHI[player] for player in range(4))
    eta_lower = payoff(ETA_WITNESS, S) - payoff(PHI, S)
    assert eta_lower == eta_upper
    eta = eta_upper

    sigma = payoff(PHI, S) - value[S]
    assert sigma == 9

    # Capacity upper bound: 1_N+1_35=1_S+1_56+1_357.  On F_35 this gives
    # x(S)<=10 because v(35)=v(357)=0 and v(56)=-10.  C attains equality.
    face_35, face_56, face_357 = 20, 48, 84
    for player in range(N):
        assert (
            int(FULL >> player & 1) + int(face_35 >> player & 1)
            == int(S >> player & 1)
            + int(face_56 >> player & 1)
            + int(face_357 >> player & 1)
        )
    assert (value[face_35], value[face_56], value[face_357]) == (0, -10, 0)
    assert payoff(C, face_35) == 0 and payoff(C, S) == 10
    capacity = F(10)
    assert capacity > sigma

    # The full exact leximin path.  For tau<=sigma the old point is feasible.
    # For sigma<=tau<=10, phi_tau=phi+(tau-sigma)(e1-e6).  Endpoint core
    # feasibility plus convexity verifies every intermediate core constraint.
    assert in_core(endpoint, PHI_10)
    displacement = tuple(PHI_10[player] - PHI[player] for player in range(N))
    assert displacement == (1, 0, 0, 0, 0, -1, 0)
    assert payoff(PHI_10, S) == 10

    # The first two Maschler stages are unchanged.  On their common face,
    # x2+x3+x4=84 and efficiency leaves x1+x6=-60.  The bumped target
    # constraint gives x1>=tau-84 and hence x6<=24-tau.  This pins
    # player 6 before efficiency pins player 1 throughout the interval.
    assert PHI[1] + PHI[2] + PHI[3] == 84
    assert PHI[0] + PHI[5] == -60
    assert 84 - capacity > 72
    assert 131 + sigma > 84 - sigma

    print(json.dumps({
        "status": "solver-free bumpable carrier failure with monotone exact path verified",
        "n": N,
        "target": members(S),
        "base_generators": [list(generator) for generator in BASE_GENERATORS],
        "endpoint_generators": [list(generator) for generator in ENDPOINT_GENERATORS],
        "leximin": [str(value) for value in PHI],
        "maschler_strata": [
            {"gain": "36", "players": [3, 4, 5, 7]},
            {"gain": "72", "players": [2]},
            {"gain": "75", "players": [6]},
            {"gain": "140", "players": [1]},
        ],
        "gamma": str(gamma),
        "eta": str(eta),
        "carrier_gap_gamma_minus_eta": str(gamma - eta),
        "selection_slack_sigma": str(sigma),
        "exact_bump_capacity": str(capacity),
        "binding_exact_bump_interval": [str(sigma), str(capacity)],
        "leximin_path": "phi_tau=phi+(tau-9)*(e1-e6)",
        "target_coordinate_changes_on_binding_interval": [
            "tau-9", "0", "0", "0"
        ],
        "conclusion": (
            "the quantitative carrier inequality fails in a binding-bumpable "
            "exact game, yet every admissible target bump is leximin-monotone"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
