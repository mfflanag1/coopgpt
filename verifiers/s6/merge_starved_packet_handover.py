#!/usr/bin/env python3
"""Merge complete starved one-sided-packet shards and check the separator."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_equality_refinement_neighborhood import COARSE_TYPES  # noqa: E402
from audit_starved_refinement_direction import coarse_roles  # noqa: E402


def choose_lmax(configuration):
    cell, roles = coarse_roles(configuration, COARSE_TYPES[0])
    p_columns = [cell[player][1] for player, role in enumerate(roles) if role == "P"]
    r_columns = [cell[player][1] for player, role in enumerate(roles) if role == "R"]
    return min(r_columns) < min(p_columns)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("shards", type=Path, nargs="+")
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    survivors = json.loads(args.triage.read_text())["survivors"]
    by_position = {}
    for path in args.shards:
        shard = json.loads(path.read_text())
        assert shard["schema"] == "starved-one-sided-packet-handover-shard-v1"
        assert shard["total"] == 504
        assert len(shard["rows"]) == shard["stop"] - shard["start"]
        for row in shard["rows"]:
            position = row["position"]
            if position in by_position:
                raise ValueError(f"duplicate position {position}")
            assert row["min"] in ("sat", "unsat") and row["max"] in ("sat", "unsat")
            by_position[position] = row
    assert set(by_position) == set(range(504))
    rows = [by_position[position] for position in range(504)]
    joint = collections.Counter((row["min"], row["max"]) for row in rows)
    assert joint[("sat", "sat")] == 0
    selected = collections.Counter()
    rendered_rows = []
    for row in rows:
        side = "max" if choose_lmax(survivors[row["survivor_index"]]) else "min"
        assert row[side] == "unsat"
        selected[side] += 1
        rendered_rows.append({**row, "selected_packet": side})
    assert selected == {"max": 128, "min": 376}
    payload = {
        "schema": "starved-one-sided-packet-handover-audit-v1",
        "scope": "complete exact QF_LRA solver census; not independent proof objects",
        "starved_only_rows": len(rows),
        "joint_verdict_summary": {
            f"min_{minimum}__max_{maximum}": count
            for (minimum, maximum), count in sorted(joint.items())
            if count
        },
        "intersection_of_one_sided_sat_sets": 0,
        "handover_rule": (
            "choose Lmax iff at least one coarse-rich player is strictly below "
            "both coarse-P players in the refined Lmax order; choose Lmin otherwise"
        ),
        "selected_packet_summary": dict(sorted(selected.items())),
        "selected_packet_unsat_in_every_row": True,
        "rows": rendered_rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("starved_only_rows", "joint_verdict_summary", "selected_packet_summary", "selected_packet_unsat_in_every_row")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
