#!/usr/bin/env python3
"""Search exactness-aware exchange menus on all 504 starved-only rows.

A coalition tight at either selection must also be no more expensive there
than at the opposite selection and at each singleton-zero core witness.  This
search uses those necessary blocker inequalities directly.  A successful
menu therefore replaces the full staged Farkas packet by finitely many
ordinary lexicographic exchange directions plus singleton exactness.

The search output is proof-discovery evidence, not an independent proof
object.  Any stable abstract menu family must subsequently be exported and
checked separately.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_equality_refinement_neighborhood import COARSE_TYPES  # noqa: E402
from audit_starved_refinement_direction import base_system, point_sum  # noqa: E402
from search_positive_handover_directions import direction_pool, lex_improves  # noqa: E402


def exactness_system(configuration, index):
    solver, x, z, cell, roles = base_system(configuration, COARSE_TYPES[0])
    witnesses = []
    for zero in range(6):
        witness = [
            z3.Real(f"starved_exact_q_{index}_{zero}_{player}")
            for player in range(6)
        ]
        solver.add(
            z3.Sum(*witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
        witnesses.append(witness)
    return solver, x, z, cell, roles, witnesses


def blocker_formula(x, z, witnesses, direction, side):
    reference = x if side == "min" else z
    comparison = z if side == "min" else x
    blockers = []
    masks = []
    for mask in range(1, (1 << 6) - 1):
        players = tuple(player for player in range(6) if mask >> player & 1)
        if sum(direction[player] for player in players) >= 0:
            continue
        blockers.append(
            z3.And(
                point_sum(comparison, players) >= point_sum(reference, players),
                *[
                    point_sum(witness, players) >= point_sum(reference, players)
                    for witness in witnesses
                ],
            )
        )
        masks.append(mask)
    return z3.Or(*blockers), tuple(masks)


def minimized_menu(configuration, index, side, pool, timeout_ms):
    solver, x, z, cell, roles, witnesses = exactness_system(configuration, index)
    solver.set(timeout=timeout_ms, unsat_core=True)
    tags = {}
    mask_counts = {}
    for number, direction in enumerate(pool):
        if not lex_improves(direction, cell, side):
            continue
        formula, masks = blocker_formula(x, z, witnesses, direction, side)
        tag = z3.Bool(f"starved_exact_menu_{index}_{number}")
        tags[tag] = direction
        mask_counts[direction] = len(masks)
        solver.add(z3.Implies(tag, formula))
    verdict = solver.check(*tags)
    if verdict != z3.unsat:
        return str(verdict), (), {}, roles
    core = list(solver.unsat_core())
    for tag in tuple(core):
        trial = [candidate for candidate in core if candidate is not tag]
        if solver.check(*trial) == z3.unsat:
            core = trial
    menu = tuple(tags[tag] for tag in core)
    return (
        "unsat",
        menu,
        {str(direction): mask_counts[direction] for direction in menu},
        roles,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--handover",
        type=Path,
        default=HERE / "starved_packet_handover_audit.json",
    )
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--bound", type=int, default=1)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    survivors = json.loads(args.triage.read_text())["survivors"]
    source_rows = json.loads(args.handover.read_text())["rows"]
    assert len(source_rows) == 504
    stop = len(source_rows) if args.stop is None else args.stop
    pool = direction_pool(args.bound)
    rows = []
    for position, source in enumerate(source_rows[args.start:stop], args.start):
        index = source["survivor_index"]
        side = source["selected_packet"]
        verdict, menu, mask_counts, roles = minimized_menu(
            survivors[index], index, side, pool, args.timeout_ms
        )
        rows.append(
            {
                "position": position,
                "survivor_index": index,
                "side": side,
                "roles": "".join(roles),
                "verdict": verdict,
                "menu": [list(direction) for direction in menu],
                "menu_size": len(menu),
                "negative_blocker_mask_counts": mask_counts,
            }
        )
        args.output.write_text(
            json.dumps(
                {
                    "schema": "starved-exactness-aware-menu-shard-v1",
                    "scope": "exact QF_LRA proof discovery; not proof objects",
                    "bound": args.bound,
                    "source": "all",
                    "start": args.start,
                    "stop": stop,
                    "total": len(source_rows),
                    "rows": rows,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    print(
        json.dumps(
            {
                "rows": len(rows),
                "verdicts": dict(sorted(Counter(row["verdict"] for row in rows).items())),
                "menu_sizes": dict(sorted(Counter(row["menu_size"] for row in rows).items())),
                "sides": dict(sorted(Counter(row["side"] for row in rows).items())),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
