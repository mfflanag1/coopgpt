#!/usr/bin/env python3
"""Exact PXC139 falsifier to the strict-spectral single-dual price route.

The main hybrid inequality survives this game.  What fails is the proposed
intermediate theorem saying that, whenever B_*<c_n T, some optimal
zero-diagonal stationary dual has product-weighted diagonal defect at most
O-c_n T.  Here the strict spectral hypothesis holds, but the minimum defect
is 54/17 while O-c_n T is only 2/3.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(HERE.parent), str(HERE.parent / "search_archive")]

from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from unrestricted_pxc91c_exact_search import selector_pair  # noqa: E402


N, TOTAL = 6, F(8)
DEFINING = {15: F(4), 29: F(6), 30: F(6), 37: F(2), 38: F(2), 52: F(2), 59: F(8)}
X = (F(1), F(1), F(0), F(5, 2), F(5, 2), F(1))
Z = (F(2), F(2), F(0), F(2), F(2), F(0))


def zero_primal():
    pi = tuple(map(F, (F(2, 17), F(2, 17), 0, F(23, 68), F(5, 17), F(9, 68))))
    flow = [[F(0)] * N for _ in range(N)]
    for (r, i), value in {
        (0, 3): F(1, 17), (0, 4): F(1, 34), (0, 5): F(1, 34),
        (1, 3): F(1, 17), (1, 4): F(1, 34), (1, 5): F(1, 34),
        (3, 0): F(23, 272), (3, 1): F(23, 272), (3, 4): F(23, 136),
        (4, 3): F(15, 68), (4, 5): F(5, 68),
        (5, 0): F(9, 272), (5, 1): F(9, 272), (5, 4): F(9, 136),
    }.items():
        flow[r][i] = value
    ux = tuple(map(F, (F(16, 17), F(16, 17), 0, F(5, 2), F(40, 17), F(1))))
    uz = tuple(map(F, (F(16, 17), F(16, 17), 0, F(2), F(2), 0)))
    return pi, tuple(map(tuple, flow)), ux, uz


def released_primal():
    pi = tuple(map(F, (F(265, 2176), F(265, 2176), 0, F(3599, 10880), F(809, 2720), F(279, 2176))))
    flow = (
        tuple(map(F, (F(1, 640), F(1, 640), 0, F(1257, 21760), F(1393, 43520), F(1257, 43520)))),
        tuple(map(F, (F(1, 640), F(1, 640), 0, F(1257, 21760), F(1393, 43520), F(1257, 43520)))),
        (F(0),) * N,
        tuple(map(F, (F(3599, 43520), F(3599, 43520), 0, 0, F(3599, 21760), 0))),
        tuple(map(F, (F(1, 256), F(1, 256), 0, F(1171, 5440), F(1, 256), F(1533, 21760)))),
        tuple(map(F, (F(279, 8704), F(279, 8704), 0, 0, F(279, 4352), 0))),
    )
    ux = tuple(map(F, (F(265, 272), F(265, 272), 0, F(5, 2), F(809, 340), F(1))))
    uz = tuple(map(F, (F(265, 272), F(265, 272), 0, F(2), F(2), 0)))
    return pi, flow, ux, uz


def replay_primal(values, certificate, cap_scale):
    pi, flow, ux, uz = certificate
    full = (1 << N) - 1
    diagonal = tuple(X[i] * Z[i] / TOTAL**2 for i in range(N))
    if sum(pi) != 1:
        raise AssertionError("mass")
    for r in range(N):
        if min(flow[r]) < 0 or sum(flow[r]) != pi[r] or flow[r][r] > cap_scale * diagonal[r]:
            raise AssertionError(("flow row", r))
        for coalition in range(1, full):
            load = sum(flow[r][i] for i in range(N) if coalition >> i & 1)
            if TOTAL * load < pi[r] * values[coalition]:
                raise AssertionError(("core row", r, coalition))
    for i in range(N):
        if sum(flow[r][i] for r in range(N)) != pi[i]:
            raise AssertionError(("column", i))
        if not 0 <= ux[i] <= min(X[i], TOTAL * pi[i]):
            raise AssertionError(("ux", i))
        if not 0 <= uz[i] <= min(Z[i], TOTAL * pi[i]):
            raise AssertionError(("uz", i))
    return sum(ux) + sum(uz) - TOTAL


def optimal_face_dual(values):
    full = (1 << N) - 1
    theta = F(104, 17)
    alpha = tuple(map(F, (0, 0, 1, 1, 0, 1)))
    beta = tuple(map(F, (0, 0, 1, 1, 1, 1)))
    p = tuple(map(F, (1, 1, 0, 0, 1, 0)))
    q = tuple(map(F, (1, 1, 0, 0, 0, 0)))
    A = tuple(F(k, 17) for k in (176, 32, 0, 288, 176, 288))
    B = tuple(F(k, 17) for k in (0, 0, 0, 176, 144, 176))
    lambdas = {
        (0, 11): F(4, 17), (0, 29): F(22, 17), (0, 33): F(26, 17), (0, 59): F(18, 17),
        (1, 11): F(4, 17), (1, 26): F(22, 17), (1, 34): F(26, 17),
        (3, 30): F(18, 17), (3, 59): F(18, 17), (3, 61): F(18, 17),
        (4, 25): F(22, 17), (4, 26): F(22, 17), (4, 48): F(44, 17),
        (5, 29): F(18, 17), (5, 30): F(18, 17), (5, 59): F(18, 17),
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values, x, z = selector_pair(DEFINING, N, TOTAL)
    if x != X or z != Z:
        raise AssertionError("selectors changed")
    spectral = spectral_decomposition("PXC139", values, x, z)
    bstar = F(spectral["sharpened_spectral_bound_ratio"]) * TOTAL
    target = F(2, 3) * TOTAL
    overlap = sum(min(a, b) for a, b in zip(x, z))
    psi = replay_primal(values, zero_primal(), F(0))
    released = replay_primal(values, released_primal(), F(1, 20))
    dual_value, defects, exposure = optimal_face_dual(values)
    if not (bstar == 5 < target == F(16, 3) < psi == F(191, 34) < overlap == 6):
        raise AssertionError("strict spectral ordering changed")
    if dual_value != TOTAL + psi or released != F(491, 85):
        raise AssertionError("primal-dual endpoint changed")
    if dual_value + F(1, 20) * exposure != TOTAL + released:
        raise AssertionError("matching release tangent")
    if not exposure == F(54, 17) > overlap - target == F(2, 3):
        raise AssertionError("single-dual no-go vanished")
    payload = {
        "claim": "PXC139 strict-spectral single-optimal-dual price no-go",
        "defining_rows": {str(mask): str(value) for mask, value in DEFINING.items()},
        "selectors": {"x": list(map(str, x)), "z": list(map(str, z))},
        "spectral_bound": str(bstar), "target": str(target), "overlap": str(overlap),
        "stationary_value": str(psi), "stationary_margin": str(psi - target),
        "minimum_optimal_face_exposure": str(exposure),
        "available_overlap_above_target": str(overlap - target),
        "exposure_excess": str(exposure - (overlap - target)),
        "dual_defects": list(map(str, defects)),
        "release_control": {"t": "1/20", "value": str(released), "matching_affine_dual": True},
        "conclusion": "B_*<c_nT does not imply an optimal zero-diagonal dual with E<=O-c_nT",
        "main_inequality_status": "not a counterexample: Psi_stat exceeds c_nT by 29/102",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
