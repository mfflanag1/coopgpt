#!/usr/bin/env python3
"""Merge the complete exactness-aware starved exchange-menu census."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


EXCEPTION_POSITIONS = {154, 365}
EXCEPTION_INDICES = {932, 2332}


def load(paths, bound):
    rows = {}
    for path in paths:
        shard = json.loads(path.read_text())
        assert shard["schema"] == "starved-exactness-aware-menu-shard-v1"
        assert shard["source"] == "all" and shard["bound"] == bound
        assert shard["total"] == 504
        for row in shard["rows"]:
            position = row["position"]
            if position in rows:
                raise ValueError(f"duplicate bound-{bound} position {position}")
            rows[position] = row
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound-one-shards", type=Path, nargs="+", required=True)
    parser.add_argument("--exception-shards", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    bound_one = load(args.bound_one_shards, 1)
    exceptions = load(args.exception_shards, 2)
    assert set(bound_one) == set(range(504))
    assert {
        position for position, row in bound_one.items() if row["verdict"] == "sat"
    } == EXCEPTION_POSITIONS
    assert set(exceptions) == EXCEPTION_POSITIONS
    assert {row["survivor_index"] for row in exceptions.values()} == EXCEPTION_INDICES

    rows = []
    for position in range(504):
        row = exceptions.get(position, bound_one[position])
        assert row["verdict"] == "unsat"
        row = dict(row)
        row["search_bound"] = 2 if position in exceptions else 1
        rows.append(row)

    sides = Counter(row["side"] for row in rows)
    menu_sizes = Counter(row["menu_size"] for row in rows)
    direction_shapes = Counter(
        tuple(sorted(direction)) for row in rows for direction in row["menu"]
    )
    payload = {
        "schema": "starved-exactness-aware-menu-audit-v1",
        "scope": (
            "complete exact QF_LRA proof-discovery census using singleton-zero "
            "witnesses and ordinary exchange blockers; not proof objects"
        ),
        "starved_only_rows": 504,
        "bound_one_summary": {"unsat": 502, "sat": 2},
        "bound_two_exception_positions": sorted(EXCEPTION_POSITIONS),
        "bound_two_exception_survivor_indices": sorted(EXCEPTION_INDICES),
        "selected_side_summary": dict(sorted(sides.items())),
        "menu_size_summary": {
            str(size): count for size, count in sorted(menu_sizes.items())
        },
        "direction_shape_summary": {
            str(shape): count for shape, count in sorted(direction_shapes.items())
        },
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: payload[key]
                for key in (
                    "starved_only_rows",
                    "bound_one_summary",
                    "bound_two_exception_survivor_indices",
                    "selected_side_summary",
                    "menu_size_summary",
                    "direction_shape_summary",
                )
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
