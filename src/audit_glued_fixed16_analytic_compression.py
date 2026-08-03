"""Analytic compression of the fixed-{5} local-factorization certificate.

The 59,595-comparison local proof can be reduced further.  The positive-part
inequality gives, for any local collection q,

    H(q) >= r_B q_B + [sum_T q_T gamma(T)
                       + r_A q_A - r_B q_B]_+.

For a first leaf, degree(q)=alpha*1-m_A*e_a, so the gamma sum is
-m_A*gamma_a.  After normalization, the resulting bound is nonincreasing in
u=q_A/m_A and nondecreasing in v=q_B/m_A.  The enumerated local cone has
0 <= u <= 3 and contains (u,v)=(3,0), hence its analytic minimum is

    8[-gamma_a+3 r_A]_+ - 27 r_A.

For roots the same bound depends only on twelve mass types.  It proves 86 of
87 arrangement rays.  The remaining sharp ray needs one exact incidence
correction, checked on the 56 roots.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


N = 6
A = 7
B = 24
U = 16
A_PLAYER = 0
B_PLAYER = 3
EXCEPTIONAL_RAY = (2, 1, 0, -1, -1, 1, 0, 1)


def core(record):
    return {int(coalition): F(weight) for coalition, weight in record["core"]}


def hinge_score(record, ray):
    r_A, r_B = map(F, ray[:2])
    gamma = tuple(map(F, ray[2:]))
    return sum((
        weight * (
            r_B * int(coalition == B)
            + max(
                sum((gamma[player] for player in range(N)
                     if coalition >> player & 1), F(0))
                + r_A * int(coalition == A)
                - r_B * int(coalition == B),
                F(0),
            )
        )
        for coalition, weight in core(record).items()
    ), F(0))


def first_mass_type(record):
    q = core(record)
    m_A = F(record["mono_A"])
    return q.get(A, F(0)) / m_A, q.get(B, F(0)) / m_A


def root_mass_type(record):
    q = core(record)
    return (
        F(record["mono_A"]),
        F(record["mono_B"]),
        q.get(A, F(0)),
        q.get(B, F(0)),
    )


def first_analytic_rate(ray):
    r_A = F(ray[0])
    gamma_A_player = F(ray[2 + A_PLAYER])
    return 8 * max(-gamma_A_player + 3 * r_A, F(0)) - 27 * r_A


def first_coarse_rate(record, ray):
    r_A, r_B = map(F, ray[:2])
    gamma_A_player = F(ray[2 + A_PLAYER])
    q = core(record)
    m_A = F(record["mono_A"])
    q_A, q_B = q.get(A, F(0)), q.get(B, F(0))
    lower_H = r_B * q_B + max(
        -m_A * gamma_A_player + r_A * q_A - r_B * q_B,
        F(0),
    )
    return (8 * lower_H - 9 * r_A * q_A) / m_A


def second_rate(record, ray):
    r_B = F(ray[1])
    q_B = core(record)[B]
    return (
        8 * hinge_score(record, ray) - 9 * r_B * q_B
    ) / F(record["mono_B"])


def root_coarse_H(mass_type, ray):
    m_A, m_B, q_A, q_B = mass_type
    r_A, r_B = map(F, ray[:2])
    gamma = tuple(map(F, ray[2:]))
    return r_B * q_B + max(
        m_A * gamma[A_PLAYER] + m_B * gamma[B_PLAYER]
        + r_A * q_A - r_B * q_B,
        F(0),
    )


def projected_core(record):
    """Delete the fixed witness player; combine any repeated masks."""
    result = {}
    for coalition, weight in core(record).items():
        projected = coalition & ~U
        result[projected] = result.get(projected, F(0)) + weight
    return tuple(sorted(result.items()))


def render_tuple(values):
    return [str(value) for value in values]


def audit(input_path):
    payload = json.loads(Path(input_path).read_text())
    blocks = payload["local_circuit_certificates"]
    first_leaves = blocks["first_leaf"]
    second_leaves = blocks["second_leaf"]
    roots = blocks["root"]
    ray_rows = payload["ray_certificates"]

    first_types = sorted({first_mass_type(record) for record in first_leaves})
    assert len(first_types) == 18
    assert all(F(0) <= u <= 3 and v >= 0 for u, v in first_types)
    assert (F(3), F(0)) in first_types

    projected_seconds = {projected_core(record) for record in second_leaves}
    assert len(projected_seconds) == 1
    root_types = sorted({root_mass_type(record) for record in roots})
    assert len(root_types) == 12

    compressed_rows = []
    exception_rows = []
    exact_comparisons = 0
    for stored in ray_rows:
        ray = tuple(stored["ray"])
        analytic_A = first_analytic_rate(ray)
        coarse_A_values = [
            first_coarse_rate(record, ray) for record in first_leaves
        ]
        exact_A_values = [
            (
                8 * hinge_score(record, ray)
                - 9 * F(ray[0]) * core(record)[A]
            ) / F(record["mono_A"])
            for record in first_leaves
        ]
        assert min(coarse_A_values) == analytic_A
        assert all(
            exact >= coarse >= analytic_A
            for exact, coarse in zip(exact_A_values, coarse_A_values)
        )

        B_values = [second_rate(record, ray) for record in second_leaves]
        assert len(set(B_values)) == 1
        analytic_B = B_values[0]
        assert analytic_B == F(stored["second_leaf_minimum_rate"])

        coarse_root_margins = [
            8 * root_coarse_H(mass_type, ray)
            + mass_type[0] * analytic_A
            + mass_type[1] * analytic_B
            for mass_type in root_types
        ]
        coarse_minimum = min(coarse_root_margins)
        exact_comparisons += len(root_types)
        method = "degree-only mass-type bound"
        certified_minimum = coarse_minimum
        exact_exception_minimum = None
        if coarse_minimum < 0:
            assert ray == EXCEPTIONAL_RAY
            negative_types = {
                root_types[index]
                for index, value in enumerate(coarse_root_margins)
                if value < 0
            }
            exceptional_roots = [
                (index, record) for index, record in enumerate(roots)
                if root_mass_type(record) in negative_types
            ]
            exact_root_margins = [
                8 * hinge_score(record, ray)
                + F(record["mono_A"]) * analytic_A
                + F(record["mono_B"]) * analytic_B
                for _index, record in exceptional_roots
            ]
            exact_exception_minimum = min(exact_root_margins)
            assert exact_exception_minimum >= 0
            nonnegative_coarse_minimum = min(
                value for value in coarse_root_margins if value >= 0
            )
            exact_comparisons += len(exceptional_roots)
            certified_minimum = min(
                nonnegative_coarse_minimum, exact_exception_minimum
            )
            method = "exceptional exact root-incidence correction"
            exception_rows.append({
                "ray": list(ray),
                "coarse_minimum": str(coarse_minimum),
                "coarse_negative_mass_types": [
                    render_tuple(root_types[index])
                    for index, value in enumerate(coarse_root_margins)
                    if value == coarse_minimum
                ],
                "exceptional_root_indices": [
                    index + 1 for index, _record in exceptional_roots
                ],
                "exceptional_root_exact_margins": [
                    str(value) for value in exact_root_margins
                ],
                "exceptional_root_exact_minimum": str(
                    exact_exception_minimum
                ),
                "other_mass_type_coarse_minimum": str(
                    nonnegative_coarse_minimum
                ),
                "certified_all_root_minimum": str(certified_minimum),
            })
        assert certified_minimum >= 0
        assert certified_minimum <= F(stored["root_minimum_margin"])
        compressed_rows.append({
            "ray": list(ray),
            "first_leaf_analytic_rate": str(analytic_A),
            "second_leaf_exact_rate": str(analytic_B),
            "coarse_root_minimum": str(coarse_minimum),
            "certificate_method": method,
            "certified_global_margin": str(certified_minimum),
        })

    assert len(exception_rows) == 1
    return {
        "status": "exact analytic compression of fixed-{5} local proof",
        "geometry": dict(payload["geometry"]),
        "input_local_comparisons": payload["exact_local_comparisons"],
        "first_leaf_degree_bound": (
            "H(q)>=r_B q_B+[-m_A gamma_a+r_A q_A-r_B q_B]_+"
        ),
        "first_leaf_normalized_mass_types": [
            render_tuple(mass_type) for mass_type in first_types
        ],
        "first_leaf_mass_type_count": len(first_types),
        "first_leaf_coefficient_ceiling": "q_A/m_A <= 3",
        "first_leaf_analytic_minimizer": ["3", "0"],
        "first_leaf_analytic_rate": "8[-gamma_a+3r_A]_+-27r_A",
        "second_leaf_projected_collections_identical": True,
        "second_leaf_projected_collection": [
            [coalition, str(weight)]
            for coalition, weight in next(iter(projected_seconds))
        ],
        "root_mass_types": [render_tuple(mass_type) for mass_type in root_types],
        "root_mass_type_count": len(root_types),
        "arrangement_rays_checked": len(ray_rows),
        "degree_only_rays": len(ray_rows) - len(exception_rows),
        "exceptional_incidence_rays": len(exception_rows),
        "compressed_root_comparisons": exact_comparisons,
        "strict_9_over_8_violations": 0,
        "exception_records": exception_rows,
        "ray_certificates": compressed_rows,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/glued_fixed16_local_factorization_n6_321.json"),
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(args.input), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
