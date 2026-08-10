#!/usr/bin/env python3
"""Search small payoff-only exchange menus on the starved direction residue."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_equality_refinement_neighborhood import COARSE_TYPES  # noqa: E402
from audit_starved_refinement_direction import base_system, point_sum  # noqa: E402
from search_positive_handover_directions import direction_pool, lex_improves  # noqa: E402


def blocker_formula(x, z, direction, side):
    blockers = []
    for mask in range(1, (1 << 6) - 1):
        players = tuple(player for player in range(6) if mask >> player & 1)
        if sum(direction[player] for player in players) >= 0:
            continue
        blockers.append(
            point_sum(z, players) >= point_sum(x, players)
            if side == "min"
            else point_sum(x, players) >= point_sum(z, players)
        )
    return z3.Or(*blockers)


def menu(configuration, pool, side, timeout_ms):
    solver, x, z, cell, _ = base_system(configuration, COARSE_TYPES[0])
    solver.set(timeout=timeout_ms, unsat_core=True)
    tags = {}
    for number, direction in enumerate(pool):
        if not lex_improves(direction, cell, side):
            continue
        tag = z3.Bool(f"starved_menu_{side}_{number}")
        tags[tag] = direction
        solver.add(z3.Implies(tag, blocker_formula(x, z, direction, side)))
    verdict = solver.check(*tags)
    if verdict != z3.unsat:
        return str(verdict), ()
    core = list(solver.unsat_core())
    changed = True
    while changed:
        changed = False
        for tag in tuple(core):
            trial = [candidate for candidate in core if candidate is not tag]
            if solver.check(*trial) == z3.unsat:
                core = trial
                changed = True
                break
    return "unsat", tuple(tags[tag] for tag in core)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directions", type=Path, default=HERE / "starved_refinement_direction_audit.json")
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--bound", type=int, default=1)
    parser.add_argument("--side", choices=("min", "max", "both"), default="both")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument("--filter-min-sat-shards", type=Path, nargs="*")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    directions = json.loads(args.directions.read_text())
    survivors = json.loads(args.triage.read_text())["survivors"]
    residue = [row for row in directions["rows"] if row["separating_direction"] is None]
    assert len(residue) == 282
    stop = len(residue) if args.stop is None else args.stop
    pool = direction_pool(args.bound)
    allowed_positions = None
    if args.filter_min_sat_shards:
        allowed_positions = {
            row["position"]
            for path in args.filter_min_sat_shards
            for row in json.loads(path.read_text())["rows"]
            if row["min"]["verdict"] == "sat"
        }
    rows = []
    for position, source_row in enumerate(residue[args.start:stop], args.start):
        if allowed_positions is not None and position not in allowed_positions:
            continue
        index = source_row["survivor_index"]
        results = {}
        sides = ("min", "max") if args.side == "both" else (args.side,)
        for side in sides:
            verdict, core = menu(survivors[index], pool, side, args.timeout_ms)
            results[side] = {"verdict": verdict, "menu": [list(item) for item in core]}
        rows.append({"position": position, "survivor_index": index, **results})
    payload = {
        "schema": "starved-payoff-menu-search-shard-v1",
        "scope": "payoff-only exact QF_LRA discovery audit; not proof objects",
        "bound": args.bound,
        "start": args.start,
        "stop": stop,
        "total": len(residue),
        "sides": list(sides),
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"start": args.start, "stop": stop, "summary": {side: {verdict: sum(row[side]["verdict"] == verdict for row in rows) for verdict in sorted({row[side]["verdict"] for row in rows})} for side in sides}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
