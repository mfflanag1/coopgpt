#!/usr/bin/env python3
"""Independent exact staged-selector calibration for PXC147.

This standalone implementation quotients the full core by U/E symmetry,
generates every coalition-count orbit directly, and solves every selector
stage with fresh Z3 QF_LRA models.  The paper proof, not these finite cases,
supplies the universal quantifiers.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3


def zq(value):
    return z3.Q(value.numerator, value.denominator)


def fq(value):
    value = z3.simplify(value)
    if z3.is_int_value(value):
        return F(value.as_long())
    return F(value.numerator_as_long(), value.denominator_as_long())


def family(m, r, transfer):
    h = F(2 * m, r - 1)
    bx, cx = F(m) + h, F(m) + r * h
    p, q, s = r * h + 1, h + 1, F(m + 1)
    total = F(m) + 2 * r * h + r + 2
    points = (
        (F(1),) * m + (bx, cx, F(1)) + (F(1),) * r + (F(1),),
        (F(0),) * m + (F(0), F(0), p) + (q,) * r + (s,),
        (F(0),) * m + (bx + 2, total - bx - 2, F(0)) + (F(0),) * r + (F(0),),
        (F(0),) * m + (F(0), transfer, p - transfer) + (q,) * r + (s,),
    )
    return points, (h, bx, cx, p, q, s, total)


def coalition_orbits(points, m, r):
    rows = []
    for uc in range(m + 1):
        for ec in range(r + 1):
            for bits in range(16):
                if (uc, ec, bits) == (m, r, 15):
                    continue
                coefficients = (
                    uc, bits & 1, (bits >> 1) & 1,
                    (bits >> 2) & 1, ec, (bits >> 3) & 1,
                )
                players = (
                    tuple(range(uc))
                    + ((m,) if bits & 1 else ())
                    + ((m + 1,) if bits & 2 else ())
                    + ((m + 2,) if bits & 4 else ())
                    + tuple(range(m + 3, m + 3 + ec))
                    + ((m + 3 + r,) if bits & 8 else ())
                )
                bound = min(
                    sum((point[player] for player in players), F(0))
                    for point in points
                )
                rows.append((coefficients, bound))
    return rows


def optimize(constraints, expression, maximize):
    solver = z3.Optimize()
    solver.add(*constraints)
    handle = solver.maximize(expression) if maximize else solver.minimize(expression)
    assert solver.check() == z3.sat
    return fq(handle.value())


def selector(points, m, r, mode):
    multiplicities = (m, 1, 1, 1, r, 1)
    total = sum(points[0], F(0))
    y = z3.Reals(f"u_{mode} b_{mode} c_{mode} d_{mode} e_{mode} g_{mode}")
    base = [sum(multiplicities[i] * y[i] for i in range(6)) == zq(total)]
    rows = coalition_orbits(points, m, r)
    for coefficients, bound in rows:
        base.append(sum(coefficients[i] * y[i] for i in range(6)) >= zq(bound))
    fixed, free, stages = {}, list(range(6)), []
    while free:
        prefix = base + [y[i] == zq(value) for i, value in fixed.items()]
        level_variable = z3.Real(f"level_{mode}_{len(stages)}")
        if mode == "min":
            level = optimize(prefix + [y[i] >= level_variable for i in free], level_variable, True)
            face = prefix + [y[i] >= zq(level) for i in free]
            pinned = [i for i in free if optimize(face, y[i], True) == level]
        else:
            level = optimize(prefix + [y[i] <= level_variable for i in free], level_variable, False)
            face = prefix + [y[i] <= zq(level) for i in free]
            pinned = [i for i in free if optimize(face, y[i], False) == level]
        assert pinned
        stages.append({"level": str(level), "pinned_roles": pinned})
        for role in pinned:
            fixed[role] = level
            free.remove(role)
    return tuple(fixed[i] for i in range(6)), stages, len(rows)


def predicted(m, r, parameters):
    h, bx, cx, p, q, s, total = parameters
    x = (F(1), bx, cx, F(1), F(1), F(1))
    if r == 2:
        z = (F(1, 5 * m), F(3, 5), F(10 * m + 3, 5),
             F(10 * m + 3, 5), F(10 * m + 3, 5), F(5 * m + 4, 5))
    elif h <= 1:
        lam, M = (1 - h) / (3 * m), (p + s) / 3
        z = (lam, lam * bx, M, M, q - lam * h, M)
    else:
        z = (F(0), F(0), p / 2, p / 2, q, s)
    return x, z, total


def check_case(m, r, transfer):
    points, parameters = family(m, r, transfer)
    expected_x, expected_z, total = predicted(m, r, parameters)
    got_x, min_stages, orbit_count = selector(points, m, r, "min")
    got_z, max_stages, _ = selector(points, m, r, "max")
    assert got_x == expected_x, (m, r, got_x, expected_x)
    assert got_z == expected_z, (m, r, got_z, expected_z)
    multiplicities = (m, 1, 1, 1, r, 1)
    rho = sum(multiplicities[i] * abs(got_x[i] - got_z[i]) for i in range(6)) / total
    return {
        "m": m, "r": r, "transfer": str(transfer), "h": str(parameters[0]),
        "coalition_orbits": orbit_count,
        "Lmin_roles": list(map(str, got_x)), "Lmax_roles": list(map(str, got_z)),
        "rho": str(rho), "Lmin_stages": min_stages, "Lmax_stages": max_stages,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    specifications = [(m, 2, F(7 * m + 1, 2)) for m in range(1, 5)]
    for m, r in ((1, 4), (1, 8), (2, 6), (1, 3), (2, 3), (4, 4), (4, 8)):
        _, parameters = family(m, r, F(0))
        p = parameters[3]
        specifications.extend((m, r, scale * p) for scale in (F(1, 2), F(3, 4), F(1)))
    cases = [check_case(*specification) for specification in specifications]

    # Fail-open control: below p/2 the theorem formula changes.
    m, r = 2, 3
    _, parameters = family(m, r, F(0))
    control_transfer = parameters[3] / 4
    points, parameters = family(m, r, control_transfer)
    got_z, _, _ = selector(points, m, r, "max")
    _, theorem_z, _ = predicted(m, r, parameters)
    assert got_z != theorem_z

    payload = {
        "claim": "independent exact role-orbit staged calibration of PXC147",
        "implementation": "standalone Z3 QF_LRA; no project selector or primary-verifier imports",
        "cases": cases,
        "negative_control": {
            "m": m, "r": r, "transfer": str(control_transfer),
            "formula_changed_below_p_over_2": True,
            "observed_Lmax_roles": list(map(str, got_z)),
        },
        "scope": "finite independent calibration; the conventional proof supplies all m,r",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
