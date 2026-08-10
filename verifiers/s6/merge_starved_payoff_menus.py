#!/usr/bin/env python3
"""Merge complete bound-two starved payoff-menu search shards."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def load_rows(paths, side):
    rows = {}
    for path in paths:
        shard = json.loads(path.read_text())
        assert shard["schema"] == "starved-payoff-menu-search-shard-v1"
        assert shard["bound"] == 2 and side in shard["sides"]
        for row in shard["rows"]:
            position = row["position"]
            if position in rows:
                raise ValueError(f"duplicate {side} position {position}")
            rows[position] = row
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-shards", type=Path, nargs="+", required=True)
    parser.add_argument("--max-shards", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    minimum = load_rows(args.min_shards, "min")
    maximum = load_rows(args.max_shards, "max")
    assert set(minimum) == set(range(282))
    expected_maximum = {
        position for position, row in minimum.items() if row["min"]["verdict"] == "sat"
    }
    assert set(maximum) == expected_maximum
    counts = collections.Counter()
    menu_sizes = collections.Counter()
    rows = []
    for position in range(282):
        min_row = minimum[position]
        assert min_row["min"]["verdict"] in ("sat", "unsat")
        if min_row["min"]["verdict"] == "unsat":
            classification = "lmin_payoff_menu"
            side = "min"
            menu = min_row["min"]["menu"]
        else:
            max_row = maximum[position]
            assert max_row["survivor_index"] == min_row["survivor_index"]
            assert max_row["max"]["verdict"] in ("sat", "unsat")
            if max_row["max"]["verdict"] == "unsat":
                classification = "lmax_payoff_menu"
                side = "max"
                menu = max_row["max"]["menu"]
            else:
                classification = "staged_residue"
                side = None
                menu = []
        counts[classification] += 1
        if menu:
            menu_sizes[(side, len(menu))] += 1
        rows.append(
            {
                "position": position,
                "survivor_index": min_row["survivor_index"],
                "classification": classification,
                "selected_side": side,
                "minimized_menu": menu,
            }
        )
    assert counts == {
        "lmin_payoff_menu": 140,
        "lmax_payoff_menu": 11,
        "staged_residue": 131,
    }
    payload = {
        "schema": "starved-payoff-menu-audit-v1",
        "scope": "complete bound-two payoff-only exact QF_LRA discovery audit; not proof objects",
        "input_single_direction_residue": 282,
        "summary": dict(sorted(counts.items())),
        "menu_size_summary": {
            f"{side}_size_{size}": count
            for (side, size), count in sorted(menu_sizes.items())
        },
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("input_single_direction_residue", "summary", "menu_size_summary")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
