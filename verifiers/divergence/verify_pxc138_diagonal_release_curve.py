#!/usr/bin/env python3
"""Exact audit of the PXC138 diagonal-release value curve.

For d_r=x_r z_r/T^2 and 0<=t<=1, PXC138 caps the formerly forbidden
diagonal by F_rr<=t d_r.  LP duality gives the exact envelope

  T+Phi(t) = min_{q in D} D(q)+t E(q),
  E(q)=sum_r d_r [Delta_r(q)]_+,

where D is the zero-diagonal PXC136 dual feasible region.  Hence the true
stationary price is the integral of the decreasing diagonal shadow price;
it is not generally the defect of one optimal zero-diagonal dual.

The sharp total-four control supplies an exact falsifier to the tempting
unconditional identification of one optimal-face defect with the total
price.  Its curve is

  Phi(t)=45/17+min(9t/17,1/51).

All arithmetic below is rational.  The dimension-free statement itself is
ordinary parametric LP duality; this file pins its load-bearing signs and
the exact strict control.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]


def csum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def sharp_data():
    item = json.loads((ROOT / "verifiers/s6/harvest6_601.json").read_text())["records"][125]
    values = tuple(map(F, item["v"]))
    x = tuple(map(F, item["lmin"]))
    z = tuple(map(F, item["lmax"]))
    expected_x = (F(4, 3), F(1, 3), F(1, 3), F(1, 3), F(4, 3), F(1, 3))
    expected_z = (F(1), F(1), F(0), F(0), F(1), F(1))
    if x != expected_x or z != expected_z:
        raise AssertionError("sharp selector control changed")
    return values, x, z


def zero_diagonal_primal():
    pi = tuple(map(F, (F(23, 68), F(2, 17), F(1, 12), F(5, 102), F(5, 17), F(2, 17))))
    flow = [[F(0)] * 6 for _ in range(6)]
    arcs = {
        (0, 1): F(23, 272), (0, 4): F(23, 136), (0, 5): F(23, 272),
        (1, 0): F(1, 17), (1, 2): F(1, 102), (1, 3): F(1, 51),
        (1, 4): F(1, 34), (2, 1): F(1, 48), (2, 4): F(1, 24),
        (2, 5): F(1, 48), (3, 1): F(5, 408), (3, 4): F(5, 204),
        (3, 5): F(5, 408), (4, 0): F(15, 68), (4, 2): F(5, 68),
        (5, 0): F(1, 17), (5, 3): F(1, 34), (5, 4): F(1, 34),
    }
    for edge, value in arcs.items():
        flow[edge[0]][edge[1]] = value
    ux = tuple(map(F, (F(4, 3), F(1, 3), F(1, 3), F(10, 51), F(20, 17), F(1, 3))))
    uz = tuple(map(F, (F(1), F(8, 17), F(0), F(0), F(1), F(8, 17))))
    return pi, tuple(map(tuple, flow)), ux, uz


def breakpoint_primal():
    pi = tuple(map(F, (F(1, 3), F(13, 108), F(1, 12), F(5, 108), F(8, 27), F(13, 108))))
    flow = (
        tuple(map(F, (0, F(1, 12), 0, 0, F(1, 6), F(1, 12)))),
        tuple(map(F, (F(19, 324), F(1, 1296), F(1, 81), F(11, 648), F(5, 162), F(1, 1296)))),
        tuple(map(F, (0, F(1, 48), 0, 0, F(1, 24), F(1, 48)))),
        tuple(map(F, (0, F(5, 432), 0, 0, F(5, 216), F(5, 432)))),
        tuple(map(F, (F(35, 162), F(1, 324), F(23, 324), 0, F(1, 324), F(1, 324)))),
        tuple(map(F, (F(19, 324), F(1, 1296), 0, F(19, 648), F(5, 162), F(1, 1296)))),
    )
    ux = tuple(map(F, (F(4, 3), F(1, 3), F(1, 3), F(5, 27), F(32, 27), F(1, 3))))
    uz = tuple(map(F, (F(1), F(13, 27), 0, 0, F(1), F(13, 27))))
    return pi, flow, ux, uz


def replay_primal(values, x, z, certificate, cap_scale):
    total = sum(x, F(0))
    n = len(x)
    full = (1 << n) - 1
    pi, flow, ux, uz = certificate
    diagonal = tuple(x[i] * z[i] / (total * total) for i in range(n))
    if sum(pi, F(0)) != 1:
        raise AssertionError("primal mass")
    for r in range(n):
        if sum(flow[r], F(0)) != pi[r] or any(value < 0 for value in flow[r]):
            raise AssertionError(("primal row", r))
        if flow[r][r] > cap_scale * diagonal[r]:
            raise AssertionError(("diagonal cap", r))
        for coalition in range(1, full):
            load = sum(flow[r][i] for i in range(n) if coalition >> i & 1)
            if total * load < pi[r] * values[coalition]:
                raise AssertionError(("primal core", r, coalition))
    for i in range(n):
        if sum(flow[r][i] for r in range(n)) != pi[i]:
            raise AssertionError(("primal column", i))
        if not 0 <= ux[i] <= min(x[i], total * pi[i]):
            raise AssertionError(("ux", i))
        if not 0 <= uz[i] <= min(z[i], total * pi[i]):
            raise AssertionError(("uz", i))
    linear_value = sum(ux, F(0)) + sum(uz, F(0))
    return linear_value - total


def minimum_slope_dual(values, x, z):
    total = sum(x, F(0))
    n = len(x)
    full = (1 << n) - 1
    theta = F(45, 17)
    alpha = tuple(map(F, (1, 1, 0, 0, 0, 1)))
    beta = tuple(map(F, (1, 0, 1, 1, 1, 0)))
    p = tuple(map(F, (0, 0, 1, 1, 1, 0)))
    q = tuple(map(F, (0, 1, 0, 0, 0, 1)))
    A = tuple(F(k, 17) for k in (28, 40, 72, 18, 50, 40))
    B = tuple(F(k, 17) for k in (50, 0, -18, -18, 10, 0))
    lambdas = {
        (0, 19): F(7, 17), (0, 33): F(9, 34), (0, 61): F(5, 34),
        (1, 14): F(11, 34), (1, 19): F(25, 34), (1, 35): F(10, 17),
        (2, 14): F(11, 34), (2, 19): F(25, 34), (2, 33): F(10, 17), (2, 61): F(8, 17),
        (3, 3): F(2, 17), (3, 9): F(8, 17), (3, 19): F(5, 34), (3, 49): F(9, 34),
        (4, 19): F(25, 34), (4, 20): F(8, 17), (4, 49): F(25, 34),
        (5, 35): F(10, 17), (5, 44): F(11, 34), (5, 49): F(25, 34),
    }
    for i in range(n):
        if min(alpha[i], beta[i], p[i], q[i]) < 0:
            raise AssertionError("negative cap multiplier")
        if alpha[i] + p[i] < 1 or beta[i] + q[i] < 1:
            raise AssertionError(("dual cap", i))
        pi_row = theta - A[i] - B[i]
        pi_row += sum(lambdas.get((i, s), F(0)) * values[s] for s in range(1, full))
        pi_row -= total * (p[i] + q[i])
        if pi_row < 0:
            raise AssertionError(("dual pi", i, pi_row))
    defects = []
    for r in range(n):
        loads = []
        for i in range(n):
            load = total * sum(
                (lambdas.get((r, s), F(0)) for s in range(1, full) if s >> i & 1),
                F(0),
            )
            loads.append(load)
            if i != r and A[r] + B[i] < load:
                raise AssertionError(("dual arc", r, i))
        defects.append(loads[r] - A[r] - B[r])
    objective = theta + sum(alpha[i] * x[i] + beta[i] * z[i] for i in range(n))
    diagonal = tuple(x[i] * z[i] / (total * total) for i in range(n))
    exposure = sum(diagonal[i] * max(F(0), defects[i]) for i in range(n))
    return objective, tuple(defects), exposure


def sharp_curve():
    values, x, z = sharp_data()
    zero_value = replay_primal(values, x, z, zero_diagonal_primal(), F(0))
    break_value = replay_primal(values, x, z, breakpoint_primal(), F(1, 27))
    dual_value, defects, exposure = minimum_slope_dual(values, x, z)
    total = sum(x, F(0))
    overlap = sum(min(a, b) for a, b in zip(x, z))
    if zero_value != F(45, 17) or dual_value - total != zero_value:
        raise AssertionError("zero endpoint mismatch")
    if break_value != overlap or overlap - zero_value != F(1, 51):
        raise AssertionError("breakpoint endpoint mismatch")
    if exposure != F(9, 17) or F(1, 27) * exposure != overlap - zero_value:
        raise AssertionError("breakpoint slope mismatch")
    if not dual_value < total + overlap or dual_value + F(1, 27) * exposure != total + overlap:
        raise AssertionError("diagonal penalty is not load-bearing")
    # Convex interpolation of the two displayed primals gives the lower
    # affine segment; the displayed dual gives the matching upper segment.
    return {
        "zero_diagonal_value": str(zero_value),
        "overlap": str(overlap),
        "price": str(overlap - zero_value),
        "first_saturation_parameter": "1/27",
        "minimum_optimal_face_exposure": str(exposure),
        "factor_over_true_price": str(exposure / (overlap - zero_value)),
        "dual_defects": list(map(str, defects)),
        "exact_curve": "Phi(t)=45/17+min(9t/17,1/51), 0<=t<=1",
        "proof": "convex interpolation of exact t=0 and t=1/27 primals plus the exact zero-diagonal dual of exposure 9/17",
        "fail_open_control": "omitting the tE penalty leaves dual value 113/17 below the required t=1/27 value 20/3",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "PXC138 exact diagonal-release curve and integrated shadow price",
        "theorem": {
            "primal": "Phi(t) is PXC136 with 0<=F_rr<=t*x_r*z_r/T^2",
            "dual_envelope": "T+Phi(t)=min_D D+t*sum_r(x_r*z_r/T^2)[Delta_r]_+",
            "endpoints": "Phi(0)=Psi_stat and Phi(1)=O",
            "price": "O-Psi_stat is the integral from 0 to 1 of the decreasing optimal diagonal shadow exposure",
            "right_slope_zero": "Phi'_+(0)=min exposure over the optimal zero-diagonal dual face",
        },
        "sharp_control": sharp_curve(),
        "falsified_strengthening": "minimum optimal-face exposure need not equal O-Psi_stat; the sharp ratio is 27",
        "scope": "dimension-free parametric LP theorem and exact sharp falsifier; the spectral/common/reciprocal bound on the integrated price remains open",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
