#!/usr/bin/env python3
"""Search small explicit improving directions in the positive critical residue.

This is proof-discovery navigation.  A reported direction is checked exactly
against the critical-triple algebra, local signs, strict distance, and the
rich singleton witness, but the resulting UNSAT blocker verdict is not by
itself an independent proof object.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402
from audit_positive_one_split_residue import (  # noqa: E402
    N,
    point_sum,
)
from audit_positive_packet_ablation_census import (  # noqa: E402
    EXPECTED,
    POSITIVE,
    lmax_side_case,
)
from audit_equality_refinement_neighborhood import refines  # noqa: E402


def critical_all_witness_solver(index, configuration):
    r = tuple(configuration[0])
    c = tuple(configuration[1])
    table = tuple(tuple(row) for row in configuration[2])
    solver = z3.Solver()
    lmin_levels, lmax_levels = nsix.levels(N, r, c, solver)
    cell = nsix.layout(N, r, c, table)
    x = [lmin_levels[cell[i][0]] for i in range(N)]
    z = [lmax_levels[cell[i][1]] for i in range(N)]
    poor = [i for i, (_, column) in enumerate(cell) if sum(c[:column]) < 2]
    rich = next(i for i, (row, _) in enumerate(cell) if sum(r[:row]) == 5)
    P = [i for i in range(N) if i not in poor and i != rich]
    assert len(poor) == 2 and len(P) == 3
    solver.add(*[x[i] > z[i] for i in poor])
    solver.add(*[z[i] > x[i] for i in P])
    solver.add(x[rich] > z[rich])
    witnesses = []
    for zero in range(N):
        witness = [z3.Real(f"handover_q_{index}_{zero}_{i}") for i in range(N)]
        witnesses.append(witness)
        solver.add(
            z3.Sum(witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
    triples = []
    for excluded in P:
        triple = tuple(i for i in P if i != excluded) + (rich,)
        triples.append(triple)
        solver.add(point_sum(z, triple) >= point_sum(x, triple))
        for witness in witnesses:
            solver.add(point_sum(witness, triple) >= point_sum(x, triple))
    solver.add(
        z3.Or(
            *[
                z3.And(
                    *[
                        point_sum(z, triples[k]) == point_sum(x, triples[k])
                        for k in pair
                    ]
                )
                for pair in ((0, 1), (0, 2), (1, 2))
            ]
        )
    )
    distance = z3.Sum(
        *[
            table[row][column]
            * z3.Abs(lmin_levels[row] - lmax_levels[column])
            for row in range(len(r))
            for column in range(len(c))
            if table[row][column]
        ]
    )
    solver.add(distance > z3.RealVal("2/3"))
    return solver, {
        "P_players": P,
        "poor_players": poor,
        "rich_player": rich,
        "triple_masks": [sum(1 << i for i in triple) for triple in triples],
    }, witnesses


def primitive(direction):
    divisor = 0
    for value in direction:
        divisor = math.gcd(divisor, abs(value))
    return divisor == 1


def direction_pool(bound):
    rows = []
    for direction in itertools.product(range(-bound, bound + 1), repeat=N):
        if sum(direction) or not any(direction) or not primitive(direction):
            continue
        rows.append(direction)
    preferred_multisets = (
        (-1, 0, 0, 0, 0, 1),
        (-2, -1, 0, 1, 1, 1),
        (-2, -1, -1, 1, 1, 2),
        (-3, -1, -1, 1, 2, 2),
        (-2, -2, -1, 1, 1, 3),
    )

    def priority(row):
        ordered = tuple(sorted(row))
        preferred = (
            preferred_multisets.index(ordered)
            if ordered in preferred_multisets
            else len(preferred_multisets)
        )
        return (
            preferred,
            sum(abs(value) for value in row),
            max(abs(value) for value in row),
            sum(value != 0 for value in row),
            row,
        )

    return tuple(
        sorted(
            rows,
            key=priority,
        )
    )


def lex_improves(direction, cell, side):
    coordinate = 0 if side == "min" else 1
    levels = sorted(
        {cell[i][coordinate] for i in range(N)}, reverse=(side == "max")
    )
    for level in levels:
        values = [
            direction[i] for i in range(N) if cell[i][coordinate] == level
        ]
        if not any(values):
            continue
        if side == "min":
            return all(value >= 0 for value in values) and any(
                value > 0 for value in values
            )
        return all(value <= 0 for value in values) and any(
            value < 0 for value in values
        )
    return False


def blocker_formula(index, configuration, direction, side, witnesses):
    r, c, table = configuration
    cell = nsix.layout(N, tuple(r), tuple(c), tuple(tuple(row) for row in table))
    x = [z3.Real(f"m{cell[i][0]}") for i in range(N)]
    z = [z3.Real(f"M{cell[i][1]}") for i in range(N)]
    reference = x if side == "min" else z
    comparison = z if side == "min" else x
    blockers = []
    masks = []
    for coalition in range(1, (1 << N) - 1):
        derivative = sum(
            direction[i] for i in range(N) if coalition >> i & 1
        )
        if derivative >= 0:
            continue
        players = tuple(i for i in range(N) if coalition >> i & 1)
        blockers.append(
            z3.And(
                point_sum(comparison, players) >= point_sum(reference, players),
                *[
                    point_sum(witness, players) >= point_sum(reference, players)
                    for witness in witnesses
                ],
            )
        )
        masks.append(coalition)
    return z3.Or(*blockers), tuple(masks)


def minimize_direction_menu(
    solver, index, configuration, directions, side, witnesses, timeout_ms
):
    menu_solver = z3.Solver()
    menu_solver.set(timeout=timeout_ms, unsat_core=True)
    menu_solver.add(*solver.assertions())
    tags = {}
    mask_counts = {}
    for number, direction in enumerate(directions):
        formula, masks = blocker_formula(
            index, configuration, direction, side, witnesses
        )
        tag = z3.Bool(f"direction_menu_{index}_{number}")
        tags[tag] = direction
        mask_counts[direction] = len(masks)
        menu_solver.add(z3.Implies(tag, formula))
    verdict = menu_solver.check(*tags)
    if verdict != z3.unsat:
        return str(verdict), (), {}
    core = list(menu_solver.unsat_core())
    changed = True
    while changed:
        changed = False
        for tag in tuple(core):
            trial = [candidate for candidate in core if candidate is not tag]
            if menu_solver.check(*trial) == z3.unsat:
                core = trial
                changed = True
    menu = tuple(tags[tag] for tag in core)
    return "unsat", menu, {str(row): mask_counts[row] for row in menu}


def canonical_lmin_menu(index, labels):
    """Fourteen subset exchanges plus two audited boundary extensions."""
    exceptional = {
        2597: (
            (1, 1, 1, -1, 0, -2),
            (1, 2, 1, -1, -1, -2),
        ),
        3237: (
            (1, 0, 1, -1, -1, 0),
            (2, 0, 1, -1, -1, -1),
            (1, 0, 0, -1, 0, 0),
            (1, 0, 0, 0, -1, 0),
        ),
    }
    if index in exceptional:
        return exceptional[index]
    directions = []
    for poor in labels["poor_players"]:
        for size in range(1, len(labels["P_players"]) + 1):
            for chosen in itertools.combinations(labels["P_players"], size):
                direction = [0] * N
                for player in chosen:
                    direction[player] = 1
                direction[poor] = -1
                direction[labels["rich_player"]] = -(size - 1)
                directions.append(tuple(direction))
    return tuple(directions)


def search(
    index,
    configuration,
    pool,
    timeout_ms,
    allow_menus,
    canonical_menus,
    max_single_directions,
):
    solver, labels, witnesses = critical_all_witness_solver(index, configuration)
    solver.set(timeout=timeout_ms)
    base = solver.check()
    if base != z3.sat:
        return {"critical_algebra_verdict": str(base)}
    side = "max" if lmax_side_case(configuration) else "min"
    cell = nsix.layout(
        N,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(row) for row in configuration[2]),
    )
    attempted = 0
    unknown = 0
    for direction in pool:
        if not lex_improves(direction, cell, side):
            continue
        if max_single_directions is not None and attempted >= max_single_directions:
            break
        attempted += 1
        formula, masks = blocker_formula(
            index, configuration, direction, side, witnesses
        )
        solver.push()
        solver.add(formula)
        verdict = solver.check()
        solver.pop()
        if verdict == z3.unsat:
            return {
                "critical_algebra_verdict": "sat",
                "selected_side": side,
                "direction": direction,
                "syntactic_negative_mask_count": len(masks),
                "directions_attempted": attempted,
                "unknown_direction_checks": unknown,
                **labels,
            }
        if verdict == z3.unknown:
            unknown += 1
    result = {
        "critical_algebra_verdict": "sat",
        "selected_side": side,
        "direction": None,
        "directions_attempted": attempted,
        "unknown_direction_checks": unknown,
    }
    if allow_menus:
        menu_pool = (
            canonical_lmin_menu(index, labels)
            if canonical_menus and side == "min"
            else pool
        )
        directions = tuple(
            direction
            for direction in menu_pool
            if lex_improves(direction, cell, side)
        )
        menu_verdict, menu, mask_counts = minimize_direction_menu(
            solver,
            index,
            configuration,
            directions,
            side,
            witnesses,
            timeout_ms,
        )
        result.update(
            {
                "full_direction_menu_verdict": menu_verdict,
                "minimized_direction_menu": menu,
                "menu_negative_mask_counts": mask_counts,
            }
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("indices", nargs="*", type=int)
    parser.add_argument(
        "--ablation-side", choices=("lmin_only", "lmax_only")
    )
    parser.add_argument("--selected-side", choices=("min", "max"))
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--bound", type=int, default=2)
    parser.add_argument("--timeout-ms", type=int, default=5_000)
    parser.add_argument("--allow-menus", action="store_true")
    parser.add_argument("--canonical-menus", action="store_true")
    parser.add_argument("--max-single-directions", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    survivors = json.loads(args.triage.read_text())["survivors"]
    if args.indices:
        indices = args.indices
    elif args.ablation_side:
        indices = EXPECTED[args.ablation_side]
    elif args.selected_side:
        indices = [
            index
            for index, configuration in enumerate(survivors)
            if refines(
                tuple(configuration[0]),
                tuple(configuration[1]),
                tuple(tuple(row) for row in configuration[2]),
                POSITIVE,
            )
            and (
                ("max" if lmax_side_case(configuration) else "min")
                == args.selected_side
            )
        ]
    else:
        indices = [
            index
            for index, configuration in enumerate(survivors)
            if refines(
                tuple(configuration[0]),
                tuple(configuration[1]),
                tuple(tuple(row) for row in configuration[2]),
                POSITIVE,
            )
        ]
    pool = direction_pool(args.bound)
    rows = []
    for index in indices:
        result = search(
            index,
            survivors[index],
            pool,
            args.timeout_ms,
            args.allow_menus,
            args.canonical_menus,
            args.max_single_directions,
        )
        row = {
            "survivor_index": index,
            "configuration": survivors[index],
            **result,
        }
        rows.append(row)
        print(index, result, flush=True)
        if args.output:
            solved_by_algebra = sum(
                item["critical_algebra_verdict"] == "unsat" for item in rows
            )
            solved_by_direction = sum(item.get("direction") is not None for item in rows)
            solved_by_menu = sum(
                item.get("full_direction_menu_verdict") == "unsat" for item in rows
            )
            args.output.write_text(
                json.dumps(
                    {
                        "status": (
                            "exact blocker checks for proof discovery; solver "
                            "UNSAT verdicts are not independent proof objects"
                        ),
                        "coefficient_bound": args.bound,
                        "direction_pool_size": len(pool),
                        "rows_completed": len(rows),
                        "solved_by_critical_algebra": solved_by_algebra,
                        "solved_by_single_direction": solved_by_direction,
                        "solved_by_direction_menu": solved_by_menu,
                        "unresolved_completed_rows": len(rows)
                        - solved_by_algebra
                        - solved_by_direction
                        - solved_by_menu,
                        "rows": rows,
                    },
                    indent=2,
                )
                + "\n"
            )

    final = (
        sum(item["critical_algebra_verdict"] == "unsat" for item in rows),
        sum(item.get("direction") is not None for item in rows),
        sum(item.get("full_direction_menu_verdict") == "unsat" for item in rows),
    )
    if args.selected_side == "max" and args.bound == 3:
        assert len(rows) == 339 and final == (230, 109, 0)
    if (
        args.selected_side == "min"
        and args.bound == 3
        and args.max_single_directions == 100
        and args.allow_menus
        and args.canonical_menus
    ):
        assert len(rows) == 1320 and final == (901, 322, 97)


if __name__ == "__main__":
    main()
