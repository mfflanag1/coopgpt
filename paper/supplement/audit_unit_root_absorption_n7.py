"""Audit the capacity-one root-absorption inequality exactly.

At target c=1, positive-part subadditivity bounds every admissible first
leaf rate by -gamma[a], independently of its arm masses.  For each lifted
root and second leaf in the certified (3,2,1) pattern, this script minimizes
the remaining homogeneous expression

    r_B q^0_B + sum_T (q^0_T+q^2_T)
        [gamma(T)+r_A 1[T=A]-r_B 1[T=B]]_+ - m_A gamma_a

over r_A,r_B >= 0, sum(gamma)=gamma(U)=0, and
m_A r_A+m_B r_B=1.  Nonnegativity proves capacity one for every compatible
first leaf, with no bound on q_A/m_A and no enumeration of first leaves.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import audit_ratio5_bad_leaf_gluing_n7 as gluing
from analyze_two_color_box_capacity import rat
from hunt_peleg_coefficient_ceiling_escape import exact_incidence_rank


def absorption_subcollection(
        root_core, second_core, m_A, require=True, *,
        players=gluing.N, A_player=gluing.A_PLAYER,
        B=gluing.B, witness=gluing.WITNESS):
    """Find z <= q^0+q^2 with the exact root-absorption degrees."""
    coalitions = tuple(sorted(set(root_core) | set(second_core)))
    aggregate = defaultdict(F, root_core)
    for coalition, weight in second_core.items():
        aggregate[coalition] += weight
    position = {coalition: index for index, coalition in enumerate(coalitions)}
    beta = len(coalitions)
    delta = beta + 1
    variable_count = beta + 2

    A_eq = []
    b_eq = []
    for player in range(players):
        row = np.zeros(variable_count)
        for coalition in coalitions:
            if coalition >> player & 1:
                row[position[coalition]] = 1
        row[beta] = -1
        if witness >> player & 1:
            row[delta] = -1
        A_eq.append(row)
        b_eq.append(float(m_A * int(player == A_player)))

    A_ub = []
    b_ub = []
    row = np.zeros(variable_count)
    if B in position:
        row[position[B]] = 1
    A_ub.append(row)
    b_ub.append(float(root_core.get(B, F(0))))

    bounds = [
        (0, float(aggregate[coalition])) for coalition in coalitions
    ] + [(None, None), (None, None)]
    result = linprog(
        np.zeros(variable_count),
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq),
        b_eq=np.asarray(b_eq),
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        if require:
            raise AssertionError(result.message)
        return None
    solution = [rat(value) for value in result.x]
    exact = (
        all(
            sum(rat(coefficient) * value
                for coefficient, value in zip(row, solution)) == rat(rhs)
            for row, rhs in zip(A_eq, b_eq)
        )
        and all(
            sum(rat(coefficient) * value
                for coefficient, value in zip(row, solution)) <= rat(rhs)
            for row, rhs in zip(A_ub, b_ub)
        )
        and all(
            (lower is None or value >= rat(lower))
            and (upper is None or value <= rat(upper))
            for value, (lower, upper) in zip(solution, bounds)
        )
    )
    return {
        "exact": exact,
        "beta": str(solution[beta]),
        "delta": str(solution[delta]),
        "B_mass": str(solution[position[B]])
            if B in position else "0",
        "subcollection": {
            str(coalition): str(solution[position[coalition]])
            for coalition in coalitions
            if solution[position[coalition]]
        },
    }


def solve(
        root_core, second_core, m_A, m_B, *,
        players=gluing.N, A=gluing.A, B=gluing.B,
        A_player=gluing.A_PLAYER, witness=gluing.WITNESS,
        r_B_penalty=F(0)):
    coalitions = tuple(sorted(set(root_core) | set(second_core)))
    aggregate = defaultdict(F, root_core)
    for coalition, weight in second_core.items():
        aggregate[coalition] += weight

    r_A, r_B = 0, 1
    gamma_start = 2
    hinge_start = gamma_start + players
    variable_count = hinge_start + len(coalitions)
    hinge_position = {
        coalition: hinge_start + index
        for index, coalition in enumerate(coalitions)
    }

    objective = np.zeros(variable_count)
    objective[r_B] = float(root_core.get(B, F(0))-r_B_penalty)
    objective[gamma_start + A_player] = -float(m_A)
    for coalition in coalitions:
        objective[hinge_position[coalition]] = float(aggregate[coalition])

    A_eq = []
    b_eq = []

    row = np.zeros(variable_count)
    row[gamma_start:gamma_start + players] = 1
    A_eq.append(row)
    b_eq.append(0)

    row = np.zeros(variable_count)
    for player in range(players):
        if witness >> player & 1:
            row[gamma_start + player] = 1
    A_eq.append(row)
    b_eq.append(0)

    row = np.zeros(variable_count)
    row[r_A] = float(m_A)
    row[r_B] = float(m_B)
    A_eq.append(row)
    b_eq.append(1)

    A_ub = []
    b_ub = []
    for coalition in coalitions:
        row = np.zeros(variable_count)
        row[r_A] = int(coalition == A)
        row[r_B] = -int(coalition == B)
        for player in range(players):
            if coalition >> player & 1:
                row[gamma_start + player] = 1
        row[hinge_position[coalition]] = -1
        A_ub.append(row)
        b_ub.append(0)

    bounds = [(0, None), (0, None)]
    bounds.extend([(None, None)] * players)
    bounds.extend([(0, None)] * len(coalitions))
    result = linprog(
        objective,
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq),
        b_eq=np.asarray(b_eq),
        bounds=bounds,
        method="highs",
    )
    assert result.success, result.message

    solution = [rat(value) for value in result.x]
    exact_objective = [rat(value) for value in objective]
    minimum = sum(
        coefficient * value
        for coefficient, value in zip(exact_objective, solution)
    )
    primal_exact = (
        all(
            sum(rat(coefficient) * value
                for coefficient, value in zip(row, solution)) == rat(rhs)
            for row, rhs in zip(A_eq, b_eq)
        )
        and all(
            sum(rat(coefficient) * value
                for coefficient, value in zip(row, solution)) <= rat(rhs)
            for row, rhs in zip(A_ub, b_ub)
        )
        and all(
            lower is None or value >= rat(lower)
            for value, (lower, _upper) in zip(solution, bounds)
        )
    )

    inequality_duals = [rat(value) for value in result.ineqlin.marginals]
    equality_duals = [rat(value) for value in result.eqlin.marginals]
    lower_duals = [rat(value) for value in result.lower.marginals]
    combined = [F(0)] * variable_count
    for multiplier, row in zip(inequality_duals, A_ub):
        for column, coefficient in enumerate(row):
            combined[column] += multiplier * rat(coefficient)
    for multiplier, row in zip(equality_duals, A_eq):
        for column, coefficient in enumerate(row):
            combined[column] += multiplier * rat(coefficient)
    for column, multiplier in enumerate(lower_duals):
        combined[column] += multiplier
    dual_value = sum(
        multiplier * rat(rhs)
        for multiplier, rhs in zip(equality_duals, b_eq)
    )
    dual_exact = (
        all(value <= 0 for value in inequality_duals)
        and all(value >= 0 for value in lower_duals)
        and combined == exact_objective
        and dual_value == minimum
    )

    return {
        "minimum": str(minimum),
        "r_B_penalty": str(r_B_penalty),
        "primal_exact": primal_exact,
        "dual_exact": dual_exact,
        "r_A": str(solution[r_A]),
        "r_B": str(solution[r_B]),
        "gamma": [
            str(value)
            for value in solution[gamma_start:gamma_start + players]
        ],
        "positive_hinges": {
            str(coalition): str(solution[hinge_position[coalition]])
            for coalition in coalitions
            if solution[hinge_position[coalition]]
        },
        "dual_normalization_multiplier": str(equality_duals[-1]),
        "dual_hinge_multipliers": {
            str(coalition): str(-inequality_duals[index])
            for index, coalition in enumerate(coalitions)
            if inequality_duals[index]
        },
        "dual_equality_multipliers": {
            "potential_sum": str(equality_duals[0]),
            "witness_potential": str(equality_duals[1]),
            "normalization": str(equality_duals[2]),
        },
        "dual_lower_bound_multipliers": {
            ("r_A" if column == r_A else
             "r_B" if column == r_B else
             f"hinge_{coalitions[column - hinge_start]}"): str(multiplier)
            for column, multiplier in enumerate(lower_duals)
            if multiplier
        },
    }


def audit():
    rowmeta, mono_A, mono_B, roots, seconds = gluing.local_families()
    records = []
    root_only_absorbers = {}
    regularized_root_mbc_count = 0
    regularized_second_mbc_count = 0
    for root_index, root in enumerate(roots, 1):
        root_core, m_A, m_B, _root_alpha = gluing.lifted_root(
            root, rowmeta, mono_A, mono_B
        )
        regularized_root = dict(root_core)
        regularized_root[(1 << gluing.N)-1-(1 << gluing.A_PLAYER)] = (
            regularized_root.get(
                (1 << gluing.N)-1-(1 << gluing.A_PLAYER),F(0)
            ) + m_A
        )
        regularized_root[(1 << gluing.N)-1-(1 << gluing.B_PLAYER)] = (
            regularized_root.get(
                (1 << gluing.N)-1-(1 << gluing.B_PLAYER),F(0)
            ) + m_B
        )
        if (len(set(gluing.degree(regularized_root,gluing.N))) == 1
                and exact_incidence_rank(
                    tuple(regularized_root.items()),gluing.N
                ) == len(regularized_root)):
            regularized_root_mbc_count += 1
        root_only_absorbers[root_index] = absorption_subcollection(
            root_core, {}, m_A, require=False
        )
        for second_index, second in enumerate(seconds, 1):
            second_core, second_m_B, _second_alpha = gluing.lifted_second(
                second, rowmeta, mono_B
            )
            scale = m_B / second_m_B
            scaled_second = {
                coalition: scale * weight
                for coalition, weight in second_core.items()
            }
            assert scaled_second[gluing.B] == 2 * m_B
            regularized_second = dict(scaled_second)
            singleton_b = 1 << gluing.B_PLAYER
            regularized_second[singleton_b] = (
                regularized_second.get(singleton_b,F(0)) + m_B
            )
            if (len(set(gluing.degree(regularized_second,gluing.N))) == 1
                    and exact_incidence_rank(
                        tuple(regularized_second.items()),gluing.N
                    ) == len(regularized_second)):
                regularized_second_mbc_count += 1
            certificate = solve(root_core, scaled_second, m_A, m_B)
            absorber = absorption_subcollection(
                root_core, scaled_second, m_A
            )
            records.append({
                "root_index": root_index,
                "second_leaf_index": second_index,
                "m_A": str(m_A),
                "m_B": str(m_B),
                "root_core": {
                    str(coalition): str(weight)
                    for coalition, weight in sorted(root_core.items())
                },
                "scaled_second_core": {
                    str(coalition): str(weight)
                    for coalition, weight in sorted(scaled_second.items())
                },
                "absorber": absorber,
                **certificate,
            })

    minima = [F(record["minimum"]) for record in records]
    assert all(record["primal_exact"] and record["dual_exact"]
               for record in records)
    assert all(record["absorber"]["exact"] for record in records)
    return {
        "status": "exact capacity-one root-absorption audit",
        "geometry": {
            "players": gluing.N,
            "A_mask": gluing.A,
            "B_mask": gluing.B,
            "A_player": gluing.A_PLAYER,
            "B_player": gluing.B_PLAYER,
            "witness_mask": gluing.WITNESS,
        },
        "root_count": len(roots),
        "second_leaf_count": len(seconds),
        "root_second_pairs": len(records),
        "exact_certificate_count": sum(
            record["primal_exact"] and record["dual_exact"]
            for record in records
        ),
        "exact_absorber_count": sum(
            record["absorber"]["exact"] for record in records
        ),
        "root_only_absorber_count": sum(
            absorber is not None for absorber in root_only_absorbers.values()
        ),
        "regularized_root_minimal_balanced_count": (
            regularized_root_mbc_count
        ),
        "regularized_second_minimal_balanced_pair_count": (
            regularized_second_mbc_count
        ),
        "root_only_absorbing_indices": [
            index for index,absorber in root_only_absorbers.items()
            if absorber is not None
        ],
        "minimum_remainder": str(min(minima)),
        "uniform_remainder_bound": "1/3",
        "second_leaf_B_to_mono_ratio": "2",
        "implied_capacity_bound": (
            "tau_U >= 1 + 1/(3 max{q1_A/m_A, 2})"
        ),
        "negative_remainder_count": sum(value < 0 for value in minima),
        "zero_remainder_count": sum(value == 0 for value in minima),
        "remainder_histogram": {
            str(value): count
            for value, count in sorted(Counter(minima).items())
        },
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
