"""Exact verification of the structural content of the five-player witness.

Both endpoint games have large cores, but Lmin differs from Lmax in the base
game.  Lmax is constant across the bump.  An exact enumeration of all ordered
payoff partitions proves that the base game is not an exact partition game at
any core allocation, while the endpoint is one.  Thus largeness alone does not
imply the exact-partition property or the existence of a Lorenz-dominating core
element, and dimension five is sharp for that classification as well as for
Lmin coalitional monotonicity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3

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


def ordered_partitions(players):
    """Yield every ordered set partition, deterministically and once each."""
    players = tuple(players)
    if not players:
        yield ()
        return
    first = players[0]
    for partition in ordered_partitions(players[1:]):
        for position in range(len(partition) + 1):
            yield (
                partition[:position]
                + ((first,),)
                + partition[position:]
            )
        for block_index, block in enumerate(partition):
            enlarged = tuple(sorted((first,) + block))
            yield (
                partition[:block_index]
                + (enlarged,)
                + partition[block_index + 1:]
            )


def exact_partition_report(game):
    """Test every possible payoff-stratum chain in exact rational LRA.

    Blocks are ordered from poorest to richest.  On each chain, core
    feasibility, equality inside blocks, tightness of every richer suffix, and
    strict inter-block gaps are imposed directly.  Z3's linear-rational engine
    handles the strict inequalities without a numerical tolerance.
    """
    n, full, values = game.n, game.N, game.v
    partitions = list(ordered_partitions(range(n)))
    if len(partitions) != 541 or len(set(partitions)) != 541:
        raise RuntimeError("ordered-partition generator is not a 541-chain bijection")
    coordinates = [z3.Real(f"ep_x_{player}") for player in range(n)]
    base = z3.Solver()
    base.add(z3.Sum(coordinates) == z3.RealVal(str(values[full])))
    for coalition in range(1, full):
        base.add(
            z3.Sum([
                coordinates[player]
                for player in range(n)
                if coalition >> player & 1
            ]) >= z3.RealVal(str(values[coalition]))
        )
    checked = 0
    strictly_feasible = 0
    witness = None
    for partition in partitions:
        checked += 1
        block_count = len(partition)
        base.push()
        for block in partition:
            representative = block[0]
            for player in block[1:]:
                base.add(coordinates[player] == coordinates[representative])
        for lower, upper in zip(partition, partition[1:]):
            base.add(coordinates[lower[0]] < coordinates[upper[0]])
        for boundary in range(block_count - 1):
            richer = {
                player
                for block in partition[boundary + 1:]
                for player in block
            }
            coalition = sum(1 << player for player in richer)
            base.add(
                z3.Sum([coordinates[player] for player in richer])
                == z3.RealVal(str(values[coalition]))
            )
        status = base.check()
        if status == z3.unknown:
            raise RuntimeError(
                f"exact-partition query undecided for chain {partition}: "
                f"{base.reason_unknown()}"
            )
        if status == z3.unsat:
            base.pop()
            continue
        strictly_feasible += 1
        model = base.model()

        def rational_string(expression):
            value = model.eval(expression, model_completion=True)
            numerator = value.numerator_as_long()
            denominator = value.denominator_as_long()
            return (
                str(numerator)
                if denominator == 1
                else f"{numerator}/{denominator}"
            )

        if witness is None:
            witness = {
                "strata_poorest_to_richest": [
                    [player + 1 for player in block] for block in partition
                ],
                "allocation": [
                    rational_string(value) for value in coordinates
                ],
                "strict_gaps": "verified exactly",
            }
        base.pop()
    return {
        "ordered_partitions_checked": checked,
        "total_ordered_partitions": 541,
        "strictly_feasible_chains": strictly_feasible,
        "is_exact_partition_game": witness is not None,
        "witness": witness,
    }


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

    # The largeness verifier sends progress to stderr; stdout remains a single
    # valid JSON document even when progress reporting is enabled.
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
    exact_partition_reports = [exact_partition_report(game) for game in games]
    if exact_partition_reports[0]["ordered_partitions_checked"] != 541:
        raise RuntimeError("base exact-partition enumeration was incomplete")
    if exact_partition_reports[0]["is_exact_partition_game"]:
        raise RuntimeError("base game unexpectedly has an exact-partition allocation")
    if not exact_partition_reports[1]["is_exact_partition_game"]:
        raise RuntimeError("endpoint exact-partition witness was not recovered")

    payload = {
        "status": "five-player large-core exact-partition separation verified",
        "arithmetic": (
            "exact rational staged LPs and complete exact acceptable-vertex "
            "enumeration; exact linear-rational ordered-partition queries"
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
            "exact_partition_game": False,
            "exact_partition_enumeration": exact_partition_reports[0],
            "lorenz_dominating_core_element_exists": False,
        },
        "endpoint": {
            "lmin": as_strings(lmin[1]),
            "lmax": as_strings(lmax[1]),
            "large_core_certificate": large_core_reports[1],
            "exact_partition_at_lmin": True,
            "exact_partition_game": True,
            "exact_partition_enumeration": exact_partition_reports[1],
            "lorenz_dominating_core_element_exists": True,
        },
        "lmax_constant_across_bump": True,
        "conclusion": (
            "large-core status alone does not force the exact-partition "
            "property, a Lorenz-dominating core element, or equality of Lmin "
            "and Lmax; the through-four-player classification is sharp at five"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
