#!/usr/bin/env python3
"""Test the coarse starved exchange direction on starved-only refinements."""

from __future__ import annotations

import argparse
import collections
import math
import json
import sys
from fractions import Fraction
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402
from audit_equality_refinement_neighborhood import COARSE_TYPES, refines  # noqa: E402


def point_sum(point, players):
    return z3.Sum(*[point[player] for player in players])


def coarse_roles(configuration, coarse):
    r, c, table = configuration
    row_groups = []
    start = 0
    for size in coarse["lmin"]:
        total = 0
        group = []
        while total < size:
            total += r[start]
            group.append(start)
            start += 1
        assert total == size
        row_groups.append(group)
    column_groups = []
    start = 0
    for size in coarse["lmax"]:
        total = 0
        group = []
        while total < size:
            total += c[start]
            group.append(start)
            start += 1
        assert total == size
        column_groups.append(group)
    row_coarse = {fine: group for group, fines in enumerate(row_groups) for fine in fines}
    column_coarse = {fine: group for group, fines in enumerate(column_groups) for fine in fines}
    cell = nsix.layout(6, tuple(r), tuple(c), tuple(tuple(values) for values in table))
    roles = []
    for row, column in cell:
        coarse_cell = (row_coarse[row], column_coarse[column])
        roles.append({(0, 0): "N", (0, 1): "P", (1, 1): "R"}[coarse_cell])
    assert collections.Counter(roles) == {"N": 2, "P": 2, "R": 2}
    return cell, tuple(roles)


def base_system(configuration, coarse):
    r, c, table = configuration
    solver = z3.Solver()
    m, big_m = nsix.levels(6, tuple(r), tuple(c), solver)
    cell, roles = coarse_roles(configuration, coarse)
    x = [m[cell[player][0]] for player in range(6)]
    z = [big_m[cell[player][1]] for player in range(6)]
    for player, role in enumerate(roles):
        solver.add(x[player] > z[player] if role in ("N", "R") else z[player] > x[player])
    distance = 2 * z3.Sum(*[x[player] - z[player] for player, role in enumerate(roles) if role in ("N", "R")])
    solver.add(distance > z3.RealVal("2/3"))
    return solver, x, z, cell, roles


def blocker_verdict(configuration, coarse, direction, side="min"):
    solver, x, z, _, roles = base_system(configuration, coarse)
    blockers = []
    for mask in range(1, (1 << 6) - 1):
        players = tuple(player for player in range(6) if mask >> player & 1)
        if sum(direction[player] for player in players) < 0:
            blockers.append(
                point_sum(z, players) >= point_sum(x, players)
                if side == "min"
                else point_sum(x, players) >= point_sum(z, players)
            )
    solver.add(z3.Or(*blockers))
    return str(solver.check()), roles


def eligible_masks(configuration, coarse, side):
    solver, x, z, cell, roles = base_system(configuration, coarse)
    masks = []
    for mask in range(1, (1 << 6) - 1):
        players = tuple(player for player in range(6) if mask >> player & 1)
        solver.push()
        solver.add(
            point_sum(z, players) >= point_sum(x, players)
            if side == "min"
            else point_sum(x, players) >= point_sum(z, players)
        )
        verdict = solver.check()
        solver.pop()
        if verdict == z3.sat:
            masks.append(mask)
        else:
            assert verdict == z3.unsat
    return tuple(masks), cell, roles


def integer_direction(values):
    fractions = [Fraction(value.numerator_as_long(), value.denominator_as_long()) for value in values]
    denominator = math.lcm(*(value.denominator for value in fractions))
    integers = [value.numerator * (denominator // value.denominator) for value in fractions]
    divisor = math.gcd(*[abs(value) for value in integers if value])
    return tuple(value // divisor for value in integers)


def separating_direction(masks, cell, side):
    coordinate = 0 if side == "min" else 1
    cutoffs = sorted(
        {item[coordinate] for item in cell}, reverse=(side == "max")
    )
    for cutoff in cutoffs:
        solver = z3.Solver()
        h = [z3.Real(f"starved_h_{player}") for player in range(6)]
        solver.add(z3.Sum(h) == 0)
        earlier = [
            player
            for player in range(6)
            if (cell[player][coordinate] < cutoff if side == "min" else cell[player][coordinate] > cutoff)
        ]
        first = [player for player in range(6) if cell[player][coordinate] == cutoff]
        solver.add(*[h[player] == 0 for player in earlier])
        solver.add(*[h[player] >= 0 if side == "min" else h[player] <= 0 for player in first])
        solver.add(
            z3.Sum(*[h[player] for player in first]) >= 1
            if side == "min"
            else z3.Sum(*[h[player] for player in first]) <= -1
        )
        for mask in masks:
            solver.add(z3.Sum(*[h[player] for player in range(6) if mask >> player & 1]) >= 0)
        if solver.check() == z3.sat:
            model = solver.model()
            return integer_direction([model.eval(value, model_completion=True) for value in h])
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    survivors = json.loads(args.triage.read_text())["survivors"]
    starved, positive = COARSE_TYPES
    rows = []
    counts = collections.Counter()
    for index, configuration in enumerate(survivors):
        if not refines(*configuration, starved) or refines(*configuration, positive):
            continue
        _, roles = coarse_roles(configuration, starved)
        direction = tuple({"N": 0, "P": 1, "R": -1}[role] for role in roles)
        verdict, _ = blocker_verdict(configuration, starved, direction)
        counts[verdict] += 1
        if verdict == "sat":
            masks, cell, _ = eligible_masks(configuration, starved, "min")
            separated = separating_direction(masks, cell, "min")
        else:
            separated = direction
        selected_side = "min" if separated is not None else None
        if separated is None:
            masks, cell, _ = eligible_masks(configuration, starved, "max")
            separated = separating_direction(masks, cell, "max")
            selected_side = "max" if separated is not None else None
        if separated is not None:
            separating_verdict, _ = blocker_verdict(
                configuration, starved, separated, selected_side
            )
            assert separating_verdict == "unsat"
        else:
            separating_verdict = None
        rows.append(
            {
                "survivor_index": index,
                "roles": "".join(roles),
                "direction": list(direction),
                "payoff_blocker_verdict": verdict,
                "separating_direction": list(separated) if separated is not None else None,
                "selected_side": selected_side,
                "separating_blocker_verdict": separating_verdict,
            }
        )
    assert len(rows) == 504
    payload = {
        "schema": "starved-refinement-coarse-direction-audit-v1",
        "scope": "payoff-only exact QF_LRA discovery audit; not proof objects",
        "starved_only_rows": len(rows),
        "verdict_summary": dict(sorted(counts.items())),
        "separated_rows": sum(row["separating_direction"] is not None for row in rows),
        "selected_side_summary": dict(
            sorted(collections.Counter(row["selected_side"] or "unresolved" for row in rows).items())
        ),
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"starved_only_rows": len(rows), "verdict_summary": dict(sorted(counts.items()))}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
