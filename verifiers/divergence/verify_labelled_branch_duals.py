#!/usr/bin/env python3
"""Exact hostile controls for the fully labelled branch-circuit dual.

For five previously archived n=7/n=8 obstructions and both balanced n=7 sharp
family orientations, this verifier fixes one complete union of staged
Lmin/Lmax circuit supports, varies every generator in the n+2 lower-envelope
normal form, and minimizes the true labelled overlap.  It then recomputes an
exact Farkas dual and all one-witness relaxations.

These are seven branch theorems, not an all-n proof and not an enumeration.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402


CASES = (
    {
        "name": "optimized_label_free_spectral_failure",
        "g": (0, 0, 3, 17, 0, 9, 1),
        "h": (14, 4, 0, 0, 12, 0, 0),
        "x": (F(25, 4), F(3, 2), F(3, 2), F(37, 4), F(21, 4), F(21, 4), F(1)),
        "z": (F(64, 9), F(32, 9), F(2, 9), F(64, 9), F(19, 3), F(49, 9), F(2, 9)),
        "support_x": (11, 26, 52, 57),
        "support_z": (15, 52, 57, 70, 75, 93, 101),
        "branch_minimum": F(3, 4),
        "one_witness_minima": (F(25, 34), F(25, 34), F(25, 34), F(3, 4), F(25, 34), F(25, 34), F(25, 34)),
    },
    {
        "name": "actual_top_fixed_failure",
        "g": (18, 17, 0, 0, 1, 0, 0),
        "h": (0, 0, 24, 10, 0, 1, 1),
        "x": (F(9), F(8), F(19, 2), F(8), F(1, 2), F(1, 2), F(1, 2)),
        "z": (F(9), F(17, 2), F(9), F(17, 2), F(1), F(0), F(0)),
        "support_x": (21, 22, 47, 79, 80),
        "support_z": (5, 21, 32, 47, 64, 79),
        "branch_minimum": F(7, 10),
        "one_witness_minima": (F(7, 10),) * 7,
    },
    {
        "name": "top_and_bottom_fixed_failure",
        "g": (10, 1, 0, 1, 21, 0, 9),
        "h": (0, 0, 1, 0, 0, 41, 0),
        "x": (F(19, 2), F(1, 2), F(1, 2), F(1, 2), F(45, 4), F(45, 4), F(17, 2)),
        "z": (F(10), F(1), F(0), F(1), F(21, 2), F(21, 2), F(9)),
        "support_x": (6, 12, 59, 115, 121, 122),
        "support_z": (4, 6, 12, 48, 49, 112, 122),
        "branch_minimum": F(2, 3),
        "one_witness_minima": (F(2, 3),) * 7,
    },
    {
        "name": "coefficient_two_congestion_failure",
        "g": (1, 1, 0, 5, 0, 4, 1),
        "h": (0, 0, 8, 0, 4, 0, 0),
        "x": (F(1), F(1), F(2), F(3), F(1), F(3), F(1)),
        "z": (F(8, 9), F(8, 9), F(8, 3), F(8, 3), F(4, 3), F(8, 3), F(8, 9)),
        "support_x": (15, 24, 44, 48, 76, 77, 78),
        "support_z": (24, 44, 79),
        "branch_minimum": F(9, 11),
        "one_witness_minima": (F(16, 25), F(16, 25), F(16, 25), F(9, 11), F(16, 25), F(9, 11), F(16, 25)),
    },
    {
        "name": "primitive_coefficient_seven_failure",
        "g": (0, 0, 7, 4, 3, 2, 0, 0),
        "h": (4, 1, 0, 0, 0, 0, 6, 5),
        "x": (F(8, 3), F(2, 3), F(7, 3), F(4, 3), F(1), F(2, 3), F(4), F(10, 3)),
        "z": (F(28, 13), F(7, 13), F(42, 13), F(24, 13), F(18, 13), F(12, 13), F(42, 13), F(35, 13)),
        "support_x": (9, 70, 85, 90, 104, 151, 165, 176, 204),
        "support_z": (9, 51, 70, 85, 90, 104, 151, 165, 170, 176, 204),
        "branch_minimum": F(34, 39),
        "one_witness_minima": (F(113, 161), F(11, 19), F(11, 19), F(47, 79), F(77, 125), F(61, 93), F(181, 261), F(2, 3)),
    },
    {
        "name": "sharp_family_p2_k4",
        "g": (6, 1, 1, 0, 0, 0, 0),
        "h": (0, 0, 0, 2, 2, 2, 2),
        "x": (F(4), F(2, 3), F(2, 3), F(2, 3), F(2, 3), F(2, 3), F(2, 3)),
        "z": (F(3, 2), F(1, 4), F(1, 4), F(3, 2), F(3, 2), F(3, 2), F(3, 2)),
        "support_x": (22, 38, 57, 70, 89, 105, 113),
        "support_z": (14, 22, 38, 57, 70, 89, 105, 113),
        "branch_minimum": F(7, 12),
        "one_witness_minima": (F(7, 12),) + (F(7, 15),) * 6,
    },
    {
        "name": "sharp_family_p3_k3",
        "g": (6, 1, 1, 1, 0, 0, 0),
        "h": (0, 0, 0, 0, 3, 3, 3),
        "x": (F(9, 2), F(3, 4), F(3, 4), F(3, 4), F(3, 4), F(3, 4), F(3, 4)),
        "z": (F(2), F(1, 3), F(1, 3), F(1, 3), F(2), F(2), F(2)),
        "support_x": (46, 49, 78, 81, 97),
        "support_z": (30, 46, 49, 78, 81, 97),
        "branch_minimum": F(7, 12),
        "one_witness_minima": (F(7, 12),) + (F(7, 16),) * 6,
    },
)


def restricted_stage_certificate(values, point, mode, support, stage, player):
    """Check one full staged stationarity relation on the fixed support."""
    n = len(point)
    blocks = payoff_blocks(point, mode)
    old = tuple(i for block in blocks[:stage] for i in block)
    current = blocks[stage]
    tight = tuple(S for S in support if coalition_sum(point, S) == values[S])
    assert tight == tuple(s for s in support)
    m = len(tight)
    old_index = {j: m + k for k, j in enumerate(old)}
    side_index = {j: m + len(old) + k for k, j in enumerate(current)}
    constant_index = m + len(old) + len(current)
    width = constant_index + 1
    side = F(1 if mode == "min" else -1)
    equalities, rhs = [], []
    for coordinate in range(n):
        row = [F(0)] * width
        for k, coalition in enumerate(tight):
            row[k] = F((coalition >> coordinate) & 1)
        if coordinate in old_index:
            row[old_index[coordinate]] = 1
        if coordinate in side_index:
            row[side_index[coordinate]] = side
        row[constant_index] = -1
        equalities.append(row)
        rhs.append(-side * F(coordinate == player))
    inequalities, inequality_rhs = [], []
    for variable in tuple(range(m)) + tuple(side_index.values()):
        row = [F(0)] * width
        row[variable] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))
    for variable in old_index.values():
        row = [F(0)] * width
        row[variable] = F(-1 if mode == "min" else 1)
        inequalities.append(row)
        inequality_rhs.append(F(0))
    status, _objective, _solution = exact_linprog(
        [F(0)] * width, inequalities, inequality_rhs, equalities, rhs
    )
    assert status == "optimal"


def verify_complete_selection(values, point, mode, support):
    for stage, block in enumerate(payoff_blocks(point, mode)):
        for player in block:
            restricted_stage_certificate(values, point, mode, support, stage, player)


def branch_system(case):
    n = len(case["x"])
    total = sum(map(F, case["g"]), F(0))
    x0 = tuple(q / total for q in case["x"])
    z0 = tuple(q / total for q in case["z"])
    generator_count = n + 2
    width = generator_count * n

    def index(generator, player):
        return generator * n + player

    inequalities, inequality_rhs, inequality_labels = [], [], []
    equalities, equality_rhs, equality_labels = [], [], []
    for generator in range(generator_count):
        for player in range(n):
            row = [F(0)] * width
            row[index(generator, player)] = -1
            inequalities.append(row)
            inequality_rhs.append(F(0))
            inequality_labels.append(("nonnegative", generator, player))
        row = [F(0)] * width
        for player in range(n):
            row[index(generator, player)] = 1
        equalities.append(row)
        equality_rhs.append(F(1))
        equality_labels.append(("total", generator))
    for player in range(n):
        row = [F(0)] * width
        row[index(2 + player, player)] = 1
        equalities.append(row)
        equality_rhs.append(F(0))
        equality_labels.append(("witness_zero", player))

    for root, support in ((0, case["support_x"]), (1, case["support_z"])):
        for coalition in support:
            for generator in range(generator_count):
                if generator == root:
                    continue
                row = [F(0)] * width
                for player in range(n):
                    if coalition >> player & 1:
                        row[index(root, player)] += 1
                        row[index(generator, player)] -= 1
                inequalities.append(row)
                inequality_rhs.append(F(0))
                inequality_labels.append(("tight", "x" if root == 0 else "z", coalition, generator))

    for generator, point, mode in ((0, x0, "min"), (1, z0, "max")):
        blocks = payoff_blocks(point, mode)
        for block in blocks:
            for player in block[1:]:
                row = [F(0)] * width
                row[index(generator, player)] = 1
                row[index(generator, block[0])] = -1
                equalities.append(row)
                equality_rhs.append(F(0))
                equality_labels.append(("stratum_equal", generator, block[0], player))
        for first, second in zip(blocks, blocks[1:]):
            row = [F(0)] * width
            if mode == "min":
                row[index(generator, first[0])] = 1
                row[index(generator, second[0])] = -1
            else:
                row[index(generator, second[0])] = 1
                row[index(generator, first[0])] = -1
            inequalities.append(row)
            inequality_rhs.append(F(0))
            inequality_labels.append(("stratum_order", generator, first[0], second[0]))

    sign_cut = {player for player in range(n) if z0[player] > x0[player]}
    for player in range(n):
        row = [F(0)] * width
        if player in sign_cut:
            row[index(0, player)] = 1
            row[index(1, player)] = -1
        else:
            row[index(1, player)] = 1
            row[index(0, player)] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))
        inequality_labels.append(("hybrid_sign", player, player in sign_cut))

    objective = [F(0)] * width
    for player in range(n):
        objective[index(0 if player in sign_cut else 1, player)] = 1
    return {
        "n": n,
        "inequalities": inequalities,
        "inequality_rhs": inequality_rhs,
        "inequality_labels": inequality_labels,
        "equalities": equalities,
        "equality_rhs": equality_rhs,
        "equality_labels": equality_labels,
        "objective": objective,
        "sign_cut": sign_cut,
    }


def exact_dual(system, optimum):
    inequalities = system["inequalities"]
    equalities = system["equalities"]
    objective = system["objective"]
    nu, ne = len(inequalities), len(equalities)
    width = nu + ne
    dual_equalities, dual_rhs = [], []
    for coordinate, coefficient in enumerate(objective):
        row = [F(0)] * width
        for k in range(nu):
            row[k] = -inequalities[k][coordinate]
        for k in range(ne):
            row[nu + k] = equalities[k][coordinate]
        dual_equalities.append(row)
        dual_rhs.append(coefficient)
    row = [F(0)] * width
    for k, rhs in enumerate(system["equality_rhs"]):
        row[nu + k] = rhs
    dual_equalities.append(row)
    dual_rhs.append(optimum)
    dual_inequalities, dual_inequality_rhs = [], []
    for k in range(nu):
        row = [F(0)] * width
        row[k] = -1
        dual_inequalities.append(row)
        dual_inequality_rhs.append(F(0))
    status, _objective, solution = exact_linprog(
        [F(0)] * width,
        dual_inequalities,
        dual_inequality_rhs,
        dual_equalities,
        dual_rhs,
    )
    assert status == "optimal"
    for row, rhs in zip(dual_equalities, dual_rhs):
        assert sum((a * b for a, b in zip(row, solution)), F(0)) == rhs
    assert all(solution[k] >= 0 for k in range(nu))
    inequality_support = [
        (system["inequality_labels"][k], solution[k])
        for k in range(nu)
        if solution[k]
    ]
    equality_support = [
        (system["equality_labels"][k], solution[nu + k])
        for k in range(ne)
        if solution[nu + k]
    ]
    return inequality_support, equality_support


def one_witness_minimum(system, witness):
    n = system["n"]
    allowed = {0, 1, 2 + witness}
    columns = [generator * n + player for generator in sorted(allowed) for player in range(n)]
    inequality_rows = []
    for k, label in enumerate(system["inequality_labels"]):
        if label[0] == "nonnegative" and label[1] not in allowed:
            continue
        if label[0] == "tight" and label[3] not in allowed:
            continue
        inequality_rows.append(k)
    equality_rows = []
    for k, label in enumerate(system["equality_labels"]):
        if label[0] == "total" and label[1] not in allowed:
            continue
        if label[0] == "witness_zero" and label[1] != witness:
            continue
        equality_rows.append(k)
    status, optimum, _solution = exact_linprog(
        [system["objective"][j] for j in columns],
        [[system["inequalities"][k][j] for j in columns] for k in inequality_rows],
        [system["inequality_rhs"][k] for k in inequality_rows],
        [[system["equalities"][k][j] for j in columns] for k in equality_rows],
        [system["equality_rhs"][k] for k in equality_rows],
    )
    assert status == "optimal"
    return optimum


def audit_case(case):
    n = len(case["x"])
    total = sum(map(F, case["g"]), F(0))
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
    values = tuple(
        min(coalition_sum(generator, coalition) for generator in generators)
        for coalition in range(1 << n)
    )
    assert values[-1] == total
    assert all(values[1 << player] == 0 for player in range(n))
    for point in (tuple(case["x"]), tuple(case["z"])):
        assert sum(point, F(0)) == total
        assert all(coalition_sum(point, coalition) >= values[coalition] for coalition in range(1, (1 << n) - 1))
    verify_complete_selection(values, tuple(case["x"]), "min", case["support_x"])
    verify_complete_selection(values, tuple(case["z"]), "max", case["support_z"])

    system = branch_system(case)
    status, optimum, solution = exact_linprog(
        system["objective"],
        system["inequalities"],
        system["inequality_rhs"],
        system["equalities"],
        system["equality_rhs"],
    )
    assert status == "optimal" and optimum == case["branch_minimum"]
    inequality_dual, equality_dual = exact_dual(system, optimum)
    one_witness = tuple(one_witness_minimum(system, player) for player in range(n))
    assert one_witness == case["one_witness_minima"]
    target = F(n, (n * n) // 4)
    passing_witnesses = [player for player, bound in enumerate(one_witness) if bound >= target]
    assert optimum >= target and passing_witnesses

    generated = tuple(
        tuple(solution[generator * n + player] for player in range(n))
        for generator in range(n + 2)
    )
    generated_values = tuple(
        min(coalition_sum(generator, coalition) for generator in generated)
        for coalition in range(1 << n)
    )
    assert all(generated_values[1 << player] == 0 for player in range(n))
    verify_complete_selection(generated_values, generated[0], "min", case["support_x"])
    verify_complete_selection(generated_values, generated[1], "max", case["support_z"])
    assert sum((min(generated[0][i], generated[1][i]) for i in range(n)), F(0)) == optimum

    witness_blocks = sorted({
        label[1] - 2
        for label, coefficient in inequality_dual
        if coefficient and label[0] == "nonnegative" and label[1] >= 2
    } | {
        label[3] - 2
        for label, coefficient in inequality_dual
        if coefficient and label[0] == "tight" and label[3] >= 2
    } | {
        label[1]
        for label, coefficient in equality_dual
        if coefficient and label[0] == "witness_zero"
    })
    return {
        "name": case["name"],
        "n": n,
        "support_sizes": {"lmin": len(case["support_x"]), "lmax": len(case["support_z"])},
        "branch_minimum": str(optimum),
        "sharp_target": str(target),
        "margin": str(optimum - target),
        "dual_support": {
            "inequalities": len(inequality_dual),
            "equalities": len(equality_dual),
            "witness_blocks_in_optimal_dual": witness_blocks,
        },
        "one_witness_minima": [str(q) for q in one_witness],
        "weakest_one_witness_minimum": str(min(one_witness)),
        "passing_witnesses": passing_witnesses,
        "extremizer": {
            "lmin": [str(q) for q in generated[0]],
            "lmax": [str(q) for q in generated[1]],
            "singleton_normalized_exact_lower_envelope": True,
            "selection_check": f"{2*n} restricted-support exact staged LP certificates",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact rational fully labelled branch-dual hostile controls",
        "cases": [audit_case(case) for case in CASES],
        "scope": (
            "seven fixed rooted-circuit branches only; supports the one-witness "
            "threshold conjecture but does not prove it for all branches or all n"
        ),
        "evidence": (
            "exact primal minima, exact Farkas coefficient identities, exact "
            "one-witness relaxations, and fresh restricted-support staged checks"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
