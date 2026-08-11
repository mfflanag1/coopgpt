#!/usr/bin/env python3
"""Exact controls for eliminating the common singleton witness.

The human rooted-hinge projection theorem replaces the witness ``w^r`` by
all rooted fractional Lmin-support packing inequalities.  Common-hinge rows
already identify ``x(S)=z(S)``, so the apparent second colour is redundant.
This verifier
uses an exact cutting-plane formulation of that projection and compares its
minimum with the existing direct one-witness LP on every maximum-overlap root
of six hostile branches and two sharp-family orientations.  For every cut it
also forms the associated singleton-slack completion and checks the resulting
semi-balanced incidence identity and linear-independence/minimality claim.

The two formulations share the fixed labelled branch data, but their
witness-feasibility components are independently formulated.  Agreement on
these eight branches is a control, not proof of the human projection theorem
or of the all-n hybrid-overlap conjecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from verify_labelled_branch_duals import (  # noqa: E402
    CASES,
    branch_system,
    one_witness_minimum,
)
from verify_n7_neutral_rectangle_control import (  # noqa: E402
    G as NEUTRAL_G,
    H as NEUTRAL_H,
    X as NEUTRAL_X,
    Z as NEUTRAL_Z,
)


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


def matrix_rank(columns, n):
    """Exact rank of incidence columns in F^n."""
    rows = [[F(column >> i & 1) for column in columns] for i in range(n)]
    rank = 0
    for column in range(len(columns)):
        pivot = next((i for i in range(rank, n) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for i in range(n):
            if i == rank or rows[i][column] == 0:
                continue
            scale = rows[i][column]
            rows[i] = [a - scale * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def decomposition_witnesses(support, n):
    """Apply the Studeny--Kratochvil exceptional-set decomposition test."""
    full = (1 << n) - 1
    witnesses = []
    width = len(support) + 1
    for exceptional in range(1, full):
        if exceptional in support:
            continue
        aub, bub = [], []
        for variable in range(len(support)):
            row = [F(0)] * width
            row[variable] = F(-1)
            aub.append(row)
            bub.append(F(0))
        aeq, beq = [], []
        for player in range(n):
            row = [F(coalition >> player & 1) for coalition in support]
            row.append(F(-1))
            aeq.append(row)
            beq.append(F(exceptional >> player & 1))
        status, _value, solution = exact_linprog(
            [F(0)] * width, aub, bub, aeq, beq
        )
        if status == "optimal":
            witnesses.append(
                {
                    "new_exceptional": exceptional,
                    "common_load": str(solution[-1]),
                    "support_weights": [str(value) for value in solution[:-1]],
                }
            )
        elif status != "infeasible":
            raise AssertionError(f"decomposition test is {status}")
    return witnesses


def semi_balanced_completion(coalitions, weights, n, root, case):
    """Audit the rooted packing's exact singleton-slack completion."""
    loads = [F(0)] * n
    coefficients = {}
    for coalition, weight in zip(coalitions, weights):
        if weight == 0:
            continue
        coefficients[coalition] = coefficients.get(coalition, F(0)) + weight
        for player in range(n):
            if coalition >> player & 1:
                loads[player] += weight
    deficits = [F(0) if i == root else F(1) - loads[i] for i in range(n)]
    if any(deficit < 0 for deficit in deficits):
        raise AssertionError("nonroot packing capacity exceeded")
    for player, deficit in enumerate(deficits):
        if deficit:
            singleton = 1 << player
            coefficients[singleton] = coefficients.get(singleton, F(0)) + deficit
    root_advantage = loads[root] - 1
    root_singleton = 1 << root
    coefficients[root_singleton] = (
        coefficients.get(root_singleton, F(0)) - root_advantage
    )
    coefficients = {
        coalition: coefficient
        for coalition, coefficient in coefficients.items()
        if coefficient
    }
    identity = [F(0)] * n
    for coalition, coefficient in coefficients.items():
        for player in range(n):
            if coalition >> player & 1:
                identity[player] += coefficient
    if identity != [F(1)] * n:
        raise AssertionError("singleton-slack incidence identity failed")
    negative = [
        coalition for coalition, coefficient in coefficients.items() if coefficient < 0
    ]
    if len(negative) > 1:
        raise AssertionError("completion is not semi-conic")
    columns = tuple(sorted(coefficients))
    rank = matrix_rank(columns, n)
    if rank != len(columns):
        raise AssertionError("extreme-packing completion is not support-minimal")
    if root_advantage > 0 and negative != [root_singleton]:
        raise AssertionError("positive root advantage lacks exceptional root singleton")
    kind = "purely_min_semi_balanced" if negative else "min_balanced"
    decompositions = decomposition_witnesses(columns, n) if negative else []
    positive_deficits = [
        player
        for player, deficit in enumerate(deficits)
        if player != root and deficit > 0
    ]
    forced_pair_decomposition = None
    exceptional_transports = []
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))

    def game_value(coalition):
        return min(
            sum(
                (generator[j] for j in range(n) if coalition >> j & 1),
                F(0),
            )
            for generator in generators
        )

    x = tuple(map(F, case["x"]))
    pair_floors = [
        F(0) if player == root else game_value(root_singleton | (1 << player))
        for player in range(n)
    ]
    pair_floor_rdb_slack = (
        sum((deficits[i] * x[i] for i in range(n) if i != root), F(0))
        - root_advantage * x[root]
        - sum(
            (deficits[i] * pair_floors[i] for i in range(n) if i != root),
            F(0),
        )
    )
    if pair_floor_rdb_slack < 0:
        raise AssertionError("pair-floor root-deficit inequality failed")
    pair_lifted_coefficients = {}
    for coalition, weight in zip(coalitions, weights):
        if weight:
            pair_lifted_coefficients[coalition] = (
                pair_lifted_coefficients.get(coalition, F(0)) + weight
            )
    deficit_total = sum((deficits[i] for i in range(n) if i != root), F(0))
    for player in positive_deficits:
        pair = root_singleton | (1 << player)
        pair_lifted_coefficients[pair] = (
            pair_lifted_coefficients.get(pair, F(0)) + deficits[player]
        )
    pair_lifted_coefficients[root_singleton] = (
        pair_lifted_coefficients.get(root_singleton, F(0))
        - root_advantage
        - deficit_total
    )
    pair_lifted_coefficients = {
        coalition: coefficient
        for coalition, coefficient in pair_lifted_coefficients.items()
        if coefficient
    }
    pair_lifted_identity = [F(0)] * n
    for coalition, coefficient in pair_lifted_coefficients.items():
        for player in range(n):
            if coalition >> player & 1:
                pair_lifted_identity[player] += coefficient
    if pair_lifted_identity != [F(1)] * n:
        raise AssertionError("pair-lifted incidence identity failed")
    pair_lifted_support = tuple(sorted(pair_lifted_coefficients))
    pair_lifted_rank = matrix_rank(pair_lifted_support, n)
    if pair_lifted_rank != len(pair_lifted_support):
        raise AssertionError("pair-lifted completion is not minimal")
    if len(pair_lifted_support) > n:
        raise AssertionError("pair-lifted min-semi-balanced support exceeds n")
    pair_lifted_negative = [
        coalition
        for coalition, coefficient in pair_lifted_coefficients.items()
        if coefficient < 0
    ]
    if pair_lifted_negative != [root_singleton]:
        raise AssertionError("pair-lifted exceptional coalition is not the root")
    pair_lifted_decompositions = decomposition_witnesses(pair_lifted_support, n)
    pair_lifted_game_slack = game_value((1 << n) - 1) - sum(
        (
            coefficient * game_value(coalition)
            for coalition, coefficient in pair_lifted_coefficients.items()
        ),
        F(0),
    )
    if pair_lifted_game_slack != pair_floor_rdb_slack:
        raise AssertionError("pair-lifted facet slack and pair-floor budget differ")
    if root_advantage > 0 and positive_deficits:
        for player in positive_deficits:
            exceptional_pair = root_singleton | (1 << player)
            if exceptional_pair in coefficients:
                raise AssertionError(
                    "root/deficit pair violates minimal-support independence"
                )
            if not any(
                row["new_exceptional"] == exceptional_pair
                for row in decompositions
            ):
                raise AssertionError("forced root/deficit decomposition was not found")
            premium = (
                game_value(exceptional_pair)
                - game_value(root_singleton)
                - game_value(1 << player)
            )
            if premium < 0:
                raise AssertionError("exact-game coalition premium became negative")
            exceptional_transports.append(
                {
                    "deficit_player": player,
                    "new_exceptional": exceptional_pair,
                    "coalition_premium": str(premium),
                    "transport_slack_loss": str(root_advantage * premium),
                    "verified": True,
                }
            )
        forced_pair_decomposition = {
            **exceptional_transports[0],
            "identity": "1_{root}+1_{deficit_player}-1_{pair}=0",
        }
    return {
        "player_loads": [str(value) for value in loads],
        "nonroot_deficits": [str(value) for value in deficits],
        "root_advantage": str(root_advantage),
        "completion_coefficients": [
            {"coalition": coalition, "coefficient": str(coefficients[coalition])}
            for coalition in columns
        ],
        "incidence_identity": "sum coefficients*incidence = 1_N",
        "incidence_rank": rank,
        "support_size": len(columns),
        "classification": kind,
        "exceptional_coalition": negative[0] if negative else None,
        "semi_balanced_identity_verified": True,
        "minimality_verified": True,
        "indecomposability_tested": bool(negative),
        "indecomposable": bool(negative) and not decompositions,
        "decomposition_count": len(decompositions),
        "first_decomposition": decompositions[0] if decompositions else None,
        "forced_pair_decomposition": forced_pair_decomposition,
        "all_single_deficit_transports": exceptional_transports,
        "pair_floors": [str(value) for value in pair_floors],
        "pair_floor_root_deficit_slack": str(pair_floor_rdb_slack),
        "pair_floor_root_deficit_verified": True,
        "pair_lifted_completion": {
            "coefficients": [
                {
                    "coalition": coalition,
                    "coefficient": str(pair_lifted_coefficients[coalition]),
                }
                for coalition in pair_lifted_support
            ],
            "incidence_identity": "sum coefficients*incidence = 1_N",
            "incidence_rank": pair_lifted_rank,
            "support_size": len(pair_lifted_support),
            "exceptional_coalition": root_singleton,
            "minimality_verified": True,
            "game_inequality_slack": str(pair_lifted_game_slack),
            "equals_pair_floor_root_deficit_slack": True,
            "indecomposable": not pair_lifted_decompositions,
            "decomposition_count": len(pair_lifted_decompositions),
            "first_decomposition": (
                pair_lifted_decompositions[0]
                if pair_lifted_decompositions
                else None
            ),
            "exact_cone_facet": not pair_lifted_decompositions,
        },
    }


