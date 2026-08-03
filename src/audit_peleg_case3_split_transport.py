"""Audit the role-specific split potential for Peleg case 3.

For a normalized parent MBC C with case-3 marking I, put

    kappa = 1-lambda(I),  theta = kappa/lambda_delta.

The split interpolation potential w is defined on C by value one on I,
theta on the split column delta, and zero elsewhere.  Balancedness forces
w(N)=1, and convexity transports the split column exactly.  This script
checks the remaining support signs and the witness corrections forced by
the three distinguished split roles that retain the root geometry.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from analyze_two_color_box_capacity import rat
from audit_unit_root_absorption_n7 import absorption_subcollection, solve
from hunt_root_absorption_descendants_n7 import (
    A,
    A_PLAYER,
    B,
    COSINGLETON_A_SOURCE,
    COSINGLETON_B_SOURCE,
    NEW_PLAYER,
    SOURCE_N,
    WITNESS,
    decoded_root,
    regularized_sources,
)


def coalition_value(potential, coalition):
    return sum(
        (potential[player] for player in range(SOURCE_N)
         if coalition >> player & 1), F(0)
    )


def assigned_interpolation(collection, assigned, second_universe):
    """Maximize the exact potential's minimum on the second support."""
    eta = SOURCE_N
    objective = np.zeros(SOURCE_N + 1)
    objective[eta] = -1
    A_eq = []
    b_eq = []
    for index, (coalition, _weight) in enumerate(collection):
        row = np.zeros(SOURCE_N + 1)
        for player in range(SOURCE_N):
            if coalition >> player & 1:
                row[player] = 1
        A_eq.append(row)
        b_eq.append(float(assigned[index]))
    A_ub = []
    for coalition in second_universe:
        row = np.zeros(SOURCE_N + 1)
        row[eta] = 1
        for player in range(SOURCE_N):
            if coalition >> player & 1:
                row[player] = -1
        A_ub.append(row)
    result = linprog(
        objective,
        A_ub=np.asarray(A_ub),
        b_ub=np.zeros(len(A_ub)),
        A_eq=np.asarray(A_eq),
        b_eq=np.asarray(b_eq),
        bounds=[(None, None)] * (SOURCE_N + 1),
        method="highs",
    )
    assert result.success, result.message
    solution = tuple(rat(value) for value in result.x)
    potential, minimum = solution[:SOURCE_N], solution[eta]
    assert all(
        coalition_value(potential, coalition) == assigned[index]
        for index, (coalition, _weight) in enumerate(collection)
    )
    assert all(
        coalition_value(potential, coalition) >= minimum
        for coalition in second_universe
    )
    return potential, minimum


def add_vectors(left, scale, right):
    return tuple(x + scale*y for x, y in zip(left, right))


def case3_descendant(collection, subset, delta, kappa):
    transformed = []
    delta_coalition, delta_weight = collection[delta]
    for index, (coalition, weight) in enumerate(collection):
        if index in subset:
            transformed.append((coalition | NEW_PLAYER, weight))
        elif index == delta:
            transformed.append((coalition, delta_weight-kappa))
        else:
            transformed.append((coalition, weight))
    transformed.append((delta_coalition | NEW_PLAYER, kappa))
    return tuple(sorted(transformed))


