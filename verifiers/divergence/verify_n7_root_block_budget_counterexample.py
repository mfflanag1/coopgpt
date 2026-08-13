#!/usr/bin/env python3
"""Exact seven-player counterexample to the full-root-block RBB conjecture.

This does *not* counterexample the hybrid-overlap bound.  It constructs a
singleton-normalized exact lower-envelope game, certifies the displayed Lmin
and Lmax by both exact staged Farkas relations and an independently formulated
Z3 tangent-direction audit, and then checks that:

* both maximum-overlap roots are fully unaffordable and form a carrier cycle;
* an Lmax-tight row splits that cycle, so it is role-irreducible there;
* the full nongainer root block has RBB numerator -8; but
* the unique target-reaching tight direct packet enlarges the carrier block
  by two labelled nongainers and proves a 5/6 base, above the 7/12 target.

Thus only the proposed universal RBB shortcut fails.  The more general
carrier-support selection alternative survives this hostile control.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import z3


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_cover_to_direct_handover import direct_witnesses  # noqa: E402
from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_carrier_separator_payment import (  # noqa: E402
    carriers,
    directed_cycles,
    full_tight_support,
)
from exactlp import exact_linprog  # noqa: E402
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402


RAW_GENERATORS = (
    (6, 7, 3, 0, 3, 3, 1),
    (7, 0, 2, 0, 1, 13, 0),
    (0, 0, 2, 5, 5, 9, 2),
)
LMIN = (F(3), F(7, 2), F(1), F(3), F(2), F(7, 2), F(1))
LMAX = (F(14, 5), F(16, 5), F(2, 5), F(13, 5), F(16, 5), F(16, 5), F(8, 5))


def normalized_generators():
    singleton = tuple(min(row[i] for row in RAW_GENERATORS) for i in range(7))
    generators = tuple(
        tuple(F(row[i] - singleton[i]) for i in range(7))
        for row in RAW_GENERATORS
    )
    return singleton, generators


def values_from_generators(generators):
    return tuple(
        min(coalition_sum(row, coalition) for row in generators)
        for coalition in range(1 << 7)
    )


def payoff_blocks(point, mode):
    levels = sorted(set(point), reverse=(mode == "max"))
    return tuple(tuple(i for i, value in enumerate(point) if value == level) for level in levels)


def z3_no_improving_directions(values, point, mode):
    """Independently check staged optimality from primal tangent directions."""

    tight = full_tight_support(values, point)
    checks = []
    old = []
    for stage, block in enumerate(payoff_blocks(point, mode)):
        for target in block:
            direction = [z3.Real(f"d_{mode}_{stage}_{target}_{i}") for i in range(7)]
            solver = z3.Solver()
            solver.add(z3.Sum(direction) == 0)
            for coalition in tight:
                solver.add(
                    z3.Sum(
                        [direction[i] for i in range(7) if coalition >> i & 1]
                    )
                    >= 0
                )
            for i in old:
                solver.add(direction[i] == 0)
            if mode == "min":
                for i in block:
                    solver.add(direction[i] >= 0)
                solver.add(direction[target] >= 1)
            else:
                for i in block:
                    solver.add(direction[i] <= 0)
                solver.add(direction[target] <= -1)
            status = solver.check()
            if status != z3.unsat:
                raise AssertionError((mode, stage, target, status, solver.model()))
            checks.append(
                {
                    "stage": stage,
                    "target": target,
                    "status": "unsat: no improving tangent direction",
                }
            )
        old.extend(block)
    return checks


def staged_dual_certificates(values, point, mode):
    """Return explicit exact staged Farkas multipliers for every player."""

    tight = full_tight_support(values, point)
    blocks = payoff_blocks(point, mode)
    certificates = []
    for stage, current in enumerate(blocks):
        old = tuple(i for block in blocks[:stage] for i in block)
        coalition_count = len(tight)
        old_index = {player: coalition_count + k for k, player in enumerate(old)}
        side_index = {
            player: coalition_count + len(old) + k
            for k, player in enumerate(current)
        }
        constant_index = coalition_count + len(old) + len(current)
        width = constant_index + 1
        side = F(1 if mode == "min" else -1)
        for target in current:
            equalities, rhs = [], []
            for coordinate in range(7):
                row = [F()] * width
                for k, coalition in enumerate(tight):
                    row[k] = F((coalition >> coordinate) & 1)
                if coordinate in old_index:
                    row[old_index[coordinate]] = 1
                if coordinate in side_index:
                    row[side_index[coordinate]] = side
                row[constant_index] = -1
                equalities.append(row)
                rhs.append(-side * F(coordinate == target))
            inequalities, inequality_rhs = [], []
            for variable in tuple(range(coalition_count)) + tuple(side_index.values()):
                row = [F()] * width
                row[variable] = -1
                inequalities.append(row)
                inequality_rhs.append(F())
            for variable in old_index.values():
                row = [F()] * width
                row[variable] = F(-1 if mode == "min" else 1)
                inequalities.append(row)
                inequality_rhs.append(F())
            status, _objective, solution = exact_linprog(
                [F()] * width,
                inequalities,
                inequality_rhs,
                equalities,
                rhs,
            )
            if status != "optimal":
                raise AssertionError(("missing staged dual", mode, stage, target, status))
            for row, value in zip(equalities, rhs):
                if sum((a * b for a, b in zip(row, solution)), F()) != value:
                    raise AssertionError("staged dual equality replay failed")
            certificates.append(
                {
                    "stage": stage,
                    "target": target,
                    "tight_coalition_weights": {
                        str(coalition): str(solution[k])
                        for k, coalition in enumerate(tight)
                        if solution[k]
                    },
                    "old_pin_weights": {
                        str(player): str(solution[index])
                        for player, index in old_index.items()
                        if solution[index]
                    },
                    "current_side_weights": {
                        str(player): str(solution[index])
                        for player, index in side_index.items()
                        if solution[index]
                    },
                    "constant": str(solution[constant_index]),
                }
            )
    return certificates


def fraction_strings(values):
    return [str(value) for value in values]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    singleton, generators = normalized_generators()
    values = values_from_generators(generators)
    full = (1 << 7) - 1
    if singleton != (0, 0, 2, 0, 1, 3, 0):
        raise AssertionError("unexpected singleton translation")
    if any(values[1 << i] for i in range(7)) or values[full] != 17:
        raise AssertionError("normalization or total failure")

    # Every generator is a core point and every coalition minimum is attained
    # by one of them.  This is the elementary lower-envelope proof of exactness.
    if not all(
        coalition_sum(generator, coalition) >= values[coalition]
        for generator in generators
        for coalition in range(1 << 7)
    ):
        raise AssertionError("normalized generator is not in the core")
    minimizers = tuple(
        tuple(
            index
            for index, generator in enumerate(generators)
            if coalition_sum(generator, coalition) == values[coalition]
        )
        for coalition in range(1 << 7)
    )
    if any(not rows for rows in minimizers):
        raise AssertionError("lower-envelope exactness minimizer missing")

    for point in (LMIN, LMAX):
        if sum(point, F()) != values[full]:
            raise AssertionError("selector efficiency failure")
        if not all(
            coalition_sum(point, coalition) >= values[coalition]
            for coalition in range(1 << 7)
        ):
            raise AssertionError("displayed selector is outside the core")

    x_tight = full_tight_support(values, LMIN)
    z_tight = full_tight_support(values, LMAX)

    # Exact dual staged certificates.  This component uses nonnegative
    # stationarity multipliers on the complete tight menus.
    dual_min = staged_dual_certificates(values, LMIN, "min")
    dual_max = staged_dual_certificates(values, LMAX, "max")

    # Independent optimality component: no multipliers, only primal tangent
    # directions in exact Z3 linear rational arithmetic.
    z3_min = z3_no_improving_directions(values, LMIN, "min")
    z3_max = z3_no_improving_directions(values, LMAX, "max")

    roots = maximum_overlap_roots(LMIN, LMAX)
    if roots != (1, 5):
        raise AssertionError(("unexpected roots", roots))
    affordability = tuple(solve_labelled_cover(x_tight, root, 7) for root in roots)
    if any(row["affordable"] for row in affordability):
        raise AssertionError("root unexpectedly affordable")
    graph = {
        row["root"]: tuple(carrier for carrier in carriers(row) if carrier in roots)
        for row in affordability
    }
    cycles = directed_cycles(graph)
    if cycles != ((1, 5),):
        raise AssertionError(("unexpected carrier cycles", cycles))
    cycle_mask = (1 << 1) | (1 << 5)
    splitters = tuple(
        coalition
        for coalition in z_tight
        if 0 < (coalition & cycle_mask) < cycle_mask
    )
    if splitters != (33, 101):
        raise AssertionError(("unexpected Lmax splitters", splitters))

    maximum_overlap = max(min(LMIN[i], LMAX[i]) for i in range(7))
    H = tuple(i for i in roots if LMAX[i] <= LMIN[i])
    P = tuple(i for i in range(7) if LMAX[i] <= LMIN[i] and i not in H)
    G = tuple(i for i in range(7) if LMAX[i] > LMIN[i])
    p, g, h = len(P), len(G), len(H)
    U = sum((maximum_overlap - LMAX[i] for i in P), F())
    R = sum((maximum_overlap - LMIN[i] for i in G), F())
    D = sum((LMAX[i] - LMIN[i] for i in G), F())
    rbb_numerator = g * (g + h) * U - g * p * R - (g + h * (p + 1)) * D
    if (maximum_overlap, H, P, G, U, R, D, rbb_numerator) != (
        F(16, 5),
        (1, 5),
        (0, 2, 3),
        (4, 6),
        F(19, 5),
        F(17, 5),
        F(9, 5),
        F(-8),
    ):
        raise AssertionError("RBB arithmetic mismatch")

    direct = direct_witnesses(LMIN, LMAX, x_tight, F(7, 12))
    if len(direct) != 1:
        raise AssertionError(("unexpected direct-witness count", len(direct)))
    witness = direct[0]
    if (
        tuple(witness["P"]),
        tuple(witness["G"]),
        tuple(witness["H"]),
        tuple(witness["J"]),
        witness["comparison_coalition"],
    ) != ((2,), (4, 6), (0, 1, 3, 5), (4,), 59):
        raise AssertionError(("unexpected direct witness", witness))
    staged_repair_circuit = {"coalition": 59, "floor_columns": [2, 6]}
    for player in range(7):
        load = int(59 >> player & 1) + int(player in (2, 6))
        if load != 1:
            raise AssertionError("staged repair incidence circuit failed")
    master = master_identity(LMIN, LMAX, (2,), (4, 6), (0, 1, 3, 5), (4,))
    if F(master["base_bound_ratio"]) != F(5, 6) or not master["budget_closes_direct"]:
        raise AssertionError("selected tight-support repair did not close")

    overlap = sum((min(LMIN[i], LMAX[i]) for i in range(7)), F())
    ratio = overlap / values[full]
    if ratio != F(76, 85) or ratio <= F(7, 12):
        raise AssertionError("actual overlap control failure")

    report = {
        "status": "exact counterexample to full-root-block RBB; main overlap target preserved",
        "scope": (
            "disproves only the proposed universal RBB shortcut on the "
            "role-irreducible all-unaffordable branch; finite hostile control, "
            "not a proof of the revised carrier-support selection lemma"
        ),
        "raw_generators": [list(row) for row in RAW_GENERATORS],
        "singleton_translation": list(singleton),
        "normalized_generators": [fraction_strings(row) for row in generators],
        "total": str(values[full]),
        "exactness": {
            "argument": (
                "each normalized generator is a core allocation and every "
                "coalition worth is attained by at least one generator"
            ),
            "coalition_minimizers": [list(rows) for rows in minimizers],
        },
        "lmin": fraction_strings(LMIN),
        "lmax": fraction_strings(LMAX),
        "lmin_blocks": [list(block) for block in payoff_blocks(LMIN, "min")],
        "lmax_blocks": [list(block) for block in payoff_blocks(LMAX, "max")],
        "lmin_tight_support": list(x_tight),
        "lmax_tight_support": list(z_tight),
        "selection_certificates": {
            "dual_lmin": dual_min,
            "dual_lmax": dual_max,
            "primal_z3_lmin": z3_min,
            "primal_z3_lmax": z3_max,
            "independence_boundary": (
                "the encodings share the reconstructed core and displayed "
                "tight menus; their staged-optimality components are dual "
                "multipliers versus primal no-improving-direction formulas"
            ),
        },
        "maximum_overlap": str(maximum_overlap),
        "maximum_overlap_roots": list(roots),
        "affordability": list(affordability),
        "carrier_graph": {str(root): list(carriers_) for root, carriers_ in graph.items()},
        "carrier_cycles": [list(cycle) for cycle in cycles],
        "lmax_cycle_splitters": list(splitters),
        "rbb": {
            "H": list(H),
            "P": list(P),
            "G": list(G),
            "U": str(U),
            "R": str(R),
            "D": str(D),
            "numerator": str(rbb_numerator),
            "scalar_margin": str(F(rbb_numerator, g * (g + h))),
        },
        "selected_tight_support_repair": {
            "primitive_lmin_floor_circuit": staged_repair_circuit,
            "circuit_identity": "1_59 + e_2 + e_6 = 1_N",
            "facet_scope": (
                "relative first-stage Lmin selection-cell circuit; the e "
                "columns are floor columns, so this is not asserted to be a "
                "new full exact-game-cone facet"
            ),
            "unique_target_reaching_direct_witness": witness,
            "master_identity": master,
            "interpretation": (
                "coalition 59 adjoins labelled nongainers 0 and 3 to the "
                "carrier cycle; the root block alone and the other proper "
                "cycle-containing tight rows fail"
            ),
        },
        "overlap": str(overlap),
        "overlap_ratio": str(ratio),
        "target": "7/12",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
