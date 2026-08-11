#!/usr/bin/env python3
"""Exact audit of sign-coherent lifts for complete staged pinning circuits.

The human theorem shows that earlier pinning relations recursively eliminate
the free-sign old-pin coefficients.  This script independently asks the exact
rational feasibility LP for a lift with the normalized signs at every stage:

* Lmin: all old-pin coefficients are nonnegative;
* Lmax: all old-pin coefficients are nonpositive.

Passing a finite archive is only a regression check; the recursive argument
in HYBRID_OVERLAP_FACET_PROGRAM.md is the dimension-free proof.
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


def has_sign_coherent_lift(
    values: tuple[F, ...],
    point: tuple[F, ...],
    mode: str,
    stage: int,
    player: int,
) -> bool:
    """Solve the incidence relation with the asserted old-pin orientation."""
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
    q_index = {j: m + k for k, j in enumerate(old)}
    r_index = {j: m + len(old) + k for k, j in enumerate(current)}
    c_index = m + len(old) + len(current)
    width = c_index + 1

    equalities: list[list[F]] = []
    rhs: list[F] = []
    side_sign = F(1 if mode == "min" else -1)
    for coordinate in range(n):
        row = [F(0)] * width
        for k, coalition in enumerate(tight):
            row[k] = F(int(bool(coalition >> coordinate & 1)))
        if coordinate in q_index:
            row[q_index[coordinate]] = F(1)
        if coordinate in r_index:
            row[r_index[coordinate]] = side_sign
        row[c_index] = F(-1)
        equalities.append(row)
        rhs.append(-side_sign * F(int(coordinate == player)))

    inequalities: list[list[F]] = []
    inequality_rhs: list[F] = []
    # Coalition and current-side multipliers are nonnegative.
    for variable in tuple(range(m)) + tuple(r_index.values()):
        row = [F(0)] * width
        row[variable] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))
    # Old multipliers have the recursively normalized sign.
    for variable in q_index.values():
        row = [F(0)] * width
        row[variable] = F(-1 if mode == "min" else 1)
        inequalities.append(row)
        inequality_rhs.append(F(0))

    status, _objective, _solution = exact_linprog(
        [F(0)] * width,
        inequalities,
        inequality_rhs,
        equalities,
        rhs,
    )
    return status == "optimal"


def audit_pair(values: tuple[F, ...], x: tuple[F, ...], z: tuple[F, ...]) -> tuple[int, list[dict]]:
    checked = 0
    failures = []
    for mode, point in (("min", x), ("max", z)):
        for stage, block in enumerate(payoff_blocks(point, mode)):
            for player in block:
                checked += 1
                if not has_sign_coherent_lift(values, point, mode, stage, player):
                    failures.append({"mode": mode, "stage": stage, "player": player})
    return checked, failures


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
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--include-n7-control", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])

    pairs = 0
    certificates = 0
    failures = []
    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for _source, trail, values, x, z in records(data, source):
            if len(x) != args.n:
                continue
            pairs += 1
            checked, pair_failures = audit_pair(values, x, z)
            certificates += checked
            for failure in pair_failures:
                failures.append({"source": str(source), "trail": trail, **failure})

    n7_checked = 0
    n7_failures = []
    if args.include_n7_control:
        n7_checked, n7_failures = audit_pair(*n7_control())

    if failures or n7_failures:
        raise AssertionError({"archive": failures, "n7": n7_failures})
    report = {
        "status": "exact rational regression audit; human proof is dimension-free",
        "archive_dimension": args.n,
        "archive_pairs": pairs,
        "archive_stage_player_certificates": certificates,
        "archive_failures": 0,
        "n7_hostile_control_included": args.include_n7_control,
        "n7_stage_player_certificates": n7_checked,
        "n7_failures": 0,
        "asserted_orientation": {
            "lmin_old_pin_weights": ">= 0",
            "lmax_old_pin_weights": "<= 0",
        },
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
