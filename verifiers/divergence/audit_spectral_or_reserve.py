#!/usr/bin/env python3
r"""Exact controls for the spectral-or-reserve alternative (PXC73).

On the ordered saturated arm the packet-side reserve and the sharpened
spectral-anchor bound are complementary in every audited and designed
instance: the reserve closes all archived six-player roots while the
spectral bound fails on twenty of them, and the spectral bound closes every
designed packet-side violation in dimensions seven through nine, where the
packet violation grows with the dimension.  Hill-climbing the combined
failure margin plateaus at the exact double boundary, whose instances
realize the sharp-family selector profile.  This driver replays the archive
disjunction, a fixed parametric family grid, and the plateau witnesses.
No universal theorem is asserted; the disjunction is the live conjecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import records  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_saturated_unit_exchange_boundary import (  # noqa: E402
    leximax_core_certified,
)
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from certified_leximin import leximin_core_certified  # noqa: E402
from leximin import leximin_core_exact  # noqa: E402
from tugame import Game  # noqa: E402


FAMILY = (
    ((4, 4, 4), 7, (1, 1, 3), "-1/5", "9/5", "23/10"),
    ((4, 4, 4), 8, (1, 1, 2), "0", "0", "0"),
    ((4, 4, 4), 9, (1, 1, 1), "0", "0", "0"),
    ((6, 3, 3), 8, (1, 1, 2), "-5/7", "2", "2"),
    ((4, 4, 4, 4), 11, (1, 1, 3), "-3/7", "29/14", "18/7"),
    ((4, 4, 4, 4), 12, (1, 1, 2), "0", "0", "0"),
    ((5, 5, 5), 8, (1, 1, 1, 4), "-1/14", "7/2", "69/14"),
    ((5, 5, 5, 5), 13, (1, 1, 1, 4), "-1", "4", "5"),
    ((5, 5, 5, 5), 15, (1, 1, 1, 2), "0", "0", "0"),
    ((8, 4, 4, 4), 15, (1, 1, 1, 2), "-11/13", "0", "3"),
    ((6, 6, 6, 6, 6), 25, (1, 1, 1, 2), "0", "1", "3/2"),
    ((6, 6, 6, 6, 6), 23, (1, 1, 1, 4), "-4/7", "24/7", "31/7"),
    ((6, 6, 6, 6, 6), 24, (1, 1, 1, 1, 2), "0", "0", "0"),
    ((6, 6, 6, 6, 6), 22, (1, 1, 1, 1, 4), "-4/3", "14/3", "17/3"),
    ((6, 6, 6, 6, 6, 6), 30, (1, 1, 1, 1, 2), "0", "0", "0"),
)

PLATEAU = (
    ((1, 0, 8, 2, 0, 1, 0), (0, 4, 0, 0, 4, 0, 4)),
    ((8, 2, 1, 0, 0, 0, 1), (0, 0, 0, 4, 4, 4, 0)),
)


def selectors(values, n):
    game = Game(n, list(values))
    x, _certificate = leximin_core_certified(game)
    if x is None:
        x = leximin_core_exact(game)
    z = leximax_core_certified(game)
    return tuple(F(q) for q in x), tuple(F(q) for q in z)


def margins(values, x, z):
    """Worst packet margin over ordered saturated roots plus spectral margin."""
    n = len(x)
    total = sum(x, F(0))
    roots = ordered_saturated_roots(values, x, z)
    if not roots:
        return None
    packet = None
    for root, gainers, _outsiders, decoration in roots:
        g = len(gainers)
        gain = sum(z[p] - x[p] for p in gainers)
        maximum = max(z[p] - x[p] for p in gainers)
        penalty = gain - maximum - (x[root] - z[root])
        mu = F((g - 1) * n, g * (n - g))
        slack = (F(n, g * (n - g)) - F(n, (n * n) // 4)) * total
        value = mu * decoration + slack - penalty
        if packet is None or value < packet:
            packet = value
    spec = spectral_decomposition("q", values, x, z)
    spectral = (
        F(spec["sharpened_spectral_bound_ratio"]) - F(spec["target_ratio"])
    ) * total
    overlap = sum(min(a, b) for a, b in zip(x, z))
    target = F(n, (n * n) // 4) * total
    return {
        "packet_margin": packet,
        "spectral_margin": spectral,
        "target_margin": overlap - target,
        "total": total,
    }


def family_instance(a, H, w):
    g, k = len(a), len(w)
    generator_one = tuple([F(0)] + [F(q) for q in a] + [F(0)] * k)
    generator_two = tuple([F(H)] + [F(0)] * g + [F(q) for q in w])
    if sum(generator_one, F(0)) != sum(generator_two, F(0)):
        raise AssertionError("family instance lost its common total")
    return (generator_one, generator_two)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            row = margins(values, x, z)
            if row is None:
                continue
            if max(row["packet_margin"], row["spectral_margin"]) < 0:
                raise AssertionError("archive disjunction failed")
            archive.append(
                {
                    "source": source.name,
                    "trail": trail,
                    "packet_margin_ratio": str(
                        row["packet_margin"] / row["total"]
                    ),
                    "spectral_margin_ratio": str(
                        row["spectral_margin"] / row["total"]
                    ),
                }
            )
    spectral_failures = [
        row for row in archive if F(row["spectral_margin_ratio"]) < 0
    ]
    for row in spectral_failures:
        # every archived spectral failure is paid exactly by the normalized
        # six-player g=2 cardinality slack T/12
        if F(row["packet_margin_ratio"]) != F(1, 12):
            raise AssertionError(
                "archived spectral failure lost its uniform packet margin"
            )

    family = []
    for a, H, w, packet, spectral, target in FAMILY:
        generators = family_instance(a, H, w)
        n = len(generators[0])
        values = lower_envelope(generators)
        x, z = selectors(values, n)
        row = margins(values, x, z)
        if row is None:
            raise AssertionError("family instance lost its ordered saturated root")
        observed = (
            str(row["packet_margin"]),
            str(row["spectral_margin"]),
            str(row["target_margin"]),
        )
        if observed != (packet, spectral, target):
            raise AssertionError(
                f"family instance {(a, H, w)} drifted: {observed!r}"
            )
        if max(row["packet_margin"], row["spectral_margin"]) < 0:
            raise AssertionError("family disjunction failed")
        if row["target_margin"] < 0:
            raise AssertionError("family instance violated the hybrid target")
        family.append(
            {
                "a": list(a),
                "H": H,
                "w": list(w),
                "n": n,
                "packet_margin": packet,
                "spectral_margin": spectral,
                "target_margin": target,
            }
        )

    plateau = []
    for generators in PLATEAU:
        generators = tuple(
            tuple(F(q) for q in generator) for generator in generators
        )
        n = len(generators[0])
        values = lower_envelope(generators)
        x, z = selectors(values, n)
        row = margins(values, x, z)
        if row is None:
            raise AssertionError("plateau witness lost its ordered saturated root")
        if row["packet_margin"] != 0 or row["spectral_margin"] != 0:
            raise AssertionError("plateau witness left the double boundary")
        if row["target_margin"] < 0:
            raise AssertionError("plateau witness violated the hybrid target")
        plateau.append(
            {
                "generators": [
                    [str(q) for q in generator] for generator in generators
                ],
                "x": [str(q) for q in x],
                "z": [str(q) for q in z],
                "target_margin": str(row["target_margin"]),
            }
        )

    summary = {
        "archive_ordered_saturated_games": len(archive),
        "archive_disjunction": len(archive),
        "archive_spectral_failures": len(spectral_failures),
        "archive_minimum_spectral_margin_ratio": str(
            min(F(row["spectral_margin_ratio"]) for row in archive)
        ),
        "family_instances": len(family),
        "family_packet_violations": sum(
            F(row["packet_margin"]) < 0 for row in family
        ),
        "family_double_boundary": sum(
            F(row["packet_margin"]) == 0 and F(row["spectral_margin"]) == 0
            for row in family
        ),
        "plateau_witnesses": len(plateau),
        "plateau_target_margins": [row["target_margin"] for row in plateau],
    }
    expected = {
        "archive_ordered_saturated_games": 89,
        "archive_disjunction": 89,
        "archive_spectral_failures": 20,
        "archive_minimum_spectral_margin_ratio": "-2/21",
        "family_instances": 15,
        "family_packet_violations": 8,
        "family_double_boundary": 6,
        "plateau_witnesses": 2,
        "plateau_target_margins": ["0", "0"],
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(f"summary[{key!r}] = {summary[key]!r} != {value!r}")

    payload = {
        "claim": (
            "packet reserve and sharpened spectral anchor are complementary "
            "on every audited and designed ordered saturated root; the "
            "double boundary realizes the sharp-family selector profile"
        ),
        "summary": summary,
        "archive_rows": archive,
        "family_rows": family,
        "plateau_rows": plateau,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
