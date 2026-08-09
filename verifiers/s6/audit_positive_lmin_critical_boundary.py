#!/usr/bin/env python3
"""Map all 342 coupled Lmin critical rows to eight abstract lemmas."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402
from audit_positive_lmax_direction_layers import feasible_common_pairs  # noqa: E402
from export_positive_lmin_critical_boundary_smt import CASES  # noqa: E402
from search_positive_handover_directions import critical_all_witness_solver  # noqa: E402


EXPECTED = {
    "nnpppr-high": 60,
    "nnpppr-low": 104,
    "nnpppr-outer": 90,
    "npnppr-high": 24,
    "npnppr-low": 72,
    "npnppr-outer": 84,
    "nppnpr-high": 12,
    "nppnpr-outer": 24,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--layers",
        type=Path,
        default=HERE / "positive_lmin_handover_layers_audit.json",
    )
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    layers = json.loads(args.layers.read_text())["rows"]["critical"]
    survivors = json.loads(args.triage.read_text())["survivors"]
    mappings = []
    rows_by_pair_count = collections.Counter()
    counts = collections.Counter()
    mapped_rows = set()
    for row in layers:
        if row["payoff_critical"] != "sat":
            continue
        index = row["survivor_index"]
        configuration = survivors[index]
        _, labels, _ = critical_all_witness_solver(
            index, configuration, include_distance=False
        )
        cell = nsix.layout(
            6,
            tuple(configuration[0]),
            tuple(configuration[1]),
            tuple(tuple(values) for values in configuration[2]),
        )
        role = {player: "N" for player in labels["poor_players"]}
        role.update({player: "P" for player in labels["P_players"]})
        role[labels["rich_player"]] = "R"
        players = sorted(
            range(6),
            key=lambda player: (
                cell[player][0],
                {"N": 0, "P": 1, "R": 2}[role[player]],
                cell[player][1],
                player,
            ),
        )
        roles = tuple(role[player] for player in players)
        assert all(cell[players[i]][0] <= cell[players[i + 1]][0] for i in range(5))
        pairs = feasible_common_pairs(configuration, index, True)
        assert len(pairs) in (1, 3)
        rows_by_pair_count[len(pairs)] += 1
        mapped_rows.add(index)
        for pair in pairs:
            positions = tuple(sorted(players.index(player) for player in pair))
            candidates = [
                name
                for name, (case_roles, case_pair, _) in CASES.items()
                if case_roles == roles and case_pair == positions
            ]
            assert len(candidates) == 1
            case = candidates[0]
            _, _, (operator, first, second) = CASES[case]
            if operator == "eq":
                assert cell[players[first]][1] == cell[players[second]][1]
            else:
                assert cell[players[first]][1] <= cell[players[second]][1]
            counts[case] += 1
            mappings.append(
                {
                    "survivor_index": index,
                    "global_lmin_role_word": "".join(roles),
                    "common_pair_positions": list(positions),
                    "abstract_case": case,
                }
            )
    assert len(mapped_rows) == 342
    assert rows_by_pair_count == {1: 278, 3: 64}
    summary = dict(sorted(counts.items()))
    assert summary == EXPECTED
    payload = {
        "schema": "positive-lmin-critical-boundary-map-v1",
        "scope": "complete finite map to eight abstract exact-QF_LRA lemmas",
        "critical_rows": 342,
        "pair_instances": len(mappings),
        "rows_by_feasible_pair_count": dict(sorted(rows_by_pair_count.items())),
        "summary": summary,
        "mappings": mappings,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("critical_rows", "pair_instances", "rows_by_feasible_pair_count", "summary")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
