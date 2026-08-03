"""Use Peleg's second and third constructions to attack the coefficient ceiling.

Start from every six-player minimal balanced collection represented by a
positive leaf circuit containing the artificial singleton {a} and arm A.
The second case adds a new singleton {p} of weight ``alpha-q(I)`` and lifts
every coalition in I through p.  It is dangerous because a lifted coalition
keeps its old weight while the new singleton can be small.

The third case adds player p and splits {a}.  For a subcollection I with

    alpha - m < q(I) < alpha,

the new singleton coefficient is m' = m + q(I) - alpha.  The arm coefficient
is unchanged (the arm itself is lifted when it belongs to I).  This script
checks whether q_A > |A'| m' in both cases and verifies every emitted
seven-player collection directly in exact arithmetic.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from hunt_glued_local_circuits import coefficient, enumerate_local
from search_both_sensitive_circuits import eliminated_matrix


SOURCE_PLAYERS = 6
NEW_PLAYER = 1 << SOURCE_PLAYERS
SELECTED_PLAYER = 0


def degree(collection, players):
    return tuple(
        sum((weight for coalition, weight in collection
             if coalition >> player & 1), F(0))
        for player in range(players)
    )


def exact_incidence_rank(collection, players):
    """Rank of coalition incidence columns by rational elimination."""
    matrix = [
        [F(int(coalition >> player & 1)) for coalition, _weight in collection]
        for player in range(players)
    ]
    height = len(matrix)
    width = len(matrix[0]) if matrix else 0
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (row for row in range(pivot_row, height)
             if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
        for row in range(height):
            if row == pivot_row or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == height:
            break
    return pivot_row


def primitive(values):
    from math import gcd, lcm
    denominator = 1
    for value in values:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in values]
    divisor = abs(gcd(*integers))
    return [value // divisor for value in integers]


def hunt():
    records = []
    source_collections = {}
    total_source_circuits = 0
    peleg_subsets_checked = 0
    valid_third_case_subsets = 0
    for arm_size in range(2, SOURCE_PLAYERS):
        arm = (1 << arm_size) - 1
        other_arm = 1 << arm_size
        matrix, _ineq, _eq, rowmeta = eliminated_matrix(
            SOURCE_PLAYERS, arm, other_arm
        )
        mono = rowmeta.index(("mono", 0, 1, SELECTED_PLAYER, arm))
        arm_core = rowmeta.index(("core", 1, arm))
        circuits = enumerate_local(
            matrix,
            rowmeta,
            1,
            (mono, arm_core),
            players=SOURCE_PLAYERS,
        )
        total_source_circuits += len(circuits)
        for circuit_index, circuit in enumerate(circuits, 1):
            support, weights = circuit
            source_core = [
                (rowmeta[index][2], F(weight))
                for index, weight in zip(support, weights)
                if rowmeta[index][0] == "core"
            ]
            m = coefficient(circuit, mono)
            arm_weight = coefficient(circuit, arm_core)
            source_degrees = degree(source_core, SOURCE_PLAYERS)
            alpha_values = [
                source_degrees[player]
                + m * int(player == SELECTED_PLAYER)
                for player in range(SOURCE_PLAYERS)
            ]
            assert len(set(alpha_values)) == 1
            alpha = alpha_values[0]
            normalized_collection = tuple(sorted(
                [(1 << SELECTED_PLAYER, m / alpha)]
                + [(coalition, weight / alpha)
                   for coalition, weight in source_core]
            ))
            source_collections[normalized_collection] = {
                "source_arm_size": arm_size,
                "source_circuit_index": circuit_index,
            }

            for subset_size in range(len(source_core) + 1):
                for subset in itertools.combinations(
                        range(len(source_core)), subset_size):
                    peleg_subsets_checked += 1
                    subset_weight = sum(
                        (source_core[index][1] for index in subset), F(0)
                    )
                    if not alpha - m < subset_weight < alpha:
                        continue
                    valid_third_case_subsets += 1
                    new_m = m + subset_weight - alpha
                    split_weight = alpha - subset_weight
                    lifted = set(subset)
                    new_core = [
                        (coalition | NEW_PLAYER if index in lifted else coalition,
                         weight)
                        for index, (coalition, weight) in enumerate(source_core)
                    ]
                    new_core.append(
                        ((1 << SELECTED_PLAYER) | NEW_PLAYER, split_weight)
                    )
                    new_arm = (
                        arm | NEW_PLAYER
                        if next(index for index,(coalition,_weight)
                                in enumerate(source_core) if coalition == arm)
                            in lifted
                        else arm
                    )
                    ratio = arm_weight / new_m
                    if ratio <= new_arm.bit_count():
                        continue

                    new_degrees = degree(new_core, SOURCE_PLAYERS + 1)
                    assert tuple(
                        new_degrees[player]
                        + new_m * int(player == SELECTED_PLAYER)
                        for player in range(SOURCE_PLAYERS + 1)
                    ) == (alpha,) * (SOURCE_PLAYERS + 1)
                    assert len({coalition for coalition,_weight in new_core}) == len(new_core)
                    all_weights = [new_m] + [weight for _coalition,weight in new_core]
                    full_collection = [
                        (1 << SELECTED_PLAYER, new_m)
                    ] + new_core
                    assert exact_incidence_rank(
                        full_collection, SOURCE_PLAYERS + 1
                    ) == len(full_collection)
                    integer_weights = primitive(all_weights)
                    records.append({
                        "peleg_case": 3,
                        "source_arm_size": arm_size,
                        "source_circuit_index": circuit_index,
                        "source_arm_mask": arm,
                        "source_alpha": str(alpha),
                        "source_singleton_weight": str(m),
                        "source_arm_weight": str(arm_weight),
                        "peleg_subset_indices_1based": [index + 1 for index in subset],
                        "peleg_subset_weight": str(subset_weight),
                        "new_arm_mask": new_arm,
                        "new_arm_size": new_arm.bit_count(),
                        "new_singleton_weight": str(new_m),
                        "new_arm_to_singleton_ratio": str(ratio),
                        "new_efficiency_level": str(alpha),
                        "new_core": [
                            [coalition,str(weight)] for coalition,weight in new_core
                        ],
                        "primitive_weights_singleton_then_core": integer_weights,
                    })

    second_case_subsets_checked = 0
    valid_second_case_subsets = 0
    second_case_arm_tests = 0
    maximum_second_case_ratio = F(0)
    maximum_second_case_record = None
    for source_index, (collection, provenance) in enumerate(
            sorted(source_collections.items()), 1):
        for subset_size in range(1, len(collection) + 1):
            for subset in itertools.combinations(range(len(collection)), subset_size):
                second_case_subsets_checked += 1
                subset_weight = sum(
                    (collection[index][1] for index in subset), F(0)
                )
                if subset_weight >= 1:
                    continue
                valid_second_case_subsets += 1
                new_m = 1 - subset_weight
                lifted = set(subset)
                for arm_index in subset:
                    second_case_arm_tests += 1
                    source_arm, arm_weight = collection[arm_index]
                    new_arm = source_arm | NEW_PLAYER
                    ratio = arm_weight / new_m
                    candidate = {
                        "peleg_case": 2,
                        "source_collection_index": source_index,
                        **provenance,
                        "source_arm_mask": source_arm,
                        "source_arm_size": source_arm.bit_count(),
                        "source_arm_weight": str(arm_weight),
                        "peleg_subset_indices_1based": [
                            index + 1 for index in subset
                        ],
                        "peleg_subset_weight": str(subset_weight),
                        "new_arm_mask": new_arm,
                        "new_arm_size": new_arm.bit_count(),
                        "new_singleton_weight": str(new_m),
                        "new_arm_to_singleton_ratio": str(ratio),
                    }
                    if ratio > maximum_second_case_ratio:
                        maximum_second_case_ratio = ratio
                        maximum_second_case_record = candidate
                    if ratio <= new_arm.bit_count():
                        continue

                    new_core = [
                        (coalition | NEW_PLAYER if index in lifted else coalition,
                         weight)
                        for index, (coalition, weight) in enumerate(collection)
                    ]
                    new_degrees = degree(new_core, SOURCE_PLAYERS + 1)
                    assert new_degrees == (
                        (F(1),) * SOURCE_PLAYERS + (1 - new_m,)
                    )
                    assert degree(
                        [(NEW_PLAYER, new_m)] + new_core,
                        SOURCE_PLAYERS + 1,
                    ) == (F(1),) * (SOURCE_PLAYERS + 1)
                    assert len({coalition for coalition, _weight in new_core}) == len(new_core)
                    all_weights = [new_m] + [weight for _coalition, weight in new_core]
                    full_collection = [(NEW_PLAYER, new_m)] + new_core
                    assert exact_incidence_rank(
                        full_collection, SOURCE_PLAYERS + 1
                    ) == len(full_collection)
                    candidate["new_efficiency_level"] = "1"
                    candidate["new_core"] = [
                        [coalition, str(weight)]
                        for coalition, weight in new_core
                    ]
                    candidate["primitive_weights_singleton_then_core"] = primitive(
                        all_weights
                    )
                    records.append(candidate)
    records.sort(
        key=lambda item: (
            -F(item["new_arm_to_singleton_ratio"]),
            item["new_arm_size"],
            item["source_circuit_index"],
        )
    )
    violations_by_case = Counter(record["peleg_case"] for record in records)
    violations_by_arm_size = Counter(record["new_arm_size"] for record in records)
    violations_by_ratio = Counter(record["new_arm_to_singleton_ratio"] for record in records)
    lifted_size_three = None
    if records and records[0]["peleg_case"] == 2:
        sharp = records[0]
        sharp_arm = sharp["new_arm_mask"]
        sharp_m = F(sharp["new_singleton_weight"])
        sharp_core = [
            (coalition, F(weight))
            for coalition, weight in sharp["new_core"]
        ]
        arm_index = next(
            index for index, (coalition, _weight) in enumerate(sharp_core)
            if coalition == sharp_arm
        )
        companion_index = next(
            index for index, (coalition, weight) in enumerate(sharp_core)
            if index != arm_index and weight == 1 - sharp_core[arm_index][1]
        )
        eighth_player = 1 << (SOURCE_PLAYERS + 1)
        lifted_indices = {arm_index, companion_index}
        lifted_core = [
            (coalition | eighth_player if index in lifted_indices else coalition,
             weight)
            for index, (coalition, weight) in enumerate(sharp_core)
        ]
        lifted_arm = sharp_arm | eighth_player
        lifted_collection = [(NEW_PLAYER, sharp_m)] + lifted_core
        assert degree(lifted_collection, SOURCE_PLAYERS + 2) == (
            F(1),
        ) * (SOURCE_PLAYERS + 2)
        assert exact_incidence_rank(
            lifted_collection, SOURCE_PLAYERS + 2
        ) == len(lifted_collection)
        lifted_size_three = {
            "construction": "Peleg case 1 applied to the sharp n=7 case-2 counterexample",
            "players": SOURCE_PLAYERS + 2,
            "singleton_mask": NEW_PLAYER,
            "singleton_weight": str(sharp_m),
            "arm_mask": lifted_arm,
            "arm_size": lifted_arm.bit_count(),
            "arm_weight": str(sharp_core[arm_index][1]),
            "arm_to_singleton_ratio": str(sharp_core[arm_index][1] / sharp_m),
            "lifted_source_indices_1based": [arm_index + 1, companion_index + 1],
            "collection": [
                [coalition, str(weight)] for coalition, weight in lifted_collection
            ],
            "primitive_weights": primitive(
                [weight for _coalition, weight in lifted_collection]
            ),
            "exact_incidence_rank": len(lifted_collection),
        }
    return {
        "status": (
            "PELEG COUNTEREXAMPLE TO COEFFICIENT CEILING FOUND"
            if records else "no Peleg second- or third-case escape from n=6 sources"
        ),
        "source_players": SOURCE_PLAYERS,
        "target_players": SOURCE_PLAYERS + 1,
        "source_local_circuits": total_source_circuits,
        "distinct_source_collections": len(source_collections),
        "peleg_subsets_checked": peleg_subsets_checked,
        "valid_third_case_subsets": valid_third_case_subsets,
        "second_case_subsets_checked": second_case_subsets_checked,
        "valid_second_case_subsets": valid_second_case_subsets,
        "second_case_arm_tests": second_case_arm_tests,
        "coefficient_ceiling_violations": len(records),
        "violations_by_peleg_case": {
            str(key): value for key, value in sorted(violations_by_case.items())
        },
        "violations_by_new_arm_size": {
            str(key): value for key, value in sorted(violations_by_arm_size.items())
        },
        "violations_by_ratio": dict(sorted(violations_by_ratio.items())),
        "maximum_ratio": (
            records[0]["new_arm_to_singleton_ratio"] if records else None
        ),
        "maximum_second_case_ratio": str(maximum_second_case_ratio),
        "maximum_second_case_record": maximum_second_case_record,
        "lifted_arm_size_three_counterexample": lifted_size_three,
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(hunt(), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
