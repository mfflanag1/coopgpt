#!/usr/bin/env python3
"""Exact rational replay of PXC144: the four-generator seven-player game H_7.

H_7 is the lower envelope of the four integer allocations
    A=(1,4,7,0,0,0,1), B=(0,0,0,5,3,3,2), C=(0,5,8,0,0,0,0), D=(0,0,4,1,3,3,2)
of total 13.  It is exact and singleton-normalized, and
    Lmin = (1,3,5,1,1,1,1),   Lmax = (1,3,13,13,13,13,9)/5,
so ||Lmin-Lmax||_1/T = 56/65 > 5/6 and O/T = 37/65 < 7/12.

This verifier is LP-free and imports no project module.  Both selectors are
proved by explicit staged Farkas identities (the sparse chain printed in the
manuscript): at every stage, for every player of the new stratum, a
nonnegative combination of core rows, efficiency, previously pinned
coordinates and the current stage inequalities is checked coefficient by
coefficient.  Each identity simultaneously bounds the stage value and forces
the player onto it; attainment by the displayed vector finishes the stage.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

N = 7
T = 13
A = (1, 4, 7, 0, 0, 0, 1)
B = (0, 0, 0, 5, 3, 3, 2)
C = (0, 5, 8, 0, 0, 0, 0)
D = (0, 0, 4, 1, 3, 3, 2)
GENERATORS = (A, B, C, D)
X = tuple(F(a) for a in (1, 3, 5, 1, 1, 1, 1))
Z = tuple(F(a, 5) for a in (1, 3, 13, 13, 13, 13, 9))


def mask(players):
    return sum(1 << i for i in players)


def csum(point, coalition):
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


V = tuple(min(csum(g, s) for g in GENERATORS) for s in range(1 << N))

# Staged certificates.  'rows': coalition -> multiplier (core rows y(S)>=v(S));
# 'eff': multiplier of efficiency; 'fixed': pinned coordinate -> multiplier;
# 'stage': other unfixed coordinate -> multiplier of its stage inequality.
# Lmin identity (min mode):   e_i = -sum lam_S 1_S + eff*1_N + sum nu_j e_j - sum beta_j e_j
#   giving y_i <= eff*T - sum lam_S v(S) + sum nu_j x_j - sum beta_j t  for every core y with y_j>=t (j unfixed).
# Lmax identity (max mode):   e_i =  sum lam_S 1_S - eff*1_N - sum nu_j e_j - sum beta_j e_j
#   giving y_i >= sum lam_S v(S) - eff*T - sum nu_j z_j - sum beta_j t  for every core y with y_j<=t (j unfixed).
LMIN_STAGES = (
    (F(1), (
        (0, {"rows": {mask((2, 3, 5)): 1, mask((1, 4, 6)): 1}, "eff": 1, "fixed": {}, "stage": {}}),
        (6, {"rows": {mask((1, 2, 3, 4, 5)): 1}, "eff": 1, "fixed": {}, "stage": {0: 1}}),
        (4, {"rows": {mask((1, 2, 3, 4, 5)): 1, mask((2, 3, 6)): 1, mask((1, 5, 6)): 1}, "eff": 2, "fixed": {}, "stage": {0: 2}}),
        (5, {"rows": {mask((1, 2, 3, 4, 5)): 1, mask((2, 3, 6)): 1, mask((1, 4, 6)): 1}, "eff": 2, "fixed": {}, "stage": {0: 2}}),
        (3, {"rows": {mask((1, 2, 3, 4, 5)): 2, mask((2, 3, 6)): 1, mask((1, 4, 6)): 1, mask((1, 5, 6)): 1, mask((2, 4, 5, 6)): 1}, "eff": 4, "fixed": {}, "stage": {0: 4}}),
    )),
    (F(3), (
        (1, {"rows": {mask((2, 4, 5, 6)): 1}, "eff": 1, "fixed": {0: -1, 3: -1}, "stage": {}}),
    )),
    (F(5), (
        (2, {"rows": {}, "eff": 1, "fixed": {0: -1, 1: -1, 3: -1, 4: -1, 5: -1, 6: -1}, "stage": {}}),
    )),
)
LMAX_STAGES = (
    (F(13, 5), (
        (4, {"rows": {mask((0, 2, 3, 4)): 1, mask((1, 2, 3, 4, 5)): 1, mask((2, 3, 6)): 1}, "eff": 1, "fixed": {}, "stage": {2: 2, 3: 2}}),
        (5, {"rows": {mask((0, 2, 3, 5)): 1, mask((1, 2, 3, 4, 5)): 1, mask((2, 3, 6)): 1}, "eff": 1, "fixed": {}, "stage": {2: 2, 3: 2}}),
        (2, {"rows": {mask((0, 2, 3, 4)): F(1, 2), mask((1, 2, 3, 4, 5)): F(1, 2), mask((2, 3, 6)): F(1, 2)}, "eff": F(1, 2), "fixed": {}, "stage": {3: 1, 4: F(1, 2)}}),
        (3, {"rows": {mask((0, 2, 3, 4)): F(1, 2), mask((1, 2, 3, 4, 5)): F(1, 2), mask((2, 3, 6)): F(1, 2)}, "eff": F(1, 2), "fixed": {}, "stage": {2: 1, 4: F(1, 2)}}),
    )),
    (F(9, 5), (
        (6, {"rows": {mask((2, 3, 6)): 1}, "eff": 0, "fixed": {2: 1, 3: 1}, "stage": {}}),
    )),
    (F(3, 5), (
        (1, {"rows": {mask((0, 2, 3, 4)): 1, mask((1, 2, 3, 4, 5)): 1, mask((1, 4, 6)): 1}, "eff": 1, "fixed": {2: 1, 3: 1, 4: 2}, "stage": {}}),
    )),
    (F(1, 5), (
        (0, {"rows": {mask((0, 2, 3, 4)): 1}, "eff": 0, "fixed": {2: 1, 3: 1, 4: 1}, "stage": {}}),
    )),
)


def check_stage_certificate(mode, point, level, player, cert, pinned, unfixed):
    """Verify one Farkas identity coefficient by coefficient, return implied bound."""
    sgn = -1 if mode == "min" else 1
    vec = [F(0)] * N
    for coalition, lam in cert["rows"].items():
        lam = F(lam)
        assert lam >= 0, ("negative multiplier", mode, player)
        for i in range(N):
            if coalition >> i & 1:
                vec[i] += sgn * lam
    vec = [c - sgn * F(cert["eff"]) for c in vec]
    for j, nu in cert["fixed"].items():
        assert j in pinned, ("fixed player not pinned", mode, player, j)
        vec[j] += F(nu) * (1 if mode == "min" else -1)
    for j, beta in cert["stage"].items():
        beta = F(beta)
        assert beta >= 0 and j in unfixed and j != player, ("stage multiplier", mode, player, j)
        vec[j] -= beta
    target = [F(1 if i == player else 0) for i in range(N)]
    assert vec == target, ("identity failed", mode, player, vec)
    constant = sgn * sum(F(lam) * V[s] for s, lam in cert["rows"].items()) - sgn * F(cert["eff"]) * T
    constant += sum(F(nu) * point[j] for j, nu in cert["fixed"].items()) * (1 if mode == "min" else -1)
    beta_total = sum((F(b) for b in cert["stage"].values()), F(0))
    # min mode: y_i <= constant - beta_total * t  (with y_j >= t);  max mode: y_i >= constant - beta_total * t (with y_j <= t)
    # Stage value bound: t <= y_i (min) / t >= y_i (max) gives t*(1+beta_total) <=/>= constant.
    stage_value = constant / (1 + beta_total)
    assert stage_value == level, ("stage value", mode, player, stage_value, level)
    forced_bound = constant - beta_total * level
    assert forced_bound == level, ("forced bound", mode, player, forced_bound, level)
    return {"player": player, "identity": "ok", "constant": str(constant), "beta_total": str(beta_total)}


def replay(mode, point, stages):
    pinned = {}
    unfixed = set(range(N))
    report = []
    for level, certs in stages:
        block = [player for player, _ in certs]
        for player, cert in certs:
            assert point[player] == level, ("displayed vector off level", mode, player)
            report.append(check_stage_certificate(mode, point, level, player, cert, pinned, unfixed))
        # players outside the block are not forced: the displayed vector is feasible with them strictly beyond the level
        for j in unfixed:
            if j not in block:
                assert (point[j] > level) if mode == "min" else (point[j] < level), ("block incomplete", mode, j)
        for player in block:
            pinned[player] = level
            unfixed.remove(player)
        report.append({"stage_level": str(level), "block": block})
    assert not unfixed
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    assert all(sum(g) == T and min(g) >= 0 for g in GENERATORS), "generators"
    assert V[-1] == T and all(V[1 << i] == 0 for i in range(N)), "normalization"
    unique = [0] * len(GENERATORS)
    for s in range(1 << N):
        hits = [k for k, g in enumerate(GENERATORS) if csum(g, s) == V[s]]
        assert hits, ("unattained", s)
        if len(hits) == 1:
            unique[hits[0]] += 1
    assert all(unique), ("redundant generator", unique)
    for g in GENERATORS:
        assert all(csum(g, s) >= V[s] for s in range(1 << N)), "generator outside core"
    for point in (X, Z):
        assert sum(point) == T and all(csum(point, s) >= V[s] for s in range(1 << N)), "selector candidate outside core"
    # Minimality of the generator set as a game: every proper subset fails (not singleton-normalized or different game).
    minimality = []
    for k in range(1, len(GENERATORS)):
        for sub in combinations(range(len(GENERATORS)), k):
            vals = tuple(min(csum(GENERATORS[j], s) for j in sub) for s in range(1 << N))
            minimality.append({"subset": list(sub), "same_game": vals == V})
    assert not any(row["same_game"] for row in minimality), "a proper generator subset defines the same game"

    lmin_report = replay("min", X, LMIN_STAGES)
    lmax_report = replay("max", Z, LMAX_STAGES)

    # The manuscript's hand chain, in the same arithmetic.
    v = lambda *players: V[mask(players)]
    hand = {
        "v(235)": v(2, 3, 5), "v(146)": v(1, 4, 6), "v(156)": v(1, 5, 6), "v(12345)": v(1, 2, 3, 4, 5),
        "v(236)": v(2, 3, 6), "v(2456)": v(2, 4, 5, 6), "v(0234)": v(0, 2, 3, 4), "v(0235)": v(0, 2, 3, 5),
    }
    assert T - v(2, 3, 5) - v(1, 4, 6) == 1                       # y_0 <= 1
    assert T - v(1, 2, 3, 4, 5) - 1 == 1                          # y_6 <= 1 once y_0 >= 1
    assert 2 * T - v(1, 2, 3, 4, 5) - v(2, 3, 6) - v(1, 5, 6) - 2 == 1   # y_4
    assert 4 * T - 2 * v(1, 2, 3, 4, 5) - v(2, 3, 6) - v(1, 4, 6) - v(1, 5, 6) - v(2, 4, 5, 6) - 4 == 1  # y_3
    assert T - v(2, 4, 5, 6) - 1 - 1 == 3                         # y_1 <= 3
    assert F(v(0, 2, 3, 4) + v(1, 2, 3, 4, 5) + v(2, 3, 6) - T, 5) == F(13, 5)  # 2y_2+2y_3+y_4 >= 13
    assert v(2, 3, 6) - 2 * F(13, 5) == F(9, 5)                   # y_6 >= 9/5
    assert v(0, 2, 3, 4) + v(1, 2, 3, 4, 5) + v(1, 4, 6) - T - 4 * F(13, 5) == F(3, 5)  # y_1 >= 3/5
    assert v(0, 2, 3, 4) - 3 * F(13, 5) == F(1, 5)                # y_0 >= 1/5

    distance = sum(abs(a - b) for a, b in zip(X, Z))
    overlap = sum(min(a, b) for a, b in zip(X, Z))
    rho = distance / T
    assert rho == F(56, 65) and overlap == F(37, 5) and overlap / T == F(37, 65)
    assert rho > F(5, 6) and overlap < F(7, 12) * T
    x_tight = [s for s in range(1, (1 << N) - 1) if csum(X, s) == V[s]]
    z_tight = [s for s in range(1, (1 << N) - 1) if csum(Z, s) == V[s]]
    payload = {
        "claim": "PXC144 H_7: four-generator integer seven-player exact game with rho=56/65 > 5/6",
        "construction": {"n": N, "total": T, "generators": [list(g) for g in GENERATORS],
                         "definition": "v(S)=min_g g(S)", "coalition_values": [str(a) for a in V]},
        "exactness": {"all_128_minima_attained": True, "all_generators_in_core": True,
                      "singleton_values": [str(V[1 << i]) for i in range(N)],
                      "unique_attainment_counts": unique, "generator_set_minimal": True,
                      "proper_subsets": minimality},
        "selectors": {"method": "LP-free replay of explicit staged Farkas identities (stdlib Fractions only)",
                      "Lmin": [str(a) for a in X], "Lmax": [str(a) for a in Z],
                      "Lmin_tight_proper_rows": x_tight, "Lmax_tight_proper_rows": z_tight,
                      "Lmin_replay": lmin_report, "Lmax_replay": lmax_report,
                      "hand_chain_values": {k: str(val) for k, val in hand.items()}},
        "violation": {"l1_distance": str(distance), "rho": str(rho), "rho_minus_5_over_6": str(rho - F(5, 6)),
                      "overlap": str(overlap), "overlap_over_T": str(overlap / T),
                      "target_7_over_12_T": str(F(7, 12) * T), "overlap_margin": str(overlap - F(7, 12) * T),
                      "pxc143_rho": "8291/9948", "improvement_over_pxc143": str(rho - F(8291, 9948))},
        "scope": "exact counterexample at n=7 to the formula s(n)=2-8n/(n^2-(n mod 2)); lower bound s(7)>=56/65; the sharp value s(7) is not determined",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