def split_aware_absorber(
        root_core, second_core, marked_root, singleton_capacity, m_A):
    """Find an old-player absorber whose lift has the right new degree.

    Root and second allocations are kept separate because only marked root
    coalitions acquire the new player.  A privately lifted second leaf also
    supplies a new singleton of the displayed capacity.
    """
    root_coalitions = tuple(sorted(root_core))
    second_coalitions = tuple(sorted(second_core))
    root_position = {
        coalition: index for index, coalition in enumerate(root_coalitions)
    }
    second_start = len(root_coalitions)
    second_position = {
        coalition: second_start+index
        for index, coalition in enumerate(second_coalitions)
    }
    beta = second_start+len(second_coalitions)
    delta = beta+1
    singleton = beta+2
    variable_count = beta+3

    A_eq = []
    b_eq = []
    for player in range(SOURCE_N):
        row = np.zeros(variable_count)
        for coalition, position in root_position.items():
            if coalition >> player & 1:
                row[position] = 1
        for coalition, position in second_position.items():
            if coalition >> player & 1:
                row[position] = 1
        row[beta] = -1
        if WITNESS >> player & 1:
            row[delta] = -1
        A_eq.append(row)
        b_eq.append(float(m_A*int(player == A_PLAYER)))

    # The child's new-player degree must equal the common baseline beta.
    row = np.zeros(variable_count)
    for coalition in marked_root:
        if coalition in root_position:
            row[root_position[coalition]] = 1
    row[singleton] = 1
    row[beta] = -1
    A_eq.append(row)
    b_eq.append(0)

    A_ub = []
    b_ub = []
    row = np.zeros(variable_count)
    if B in root_position:
        row[root_position[B]] = 1
    if B in second_position:
        row[second_position[B]] = 1
    A_ub.append(row)
    b_ub.append(float(root_core.get(B, F(0))))

    bounds = (
        [(0, float(root_core[coalition])) for coalition in root_coalitions]
        + [(0, float(second_core[coalition]))
           for coalition in second_coalitions]
        + [(None, None), (None, None), (0, float(singleton_capacity))]
    )
    result = linprog(
        np.zeros(variable_count),
        A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    if not result.success:
        return None
    solution = tuple(rat(value) for value in result.x)
    assert all(
        sum(rat(coefficient)*value
            for coefficient, value in zip(row, solution)) == rat(rhs)
        for row, rhs in zip(A_eq, b_eq)
    )
    assert all(
        sum(rat(coefficient)*value
            for coefficient, value in zip(row, solution)) <= rat(rhs)
        for row, rhs in zip(A_ub, b_ub)
    )
    assert all(
        (lower is None or value >= rat(lower))
        and (upper is None or value <= rat(upper))
        for value, (lower, upper) in zip(solution, bounds)
    )
    return {
        "beta": str(solution[beta]),
        "delta": str(solution[delta]),
        "new_singleton_mass": str(solution[singleton]),
        "root_subcollection": {
            str(coalition): str(solution[position])
            for coalition, position in root_position.items()
            if solution[position]
        },
        "second_subcollection": {
            str(coalition): str(solution[position])
            for coalition, position in second_position.items()
            if solution[position]
        },
    }


def audit():
    roots, lifted_seconds = regularized_sources()
    second_universe = tuple(sorted({
        coalition
        for second, _m_B in lifted_seconds
        for coalition in second
        if coalition < (1 << SOURCE_N)
    }))
    witness_player = WITNESS.bit_length() - 1
    records = []
    role_counts = Counter()
    root_only_counts = Counter()
    forced_identity_failures = 0

    for root_index, collection in enumerate(roots, 1):
        collection_weights = dict(collection)
        m_A = collection_weights[COSINGLETON_A_SOURCE]
        m_B = collection_weights[COSINGLETON_B_SOURCE]
        root_core = dict(collection_weights)
        root_core.pop(COSINGLETON_A_SOURCE)
        root_core.pop(COSINGLETON_B_SOURCE)
        parent_root_only = absorption_subcollection(
            root_core, {}, m_A, require=False, players=SOURCE_N,
            A_player=A_PLAYER, B=B, witness=WITNESS,
        ) is not None
        comp_a = next(
            index for index, (coalition, _weight) in enumerate(collection)
            if coalition == COSINGLETON_A_SOURCE
        )
        comp_b = next(
            index for index, (coalition, _weight) in enumerate(collection)
            if coalition == COSINGLETON_B_SOURCE
        )
        B_index = next(
            index for index, (coalition, _weight) in enumerate(collection)
            if coalition == B
        )

        for size in range(2, len(collection) + 1):
            for subset_tuple in itertools.combinations(range(len(collection)), size):
                subset = set(subset_tuple)
                if B_index in subset:
                    continue
                marked_weight = sum(
                    (collection[index][1] for index in subset), F(0)
                )
                if not marked_weight < 1:
                    continue
                kappa = 1-marked_weight
                for delta, (delta_coalition, delta_weight) in enumerate(collection):
                    if delta in subset or not delta_weight > kappa:
                        continue
                    descendant = case3_descendant(collection, subset, delta, kappa)
                    decoded = decoded_root(descendant)
                    if decoded is None:
                        continue
                    child_items, child_m_A, child_m_B = decoded
                    child_root_only_absorber = absorption_subcollection(
                        dict(child_items), {}, child_m_A, require=False,
                        players=SOURCE_N+1, A_player=A_PLAYER, B=B,
                        witness=WITNESS,
                    )
                    child_root_only = child_root_only_absorber is not None

                    role = (
                        "cosingleton_a" if delta == comp_a else
                        "cosingleton_b" if delta == comp_b else
                        "B" if delta == B_index else "core"
                    )
                    role_counts[role] += 1
                    root_only_counts[(role, parent_root_only)] += 1
                    theta = kappa/delta_weight
                    assigned = tuple(
                        F(1) if index in subset else
                        theta if index == delta else F(0)
                        for index in range(len(collection))
                    )
                    potential, minimum = assigned_interpolation(
                        collection, assigned, second_universe
                    )
                    expected = {
                        "cosingleton_a": (1-theta, F(0), F(0)),
                        "cosingleton_b": (F(0), 1-theta, -(1-theta)),
                        "B": (F(0), F(0), theta),
                    }[role]
                    actual = (
                        potential[A_PLAYER], potential[3],
                        potential[witness_player],
                    )
                    forced_identity_failures += not (
                        sum(potential, F(0)) == 1 and actual == expected
                    )

                    corrections = {}
                    for anchor in range(SOURCE_N):
                        if anchor == witness_player:
                            continue
                        # Add -w_u at u and subtract the same amount at an
                        # anchor, preserving total sum while forcing u to 0.
                        direction = tuple(
                            int(player == witness_player)-int(player == anchor)
                            for player in range(SOURCE_N)
                        )
                        corrected = add_vectors(
                            potential, -potential[witness_player], direction
                        )
                        root_differences = {
                            str(coalition): str(
                                coalition_value(corrected, coalition)
                                - assigned[index]
                            )
                            for index, (coalition, _weight) in enumerate(collection)
                            if index not in (comp_a, comp_b)
                        }
                        corrections[str(anchor)] = {
                            "potential": [str(value) for value in corrected],
                            "minimum_second_value": str(min(
                                coalition_value(corrected, coalition)
                                for coalition in second_universe
                            )),
                            "minimum_root_interpolation_difference": str(min(
                                F(value) for value in root_differences.values()
                            )),
                            "root_interpolation_differences": root_differences,
                        }

                    records.append({
                        "root_index": root_index,
                        "parent_root_only": parent_root_only,
                        "child_root_only": child_root_only,
                        "child_root_only_absorber": child_root_only_absorber,
                        "parent_m_A": str(m_A),
                        "parent_m_B": str(m_B),
                        "child_m_A": str(child_m_A),
                        "child_m_B": str(child_m_B),
                        "child_root_core": [
                            [coalition, str(weight)]
                            for coalition, weight in child_items
                        ],
                        "regularized_parent_collection": [
                            [coalition, str(weight)]
                            for coalition, weight in collection
                        ],
                        "subset_indices_1based": [index+1 for index in subset_tuple],
                        "delta_index_1based": delta+1,
                        "delta_role": role,
                        "kappa": str(kappa),
                        "delta_weight": str(delta_weight),
                        "theta": str(theta),
                        "potential": [str(value) for value in potential],
                        "minimum_second_value": str(minimum),
                        "forced_abu": [str(value) for value in actual],
                        "corrections_by_anchor": corrections,
                    })

    assert sum(role_counts.values()) == 104
    role_minima = {
        role: min(
            F(record["minimum_second_value"])
            for record in records if record["delta_role"] == role
        )
        for role in role_counts
    }
    best_anchor_counts = Counter()
    correction_feasible_counts = Counter()
    child_root_only_counts = Counter()
    for record in records:
        child_root_only_counts[
            (record["delta_role"], record["parent_root_only"],
             record["child_root_only"])
        ] += 1
        scored = []
        for anchor, correction in record["corrections_by_anchor"].items():
            pair = (
                F(correction["minimum_root_interpolation_difference"]),
                F(correction["minimum_second_value"]),
            )
            scored.append((pair, int(anchor)))
            if pair[0] >= 0 and pair[1] >= 0:
                correction_feasible_counts[(record["delta_role"], int(anchor))] += 1
        best_anchor_counts[(record["delta_role"], max(scored)[1])] += 1

    # In the B-split comparison, convex transport can lose at most
    # kappa*r_B at the split hinge.  Minimize the parent remainder minus
    # precisely that loss for every distinct parent/second pairing.
    B_loss_margins = []
    seen_B_parents = set()
    for record in records:
        if record["delta_role"] != "B":
            continue
        key = (record["root_index"], record["kappa"])
        if key in seen_B_parents:
            continue
        seen_B_parents.add(key)
        root = dict(roots[record["root_index"]-1])
        parent_m_A = root.pop(COSINGLETON_A_SOURCE)
        parent_m_B = root.pop(COSINGLETON_B_SOURCE)
        kappa = F(record["kappa"])
        for second_index, (lifted_second, second_m_B) in enumerate(
                lifted_seconds, 1):
            source_second = dict(lifted_second)
            source_second.pop(NEW_PLAYER)
            scale = parent_m_B/second_m_B
            source_second = {
                coalition: scale*weight
                for coalition, weight in source_second.items()
            }
            result = solve(
                root, source_second, parent_m_A, parent_m_B,
                players=SOURCE_N, A=A, A_player=A_PLAYER, B=B,
                witness=WITNESS, r_B_penalty=kappa,
            )
            B_loss_margins.append({
                "root_index": record["root_index"],
                "kappa": record["kappa"],
                "second_index": second_index,
                "minimum_parent_remainder_minus_kappa_r_B": result["minimum"],
                "r_A": result["r_A"],
                "r_B": result["r_B"],
                "primal_exact": result["primal_exact"],
                "dual_exact": result["dual_exact"],
                "parent_root_core": [
                    [coalition, str(weight)]
                    for coalition, weight in sorted(root.items())
                ],
                "parent_second_core": [
                    [coalition, str(weight)]
                    for coalition, weight in sorted(source_second.items())
                ],
                "parent_m_A": str(parent_m_A),
                "parent_m_B": str(parent_m_B),
                "certificate": result,
            })

    residual_b_absorbers = []
    modified_parent_absorbers = []
    residual_b_split_aware_absorbers = []
    for record in records:
        if (record["delta_role"] != "cosingleton_b"
                or record["child_root_only"]):
            continue
        child_root = {
            coalition: F(weight)
            for coalition, weight in record["child_root_core"]
        }
        child_m_A = F(record["child_m_A"])
        child_m_B = F(record["child_m_B"])
        for second_index, (lifted_second, second_m_B) in enumerate(
                lifted_seconds, 1):
            scale = child_m_B/second_m_B
            child_second = {
                coalition: scale*weight
                for coalition, weight in lifted_second.items()
            }
            absorber = absorption_subcollection(
                child_root, child_second, child_m_A, players=SOURCE_N+1,
                A_player=A_PLAYER, B=B, witness=WITNESS,
            )
            residual_b_absorbers.append({
                "root_index": record["root_index"],
                "subset_indices_1based": record["subset_indices_1based"],
                "second_index": second_index,
                "absorber": absorber,
            })

        parent_collection = roots[record["root_index"]-1]
        marked_indices = {
            index-1 for index in record["subset_indices_1based"]
        }
        marked_root = {
            coalition
            for index, (coalition, _weight) in enumerate(parent_collection)
            if index in marked_indices
            and coalition not in (
                COSINGLETON_A_SOURCE, COSINGLETON_B_SOURCE
            )
        }
        parent_root = dict(parent_collection)
        parent_m_A = parent_root.pop(COSINGLETON_A_SOURCE)
        parent_m_B = parent_root.pop(COSINGLETON_B_SOURCE)
        transferred = parent_m_B-child_m_B
        parent_root[COSINGLETON_B_SOURCE] = transferred
        for second_index, (lifted_second, second_m_B) in enumerate(
                lifted_seconds, 1):
            source_second = dict(lifted_second)
            source_second.pop(NEW_PLAYER)
            scale = child_m_B/second_m_B
            source_second = {
                coalition: scale*weight
                for coalition, weight in source_second.items()
            }
            absorber = absorption_subcollection(
                parent_root, source_second, parent_m_A,
                require=False,
                players=SOURCE_N, A_player=A_PLAYER, B=B,
                witness=WITNESS,
            )
            modified_parent_absorbers.append({
                "root_index": record["root_index"],
                "subset_indices_1based": record["subset_indices_1based"],
                "second_index": second_index,
                "transferred_cosingleton_b_mass": str(transferred),
                "absorber_exists": absorber is not None,
                "absorber": absorber,
            })
            singleton_capacity = scale*lifted_second[NEW_PLAYER]
            split_absorber = split_aware_absorber(
                parent_root, source_second, marked_root,
                singleton_capacity, parent_m_A,
            )
            residual_b_split_aware_absorbers.append({
                "root_index": record["root_index"],
                "subset_indices_1based": record["subset_indices_1based"],
                "second_index": second_index,
                "marked_root_coalitions": sorted(marked_root),
                "singleton_capacity": str(singleton_capacity),
                "m_A": str(parent_m_A),
                "modified_root_core": [
                    [coalition, str(weight)]
                    for coalition, weight in sorted(parent_root.items())
                ],
                "source_second_core": [
                    [coalition, str(weight)]
                    for coalition, weight in sorted(source_second.items())
                ],
                "absorber_exists": split_absorber is not None,
                "absorber": split_absorber,
            })

    return {
        "status": "Peleg case 3 closed on the certified root family",
        "case3_closed_for_certified_family": (
            forced_identity_failures == 0
            and role_minima["cosingleton_a"] >= 0
            and correction_feasible_counts[("B", 3)] == role_counts["B"]
            and min(F(record[
                "minimum_parent_remainder_minus_kappa_r_B"
            ]) for record in B_loss_margins) >= 0
            and sum(
                record["delta_role"] == "cosingleton_b"
                and record["child_root_only"]
                for record in records
            ) == 50
            and all(record["absorber_exists"]
                    for record in residual_b_split_aware_absorbers)
        ),
        "decoded_emissions": len(records),
        "role_counts": dict(sorted(role_counts.items())),
        "root_only_parent_counts": {
            f"{role}:{str(flag).lower()}": count
            for (role, flag), count in sorted(root_only_counts.items())
        },
        "root_only_transition_counts": {
            f"{role}:{str(parent).lower()}->{str(child).lower()}": count
            for (role, parent, child), count
            in sorted(child_root_only_counts.items())
        },
        "forced_identity_failures": forced_identity_failures,
        "minimum_second_value_by_role": {
            role: str(value) for role, value in sorted(role_minima.items())
        },
        "fully_nonnegative_correction_counts_by_role_anchor": {
            f"{role}:{anchor}": count
            for (role, anchor), count in sorted(correction_feasible_counts.items())
        },
        "lexicographically_best_anchor_counts": {
            f"{role}:{anchor}": count
            for (role, anchor), count in sorted(best_anchor_counts.items())
        },
        "B_split_loss_margin_minimum": str(min(
            F(record["minimum_parent_remainder_minus_kappa_r_B"])
            for record in B_loss_margins
        )),
        "B_split_loss_margin_records": B_loss_margins,
        "residual_b_pair_count": len(residual_b_absorbers),
        "b_split_child_root_only_emissions": sum(
            record["delta_role"] == "cosingleton_b"
            and record["child_root_only"]
            for record in records
        ),
        "b_split_residual_emissions": sum(
            record["delta_role"] == "cosingleton_b"
            and not record["child_root_only"]
            for record in records
        ),
        "residual_b_absorbers": residual_b_absorbers,
        "modified_parent_absorber_failures": sum(
            not record["absorber_exists"]
            for record in modified_parent_absorbers
        ),
        "modified_parent_absorbers": modified_parent_absorbers,
        "residual_b_split_aware_absorber_failures": sum(
            not record["absorber_exists"]
            for record in residual_b_split_aware_absorbers
        ),
        "residual_b_split_aware_absorbers":
            residual_b_split_aware_absorbers,
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
