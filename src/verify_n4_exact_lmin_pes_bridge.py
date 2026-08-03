"""Exact symbolic certificate for the Lmin/PES bridge through four players.

For a singleton-normalized exact game and its Lmin point phi, write

    s(T) = phi(T) - v(T) >= 0.

Exactness is encoded from the definition: for every proper coalition C there
is a displacement d^C with total zero, d^C(C)=-s(C), and
d^C(T)>=-s(T) for every proper T.  The ordered payoff strata of phi have one
of the seven nontrivial compositions of four.  At each progressive-filling
stage, exact KKT multipliers certify both the common-level optimum and the
individual pinning of every player in the current stratum.

The query asks whether, at some strict payoff gap, the coalition of all richer
players can have positive slack.  Z3's exact linear-rational solver proves the
query infeasible for all seven compositions.  Hence every richer suffix is
tight.  Its core inequality bounds every allocation's corresponding richest
coordinate sum from below, so phi Lorenz-dominates the entire core and equals
both ordinary Lmin and Lmax (and PES on egalitarian-stable games).

The script also runs two negative controls.  Removing the exact-face witnesses
or removing the individual-pinning duals makes at least one query satisfiable.
"""
from __future__ import annotations

import itertools
import json
import sys

import z3


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


def members(coalition, player_count):
    return [i for i in range(player_count) if coalition >> i & 1]


def coalition_sum(vector, coalition, player_count):
    selected = [vector[i] for i in members(coalition, player_count)]
    return z3.Sum(selected) if selected else z3.RealVal(0)


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


def add_stage_dual(
    solver,
    *,
    tag,
    slack,
    free,
    earlier,
    current,
    player_count,
    coalitions,
    objective_player=None,
):
    """Add exact KKT conditions at phi for one minimization LP.

    objective_player=None certifies max min_{i in free} x_i.
    objective_player=i certifies that player i cannot rise after the common
    level and all earlier coordinates have been fixed.
    """
    lambdas = {
        coalition: z3.Real(f"lambda_{tag}_{coalition}")
        for coalition in coalitions
    }
    floors = {i: z3.Real(f"floor_{tag}_{i}") for i in free}
    efficiency = z3.Real(f"efficiency_{tag}")
    pins = {i: z3.Real(f"pin_{tag}_{i}") for i in earlier}

    solver.add(*[value >= 0 for value in lambdas.values()])
    solver.add(*[value >= 0 for value in floors.values()])
    for i in free:
        if i not in current:
            solver.add(floors[i] == 0)
    for coalition in coalitions:
        # Complementarity at phi: a used core inequality must be tight.
        solver.add(z3.Or(lambdas[coalition] == 0, slack[coalition] == 0))

    if objective_player is None:
        # Stationarity in the common-level variable.
        solver.add(z3.Sum([floors[i] for i in free]) == 1)

    for i in range(player_count):
        stationarity = -(1 if objective_player == i else 0)
        stationarity -= z3.Sum([
            lambdas[coalition]
            for coalition in coalitions
            if coalition >> i & 1
        ])
        stationarity += efficiency
        if i in free:
            stationarity -= floors[i]
        if i in earlier:
            stationarity += pins[i]
        solver.add(stationarity == 0)


