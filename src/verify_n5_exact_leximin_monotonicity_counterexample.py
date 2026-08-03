"""Solver-free certificate for an exact proper-coalition monotonicity failure.

Both games are lower envelopes of common-total allocations.  The base game
adds one allocation to the two endpoint generators and differs from the
endpoint game only at S={1,3,4,5}.  Exact arithmetic verifies the complete
leximin path and the strict losses of target players 3 and 5.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximin_core_exact
from tugame import Game


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


N = 5
FULL = (1 << N) - 1
S = 29  # {1,3,4,5}; outside player 2.
A = (2, 0, 12, 6, 0)
B = (0, 0, 0, 0, 20)
P = (0, 2, 10, 4, 4)
BASE_GENERATORS = (A, B, P)
ENDPOINT_GENERATORS = (A, B)
PHI_BASE = (F(1), F(1), F(13, 2), F(5), F(13, 2))
PHI_ENDPOINT = (F(2), F(0), F(6), F(6), F(6))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def payoff(point, coalition):
    return sum(point[player] for player in range(N) if coalition >> player & 1)


def lower_envelope(generators):
    values = [F(0)] * (1 << N)
    for coalition in range(1, FULL):
        values[coalition] = min(payoff(point, coalition) for point in generators)
    values[FULL] = F(sum(generators[0]))
    return values


def in_core(values, point):
    return payoff(point, FULL) == values[FULL] and all(
        payoff(point, coalition) >= values[coalition]
        for coalition in range(1, FULL)
    )


def members(coalition):
    return [player + 1 for player in range(N) if coalition >> player & 1]


def path(tau):
    tau = F(tau)
    if tau <= 19:
        return PHI_BASE
    return (
        tau - 18,
        20 - tau,
        16 - tau / 2,
        tau - 14,
        16 - tau / 2,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    require(all(sum(point) == 20 for point in BASE_GENERATORS),
            "generators do not have common total 20")
    base = lower_envelope(BASE_GENERATORS)
    endpoint = lower_envelope(ENDPOINT_GENERATORS)
    changed = [
        coalition for coalition in range(1, FULL)
        if base[coalition] != endpoint[coalition]
    ]
    require(changed == [S], "games differ away from the target")
    require((base[S], endpoint[S]) == (18, 20), "wrong bump interval")

    # The compact off-target check behind changed == [S]: if 5 is absent,
    # B(T)=0<=P(T).  If 5 is present, P(T)-A(T)=4+2*1_{2 in T}
    # -2*|T intersect {1,3,4}|, negative only at T=S.
    for coalition in range(1, FULL):
        if not coalition >> 4 & 1:
            require(payoff(B, coalition) <= payoff(P, coalition),
                    "B does not dominate P off player 5")
        elif coalition != S:
            require(payoff(A, coalition) <= payoff(P, coalition),
                    "A does not dominate P on a non-target coalition")

    # Lower envelopes of common-total allocations are exact: every displayed
    # generator is in the core and one attains each coalition worth.
    for values, generators in ((base, BASE_GENERATORS),
                               (endpoint, ENDPOINT_GENERATORS)):
        require(all(in_core(values, point) for point in generators),
                "a lower-envelope generator left the core")
        require(all(
            any(payoff(point, coalition) == values[coalition]
                for point in generators)
            for coalition in range(1, FULL + 1)
        ), "a coalition worth is not attained")

    floors = tuple(base[1 << player] for player in range(N))
    require(floors == (0, 0, 0, 0, 0), "singleton floors are not zero")
    require(tuple(endpoint[1 << player] for player in range(N)) == floors,
            "the bump changed singleton floors")
    require(in_core(base, PHI_BASE), "base leximin candidate is infeasible")
    require(in_core(endpoint, PHI_ENDPOINT),
            "endpoint leximin candidate is infeasible")

    # Recompute both headline allocations with the project's independent exact
    # rational Maschler implementation; the hand stage certificates below are
    # retained for transparency rather than used as substitutes for this test.
    computed_base = tuple(leximin_core_exact(Game(N, base)))
    computed_endpoint = tuple(leximin_core_exact(Game(N, endpoint)))
    require(computed_base == PHI_BASE,
            f"recomputed base Lmin is {computed_base}, expected {PHI_BASE}")
    require(computed_endpoint == PHI_ENDPOINT,
            "recomputed endpoint Lmin disagrees with the displayed vector")

    # Structural escape from the four-player protector proof.  The base
    # allocation has strata 2+1+2.  Its only tight nontrivial proper
    # coalitions protect the three poorer players, while the richer pair
    # {3,5} remains strictly slack.
    base_tight_proper = [
        coalition for coalition in range(1, FULL)
        if payoff(PHI_BASE, coalition) == base[coalition]
    ]
    require(base_tight_proper == [21, 28],
            "unexpected tight-coalition geometry at the base Lmin point")
    richer_pair = 20  # {3,5}
    require(
        (base[richer_pair], payoff(PHI_BASE, richer_pair)) == (12, 13),
        "the 3|2 exact-partition obstruction is not the displayed unit slack",
    )

    # Base Maschler certificate.  v(345)=18 implies x1+x2<=2, so the first
    # common gain is at most 1 and pins 1,2.  Then v(135)=14 forces x4<=5;
    # efficiency leaves x3+x5=13, which is equalized.
    require(base[28] == 18 and base[21] == 14,
            "base stage coalitions have wrong values")
    require(PHI_BASE[0] + PHI_BASE[1] == 2, "base first stage not tight")
    require(PHI_BASE[3] == 5, "base second stage not tight")
    require(PHI_BASE[2] == PHI_BASE[4] == F(13, 2),
            "base final stage not equalized")

    # Endpoint certificate.  S tight at 20 pins player 2 at its floor zero;
    # v(345)=18 then caps player 1 at 2; v(35)=12 caps player 4 at 6; the
    # remaining pair is equalized at 6.
    require(endpoint[28] == 18 and endpoint[20] == 12,
            "endpoint stage coalitions have wrong values")
    require(PHI_ENDPOINT == (2, 0, 6, 6, 6),
            "wrong endpoint stage solution")

    # The old point stays feasible through tau=19.  On [19,20] every path
    # coordinate is affine, so feasibility at both endpoints proves it on the
    # whole interval.  The displayed caps reproduce the four Maschler stages.
    require(payoff(PHI_BASE, S) == 19, "wrong nonbinding threshold")
    for tau in (F(19), F(20)):
        values = list(base)
        values[S] = tau
        candidate = path(tau)
        require(in_core(values, candidate), "path endpoint is infeasible")
        require(payoff(candidate, S) == tau, "target is not path-tight")
        require(candidate[1] == 20 - tau, "stage 1 formula failed")
        require(candidate[0] == tau - 18, "stage 2 formula failed")
        require(candidate[3] == tau - 14, "stage 3 formula failed")
        require(candidate[2] == candidate[4] == 16 - tau / 2,
                "stage 4 formula failed")

    # Star holds at every binding interior point even though the realized
    # leximin derivative lowers target players 3 and 5.  This directly refutes
    # the previously conjectured star-along-path implication.
    for tau in (F(19), F(20)):
        values = list(base)
        values[S] = tau
        witness = (F(2), F(0), 16 - tau / 2, tau - 14, 16 - tau / 2)
        require(in_core(values, witness), "star witness is infeasible")

    for tau in (F(19), F(39, 2)):
        values = list(base)
        values[S] = tau
        witness = (F(2), F(0), 16 - tau / 2, tau - 14, 16 - tau / 2)
        require(all(witness[player] >= path(tau)[player]
                    for player in (0, 2, 3, 4)),
                "star witness lowers a target player")
        require(payoff(witness, S) == 20 > tau,
                "star witness does not raise the target total")

    drops = {
        player + 1: PHI_BASE[player] - PHI_ENDPOINT[player]
        for player in range(N)
        if S >> player & 1 and PHI_ENDPOINT[player] < PHI_BASE[player]
    }
    require(drops == {3: F(1, 2), 5: F(1, 2)}, "wrong target losses")

    report = {
        "status": "exact proper-coalition monotonicity counterexample verified",
        "lmin_verification": "exact rational staged Maschler LP recomputation",
        "n": N,
        "target": members(S),
        "base_generators": [list(point) for point in BASE_GENERATORS],
        "endpoint_generators": [list(point) for point in ENDPOINT_GENERATORS],
        "base_target_value": str(base[S]),
        "endpoint_target_value": str(endpoint[S]),
        "nonbinding_threshold": str(payoff(PHI_BASE, S)),
        "base_leximin": [str(value) for value in PHI_BASE],
        "endpoint_leximin": [str(value) for value in PHI_ENDPOINT],
        "base_payoff_strata": [[1, 2], [4], [3, 5]],
        "base_tight_nontrivial_proper_coalitions": {
            "135": str(base[21]),
            "345": str(base[28]),
        },
        "failed_exact_partition_boundary": {
            "poorer_side": [1, 2, 4],
            "richer_side": [3, 5],
            "richer_pair_value": str(base[richer_pair]),
            "richer_pair_lmin_sum": str(payoff(PHI_BASE, richer_pair)),
            "slack": str(payoff(PHI_BASE, richer_pair) - base[richer_pair]),
        },
        "target_player_losses": {str(player): str(loss)
                                  for player, loss in drops.items()},
        "binding_path": [
            "tau-18", "20-tau", "16-tau/2", "tau-14", "16-tau/2"
        ],
        "binding_interval": ["19", "20"],
        "star_holds_on_binding_interior": True,
        "conclusion": (
            "leximin above singleton floors is not coalitionally monotone "
            "on exact games; star along the exact path is not sufficient"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