def master_without_witness(system):
    """Keep x,z rows and their direct tightness comparisons."""
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
        "aub": [
            [system["inequalities"][k][j] for j in columns]
            for k in inequality_rows
        ],
        "bub": [system["inequality_rhs"][k] for k in inequality_rows],
        "aeq": [
            [system["equalities"][k][j] for j in columns]
            for k in equality_rows
        ],
        "beq": [system["equality_rhs"][k] for k in equality_rows],
    }


def separator(coalitions, n, root, x):
    """Maximize the projected rooted-hinge inequality at fixed x,z."""
    width = len(coalitions)
    aub, bub = [], []
    for player in range(n):
        if player == root:
            continue
        aub.append([F(int(coalition >> player & 1)) for coalition in coalitions])
        bub.append(F(1))
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = F(-1)
        aub.append(row)
        bub.append(F(0))
    objective = []
    for coalition in coalitions:
        objective.append(
            -sum((x[i] for i in range(n) if coalition >> i & 1), F(0))
        )
    status, negative_value, weights = exact_linprog(objective, aub, bub)
    if status != "optimal":
        raise AssertionError(f"rooted-hinge separator is {status}")
    return -negative_value, weights


def projected_minimum(case, root):
    common = tuple(sorted(set(case["support_x"]).intersection(case["support_z"])))
    reduced_case = dict(case)
    reduced_case["support_z"] = common
    system = branch_system(reduced_case)
    n = system["n"]
    master = master_without_witness(system)
    coalitions = tuple(case["support_x"])
    cuts = []

    for _iteration in range(256):
        status, optimum, solution = exact_linprog(
            master["objective"],
            master["aub"],
            master["bub"],
            master["aeq"],
            master["beq"],
        )
        if status != "optimal":
            raise AssertionError(f"projected master is {status}")
        x = solution[:n]
        violation, weights = separator(coalitions, n, root, x)
        if violation <= 1:
            return optimum, cuts

        support = tuple(k for k, weight in enumerate(weights) if weight > 0)
        if len(support) > n - 1:
            raise AssertionError("extreme rooted-hinge packing exceeds support bound")
        row = [F(0)] * (2 * n)
        for weight, coalition in zip(weights, coalitions):
            if weight == 0:
                continue
            for player in range(n):
                if coalition >> player & 1:
                    row[player] += weight
        master["aub"].append(row)
        master["bub"].append(F(1))
        cuts.append(
            {
                "violated_value": str(violation),
                "support": [
                    {
                        "coalition": coalitions[k],
                        "weight": str(weights[k]),
                    }
                    for k in support
                ],
                "semi_balanced_completion": semi_balanced_completion(
                    coalitions, weights, n, root, case
                ),
            }
        )
    raise AssertionError("rooted-hinge cutting plane did not terminate")


