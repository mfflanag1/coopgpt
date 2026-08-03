"""Classify the potential defect in Peleg cases 2 and 3.

For every admissible marking of the 56 regularized roots, compute an exact
interpolation potential v(T)=1[T in I], maximize its minimum value on the
second-leaf support, and test whether root-only absorption survives the
case-2 singleton insertion or case-3 coalition split.
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
    A_PLAYER,
    B,
    COSINGLETON_A_SOURCE,
    COSINGLETON_B_SOURCE,
    N,
    NEW_PLAYER,
    SOURCE_N,
    WITNESS,
    decoded_root,
    regularized_sources,
)


def interpolation(collection,subset,second_universe):
    eta = SOURCE_N
    objective = np.zeros(SOURCE_N+1)
    objective[eta] = -1
    A_eq = []
    b_eq = []
    for index,(coalition,_weight) in enumerate(collection):
        row = np.zeros(SOURCE_N+1)
        for player in range(SOURCE_N):
            if coalition >> player & 1:
                row[player] = 1
        A_eq.append(row)
        b_eq.append(int(index in subset))
    A_ub = []
    for coalition in second_universe:
        row = np.zeros(SOURCE_N+1)
        row[eta] = 1
        for player in range(SOURCE_N):
            if coalition >> player & 1:
                row[player] = -1
        A_ub.append(row)
    result = linprog(
        objective,A_ub=np.asarray(A_ub),b_ub=np.zeros(len(A_ub)),
        A_eq=np.asarray(A_eq),b_eq=np.asarray(b_eq),
        bounds=[(None,None)]*(SOURCE_N+1),method="highs"
    )
    assert result.success,result.message
    solution = tuple(rat(value) for value in result.x)
    potential,minimum = solution[:SOURCE_N],solution[eta]
    assert all(
        sum((potential[player] for player in range(SOURCE_N)
             if coalition >> player & 1),F(0)) == int(index in subset)
        for index,(coalition,_weight) in enumerate(collection)
    )
    assert all(
        sum((potential[player] for player in range(SOURCE_N)
             if coalition >> player & 1),F(0)) >= minimum
        for coalition in second_universe
    )
    return potential,minimum


def child_root_only(descendant):
    decoded = decoded_root(descendant)
    assert decoded is not None
    child_items,m_A,_m_B = decoded
    return absorption_subcollection(
        dict(child_items),{},m_A,require=False,players=N,
        A_player=A_PLAYER,B=B,witness=WITNESS
    ) is not None


def audit():
    roots,lifted_seconds = regularized_sources()
    second_universe = tuple(sorted({
        coalition for second,_m_B in lifted_seconds for coalition in second
        if coalition < (1 << SOURCE_N)
    }))
    records = []
    emitted = Counter()
    root_only_parent = Counter()
    root_only_child_failures = Counter()
    identity_failures = 0
    case2_root_sign_failures = 0
    case2_second_sign_failures = 0
    for root_index,collection in enumerate(roots,1):
        weights = dict(collection)
        m_A = weights.pop(COSINGLETON_A_SOURCE)
        weights.pop(COSINGLETON_B_SOURCE)
        parent_root_only = absorption_subcollection(
            weights,{},m_A,require=False,players=SOURCE_N,
            A_player=A_PLAYER,B=B,witness=WITNESS
        ) is not None
        comp_a = next(i for i,(S,_w) in enumerate(collection)
                      if S == COSINGLETON_A_SOURCE)
        comp_b = next(i for i,(S,_w) in enumerate(collection)
                      if S == COSINGLETON_B_SOURCE)
        B_index = next(i for i,(S,_w) in enumerate(collection) if S == B)
        for size in range(2,len(collection)+1):
            for subset_tuple in itertools.combinations(range(len(collection)),size):
                subset = set(subset_tuple)
                if B_index in subset:
                    continue
                marked_weight = sum(
                    (collection[index][1] for index in subset),F(0)
                )
                if not marked_weight < 1:
                    continue
                kappa = 1-marked_weight
                potential,minimum = interpolation(
                    collection,subset,second_universe
                )
                if comp_a in subset and comp_b in subset:
                    forced = (
                        sum(potential,F(0)) == marked_weight
                        and potential[0] == potential[3] == -kappa
                        and potential[4] == kappa
                    )
                    identity_failures += not forced

                case2 = tuple(sorted([
                    (S | NEW_PLAYER if index in subset else S,weight)
                    for index,(S,weight) in enumerate(collection)
                ]+[(NEW_PLAYER,kappa)]))
                if (comp_a in subset and comp_b in subset
                        and decoded_root(case2) is not None):
                    emitted[2] += 1
                    correction = tuple(
                        int(player in (0,3))-int(player == 4)
                        for player in range(SOURCE_N)
                    )
                    corrected = tuple(
                        value+kappa*shift
                        for value,shift in zip(potential,correction)
                    )
                    case2_root_sign_failures += not all(
                        sum((correction[player] for player in range(SOURCE_N)
                             if S >> player & 1),0) >= 0
                        for S in weights
                    )
                    case2_second_sign_failures += not all(
                        sum((corrected[player] for player in range(SOURCE_N)
                             if S >> player & 1),F(0)) >= 0
                        for S in second_universe
                    )
                    if parent_root_only:
                        root_only_parent[2] += 1
                        root_only_child_failures[2] += not child_root_only(case2)
                    else:
                        records.append({
                            "case":2,"root_index":root_index,
                            "subset_indices_1based":[i+1 for i in subset_tuple],
                            "kappa":str(kappa),"minimum_second_value":str(minimum),
                            "potential":[str(value) for value in potential],
                        })

                for delta,(delta_coalition,delta_weight) in enumerate(collection):
                    if (delta in subset
                            or not marked_weight > 1-delta_weight):
                        continue
                    transformed = []
                    for index,(S,weight) in enumerate(collection):
                        if index in subset:
                            transformed.append((S | NEW_PLAYER,weight))
                        elif index == delta:
                            transformed.append((S,delta_weight-kappa))
                        else:
                            transformed.append((S,weight))
                    transformed.append((delta_coalition | NEW_PLAYER,kappa))
                    case3 = tuple(sorted(transformed))
                    if decoded_root(case3) is None:
                        continue
                    emitted[3] += 1
                    if parent_root_only:
                        root_only_parent[3] += 1
                        root_only_child_failures[3] += not child_root_only(case3)
                    else:
                        delta_role = (
                            "cosingleton_a" if delta == comp_a else
                            "cosingleton_b" if delta == comp_b else
                            "B" if delta == B_index else "core"
                        )
                        records.append({
                            "case":3,"root_index":root_index,
                            "subset_indices_1based":[i+1 for i in subset_tuple],
                            "delta_index_1based":delta+1,
                            "delta_role":delta_role,
                            "kappa":str(kappa),"delta_weight":str(delta_weight),
                            "minimum_second_value":str(minimum),
                            "potential":[str(value) for value in potential],
                        })

    adversarial = Counter(record['case'] for record in records)
    minima = {
        case:min(F(record['minimum_second_value'])
                 for record in records if record['case'] == case)
        for case in adversarial
    }
    types = {
        case:Counter((record['kappa'],tuple(record['potential']))
                     for record in records if record['case'] == case)
        for case in adversarial
    }
    return {
        "status":"exact case-2/3 interpolation-defect classification",
        "raw_decoded_emissions":{str(k):v for k,v in sorted(emitted.items())},
        "root_only_parent_emissions":{
            str(k):v for k,v in sorted(root_only_parent.items())
        },
        "root_only_child_failures":{
            str(k):v for k,v in sorted(root_only_child_failures.items())
        },
        "adversarial_parent_emissions":{
            str(k):v for k,v in sorted(adversarial.items())
        },
        "forced_identity_failures":identity_failures,
        "case2_root_correction_sign_failures":case2_root_sign_failures,
        "case2_second_corrected_sign_failures":case2_second_sign_failures,
        "minimum_second_support_value":{
            str(k):str(v) for k,v in sorted(minima.items())
        },
        "potential_type_count":{
            str(k):len(v) for k,v in sorted(types.items())
        },
        "potential_types":{
            str(case):[
                {"kappa":kappa,"potential":list(potential),"count":count}
                for (kappa,potential),count in sorted(counter.items())
            ] for case,counter in sorted(types.items())
        },
        "records":records,
    }


def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    return parser.parse_args()


if __name__=="__main__":
    args=parse_args()
    rendered=json.dumps(audit(),indent=2)+"\n"
    if args.output: args.output.write_text(rendered)
    else: print(rendered,end="")
