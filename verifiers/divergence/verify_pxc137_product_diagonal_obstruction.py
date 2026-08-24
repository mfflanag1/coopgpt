#!/usr/bin/env python3
"""Exact audit of the PXC137 product-flow/forced-diagonal theorem.

Dropping only ``F[r,r]=0`` from PXC136 makes the stationary bridge exact.
For two efficient core allocations x,z, the product occupation measure

    pi_r = (x_r+z_r)/(2T),
    F_ri = (x_r z_i+z_r x_i)/(2T^2)

has equal row/column marginals, satisfies every witness-core inequality,
and has bridge allocation (x+z)/2.  The latter lies in the coordinate box
between x and z, so the relaxed bridge equals overlap exactly.  Hence the
entire PXC136 loss is the price of deleting the diagonal.

This verifier checks the identities over the complete archived n=6 bank,
on the named mechanism controls, and against the matched sharp PXC136 dual.
It does not claim that the diagonal can always be repaired.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

from z3 import Q, Real, Solver, Sum, sat


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
DIV = HERE.parent
ARCHIVE = DIV / "search_archive"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(ARCHIVE)]

from audit_lmax_overcover import records  # noqa: E402
from unrestricted_pxc91c_exact_search import selector_pair  # noqa: E402
from verify_pxc136_stationary_witness_bridge import named_games  # noqa: E402


def zq(value: F):
    value = F(value)
    return Q(value.numerator, value.denominator)


def product_certificate(values, x, z):
    n = len(x)
    total = sum(x, F(0))
    full = (1 << n) - 1
    if total <= 0 or total != sum(z, F(0)):
        raise AssertionError("invalid efficient pair")
    for coalition in range(1, full):
        if sum((x[i] for i in range(n) if coalition >> i & 1), F(0)) < values[coalition]:
            raise AssertionError(("x outside core", coalition))
        if sum((z[i] for i in range(n) if coalition >> i & 1), F(0)) < values[coalition]:
            raise AssertionError(("z outside core", coalition))

    pi = tuple((x[i] + z[i]) / (2 * total) for i in range(n))
    flow = tuple(
        tuple((x[r] * z[i] + z[r] * x[i]) / (2 * total * total) for i in range(n))
        for r in range(n)
    )
    midpoint = tuple((x[i] + z[i]) / 2 for i in range(n))
    if sum(pi, F(0)) != 1:
        raise AssertionError("product mass")
    for r in range(n):
        if sum(flow[r], F(0)) != pi[r]:
            raise AssertionError(("product row", r))
        for coalition in range(1, full):
            load = sum((flow[r][i] for i in range(n) if coalition >> i & 1), F(0))
            rhs = pi[r] * values[coalition]
            if total * load < rhs:
                raise AssertionError(("product core row", r, coalition))
            # The exact slack identity is load-bearing for the tangent repair.
            xs = sum((x[i] for i in range(n) if coalition >> i & 1), F(0))
            zs = sum((z[i] for i in range(n) if coalition >> i & 1), F(0))
            expected = (
                x[r] * (zs - values[coalition])
                + z[r] * (xs - values[coalition])
            ) / (2 * total)
            if total * load - rhs != expected:
                raise AssertionError(("product slack identity", r, coalition))
    for i in range(n):
        if sum((flow[r][i] for r in range(n)), F(0)) != pi[i]:
            raise AssertionError(("product column", i))
        if not min(x[i], z[i]) <= midpoint[i] <= max(x[i], z[i]):
            raise AssertionError(("midpoint box", i))
        if flow[i][i] != x[i] * z[i] / (total * total):
            raise AssertionError(("product diagonal", i))
    overlap = sum((min(x[i], z[i]) for i in range(n)), F(0))
    bridge = sum(
        min(x[i], midpoint[i]) + min(z[i], midpoint[i]) - midpoint[i]
        for i in range(n)
    )
    if bridge != overlap:
        raise AssertionError(("relaxed bridge", bridge, overlap))
    return {
        "pi": list(map(str, pi)),
        "midpoint": list(map(str, midpoint)),
        "diagonal": [str(flow[i][i]) for i in range(n)],
        "diagonal_mass": str(sum((flow[i][i] for i in range(n)), F(0))),
        "overlap": str(overlap),
        "relaxed_bridge": str(bridge),
    }


def zero_diagonal_midpoint_status(values, x, z):
    """Exact status after retaining the midpoint and restoring F_rr=0."""
    n = len(x)
    total = sum(x, F(0))
    full = (1 << n) - 1
    pi = tuple((x[i] + z[i]) / (2 * total) for i in range(n))
    flow = [[Real(f"f_{r}_{i}") for i in range(n)] for r in range(n)]
    solver = Solver()
    for r in range(n):
        solver.add(Sum(flow[r]) == zq(pi[r]), flow[r][r] == 0)
        solver.add(*[flow[r][i] >= 0 for i in range(n)])
        for coalition in range(1, full):
            solver.add(
                zq(total) * Sum([flow[r][i] for i in range(n) if coalition >> i & 1])
                >= zq(pi[r] * values[coalition])
            )
    for i in range(n):
        solver.add(Sum([flow[r][i] for r in range(n)]) == zq(pi[i]))
    status = solver.check()
    if status == sat:
        return "sat"
    return str(status)


def named_controls():
    rows = []
    for label, constraints, n, total in named_games():
        values, x, z = selector_pair(constraints, n, total)
        certificate = product_certificate(values, x, z)
        certificate["label"] = label
        certificate["n"] = n
        certificate["midpoint_zero_diagonal_status"] = zero_diagonal_midpoint_status(values, x, z)
        rows.append(certificate)
    return rows


def archive_audit():
    unique = {}
    raw = 0
    for path in (ROOT / "verifiers/s6/harvest6_601.json", ROOT / "verifiers/s6/harvest6_602.json"):
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            if len(x) == 6 and sum(x, F(0)) == sum(z, F(0)) > 0:
                raw += 1
                unique[(values, x, z)] = (str(source), trail)
    for values, x, z in unique:
        product_certificate(values, x, z)
    return {
        "raw_records": raw,
        "distinct_exact_selector_triples": len(unique),
        "all_relaxed_bridges_equal_overlap": True,
    }


def sharp_dual_control():
    item = json.loads((ROOT / "verifiers/s6/harvest6_601.json").read_text())["records"][125]
    values = tuple(map(F, item["v"]))
    x = tuple(map(F, item["lmin"]))
    z = tuple(map(F, item["lmax"]))
    total = F(4)
    product = product_certificate(values, x, z)
    row_potential = tuple(F(q, 17) for q in (28, 50, 28, 28, 60, 50))
    column_potential = tuple(F(q, 17) for q in (40, -10, -28, -28, 0, -10))
    lambdas = {
        (0, 19): F(14, 17), (0, 35): F(4, 17), (0, 49): F(14, 17),
        (1, 14): F(22, 17), (1, 19): F(50, 17), (1, 35): F(40, 17),
        (2, 19): F(14, 17), (2, 35): F(4, 17), (2, 49): F(14, 17),
        (3, 19): F(14, 17), (3, 35): F(4, 17), (3, 49): F(14, 17),
        (4, 19): F(50, 17), (4, 20): F(32, 17), (4, 49): F(50, 17),
        (5, 35): F(40, 17), (5, 44): F(22, 17), (5, 49): F(50, 17),
    }
    diagonal = tuple(x[i] * z[i] / (total * total) for i in range(6))
    defects = []
    for r in range(6):
        root_load = sum(
            (weight for (root, coalition), weight in lambdas.items()
             if root == r and coalition >> r & 1),
            F(0),
        )
        defect = total * root_load - row_potential[r] - column_potential[r]
        defects.append(defect)
    weighted_positive_defect = sum(
        (diagonal[r] * max(F(0), defects[r]) for r in range(6)), F(0)
    )
    stationary = F(45, 17)
    overlap = F(product["overlap"])
    if not stationary >= overlap - weighted_positive_defect:
        raise AssertionError("diagonal-defect lower bound")
    return {
        "overlap": str(overlap),
        "stationary_optimum": str(stationary),
        "stationary_loss": str(overlap - stationary),
        "midpoint_zero_diagonal_status": zero_diagonal_midpoint_status(values, x, z),
        "dual_diagonal_defects": list(map(str, defects)),
        "product_diagonal_weights": list(map(str, diagonal)),
        "weighted_positive_defect": str(weighted_positive_defect),
        "proved_bound": str(overlap - weighted_positive_defect),
        "warning": "the displayed sharp dual makes PXC137d strict; it is a sign/load-bearing control, not an optimal diagonal-price certificate",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "PXC137 product midpoint and forced-diagonal obstruction",
        "theorem": {
            "product_flow": "pi=(x+z)/(2T), F_ri=(x_r z_i+z_r x_i)/(2T^2)",
            "relaxed_exactness": "dropping only F_rr=0 gives Psi_relaxed=O for every efficient core pair",
            "row_slack": "T F_r(S)-pi_r v(S)=[x_r(z(S)-v(S))+z_r(x(S)-v(S))]/(2T)",
            "missing_dual_rows": "A_r+B_r>=T sum_{S contains r} lambda_{rS}",
            "diagonal_defect_bound": "Psi>=O-sum_r (x_r z_r/T^2) [T L_r(r)-A_r-B_r]_+ for every optimal PXC136 dual",
        },
        "named_controls": named_controls(),
        "archive_audit": archive_audit(),
        "sharp_dual_control": sharp_dual_control(),
        "scope": (
            "dimension-free algebraic reduction: the stationary bridge loss is caused solely by the forced-zero diagonal constraint. "
            "It does not prove that diagonal repair is cheap enough to reach the hybrid target."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
