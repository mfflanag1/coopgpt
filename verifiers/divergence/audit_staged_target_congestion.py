#!/usr/bin/env python3
"""Exact audit of the staged target-count congestion conjecture.

For every payoff stage and every player that gains from Lmin to Lmax, jointly
choose sign-coherent pinning certificates and minimize the largest auxiliary
unit-column load.  The candidate Lmin inequality is

    minimum congestion <= number of gaining targets in the stage.

The script also audits the formal Lmax mirror, which is false, and records an
exact counterexample.  Finite success on the Lmin side is discovery evidence
only; the conjecture remains unproved.
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


def payoff_blocks(point: tuple[F, ...], mode: str) -> tuple[tuple[int, ...], ...]:
    levels = sorted(set(point), reverse=(mode == "max"))
    return tuple(tuple(i for i, value in enumerate(point) if value == level) for level in levels)


def minimum_stage_congestion(
    values: tuple[F, ...],
    x: tuple[F, ...],
    z: tuple[F, ...],
    mode: str,
    stage: int,
) -> tuple[tuple[int, ...], F]:
    """Return the gaining targets and exact minimum auxiliary column load."""
    point = x if mode == "min" else z
    side_sign = F(1 if mode == "min" else -1)
    n = len(point)
    full = (1 << n) - 1
    blocks = payoff_blocks(point, mode)
    old = tuple(i for block in blocks[:stage] for i in block)
    current = blocks[stage]
    cumulative = old + current
    targets = tuple(i for i in current if z[i] > x[i])
    if not targets:
        return targets, F(0)
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(point, coalition) == values[coalition]
    )

    m = len(tight)
    block_width = m + len(cumulative) + 1
    kappa_index = len(targets) * block_width
    width = kappa_index + 1

    def lam(target_pos: int, coalition_pos: int) -> int:
        return target_pos * block_width + coalition_pos

    def auxiliary(target_pos: int, player_pos: int) -> int:
        return target_pos * block_width + m + player_pos

    def efficiency(target_pos: int) -> int:
        return target_pos * block_width + m + len(cumulative)

    equalities: list[list[F]] = []
    rhs: list[F] = []
    for target_pos, target in enumerate(targets):
        for player in range(n):
            row = [F(0)] * width
            for coalition_pos, coalition in enumerate(tight):
                row[lam(target_pos, coalition_pos)] = F(
                    int(bool(coalition >> player & 1))
                )
            if player in cumulative:
                row[auxiliary(target_pos, cumulative.index(player))] = side_sign
            row[efficiency(target_pos)] = F(-1)
            equalities.append(row)
            rhs.append(-side_sign * F(int(player == target)))

    inequalities: list[list[F]] = []
    inequality_rhs: list[F] = []
    # Coalition, auxiliary, and congestion variables are nonnegative;
    # efficiency multipliers are free on both sides.
    nonnegative = set(range(width))
    for target_pos in range(len(targets)):
        nonnegative.remove(efficiency(target_pos))
    for variable in sorted(nonnegative):
        row = [F(0)] * width
        row[variable] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))
    for player_pos in range(len(cumulative)):
        row = [F(0)] * width
        for target_pos in range(len(targets)):
            row[auxiliary(target_pos, player_pos)] = F(1)
        row[kappa_index] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))

    objective = [F(0)] * width
    objective[kappa_index] = F(1)
    status, optimum, _solution = exact_linprog(
        objective,
        inequalities,
        inequality_rhs,
        equalities,
        rhs,
    )
    if status != "optimal":
        raise RuntimeError(status)
    return targets, optimum


def n7_control() -> tuple[tuple[F, ...], tuple[F, ...], tuple[F, ...]]:
    g = tuple(map(F, (0, 5, 0, 3, 2, 0, 0)))
    h = tuple(map(F, (1, 0, 2, 0, 0, 5, 2)))
    values = tuple(
        min(coalition_sum(g, mask), coalition_sum(h, mask))
        for mask in range(1 << 7)
    )
    x = tuple(map(F, (1, 2, 1, 1, 1, 3, 1)))
    z = (F(5, 6), F(5, 2), F(5, 6), F(4, 3), F(7, 6), F(5, 2), F(5, 6))
    return values, x, z


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--include-n7-control", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = {
        mode: {
            "nontrivial_stages": 0,
            "target_count_bound_failures": 0,
            "maximum_congestion_per_target": F(0),
            "first_failure": None,
        }
        for mode in ("min", "max")
    }
    pair_count = 0
    for source in args.paths:
        data = json.loads(source.read_text())
        for _source, trail, values, x, z in records(data, source):
            if len(x) != args.n:
                continue
            pair_count += 1
            for mode, point in (("min", x), ("max", z)):
                for stage in range(len(payoff_blocks(point, mode))):
                    targets, congestion = minimum_stage_congestion(
                        values, x, z, mode, stage
                    )
                    if not targets:
                        continue
                    row = summary[mode]
                    row["nontrivial_stages"] += 1
                    normalized = congestion / len(targets)
                    row["maximum_congestion_per_target"] = max(
                        row["maximum_congestion_per_target"], normalized
                    )
                    if congestion > len(targets):
                        row["target_count_bound_failures"] += 1
                        if row["first_failure"] is None:
                            row["first_failure"] = {
                                "source": str(source),
                                "trail": trail,
                                "stage": stage,
                                "targets": list(targets),
                                "target_count": len(targets),
                                "minimum_congestion": str(congestion),
                            }

    n7_rows = []
    if args.include_n7_control:
        values, x, z = n7_control()
        for mode, point in (("min", x), ("max", z)):
            for stage in range(len(payoff_blocks(point, mode))):
                targets, congestion = minimum_stage_congestion(
                    values, x, z, mode, stage
                )
                if targets:
                    n7_rows.append(
                        {
                            "mode": mode,
                            "stage": stage,
                            "targets": list(targets),
                            "target_count": len(targets),
                            "minimum_congestion": str(congestion),
                        }
                    )

    report = {
        "status": "exact rational conjecture audit with a negative mirror control",
        "archive_dimension": args.n,
        "archive_pairs": pair_count,
        "lmin": {
            **summary["min"],
            "maximum_congestion_per_target": str(
                summary["min"]["maximum_congestion_per_target"]
            ),
            "interpretation": "finite evidence only; target-count cap remains conjectural",
        },
        "lmax_mirror": {
            **summary["max"],
            "maximum_congestion_per_target": str(
                summary["max"]["maximum_congestion_per_target"]
            ),
            "interpretation": "the formal mirror is false",
        },
        "n7_hostile_control": n7_rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
