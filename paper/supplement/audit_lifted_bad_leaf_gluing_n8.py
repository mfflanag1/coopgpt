"""Glue the sharp n=8 coefficient-ceiling counterexample to the n=6 frontier.

The first leaf is the Peleg-lifted minimal balanced collection with arm mass
four and matched singleton mass one.  Every one of the 56 certified roots
and three certified second leaves is relabelled into eight players and given
two private singleton columns, preserving its local nullity-one relation.
All 168 gluings are checked as exact global circuits and audited at the fixed
witness U={5} (zero-based player 4).
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction as F
from pathlib import Path

from analyze_two_color_box_capacity import analyze, circuit_data
from hunt_glued_local_circuits import coefficient, enumerate_local, rank_mod_prime
from search_both_sensitive_circuits import eliminated_matrix


SOURCE_N = 6
SOURCE_A = 0b000111
SOURCE_B = 0b011000
N = 8
A = 0b11000001  # {0,6,7}
B = 0b00011000  # {3,4}
A_PLAYER = 6
B_PLAYER = 3
WITNESS = 1 << 4

ROOT_MAP = {0: 6, 1: 0, 2: 7, 3: 3, 4: 4, 5: 1}
SECOND_MAP = {0: 0, 1: 6, 2: 7, 3: 3, 4: 4, 5: 1}
PRIVATE_PLAYERS = (2, 5)

# Primitive first-leaf relation.  Adding singleton {6} with weight one makes
# the displayed core collection regular of degree five.
BAD_FIRST_CORE = {
    A: F(4),
    0b10000111: F(1),  # {0,1,2,7}
    0b00001010: F(1),  # {1,3}
    0b00011100: F(2),  # {2,3,4}
    0b00101100: F(2),  # {2,3,5}
    0b00110010: F(3),  # {1,4,5}
}
BAD_FIRST_MONO = F(1)


def map_mask(mask, mapping):
    return sum(
        1 << mapping[player]
        for player in range(SOURCE_N)
        if mask >> player & 1
    )


def degree(collection, players):
    return tuple(
        sum(
            (weight for coalition, weight in collection.items()
             if coalition >> player & 1),
            F(0),
        )
        for player in range(players)
    )


def primitive(values):
    denominator = 1
    for value in values:
        denominator = math.lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in values]
    divisor = abs(math.gcd(*integers))
    return tuple(value // divisor for value in integers)


def local_data(circuit, rowmeta, game):
    return {
        rowmeta[index][2]: F(weight)
        for index, weight in zip(*circuit)
        if rowmeta[index][0] == "core" and rowmeta[index][1] == game
    }


def extend_core(core, mapping, alpha):
    extended = {map_mask(coalition, mapping): weight
                for coalition, weight in core.items()}
    for player in PRIVATE_PLAYERS:
        assert 1 << player not in extended
        extended[1 << player] = alpha
    return extended


def local_families():
    matrix, _ineq, _eq, rowmeta = eliminated_matrix(
        SOURCE_N, SOURCE_A, SOURCE_B
    )
    mono_A = rowmeta.index(("mono", 0, 1, 0, SOURCE_A))
    mono_B = rowmeta.index(("mono", 0, 2, 3, SOURCE_B))
    root_B = rowmeta.index(("core", 0, SOURCE_B))
    crossed_A = rowmeta.index(("core", 2, SOURCE_A))
    leaf_B = rowmeta.index(("core", 2, SOURCE_B))
    roots = enumerate_local(
        matrix, rowmeta, 0, (mono_A, mono_B, root_B), players=SOURCE_N
    )
    seconds = enumerate_local(
        matrix, rowmeta, 2, (mono_B, crossed_A, leaf_B), players=SOURCE_N
    )
    seconds = [
        circuit for circuit in seconds
        if coefficient(circuit, crossed_A) < coefficient(circuit, leaf_B)
    ]
    assert (len(roots), len(seconds)) == (56, 3)
    return rowmeta, mono_A, mono_B, roots, seconds


def lifted_root(circuit, rowmeta, mono_A, mono_B):
    m_A = coefficient(circuit, mono_A)
    m_B = coefficient(circuit, mono_B)
    core = local_data(circuit, rowmeta, 0)
    source_degree = degree(core, SOURCE_N)
    levels = tuple(
        source_degree[player]
        - m_A * int(player == 0)
        - m_B * int(player == 3)
        for player in range(SOURCE_N)
    )
    assert len(set(levels)) == 1
    alpha = levels[0]
    extended = extend_core(core, ROOT_MAP, alpha)
    target_degree = degree(extended, N)
    assert target_degree == tuple(
        alpha + m_A * int(player == A_PLAYER)
        + m_B * int(player == B_PLAYER)
        for player in range(N)
    )
    return extended, m_A, m_B, alpha


def lifted_second(circuit, rowmeta, mono_B):
    m_B = coefficient(circuit, mono_B)
    core = local_data(circuit, rowmeta, 2)
    source_degree = degree(core, SOURCE_N)
    levels = tuple(
        source_degree[player] + m_B * int(player == 3)
        for player in range(SOURCE_N)
    )
    assert len(set(levels)) == 1
    alpha = levels[0]
    extended = extend_core(core, SECOND_MAP, alpha)
    target_degree = degree(extended, N)
    assert target_degree == tuple(
        alpha - m_B * int(player == B_PLAYER)
        for player in range(N)
    )
    assert extended[A] < extended[B]
    return extended, m_B, alpha


def add_component(weights, rowmeta, game, collection, scale=F(1)):
    for coalition, weight in collection.items():
        index = rowmeta.index(("core", game, coalition))
        assert index not in weights
        weights[index] = scale * weight


def make_payload(rowmeta, weights):
    support = tuple(sorted(weights))
    integers = primitive([weights[index] for index in support])
    return {
        "n": N,
        "A_mask": A,
        "B_mask": B,
        "circuits": [{
            "active_rows": [list(rowmeta[index]) for index in support],
            "circuit_weights": list(integers),
        }],
    }, support, integers


def audit():
    source_meta, source_mono_A, source_mono_B, roots, seconds = local_families()
    matrix, _ineq, _eq, rowmeta = eliminated_matrix(N, A, B)
    mono_A = rowmeta.index(("mono", 0, 1, A_PLAYER, A))
    mono_B = rowmeta.index(("mono", 0, 2, B_PLAYER, B))

    first_degree = degree(BAD_FIRST_CORE, N)
    assert first_degree == tuple(
        F(5) - BAD_FIRST_MONO * int(player == A_PLAYER)
        for player in range(N)
    )

    records = []
    exact_circuits = 0
    for root_index, root in enumerate(roots, 1):
        root_core, root_m_A, root_m_B, root_alpha = lifted_root(
            root, source_meta, source_mono_A, source_mono_B
        )
        for second_index, second in enumerate(seconds, 1):
            second_core, second_m_B, second_alpha = lifted_second(
                second, source_meta, source_mono_B
            )
            weights = {mono_A: root_m_A, mono_B: root_m_B}
            add_component(weights, rowmeta, 0, root_core)
            add_component(
                weights, rowmeta, 1, BAD_FIRST_CORE,
                root_m_A / BAD_FIRST_MONO,
            )
            add_component(
                weights, rowmeta, 2, second_core,
                root_m_B / second_m_B,
            )
            payload, support, integers = make_payload(rowmeta, weights)
            block = matrix[:, support].astype(int)
            assert all(
                sum(int(block[row, column]) * integers[column]
                    for column in range(len(support))) == 0
                for row in range(block.shape[0])
            )
            modular_rank = rank_mod_prime(block)
            assert modular_rank == len(support) - 1
            exact_circuits += 1

            _n, _A, _B, aggregate, required_A, required_B = circuit_data(
                payload, 1
            )
            scalar_capacity = 1 / (
                required_A / aggregate[A] + required_B / aggregate[B]
            )
            fixed = analyze(payload, 1, WITNESS)
            assert fixed["primal_exact"] and fixed["dual_exact"]
            records.append({
                "root_index": root_index,
                "second_leaf_index": second_index,
                "support_size": len(support),
                "modular_rank": modular_rank,
                "root_m_A": str(root_m_A),
                "root_m_B": str(root_m_B),
                "root_alpha": str(root_alpha),
                "second_alpha": str(second_alpha),
                "required_A": str(required_A),
                "required_B": str(required_B),
                "aggregate_A": str(aggregate[A]),
                "aggregate_B": str(aggregate[B]),
                "scalar_capacity": str(scalar_capacity),
                "fixed_witness_capacity": fixed["capacity"],
                "fixed_witness_certificate": fixed,
                "active_rows": payload["circuits"][0]["active_rows"],
                "circuit_weights": payload["circuits"][0]["circuit_weights"],
            })

    records.sort(key=lambda item: (
        F(item["fixed_witness_capacity"]),
        F(item["scalar_capacity"]),
        item["root_index"],
        item["second_leaf_index"],
    ))
    capacities = [F(record["fixed_witness_capacity"]) for record in records]
    return {
        "status": "exact lifted bad-leaf gluing audit",
        "players": N,
        "A_mask": A,
        "B_mask": B,
        "fixed_witness_mask": WITNESS,
        "bad_first_leaf_arm_to_mono_ratio": "4",
        "root_count": len(roots),
        "second_leaf_count": len(seconds),
        "gluing_count": len(records),
        "exact_global_circuit_count": exact_circuits,
        "minimum_fixed_witness_capacity": str(min(capacities)),
        "below_nine_eighths": sum(value < F(9, 8) for value in capacities),
        "below_one": sum(value < 1 for value in capacities),
        "at_one": sum(value == 1 for value in capacities),
        "best_record": records[0],
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
