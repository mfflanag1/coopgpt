#!/usr/bin/env python3
"""Exact audit of the two-packet obstruction and its singleton exactification.

The example separates two statements that must not be conflated in an s(6)
proof:

* sparse first-stage Lmax/Lmin incidence certificates plus the individual
  cross-selection inequalities permit overlap 1/2; but
* adjoining explicit common-total generators to normalize every singleton
  changes the staged Lmin selection and restores overlap exactly to 2/3.

All data are rational.  Lexicographic selections are computed twice: by the
home-grown nonnegative simplex in ``verifiers/divergence`` and by the separate
free-variable exact LP implementation in ``src/exactlp.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402
from lexsimplex import lex_point_with_trace  # noqa: E402


N = 6
FULL = (1 << N) - 1
TRIAL_LMIN = (F(1, 12), F(1, 12), F(1, 12), F(1, 12), F(7, 12), F(1, 12))
LMAX = (F(0), F(1, 4), F(0), F(1, 4), F(1, 4), F(1, 4))

# Three distinct rows suffice to give every coordinate a zero.  Repetitions in
# the original feasibility extraction have deliberately been removed.
SINGLETON_WITNESSES = (
    (F(0), F(0), F(1, 4), F(3, 4), F(0), F(0)),
    (F(1, 4), F(0), F(0), F(3, 4), F(0), F(0)),
    (F(1, 4), F(0), F(0), F(0), F(3, 4), F(0)),
)

TOP_COALITION = 56       # {3,4,5}
BOTTOM_COALITION = 26    # {1,3,4}
ALPHA = (F(0), F(0), F(0), F(1, 3), F(1, 3), F(1, 3))
BETA = (F(1, 3), F(0), F(1, 3), F(0), F(0), F(1, 3))


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def lower_envelope(rows):
    return tuple(
        min(coalition_sum(row, coalition) for row in rows)
        for coalition in range(1 << N)
    )


def overlap(x, z):
    return sum((min(a, b) for a, b in zip(x, z)), F(0))


def independent_lex(v, mode):
    """Independent staged encoding using ``exact_linprog`` (all vars free)."""
    pinned = {}
    free = set(range(N))
    trace = []
    while free:
        # Variables are x_0,...,x_5,t.  The core singleton rows enforce x>=0
        # in the normalized game; the abstract envelope has stronger positive
        # singleton bounds where needed.
        aub, bub = [], []
        for coalition in range(1, FULL):
            row = [F(0)] * (N + 1)
            for i in range(N):
                if coalition >> i & 1:
                    row[i] = F(-1)
            aub.append(row)
            bub.append(-v[coalition])
        for i in free:
            row = [F(0)] * (N + 1)
            if mode == "min":
                row[i], row[N] = F(-1), F(1)   # t <= x_i
            else:
                row[i], row[N] = F(1), F(-1)   # x_i <= t
            aub.append(row)
            bub.append(F(0))

        aeq = [[F(1)] * N + [F(0)]]
        beq = [v[FULL]]
        for i, value in sorted(pinned.items()):
            row = [F(0)] * (N + 1)
            row[i] = F(1)
            aeq.append(row)
            beq.append(value)

        objective = [F(0)] * (N + 1)
        objective[N] = F(-1) if mode == "min" else F(1)
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        assert status == "optimal"
        level = -optimum if mode == "min" else optimum

        # Hold every free coordinate on the feasible side of this stage level,
        # then test its opposite extremum to decide whether it is forced.
        stage_aub = [row[:] for row in aub[: (FULL - 1)]]
        stage_bub = list(bub[: (FULL - 1)])
        for i in free:
            row = [F(0)] * (N + 1)
            row[i] = F(-1) if mode == "min" else F(1)
            stage_aub.append(row)
            stage_bub.append(-level if mode == "min" else level)

        newly = []
        for i in sorted(free):
            objective = [F(0)] * (N + 1)
            objective[i] = F(-1) if mode == "min" else F(1)
            status, optimum, _ = exact_linprog(
                objective, stage_aub, stage_bub, aeq, beq
            )
            assert status == "optimal"
            extreme = -optimum if mode == "min" else optimum
            if extreme == level:
                newly.append(i)
        assert newly
        for i in newly:
            pinned[i] = level
            free.remove(i)
        trace.append(
            {
                "level": level,
                "newly_pinned": tuple(newly),
                "remaining_free": tuple(sorted(free)),
            }
        )
    return tuple(pinned[i] for i in range(N)), trace


def first_floor_pinning_certificate(v, trial, player):
    """Find the exact dual certificate that ``player`` is pinned at the floor.

    For ``mu=min(trial)`` and ``P={j:trial_j=mu}``, the certificate is

        sum_S lambda_S 1_S + sum_{j in P} q_j e_j + e_player = c 1_N,
        c T - sum_S lambda_S v(S) - mu sum_j q_j = mu,

    with lambda,q,c nonnegative and S restricted to proper trial-tight
    coalitions.  Evaluating the incidence identity at any core point whose
    coordinates are at least mu proves y_player<=mu.  Strong LP duality gives
    the converse, so feasibility is equivalent to individual first-stage
    pinning.
    """
    mu = min(trial)
    floor = tuple(i for i, value in enumerate(trial) if value == mu)
    if player not in floor:
        raise ValueError("pinning certificate requested off the trial floor")
    tight = tuple(
        coalition
        for coalition in range(1, FULL)
        if coalition_sum(trial, coalition) == v[coalition]
    )
    m = len(tight)
    q_index = {j: m + k for k, j in enumerate(floor)}
    c_index = m + len(floor)
    width = c_index + 1

    aeq, beq = [], []
    for i in range(N):
        row = [F(0)] * width
        for k, coalition in enumerate(tight):
            row[k] = F(int(bool(coalition >> i & 1)))
        if i in q_index:
            row[q_index[i]] = F(1)
        row[c_index] = F(-1)
        aeq.append(row)
        beq.append(F(-int(i == player)))
    row = [F(0)] * width
    for k, coalition in enumerate(tight):
        row[k] = -v[coalition]
    for j in floor:
        row[q_index[j]] = -mu
    row[c_index] = v[FULL]
    aeq.append(row)
    beq.append(mu)

    aub, bub = [], []
    for k in range(width):
        row = [F(0)] * width
        row[k] = F(-1)
        aub.append(row)
        bub.append(F(0))
    status, _, solution = exact_linprog(
        [F(0)] * width, aub, bub, aeq, beq
    )
    if status == "infeasible":
        return None
    assert status == "optimal"
    lambdas = tuple(
        (tight[k], solution[k]) for k in range(m) if solution[k] > 0
    )
    q = tuple((j, solution[q_index[j]]) for j in floor if solution[q_index[j]] > 0)
    c = solution[c_index]
    assert c >= 0
    for i in range(N):
        load = sum(
            (weight for coalition, weight in lambdas if coalition >> i & 1),
            F(0),
        ) + sum((weight for j, weight in q if j == i), F(0)) + F(int(i == player))
        assert load == c
    assert (
        c * v[FULL]
        - sum((weight * v[coalition] for coalition, weight in lambdas), F(0))
        - mu * sum((weight for _, weight in q), F(0))
        == mu
    )
    return {"coalition_weights": lambdas, "floor_weights": q, "cover_level": c}


def staged_pinning_certificate(v, point, trace, mode, stage, player):
    """Exact dual certificate for one coordinate pinned at one lex stage.

    For Lmin, on the face with old coordinates fixed and the current block
    constrained below by its level, the incidence identity is

        sum lambda_S 1_S + sum q_j e_j + sum r_k e_k + e_i = c 1_N.

    For Lmax, with the current block constrained above by its level, it is

        sum lambda_S 1_S + sum q_j e_j - sum r_k e_k - e_i = c 1_N.

    Here lambda and r are nonnegative, q and c are free, and supported
    coalitions are point-tight.  The corresponding exact objective identity
    proves the required opposite extremum equals the stage level.
    """
    if mode not in ("min", "max"):
        raise ValueError(mode)
    block = tuple(trace[stage]["newly_pinned"])
    if player not in block:
        raise ValueError("player is not in the requested stage block")
    old = tuple(
        i
        for earlier in range(stage)
        for i in trace[earlier]["newly_pinned"]
    )
    level = trace[stage]["level"]
    tight = tuple(
        coalition
        for coalition in range(1, FULL)
        if coalition_sum(point, coalition) == v[coalition]
    )
    m = len(tight)
    q_index = {j: m + k for k, j in enumerate(old)}
    r_index = {j: m + len(old) + k for k, j in enumerate(block)}
    c_index = m + len(old) + len(block)
    width = c_index + 1

    aeq, beq = [], []
    for i in range(N):
        row = [F(0)] * width
        for k, coalition in enumerate(tight):
            row[k] = F(int(bool(coalition >> i & 1)))
        if i in q_index:
            row[q_index[i]] = F(1)
        if i in r_index:
            row[r_index[i]] = F(1 if mode == "min" else -1)
        row[c_index] = F(-1)
        aeq.append(row)
        beq.append(F(-int(i == player) if mode == "min" else int(i == player)))

    row = [F(0)] * width
    if mode == "min":
        for k, coalition in enumerate(tight):
            row[k] = -v[coalition]
        for j in old:
            row[q_index[j]] = -point[j]
        for j in block:
            row[r_index[j]] = -level
        row[c_index] = v[FULL]
    else:
        for k, coalition in enumerate(tight):
            row[k] = v[coalition]
        for j in old:
            row[q_index[j]] = point[j]
        for j in block:
            row[r_index[j]] = -level
        row[c_index] = -v[FULL]
    aeq.append(row)
    beq.append(level)

    aub, bub = [], []
    for k in tuple(range(m)) + tuple(r_index.values()):
        row = [F(0)] * width
        row[k] = F(-1)
        aub.append(row)
        bub.append(F(0))
    status, _, solution = exact_linprog([F(0)] * width, aub, bub, aeq, beq)
    assert status == "optimal"
    lambdas = tuple(
        (tight[k], solution[k]) for k in range(m) if solution[k] > 0
    )
    old_weights = tuple(
        (j, solution[q_index[j]]) for j in old if solution[q_index[j]] != 0
    )
    side_weights = tuple(
        (j, solution[r_index[j]]) for j in block if solution[r_index[j]] > 0
    )
    c = solution[c_index]

    for i in range(N):
        load = sum(
            (weight for coalition, weight in lambdas if coalition >> i & 1),
            F(0),
        ) + sum((weight for j, weight in old_weights if j == i), F(0))
        side = sum((weight for j, weight in side_weights if j == i), F(0))
        if mode == "min":
            load += side + F(int(i == player))
        else:
            load -= side + F(int(i == player))
        assert load == c
    if mode == "min":
        objective = (
            c * v[FULL]
            - sum((weight * v[S] for S, weight in lambdas), F(0))
            - sum((weight * point[j] for j, weight in old_weights), F(0))
            - level * sum((weight for _, weight in side_weights), F(0))
        )
    else:
        objective = (
            sum((weight * v[S] for S, weight in lambdas), F(0))
            + sum((weight * point[j] for j, weight in old_weights), F(0))
            - level * sum((weight for _, weight in side_weights), F(0))
            - c * v[FULL]
        )
    assert objective == level
    return {
        "stage": stage,
        "player": player,
        "level": level,
        "coalition_weights": lambdas,
        "old_pin_weights": old_weights,
        "level_side_weights": side_weights,
        "efficiency_weight": c,
        "incidence_sign": "+e_i" if mode == "min" else "-e_i",
    }


def all_staged_pinning_certificates(v, point, trace, mode):
    return tuple(
        staged_pinning_certificate(v, point, trace, mode, stage, player)
        for stage in range(len(trace))
        for player in trace[stage]["newly_pinned"]
    )


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def audit_game(label, rows):
    assert all(all(q >= 0 for q in row) and sum(row) == 1 for row in rows)
    v = lower_envelope(rows)
    # Each row lies in the core of its lower envelope and attains the grand
    # coalition; every coalition is attained by a row.  This is an explicit
    # exactness certificate, not a numerical inference.
    assert all(
        coalition_sum(row, coalition) >= v[coalition]
        for row in rows
        for coalition in range(1 << N)
    )
    assert all(
        any(coalition_sum(row, coalition) == v[coalition] for row in rows)
        for coalition in range(1 << N)
    )

    selections = {}
    for mode in ("min", "max"):
        simplex_point, simplex_trace = lex_point_with_trace(N, v, mode)
        independent_point, independent_trace = independent_lex(v, mode)
        assert tuple(simplex_point) == independent_point
        assert simplex_trace == independent_trace
        selections[mode] = {
            "point": independent_point,
            "trace": independent_trace,
            "pinning_certificates": all_staged_pinning_certificates(
                v, independent_point, independent_trace, mode
            ),
        }

    trial_floor = min(TRIAL_LMIN)
    trial_bottom = tuple(i for i, value in enumerate(TRIAL_LMIN) if value == trial_floor)
    pinning = {
        str(i): first_floor_pinning_certificate(v, TRIAL_LMIN, i)
        for i in trial_bottom
    }

    return {
        "label": label,
        "generators": rows,
        "singleton_values": tuple(v[1 << i] for i in range(N)),
        "singleton_normalized": all(v[1 << i] == 0 for i in range(N)),
        "lmin": selections["min"],
        "lmax": selections["max"],
        "overlap": overlap(
            selections["min"]["point"], selections["max"]["point"]
        ),
        "total": v[FULL],
        "top_coalition_value": v[TOP_COALITION],
        "bottom_coalition_value": v[BOTTOM_COALITION],
        "trial_lmin_first_floor_pinning_certificates": pinning,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    abstract = audit_game("two-generator abstract obstruction", (TRIAL_LMIN, LMAX))
    exactified = audit_game(
        "singleton-exactified boundary",
        (TRIAL_LMIN, LMAX) + SINGLETON_WITNESSES,
    )

    assert abstract["lmin"]["point"] == TRIAL_LMIN
    assert abstract["lmax"]["point"] == LMAX
    assert abstract["overlap"] == F(1, 2)
    assert not abstract["singleton_normalized"]

    true_lmin = (F(1, 12), F(1, 12), F(1, 12), F(1, 3), F(1, 3), F(1, 12))
    assert exactified["lmin"]["point"] == true_lmin
    assert exactified["lmax"]["point"] == LMAX
    assert exactified["overlap"] == F(2, 3)
    assert exactified["singleton_normalized"]
    assert all(
        abstract["trial_lmin_first_floor_pinning_certificates"][str(i)] is not None
        for i in (0, 1, 2, 3, 5)
    )
    assert all(
        exactified["trial_lmin_first_floor_pinning_certificates"][str(i)] is not None
        for i in (0, 1, 2, 5)
    )
    assert exactified["trial_lmin_first_floor_pinning_certificates"]["3"] is None

    # The same sparse paired certificate and both individual cross inequalities
    # survive exactification.  It is therefore insufficient as a theorem
    # hypothesis: what fails is the proposed *full* bottom stratum of TRIAL_LMIN.
    assert sum(ALPHA) == sum(BETA) == 1
    assert all(
        F(int(bool(TOP_COALITION >> i & 1)), 3) == ALPHA[i]
        for i in range(N)
    )
    assert all(
        F(int(not bool(BOTTOM_COALITION >> i & 1)), 3) == BETA[i]
        for i in range(N)
    )
    assert coalition_sum(TRIAL_LMIN, TOP_COALITION) == coalition_sum(
        LMAX, TOP_COALITION
    ) == F(3, 4)
    assert coalition_sum(TRIAL_LMIN, BOTTOM_COALITION) == coalition_sum(
        LMAX, BOTTOM_COALITION
    ) == F(3, 4)
    assert sum(a * x for a, x in zip(ALPHA, TRIAL_LMIN)) == max(LMAX)
    assert sum(b * z for b, z in zip(BETA, LMAX)) == min(TRIAL_LMIN)
    assert abstract["top_coalition_value"] == exactified["top_coalition_value"] == F(3, 4)
    assert abstract["bottom_coalition_value"] == exactified["bottom_coalition_value"] == F(3, 4)

    # This feasible first-stage improvement is a short primal certificate that
    # player 3 was not forced at the trial floor after exactification.
    assert all(
        coalition_sum(true_lmin, coalition)
        >= lower_envelope((TRIAL_LMIN, LMAX) + SINGLETON_WITNESSES)[coalition]
        for coalition in range(1 << N)
    )
    assert min(true_lmin) == F(1, 12) and true_lmin[3] > F(1, 12)

    report = {
        "status": (
            "exact boundary audit with complete staged pinning certificates; "
            "not a proof of the general six-player bound"
        ),
        "paired_certificate": {
            "top_support": [TOP_COALITION],
            "top_weight": F(1, 3),
            "eta": F(0),
            "alpha": ALPHA,
            "bottom_support": [BOTTOM_COALITION],
            "bottom_weight": F(1, 3),
            "xi": F(1, 3),
            "beta": BETA,
            "cross_inequalities": "both tight at 3/4",
        },
        "abstract": abstract,
        "exactified": exactified,
        "conclusion": (
            "paired first-stage certificates do not imply overlap >=2/3; "
            "singleton exactification preserves them but invalidates the trial "
            "full bottom stratum, and the recomputed Lmin has overlap exactly 2/3"
        ),
    }
    rendered = json.dumps(encode(report), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
