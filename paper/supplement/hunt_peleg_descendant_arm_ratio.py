"""Search one Peleg generation beyond the sharp n=7 arm-ratio examples.

Every exact n=7 violation emitted by ``hunt_peleg_coefficient_ceiling_escape``
is used as a source minimal balanced collection.  Peleg cases 1--3 add an
eighth player.  Each distinct positive, balanced, incidence-independent
descendant is checked for every singleton/containing-arm coefficient ratio.
The primary target is a three-player arm ratio strictly above four, which
would break the lifted 9/8 gluing through roots 15, 19, and 27.
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


SOURCE_PLAYERS = 7
NEW_PLAYER = 1 << SOURCE_PLAYERS


def primitive(values):
    denominator = 1
    for value in values:
        denominator = math.lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in values]
    divisor = abs(math.gcd(*integers))
    return [value // divisor for value in integers]


def canonical(collection):
    return tuple(sorted(collection))


def validate(collection):
    masks = [coalition for coalition, _weight in collection]
    if len(set(masks)) != len(masks):
        return False
    if not all(weight > 0 for _coalition, weight in collection):
        return False
    if degree(collection, SOURCE_PLAYERS + 1) != (F(1),) * (SOURCE_PLAYERS + 1):
        return False
    return exact_incidence_rank(collection, SOURCE_PLAYERS + 1) == len(collection)


def descendants(collection):
    size = len(collection)
    for subset_size in range(size + 1):
        for subset_tuple in itertools.combinations(range(size), subset_size):
            subset = set(subset_tuple)
            subset_weight = sum(
                (collection[index][1] for index in subset), F(0)
            )
            if subset_weight == 1:
                yield 1, [
                    (coalition | NEW_PLAYER if index in subset else coalition, weight)
                    for index, (coalition, weight) in enumerate(collection)
                ], subset_tuple, None
            if subset_weight < 1:
                yield 2, [
                    (coalition | NEW_PLAYER if index in subset else coalition, weight)
                    for index, (coalition, weight) in enumerate(collection)
                ] + [(NEW_PLAYER, 1 - subset_weight)], subset_tuple, None
            if not subset_weight < 1:
                continue
            for delta, (delta_coalition, delta_weight) in enumerate(collection):
                if delta in subset or not subset_weight > 1 - delta_weight:
                    continue
                transformed = []
                for index, (coalition, weight) in enumerate(collection):
                    if index in subset:
                        transformed.append((coalition | NEW_PLAYER, weight))
                    elif index == delta:
                        transformed.append(
                            (coalition, weight + subset_weight - 1)
                        )
                    else:
                        transformed.append((coalition, weight))
                transformed.append((delta_coalition | NEW_PLAYER, 1 - subset_weight))
                yield 3, transformed, subset_tuple, delta


def ratio_records(collection):
    for singleton_index, (singleton, singleton_weight) in enumerate(collection):
        if singleton.bit_count() != 1:
            continue
        for arm_index, (arm, arm_weight) in enumerate(collection):
            if arm_index == singleton_index or not arm & singleton:
                continue
            yield {
                "singleton_mask": singleton,
                "singleton_weight": str(singleton_weight),
                "arm_mask": arm,
                "arm_size": arm.bit_count(),
                "arm_weight": str(arm_weight),
                "arm_to_singleton_ratio": str(arm_weight / singleton_weight),
            }


def next_generation_candidates(collection):
    """Candidates for a three-player arm ratio after adding player nine."""
    size = len(collection)
    ninth_player = 1 << (SOURCE_PLAYERS + 1)
    for subset_size in range(1, size + 1):
        for subset_tuple in itertools.combinations(range(size), subset_size):
            subset = set(subset_tuple)
            subset_weight = sum(
                (collection[index][1] for index in subset), F(0)
            )
            if subset_weight >= 1:
                continue
            new_singleton_weight = 1 - subset_weight
            for arm_index in subset:
                arm, arm_weight = collection[arm_index]
                if arm.bit_count() != 2:
                    continue
                yield {
                    "peleg_case": 2,
                    "subset": subset_tuple,
                    "delta": None,
                    "singleton_mask": ninth_player,
                    "singleton_weight": new_singleton_weight,
                    "arm_index": arm_index,
                    "arm_mask": arm | ninth_player,
                    "arm_weight": arm_weight,
                    "ratio": arm_weight / new_singleton_weight,
                }
            for delta, (singleton, singleton_weight) in enumerate(collection):
                if (delta in subset or singleton.bit_count() != 1
                        or not subset_weight > 1 - singleton_weight):
                    continue
                new_singleton_weight = singleton_weight + subset_weight - 1
                for arm_index, (arm, arm_weight) in enumerate(collection):
                    if arm_index == delta or not arm & singleton:
                        continue
                    new_arm_size = arm.bit_count() + int(arm_index in subset)
                    if new_arm_size != 3:
                        continue
                    yield {
                        "peleg_case": 3,
                        "subset": subset_tuple,
                        "delta": delta,
                        "singleton_mask": singleton,
                        "singleton_weight": new_singleton_weight,
                        "arm_index": arm_index,
                        "arm_mask": arm | ninth_player if arm_index in subset else arm,
                        "arm_weight": arm_weight,
                        "ratio": arm_weight / new_singleton_weight,
                    }


def materialize_next_generation(collection, candidate):
    ninth_player = 1 << (SOURCE_PLAYERS + 1)
    subset = set(candidate["subset"])
    if candidate["peleg_case"] == 2:
        return canonical([
            (coalition | ninth_player if index in subset else coalition, weight)
            for index, (coalition, weight) in enumerate(collection)
        ] + [(ninth_player, candidate["singleton_weight"])])
    delta = candidate["delta"]
    delta_coalition, delta_weight = collection[delta]
    transformed = []
    for index, (coalition, weight) in enumerate(collection):
        if index in subset:
            transformed.append((coalition | ninth_player, weight))
        elif index == delta:
            transformed.append(
                (coalition, candidate["singleton_weight"])
            )
        else:
            transformed.append((coalition, weight))
    transformed.append((
        delta_coalition | ninth_player,
        1 - sum((collection[index][1] for index in subset), F(0)),
    ))
    return canonical(transformed)


def hunt(source_payload):
    source_collections = {}
    for record in source_payload["records"]:
        if record["peleg_case"] != 2:
            continue
        collection = canonical(
            [(1 << (SOURCE_PLAYERS - 1), F(record["new_singleton_weight"]))]
            + [(coalition, F(weight)) for coalition, weight in record["new_core"]]
        )
        source_collections[collection] = True

    seen_descendants = set()
    valid_by_case = Counter()
    generated_by_case = Counter()
    maximum_by_arm_size = {}
    target_records = []
    next_generation_tests = 0
    next_generation_above_four = 0
    next_generation_best = None
    for source_index, collection in enumerate(sorted(source_collections), 1):
        assert degree(collection, SOURCE_PLAYERS) == (F(1),) * SOURCE_PLAYERS
        assert exact_incidence_rank(collection, SOURCE_PLAYERS) == len(collection)
        for case, descendant, subset, delta in descendants(collection):
            generated_by_case[case] += 1
            descendant = canonical(descendant)
            if descendant in seen_descendants:
                continue
            if not validate(descendant):
                continue
            seen_descendants.add(descendant)
            valid_by_case[case] += 1
            for candidate in next_generation_candidates(descendant):
                next_generation_tests += 1
                if (next_generation_best is None
                        or candidate["ratio"] > next_generation_best[1]["ratio"]):
                    next_generation_best = (descendant, candidate)
                if candidate["ratio"] > 4:
                    next_generation_above_four += 1
            for ratio_record in ratio_records(descendant):
                arm_size = ratio_record["arm_size"]
                ratio = F(ratio_record["arm_to_singleton_ratio"])
                current = maximum_by_arm_size.get(arm_size)
                if current is None or ratio > F(current["arm_to_singleton_ratio"]):
                    maximum_by_arm_size[arm_size] = {
                        "source_index": source_index,
                        "peleg_case": case,
                        "subset_indices_1based": [index + 1 for index in subset],
                        "delta_index_1based": delta + 1 if delta is not None else None,
                        **ratio_record,
                        "collection": [
                            [coalition, str(weight)] for coalition, weight in descendant
                        ],
                        "primitive_weights": primitive(
                            [weight for _coalition, weight in descendant]
                        ),
                    }
                if arm_size == 3 and ratio > 4:
                    target_records.append({
                        "source_index": source_index,
                        "peleg_case": case,
                        "subset_indices_1based": [index + 1 for index in subset],
                        "delta_index_1based": delta + 1 if delta is not None else None,
                        **ratio_record,
                        "collection": [
                            [coalition, str(weight)] for coalition, weight in descendant
                        ],
                        "primitive_weights": primitive(
                            [weight for _coalition, weight in descendant]
                        ),
                    })
    target_records.sort(key=lambda item: -F(item["arm_to_singleton_ratio"]))
    rendered_next_best = None
    if next_generation_best is not None:
        source, candidate = next_generation_best
        next_collection = materialize_next_generation(source, candidate)
        assert degree(next_collection, SOURCE_PLAYERS + 2) == (
            F(1),
        ) * (SOURCE_PLAYERS + 2)
        assert exact_incidence_rank(
            next_collection, SOURCE_PLAYERS + 2
        ) == len(next_collection)
        rendered_next_best = {
            "peleg_case": candidate["peleg_case"],
            "subset_indices_1based": [index + 1 for index in candidate["subset"]],
            "delta_index_1based": (
                candidate["delta"] + 1 if candidate["delta"] is not None else None
            ),
            "singleton_mask": candidate["singleton_mask"],
            "singleton_weight": str(candidate["singleton_weight"]),
            "arm_mask": candidate["arm_mask"],
            "arm_size": candidate["arm_mask"].bit_count(),
            "arm_weight": str(candidate["arm_weight"]),
            "arm_to_singleton_ratio": str(candidate["ratio"]),
            "collection": [
                [coalition, str(weight)] for coalition, weight in next_collection
            ],
            "primitive_weights": primitive(
                [weight for _coalition, weight in next_collection]
            ),
            "exact_incidence_rank": len(next_collection),
        }
    return {
        "status": (
            "three-player arm ratio above four found"
            if target_records else "no three-player arm ratio above four in one generation"
        ),
        "source_players": SOURCE_PLAYERS,
        "target_players": SOURCE_PLAYERS + 1,
        "distinct_source_collections": len(source_collections),
        "generated_by_peleg_case": {
            str(key): value for key, value in sorted(generated_by_case.items())
        },
        "distinct_valid_descendants": len(seen_descendants),
        "valid_descendants_by_first_generation_case": {
            str(key): value for key, value in sorted(valid_by_case.items())
        },
        "maximum_by_arm_size": {
            str(key): value for key, value in sorted(maximum_by_arm_size.items())
        },
        "target_violation_count": len(target_records),
        "target_records": target_records,
        "next_generation_target_players": SOURCE_PLAYERS + 2,
        "next_generation_three_arm_candidates_tested": next_generation_tests,
        "next_generation_three_arm_ratio_above_four": next_generation_above_four,
        "next_generation_best": rendered_next_best,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    payload = hunt(json.loads(args.input.read_text()))
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
