"""Search Peleg descendants of every certified root for absorber failure.

Root relations become minimal balanced collections after adding the two
cosingletons N\{a} and N\{b}.  This script applies all four Peleg cases to all 56
regularized six-player roots, filters the seven-player descendants that still
encode the same two-defect root geometry, and tests them against all three
privately lifted second leaves.  The first leaf never enters the search.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import audit_ratio5_bad_leaf_gluing_n7 as gluing
from audit_unit_root_absorption_n7 import absorption_subcollection,solve
from hunt_full_n5_peleg_escape import (
    peleg_descendants,
    peleg_fourth_descendants,
    valid_mbc,
)
from hunt_glued_local_circuits import coefficient
from hunt_peleg_coefficient_ceiling_escape import exact_incidence_rank


SOURCE_N = 6
N = 7
A = 0b0000111
B = 0b0011000
A_PLAYER = 0
B_PLAYER = 3
WITNESS = 1 << 4
NEW_PLAYER = 1 << SOURCE_N
FULL_SOURCE = (1 << SOURCE_N) - 1
FULL = (1 << N) - 1
COSINGLETON_A_SOURCE = FULL_SOURCE ^ (1 << A_PLAYER)
COSINGLETON_B_SOURCE = FULL_SOURCE ^ (1 << B_PLAYER)
COSINGLETON_A = FULL ^ (1 << A_PLAYER)
COSINGLETON_B = FULL ^ (1 << B_PLAYER)


def add_weight(collection, coalition, weight):
    collection[coalition] = collection.get(coalition,F(0)) + weight


def regularized_sources():
    rowmeta, mono_A, mono_B, roots, seconds = gluing.local_families()
    root_mbcs = []
    for root in roots:
        core = gluing.local_data(root,rowmeta,0)
        m_A = coefficient(root,mono_A)
        m_B = coefficient(root,mono_B)
        collection = dict(core)
        add_weight(collection,COSINGLETON_A_SOURCE,m_A)
        add_weight(collection,COSINGLETON_B_SOURCE,m_B)
        level = next(iter(set(gluing.degree(collection,SOURCE_N))))
        normalized = tuple(sorted(
            (coalition,weight/level) for coalition,weight in collection.items()
        ))
        assert valid_mbc(normalized,SOURCE_N)
        root_mbcs.append(normalized)
    assert len(set(root_mbcs)) == 56

    lifted_seconds = []
    for second in seconds:
        core = gluing.local_data(second,rowmeta,2)
        m_B = coefficient(second,mono_B)
        levels = tuple(
            value + m_B*int(player == B_PLAYER)
            for player,value in enumerate(gluing.degree(core,SOURCE_N))
        )
        assert len(set(levels)) == 1
        alpha = levels[0]
        lifted = dict(core)
        lifted[NEW_PLAYER] = alpha
        assert gluing.degree(lifted,N) == tuple(
            alpha-m_B*int(player == B_PLAYER) for player in range(N)
        )
        assert lifted[B] == 2*m_B
        lifted_seconds.append((lifted,m_B))
    assert len(lifted_seconds) == 3
    return root_mbcs,lifted_seconds


def decoded_root(collection):
    weights = dict(collection)
    if (COSINGLETON_A not in weights
            or COSINGLETON_B not in weights
            or B not in weights):
        return None
    m_A = weights.pop(COSINGLETON_A)
    m_B = weights.pop(COSINGLETON_B)
    if not weights or m_A <= 0 or m_B <= 0:
        return None
    degree = gluing.degree(weights,N)
    baseline = degree[1]
    if degree != tuple(
            baseline+m_A*int(player == A_PLAYER)
            +m_B*int(player == B_PLAYER)
            for player in range(N)):
        return None
    return tuple(sorted(weights.items())),m_A,m_B


def hunt():
    source_roots,seconds = regularized_sources()
    decoded = {}
    raw_by_case = Counter()
    for source_index,source in enumerate(source_roots,1):
        for case,descendant in peleg_descendants(source,SOURCE_N):
            candidate = decoded_root(descendant)
            if candidate is None:
                continue
            raw_by_case[case] += 1
            root_core,m_A,m_B = candidate
            signature = (root_core,m_A,m_B)
            decoded.setdefault(signature,{
                "source_root_index": source_index,
                "peleg_case": case,
                "regularized_collection": [
                    [coalition,str(weight)] for coalition,weight in descendant
                ],
            })

    case4_rank_one_unions = 0
    for first_index,second_index in itertools.combinations(
            range(len(source_roots)),2):
        first,second = source_roots[first_index],source_roots[second_index]
        union = tuple(sorted(
            {coalition for coalition,_weight in first}
            | {coalition for coalition,_weight in second}
        ))
        if len(union) > N:
            continue
        dummy = tuple((coalition,F(1)) for coalition in union)
        if exact_incidence_rank(dummy,SOURCE_N) != len(union)-1:
            continue
        case4_rank_one_unions += 1
        for descendant in peleg_fourth_descendants(first,second,SOURCE_N):
            if not valid_mbc(descendant,N):
                continue
            candidate = decoded_root(descendant)
            if candidate is None:
                continue
            raw_by_case[4] += 1
            root_core,m_A,m_B = candidate
            signature = (root_core,m_A,m_B)
            decoded.setdefault(signature,{
                "source_root_pair": [first_index+1,second_index+1],
                "peleg_case": 4,
                "regularized_collection": [
                    [coalition,str(weight)] for coalition,weight in descendant
                ],
            })

    root_only_failures = 0
    pair_failures = []
    pair_count = 0
    remainder_histogram = Counter()
    remainder_histogram_by_case = {}
    for root_index,((root_items,m_A,m_B),metadata) in enumerate(
            sorted(decoded.items()),1):
        root = dict(root_items)
        root_only = absorption_subcollection(
            root,{},m_A,require=False,players=N,A_player=A_PLAYER,
            B=B,witness=WITNESS
        )
        if root_only is None:
            root_only_failures += 1
        for second_index,(second,second_m_B) in enumerate(seconds,1):
            scale = m_B/second_m_B
            scaled_second = {
                coalition:scale*weight for coalition,weight in second.items()
            }
            pair_count += 1
            absorber = absorption_subcollection(
                root,scaled_second,m_A,require=False,players=N,
                A_player=A_PLAYER,B=B,witness=WITNESS
            )
            if absorber is None:
                pair_failures.append({
                    "root_index": root_index,
                    "second_leaf_index": second_index,
                    "m_A": str(m_A),
                    "m_B": str(m_B),
                    "root_core": [[S,str(weight)] for S,weight in root_items],
                    **metadata,
                })
                continue
            remainder = solve(
                root,scaled_second,m_A,m_B,players=N,A=A,B=B,
                A_player=A_PLAYER,witness=WITNESS
            )
            assert remainder['primal_exact'] and remainder['dual_exact']
            remainder_value = F(remainder['minimum'])
            remainder_histogram[remainder_value] += 1
            remainder_histogram_by_case.setdefault(
                metadata['peleg_case'],Counter()
            )[remainder_value] += 1

    return {
        "status": (
            "absorber failure found" if pair_failures
            else "no absorber failure in all-four-case certified-root descendants"
        ),
        "scope": (
            "all four Peleg cases from the 56 regularized n=6 "
            "roots that retain both distinguished cosingletons and root B"
        ),
        "source_root_mbc_count": len(source_roots),
        "raw_decoded_descendants_by_case": {
            str(case):count for case,count in sorted(raw_by_case.items())
        },
        "case4_rank_one_parent_unions": case4_rank_one_unions,
        "distinct_decoded_seven_player_roots": len(decoded),
        "root_only_absorber_failures": root_only_failures,
        "second_leaf_count": len(seconds),
        "root_second_pairs_tested": pair_count,
        "absorber_failure_count": len(pair_failures),
        "minimum_normalized_dual_remainder": (
            str(min(remainder_histogram)) if remainder_histogram else None
        ),
        "remainder_histogram": {
            str(value):count
            for value,count in sorted(remainder_histogram.items())
        },
        "remainder_histogram_by_peleg_case": {
            str(case):{
                str(value):count for value,count in sorted(histogram.items())
            }
            for case,histogram in sorted(remainder_histogram_by_case.items())
        },
        "failure_records": pair_failures[:100],
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
