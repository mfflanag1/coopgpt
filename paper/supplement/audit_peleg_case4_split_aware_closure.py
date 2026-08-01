"""Close certified Peleg case 4 with split-aware parent coordinates.

Case 4 mixes two normalized parent MBCs along a rank-one balancing segment
and attaches the new player to a subset I of mixed weight one.  A source-side
absorber lifts if its root and second allocations are kept separate and

    marked root mass + private-new-singleton mass = baseline degree.

This script enumerates every decoded case-4 emission from the 56 certified
roots and stores an exact rational lift certificate for each of its three
second-leaf pairings.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

from audit_peleg_case3_split_transport import split_aware_absorber
from audit_unit_root_absorption_n7 import absorption_subcollection
from hunt_full_n5_peleg_escape import valid_mbc
from hunt_peleg_coefficient_ceiling_escape import exact_incidence_rank
from hunt_root_absorption_descendants_n7 import (
    A_PLAYER,
    B,
    COSINGLETON_A_SOURCE,
    COSINGLETON_B_SOURCE,
    NEW_PLAYER,
    N,
    SOURCE_N,
    WITNESS,
    decoded_root,
    regularized_sources,
)


def add_weight(target, coalition, weight):
    target[coalition] += weight


def case4_emissions(roots):
    for first_index, second_index in itertools.combinations(range(len(roots)), 2):
        first, second = roots[first_index], roots[second_index]
        union = tuple(sorted(
            {coalition for coalition, _weight in first}
            | {coalition for coalition, _weight in second}
        ))
        if len(union) > N:
            continue
        dummy = tuple((coalition, F(1)) for coalition in union)
        if exact_incidence_rank(dummy, SOURCE_N) != len(union)-1:
            continue
        first_weights, second_weights = dict(first), dict(second)
        mu = tuple(first_weights.get(coalition, F(0)) for coalition in union)
        nu = tuple(second_weights.get(coalition, F(0)) for coalition in union)
        for subset_size in range(len(union)+1):
            for subset_tuple in itertools.combinations(range(len(union)), subset_size):
                mu_I = sum((mu[index] for index in subset_tuple), F(0))
                nu_I = sum((nu[index] for index in subset_tuple), F(0))
                if mu_I == nu_I:
                    continue
                mixing = (1-mu_I)/(nu_I-mu_I)
                if not 0 < mixing < 1:
                    continue
                subset = set(subset_tuple)
                weights = tuple(
                    (1-mixing)*left+mixing*right
                    for left, right in zip(mu, nu)
                )
                assert all(weight > 0 for weight in weights)
                mixed = tuple(zip(union, weights))
                descendant = tuple(sorted(
                    (coalition | NEW_PLAYER if index in subset else coalition,
                     weight)
                    for index, (coalition, weight) in enumerate(mixed)
                ))
                if not valid_mbc(descendant, N):
                    continue
                decoded = decoded_root(descendant)
                if decoded is None:
                    continue
                yield {
                    "first_parent_index": first_index+1,
                    "second_parent_index": second_index+1,
                    "union": union,
                    "mixed": mixed,
                    "subset": subset,
                    "subset_tuple": subset_tuple,
                    "mu_I": mu_I,
                    "nu_I": nu_I,
                    "mixing": mixing,
                    "descendant": descendant,
                    "decoded": decoded,
                }


def rank_one_parent_union_count(roots):
    count = 0
    for first, second in itertools.combinations(roots, 2):
        union = tuple(sorted(
            {coalition for coalition, _weight in first}
            | {coalition for coalition, _weight in second}
        ))
        if len(union) > N:
            continue
        dummy = tuple((coalition, F(1)) for coalition in union)
        count += exact_incidence_rank(dummy, SOURCE_N) == len(union)-1
    return count


def mapped_absorber(certificate, marked_root):
    mapped = defaultdict(F)
    for coalition, value in certificate["root_subcollection"].items():
        coalition = int(coalition)
        add_weight(
            mapped,
            coalition | NEW_PLAYER if coalition in marked_root else coalition,
            F(value),
        )
    for coalition, value in certificate["second_subcollection"].items():
        add_weight(mapped, int(coalition), F(value))
    add_weight(mapped, NEW_PLAYER, F(certificate["new_singleton_mass"]))
    return dict(mapped)


def verify_mapped(
        certificate, marked_root, child_root, child_second, m_A):
    z = mapped_absorber(certificate, marked_root)
    aggregate = defaultdict(F, child_root)
    for coalition, weight in child_second.items():
        aggregate[coalition] += weight
    beta = F(certificate["beta"])
    delta = F(certificate["delta"])
    return (
        all(F(0) <= value <= aggregate[coalition]
            for coalition, value in z.items())
        and all(
            sum((value for coalition, value in z.items()
                 if coalition >> player & 1), F(0))
            == beta+m_A*int(player == A_PLAYER)
               +delta*int(WITNESS >> player & 1)
            for player in range(N)
        )
        and z.get(B, F(0)) <= child_root.get(B, F(0))
    )


def audit():
    roots, lifted_seconds = regularized_sources()
    records = []
    raw_emissions = 0
    root_only_emissions = 0
    pair_failures = 0
    mapped_failures = 0
    mixing_histogram = Counter()
    parent_pairs = Counter()
    distinct_descendants = set()
    rank_one_count = rank_one_parent_union_count(roots)

    for emission in case4_emissions(roots):
        raw_emissions += 1
        first_parent = emission["first_parent_index"]
        second_parent = emission["second_parent_index"]
        parent_pairs[(first_parent, second_parent)] += 1
        mixing_histogram[emission["mixing"]] += 1
        child_items, m_A, m_B = emission["decoded"]
        child_root = dict(child_items)
        child_signature = (child_items, m_A, m_B)
        distinct_descendants.add(child_signature)
        root_only = absorption_subcollection(
            child_root, {}, m_A, require=False, players=N,
            A_player=A_PLAYER, B=B, witness=WITNESS,
        )
        root_only_emissions += root_only is not None

        mixed_root = dict(emission["mixed"])
        assert mixed_root.pop(COSINGLETON_A_SOURCE) == m_A
        assert mixed_root.pop(COSINGLETON_B_SOURCE) == m_B
        marked_root = {
            coalition
            for index, (coalition, _weight) in enumerate(emission["mixed"])
            if index in emission["subset"]
            and coalition not in (
                COSINGLETON_A_SOURCE, COSINGLETON_B_SOURCE
            )
        }
        assert COSINGLETON_A_SOURCE in {
            emission["union"][index] for index in emission["subset"]
        }
        assert COSINGLETON_B_SOURCE in {
            emission["union"][index] for index in emission["subset"]
        }
        assert B not in {
            emission["union"][index] for index in emission["subset"]
        }

        pair_certificates = []
        for second_index, (lifted_second, second_m_B) in enumerate(
                lifted_seconds, 1):
            scale = m_B/second_m_B
            source_second = dict(lifted_second)
            singleton_capacity = scale*source_second.pop(NEW_PLAYER)
            source_second = {
                coalition: scale*weight
                for coalition, weight in source_second.items()
            }
            child_second = {
                coalition: scale*weight
                for coalition, weight in lifted_second.items()
            }
            certificate = split_aware_absorber(
                mixed_root, source_second, marked_root,
                singleton_capacity, m_A,
            )
            if certificate is None:
                pair_failures += 1
                pair_certificates.append({
                    "second_index": second_index,
                    "absorber_exists": False,
                })
                continue
            mapped_exact = verify_mapped(
                certificate, marked_root, child_root, child_second, m_A
            )
            mapped_failures += not mapped_exact
            pair_certificates.append({
                "second_index": second_index,
                "absorber_exists": True,
                "mapped_exact": mapped_exact,
                "singleton_capacity": str(singleton_capacity),
                "source_second_core": [
                    [coalition, str(weight)]
                    for coalition, weight in sorted(source_second.items())
                ],
                "certificate": certificate,
            })

        records.append({
            "first_parent_index": first_parent,
            "second_parent_index": second_parent,
            "union": list(emission["union"]),
            "mixed_collection": [
                [coalition, str(weight)]
                for coalition, weight in emission["mixed"]
            ],
            "subset_indices_1based": [
                index+1 for index in emission["subset_tuple"]
            ],
            "marked_root_coalitions": sorted(marked_root),
            "mu_I": str(emission["mu_I"]),
            "nu_I": str(emission["nu_I"]),
            "mixing": str(emission["mixing"]),
            "m_A": str(m_A),
            "m_B": str(m_B),
            "mixed_root_core": [
                [coalition, str(weight)]
                for coalition, weight in sorted(mixed_root.items())
            ],
            "child_root_core": [
                [coalition, str(weight)]
                for coalition, weight in child_items
            ],
            "child_root_only_absorber": root_only,
            "pair_certificates": pair_certificates,
        })

    assert raw_emissions == 228
    return {
        "status": "Peleg case 4 closed on the certified root family",
        "case4_closed_for_certified_family": (
            raw_emissions == 228 and pair_failures == 0
            and mapped_failures == 0
        ),
        "source_root_count": len(roots),
        "rank_one_parent_union_count": rank_one_count,
        "raw_decoded_emissions": raw_emissions,
        "distinct_decoded_descendants": len(distinct_descendants),
        "parent_pair_count": len(parent_pairs),
        "root_only_emissions": root_only_emissions,
        "root_second_pair_count": raw_emissions*len(lifted_seconds),
        "split_aware_absorber_failures": pair_failures,
        "mapped_child_verification_failures": mapped_failures,
        "mixing_histogram": {
            str(value): count for value, count in sorted(mixing_histogram.items())
        },
        "parent_pair_emission_histogram": {
            f"{first},{second}": count
            for (first, second), count in sorted(parent_pairs.items())
        },
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(), indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
