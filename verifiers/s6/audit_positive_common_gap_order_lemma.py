#!/usr/bin/env python3
"""Check the combinatorial hypotheses of the common-gap order lemma.

No LP or SMT verdict is computed here.  The audit reads the payoff-only row
set, reconstructs the two weak orders from each contingency table, and checks
the two alternatives used by the human proof:

* no P pair has the same weak relation in Lmin and Lmax; or
* exactly one pair is concordant, and the third P player is strictly
  gap-dominated by both members of that pair.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402


EXPECTED = {
    "no_concordant_pair": 361,
    "unique_concordant_pair_with_double_inversion": 412,
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
        "--source",
        type=Path,
        default=HERE / "positive_common_gap_pair_audit.json",
    )
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.source.read_text())
    survivors = json.loads(args.triage.read_text())["survivors"]
    counts = collections.Counter()
    rows = []
    for source_row in source["rows"]:
        index = source_row["survivor_index"]
        configuration = survivors[index]
        cell = nsix.layout(
            6,
            tuple(configuration[0]),
            tuple(configuration[1]),
            tuple(tuple(values) for values in configuration[2]),
        )
        _, middle, _ = labels(configuration, cell)
        concordant = []
        for first_position in range(3):
            for second_position in range(first_position + 1, 3):
                first, second = middle[first_position], middle[second_position]
                if relation(cell[first][0], cell[second][0]) == relation(
                    cell[first][1], cell[second][1]
                ):
                    concordant.append(tuple(sorted((first, second))))
        if not concordant:
            classification = "no_concordant_pair"
            assert source_row["classification"] == "no_order_feasible_pair"
            extra = {}
        else:
            assert len(concordant) == 1
            pair = concordant[0]
            third = next(player for player in middle if player not in pair)
            inverted_by = []
            for player in pair:
                x_weak = cell[third][0] <= cell[player][0]
                z_weak = cell[third][1] >= cell[player][1]
                strict = cell[third][0] < cell[player][0] or cell[third][1] > cell[player][1]
                if x_weak and z_weak and strict:
                    inverted_by.append(player)
            assert tuple(sorted(inverted_by)) == pair
            classification = "unique_concordant_pair_with_double_inversion"
            assert source_row["classification"] == "unique_pair_third_gap_fails"
            extra = {
                "third_P_player": third,
                "strictly_gap_dominated_by": list(pair),
            }
        counts[classification] += 1
        rows.append(
            {
                "selected_side": source_row["selected_side"],
                "survivor_index": index,
                "P_players": list(middle),
                "concordant_pairs": [list(pair) for pair in concordant],
                "classification": classification,
                **extra,
            }
        )
    summary = dict(sorted(counts.items()))
    assert summary == EXPECTED
    payload = {
        "schema": "positive-common-gap-order-lemma-audit-v1",
        "scope": "purely combinatorial finite map for the human common-gap order lemma",
        "row_count": len(rows),
        "summary": summary,
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"row_count": len(rows), "summary": summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
