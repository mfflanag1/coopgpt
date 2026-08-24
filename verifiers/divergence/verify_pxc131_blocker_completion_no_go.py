#!/usr/bin/env python3
"""Exact audit of the PXC131 nontrivial blocker-completion no-go.

PXC131's equivalence is an LP-duality theorem in the manuscript.  This audit
reconstructs the PXC101 and PXC104 lower-envelope games, deletes one blocker
inequality from the full core description, and solves the resulting rational
LP exactly.  Each blocker is irredundant, so exactness alone cannot complete
it to an active exceptional-set packet supported away from itself.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
ARCHIVE = HERE.parent / "search_archive"
sys.path[:0] = [str(ARCHIVE), str(ROOT / "src")]

from exactlp import exact_linprog  # noqa: E402
from unrestricted_pxc91c_exact_search import lower_envelope  # noqa: E402


def csum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def reduced_minimum(values, exceptional):
    n = (len(values) - 1).bit_length()
    full = (1 << n) - 1
    aub, bub = [], []
    for row in range(1, full):
        if row == exceptional:
            continue
        aub.append([-F((row >> i) & 1) for i in range(n)])
        bub.append(-values[row])
    for i in range(n):
        row = [F(0)] * n
        row[i] = -1
        aub.append(row)
        bub.append(F(0))
    objective = [F((exceptional >> i) & 1) for i in range(n)]
    status, value, point = exact_linprog(
        objective, aub, bub, [[F(1)] * n], [values[full]]
    )
    if status != "optimal":
        raise AssertionError((exceptional, status))
    violations = tuple(
        row for row in range(1, full)
        if row != exceptional and csum(point, row) < values[row]
    )
    if violations:
        raise AssertionError((exceptional, violations))
    return value, tuple(point)


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    games = {
        "PXC101_six_player_forced_zero": {
            "total": F(17),
            "constraints": {7: F(11), 11: F(11), 17: F(6), 51: F(11)},
            "blockers": (17,),
            "expected": {17: (F(3), (F(3), F(5), F(3), F(3), F(0), F(3)))},
        },
        "PXC104_reciprocal_cross_blockers": {
            "total": F(23),
            "constraints": {
                7: F(16), 11: F(16), 19: F(13),
                23: F(18), 35: F(13), 39: F(18),
            },
            "blockers": (23, 39),
            "expected": {
                23: (F(16), (F(16), F(0), F(0), F(5), F(0), F(2))),
                39: (F(16), (F(16), F(0), F(0), F(5), F(2), F(0))),
            },
        },
    }
    records = []
    for name, game in games.items():
        values = lower_envelope(game["constraints"], 6, game["total"])
        for blocker in game["blockers"]:
            value, point = reduced_minimum(values, blocker)
            expected_value, expected_point = game["expected"][blocker]
            if (value, point) != (expected_value, expected_point):
                raise AssertionError((name, blocker, value, point))
            if value >= values[blocker]:
                raise AssertionError((name, blocker, "blocker unexpectedly redundant"))
            records.append({
                "game": name,
                "blocker": blocker,
                "blocker_worth": values[blocker],
                "minimum_after_deleting_only_blocker_row": value,
                "strict_irredundancy_gap": values[blocker] - value,
                "minimizer": point,
                "all_other_core_rows_satisfied": True,
            })
    payload = {
        "claim": "PXC131 nontrivial exceptional-packet completion criterion and blocker no-go",
        "records": records,
        "scope": {
            "proved_conventionally": (
                "an active exceptional-set packet supported off E exists iff the E core "
                "inequality is implied by all other core inequalities"
            ),
            "exact_no_go": (
                "the PXC101 forced-zero blocker and both PXC104 cross blockers are "
                "irredundant, so exactness alone cannot produce such a completion"
            ),
            "not_proved": (
                "absence of mixed-colour witness packets with a different exceptional set"
            ),
        },
    }
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
