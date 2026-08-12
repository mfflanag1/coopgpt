#!/usr/bin/env python3
"""Exact audit of a normalized weighted four-role 3/4 obstruction."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402

WEIGHTS = (8, 1, 1, 1)
GENERATORS = (
    (F(0), F(5), F(3), F(4)),
    (F(1), F(3), F(3), F(5)),
    (F(2), F(4), F(3), F(3)),
    (F(5), F(0), F(7), F(0)),
    (F(0), F(6), F(0), F(6)),
)
EXPECTED_VALUES = tuple(map(F, (0, 0, 0, 4, 0, 0, 6, 6, 0, 4, 0, 5, 6, 6, 7, 12)))
EXPECTED_LMIN = tuple(map(F, (5, 1, 5, 1)))
EXPECTED_LMAX = tuple(map(F, (3, 3, 3, 3)))
BLOCKS = (tuple(range(8)), (8,), (9,), (10,))


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def role_values():
    values = tuple(
        min(coalition_sum(point, coalition) for point in GENERATORS)
        for coalition in range(16)
    )
    if values != EXPECTED_VALUES or any(sum(point, F(0)) != 12 for point in GENERATORS):
        raise AssertionError(("role envelope", values))
    if any(
        not any(coalition_sum(point, coalition) == values[coalition] for point in GENERATORS)
        for coalition in range(16)
    ):
        raise AssertionError("unattained role coalition")
    return values


def stage_rows(values, weights, pinned, free, mode):
    aub, bub = [], []
    for coalition in range(1, 15):
        aub.append([F(-1 if coalition >> i & 1 else 0) for i in range(4)] + [F(0)])
        bub.append(-values[coalition])
    aeq = [[F(1)] * 4 + [F(0)]]
    beq = [values[15]]
    for role, payoff in pinned.items():
        row = [F(0)] * 5
        row[role] = F(1)
        aeq.append(row)
        beq.append(payoff)
    for role in free:
        row = [F(0)] * 5
        if mode == "min":
            row[role], row[4] = F(-1), F(weights[role])
        else:
            row[role], row[4] = F(1), F(-weights[role])
        aub.append(row)
        bub.append(F(0))
    return aub, bub, aeq, beq


def weighted_lex_point(values, weights, mode):
    """Independent staged exact-LP encoding in role totals."""
    pinned, free, trace = {}, set(range(4)), []
    while free:
        aub, bub, aeq, beq = stage_rows(values, weights, pinned, free, mode)
        objective = [F(0)] * 5
        objective[4] = F(-1 if mode == "min" else 1)
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        if status != "optimal":
            raise AssertionError((mode, status))
        level = -optimum if mode == "min" else optimum
        level_row = [F(0)] * 5
        level_row[4] = F(1)
        aeq.append(level_row)
        beq.append(level)
        newly = []
        for role in sorted(free):
            direction = [F(0)] * 5
            direction[role] = F(-1 if mode == "min" else 1)
            status, extreme, _ = exact_linprog(direction, aub, bub, aeq, beq)
            if status != "optimal":
                raise AssertionError((mode, role, status))
            forced = -extreme if mode == "min" else extreme
            if forced == weights[role] * level:
                newly.append(role)
        if not newly:
            raise AssertionError((mode, "stage pinned nobody", level))
        for role in newly:
            pinned[role] = weights[role] * level
            free.remove(role)
        trace.append({"level": str(level), "newly_pinned_roles": newly})
    return tuple(pinned[i] for i in range(4)), trace


def completed_role_mask(coalition):
    return sum(
        1 << role
        for role, block in enumerate(BLOCKS)
        if all(coalition >> player & 1 for player in block)
    )


def clone_witness(role_point, coalition):
    allocation = [F(0)] * 11
    for role, block in enumerate(BLOCKS):
        if all(coalition >> player & 1 for player in block):
            allocation[block[0]] = role_point[role]
        elif any(coalition >> player & 1 for player in block):
            outside = next(player for player in block if not (coalition >> player & 1))
            allocation[outside] = role_point[role]
        else:
            allocation[block[0]] = role_point[role]
    return tuple(allocation)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values = role_values()
    parameter_rows = []
    for m in range(5, 41):
        weights = (m, 1, 1, 1)
        test_lmin, _ = weighted_lex_point(values, weights, "min")
        test_lmax, _ = weighted_lex_point(values, weights, "max")
        if test_lmin != EXPECTED_LMIN or test_lmax != EXPECTED_LMAX:
            raise AssertionError((m, test_lmin, test_lmax))
        parameter_rows.append({"m": m, "atomic_players": m + 3})
    lmin, lmin_trace = weighted_lex_point(values, WEIGHTS, "min")
    lmax, lmax_trace = weighted_lex_point(values, WEIGHTS, "max")
    if lmin != EXPECTED_LMIN or lmax != EXPECTED_LMAX:
        raise AssertionError((lmin, lmax))

    clone_values = tuple(values[completed_role_mask(S)] for S in range(1 << 11))
    for coalition in range(1 << 11):
        mask = completed_role_mask(coalition)
        attaining = next(p for p in GENERATORS if coalition_sum(p, mask) == values[mask])
        witness = clone_witness(attaining, coalition)
        if coalition_sum(witness, coalition) != clone_values[coalition]:
            raise AssertionError(("clone attainment", coalition))
        if any(coalition_sum(witness, other) < clone_values[other] for other in range(1 << 11)):
            raise AssertionError(("clone core witness", coalition))

    overlap = sum((min(a, b) for a, b in zip(lmin, lmax)), F(0))
    report = {
        "status": "normalized weighted four-role obstruction verified exactly",
        "role_weights": list(WEIGHTS),
        "symbolic_weight_family": "(m,1,1,1), m>=5",
        "exact_parameter_grid": parameter_rows,
        "lower_envelope_generators": [[str(q) for q in p] for p in GENERATORS],
        "role_values_binary_order": [str(value) for value in values],
        "weighted_lmin_role_totals": [str(q) for q in lmin],
        "weighted_lmax_role_totals": [str(q) for q in lmax],
        "lmin_trace": lmin_trace,
        "lmax_trace": lmax_trace,
        "role_singletons_zero": all(values[1 << role] == 0 for role in range(4)),
        "canonical_atomic_players": 11,
        "canonical_clone_coalitions_checked": 1 << 11,
        "total": "12",
        "overlap": str(overlap),
        "overlap_ratio": str(overlap / 12),
        "eleven_player_target": "11/30",
        "scope": "refutes a universal 3/4 normalized weighted four-role bound, not the atomic-player conjecture",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
