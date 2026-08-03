"""Exact certificates for Peleg case-1 root-absorption closure.

For a regularized root MBC C and a case-1 marking I, solve

    v(T) = 1[T in I]  (T in C).

When I contains both distinguished cosingletons, excludes B, and has
balancing weight one, these equations force v(N)=1 and v_a=v_b=v_u=0.
If v is nonnegative on the second-leaf support, the parent fixed-witness dual
remainder is at most the child's remainder by positive-part subadditivity.
This transports both absorber feasibility and the normalized 1/3 reserve.
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
from audit_unit_root_absorption_n7 import absorption_subcollection
from hunt_root_absorption_descendants_n7 import (
    A,
    A_PLAYER,
    B,
    B_PLAYER,
    COSINGLETON_A_SOURCE,
    COSINGLETON_B_SOURCE,
    SOURCE_N,
    WITNESS,
    N,
    NEW_PLAYER,
    decoded_root,
    regularized_sources,
)


def interpolation_potential(collection,subset,second_universe):
    A_eq = []
    b_eq = []
    for index,(coalition,_weight) in enumerate(collection):
        A_eq.append([
            int(coalition >> player & 1) for player in range(SOURCE_N)
        ])
        b_eq.append(int(index in subset))
    A_ub = [[
        -int(coalition >> player & 1) for player in range(SOURCE_N)
    ] for coalition in second_universe]
    result = linprog(
        np.zeros(SOURCE_N),
        A_ub=np.asarray(A_ub),
        b_ub=np.zeros(len(A_ub)),
        A_eq=np.asarray(A_eq),
        b_eq=np.asarray(b_eq),
        bounds=[(None,None)]*SOURCE_N,
        method="highs",
    )
    if not result.success:
        return None
    potential = tuple(rat(value) for value in result.x)
    exact = (
        all(sum((potential[player] for player in range(SOURCE_N)
                 if coalition >> player & 1),F(0)) == int(index in subset)
            for index,(coalition,_weight) in enumerate(collection))
        and all(sum((potential[player] for player in range(SOURCE_N)
                     if coalition >> player & 1),F(0)) >= 0
                for coalition in second_universe)
    )
    assert exact
    return potential


def audit():
    roots,lifted_seconds = regularized_sources()
    second_universe = tuple(sorted({
        coalition
        for second,_m_B in lifted_seconds
        for coalition in second
        if coalition < (1 << SOURCE_N)
    }))
    records = []
    adversarial_roots = 0
    raw_case1_markings = 0
    root_only_parent_markings = 0
    root_only_child_failures = 0
    for root_index,collection in enumerate(roots,1):
        weights = dict(collection)
        m_A = weights.pop(COSINGLETON_A_SOURCE)
        m_B = weights.pop(COSINGLETON_B_SOURCE)
        root_core = dict(weights)
        root_only = absorption_subcollection(
            root_core,{},m_A,require=False,players=SOURCE_N,
            A_player=A_PLAYER,B=B,witness=WITNESS
        )
        if root_only is None:
            adversarial_roots += 1
            assert A not in root_core
        comp_a_index = next(
            index for index,(coalition,_weight) in enumerate(collection)
            if coalition == COSINGLETON_A_SOURCE
        )
        comp_b_index = next(
            index for index,(coalition,_weight) in enumerate(collection)
            if coalition == COSINGLETON_B_SOURCE
        )
        B_index = next(
            index for index,(coalition,_weight) in enumerate(collection)
            if coalition == B
        )
        for size in range(2,len(collection)+1):
            for subset_tuple in itertools.combinations(range(len(collection)),size):
                subset = set(subset_tuple)
                if (comp_a_index not in subset or comp_b_index not in subset
                        or B_index in subset):
                    continue
                subset_weight = sum(
                    (collection[index][1] for index in subset),F(0)
                )
                if subset_weight != 1:
                    continue
                if root_only is not None:
                    root_only_parent_markings += 1
                    descendant = tuple(
                        (coalition | NEW_PLAYER if index in subset else coalition,
                         weight)
                        for index,(coalition,weight) in enumerate(collection)
                    )
                    decoded = decoded_root(descendant)
                    assert decoded is not None
                    child_items,child_m_A,_child_m_B = decoded
                    child_absorber = absorption_subcollection(
                        dict(child_items),{},child_m_A,require=False,
                        players=N,A_player=A_PLAYER,B=B,witness=WITNESS
                    )
                    if child_absorber is None:
                        root_only_child_failures += 1
                    continue
                raw_case1_markings += 1
                potential = interpolation_potential(
                    collection,subset,second_universe
                )
                records.append({
                    "root_index": root_index,
                    "regularized_collection": [
                        [coalition,str(weight)]
                        for coalition,weight in collection
                    ],
                    "subset_indices_1based": [index+1 for index in subset_tuple],
                    "potential": [str(value) for value in potential]
                        if potential is not None else None,
                    "minimum_second_support_value": (
                        str(min(sum((potential[player]
                                     for player in range(SOURCE_N)
                                     if coalition >> player & 1),F(0))
                                for coalition in second_universe))
                        if potential is not None else None
                    ),
                })

    successful = [record for record in records if record['potential'] is not None]
    potential_types = Counter(
        tuple(record['potential']) for record in successful
    )
    forced_identities = all(
        sum(map(F,record['potential']),F(0)) == 1
        and F(record['potential'][A_PLAYER]) == 0
        and F(record['potential'][B_PLAYER]) == 0
        and F(record['potential'][WITNESS.bit_length()-1]) == 0
        for record in successful
    )
    return {
        "status": (
            "case-1 closure sign condition certified"
            if len(successful) == len(records)
            else "case-1 closure sign failure found"
        ),
        "source_root_count": len(roots),
        "root_only_nonabsorbing_source_count": adversarial_roots,
        "root_only_parent_case1_marking_count": root_only_parent_markings,
        "root_only_child_failure_count": root_only_child_failures,
        "second_support_universe": list(second_universe),
        "case1_adversarial_marking_count": raw_case1_markings,
        "nonnegative_interpolation_certificate_count": len(successful),
        "sign_failure_count": len(records)-len(successful),
        "forced_potential_identities_hold": forced_identities,
        "minimum_second_support_value": str(min(
            F(record['minimum_second_support_value']) for record in successful
        )) if successful else None,
        "potential_type_histogram": [
            {"potential":list(potential),"count":count}
            for potential,count in sorted(potential_types.items())
        ],
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(),indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered,end="")
