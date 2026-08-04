"""Exact audit of cover-free leximin face ascent and positive variation.

The proof is convex-geometric and human.  This script checks the identities
on two unrelated rational allocation segments and the three defining
exact-game mechanisms; it is not independent proof evidence.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope as five_lower_envelope,
)
from verify_three_trace_half_integral_family import (
    lower_envelope as three_lower_envelope,
    mask,
    vertices as three_vertices,
)
from verify_two_poorer_rich_family import (
    generators as cosingleton_generators,
    lower_envelope as cosingleton_lower_envelope,
)


def coalition_sum(point, coalition):
    return sum(
        (point[i] for i in range(len(point)) if coalition >> i & 1), F(0)
    )


def positive_variation(point, phi, players):
    return sum((max(point[i] - phi[i], F(0)) for i in players), F(0))


def interval_audit(
    name,
    points,
    phi,
    root,
    values=None,
    certify_segment_leximin=False,
):
    points = [tuple(F(value) for value in point) for point in points]
    phi = tuple(F(value) for value in phi)
    n = len(phi)
    full = (1 << n) - 1
    if any(sum(point, F(0)) != sum(phi, F(0)) for point in points):
        raise AssertionError(f"{name}: allocation set is not efficient")
    poor = [i for i in range(n) if not (root >> i & 1)]

    leximin_certificate = None
    if certify_segment_leximin:
        if len(points) != 2 or points[0] != phi:
            raise AssertionError(f"{name}: segment certificate needs (phi,z)")
        minimum = min(phi)
        losing_minima = [
            i for i in range(n)
            if phi[i] == minimum and points[1][i] < phi[i]
        ]
        if not losing_minima:
            raise AssertionError(f"{name}: no minimum coordinate decreases")
        # Every nontrivial point of [phi,z] strictly lowers one coordinate
        # that is globally minimal at phi.  Its minimum is therefore below
        # min(phi), which proves phi is the unique leximin point of the whole
        # segment without sampling parameter values.
        leximin_certificate = {
            "type": "global-minimum-coordinate-strictly-decreases",
            "minimum": str(minimum),
            "losing_minimum_coordinates": [i + 1 for i in losing_minima],
            "unique_leximin_on_segment": True,
        }

    def face_deficit(coalition):
        return coalition_sum(phi, coalition) - min(
            coalition_sum(point, coalition) for point in points
        )

    interval = [coalition for coalition in range(1 << n) if coalition & root == root]
    face_maximum = max(face_deficit(coalition) for coalition in interval)
    variation_maximum = max(positive_variation(point, phi, poor) for point in points)
    if face_maximum != variation_maximum:
        raise AssertionError(f"{name}: positive-variation duality failed")

    terminals = [coalition for coalition in interval if face_deficit(coalition) == face_maximum]
    maximizing_points = [
        point for point in points
        if positive_variation(point, phi, poor) == variation_maximum
    ]
    sign_cells = []
    for point in maximizing_points:
        negative = {i for i in poor if point[i] < phi[i]}
        zero = {i for i in poor if point[i] == phi[i]}
        predicted = []
        for coalition in interval:
            selected = {i for i in poor if coalition >> i & 1}
            if negative <= selected <= negative | zero:
                predicted.append(coalition)
                if coalition not in terminals:
                    raise AssertionError(f"{name}: predicted sign cell is not terminal")
                if coalition_sum(point, coalition) != min(
                    coalition_sum(candidate, coalition) for candidate in points
                ):
                    raise AssertionError(f"{name}: maximizing point does not exactify cell")
        sign_cells.append(
            {
                "point": [str(value) for value in point],
                "negative_poor_coordinates": [i + 1 for i in sorted(negative)],
                "zero_poor_coordinates": [i + 1 for i in sorted(zero)],
                "predicted_terminal_masks": predicted,
            }
        )

    if values is not None:
        game_slacks = [
            coalition_sum(phi, coalition) - values[coalition]
            for coalition in interval
        ]
        point_face_slacks = [face_deficit(coalition) for coalition in interval]
        # Defining points need not exhaust the full game core, so their face
        # deficits are certified lower bounds.  Equality is asserted only
        # when it actually holds for the supplied representation.
        representation_exact_on_interval = game_slacks == point_face_slacks
    else:
        representation_exact_on_interval = True

    return {
        "name": name,
        "player_count": n,
        "root_mask": root,
        "root_face_deficit": str(face_deficit(root)),
        "interval_maximum": str(face_maximum),
        "positive_variation_maximum": str(variation_maximum),
        "terminal_masks": terminals,
        "sign_cells": sign_cells,
        "leximin_certificate": leximin_certificate,
        "defining_representation_exact_on_interval": representation_exact_on_interval,
        "grand_coalition_mask": full,
    }


def audits():
    segment_four = interval_audit(
        "four_player_allocation_segment",
        ((F(1), F(1), F(2), F(2)),
         (F(0), F(3), F(3, 2), F(3, 2))),
        (F(1), F(1), F(2), F(2)),
        mask((2, 3)),
        certify_segment_leximin=True,
    )
    segment_five = interval_audit(
        "five_player_multi_loss_segment",
        ((F(1), F(1), F(1), F(2), F(2)),
         (F(0), F(0), F(4), F(3, 2), F(3, 2))),
        (F(1), F(1), F(1), F(2), F(2)),
        mask((3, 4)),
        certify_segment_leximin=True,
    )

    five_points = BASE_GENERATORS
    five = interval_audit(
        "five_player_exact_game_defining_points",
        five_points,
        PHI_BASE,
        mask((2, 4)),
        five_lower_envelope(five_points),
    )

    three_points = three_vertices(1, 2, 2)
    three_game = three_lower_envelope(three_points)
    three = interval_audit(
        "seven_player_three_trace_core_vertices",
        three_points,
        tuple([F(1), F(1)] + [F(2)] * 5),
        mask(range(2, 7)),
        three_game.v,
    )

    m, h = 2, 4
    scale = (h - 2) * (h - 3)
    cosingleton_points = cosingleton_generators(m, h)
    cosingleton = interval_audit(
        "six_player_cosingleton_defining_points",
        cosingleton_points,
        tuple([F(scale)] * m + [F(2 * scale)] * h),
        mask(range(m, m + h)),
        cosingleton_lower_envelope(cosingleton_points),
    )
    return [segment_four, segment_five, five, three, cosingleton]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "status": "leximin face ascent geometry audited",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "audits": audits(),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
