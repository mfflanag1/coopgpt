#!/usr/bin/env python3
"""Audit the map from 504 starved rows to the two universal exchange branches."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402
from audit_equality_refinement_neighborhood import COARSE_TYPES, refines  # noqa: E402
from audit_starved_refinement_direction import coarse_roles  # noqa: E402
from audit_starved_universal_exchange_lemma import direction_family  # noqa: E402
from merge_starved_packet_handover import choose_lmax  # noqa: E402
from search_positive_handover_directions import lex_improves  # noqa: E402


def symbolic_lex_from_ranks(ranks, direction, side):
    if side == "min":
        return any(
            value > 0
            and all(
                ranks[player] >= ranks[pivot]
                for player, coefficient in enumerate(direction)
                if coefficient != 0
            )
            and all(
                ranks[player] > ranks[pivot]
                for player, coefficient in enumerate(direction)
                if coefficient < 0
            )
            for pivot, value in enumerate(direction)
        )
    return any(
        value < 0
        and all(
            ranks[player] <= ranks[pivot]
            for player, coefficient in enumerate(direction)
            if coefficient != 0
        )
        and all(
            ranks[player] < ranks[pivot]
            for player, coefficient in enumerate(direction)
            if coefficient > 0
        )
        for pivot, value in enumerate(direction)
    )


def digest(indices):
    return hashlib.sha256(",".join(map(str, indices)).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument(
        "--handover", type=Path, default=HERE / "starved_packet_handover_audit.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    survivors = json.loads(args.triage.read_text())["survivors"]
    handover = json.loads(args.handover.read_text())["rows"]
    starved, positive = COARSE_TYPES
    starved_indices = [
        index for index, configuration in enumerate(survivors) if refines(*configuration, starved)
    ]
    overlap_indices = [
        index for index in starved_indices if refines(*survivors[index], positive)
    ]
    starved_only_indices = sorted(row["survivor_index"] for row in handover)
    assert len(starved_indices) == 1352
    assert len(overlap_indices) == 848
    assert len(starved_only_indices) == 504
    assert set(starved_indices) == set(overlap_indices) | set(starved_only_indices)

    for index in starved_indices:
        cell, roles = coarse_roles(survivors[index], starved)
        rich_rows = {cell[player][0] for player, role in enumerate(roles) if role == "R"}
        assert (len(rich_rows) == 1) == (index in starved_only_indices)

    directions = direction_family()
    checks = 0
    selected = Counter()
    for row in handover:
        configuration = survivors[row["survivor_index"]]
        cell, roles = coarse_roles(configuration, starved)
        assert Counter(roles) == {"N": 2, "P": 2, "R": 2}
        rich_rows = {cell[player][0] for player, role in enumerate(roles) if role == "R"}
        assert len(rich_rows) == 1
        side = "max" if choose_lmax(configuration) else "min"
        assert side == row["selected_packet"]
        selected[side] += 1
        for checked_side in ("min", "max"):
            coordinate = 0 if checked_side == "min" else 1
            ranks = tuple(item[coordinate] for item in cell)
            for direction in directions:
                assert symbolic_lex_from_ranks(ranks, direction, checked_side) == lex_improves(
                    direction, cell, checked_side
                )
                checks += 1

    payload = {
        "schema": "starved-universal-exchange-mapping-audit-v1",
        "status": "PASS",
        "scope": "trust-free finite structural and predicate map; no solver verdicts",
        "starved_survivor_refinements": len(starved_indices),
        "positive_overlap_refinements": len(overlap_indices),
        "starved_only_refinements": len(starved_only_indices),
        "starved_only_iff_coarse_rich_lmin_pair_remains_tied": True,
        "starved_only_indices_sha256": digest(starved_only_indices),
        "selected_side_summary": dict(sorted(selected.items())),
        "universal_direction_count": len(directions),
        "symbolic_lex_predicate_checks": checks,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
