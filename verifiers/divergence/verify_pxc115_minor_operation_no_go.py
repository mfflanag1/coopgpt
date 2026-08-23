#!/usr/bin/env python3
"""Exact primary audit of natural player-minor operations for PXC115.

The purpose is adversarial: it tests whether the usual literal coordinate
operations preserve the sparse Lmin--Lmax fidelity-failure problem.  It does
not infer a global theorem from a bounded search.  Each negative result is a
fully specified rational counterexample to a universal preservation claim.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
ARCHIVE = HERE.parent / "search_archive"
sys.path[:0] = [str(HERE.parent), str(ARCHIVE)]

from audit_pxc52_coloured_charge import lower_envelope as point_envelope  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    csum,
    selector_pair,
    tight_rows,
)
from verify_pxc101_forced_zero_family import family  # noqa: E402


def nonzero_constraints(values: tuple[F, ...]) -> dict[int, F]:
    return {s: values[s] for s in range(1, len(values) - 1) if values[s]}


def replay(values: tuple[F, ...]):
    n = len(values).bit_length() - 1
    rebuilt, x, z = selector_pair(nonzero_constraints(values), n, values[-1])
    return rebuilt, x, z


def delete_player(values: tuple[F, ...], player: int) -> tuple[F, ...]:
    n = len(values).bit_length() - 1
    keep = tuple(i for i in range(n) if i != player)
    return tuple(
        values[sum(1 << keep[j] for j in range(n - 1) if s >> j & 1)]
        for s in range(1 << (n - 1))
    )


def normalized_contraction(values: tuple[F, ...], player: int) -> tuple[F, ...]:
    """Contract a player, then subtract the contracted singleton baselines."""
    n = len(values).bit_length() - 1
    keep = tuple(i for i in range(n) if i != player)
    raw = tuple(
        values[(1 << player) | sum(
            1 << keep[j] for j in range(n - 1) if s >> j & 1
        )] - values[1 << player]
        for s in range(1 << (n - 1))
    )
    singleton = tuple(raw[1 << j] for j in range(n - 1))
    return tuple(
        q - sum(singleton[j] for j in range(n - 1) if s >> j & 1)
        for s, q in enumerate(raw)
    )


def amalgamate(values: tuple[F, ...], first: int, second: int) -> tuple[F, ...]:
    """Replace two players by one whose presence means that both are present."""
    n = len(values).bit_length() - 1
    keep = tuple(i for i in range(n) if i not in (first, second))
    star = n - 2
    answer = []
    for s in range(1 << (n - 1)):
        old = sum(1 << keep[j] for j in range(n - 2) if s >> j & 1)
        if s >> star & 1:
            old |= (1 << first) | (1 << second)
        answer.append(values[old])
    return tuple(answer)


def permute(values: tuple[F, ...], image: tuple[int, ...]) -> tuple[F, ...]:
    n = len(image)
    if sorted(image) != list(range(n)):
        raise ValueError("image must be a permutation")
    answer = [F(0)] * (1 << n)
    for old_mask, q in enumerate(values):
        new_mask = sum(1 << image[i] for i in range(n) if old_mask >> i & 1)
        answer[new_mask] = q
    return tuple(answer)


def append_null(values: tuple[F, ...]) -> tuple[F, ...]:
    """Adjoin a player that is absent from every game value."""
    return tuple(values[s & (len(values) - 1)] for s in range(2 * len(values)))


def first_envelope_gap(values: tuple[F, ...], rebuilt: tuple[F, ...]):
    for coalition, (old, new) in enumerate(zip(values, rebuilt)):
        if old != new:
            return {
                "coalition": coalition,
                "stated_value": str(old),
                "core_lower_envelope_value": str(new),
            }
    return None


def pxc101_values(k: int):
    item = family(k)
    values, x, z = selector_pair(
        item["constraints"], item["n"], item["total"]
    )
    if x != item["x"] or z != item["z"]:
        raise AssertionError((k, x, z))
    return item, values, x, z


def exact_failure_audit(label: str, values: tuple[F, ...], x, z):
    result = audit_game(label, values, x, z, pool_max=10, replay_exact=False)
    if result is None:
        raise AssertionError((label, "not in the two-top divergent domain"))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    n6, v6, x6, z6 = pxc101_values(2)
    n7, v7, x7, z7 = pxc101_values(3)
    original = exact_failure_audit("PXC101_n7", v7, x7, z7)
    if original["fixed_faithful_cover_exists"]:
        raise AssertionError("PXC101 n=7 ceased to be a universal-cover failure")

    # Literal restriction can leave the exact-game cone.
    deleted = delete_player(v6, 2)
    deleted_replay, deleted_x, deleted_z = replay(deleted)
    deletion_gap = first_envelope_gap(deleted, deleted_replay)
    if deletion_gap is None:
        raise AssertionError("ordinary deletion unexpectedly preserved exactness")

    # Even literal removal of one of two defining-row-parallel,
    # selector-equal bottom players can leave the exact cone.
    parallel_deleted = delete_player(v7, 6)
    parallel_deleted_replay, _, _ = replay(parallel_deleted)
    parallel_deletion_gap = first_envelope_gap(
        parallel_deleted, parallel_deleted_replay
    )
    if parallel_deletion_gap != {
        "coalition": 1,
        "stated_value": "0",
        "core_lower_envelope_value": "6",
    }:
        raise AssertionError(("parallel deletion gap", parallel_deletion_gap))

    # Contracting a symmetric low outsider leaves an exact, normalized,
    # divergent two-top game, but the two extreme covers are now faithful.
    contracted = normalized_contraction(v7, 6)
    contracted_replay, contracted_x, contracted_z = replay(contracted)
    if contracted_replay != contracted:
        raise AssertionError("normalized contraction lost exactness")
    if any(contracted[1 << i] for i in range(6)):
        raise AssertionError("normalized contraction lost singleton normalization")
    contracted_audit = exact_failure_audit(
        "PXC101_n7_contract_parallel_bottom", contracted,
        contracted_x, contracted_z,
    )
    if not contracted_audit["fixed_faithful_cover_exists"]:
        raise AssertionError("contraction did not destroy the failure")

    # Players 5 and 6 have identical incidence in every displayed PXC101 row,
    # and equal coordinates in both selectors.  Literal amalgamation still
    # destroys cover failure.
    amalgamated = amalgamate(v7, 5, 6)
    amalgamated_replay, amalgamated_x, amalgamated_z = replay(amalgamated)
    if amalgamated_replay != amalgamated:
        raise AssertionError("parallel amalgamation lost exactness")
    amalgamated_audit = exact_failure_audit(
        "PXC101_n7_amalgamate_parallel_bottom", amalgamated,
        amalgamated_x, amalgamated_z,
    )
    if not amalgamated_audit["fixed_faithful_cover_exists"]:
        raise AssertionError("parallel amalgamation did not destroy the failure")
    if (contracted_x, contracted_z) != (amalgamated_x, amalgamated_z):
        raise AssertionError("the two reductions ceased to share selectors")

    # A zero coordinate of Lmax is not a null-player certificate.  This second
    # exact six-player universal failure has z_2=0, a unique complete Cx, five
    # extreme covers, and a common blocker.  It is therefore also a
    # dimension-minimal counterexample to literal PXC101 canonicality.
    zero_points = tuple(tuple(map(F, row)) for row in (
        (0, 13, 1, 3, 0, 1),
        (12, 0, 0, 1, 1, 4),
        (12, 5, 0, 0, 0, 1),
        (4, 10, 1, 0, 0, 3),
        (11, 3, 0, 1, 0, 3),
        (3, 11, 1, 3, 0, 0),
    ))
    zero_game = point_envelope(zero_points)
    zero_replay, zero_x, zero_z = replay(zero_game)
    if zero_replay != zero_game or zero_z[2] != 0:
        raise AssertionError(("zero-coordinate calibration", zero_x, zero_z))
    zero_audit = exact_failure_audit(
        "secondary_n6_common_direction_failure", zero_game, zero_x, zero_z
    )
    if zero_audit["fixed_faithful_cover_exists"]:
        raise AssertionError("secondary common-direction control became faithful")
    if zero_audit["complete_cx_count"] != 1 or len(zero_audit["covers"]) != 5:
        raise AssertionError("secondary complete-Cx/cover census changed")
    common_direction = (F(0), F(0), F(0), F(1), F(0), F(-1))
    zero_cover_union = {
        s for cover in zero_audit["covers"] for s in cover["rows"]
    }
    if any(csum(common_direction, s) for s in (19, 43, *zero_cover_union)):
        raise AssertionError("secondary common direction left the retained union")
    negative_ztight = tuple(
        s for s in tight_rows(zero_game, zero_z)
        if csum(common_direction, s) < 0
    )
    if negative_ztight != (39,) or 39 in zero_cover_union:
        raise AssertionError(("secondary forced-zero blocker", negative_ztight))
    zero_contracted = normalized_contraction(zero_game, 0)
    zero_contracted_replay, _, _ = replay(zero_contracted)
    contraction_exactness_gap = first_envelope_gap(
        zero_contracted, zero_contracted_replay
    )
    if contraction_exactness_gap != {
        "coalition": 1,
        "stated_value": "0",
        "core_lower_envelope_value": "1",
    }:
        raise AssertionError(("contraction exactness gap", contraction_exactness_gap))
    zero_deleted = delete_player(zero_game, 2)
    zero_deleted_replay, _, _ = replay(zero_deleted)
    zero_gap = first_envelope_gap(zero_deleted, zero_deleted_replay)
    if zero_gap is None:
        raise AssertionError("z-zero deletion unexpectedly preserved exactness")

    # Relabeling and true null extension/reduction are positive controls.
    image = (1, 0, 3, 2, 5, 4)
    relabelled = permute(v6, image)
    relabelled_replay, relabelled_x, relabelled_z = replay(relabelled)
    if relabelled_replay != relabelled:
        raise AssertionError("relabeling lost exactness")
    expected_x = tuple(x6[image.index(i)] for i in range(6))
    expected_z = tuple(z6[image.index(i)] for i in range(6))
    if (relabelled_x, relabelled_z) != (expected_x, expected_z):
        raise AssertionError("relabeling changed selectors beyond permutation")
    relabelled_audit = exact_failure_audit(
        "PXC101_n6_relabelled", relabelled, relabelled_x, relabelled_z
    )
    if relabelled_audit["fixed_faithful_cover_exists"]:
        raise AssertionError("relabeling destroyed universal failure")

    null_extended = append_null(v6)
    null_replay, null_x, null_z = replay(null_extended)
    if null_replay != null_extended:
        raise AssertionError("null extension lost exactness")
    if delete_player(null_extended, 6) != v6:
        raise AssertionError("null reduction is not inverse to extension")
    if tuple(q for i, q in enumerate(null_x) if i != 6) != x6 or null_x[6] != 0:
        raise AssertionError("null extension changed Lmin")
    if tuple(q for i, q in enumerate(null_z) if i != 6) != z6 or null_z[6] != 0:
        raise AssertionError("null extension changed Lmax")

    # Core-null equivalence is not cover-quantifier equivalence.  A null
    # extension of PXC104 has the same selectors and a complete certificate
    # obtained by adding the old grand-coalition row (which forces the null
    # coordinate to zero), but its enlarged duplicate-row cover polytope has
    # faithful extreme covers.
    pxc104_constraints = {
        7: F(16), 11: F(16), 19: F(13), 23: F(18), 35: F(13), 39: F(18)
    }
    pxc104, pxc104_x, pxc104_z = selector_pair(
        pxc104_constraints, 6, F(23)
    )
    pxc104_null = append_null(pxc104)
    pxc104_null_replay, pxc104_null_x, pxc104_null_z = replay(pxc104_null)
    if pxc104_null_replay != pxc104_null:
        raise AssertionError("PXC104 null extension lost exactness")
    if pxc104_null_x != pxc104_x + (F(0),) or pxc104_null_z != pxc104_z + (F(0),):
        raise AssertionError("PXC104 null extension changed selectors")
    from unrestricted_pxc91c_exact_search import covers, lift  # local, primary audit
    pxc104_null_cx = (7, 11, 63)
    pxc104_null_covers = covers(pxc104_null, pxc104_null_z)
    pxc104_faithful = []
    for rows, _certificate in pxc104_null_covers:
        faithful, lx, lz, singleton = lift(
            pxc104_null, pxc104_null_x, pxc104_null_z,
            pxc104_null_cx, rows, True,
        )
        if lx != pxc104_null_x or not singleton:
            raise AssertionError(("PXC104 null lift base", rows, lx, singleton))
        if faithful:
            pxc104_faithful.append(rows)
    if tuple(pxc104_faithful) != (
        (11, 19, 39, 87, 99),
        (11, 23, 35, 83, 103),
    ):
        raise AssertionError(("PXC104 null faithful covers", pxc104_faithful))

    payload = {
        "claim": (
            "PXC115 exact no-go for literal deletion, parallel-element "
            "removal, normalized contraction, incidence-parallel "
            "amalgamation, and selector-zero deletion; relabeling and "
            "core-forced null reduction are scoped positive controls"
        ),
        "operations": {
            "ordinary_deletion": {
                "source": "PXC101 n=6",
                "deleted_player": 2,
                "source_exact_singleton_normalized": True,
                "result_exact": False,
                "first_exactness_gap": deletion_gap,
                "core_envelope_selectors": {
                    "Lmin": list(map(str, deleted_x)),
                    "Lmax": list(map(str, deleted_z)),
                },
            },
            "parallel_element_removal": {
                "source": "PXC101 n=7",
                "removed_player": 6,
                "parallel_to_player": 5,
                "parallel_in_defining_rows": True,
                "equal_in_Lmin_and_Lmax": x7[5] == x7[6] and z7[5] == z7[6],
                "result_exact": False,
                "first_exactness_gap": parallel_deletion_gap,
            },
            "normalized_contraction": {
                "exactness_counterexample": {
                    "source": "PXC116 sparse failure",
                    "contracted_player": 0,
                    "result_exact": False,
                    "first_exactness_gap": contraction_exactness_gap,
                },
                "sparse_failure_source": "PXC101 n=7",
                "contracted_player": 6,
                "source_universal_cover_failure": True,
                "result_exact_singleton_normalized": True,
                "result_selectors": {
                    "Lmin": list(map(str, contracted_x)),
                    "Lmax": list(map(str, contracted_z)),
                },
                "result_cover_rows": [q["rows"] for q in contracted_audit["covers"]],
                "result_every_cover_faithful": all(
                    q["fixed_faithful"] for q in contracted_audit["covers"]
                ),
            },
            "parallel_amalgamation": {
                "source": "PXC101 n=7",
                "amalgamated_players": [5, 6],
                "parallel_in_defining_rows": True,
                "equal_in_Lmin_and_Lmax": x7[5] == x7[6] and z7[5] == z7[6],
                "result_exact_singleton_normalized": True,
                "result_selectors": {
                    "Lmin": list(map(str, amalgamated_x)),
                    "Lmax": list(map(str, amalgamated_z)),
                },
                "result_every_cover_faithful": all(
                    q["fixed_faithful"] for q in amalgamated_audit["covers"]
                ),
            },
            "selector_zero_deletion": {
                "source_generators": [list(map(str, q)) for q in zero_points],
                "source_selectors": {
                    "Lmin": list(map(str, zero_x)),
                    "Lmax": list(map(str, zero_z)),
                },
                "source_universal_cover_failure": True,
                "source_unique_complete_cx": zero_audit["complete_cx_count"] == 1,
                "source_extreme_cover_count": len(zero_audit["covers"]),
                "deleted_zero_Lmax_player": 2,
                "result_exact": False,
                "first_exactness_gap": zero_gap,
            },
            "minimal_common_primitive_falsifier": {
                "dimension": 6,
                "selectors": {
                    "Lmin": list(map(str, zero_x)),
                    "Lmax": list(map(str, zero_z)),
                },
                "complete_cx": zero_audit["complete_cx_cover_matrix"],
                "extreme_cover_rows": [q["rows"] for q in zero_audit["covers"]],
                "every_cover_fails": not zero_audit["fixed_faithful_cover_exists"],
                "common_direction": list(map(str, common_direction)),
                "negative_z_tight_rows": list(negative_ztight),
                "forced_zero_blocker_absent_from_cover_union": 39 not in zero_cover_union,
                "not_relabeling_equivalent_to_PXC101_reason": (
                    "five qualifying extreme covers versus PXC101's two"
                ),
                "dimension_minimality_dependency": (
                    "imports PXC100: no unrestricted sparse-fidelity failure at n<=5"
                ),
            },
            "relabeling_control": {
                "permutation_old_to_new": list(image),
                "exact_and_selector_equivariant": True,
                "universal_cover_failure_preserved": True,
            },
            "null_reduction_control": {
                "source": "PXC101 n=6 plus one null player",
                "core_forced_null_coordinate": 6,
                "extension_exact": True,
                "selectors_are_original_plus_zero": True,
                "deletion_recovers_source_byte_for_byte": True,
                "scope": "core and selector control only, not cover-extremality invariance",
            },
            "null_extension_cover_warning": {
                "source": "PXC104 reciprocal failure",
                "same_exact_core_selectors_plus_zero": True,
                "complete_cx_with_old_grand_row": list(pxc104_null_cx),
                "extreme_cover_count_after_extension": len(pxc104_null_covers),
                "faithful_extreme_covers_after_extension": [
                    list(q) for q in pxc104_faithful
                ],
                "conclusion": (
                    "null equivalence does not preserve the quantified extreme-cover verdict"
                ),
            },
        },
        "scope": (
            "Each negative row refutes universal preservation by the named "
            "literal operation.  This is not yet a classification of every "
            "conditional/admissible reduction and not by itself an antichain theorem."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
