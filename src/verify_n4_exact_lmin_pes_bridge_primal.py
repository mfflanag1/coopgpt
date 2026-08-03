"""Independent primal-direction verifier for the Lmin/Lmax bridge.

This checker deliberately does not use the KKT multipliers or complementarity
encoding in ``verify_n4_exact_lmin_pes_bridge.py``.  Instead it enumerates the
set A of core inequalities tight at the proposed Lmin point phi.  The tangent
cone is then given definitionally by

    d(N) = 0,  d(T) >= 0 for T in A.

For each payoff stratum, leximin optimality says that no direction can keep
all players in the current stratum weakly above their level while raising one
of them, after earlier strata have been fixed.  These are primal feasibility
queries, not dual certificates.

For every tangent pattern passing those queries, a second exact-linear system
asks whether nonnegative slacks and exact-face witnesses realize it.  Inactive
slacks and strict payoff gaps are normalized to at least one by positive
homogeneity.  The enumeration proves that every realizable pattern has every
richer-player suffix tight.  It also emits a concrete exact game for every
realizable ordered stratum composition.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import z3


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


def members(coalition, player_count):
    return [i for i in range(player_count) if coalition >> i & 1]


def coalition_sum(vector, coalition, player_count):
    return z3.Sum([vector[i] for i in members(coalition, player_count)])


def compositions(total):
    for cuts in itertools.product((0, 1), repeat=total - 1):
        parts = []
        previous = 0
        for position, cut in enumerate(cuts, 1):
            if cut:
                parts.append(position - previous)
                previous = position
        parts.append(total - previous)
        yield parts


def blocks_for(composition):
    blocks = []
    start = 0
    for size in composition:
        blocks.append(list(range(start, start + size)))
        start += size
    return blocks


def richer_suffixes(blocks):
    return [
        sum(1 << i for block in blocks[boundary + 1:] for i in block)
        for boundary in range(len(blocks) - 1)
    ]


def direction_exists(player_count, active, earlier, current, raised):
    """Whether a local core direction lexicographically improves one player."""
    direction = [z3.Real(f"direction_{i}") for i in range(player_count)]
    solver = z3.Solver()
    solver.add(z3.Sum(direction) == 0)
    for coalition in active:
        solver.add(coalition_sum(direction, coalition, player_count) >= 0)
    for i in earlier:
        solver.add(direction[i] == 0)
    for i in current:
        solver.add(direction[i] >= 0)
    # Homogeneity replaces strict positivity by a unit improvement.
    solver.add(direction[raised] >= 1)
    return solver.check() == z3.sat


def tangent_is_leximin(player_count, composition, active):
    earlier = []
    for current in blocks_for(composition):
        for raised in current:
            if direction_exists(
                player_count,
                active,
                earlier,
                current,
                raised,
            ):
                return False
        earlier.extend(current)
    return True


def realization_solver(player_count, composition, active):
    full = (1 << player_count) - 1
    coalitions = list(range(1, full))
    blocks = blocks_for(composition)
    solver = z3.Solver()
    phi = [z3.Real(f"phi_{i}") for i in range(player_count)]
    slack = {coalition: z3.Real(f"slack_{coalition}") for coalition in coalitions}
    solver.add(*[value >= 0 for value in phi])
    for coalition in coalitions:
        if coalition in active:
            solver.add(slack[coalition] == 0)
        else:
            solver.add(slack[coalition] >= 1)
    for i in range(player_count):
        solver.add(slack[1 << i] == phi[i])

    levels = []
    for block_index, block in enumerate(blocks):
        level = z3.Real(f"level_{block_index}")
        levels.append(level)
        solver.add(*[phi[i] == level for i in block])
        if block_index:
            solver.add(level >= levels[block_index - 1] + 1)

    # Exactness from its definition: every proper coalition has an attaining
    # core displacement from phi.
    for face in coalitions:
        displacement = [
            z3.Real(f"face_{face}_d_{i}") for i in range(player_count)
        ]
        solver.add(z3.Sum(displacement) == 0)
        solver.add(
            coalition_sum(displacement, face, player_count) == -slack[face]
        )
        for coalition in coalitions:
            solver.add(
                coalition_sum(displacement, coalition, player_count)
                >= -slack[coalition]
            )
    return solver, phi, slack


def rational_string(model, expression):
    value = model.eval(expression, model_completion=True)
    if not z3.is_rational_value(value):
        raise RuntimeError(f"nonrational model value: {value}")
    numerator = value.numerator_as_long()
    denominator = value.denominator_as_long()
    return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"


def realization_record(player_count, active, phi, slack, model):
    full = (1 << player_count) - 1
    return {
        "phi": [rational_string(model, value) for value in phi],
        "proper_coalition_values": {
            str(coalition): rational_string(
                model,
                coalition_sum(phi, coalition, player_count) - slack[coalition],
            )
            for coalition in range(1, full)
        },
        "grand_value": rational_string(model, z3.Sum(phi)),
        "tight_coalitions": sorted(active),
    }


def candidate_active_sets(player_count, composition):
    full = (1 << player_count) - 1
    singletons = {1 << i for i in range(player_count)}
    nonsingletons = [
        coalition for coalition in range(1, full) if coalition not in singletons
    ]
    first_block_singletons = {1 << i for i in blocks_for(composition)[0]}
    # Equal singleton slacks within the first block mean that either its whole
    # block is tight at level zero or no singleton is tight.  Higher-stratum
    # singleton inequalities can never be tight.
    for zero_first_level in (False, True):
        fixed_singletons = first_block_singletons if zero_first_level else set()
        for bits in range(1 << len(nonsingletons)):
            active = set(fixed_singletons)
            active.update(
                coalition
                for index, coalition in enumerate(nonsingletons)
                if bits >> index & 1
            )
            yield active


def verify_case(player_count, composition):
    blocks = blocks_for(composition)
    suffixes = richer_suffixes(blocks)
    counts = {
        "active_sets_enumerated": 0,
        "leximin_tangent_patterns": 0,
        "exact_realizations_checked": 0,
    }
    witness = None
    for active in candidate_active_sets(player_count, composition):
        counts["active_sets_enumerated"] += 1
        if not tangent_is_leximin(player_count, composition, active):
            continue
        counts["leximin_tangent_patterns"] += 1
        needs_theorem_check = any(suffix not in active for suffix in suffixes)
        if witness is not None and not needs_theorem_check:
            continue
        solver, phi, slack = realization_solver(
            player_count,
            composition,
            active,
        )
        counts["exact_realizations_checked"] += 1
        status = solver.check()
        if status == z3.unknown:
            raise RuntimeError(
                f"unknown realization status at n={player_count}, "
                f"composition={composition}, active={sorted(active)}"
            )
        if status == z3.sat:
            if needs_theorem_check:
                raise RuntimeError(
                    "primal-direction counterexample found: "
                    f"n={player_count}, composition={composition}, "
                    f"active={sorted(active)}"
                )
            if witness is None:
                witness = realization_record(
                    player_count,
                    active,
                    phi,
                    slack,
                    solver.model(),
                )
    return {
        "payoff_stratum_composition": composition,
        **counts,
        "realizable": witness is not None,
        "explicit_exact_witness": witness,
        "positive_richer_suffix_slack": "impossible",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = []
    for player_count in range(2, 5):
        cases = []
        for composition in compositions(player_count):
            if len(composition) == 1:
                continue
            print(
                f"checking n={player_count}, composition={composition}",
                file=sys.stderr,
                flush=True,
            )
            cases.append(verify_case(player_count, composition))
        results.append({"player_count": player_count, "cases": cases})
    payload = {
        "status": "independent primal-direction Lmin/Lmax bridge verified",
        "arithmetic": "Z3 exact linear rational feasibility",
        "independence": (
            "enumerates tight sets and excludes primal leximin-improving "
            "directions; uses no KKT multipliers and no complementarity"
        ),
        "results": results,
        "conclusion": (
            "every richer-player suffix at a strict Lmin payoff gap is tight "
            "in every singleton-normalized exact game through four players"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
