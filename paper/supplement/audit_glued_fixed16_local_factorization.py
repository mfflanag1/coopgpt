"""Exact local-factorization proof of the glued fixed-{5} 9/8 bound.

The global arrangement audit evaluates 87 dual rays on 59,304 distinct
product-forbidden gluings.  This script proves the stronger local statement.
For each dual ray, its 9/8 cross-multiplied objective factors into

    root_score + m_A * first_leaf_rate + m_B * second_leaf_rate,

where m_A and m_B are the two monotonicity weights in the root circuit.
Minimizing the two leaf rates independently and then checking the 56 root
circuits proves the inequality for every one of the 56*626*3 raw local
gluings, not only the product-forbidden subfamily.

All ranks and local primitive kernels are inherited from the exact local
enumerator.  All scores below are Fractions.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from audit_glued_fixed16_arrangement import (
    B,
    N,
    expand_ray,
    ray_hinge,
    symmetry_representative,
)
from hunt_glued_local_circuits import (
    A,
    A_PLAYER,
    B_PLAYER,
    coefficient,
    enumerate_local,
)
from search_both_sensitive_circuits import eliminated_matrix


def local_data():
    matrix, _inequalities, _equalities, rowmeta = eliminated_matrix(N, A, B)
    mono_A = rowmeta.index(("mono", 0, 1, A_PLAYER, A))
    mono_B = rowmeta.index(("mono", 0, 2, B_PLAYER, B))
    root_B = rowmeta.index(("core", 0, B))
    leaf_A = rowmeta.index(("core", 1, A))
    crossed_A = rowmeta.index(("core", 2, A))
    leaf_B = rowmeta.index(("core", 2, B))

    roots = enumerate_local(matrix, rowmeta, 0, (mono_A, mono_B, root_B))
    first_leaves = enumerate_local(matrix, rowmeta, 1, (mono_A, leaf_A))
    second_leaves = enumerate_local(
        matrix, rowmeta, 2, (mono_B, crossed_A, leaf_B)
    )
    second_leaves = tuple(
        circuit for circuit in second_leaves
        if coefficient(circuit, crossed_A) < coefficient(circuit, leaf_B)
    )
    return {
        "rowmeta": rowmeta,
        "mono_A": mono_A,
        "mono_B": mono_B,
        "leaf_A": leaf_A,
        "leaf_B": leaf_B,
        "roots": tuple(roots),
        "first_leaves": tuple(first_leaves),
        "second_leaves": second_leaves,
    }


def coalition_score(circuit, ray, rowmeta):
    """The additive dual numerator contributed by one game block."""
    score = F(0)
    for index, weight in zip(*circuit):
        meta = rowmeta[index]
        if meta[0] != "core":
            continue
        coalition = meta[2]
        score += F(weight) * (
            max(F(ray_hinge(ray, coalition)), 0)
            + F(ray[1]) * int(coalition == B)
        )
    return score


def circuit_coalition_universe(circuits, rowmeta):
    return {
        meta[2]
        for circuit in circuits
        for index in circuit[0]
        if (meta := rowmeta[index])[0] == "core"
    }


def render_local_circuit(circuit, game, data):
    """Emit enough exact data for a dependency-free verifier."""
    rowmeta = data["rowmeta"]
    core = [
        [rowmeta[index][2], str(weight)]
        for index, weight in zip(*circuit)
        if rowmeta[index][0] == "core"
    ]
    mono_A = coefficient(circuit, data["mono_A"])
    mono_B = coefficient(circuit, data["mono_B"])
    degrees = [
        sum(
            F(weight) for coalition, weight in core
            if coalition >> player & 1
        )
        for player in range(N)
    ]
    if game == 0:
        levels = [
            degrees[player]
            - mono_A * int(player == A_PLAYER)
            - mono_B * int(player == B_PLAYER)
            for player in range(N)
        ]
    elif game == 1:
        levels = [
            degrees[player] + mono_A * int(player == A_PLAYER)
            for player in range(N)
        ]
    else:
        levels = [
            degrees[player] + mono_B * int(player == B_PLAYER)
            for player in range(N)
        ]
    assert len(set(levels)) == 1
    return {
        "core": core,
        "mono_A": str(mono_A),
        "mono_B": str(mono_B),
        "efficiency_level": str(levels[0]),
    }


def audit(arrangement_path):
    arrangement = json.loads(Path(arrangement_path).read_text())
    data = local_data()
    rowmeta = data["rowmeta"]
    roots = data["roots"]
    first_leaves = data["first_leaves"]
    second_leaves = data["second_leaves"]
    mono_A = data["mono_A"]
    mono_B = data["mono_B"]
    leaf_A = data["leaf_A"]
    leaf_B = data["leaf_B"]

    local_universe = circuit_coalition_universe(
        roots + first_leaves + second_leaves, rowmeta
    )
    arrangement_universe = set(
        arrangement["geometry"].get("coalition_universe", [])
    )
    if not arrangement_universe:
        arrangement_universe = {
            source
            for hyperplane in arrangement["hyperplanes"]
            for source in hyperplane["sources"]
            if isinstance(source, int)
        }
        arrangement_universe.update(arrangement["zero_hyperplane_masks"])
    assert local_universe == arrangement_universe

    rays = tuple(tuple(ray) for ray in arrangement["expanded_rays"])
    assert tuple(expand_ray(tuple(ray)) for ray in arrangement["reduced_rays"]) == rays

    ray_certificates = []
    local_comparisons = 0
    second_leaf_rates_identical = True
    minimum_rate_margin_triples = set()
    for ray in rays:
        first_rates = []
        for circuit in first_leaves:
            rate = (
                8 * coalition_score(circuit, ray, rowmeta)
                - 9 * F(ray[0]) * coefficient(circuit, leaf_A)
            ) / coefficient(circuit, mono_A)
            first_rates.append(rate)

        second_rates = []
        for circuit in second_leaves:
            rate = (
                8 * coalition_score(circuit, ray, rowmeta)
                - 9 * F(ray[1]) * coefficient(circuit, leaf_B)
            ) / coefficient(circuit, mono_B)
            second_rates.append(rate)

        first_minimum = min(first_rates)
        second_minimum = min(second_rates)
        second_leaf_rates_identical &= len(set(second_rates)) == 1
        root_margins = [
            8 * coalition_score(circuit, ray, rowmeta)
            + coefficient(circuit, mono_A) * first_minimum
            + coefficient(circuit, mono_B) * second_minimum
            for circuit in roots
        ]
        root_minimum = min(root_margins)
        minimum_rate_margin_triples.add(
            (first_minimum, second_minimum, root_minimum)
        )
        local_comparisons += (
            len(first_rates) + len(second_rates) + len(root_margins)
        )
        ray_certificates.append({
            "ray": list(ray),
            "first_leaf_minimum_rate": str(first_minimum),
            "first_leaf_minimizers": [
                index + 1 for index, value in enumerate(first_rates)
                if value == first_minimum
            ],
            "second_leaf_minimum_rate": str(second_minimum),
            "second_leaf_minimizers": [
                index + 1 for index, value in enumerate(second_rates)
                if value == second_minimum
            ],
            "root_minimum_margin": str(root_minimum),
            "root_minimizers": [
                index + 1 for index, value in enumerate(root_margins)
                if value == root_minimum
            ],
        })

    zero_rays = {
        tuple(item["ray"])
        for item in ray_certificates
        if F(item["root_minimum_margin"]) == 0
    }
    negative = [
        item for item in ray_certificates
        if F(item["root_minimum_margin"]) < 0
    ]
    arrangement_sharp = {
        tuple(item["ray"])
        for item in arrangement["capacity_evaluation"]["ray_minima"]
        if item["minimum_value"] == "9/8"
    }
    assert not negative
    assert zero_rays == arrangement_sharp

    raw_gluing_count = len(roots) * len(first_leaves) * len(second_leaves)
    return {
        "status": "exact local-factorization proof of fixed-{5} 9/8 bound",
        "geometry": dict(arrangement["geometry"]),
        "scope": (
            "all raw gluings of the enumerated root and leaf local circuits, "
            "including but not limited to the product-forbidden subfamily"
        ),
        "local_circuit_counts": {
            "root": len(roots),
            "first_leaf": len(first_leaves),
            "second_leaf": len(second_leaves),
        },
        "raw_local_gluing_triples_covered": raw_gluing_count,
        "coalition_universe_size": len(local_universe),
        "coalition_universe_matches_arrangement": True,
        "arrangement_ray_count": len(rays),
        "exact_local_comparisons": local_comparisons,
        "negative_root_margin_rays": 0,
        "zero_root_margin_rays": len(zero_rays),
        "zero_root_margin_symmetry_orbits": len({
            symmetry_representative(ray) for ray in zero_rays
        }),
        "zero_rays_equal_global_sharp_rays": True,
        "second_leaf_rates_identical_on_every_ray": (
            second_leaf_rates_identical
        ),
        "distinct_minimum_rate_margin_triples": len(
            minimum_rate_margin_triples
        ),
        "proof_identity": {
            "first_leaf_rate": (
                "(8 H(q^1)-9 r_A q^1_A)/m_A"
            ),
            "second_leaf_rate": (
                "(8 H(q^2)-9 r_B q^2_B)/m_B"
            ),
            "global_margin": (
                "8 H(q^0)+m_A first_leaf_rate+"
                "m_B second_leaf_rate = 8 L-9 D"
            ),
        },
        "local_circuit_certificates": {
            "root": [
                render_local_circuit(circuit, 0, data) for circuit in roots
            ],
            "first_leaf": [
                render_local_circuit(circuit, 1, data)
                for circuit in first_leaves
            ],
            "second_leaf": [
                render_local_circuit(circuit, 2, data)
                for circuit in second_leaves
            ],
        },
        "ray_certificates": ray_certificates,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--arrangement",
        type=Path,
        default=Path("results/glued_fixed16_dual_arrangement_n6_321.json"),
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(args.arrangement), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
