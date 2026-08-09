#!/usr/bin/env python3
"""Freeze one positive-handover obstruction as exact SMT-LIB.

The selected direction is read from a committed handover artifact rather than
copied into this exporter.  The formula rebuilds the critical-triple system,
all six exactness witnesses, and the disjunction of coalitional blockers for
that direction.  An UNSAT result therefore says that the displayed exchange
direction is feasible throughout the selected critical support type.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from export_core_closure_smt import qf_lra_smt2  # noqa: E402
from search_positive_handover_directions import (  # noqa: E402
    blocker_formula,
    critical_all_witness_solver,
    lex_improves,
)
import nsix  # noqa: E402


def artifact_row(index: int, artifact: Path) -> dict:
    rows = json.loads(artifact.read_text())["rows"]
    matches = [row for row in rows if row["survivor_index"] == index]
    if len(matches) != 1:
        raise ValueError(
            f"expected one row for survivor {index}, found {len(matches)}"
        )
    return matches[0]


def build(index: int, triage: Path, artifact: Path):
    survivors = json.loads(triage.read_text())["survivors"]
    if not 0 <= index < len(survivors):
        raise ValueError(f"index must lie in [0,{len(survivors)})")
    configuration = survivors[index]
    row = artifact_row(index, artifact)
    if row["configuration"] != configuration:
        raise ValueError("artifact configuration does not match triage source")
    if row.get("critical_algebra_verdict") != "sat":
        raise ValueError("selected row is not a direction-obstruction case")
    if row.get("direction") is None:
        raise ValueError("selected row has no single improving direction")

    side = row["selected_side"]
    direction = tuple(row["direction"])
    cell = nsix.layout(
        6,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(values) for values in configuration[2]),
    )
    if not lex_improves(direction, cell, side):
        raise ValueError("artifact direction does not lexicographically improve")

    solver, labels, witnesses = critical_all_witness_solver(index, configuration)
    for key in ("poor_players", "P_players", "rich_player", "triple_masks"):
        if row[key] != labels[key]:
            raise ValueError(f"artifact label {key} does not match reconstruction")
    blocker, masks = blocker_formula(
        index, configuration, direction, side, witnesses
    )
    if len(masks) != row["syntactic_negative_mask_count"]:
        raise ValueError("artifact blocker-mask count does not match reconstruction")
    solver.add(blocker)
    return solver


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument(
        "--artifact",
        type=Path,
        default=HERE / "positive_lmax_handover_directions.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(
        qf_lra_smt2(build(args.index, args.triage, args.artifact))
    )


if __name__ == "__main__":
    main()
