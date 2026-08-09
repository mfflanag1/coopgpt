#!/usr/bin/env python3
"""Enumerate the stratum/table refinements of the two equality types.

This is the finite combinatorial part of a possible first-crossing argument:
near a game with a fixed strict gap between coarse payoff levels, nearby
selection strata can split those levels but cannot cross the gap.  Hence their
ordered contingency table is a contiguous refinement of the equality table.

The script does not prove continuity of the selections or the first-crossing
argument.  It only audits the exact finite neighborhood and joins it to the
accepted strict/equality census verdicts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nsix  # noqa: E402


COARSE_TYPES = (
    {
        "name": "starved_4_2_by_2_4",
        "lmin": (4, 2),
        "lmax": (2, 4),
        "table": ((2, 2), (0, 2)),
        "survivor_index": 1408,
    },
    {
        "name": "positive_5_1_by_2_4",
        "lmin": (5, 1),
        "lmax": (2, 4),
        "table": ((2, 3), (0, 1)),
        "survivor_index": 2236,
    },
)


def key(r, c, table):
    return (tuple(r), tuple(c), tuple(tuple(row) for row in table))


def contiguous_groups(fine, coarse):
    groups = []
    start = 0
    for target in coarse:
        total = 0
        stop = start
        while stop < len(fine) and total < target:
            total += fine[stop]
            stop += 1
        if total != target:
            return None
        groups.append(tuple(range(start, stop)))
        start = stop
    return tuple(groups) if start == len(fine) else None


def refines(r, c, table, coarse):
    row_groups = contiguous_groups(r, coarse["lmin"])
    column_groups = contiguous_groups(c, coarse["lmax"])
    if row_groups is None or column_groups is None:
        return False
    aggregated = tuple(
        tuple(
            sum(table[i][j] for i in row_group for j in column_group)
            for column_group in column_groups
        )
        for row_group in row_groups
    )
    return aggregated == coarse["table"]


def verdict_map(report):
    return {
        key(row["lmin"], row["lmax"], row["table"]): row["result"]
        for row in report["rows"]
    }


def tally(values):
    values = tuple(values)
    return {label: sum(value == label for value in values) for label in ("sat", "unsat", "unknown")}


def index_digest(indices):
    payload = ",".join(str(index) for index in indices).encode()
    return hashlib.sha256(payload).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument(
        "--strict", type=Path, default=HERE / "core_generator_census.json"
    )
    parser.add_argument(
        "--triple", type=Path, default=HERE / "equality_triple_census.json"
    )
    parser.add_argument(
        "--no-triple", type=Path, default=HERE / "equality_no_triple_census.json"
    )
    args = parser.parse_args()

    triage = json.loads(args.triage.read_text())
    survivors = {key(*configuration) for configuration in triage["survivors"]}
    strict = verdict_map(json.loads(args.strict.read_text()))
    triple = verdict_map(json.loads(args.triple.read_text()))
    no_triple = verdict_map(json.loads(args.no_triple.read_text()))
    assert set(strict) == set(triple) == set(no_triple) == survivors

    universe = []
    for r in nsix.compositions(6):
        for c in nsix.compositions(6):
            for table in nsix.tables(r, c):
                universe.append((r, c, table))
    assert len(universe) == 37277

    reports = []
    union = set()
    immediate_union = set()
    for coarse in COARSE_TYPES:
        neighborhood = [
            (r, c, table) for r, c, table in universe if refines(r, c, table, coarse)
        ]
        keys = {key(r, c, table) for r, c, table in neighborhood}
        survivor_keys = keys & survivors
        union |= keys
        coarse_key = key(coarse["lmin"], coarse["lmax"], coarse["table"])
        assert coarse_key in survivor_keys
        strict_tally = tally(strict[item] for item in survivor_keys)
        triple_tally = tally(triple[item] for item in survivor_keys)
        no_triple_tally = tally(no_triple[item] for item in survivor_keys)
        equality_possible = sorted(
            item for item in survivor_keys if triple[item] == "sat" or no_triple[item] == "sat"
        )
        assert equality_possible == [coarse_key]
        survivor_indices = sorted(
            triage["survivors"].index(
                [list(item[0]), list(item[1]), [list(row) for row in item[2]]]
            )
            for item in survivor_keys
        )
        immediate_keys = {
            key(r, c, table)
            for r, c, table in neighborhood
            if (len(r) - len(coarse["lmin"]))
            + (len(c) - len(coarse["lmax"]))
            <= 1
        }
        immediate_union |= immediate_keys
        reports.append(
            {
                "name": coarse["name"],
                "coarse_lmin": coarse["lmin"],
                "coarse_lmax": coarse["lmax"],
                "coarse_table": coarse["table"],
                "survivor_index": coarse["survivor_index"],
                "universe_refinement_count": len(keys),
                "hand_net_survivor_refinement_count": len(survivor_keys),
                "strict_failure_tally_on_survivor_refinements": strict_tally,
                "equality_with_triple_tally_on_survivor_refinements": triple_tally,
                "equality_without_triple_tally_on_survivor_refinements": no_triple_tally,
                "equality_feasible_refinements": [
                    {
                        "lmin": item[0],
                        "lmax": item[1],
                        "table": item[2],
                    }
                    for item in equality_possible
                ],
                "immediate_refinement_count": len(immediate_keys),
                "immediate_hand_net_survivor_refinement_count": len(
                    immediate_keys & survivors
                ),
                "survivor_refinement_indices_sha256": index_digest(survivor_indices),
                "first_twenty_survivor_refinement_indices": survivor_indices[:20],
            }
        )

    union_survivors = union & survivors
    immediate_union_survivors = immediate_union & survivors
    immediate_union_indices = sorted(
        triage["survivors"].index(
            [list(item[0]), list(item[1]), [list(row) for row in item[2]]]
        )
        for item in immediate_union_survivors
    )
    report = {
        "status": (
            "exact refinement-neighborhood enumeration joined to census verdicts; "
            "the first-crossing continuity argument remains a separate proof obligation"
        ),
        "universe_count": len(universe),
        "union_refinement_count": len(union),
        "union_hand_net_survivor_refinement_count": len(union_survivors),
        "immediate_union_refinement_count": len(immediate_union),
        "immediate_union_hand_net_survivor_refinement_count": len(
            immediate_union_survivors
        ),
        "immediate_union_survivor_indices": immediate_union_indices,
        "strict_failure_tally_on_union_survivors": tally(
            strict[item] for item in union_survivors
        ),
        "strict_failure_tally_on_immediate_union_survivors": tally(
            strict[item] for item in immediate_union_survivors
        ),
        "types": reports,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
