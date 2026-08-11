#!/usr/bin/env python3
"""Independent exact cutting-plane audit of mixed-witness elimination.

The direct formulation keeps a root-zero witness.  This formulation removes
that block, retains the labelled x/z master, and separates over the tagged
rooted packing polytope.  Agreement checks the witness-feasibility component
of the human mixed-projection theorem on hostile and sharp fixed branches.
It is finite control evidence, not a proof of the theorem or the universal
hybrid-overlap bound.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog
from verify_labelled_branch_duals import CASES, branch_system, one_witness_minimum
from verify_n7_neutral_rectangle_control import (
    G as NEUTRAL_G,
    H as NEUTRAL_H,
    X as NEUTRAL_X,
    Z as NEUTRAL_Z,
)
from verify_rooted_hinge_projection import decomposition_witnesses


NEUTRAL_CASE = {
    "name": "neutral_rectangle_control",
    "g": NEUTRAL_G,
    "h": NEUTRAL_H,
    "x": NEUTRAL_X,
    "z": NEUTRAL_Z,
    "support_x": (9, 10, 38, 70, 111),
    "support_z": (9,),
}
CONTROL_CASES = CASES + (NEUTRAL_CASE,)


def vector_rank(columns) -> int:
    if not columns:
        return 0
    rows = [[F(column[i]) for column in columns] for i in range(len(columns[0]))]
    rank = 0
    for column in range(len(columns)):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [q / scale for q in rows[rank]]
        for i in range(len(rows)):
            if i == rank or not rows[i][column]:
                continue
            scale = rows[i][column]
            rows[i] = [a - scale * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def master_without_witness(system):
    n = system["n"]
    columns = list(range(2 * n))
    inequality_rows = []
    for k, label in enumerate(system["inequality_labels"]):
        if label[0] == "nonnegative" and label[1] >= 2:
            continue
        if label[0] == "tight" and label[3] >= 2:
            continue
        inequality_rows.append(k)
    equality_rows = []
    for k, label in enumerate(system["equality_labels"]):
        if label[0] == "total" and label[1] >= 2:
            continue
        if label[0] == "witness_zero":
            continue
        equality_rows.append(k)
    return {
        "objective": [system["objective"][j] for j in columns],
        "aub": [[system["inequalities"][k][j] for j in columns] for k in inequality_rows],
        "bub": [system["inequality_rhs"][k] for k in inequality_rows],
        "aeq": [[system["equalities"][k][j] for j in columns] for k in equality_rows],
        "beq": [system["equality_rhs"][k] for k in equality_rows],
    }


def tagged_separator(tagged, n, root, x, z):
    aub, bub = [], []
    for player in range(n):
        if player == root:
            continue
        aub.append([F(coalition >> player & 1) for _colour, coalition in tagged])
        bub.append(F(1))
    for variable in range(len(tagged)):
        row = [F(0)] * len(tagged)
        row[variable] = -1
        aub.append(row)
        bub.append(F(0))
    objective = []
    for colour, coalition in tagged:
        point = x if colour == "x" else z
        objective.append(-sum((point[i] for i in range(n) if coalition >> i & 1), F(0)))
    status, negative_value, weights = exact_linprog(objective, aub, bub)
    if status != "optimal":
        raise AssertionError(f"tagged separator is {status}")
    return -negative_value, weights


def coalition_rank(coalitions, n):
    return vector_rank(
        [tuple(F(coalition >> i & 1) for i in range(n)) for coalition in coalitions]
    )


def packet_audit(tagged, weights, n, root, case):
    support = [k for k, weight in enumerate(weights) if weight]
    offroot_columns = [
        tuple(F(coalition >> i & 1) for i in range(n) if i != root)
        for k, (_colour, coalition) in enumerate(tagged)
        if k in support
    ]
    if vector_rank(offroot_columns) != len(support):
        raise AssertionError("separator did not return an extreme tagged packet")
    if len(support) > n - 1:
        raise AssertionError("mixed packet exceeds n-1 support bound")

    loads = [F(0)] * n
    projected = {}
    for (colour, coalition), weight in zip(tagged, weights):
        if not weight:
            continue
        projected[coalition] = projected.get(coalition, F(0)) + weight
        for i in range(n):
            if coalition >> i & 1:
                loads[i] += weight
    coefficients = dict(projected)
    for i in range(n):
        if i == root:
            continue
        deficit = F(1) - loads[i]
        if deficit < 0:
            raise AssertionError("offroot capacity exceeded")
        if deficit:
            singleton = 1 << i
            coefficients[singleton] = coefficients.get(singleton, F(0)) + deficit
    delta = loads[root] - 1
    root_singleton = 1 << root
    coefficients[root_singleton] = coefficients.get(root_singleton, F(0)) - delta
    coefficients = {coalition: q for coalition, q in coefficients.items() if q}
    identity = [F(0)] * n
    for coalition, coefficient in coefficients.items():
        for i in range(n):
            if coalition >> i & 1:
                identity[i] += coefficient
    if identity != [F(1)] * n:
        raise AssertionError("projected completion identity failed")
    negative = [coalition for coalition, q in coefficients.items() if q < 0]
    if len(negative) > 1 or (negative and negative != [root_singleton]):
        raise AssertionError("projected packet is not singleton-exceptional")
    projected_support = tuple(sorted(coefficients))
    projected_rank = coalition_rank(projected_support, n)
    projected_minimal = projected_rank == len(projected_support)
    projected_decompositions = (
        decomposition_witnesses(projected_support, n)
        if negative and projected_minimal
        else []
    )

    pair_lift = dict(projected)
    deficit_total = F(0)
    for i in range(n):
        if i == root:
            continue
        deficit = F(1) - loads[i]
        if deficit:
            pair = (1 << root) | (1 << i)
            pair_lift[pair] = pair_lift.get(pair, F(0)) + deficit
            deficit_total += deficit
    pair_lift[root_singleton] = pair_lift.get(root_singleton, F(0)) - delta - deficit_total
    pair_lift = {coalition: q for coalition, q in pair_lift.items() if q}
    pair_identity = [F(0)] * n
    for coalition, coefficient in pair_lift.items():
        for i in range(n):
            if coalition >> i & 1:
                pair_identity[i] += coefficient
    if pair_identity != [F(1)] * n:
        raise AssertionError("rooted-pair shear identity failed")
    pair_negative = [coalition for coalition, q in pair_lift.items() if q < 0]
    if pair_negative != [root_singleton]:
        raise AssertionError("rooted-pair shear lost its unique exceptional root")
    pair_support = tuple(sorted(pair_lift))
    pair_rank = coalition_rank(pair_support, n)
    pair_minimal = pair_rank == len(pair_support)
    pair_decompositions = (
        decomposition_witnesses(pair_support, n) if pair_minimal else []
    )
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))

    def game_value(coalition):
        return min(
            sum((generator[i] for i in range(n) if coalition >> i & 1), F(0))
            for generator in generators
        )

    pair_game_slack = game_value((1 << n) - 1) - sum(
        (coefficient * game_value(coalition) for coalition, coefficient in pair_lift.items()),
        F(0),
    )
    if pair_game_slack < 0:
        raise AssertionError("rooted-pair exact-game inequality has negative slack")

    return {
        "tagged_support": [
            {
                "selection": tagged[k][0],
                "coalition": tagged[k][1],
                "weight": str(weights[k]),
            }
            for k in support
        ],
        "tagged_support_size": len(support),
        "tagged_vertex_rank_verified": True,
        "player_loads": [str(q) for q in loads],
        "root_excess_delta": str(delta),
        "projected_completion": [
            {"coalition": coalition, "coefficient": str(coefficients[coalition])}
            for coalition in sorted(coefficients)
        ],
        "projected_incidence_identity_verified": True,
        "projected_support_rank": projected_rank,
        "projected_support_minimal": projected_minimal,
        "projected_kind": "purely_min_semi_balanced" if negative else "min_balanced",
        "exceptional_coalition": negative[0] if negative else None,
        "projected_decomposition_count": len(projected_decompositions),
        "projected_exact_cone_facet": bool(negative) and projected_minimal and not projected_decompositions,
        "colour_erasure_merged_a_duplicate": len(projected) < len(support),
        "rooted_pair_shear": {
            "completion": [
                {"coalition": coalition, "coefficient": str(pair_lift[coalition])}
                for coalition in pair_support
            ],
            "incidence_identity_verified": True,
            "support_rank": pair_rank,
            "support_minimal": pair_minimal,
            "decomposition_count": len(pair_decompositions),
            "exact_cone_facet": pair_minimal and not pair_decompositions,
            "game_inequality_slack": str(pair_game_slack),
        },
    }


def projected_minimum(case, root):
    system = branch_system(case)
    n = system["n"]
    master = master_without_witness(system)
    tagged = tuple(("x", coalition) for coalition in case["support_x"]) + tuple(
        ("z", coalition) for coalition in case["support_z"]
    )
    cuts = []
    for _iteration in range(256):
        status, optimum, solution = exact_linprog(
            master["objective"], master["aub"], master["bub"], master["aeq"], master["beq"]
        )
        if status != "optimal":
            raise AssertionError(f"mixed projected master is {status}")
        x, z = solution[:n], solution[n : 2 * n]
        violation, weights = tagged_separator(tagged, n, root, x, z)
        if violation <= 1:
            return optimum, cuts
        row = [F(0)] * (2 * n)
        for (colour, coalition), weight in zip(tagged, weights):
            offset = 0 if colour == "x" else n
            for i in range(n):
                if coalition >> i & 1:
                    row[offset + i] += weight
        master["aub"].append(row)
        master["bub"].append(F(1))
        cuts.append(
            {
                "violated_value": str(violation),
                **packet_audit(tagged, weights, n, root, case),
            }
        )
    raise AssertionError("mixed-witness cutting plane did not terminate")


def audit_case(case):
    system = branch_system(case)
    n = system["n"]
    overlap = tuple(min(case["x"][i], case["z"][i]) for i in range(n))
    roots = tuple(i for i, q in enumerate(overlap) if q == max(overlap))
    rows = []
    for root in roots:
        projected, cuts = projected_minimum(case, root)
        direct = one_witness_minimum(system, root)
        if projected != direct:
            raise AssertionError((case["name"], root, projected, direct))
        rows.append(
            {
                "root": root,
                "projected_minimum": str(projected),
                "direct_witness_minimum": str(direct),
                "cut_count": len(cuts),
                "maximum_tagged_cut_support": max(
                    (cut["tagged_support_size"] for cut in cuts), default=0
                ),
                "cuts": cuts,
            }
        )
    return {
        "name": case["name"],
        "n": n,
        "maximum_overlap_roots": list(roots),
        "tagged_menu_sizes": {"x": len(case["support_x"]), "z": len(case["support_z"])},
        "roots": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact mixed-witness projection cutting-plane controls",
        "human_theorem_audited": (
            "eliminating one root-zero witness is equivalent to all tagged rooted "
            "packing inequalities, whose extreme supports have size at most n-1"
        ),
        "independence_boundary": (
            "the projected and direct formulations share labelled branch rows; "
            "their witness-feasibility components are independently formulated"
        ),
        "scope": (
            "maximum-overlap roots of seven hostile/sharp fixed branches and one "
            "neutral control; exact controls only, not an all-n theorem"
        ),
        "cases": [audit_case(case) for case in CONTROL_CASES],
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
