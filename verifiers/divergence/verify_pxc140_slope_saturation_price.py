#!/usr/bin/env python3
"""Exact audit of the PXC140 slope-times-saturation price theorem.

For the concave diagonal-release curve Psi_t, let e0=Psi'_+(0) and let tau
be the first t with Psi_t=O.  Monotonicity of the right slope gives

    O-Psi = integral_0^tau Phi'_+(t) dt <= tau*e0.

Thus tau*e0<=O-c_nT is a sufficient hybrid-overlap certificate.  This file
checks the sharp equality control and an exact strict-spectral PXC139
control.  The latter is important: its pointwise e0 bound fails, while the
two-factor theorem succeeds.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from verify_pxc138_diagonal_release_curve import sharp_curve
from verify_pxc139_strict_spectral_single_dual_no_go import (
    DEFINING, N, TOTAL, X, Z, optimal_face_dual, replay_primal, selector_pair,
)


def saturation_primal():
    pi = tuple(map(F, (F(19, 144), F(19, 144), 0, F(5, 16), F(11, 36), F(17, 144))))
    flow = (
        tuple(map(F, (F(7, 1296), F(7, 1296), 0, F(143, 2592), F(199, 5184), F(143, 5184)))),
        tuple(map(F, (F(7, 1296), F(7, 1296), 0, F(143, 2592), F(199, 5184), F(143, 5184)))),
        (F(0),) * N,
        tuple(map(F, (F(5, 64), F(5, 64), 0, 0, F(5, 32), 0))),
        tuple(map(F, (F(35, 2592), F(35, 2592), 0, F(131, 648), F(35, 2592), F(163, 2592)))),
        tuple(map(F, (F(17, 576), F(17, 576), 0, 0, F(17, 288), 0))),
    )
    ux = tuple(map(F, (1, 1, 0, F(5, 2), F(22, 9), F(17, 18))))
    uz = tuple(map(F, (F(19, 18), F(19, 18), 0, 2, 2, 0)))
    return pi, flow, ux, uz


def left_saturation_dual(values):
    full = (1 << N) - 1
    theta = F(90, 17)
    alpha = tuple(map(F, (1, 1, 1, 1, 0, 0)))
    beta = tuple(map(F, (0, 0, 1, 1, 1, 1)))
    p = tuple(map(F, (0, 0, 0, 0, 1, 1)))
    q = tuple(map(F, (1, 1, 0, 0, 0, 0)))
    A = tuple(F(k, 17) for k in (100, 80, 36, 148, 100, 0))
    B = tuple(F(k, 17) for k in (0, 0, 0, 100, 20, -36))
    lambdas = {
        (0, 11): F(10, 17), (0, 29): F(25, 34), (0, 33): F(11, 34), (0, 59): F(5, 34),
        (1, 15): F(10, 17), (1, 26): F(25, 34), (1, 34): F(11, 34),
        (2, 8): F(10, 17), (2, 24): F(5, 34), (2, 31): F(9, 34),
        (3, 15): F(9, 34), (3, 30): F(7, 17), (3, 59): F(7, 17), (3, 61): F(7, 17),
        (4, 25): F(25, 34), (4, 26): F(25, 34), (4, 48): F(8, 17),
        (5, 56): F(5, 34),
    }
    for i in range(N):
        if alpha[i] + p[i] < 1 or beta[i] + q[i] < 1:
            raise AssertionError(("dual cap", i))
        root = theta - A[i] - B[i]
        root += sum(lambdas.get((i, s), F(0)) * values[s] for s in range(1, full))
        root -= TOTAL * (p[i] + q[i])
        if root < 0:
            raise AssertionError(("dual root", i, root))
    defects = []
    for r in range(N):
        loads = []
        for i in range(N):
            load = TOTAL * sum(
                (lambdas.get((r, s), F(0)) for s in range(1, full) if s >> i & 1), F(0)
            )
            loads.append(load)
            if i != r and A[r] + B[i] < load:
                raise AssertionError(("dual arc", r, i))
        defects.append(loads[r] - A[r] - B[r])
    objective = theta + sum(alpha[i] * X[i] + beta[i] * Z[i] for i in range(N))
    diagonal = tuple(X[i] * Z[i] / TOTAL**2 for i in range(N))
    exposure = sum(diagonal[i] * max(F(0), defects[i]) for i in range(N))
    return objective, tuple(defects), exposure


def pxc139_control():
    values, x, z = selector_pair(DEFINING, N, TOTAL)
    if x != X or z != Z:
        raise AssertionError("PXC139 selectors changed")
    tau = F(14, 81)
    overlap = sum(min(a, b) for a, b in zip(x, z))
    saturation_value = replay_primal(values, saturation_primal(), tau)
    if saturation_value != overlap:
        raise AssertionError("saturation primal misses box")
    left_objective, left_defects, left_exposure = left_saturation_dual(values)
    if not left_exposure > 0 or left_objective + tau * left_exposure != TOTAL + overlap:
        raise AssertionError("saturation supporting dual")
    # Positive left slope and a supporting line meeting O at tau prove that
    # no smaller t can already attain O.
    zero_objective, _zero_defects, e0 = optimal_face_dual(values)
    psi = zero_objective - TOTAL
    price = overlap - psi
    product = tau * e0
    target_surplus = overlap - F(16, 3)
    if not price <= product == F(28, 51) < target_surplus == F(2, 3):
        raise AssertionError("two-factor price control")
    return {
        "tau_star": str(tau), "initial_slope": str(e0),
        "slope_times_tau": str(product), "true_price": str(price),
        "available_overlap_above_target": str(target_surplus),
        "left_saturation_slope": str(left_exposure),
        "left_saturation_defects": list(map(str, left_defects)),
        "pointwise_route_fails": e0 > target_surplus,
        "two_factor_route_succeeds": product < target_surplus,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sharp = sharp_curve()
    sharp_tau, sharp_e0 = F(1, 27), F(9, 17)
    if sharp_tau * sharp_e0 != F(sharp["price"]):
        raise AssertionError("sharp slope-saturation equality")
    payload = {
        "claim": "PXC140 slope-times-saturation price theorem",
        "theorem": {
            "tau": "first t in [0,1] with Psi_t=O",
            "initial_slope": "e0=Psi'_+(0)=minimum E on the optimal zero-diagonal dual face",
            "bound": "O-Psi<=tau*e0",
            "hybrid_certificate": "tau*e0<=O-c_nT implies Psi>=c_nT",
            "mechanism_split": "e0 is staged dual price per diagonal unit; tau is minimum primal box-saturation capacity",
        },
        "sharp_equality_control": {
            "tau_star": str(sharp_tau), "initial_slope": str(sharp_e0),
            "product": str(sharp_tau * sharp_e0), "true_price": sharp["price"],
        },
        "strict_spectral_pxc139_control": pxc139_control(),
        "scope": "dimension-free concavity theorem and two exact controls; deriving the product bound from PXC112/PXC114 remains open",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
