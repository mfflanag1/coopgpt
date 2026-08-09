#!/usr/bin/env python3
"""Exact controls showing that both staged packets remain necessary.

After imposing the positive critical-triple theorem and all local cross-cell
signs, the full Lmin packet alone still admits an outward simultaneous-split
displayed pair (index 239), while the full Lmax packet alone admits another
(index 212).  This script closes both rational generator systems and
independently recomputes their true selections.  In each case the retained
side is correct, the omitted side moves, and the true distance falls well
below 2/3.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import z3


COOPGAMES = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

from audit_core_closure_reconstruction import (  # noqa: E402
    coalition_sum,
    encode,
    lower_envelope,
)
from audit_equality_refinement_neighborhood import (  # noqa: E402
    COARSE_TYPES,
    contiguous_groups,
)
from audit_two_packet_exactification import (  # noqa: E402
    all_staged_pinning_certificates,
    independent_lex,
)
from core_closure_pipeline import (  # noqa: E402
    linear_sum,
    pipeline2_generator_normal_form,
)
from diagnose_refinement_unsat_groups import semantic_group  # noqa: E402
from lexsimplex import lex_point_with_trace  # noqa: E402


N = 6
FULL = (1 << N) - 1
POSITIVE = COARSE_TYPES[1]
CASES = (
    (239, "min"),
    (212, "max"),
)


def z3_fraction(model, expression):
    value = model.eval(expression)
    return F(value.numerator_as_long(), value.denominator_as_long())


def l1(left, right):
    return sum((abs(a - b) for a, b in zip(left, right)), F(0))


def overlap(left, right):
    return sum((min(a, b) for a, b in zip(left, right)), F(0))


def build_ablation(index, configuration, retained_side):
    r = tuple(configuration[0])
    c = tuple(configuration[1])
    table = tuple(tuple(row) for row in configuration[2])
    data = pipeline2_generator_normal_form(N, r, c, table, F(2, 3), fail=True)
    original = tuple(data["solver"].assertions())
    solver = z3.Solver()
    for position, assertion in enumerate(original):
        group = semantic_group(assertion, position, len(original))
        if retained_side == "min" and (
            group.startswith("ceiling_") or group == "lmax_support_eligibility"
        ):
            continue
        if retained_side == "max" and (
            group.startswith("floor_") or group == "lmin_support_eligibility"
        ):
            continue
        solver.add(assertion)

    cell = data["cell"]
    row_groups = contiguous_groups(r, POSITIVE["lmin"])
    column_groups = contiguous_groups(c, POSITIVE["lmax"])
    poor = [
        i
        for i, (row, column) in enumerate(cell)
        if row in row_groups[0] and column in column_groups[0]
    ]
    P = [
        i
        for i, (row, column) in enumerate(cell)
        if row in row_groups[0] and column in column_groups[1]
    ]
    rich = [
        i
        for i, (row, column) in enumerate(cell)
        if row in row_groups[1] and column in column_groups[1]
    ]
    assert len(poor) == 2 and len(P) == 3 and len(rich) == 1
    rich = rich[0]
    x, z, generators = data["lmin"], data["lmax"], data["generators"]
    solver.add(*[x[i] > z[i] for i in poor])
    solver.add(*[z[i] > x[i] for i in P])
    solver.add(x[rich] > z[rich])

    triples = []
    for excluded in P:
        triple = tuple(i for i in P if i != excluded) + (rich,)
        triples.append(triple)
        # x is tight: every other displayed generator dominates its sum.
        solver.add(
            *[
                linear_sum(x[i] for i in triple)
                <= linear_sum(generator[i] for i in triple)
                for generator in generators[1:]
            ]
        )
    # At least two triples are also z-tight.
    solver.add(
        z3.Or(
            *[
                z3.And(
                    *[
                        linear_sum(z[i] for i in triples[k])
                        <= linear_sum(generator[i] for i in triples[k])
                        for k in pair
                        for generator in (x,) + tuple(generators[2:])
                    ]
                )
                for pair in itertools.combinations(range(3), 2)
            ]
        )
    )
    return solver, data, {
        "poor_players": poor,
        "P_players": P,
        "rich_player": rich,
        "triple_masks": [sum(1 << i for i in triple) for triple in triples],
    }


def audit_case(index, retained_side, triage):
    configuration = triage["survivors"][index]
    solver, data, labels = build_ablation(index, configuration, retained_side)
    assert solver.check() == z3.sat
    model = solver.model()
    claimed_lmin = tuple(z3_fraction(model, value) for value in data["lmin"])
    claimed_lmax = tuple(z3_fraction(model, value) for value in data["lmax"])
    witnesses = tuple(
        tuple(z3_fraction(model, value) for value in row)
        for row in data["singleton_witnesses"]
    )
    generators = (claimed_lmin, claimed_lmax) + witnesses
    assert all(sum(row) == 1 and min(row) >= 0 for row in generators)
    assert all(witnesses[i][i] == 0 for i in range(N))
    claimed_distance = l1(claimed_lmin, claimed_lmax)
    assert claimed_distance > F(2, 3)

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
        exact_point, exact_trace = independent_lex(game, mode)
        assert tuple(simplex_point) == exact_point
        assert simplex_trace == exact_trace
        certificates = all_staged_pinning_certificates(
            game, exact_point, exact_trace, mode
        )
        assert len(certificates) == N
        selections[mode] = {
            "point": exact_point,
            "trace": exact_trace,
            "pinning_certificates": certificates,
        }

    actual_lmin = selections["min"]["point"]
    actual_lmax = selections["max"]["point"]
    assert (actual_lmin == claimed_lmin) == (retained_side == "min")
    assert (actual_lmax == claimed_lmax) == (retained_side == "max")
    actual_distance = l1(actual_lmin, actual_lmax)
    assert actual_distance < F(2, 3)

    full = pipeline2_generator_normal_form(
        N,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(row) for row in configuration[2]),
        F(2, 3),
        fail=True,
    )["solver"]
    assert full.check() == z3.unsat
    return {
        "survivor_index": index,
        "retained_full_staged_side": retained_side,
        "configuration": configuration,
        **labels,
        "claimed_pair": {
            "lmin": claimed_lmin,
            "lmax": claimed_lmax,
            "l1_distance": claimed_distance,
            "overlap": overlap(claimed_lmin, claimed_lmax),
        },
        "singleton_witnesses": witnesses,
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
            "l1_distance": actual_distance,
            "overlap": overlap(actual_lmin, actual_lmax),
            "independent_exact_selection_encodings": 2,
            "complete_staged_pinning_certificates": 12,
        },
        "omitted_side_changed": "max" if retained_side == "min" else "min",
        "full_two_sided_staged_verdict": "unsat",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    args = parser.parse_args()
    triage = json.loads(args.triage.read_text())
    rows = [audit_case(*case, triage) for case in CASES]
    report = {
        "status": "PASS",
        "scope": (
            "exact simultaneous-split ablations: neither full staged side alone "
            "proves the positive critical-neighborhood bound"
        ),
        "cases": rows,
        "interpretation": (
            "both staged packets are load-bearing beyond one split; exact closure "
            "preserves the retained selection, changes the omitted selection, and "
            "returns the true pair strictly inside 2/3"
        ),
    }
    rendered = json.dumps(encode(report), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
