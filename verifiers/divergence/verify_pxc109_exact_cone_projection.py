#!/usr/bin/env python3
"""Exact audit of the PXC109--PXC111 exact-cone projection theorem.

This verifier has four jobs.

* It checks the dimension-free partition-star semi-balanced identity and the
  exceptional-set classification used in the human indecomposability proof.
* It identifies the PXC101 and PXC104 positive covers with the same published
  n=6 exact-cone facet type, and checks the cross-cover two-facet incidence.
* It computes the exact minimal-face ranks of the PXC101 and PXC105 anchors
  against the complete Studeny--Kratochvil n=6 facet catalogue.
* It checks the PXC88 negative control: its unequal-top cover and the two
  indispensable later blockers have linearly independent augmented incidence
  columns, so no subset can be semi-balanced.

The catalogue computation is evidence for the stated n=6 ranks.  The
dimension-free facet and cellwise-projection statements are human theorems,
not consequences of this finite program.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "verifiers/lib")]

import catalogue  # noqa: E402
from exactlp import exact_linprog  # noqa: E402


def incidence(mask: int, n: int) -> tuple[F, ...]:
    return tuple(F((mask >> i) & 1) for i in range(n))


def matrix_rank(rows) -> int:
    a = [list(map(F, row)) for row in rows]
    if not a:
        return 0
    rank = 0
    for column in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][column]
        a[rank] = [q / scale for q in a[rank]]
        for i in range(len(a)):
            if i == rank or a[i][column] == 0:
                continue
            scale = a[i][column]
            a[i] = [q - scale * r for q, r in zip(a[i], a[rank])]
        rank += 1
    return rank


def mask(players) -> int:
    return sum(1 << i for i in players)


def partition_star(block_sizes: tuple[int, ...]) -> dict:
    """Return and audit the partition-star system on T={0,1}."""
    if len(block_sizes) < 2 or any(size <= 0 for size in block_sizes):
        raise AssertionError(block_sizes)
    top = 3
    blocks, cursor = [], 2
    for size in block_sizes:
        block = tuple(range(cursor, cursor + size))
        cursor += size
        blocks.append(block)
    n = cursor
    rows = tuple(top | mask(block) for block in blocks)
    coefficients = {top: F(-(len(blocks) - 1))}
    coefficients.update({row: F(1) for row in rows})
    load = [sum(c for row, c in coefficients.items() if row >> i & 1)
            for i in range(n)]
    if load != [F(1)] * n:
        raise AssertionError((block_sizes, load))

    # Closed-form Studeny--Kratochvil exceptional-set test.  A possible new
    # exceptional E must be constant on every block.  The displayed scalar
    # inequalities leave only T, T union B_i, empty, or N; hence no unsupported
    # proper exceptional coalition decomposes the system.
    full = (1 << n) - 1
    feasible = []
    for top_bit in (0, 1):
        for block_bits in itertools.product((0, 1), repeat=len(blocks)):
            candidate = (top if top_bit else 0)
            for bit, block in zip(block_bits, blocks):
                if bit:
                    candidate |= mask(block)
            # Scale the negative new-exception coefficient to one.  Search the
            # only breakpoints needed for the common load c: -1 and 0, plus the
            # point making the old-top coefficient zero.
            for common in (F(-1), F(0),
                           F(top_bit - sum(block_bits), len(blocks) - 1)):
                positive = [common + bit for bit in block_bits]
                old_top = (-(len(blocks) - 1) * common
                           + top_bit - sum(block_bits))
                if all(q >= 0 for q in positive) and old_top >= 0:
                    feasible.append(candidate)
                    break
    feasible = tuple(sorted(set(feasible)))
    expected = tuple(sorted((0, top, full, *rows)))
    if feasible != expected:
        raise AssertionError((block_sizes, feasible, expected))
    support_rank = matrix_rank([incidence(row, n) for row in (top, *rows)])
    if support_rank != len(rows) + 1:
        raise AssertionError((block_sizes, support_rank))
    return {
        "block_sizes": list(block_sizes),
        "n": n,
        "exceptional_top_pair": top,
        "positive_rows": list(rows),
        "coefficients": {str(k): str(v) for k, v in coefficients.items()},
        "support_rank": support_rank,
        "feasible_exceptional_sets_including_empty_full_and_support": list(feasible),
        "unsupported_proper_exceptional_sets": [],
        "indecomposable": True,
    }


def lower_envelope(n: int, total: F, constraints: dict[int, F]) -> tuple[F, ...]:
    aub, bub = [], []
    for coalition, bound in constraints.items():
        aub.append([-q for q in incidence(coalition, n)])
        bub.append(-bound)
    for player in range(n):
        row = [F(0)] * n
        row[player] = F(-1)
        aub.append(row)
        bub.append(F(0))
    values = []
    for coalition in range(1 << n):
        status, value, _point = exact_linprog(
            incidence(coalition, n), aub, bub, [[F(1)] * n], [total]
        )
        if status != "optimal":
            raise AssertionError((coalition, status))
        values.append(value)
    return tuple(values)


def pxc101_values(M: F, q: F, J: F, K: F) -> tuple[F, ...]:
    total = 2 * M + 2 * q + J + K
    return lower_envelope(6, total, {
        7: 2 * M + q,
        11: 2 * M + q,
        17: M + J,
        51: 2 * M + J + K,
    })


def pxc105_values(A: F) -> tuple[F, ...]:
    values = []
    for coalition in range(64):
        if coalition == 63:
            values.append(F(18) + A)
            continue
        if coalition & 3 != 3:
            values.append(F(0))
            continue
        trace = coalition >> 2
        candidates = [F(12)]
        if trace & 0b0011:
            candidates.append(F(16))
        if trace & 0b1100:
            candidates.append(F(13))
        if trace & 0b0001 and trace & 0b1100:
            candidates.append(F(13) + A)
        values.append(max(candidates))
    return tuple(values)


def exact_cone_facets_n6():
    full = 63
    answer: dict[tuple[int, ...], set[int]] = {}
    _letters, types = catalogue.load(6)
    for type_index, item in enumerate(types, 1):
        for permutation in itertools.permutations(range(6)):
            coefficients = [0] * 64
            for coalition, weight in item["lam"].items():
                image = sum(1 << permutation[i] for i in range(6)
                            if coalition >> i & 1)
                coefficients[image] += weight
            coefficients[full] -= item["r"]
            answer.setdefault(tuple(coefficients[1:]), set()).add(type_index)
    if len(answer) != 7006:
        raise AssertionError(("n6 facet count", len(answer)))
    return answer


def active_face(values: tuple[F, ...], facets) -> dict:
    active = []
    for normal, types in facets.items():
        slack = sum((F(normal[s - 1]) * values[s] for s in range(1, 64)), F(0))
        if slack > 0:
            raise AssertionError(("exact-cone violation", types, slack))
        if slack == 0:
            active.append((normal, types))
    rank = matrix_rank([normal for normal, _types in active])
    return {
        "active_facet_count": len(active),
        "active_normal_rank": rank,
        "minimal_exact_face_codimension": rank,
        "minimal_exact_face_dimension": 63 - rank,
        "active_catalogue_types": sorted(set().union(*(types for _, types in active))),
    }


def catalogue_type(lam: dict[int, int]) -> list[int]:
    index, _rows = catalogue.index(6)
    answer = index.get(catalogue.canon(6, lam))
    if not answer:
        raise AssertionError(("facet missing from catalogue", lam))
    return answer


def pxc88_no_semibalanced_projection() -> dict:
    # Unique unequal-top cover plus its two indispensable later blockers.
    rows = (27, 39, 66, 71, 75)
    # Columns are the five coalition incidences and the negative constant
    # target.  Full column rank rules out every nonzero constant dependence,
    # hence every semi-balanced subset.
    augmented_rows = [
        [F((row >> player) & 1) for row in rows] + [F(-1)]
        for player in range(7)
    ]
    rank = matrix_rank(augmented_rows)
    if rank != 6:
        raise AssertionError(("PXC88 augmented rank", rank))
    return {
        "n": 7,
        "cover_rows": [27, 39, 66],
        "cover_weights": ["1/3", "1/3", "1/3"],
        "eta": "1/3",
        "top_coefficients": ["1/3", "2/3"],
        "indispensable_blockers": [71, 75],
        "augmented_incidence_rank": rank,
        "augmented_columns": 6,
        "nonzero_constant_dependence": False,
        "semi_balanced_subsystem": False,
        "conclusion": (
            "the natural cover-blocker projection contains no exact-cone facet; "
            "unequal top coefficients obstruct the top-pair shear"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # Dimension-free theorem controls, including the PXC106 block sizes and
    # several larger asymmetric instances.
    stars = [partition_star(sizes) for sizes in (
        (1, 1), (1, 1, 1), (1, 1, 2), (1, 2, 3), (2, 3, 4),
    )]

    pxc101_lam = {3: -2, 7: 1, 11: 1, 51: 1}
    pxc104_left = {3: -2, 11: 1, 19: 1, 39: 1}
    pxc104_right = {3: -2, 11: 1, 23: 1, 35: 1}
    facet_types = {
        "PXC101": catalogue_type(pxc101_lam),
        "PXC104_left": catalogue_type(pxc104_left),
        "PXC104_right": catalogue_type(pxc104_right),
    }
    if set(map(tuple, facet_types.values())) != {(33,)}:
        raise AssertionError(facet_types)

    # Each PXC104 cross blocker is a row of the opposite facet and absent from
    # the facet whose tangent it cuts.
    left_support = set(pxc104_left)
    right_support = set(pxc104_right)
    if not (23 in right_support - left_support and 39 in left_support - right_support):
        raise AssertionError("PXC104 cross-facet incidence changed")

    facets = exact_cone_facets_n6()
    pxc101 = active_face(pxc101_values(F(15, 4), F(3), F(2), F(1)), facets)
    pxc105_faces = {
        str(A): active_face(pxc105_values(A), facets)
        for A in (F(17, 4), F(5), F(21, 4))
    }
    if pxc101["active_facet_count"] != 552 or pxc101["active_normal_rank"] != 54:
        raise AssertionError(("PXC101 face changed", pxc101))
    expected_pxc105 = {(835, 53, 10)}
    observed_pxc105 = {
        (item["active_facet_count"], item["active_normal_rank"],
         item["minimal_exact_face_dimension"])
        for item in pxc105_faces.values()
    }
    if observed_pxc105 != expected_pxc105:
        raise AssertionError(("PXC105 face changed", observed_pxc105))

    # PXC90 full-rank faithful negative control: five outsider columns have
    # rank five, so no nonzero later tangent survives the cover equalities.
    pxc90_rows = (23, 27, 39, 75, 114)
    pxc90_outsiders = (2, 3, 4, 5, 6)
    pxc90_matrix = [[F((row >> i) & 1) for row in pxc90_rows]
                    for i in pxc90_outsiders]
    pxc90_rank = matrix_rank(pxc90_matrix)
    if pxc90_rank != 5:
        raise AssertionError(("PXC90 rank", pxc90_rank))

    negative = pxc88_no_semibalanced_projection()
    payload = {
        "claim": (
            "PXC109 cellwise rational-polyhedral projection, PXC110 "
            "partition-star exact-cone facets, and PXC111 sharp failure of "
            "the unrestricted facet correspondence"
        ),
        "partition_star_theorem": {
            "identity": (
                "sum_i 1_(T union B_i) - (m-1)1_T = 1_N for every "
                "nontrivial partition N\\T = disjoint union_i B_i"
            ),
            "indecomposability": (
                "the only feasible exceptional sets are empty, N, T, and "
                "the supported T union B_i"
            ),
            "audited_instances": stars,
        },
        "family_projection": {
            "PXC101": {
                "facet_system": {str(k): str(v) for k, v in pxc101_lam.items()},
                "catalogue_type": facet_types["PXC101"],
                "interpretation": (
                    "one partition-star facet plus an external forced-zero blocker 17"
                ),
                "exact_cone_face": pxc101,
            },
            "PXC104_PXC105": {
                "left_facet": {str(k): str(v) for k, v in pxc104_left.items()},
                "right_facet": {str(k): str(v) for k, v in pxc104_right.items()},
                "catalogue_types": [facet_types["PXC104_left"],
                                    facet_types["PXC104_right"]],
                "cross_edges": [
                    {"from": "left", "to": "right", "blocker": 23},
                    {"from": "right", "to": "left", "blocker": 39},
                ],
                "minimal_union": True,
                "exact_cone_faces": pxc105_faces,
                "conic_family_span_dimension": 2,
            },
            "PXC106": {
                "dimension_free": True,
                "left_blocks": ["{b}", "J", "{a} union K"],
                "right_blocks": ["{b}", "{a} union J", "K"],
                "interpretation": (
                    "minimal union of two indecomposable partition-star facets "
                    "with the PXC108 two-cycle"
                ),
            },
        },
        "counterexample_to_unrestricted_correspondence": negative,
        "PXC90_full_rank_control": {
            "rows": list(pxc90_rows),
            "outsider_rank": pxc90_rank,
            "outsider_dimension": 5,
            "later_tangent_kernel_dimension": 0,
            "classification": "faithful",
        },
        "cellwise_projection_scope": {
            "fixed_data": (
                "x/z ordered partitions, active menus, fixed Cx, extreme-cover "
                "supports, active zero normals, and PXC108 edge/nonedge pattern"
            ),
            "result": (
                "the realization set is the projection of a relatively open "
                "rational polyhedral cone; for fixed n the failure locus is a "
                "finite union of such projected cones"
            ),
            "warning": (
                "selector cells decorate faces of the exact-game cone; they are "
                "not in general facets of that cone"
            ),
        },
        "sources": {
            "facet_catalogue": "verifiers/lib/cat/n6.csv",
            "catalogue_sha256": hashlib.sha256(
                (ROOT / "verifiers/lib/cat/n6.csv").read_bytes()
            ).hexdigest(),
            "Studeny_Kratochvil_DOI": "10.1007/s00186-022-00770-4",
            "Lohmann_Borm_Herings_DOI": "10.1016/j.mathsocsci.2012.01.002",
        },
        "evidence_scope": (
            "exact rational incidence and complete n=6 facet-catalogue audit; "
            "the dimension-free projection and indecomposability arguments are "
            "stated conventionally in the manuscript"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