def build_query(
    player_count,
    composition,
    *,
    exact_faces=True,
    individual_pins=True,
    require_positive_suffix=True,
):
    solver = z3.Solver()
    full = (1 << player_count) - 1
    coalitions = list(range(1, full))
    blocks = []
    start = 0
    for size in composition:
        blocks.append(list(range(start, start + size)))
        start += size

    phi = [z3.Real(f"phi_{i}") for i in range(player_count)]
    slack = {
        coalition: z3.Real(f"slack_{coalition}")
        for coalition in coalitions
    }
    solver.add(*[value >= 0 for value in phi])
    solver.add(*[value >= 0 for value in slack.values()])
    # Singleton normalization v({i})=0.
    for i in range(player_count):
        solver.add(slack[1 << i] == phi[i])

    levels = []
    for block_index, block in enumerate(blocks):
        level = z3.Real(f"level_{block_index}")
        levels.append(level)
        solver.add(*[phi[i] == level for i in block])
        if block_index:
            # Positive homogeneity lets the smallest strict gap be scaled to 1.
            solver.add(level >= levels[block_index - 1] + 1)

    if exact_faces:
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

    earlier = []
    for stage, block in enumerate(blocks):
        free = [
            i
            for later_stage in range(stage, len(blocks))
            for i in blocks[later_stage]
        ]
        current = set(block)
        add_stage_dual(
            solver,
            tag=f"stage_{stage}_level",
            slack=slack,
            free=free,
            earlier=earlier,
            current=current,
            player_count=player_count,
            coalitions=coalitions,
        )
        if individual_pins:
            for i in block:
                add_stage_dual(
                    solver,
                    tag=f"stage_{stage}_player_{i}",
                    slack=slack,
                    free=free,
                    earlier=earlier,
                    current=current,
                    player_count=player_count,
                    coalitions=coalitions,
                    objective_player=i,
                )
        earlier.extend(block)

    richer_suffixes = []
    for boundary in range(len(blocks) - 1):
        coalition = sum(
            1 << i
            for later_stage in range(boundary + 1, len(blocks))
            for i in blocks[later_stage]
        )
        richer_suffixes.append(coalition)
    if require_positive_suffix:
        solver.add(z3.Or(*[slack[coalition] > 0 for coalition in richer_suffixes]))
    return solver, richer_suffixes


def main():
    theorem_results = []
    compositions_by_size = {}
    for player_count in range(2, 5):
        nontrivial = [c for c in compositions(player_count) if len(c) > 1]
        compositions_by_size[player_count] = nontrivial
        cases = []
        for composition in nontrivial:
            base_solver, _ = build_query(
                player_count,
                composition,
                require_positive_suffix=False,
            )
            base_status = base_solver.check()
            if base_status not in (z3.sat, z3.unsat):
                raise RuntimeError(
                    f"undecided base stratum system for {player_count}, "
                    f"{composition}: {base_status}"
                )
            solver, suffixes = build_query(player_count, composition)
            status = solver.check()
            if status != z3.unsat:
                raise RuntimeError(
                    f"{player_count}-player bridge failed for composition "
                    f"{composition}: {status}"
                )
            cases.append({
                "payoff_stratum_composition": composition,
                "stratum_system": (
                    "feasible" if base_status == z3.sat else "infeasible"
                ),
                "richer_suffixes": suffixes,
                "positive_suffix_slack_query": (
                    "unsatisfiable (nonvacuous)"
                    if base_status == z3.sat
                    else "unsatisfiable because the stratum pattern is impossible"
                ),
            })
        theorem_results.append({"player_count": player_count, "cases": cases})

    controls = {}
    for name, options in (
        ("omit_exact_faces", {"exact_faces": False}),
        ("omit_individual_pins", {"individual_pins": False}),
    ):
        satisfiable = []
        for player_count, nontrivial in compositions_by_size.items():
            for composition in nontrivial:
                solver, _ = build_query(player_count, composition, **options)
                if solver.check() == z3.sat:
                    satisfiable.append({
                        "player_count": player_count,
                        "payoff_stratum_composition": composition,
                    })
        if not satisfiable:
            raise RuntimeError(f"negative control {name} did not open any case")
        controls[name] = satisfiable

    print(json.dumps({
        "status": "exact symbolic Lmin/PES bridge verified through four players",
        "solver": f"z3 {z3.get_version_string()} exact linear rational arithmetic",
        "theorem": (
            "in every singleton-normalized exact game with at most four players, "
            "every strict "
            "Lmin payoff gap has a tight richer-player suffix; consequently Lmin "
            "Lorenz-dominates the core and equals Lmax/PES"
        ),
        "compositions_checked": theorem_results,
        "negative_controls": controls,
        "consequence": (
            "combined with exact=>large-core through four players and coalitional "
            "monotonicity of PES/Lmax, the five-player exact Lmin counterexample "
            "has minimum possible dimension"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
