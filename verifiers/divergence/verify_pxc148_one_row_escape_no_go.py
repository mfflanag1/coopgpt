#!/usr/bin/env python3
"""Exact incidence-cone audit of the PXC148 one-row escape no-go.

For a symmetric replacement row F_i={e_i} union W, W subset {b,c,d,g},
the script solves the nonnegative incidence identity that would pin
E\{e_i} using N and the retained PXC147 rows.  The conventional proof
solves the same seven load equations for symbolic r.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3


ROLE_NAMES = ("b", "c", "d", "g")
EXPECTED = {
    0b0001: ("be_i", ("1", "0", "1", "0", "1", "0")),
    0b1001: ("be_i g", ("2", "1", "1", "0", "1", "0")),
    0b1111: ("bcde_i g", ("1", "0", "0", "0", "1", "0")),
}


def text(value):
    value = z3.simplify(value)
    if z3.is_int_value(value):
        return str(value.as_long())
    if value.denominator_as_long() == 1:
        return str(value.numerator_as_long())
    return f"{value.numerator_as_long()}/{value.denominator_as_long()}"


def solve(row_bits, r, nonnegative=True):
    # Coordinates: U,b,c,d,e_i,E_other,g.
    N = (1, 1, 1, 1, 1, 1, 1)
    R3 = (0, 1, 1, 1, 1, 1, 0)
    R4 = (0, 0, 1, 1, 0, 0, 1)
    R7 = (0, 0, 1, 0, 1, 1, 1)
    one = (
        0, row_bits & 1, (row_bits >> 1) & 1,
        (row_bits >> 2) & 1, 1, 0, (row_bits >> 3) & 1,
    )
    others = (
        0, (r - 1) * (row_bits & 1), (r - 1) * ((row_bits >> 1) & 1),
        (r - 1) * ((row_bits >> 2) & 1), 0, 1,
        (r - 1) * ((row_bits >> 3) & 1),
    )
    K, a, b, c, d, e = z3.Reals("K a b c d e")
    variables = (K, a, b, c, d, e)
    solver = z3.Solver()
    solver.add(K >= 1)
    if nonnegative:
        solver.add(*[variable >= 0 for variable in variables])
    loads = [
        K * N[i] - a * R3[i] - b * R4[i] - c * R7[i]
        - d * one[i] - e * others[i]
        for i in range(7)
    ]
    target = (K, 0, 0, 0, 0, 1, 0)
    solver.add(*[loads[i] == target[i] for i in range(7)])
    if solver.check() != z3.sat:
        return None
    model = solver.model()
    return tuple(text(model.eval(variable)) for variable in variables)


def scalar_check():
    cases = []
    for r in range(3, 13):
        for m in range(1, 13):
            # Retained cdg plus efficiency gives rq=m+B_x+r.  Comparison
            # of either new F row with B requires q>=B_x+1, equivalently
            # (r-1)B_x<=m.  The record pins the sharp boundary.
            bx_bound = F(m, r - 1)
            q_boundary = F(m + bx_bound + r, r)
            assert q_boundary == bx_bound + 1
            cx_bound = 2 * m + bx_bound + r
            cases.append({
                "m": m, "r": r,
                "sharp_upper_bound_Bx": str(bx_bound),
                "boundary_q": str(q_boundary),
                "resulting_upper_bound_Cx": str(cx_bound),
            })
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    by_r = {}
    for r in range(3, 13):
        survivors = {}
        for bits in range(1, 16):
            witness = solve(bits, r)
            if witness is not None:
                survivors[format(bits, "04b")] = {
                    "row": EXPECTED[bits][0] if bits in EXPECTED else "unexpected",
                    "coefficients_K_R3_R4_R7_Fi_sumFother": witness,
                }
        expected = {
            format(bits, "04b"): {
                "row": name,
                "coefficients_K_R3_R4_R7_Fi_sumFother": coefficients,
            }
            for bits, (name, coefficients) in EXPECTED.items()
        }
        assert survivors == expected, (r, survivors)
        by_r[str(r)] = survivors

    # Fail-open control: dropping coefficient nonnegativity admits additional
    # formal identities, so the cone signs are load-bearing.
    signed = [bits for bits in range(1, 16) if solve(bits, 4, nonnegative=False)]
    assert len(signed) > len(EXPECTED)

    payload = {
        "claim": "PXC148 one-row symmetric E-pinning escape no-go",
        "identity": "K*N-a*R3-b*R4-c*R7-d*F_i-e*sum_{j!=i}F_j = K*U + E_without_i",
        "nonnegative_survivors": by_r,
        "scalar_consequences": scalar_check(),
        "negative_control": {
            "drop_nonnegative_coefficients_survivor_count": len(signed),
            "strict_cone_survivor_count": len(EXPECTED),
        },
        "scope": (
            "all one-own-E symmetric row types F_i={e_i} union W with "
            "W subset {b,c,d,g}, under the displayed retained-row dual form; "
            "not all possible multi-row or split-block mechanisms"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
