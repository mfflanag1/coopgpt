#!/usr/bin/env python3
"""Discover table-independent patterns for the 97 Lmin exchange-menu rows."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402
from audit_positive_lmax_direction_layers import feasible_common_pairs  # noqa: E402
from audit_positive_lmin_direction_patterns import (  # noqa: E402
    N,
    add_relation,
    exact_relations,
    point_sum,
    relation_formula,
    relation_holds,
    shared_relations,
    weak_core_combinations,
)
from search_positive_handover_directions import (  # noqa: E402
    canonical_lmin_menu,
    critical_all_witness_solver,
    lex_improves,
)


def abstract_solver(key, x_relations, z_relations):
    roles, directions, common_pair = key
    solver = z3.Solver()
    x = [z3.Real(f"menu_pattern_x_{i}") for i in range(N)]
    z = [z3.Real(f"menu_pattern_z_{i}") for i in range(N)]
    solver.add(
        z3.Sum(x) == 1,
        z3.Sum(z) == 1,
        *[coordinate >= 0 for coordinate in x + z],
        *[x[i] <= x[i + 1] for i in range(N - 1)],
    )
    for player, role in enumerate(roles):
        solver.add(x[player] > z[player] if role in ("N", "R") else z[player] > x[player])
    for item in x_relations:
        add_relation(solver, x, item)
    for item in z_relations:
        add_relation(solver, z, item)

    middle = tuple(player for player, role in enumerate(roles) if role == "P")
    rich = roles.index("R")
    triples = {
        excluded: tuple(player for player in middle if player != excluded) + (rich,)
        for excluded in middle
    }
    for excluded in middle:
        solver.add(point_sum(z, triples[excluded]) >= point_sum(x, triples[excluded]))
    for excluded in common_pair:
        solver.add(point_sum(z, triples[excluded]) == point_sum(x, triples[excluded]))
    witnesses = []
    for zero in range(N):
        witness = [z3.Real(f"menu_pattern_q_{zero}_{i}") for i in range(N)]
        witnesses.append(witness)
        solver.add(
            z3.Sum(witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
        for excluded in middle:
            solver.add(point_sum(witness, triples[excluded]) >= point_sum(x, triples[excluded]))
    positive = [player for player, role in enumerate(roles) if role in ("N", "R")]
    solver.add(2 * point_sum([x[i] - z[i] for i in range(N)], positive) > z3.RealVal("2/3"))

    for menu_number, direction in enumerate(directions):
        blockers = []
        for mask in range(1, (1 << N) - 1):
            players = tuple(i for i in range(N) if mask >> i & 1)
            if sum(direction[i] for i in players) >= 0:
                continue
            blockers.append(
                z3.And(
                    point_sum(z, players) >= point_sum(x, players),
                    *[
                        point_sum(witness, players) >= point_sum(x, players)
                        for witness in witnesses
                    ],
                )
            )
        solver.add(z3.Or(*blockers))
    return solver


def normalize(row, configuration):
    index = row["survivor_index"]
    _, labels, _ = critical_all_witness_solver(index, configuration, include_distance=False)
    cell = nsix.layout(
        N,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(values) for values in configuration[2]),
    )
    role = {player: "N" for player in labels["poor_players"]}
    role.update({player: "P" for player in labels["P_players"]})
    role[labels["rich_player"]] = "R"
    players = sorted(
        range(N),
        key=lambda player: (
            cell[player][0],
            {"N": 0, "P": 1, "R": 2}[role[player]],
            cell[player][1],
            player,
        ),
    )
    inverse = {player: position for position, player in enumerate(players)}
    return {
        "index": index,
        "roles": tuple(role[player] for player in players),
        "directions": tuple(
            sorted(
                tuple(direction[player] for player in players)
                for direction in canonical_lmin_menu(index, labels)
                if lex_improves(direction, cell, "min")
            )
        ),
        "x_ranks": tuple(cell[player][0] for player in players),
        "z_ranks": tuple(cell[player][1] for player in players),
        "pairs": tuple(
            tuple(sorted(inverse[player] for player in pair))
            for pair in feasible_common_pairs(configuration, index, True)
        ),
    }


def minimized_exact_core(key, x_relations, z_relations, instance):
    solver = abstract_solver(key, x_relations, z_relations)
    solver.set(unsat_core=True)
    x = [z3.Real(f"menu_pattern_x_{i}") for i in range(N)]
    z = [z3.Real(f"menu_pattern_z_{i}") for i in range(N)]
    shared = {("x", *item) for item in x_relations} | {
        ("z", *item) for item in z_relations
    }
    tags = {}
    for number, item in enumerate(
        candidate for candidate in exact_relations(instance) if candidate not in shared
    ):
        coordinate, operator, first, second = item
        tag = z3.Bool(f"menu_pattern_relation_{number}")
        tags[tag] = item
        point = x if coordinate == "x" else z
        solver.add(z3.Implies(tag, relation_formula(point, (operator, first, second))))
    assert solver.check(*tags) == z3.unsat
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
    return tuple(sorted(tags[tag] for tag in core))


def refinement_verdict(key, x_relations, z_relations, refinements):
    solver = abstract_solver(key, x_relations, z_relations)
    x = [z3.Real(f"menu_pattern_x_{i}") for i in range(N)]
    z = [z3.Real(f"menu_pattern_z_{i}") for i in range(N)]
    for coordinate, operator, first, second in refinements:
        point = x if coordinate == "x" else z
        solver.add(relation_formula(point, (operator, first, second)))
    return str(solver.check())


def core_cover(key, x_relations, z_relations, instances):
    representatives = {}
    for instance in instances:
        representatives.setdefault((instance["x_ranks"], instance["z_ranks"]), instance)
    cores = {
        minimized_exact_core(key, x_relations, z_relations, instance)
        for instance in representatives.values()
    }
    candidates = set(cores)
    for candidate in weak_core_combinations(cores):
        if refinement_verdict(key, x_relations, z_relations, candidate) == "unsat":
            candidates.add(candidate)
    coverage = {
        core: {
            number
            for number, instance in enumerate(instances)
            if all(relation_holds(instance, item) for item in core)
        }
        for core in candidates
    }
    uncovered = set(range(len(instances)))
    chosen = []
    while uncovered:
        core = max(
            coverage,
            key=lambda candidate: (
                len(coverage[candidate] & uncovered), -len(candidate), candidate
            ),
        )
        assert coverage[core] & uncovered
        chosen.append(core)
        uncovered -= coverage[core]
    return tuple(chosen)


def minimize_proof_relations(key, relations):
    core = list(dict.fromkeys(relations))
    for item in tuple(core):
        trial = [candidate for candidate in core if candidate != item]
        x_relations = tuple(candidate[1:] for candidate in trial if candidate[0] == "x")
        z_relations = tuple(candidate[1:] for candidate in trial if candidate[0] == "z")
        if str(abstract_solver(key, x_relations, z_relations).check()) == "unsat":
            core = trial
    return tuple(core)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--menus", type=Path, default=HERE / "positive_lmin_handover_directions.json"
    )
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.menus.read_text())["rows"]
    survivors = json.loads(args.triage.read_text())["survivors"]
    rows = [row for row in source if row.get("full_direction_menu_verdict") == "unsat"]
    assert len(rows) == 97
    groups = collections.defaultdict(list)
    for row in rows:
        normalized = normalize(row, survivors[row["survivor_index"]])
        for pair in normalized["pairs"]:
            key = (normalized["roles"], normalized["directions"], pair)
            groups[key].append(normalized)
    verdicts = collections.Counter()
    patterns = []
    proof_cases = []
    proof_mappings = []
    for number, (key, instances) in enumerate(sorted(groups.items()), 1):
        x_relations = shared_relations(instances, "x_ranks")
        z_relations = shared_relations(instances, "z_ranks")
        verdict = str(abstract_solver(key, x_relations, z_relations).check())
        verdicts[verdict] += 1
        pattern = {
                "pattern": number,
                "roles": "".join(key[0]),
                "directions": [list(item) for item in key[1]],
                "common_pair_positions": list(key[2]),
                "mapping_instances": len(instances),
                "survivor_indices": sorted({item["index"] for item in instances}),
                "shared_x_relations": [list(item) for item in x_relations],
                "shared_z_relations": [list(item) for item in z_relations],
                "abstract_blocker_verdict": verdict,
            }
        patterns.append(pattern)
        refinements = ((),) if verdict == "unsat" else core_cover(
            key, x_relations, z_relations, instances
        )
        shared = tuple(("x", *item) for item in x_relations) + tuple(
            ("z", *item) for item in z_relations
        )
        case_relations = []
        for refinement_number, refinement in enumerate(refinements, 1):
            minimized = minimize_proof_relations(key, shared + refinement)
            case_id = f"pattern-{number:02d}-{refinement_number}"
            assert refinement_verdict(key, (), (), minimized) == "unsat"
            case_relations.append((case_id, minimized))
            proof_cases.append(
                {
                    "case": case_id,
                    "pattern": number,
                    "roles": "".join(key[0]),
                    "directions": [list(item) for item in key[1]],
                    "common_pair_positions": list(key[2]),
                    "relations": [list(item) for item in minimized],
                    "relation_count": len(minimized),
                }
            )
        for instance in instances:
            eligible = [
                case_id
                for case_id, relations in case_relations
                if all(relation_holds(instance, item) for item in relations)
            ]
            assert eligible
            proof_mappings.append(
                {
                    "survivor_index": instance["index"],
                    "common_pair_positions": list(key[2]),
                    "proof_case": eligible[0],
                }
            )
    mapping_counts = collections.Counter(item["proof_case"] for item in proof_mappings)
    for case in proof_cases:
        case["mapped_instances"] = mapping_counts[case["case"]]
        assert case["mapped_instances"] > 0
    payload = {
        "schema": "positive-lmin-menu-pattern-discovery-v1",
        "scope": "discovery map to abstract exact-QF_LRA blockers; not proof objects",
        "menu_rows": len(rows),
        "pair_instances": sum(len(items) for items in groups.values()),
        "pattern_count": len(patterns),
        "proof_case_count": len(proof_cases),
        "verdict_summary": dict(sorted(verdicts.items())),
        "patterns": patterns,
        "proof_cases": proof_cases,
        "proof_mappings": proof_mappings,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("menu_rows", "pair_instances", "pattern_count", "verdict_summary")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
