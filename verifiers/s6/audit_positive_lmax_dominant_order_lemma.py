#!/usr/bin/env python3
"""Check the order hypotheses of the uniform 80-row Lmax direction proof.

This audit performs no LP or SMT query.  It verifies directly from the two
stratum orders that every possible common P pair either forces the decreased
player p to have gap -A or is excluded by the gap-inversion lemma.  It also
checks the unique P player lying strictly below p in both orders.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402


EXPECTED = {
    "two_concordant_one_containing_p": 62,
    "three_concordant_two_containing_p": 18,
}


def relation(first, second):
    return "lt" if first < second else "gt" if first > second else "eq"


def labels(configuration, cell):
    row_sizes, column_sizes, _ = configuration
    poor = tuple(
        player
        for player, (_, column) in enumerate(cell)
        if sum(column_sizes[:column]) < 2
    )
    rich = next(
        player
        for player, (row, _) in enumerate(cell)
        if sum(row_sizes[:row]) == 5
    )
    middle = tuple(player for player in range(6) if player not in poor and player != rich)
    assert len(poor) == 2 and len(middle) == 3
    return poor, middle, rich


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--layers",
        type=Path,
        default=HERE / "positive_lmax_direction_layers_audit.json",
    )
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    layers = json.loads(args.layers.read_text())["rows"]
    survivors = json.loads(args.triage.read_text())["survivors"]
    counts = collections.Counter()
    rows = []
    for source_row in layers:
        if source_row["template"] != "N(0,0)_P(-1,0,0)_r1":
            continue
        index = source_row["survivor_index"]
        configuration = survivors[index]
        cell = nsix.layout(
            6,
            tuple(configuration[0]),
            tuple(configuration[1]),
            tuple(tuple(values) for values in configuration[2]),
        )
        poor, middle, rich = labels(configuration, cell)
        p = source_row["direction"].index(-1)
        assert p in middle and source_row["direction"][rich] == 1
        concordant = []
        for first, second in itertools.combinations(middle, 2):
            if relation(cell[first][0], cell[second][0]) == relation(
                cell[first][1], cell[second][1]
            ):
                concordant.append(tuple(sorted((first, second))))
        containing_p = [pair for pair in concordant if p in pair]
        assert containing_p
        resolutions = []
        for pair in concordant:
            if p in pair:
                resolutions.append({"pair": list(pair), "resolution": "contains_p"})
                continue
            shared = [player for player in pair if cell[player] == cell[p]]
            inverted_by = [
                player
                for player in pair
                if cell[p][0] <= cell[player][0]
                and cell[p][1] >= cell[player][1]
                and (cell[p][0] < cell[player][0] or cell[p][1] > cell[player][1])
            ]
            assert shared or inverted_by
            resolutions.append(
                {
                    "pair": list(pair),
                    "resolution": "shares_p_gap" if shared else "excluded_by_gap_inversion",
                    "witness_players": sorted(shared or inverted_by),
                }
            )
        low = [
            player
            for player in middle
            if cell[player][0] < cell[p][0] and cell[player][1] < cell[p][1]
        ]
        assert low == [source_row["forced_low_P_player"]]
        if (len(concordant), len(containing_p)) == (2, 1):
            classification = "two_concordant_one_containing_p"
        else:
            assert (len(concordant), len(containing_p)) == (3, 2)
            classification = "three_concordant_two_containing_p"
        counts[classification] += 1
        rows.append(
            {
                "survivor_index": index,
                "poor_players": list(poor),
                "P_players": list(middle),
                "rich_player": rich,
                "decreased_P_player": p,
                "unique_P_player_below_p_in_both_orders": low[0],
                "classification": classification,
                "concordant_pair_resolutions": resolutions,
            }
        )
    summary = dict(sorted(counts.items()))
    assert len(rows) == 80 and summary == EXPECTED
    payload = {
        "schema": "positive-lmax-dominant-order-lemma-audit-v1",
        "scope": "purely combinatorial finite map for the uniform 80-row Lmax proof",
        "row_count": len(rows),
        "summary": summary,
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"row_count": len(rows), "summary": summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
