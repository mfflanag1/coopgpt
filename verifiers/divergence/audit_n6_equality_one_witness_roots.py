#!/usr/bin/env python3
"""Exact one-witness root audit on the five archived n=6 equality games.

This reads only records attaining normalized overlap 2/3, extracts one exact
complete staged support for each selection, and computes all six rooted
three-generator relaxation minima.  It is a sharp-layer audit, not a census
proof of the six-player or all-n theorem.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from verify_labelled_branch_duals import branch_system, one_witness_minimum  # noqa: E402


def stage_support(values, point, mode, stage, player):
    """Return the coalition support of one exact staged basic certificate."""
    n = len(point)
    full = (1 << n) - 1
    blocks = payoff_blocks(point, mode)
    old = tuple(i for block in blocks[:stage] for i in block)
    current = blocks[stage]
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(point, coalition) == values[coalition]
    )
    m = len(tight)
    old_index = {j: m + k for k, j in enumerate(old)}
    side_index = {j: m + len(old) + k for k, j in enumerate(current)}
    constant_index = m + len(old) + len(current)
    width = constant_index + 1
    side = F(1 if mode == "min" else -1)

    equalities, equality_rhs = [], []
    for coordinate in range(n):
        row = [F(0)] * width
        for k, coalition in enumerate(tight):
            row[k] = F((coalition >> coordinate) & 1)
        if coordinate in old_index:
            row[old_index[coordinate]] = 1
        if coordinate in side_index:
            row[side_index[coordinate]] = side
        row[constant_index] = -1
        equalities.append(row)
        equality_rhs.append(-side * F(coordinate == player))

    inequalities, inequality_rhs = [], []
    for variable in tuple(range(m)) + tuple(side_index.values()):
        row = [F(0)] * width
        row[variable] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))
    for variable in old_index.values():
        row = [F(0)] * width
        row[variable] = F(-1 if mode == "min" else 1)
        inequalities.append(row)
        inequality_rhs.append(F(0))

    status, _objective, solution = exact_linprog(
        [F(0)] * width,
        inequalities,
        inequality_rhs,
        equalities,
        equality_rhs,
    )
    assert status == "optimal"
    return tuple(tight[k] for k in range(m) if solution[k] > 0)


def audit_record(source, trail, values, x, z):
    n = len(x)
    total = sum(x, F(0))
    support_x, support_z = set(), set()
    for mode, point, support in (("min", x, support_x), ("max", z, support_z)):
        for stage, block in enumerate(payoff_blocks(point, mode)):
            for player in block:
                support.update(stage_support(values, point, mode, stage, player))

    case = {
        "x": x,
        "z": z,
        "g": (total,) + (F(0),) * (n - 1),
        "support_x": tuple(sorted(support_x)),
        "support_z": tuple(sorted(support_z)),
    }
    system = branch_system(case)
    bounds = tuple(one_witness_minimum(system, player) for player in range(n))
    target = F(2, 3)
    passing = tuple(player for player, bound in enumerate(bounds) if bound >= target)
    overlap_coordinates = tuple(min(x[i], z[i]) / total for i in range(n))
    maximum_overlap_roots = tuple(
        i for i, value in enumerate(overlap_coordinates) if value == max(overlap_coordinates)
    )
    assert passing
    assert set(maximum_overlap_roots) <= set(passing)
    return {
        "source": source.name,
        "trail": trail,
        "total": str(total),
        "support_sizes": {"lmin": len(support_x), "lmax": len(support_z)},
        "root_bounds": [str(bound) for bound in bounds],
        "passing_roots": list(passing),
        "maximum_overlap_roots": list(maximum_overlap_roots),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = []
    for source in args.paths:
        data = json.loads(source.read_text())
        for parsed_source, trail, values, x, z in records(data, source):
            total = sum(x, F(0))
            overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
            if len(x) == 6 and 3 * overlap == 2 * total:
                cases.append(audit_record(parsed_source, trail, values, x, z))
    assert len(cases) == 5
    report = {
        "status": "exact rational one-witness audit of all five archived n=6 equality records",
        "cases": cases,
        "all_cases_have_passing_root": True,
        "all_maximum_overlap_roots_pass": True,
        "scope": "five archived equality records only; not a proof of root selection",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
