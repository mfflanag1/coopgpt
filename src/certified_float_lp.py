"""Fast LP proposals with exact rational primal--dual verification.

All variables are free; finite bounds should be supplied as inequality rows.
The floating solver is used only to propose a basis. A result is returned only
after rational reconstruction proves primal feasibility, dual feasibility,
stationarity, and equality of the two objective values exactly.
"""
from __future__ import annotations

from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog


def rational(value, denominator=10_000_000):
    return F(float(value)).limit_denominator(denominator)


def dot(left, right):
    return sum((F(a) * F(b) for a, b in zip(left, right)), F(0))


def certified_lp_min(c, A_ub, b_ub, A_eq, b_eq):
    """Return an exactly certified optimum and point for a free-variable LP."""
    variable_count = len(c)
    result = linprog(
        np.asarray([float(F(value)) for value in c]),
        A_ub=(
            np.asarray([[float(F(value)) for value in row] for row in A_ub])
            if A_ub else None
        ),
        b_ub=(
            np.asarray([float(F(value)) for value in b_ub]) if b_ub else None
        ),
        A_eq=(
            np.asarray([[float(F(value)) for value in row] for row in A_eq])
            if A_eq else None
        ),
        b_eq=(
            np.asarray([float(F(value)) for value in b_eq]) if b_eq else None
        ),
        bounds=[(None, None)] * variable_count,
        method="highs",
    )
    if not result.success:
        return None, None, {"status": result.message}

    point = [rational(value) for value in result.x]
    inequality_duals = (
        [rational(value) for value in result.ineqlin.marginals]
        if A_ub else []
    )
    equality_duals = (
        [rational(value) for value in result.eqlin.marginals]
        if A_eq else []
    )
    primal_value = dot(c, point)
    dual_value = sum(
        (multiplier * F(rhs)
         for multiplier, rhs in zip(inequality_duals, b_ub)),
        F(0),
    ) + sum(
        (multiplier * F(rhs)
         for multiplier, rhs in zip(equality_duals, b_eq)),
        F(0),
    )

    primal_exact = (
        all(dot(row, point) <= F(rhs) for row, rhs in zip(A_ub, b_ub))
        and all(dot(row, point) == F(rhs) for row, rhs in zip(A_eq, b_eq))
    )
    dual_exact = all(value <= 0 for value in inequality_duals)
    stationarity = []
    for column in range(variable_count):
        stationarity.append(
            sum(
                (multiplier * F(row[column])
                 for multiplier, row in zip(inequality_duals, A_ub)),
                F(0),
            )
            + sum(
                (multiplier * F(row[column])
                 for multiplier, row in zip(equality_duals, A_eq)),
                F(0),
            )
        )
    dual_exact = dual_exact and stationarity == [F(value) for value in c]
    objective_exact = primal_value == dual_value
    if not (primal_exact and dual_exact and objective_exact):
        return None, None, {
            "status": "rational reconstruction failed exact verification",
            "primal_exact": primal_exact,
            "dual_exact": dual_exact,
            "objective_exact": objective_exact,
        }
    return primal_value, point, {
        "status": "exact rational primal-dual certificate",
        "inequality_duals": inequality_duals,
        "equality_duals": equality_duals,
        "dual_value": dual_value,
    }