def audit_case(case0):
    case = dict(case0)
    common = tuple(sorted(set(case["support_x"]).intersection(case["support_z"])))
    case["support_z"] = common
    system = branch_system(case)
    n = system["n"]
    coordinate_overlap = tuple(min(case["x"][i], case["z"][i]) for i in range(n))
    roots = tuple(
        i for i, value in enumerate(coordinate_overlap)
        if value == max(coordinate_overlap)
    )
    rows = []
    for root in roots:
        projected, cuts = projected_minimum(case0, root)
        direct = one_witness_minimum(system, root)
        if projected != direct:
            raise AssertionError(
                {
                    "case": case["name"],
                    "root": root,
                    "projected": str(projected),
                    "direct": str(direct),
                }
            )
        rows.append(
            {
                "root": root,
                "projected_minimum": str(projected),
                "direct_witness_minimum": str(direct),
                "cut_count": len(cuts),
                "maximum_cut_support": max(
                    (len(cut["support"]) for cut in cuts), default=0
                ),
                "cuts": cuts,
            }
        )
    return {
        "name": case["name"],
        "n": n,
        "lmin_support": list(case["support_x"]),
        "common_hinge_support": list(common),
        "maximum_overlap_roots": list(roots),
        "roots": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact rooted-hinge projection controls",
        "human_theorem_audited": (
            "after common rows identify x(S)=z(S), eliminating a singleton-zero "
            "witness gives all rooted fractional Lmin-support packing inequalities; "
            "extreme packings use at most n-1 rows, and their singleton-slack "
            "completions are min-semi-balanced systems"
        ),
        "positive_root_nonfacet_theorem_audited": (
            "every generated positive-root completion has a nonroot deficit; "
            "the root and deficit singletons give an explicit two-singleton "
            "Studeny--Kratochvil decomposition"
        ),
        "pair_floor_projection_audited": (
            "retaining witness bounds w_i>=v({r,i}) adds the exact weighted "
            "exceptional-transport premium to root-deficit balance"
        ),
        "rooted_pair_lift_theorem_audited": (
            "replacing deficit singleton columns by rooted-pair columns "
            "preserves incidence rank and turns the pair-floor budget into a "
            "min-semi-balanced exact-game inequality; indecomposability is "
            "tested exhaustively"
        ),
        "scope": (
            "maximum-overlap roots of six hostile fixed branches and two sharp "
            "orientations; exact controls only, not an all-n proof"
        ),
        "cases": [audit_case(case) for case in CONTROL_CASES],
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
