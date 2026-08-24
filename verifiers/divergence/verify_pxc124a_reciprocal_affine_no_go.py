#!/usr/bin/env python3
"""Independent symbolic and exact-grid audit of the PXC124a selector-profile no-go."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import sympy as sp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    M, A, B, j, k, s = sp.symbols("M A B j k s")
    T = 2 * M + A + B + j + k
    u = (A + j + k - s) / 3
    expr_high = sp.factor(sp.Rational(2, 3) * T - (2 * M + j + k + 2 * u))
    expr_low = sp.factor(sp.Rational(2, 3) * T - (2 * M + j + u + 2 * u))
    expr_u_above_B = sp.factor(
        sp.Rational(2, 3) * T - (2 * M + j + k + B + u)
    )
    assert sp.simplify(
        expr_high - (2 * B - 2 * M - 3 * j - 3 * k + 2 * s) / 3
    ) == 0
    assert sp.simplify(
        expr_low - (-A + 2 * B - 2 * M - 4 * j - k + 3 * s) / 3
    ) == 0
    assert sp.simplify(
        expr_u_above_B - (-2 * M + A - B - 2 * j - 2 * k + s) / 3
    ) == 0

    checked = 0
    maximum = None
    witness = None
    for Mi in range(4, 13):
        for Ai in range(2, Mi):
            for Bi in range(1, Ai):
                for ji in range(Bi):
                    for ki in range(ji, Bi):
                        for si in range(Ai - Bi):
                            Mf, Af, Bf = F(Mi), F(Ai), F(Bi)
                            jf, kf, sf = F(ji), F(ki), F(si)
                            uf = (Af + jf + kf - sf) / 3
                            xa = uf + sf
                            residual_x = sorted((uf, uf, uf, xa), reverse=True)
                            residual_z = sorted((Af, Bf, jf, kf))
                            bh_res = sum((min(xv, zv)
                                          for xv, zv in zip(residual_x, residual_z)), F(0))
                            total = 2 * Mf + Af + Bf + jf + kf
                            slack = F(2, 3) * total - (2 * Mf + bh_res)
                            checked += 1
                            if maximum is None or slack > maximum:
                                maximum = slack
                                witness = (Mi, Ai, Bi, ji, ki, si)
                            assert slack < 0
    payload = {
        "claim": "asymmetric PXC104 selector lane has B_H>2T/3",
        "symbolic_branches": {
            "u_between_k_and_B": str(expr_high),
            "u_below_k": str(expr_low),
            "u_above_B": str(expr_u_above_B),
        },
        "exact_grid_profiles": checked,
        "largest_target_minus_BH": str(maximum),
        "largest_slack_parameters_M_A_B_j_k_s": list(witness),
        "scope": (
            "conditional selector-profile theorem plus exact integer-grid "
            "regression; not an exhaustive reciprocal-incidence theorem"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
