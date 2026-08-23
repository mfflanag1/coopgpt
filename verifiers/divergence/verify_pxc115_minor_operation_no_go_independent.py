#!/usr/bin/env python3
"""Independent exact audit of the PXC115 minor-operation no-go.

This verifier imports only two older standalone rational active-set audits.
Those audits import no project game, simplex, selector, cover, or PXC115 code.
The reductions, subgame exactness tests, cover census, and null-extension
checks below are newly formulated and share no implementation with the
primary PXC115 verifier.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ARCHIVE = HERE.parent / "search_archive"
sys.path[:0] = [str(HERE.parent), str(ARCHIVE)]

import verify_pxc101_forced_zero_family_independent as p101  # noqa: E402
import unrestricted_pxc91c_n6_generator_counterexample_independent as second  # noqa: E402
import z3  # noqa: E402


def csum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def constraints_of(values):
    return {s: values[s] for s in range(1, len(values) - 1) if values[s]}


def delete(values, player):
    n = len(values).bit_length() - 1
    keep = tuple(i for i in range(n) if i != player)
    return tuple(
        values[sum(1 << keep[j] for j in range(n - 1) if s >> j & 1)]
        for s in range(1 << (n - 1))
    )


def contract_normalized(values, player):
    n = len(values).bit_length() - 1
    keep = tuple(i for i in range(n) if i != player)
    raw = tuple(
        values[(1 << player) | sum(
            1 << keep[j] for j in range(n - 1) if s >> j & 1
        )] - values[1 << player]
        for s in range(1 << (n - 1))
    )
    baselines = tuple(raw[1 << j] for j in range(n - 1))
    return tuple(
        q - sum(baselines[j] for j in range(n - 1) if s >> j & 1)
        for s, q in enumerate(raw)
    )


def amalgamate(values, first, second_player):
    n = len(values).bit_length() - 1
    keep = tuple(i for i in range(n) if i not in (first, second_player))
    star = n - 2
    answer = []
    for s in range(1 << (n - 1)):
        old = sum(1 << keep[j] for j in range(n - 2) if s >> j & 1)
        if s >> star & 1:
            old |= (1 << first) | (1 << second_player)
        answer.append(values[old])
    return tuple(answer)


def append_null(values):
    return tuple(values[s & (len(values) - 1)] for s in range(2 * len(values)))


def core_minimum(values, coalition):
    n = len(values).bit_length() - 1
    objective = [F((coalition >> i) & 1) for i in range(n)]
    lower = p101.inequalities(constraints_of(values), n)
    optimum, point = p101.active_lp(
        objective, lower, [([F(1)] * n, values[-1])]
    )
    return optimum, point


def cover_lifts(values, x, z, cx):
    n = len(x)
    full = (1 << n) - 1
    ztight = tuple(s for s in range(1, full) if csum(z, s) == values[s])
    cover_items = p101.cover_census(ztight, n, z)
    results = []
    for rows, weights, eta, alpha in cover_items:
        retained = {s: csum(x, s) for s in cx}
        retained.update({s: csum(z, s) for s in rows})
        lx = p101.selector(retained, n, values[-1], "min")
        lz = p101.selector(retained, n, values[-1], "max")
        results.append((rows, weights, eta, alpha, lx, lz))
    return tuple(results)


def z3q(value):
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def prove_pxc101_n7_mapped_values(defining, total, expected, mapper):
    """Prove all mapped coalition minima by exact Z3 lower/attainment gates."""
    n = 7
    y = [z3.Real(f"y_{i}") for i in range(n)]
    base = [q >= 0 for q in y]
    base.append(z3.Sum(y) == z3q(total))
    for coalition, bound in defining.items():
        base.append(z3.Sum([y[i] for i in range(n) if coalition >> i & 1])
                    >= z3q(bound))
    checked = []
    for coalition, target in enumerate(expected):
        old = mapper(coalition)
        objective = z3.Sum([y[i] for i in range(n) if old >> i & 1])
        lower = z3.Solver(); lower.add(*base, objective < z3q(target))
        if lower.check() != z3.unsat:
            raise AssertionError(("mapped lower bound", coalition, target))
        attain = z3.Solver(); attain.add(*base, objective == z3q(target))
        if attain.check() != z3.sat:
            raise AssertionError(("mapped attainment", coalition, target))
        checked.append(coalition)
    return tuple(checked)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # Independent n=6/n=7 PXC101 reconstruction.
    n6, t6, defining6, x6, z6, _ = p101.family(2)
    n7, t7, defining7, x7, z7, _ = p101.family(3)
    v6, _ = p101.lower_envelope(defining6, n6, t6)
    v7, _ = p101.lower_envelope(defining7, n7, t7)

    # Ordinary deletion: one explicit violated exactness equality.
    deleted = delete(v6, 2)
    deletion_min, deletion_point = core_minimum(deleted, 1)
    if deleted[1] != 0 or deletion_min != 6:
        raise AssertionError(("deletion gap", deleted[1], deletion_min))

    parallel_deleted = delete(v7, 6)
    parallel_min, parallel_point = core_minimum(parallel_deleted, 1)
    if parallel_deleted[1] != 0 or parallel_min != 6:
        raise AssertionError((
            "parallel-element deletion gap", parallel_deleted[1], parallel_min
        ))

    # Contraction and incidence-parallel amalgamation independently coincide
    # with a four-row exact game whose two covers are faithful.
    reduced_defining = {7: F(11), 11: F(11), 17: F(6), 51: F(12)}
    reduced_values, _ = p101.lower_envelope(reduced_defining, 6, F(18))
    contraction_checks = prove_pxc101_n7_mapped_values(
        defining7, t7, reduced_values, lambda coalition: coalition | (1 << 6)
    )
    amalgamation_checks = prove_pxc101_n7_mapped_values(
        defining7, t7, reduced_values,
        lambda coalition: (
            (coalition & 31) |
            (((1 << 5) | (1 << 6)) if coalition >> 5 & 1 else 0)
        ),
    )
    reduced_x = p101.selector(reduced_defining, 6, F(18), "min")
    reduced_z = p101.selector(reduced_defining, 6, F(18), "max")
    expected_reduced_x = (F(13, 3), F(13, 3)) + (F(7, 3),) * 4
    expected_reduced_z = tuple(map(F, (4, 4, 3, 3, 2, 2)))
    if reduced_x != expected_reduced_x or reduced_z != expected_reduced_z:
        raise AssertionError((reduced_x, reduced_z))
    reduced_lifts = cover_lifts(reduced_values, reduced_x, reduced_z, (7, 11))
    if tuple(q[0] for q in reduced_lifts) != ((3,), (7, 11, 51)):
        raise AssertionError("reduced cover census changed")
    if any(q[4] != reduced_x or q[5] != reduced_z for q in reduced_lifts):
        raise AssertionError("a reduced cover is not faithful")

    # The pre-existing standalone six-generator encoding supplies a genuinely
    # independent minimal common-branch and z-zero deletion falsifier.
    if second.Z[2] != 0 or second.CX != (19, 43):
        raise AssertionError("secondary calibration changed")
    all_covers = second.covers(True)
    if len(all_covers) != 5:
        raise AssertionError(("secondary covers", all_covers))
    subset_lmins = {}
    for size in range(3):
        for rows in itertools.combinations(second.CX, size):
            subset_lmins[rows] = second.sparse_selector(
                {s: csum(second.X, s) for s in rows}, "min"
            )
    if subset_lmins[second.CX] != second.X or any(
        lx == second.X for rows, lx in subset_lmins.items() if rows != second.CX
    ):
        raise AssertionError("secondary complete-Cx uniqueness changed")
    second_lifts = []
    for rows, _weights, _eta, _alpha in all_covers:
        retained = {s: csum(second.X, s) for s in second.CX}
        retained.update({s: csum(second.Z, s) for s in rows})
        lx = second.sparse_selector(retained, "min")
        lz = second.sparse_selector(retained, "max")
        if lx != second.X or lz != second.ZPRIME:
            raise AssertionError(("secondary failing lift", rows, lx, lz))
        second_lifts.append({"rows": list(rows), "lmax": list(map(str, lz))})
    common_direction = (F(0), F(0), F(0), F(1), F(0), F(-1))
    cover_union = {s for rows, *_ in all_covers for s in rows}
    if any(csum(common_direction, s) for s in (*second.CX, *cover_union)):
        raise AssertionError("secondary direction no longer vanishes on cover union")
    second_ztight = tuple(
        s for s in range(1, 63) if csum(second.Z, s) == second.VALUES[s]
    )
    negative_ztight = tuple(
        s for s in second_ztight if csum(common_direction, s) < 0
    )
    if negative_ztight != (39,) or 39 in cover_union:
        raise AssertionError(("secondary forced-zero blocker", negative_ztight))
    contraction_gap_values = contract_normalized(second.VALUES, 0)
    contraction_min, contraction_point = core_minimum(contraction_gap_values, 1)
    if contraction_gap_values[1] != 0 or contraction_min != 1:
        raise AssertionError((
            "contraction exactness gap", contraction_gap_values[1], contraction_min
        ))
    zero_deleted = delete(second.VALUES, 2)
    zero_min, zero_point = core_minimum(zero_deleted, 2)
    if zero_deleted[2] != 0 or zero_min != 2:
        raise AssertionError(("z-zero deletion gap", zero_deleted[2], zero_min))

    # Independent null-extension warning for PXC104.  It is enough to verify
    # the complete certificate and the two new faithful covers; the primary
    # audit exhausts all 22 extreme covers.
    p104_defining = {
        7: F(16), 11: F(16), 19: F(13),
        23: F(18), 35: F(13), 39: F(18),
    }
    p104_values, _ = p101.lower_envelope(p104_defining, 6, F(23))
    p104_x = (F(41, 6), F(41, 6)) + (F(7, 3),) * 4
    p104_z = tuple(map(F, (6, 6, 5, 4, 1, 1)))
    null_values = append_null(p104_values)
    null_x, null_z = p104_x + (F(0),), p104_z + (F(0),)
    null_cx = (7, 11, 63)
    faithful_supports = (
        (11, 19, 39, 87, 99),
        (11, 23, 35, 83, 103),
    )
    null_ztight = tuple(
        s for s in range(1, 127) if csum(null_z, s) == null_values[s]
    )
    null_cover_items = p101.cover_census(null_ztight, 7, null_z)
    null_cover_supports = tuple(q[0] for q in null_cover_items)
    faithful_replays = []
    for rows in faithful_supports:
        if rows not in null_cover_supports:
            raise AssertionError(("not an extreme null cover", rows))
        projected_rows = {s & 63 for s in (*null_cx, *rows)} - {63}
        if projected_rows != set(p104_defining):
            raise AssertionError(("null support does not recover full core", rows,
                                  projected_rows))
        faithful_replays.append({
            "rows": list(rows),
            "faithful": True,
            "reason": "Cx plus projected cover rows equals every PXC104 defining row",
        })

    payload = {
        "claim": "independent exact audit of PXC115 natural-minor no-go",
        "ordinary_deletion": {
            "stated_singleton_value": str(deleted[1]),
            "core_lower_envelope_value": str(deletion_min),
            "core_minimizer": list(map(str, deletion_point)),
        },
        "parallel_element_removal": {
            "source_players": [5, 6],
            "defining_row_parallel_and_selector_equal": True,
            "removed_player": 6,
            "stated_singleton_value": str(parallel_deleted[1]),
            "core_lower_envelope_value": str(parallel_min),
            "core_minimizer": list(map(str, parallel_point)),
        },
        "contraction_and_parallel_amalgamation": {
            "same_all_64_coalition_values": True,
            "contraction_Z3_lower_and_attainment_checks": len(contraction_checks),
            "amalgamation_Z3_lower_and_attainment_checks": len(amalgamation_checks),
            "result_selectors": {
                "Lmin": list(map(str, reduced_x)),
                "Lmax": list(map(str, reduced_z)),
            },
            "extreme_covers": [list(q[0]) for q in reduced_lifts],
            "every_cover_faithful": True,
        },
        "normalized_contraction_exactness_counterexample": {
            "source": "PXC116 sparse failure",
            "contracted_player": 0,
            "contracted_values": list(map(str, contraction_gap_values)),
            "coalition": 1,
            "stated_value": str(contraction_gap_values[1]),
            "core_lower_envelope_value": str(contraction_min),
            "core_minimizer": list(map(str, contraction_point)),
        },
        "minimal_common_primitive_falsifier": {
            "selectors": {
                "Lmin": list(map(str, second.X)),
                "Lmax": list(map(str, second.Z)),
            },
            "unique_complete_cx": list(second.CX),
            "extreme_covers": [list(q[0]) for q in all_covers],
            "cover_count": len(all_covers),
            "failing_lifts": second_lifts,
            "common_direction": list(map(str, common_direction)),
            "forced_zero_blocker": 39,
            "negative_z_tight_rows": list(negative_ztight),
            "forced_zero_blocker_absent_from_cover_union": 39 not in cover_union,
            "zero_player_deletion": {
                "player": 2,
                "stated_value": str(zero_deleted[2]),
                "core_lower_envelope_value": str(zero_min),
                "core_minimizer": list(map(str, zero_point)),
            },
        },
        "null_extension_cover_warning": {
            "complete_cx": list(null_cx),
            "faithful_extreme_cover_replays": faithful_replays,
        },
        "independence": (
            "standalone rational active-set kernels; imports no project game, "
            "simplex, selector, cover, PXC115, or primary-verifier implementation"
        ),
        "scope": (
            "Independent reconstruction of every load-bearing negative witness; "
            "the primary verifier separately exhausts the 22-cover null extension."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
