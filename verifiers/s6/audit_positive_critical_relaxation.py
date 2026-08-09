#!/usr/bin/env python3
"""Audit a sharp negative control for the positive critical residue.

The displayed rational generators satisfy singleton exactification, all three
forced Lmin-triple inequalities, two common-triple equalities, and have a
*claimed* pair at distance 31/45.  Closing the generators produces an exact
game, but exact recomputation changes both staged selections and reduces their
distance to 4/9.  Thus the three-triple residue is necessary local structure,
not a replacement for the full staged pinning packet.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

from audit_core_closure_reconstruction import (  # noqa: E402
    coalition_sum,
    encode,
    lower_envelope,
)
from audit_two_packet_exactification import (  # noqa: E402
    all_staged_pinning_certificates,
    independent_lex,
)
from lexsimplex import lex_point_with_trace  # noqa: E402


N = 6
FULL = (1 << N) - 1
P = (2, 3, 4)
R = 5

CLAIMED_LMIN = tuple(
    map(F, ("2/135", "29/270", "7/30", "1/6", "7/30", "11/45"))
)
CLAIMED_LMAX = tuple(
    map(F, ("1/270", "1/270", "47/135", "38/135", "47/135", "2/135"))
)
WITNESSES = tuple(
    tuple(map(F, row))
    for row in (
        ("0", "13/45", "0", "0", "0", "32/45"),
        ("13/45", "0", "0", "0", "0", "32/45"),
        ("13/45", "0", "0", "0", "1/15", "29/45"),
        ("0", "13/45", "0", "0", "1/15", "29/45"),
        ("13/45", "0", "0", "0", "0", "32/45"),
        ("0", "0", "16/45", "13/45", "16/45", "0"),
    )
)
CANONICAL_LMIN = tuple(map(F, ("1/9", "1/9", "1/9", "1/9", "1/9", "4/9")))
CANONICAL_LMAX = tuple(
    map(F, ("1/18", "1/18", "2/9", "2/9", "2/9", "2/9"))
)
CANONICAL_WITNESSES = tuple(
    tuple(map(F, row))
    for row in (
        ("0", "31/360", "89/360", "89/360", "89/360", "31/180"),
        ("11/180", "0", "49/180", "49/180", "49/180", "11/90"),
        ("0", "1/3", "0", "0", "0", "2/3"),
        ("0", "1/3", "0", "0", "0", "2/3"),
        ("0", "1/3", "0", "0", "0", "2/3"),
        ("0", "0", "1/3", "1/3", "1/3", "0"),
    )
)


def l1(left, right):
    return sum((abs(a - b) for a, b in zip(left, right)), F(0))


def overlap(left, right):
    return sum((min(a, b) for a, b in zip(left, right)), F(0))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    generators = (CLAIMED_LMIN, CLAIMED_LMAX) + WITNESSES
    assert all(sum(row) == 1 and min(row) >= 0 for row in generators)
    assert all(WITNESSES[i][i] == 0 for i in range(N))

    triples = {
        i: sum(1 << j for j in P if j != i) | (1 << R) for i in P
    }
    triple_rows = []
    common = []
    for i, coalition in triples.items():
        x_sum = coalition_sum(CLAIMED_LMIN, coalition)
        z_sum = coalition_sum(CLAIMED_LMAX, coalition)
        witness_sums = [coalition_sum(row, coalition) for row in WITNESSES]
        assert min(witness_sums) >= x_sum
        assert z_sum >= x_sum
        if z_sum == x_sum:
            common.append(coalition)
        triple_rows.append(
            {
                "excluded_P_player": i,
                "coalition_mask": coalition,
                "claimed_lmin_sum": x_sum,
                "claimed_lmax_sum": z_sum,
                "minimum_singleton_witness_sum": min(witness_sums),
            }
        )
    assert len(common) >= 2
    assert l1(CLAIMED_LMIN, CLAIMED_LMAX) == F(31, 45) > F(2, 3)

    # The relaxation is not merely a remote point.  Interpolate each displayed
    # generator with its canonical counterpart.  Endpoint verification plus
    # affinity proves every singleton/triple constraint along the entire ray;
    # the cross-cell signs are unchanged, so the claimed distance is
    # 2/3 + lambda/45 for every lambda in (0,1].
    assert all(
        sum(row) == 1 and row[i] == 0 and min(row) >= 0
        for i, row in enumerate(CANONICAL_WITNESSES)
    )
    canonical_triple_rows = []
    for i, coalition in triples.items():
        x_sum = coalition_sum(CANONICAL_LMIN, coalition)
        z_sum = coalition_sum(CANONICAL_LMAX, coalition)
        witness_sums = [
            coalition_sum(row, coalition) for row in CANONICAL_WITNESSES
        ]
        assert x_sum == z_sum == F(2, 3)
        assert min(witness_sums) >= x_sum
        canonical_triple_rows.append(
            {
                "excluded_P_player": i,
                "coalition_mask": coalition,
                "common_sum": x_sum,
                "minimum_singleton_witness_sum": min(witness_sums),
            }
        )
    canonical_signs = [
        (a > b) - (a < b) for a, b in zip(CANONICAL_LMIN, CANONICAL_LMAX)
    ]
    relaxed_signs = [
        (a > b) - (a < b) for a, b in zip(CLAIMED_LMIN, CLAIMED_LMAX)
    ]
    assert canonical_signs == relaxed_signs
    assert l1(CANONICAL_LMIN, CANONICAL_LMAX) == F(2, 3)
    distance_ray = "2/3 + lambda/45, 0<lambda<=1"

    game = lower_envelope(generators)
    assert game[FULL] == 1
    assert all(game[1 << i] == 0 for i in range(N))
    assert all(
        any(coalition_sum(row, coalition) == game[coalition] for row in generators)
        for coalition in range(1 << N)
    )

    selections = {}
    for mode in ("min", "max"):
        simplex_point, simplex_trace = lex_point_with_trace(N, game, mode)
        independent_point, independent_trace = independent_lex(game, mode)
        assert tuple(simplex_point) == independent_point
        assert simplex_trace == independent_trace
        certificates = all_staged_pinning_certificates(
            game, independent_point, independent_trace, mode
        )
        assert len(certificates) == N
        selections[mode] = {
            "point": independent_point,
            "trace": independent_trace,
            "pinning_certificates": certificates,
        }

    actual_lmin = selections["min"]["point"]
    actual_lmax = selections["max"]["point"]
    assert actual_lmin != CLAIMED_LMIN
    assert actual_lmax != CLAIMED_LMAX
    assert l1(actual_lmin, actual_lmax) == F(4, 9)
    assert overlap(actual_lmin, actual_lmax) == F(7, 9)

    report = {
        "status": "PASS",
        "scope": (
            "exact negative control: the three-triple critical residue does not "
            "replace full staged Lmin/Lmax optimality"
        ),
        "claimed_pair": {
            "lmin": CLAIMED_LMIN,
            "lmax": CLAIMED_LMAX,
            "l1_distance": l1(CLAIMED_LMIN, CLAIMED_LMAX),
            "overlap": overlap(CLAIMED_LMIN, CLAIMED_LMAX),
        },
        "singleton_witnesses": WITNESSES,
        "forced_triple_checks": triple_rows,
        "common_triple_masks": common,
        "arbitrarily_local_relaxation_ray": {
            "canonical_lmin": CANONICAL_LMIN,
            "canonical_lmax": CANONICAL_LMAX,
            "canonical_singleton_witnesses": CANONICAL_WITNESSES,
            "canonical_triple_checks": canonical_triple_rows,
            "interpolation": (
                "componentwise (1-lambda)*canonical + lambda*displayed for "
                "Lmin, Lmax, and each indexed singleton witness"
            ),
            "claimed_l1_distance": distance_ray,
            "status": (
                "all simplex, zero-coordinate, triple-dominance, and common-"
                "triple constraints hold for every 0<=lambda<=1"
            ),
        },
        "closed_game": {
            "characteristic_function": game,
            "singleton_normalized": True,
            "exactness_certificate": (
                "finite lower envelope; every coalition is attained by a displayed generator"
            ),
        },
        "recomputed": {
            "lmin": selections["min"],
            "lmax": selections["max"],
            "l1_distance": l1(actual_lmin, actual_lmax),
            "overlap": overlap(actual_lmin, actual_lmax),
            "independent_exact_selection_encodings": 2,
            "complete_staged_pinning_certificates": 12,
        },
        "interpretation": (
            "singleton exactification plus the three critical triples is still a "
            "relaxation; exact closure changes the later staged selections and "
            "moves the true pair safely inside the 2/3 boundary"
        ),
    }
    rendered = json.dumps(encode(report), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
