"""Attack the ratio-four frontier from every five-player MBC.

All 1,292 minimal balanced collections on five players are enumerated
directly as the positive vertices of A lambda = 1.  Peleg cases 1--3 then
generate a large exact subset of the six-player collections, including
sources that contain no singleton.  Every case-2 and singleton-splitting
case-3 extension to seven players is screened for an arm of size at most
three with arm/singleton coefficient ratio above four.

Peleg's two-parent fourth case is then generated from every pair of the
five-player vertices.  The published total of 200,214 six-player minimal
balanced collections is used as a completeness checksum before the final
screen.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from hunt_peleg_coefficient_ceiling_escape import degree, exact_incidence_rank


SOURCE_PLAYERS = 5


def exact_balancing_weights(support, players):
    """Unique positive solution of the incidence system, or ``None``."""
    width = len(support)
    matrix = [
        [F(int(coalition >> player & 1)) for coalition in support] + [F(1)]
        for player in range(players)
    ]
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (row for row in range(pivot_row, players)
             if matrix[row][column]),
            None,
        )
        if pivot is None:
            return None
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
        for row in range(players):
            if row == pivot_row or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                value - scale * pivot_entry
                for value, pivot_entry in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_row += 1
    if any(
            all(matrix[row][column] == 0 for column in range(width))
            and matrix[row][-1] != 0
            for row in range(pivot_row, players)):
        return None
    weights = tuple(matrix[row][-1] for row in range(width))
    return weights if all(weight > 0 for weight in weights) else None


def enumerate_minimal_balanced(players):
    coalitions = tuple(range(1,1 << players))
    collections = []
    full = (1 << players) - 1
    for size in range(1,players + 1):
        for support in itertools.combinations(coalitions,size):
            # Fast coverage gate before rational elimination.
            union = 0
            for coalition in support:
                union |= coalition
            if union != full:
                continue
            weights = exact_balancing_weights(support,players)
            if weights is not None:
                collections.append(tuple(zip(support,weights)))
    return collections


def canonical(collection):
    return tuple(sorted(collection))


def peleg_descendants(collection, players):
    new_player = 1 << players
    size = len(collection)
    for subset_size in range(size + 1):
        for subset_tuple in itertools.combinations(range(size),subset_size):
            subset = set(subset_tuple)
            subset_weight = sum(
                (collection[index][1] for index in subset),F(0)
            )
            if subset_weight == 1:
                yield 1,canonical([
                    (coalition | new_player if index in subset else coalition,weight)
                    for index,(coalition,weight) in enumerate(collection)
                ])
            if subset_weight < 1:
                yield 2,canonical([
                    (coalition | new_player if index in subset else coalition,weight)
                    for index,(coalition,weight) in enumerate(collection)
                ] + [(new_player,1-subset_weight)])
            if not subset_weight < 1:
                continue
            for delta,(delta_coalition,delta_weight) in enumerate(collection):
                if delta in subset or not subset_weight > 1-delta_weight:
                    continue
                transformed = []
                for index,(coalition,weight) in enumerate(collection):
                    if index in subset:
                        transformed.append((coalition | new_player,weight))
                    elif index == delta:
                        transformed.append((coalition,delta_weight+subset_weight-1))
                    else:
                        transformed.append((coalition,weight))
                transformed.append((delta_coalition | new_player,1-subset_weight))
                yield 3,canonical(transformed)


def support_bits(collection):
    return sum(1 << (coalition-1) for coalition,_weight in collection)


def coalitions_from_bits(bits):
    coalitions = []
    while bits:
        low = bits & -bits
        coalitions.append(low.bit_length())
        bits -= low
    return tuple(coalitions)


def peleg_fourth_descendants(first, second, players):
    """Fourth-case descendants for a rank-one union of two MBCs."""
    new_player = 1 << players
    union = tuple(sorted(
        {coalition for coalition,_weight in first}
        | {coalition for coalition,_weight in second}
    ))
    first_weights, second_weights = dict(first),dict(second)
    mu = tuple(first_weights.get(coalition,F(0)) for coalition in union)
    nu = tuple(second_weights.get(coalition,F(0)) for coalition in union)
    for subset_size in range(len(union)+1):
        for subset_tuple in itertools.combinations(range(len(union)),subset_size):
            mu_I = sum((mu[index] for index in subset_tuple),F(0))
            nu_I = sum((nu[index] for index in subset_tuple),F(0))
            if mu_I == nu_I:
                continue
            t = (1-mu_I)/(nu_I-mu_I)
            if not 0 < t < 1:
                continue
            subset = set(subset_tuple)
            weights = tuple((1-t)*left+t*right for left,right in zip(mu,nu))
            assert all(weight > 0 for weight in weights)
            yield canonical([
                (coalition | new_player if index in subset else coalition,weight)
                for index,(coalition,weight) in enumerate(zip(union,weights))
            ])


def valid_mbc(collection, players):
    return (
        len({coalition for coalition,_weight in collection}) == len(collection)
        and degree(collection,players) == (F(1),)*players
        and exact_incidence_rank(collection,players) == len(collection)
    )


def primitive(values):
    denominator = 1
    for value in values:
        denominator = math.lcm(denominator,value.denominator)
    integers = [int(value*denominator) for value in values]
    divisor = abs(math.gcd(*integers))
    return [value//divisor for value in integers]


def target_extensions(collection):
    """Peleg case-2/3 extensions with arm size <=3 and ratio above four."""
    players = SOURCE_PLAYERS + 1
    new_player = 1 << players
    size = len(collection)
    for subset_size in range(1,size + 1):
        for subset_tuple in itertools.combinations(range(size),subset_size):
            subset = set(subset_tuple)
            subset_weight = sum(
                (collection[index][1] for index in subset),F(0)
            )
            if subset_weight >= 1:
                continue
            new_singleton_weight = 1-subset_weight
            for arm_index in subset:
                arm,arm_weight = collection[arm_index]
                new_arm = arm | new_player
                ratio = arm_weight/new_singleton_weight
                if new_arm.bit_count() <= 3 and ratio > 4:
                    descendant = canonical([
                        (coalition | new_player if index in subset else coalition,weight)
                        for index,(coalition,weight) in enumerate(collection)
                    ] + [(new_player,new_singleton_weight)])
                    yield 2,subset_tuple,None,new_player,new_singleton_weight,new_arm,arm_weight,descendant
            for delta,(singleton,singleton_weight) in enumerate(collection):
                if (delta in subset or singleton.bit_count() != 1
                        or not subset_weight > 1-singleton_weight):
                    continue
                shrunken = singleton_weight+subset_weight-1
                for arm_index,(arm,arm_weight) in enumerate(collection):
                    if arm_index == delta or not arm & singleton:
                        continue
                    new_arm = arm | new_player if arm_index in subset else arm
                    ratio = arm_weight/shrunken
                    if new_arm.bit_count() > 3 or ratio <= 4:
                        continue
                    transformed = []
                    for index,(coalition,weight) in enumerate(collection):
                        if index in subset:
                            transformed.append((coalition | new_player,weight))
                        elif index == delta:
                            transformed.append((coalition,shrunken))
                        else:
                            transformed.append((coalition,weight))
                    transformed.append((singleton | new_player,1-subset_weight))
                    yield 3,subset_tuple,delta,singleton,shrunken,new_arm,arm_weight,canonical(transformed)


def hunt():
    five_player = enumerate_minimal_balanced(SOURCE_PLAYERS)
    assert len(five_player) == 1292
    generated_by_case = Counter()
    six_player = {}
    for collection in five_player:
        assert valid_mbc(collection,SOURCE_PLAYERS)
        for case,descendant in peleg_descendants(collection,SOURCE_PLAYERS):
            generated_by_case[case] += 1
            if descendant not in six_player:
                assert valid_mbc(descendant,SOURCE_PLAYERS + 1)
                six_player[descendant] = case

    # A fourth-case union has at most six columns because its incidence rank
    # is |C|-1 <= 5.  Cache unions: a rank-one balancing segment has exactly
    # the two endpoint vertices, so processing one endpoint pair suffices.
    indexed = [(collection,support_bits(collection)) for collection in five_player]
    seen_unions = set()
    rank_one_unions = 0
    raw_fourth_generated = 0
    for first_index,(first,first_bits) in enumerate(indexed):
        for second,second_bits in indexed[first_index+1:]:
            union_bits = first_bits | second_bits
            if union_bits.bit_count() > SOURCE_PLAYERS+1 or union_bits in seen_unions:
                continue
            seen_unions.add(union_bits)
            union = coalitions_from_bits(union_bits)
            dummy = tuple((coalition,F(1)) for coalition in union)
            if exact_incidence_rank(dummy,SOURCE_PLAYERS) != len(union)-1:
                continue
            rank_one_unions += 1
            for descendant in peleg_fourth_descendants(first,second,SOURCE_PLAYERS):
                raw_fourth_generated += 1
                if descendant not in six_player:
                    assert valid_mbc(descendant,SOURCE_PLAYERS+1)
                    six_player[descendant] = 4

    assert len(six_player) == 200214

    records = []
    violation_count = 0
    violations_by_case = Counter()
    violations_by_arm_size = Counter()
    violations_by_ratio = Counter()
    for source_index,collection in enumerate(sorted(six_player),1):
        # Count every admissible target emitted by the sharp inequality gate.
        for (case,subset,delta,singleton,singleton_weight,arm,arm_weight,
             descendant) in target_extensions(collection):
            violation_count += 1
            assert valid_mbc(descendant,SOURCE_PLAYERS + 2)
            record = {
                "source_collection_index": source_index,
                "peleg_case": case,
                "subset_indices_1based": [index+1 for index in subset],
                "delta_index_1based": delta+1 if delta is not None else None,
                "singleton_mask": singleton,
                "singleton_weight": str(singleton_weight),
                "arm_mask": arm,
                "arm_size": arm.bit_count(),
                "arm_weight": str(arm_weight),
                "arm_to_singleton_ratio": str(arm_weight/singleton_weight),
                "collection": [[S,str(weight)] for S,weight in descendant],
                "primitive_weights": primitive(
                    [weight for _S,weight in descendant]
                ),
                "exact_incidence_rank": len(descendant),
            }
            violations_by_case[case] += 1
            violations_by_arm_size[arm.bit_count()] += 1
            violations_by_ratio[str(arm_weight/singleton_weight)] += 1
            records.append(record)
            if len(records) > 2000:
                records.sort(key=lambda item:-F(item["arm_to_singleton_ratio"]))
                del records[2000:]
    records.sort(key=lambda item:-F(item["arm_to_singleton_ratio"]))
    return {
        "status": (
            "ratio above four found from the complete n=6 source family"
            if violation_count else "no ratio above four from any n=6 source"
        ),
        "scope": "all n=5 MBCs; all four Peleg cases; complete n=6 MBC family; Peleg case-2 and singleton-splitting case-3 extensions to n=7",
        "five_player_minimal_balanced_collections": len(five_player),
        "raw_n6_generated_by_case": {
            str(key):value for key,value in sorted(generated_by_case.items())
        },
        "rank_one_two_parent_unions": rank_one_unions,
        "raw_n6_generated_by_case_4": raw_fourth_generated,
        "distinct_six_player_sources": len(six_player),
        "expected_complete_six_player_count": 200214,
        "complete_six_player_count_matches": len(six_player) == 200214,
        "ratio_above_four_extensions": violation_count,
        "violations_by_peleg_case": {
            str(key):value for key,value in sorted(violations_by_case.items())
        },
        "violations_by_arm_size": {
            str(key):value for key,value in sorted(violations_by_arm_size.items())
        },
        "violations_by_ratio": dict(sorted(violations_by_ratio.items())),
        "stored_record_limit": 2000,
        "records_stored": len(records),
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(hunt(),indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered,end="")
