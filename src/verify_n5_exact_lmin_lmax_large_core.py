"""Exact verification of the structural content of the five-player witness.

Both endpoint games have large cores, but Lmin differs from Lmax in the base
game.  Lmax is constant across the bump.  Thus largeness alone does not imply
the exact-partition property witnessed at Lmin, and dimension five is sharp
for that classification as well as for Lmin coalitional monotonicity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from largeness_exact import verify_large_cores_exact
from leximin import leximax_core_exact, leximin_core_exact
from tugame import Game
from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    ENDPOINT_GENERATORS,
    PHI_BASE,
    PHI_ENDPOINT,
    S,
    lower_envelope,
    members,
)


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


def as_strings(vector):
    return [str(value) for value in vector]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    base_values = lower_envelope(BASE_GENERATORS)
    endpoint_values = lower_envelope(ENDPOINT_GENERATORS)
    games = [Game(5, base_values), Game(5, endpoint_values)]
    lmin = [tuple(leximin_core_exact(game)) for game in games]
    lmax = [tuple(leximax_core_exact(game)) for game in games]
    if lmin != [PHI_BASE, PHI_ENDPOINT]:
        raise RuntimeError(f"unexpected Lmin allocations: {lmin}")
    if lmax != [PHI_ENDPOINT, PHI_ENDPOINT]:
        raise RuntimeError(f"unexpected Lmax allocations: {lmax}")

    large_core_reports = verify_large_cores_exact(
        [base_values, endpoint_values],
        5,
        progress=not args.quiet,
    )
    richer_suffix = (1 << 2) | (1 << 4)  # {3,5}, tied richest base players.
    base_suffix_payoff = games[0].xS(lmin[0], richer_suffix)
    base_suffix_value = games[0].v[richer_suffix]
    if not base_suffix_payoff > base_suffix_value:
        raise RuntimeError("the base game does not exhibit strict suffix slack")

    payload = {
        "status": "five-player large-core Lmin/Lmax separation verified",
        "arithmetic": (
            "exact rational staged LPs and complete exact acceptable-vertex "
            "enumeration"
        ),
        "target": members(S),
        "base": {
            "lmin": as_strings(lmin[0]),
            "lmax": as_strings(lmax[0]),
            "large_core_certificate": large_core_reports[0],
            "slack_richer_suffix": [3, 5],
            "suffix_payoff": str(base_suffix_payoff),
            "suffix_value": str(base_suffix_value),
            "exact_partition_at_lmin": False,
        },
        "endpoint": {
            "lmin": as_strings(lmin[1]),
            "lmax": as_strings(lmax[1]),
            "large_core_certificate": large_core_reports[1],
            "exact_partition_at_lmin": True,
        },
        "lmax_constant_across_bump": True,
        "conclusion": (
            "large-core status alone does not force Lmin to have the exact-"
            "partition property or to equal Lmax; the through-four-player "
            "classification is sharp at five"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
