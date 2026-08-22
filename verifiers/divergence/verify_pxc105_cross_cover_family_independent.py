#!/usr/bin/env python3
"""Independent solver-free rational audit of the PXC105 family.

This imports only the active-set kernel of the independent PXC98 verifier;
it imports no project game, selector, cover, PXC104, or PXC105 code.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

import verify_unrestricted_pxc91c_pxc98_independent as independent

N = 6
LO, HI = F(4), F(11, 2)
ANCHORS = (F(17, 4), F(9, 2), F(5), F(21, 4), F(27, 5))
CX = (7, 11)
COVERS = ((3,), (11, 19, 39), (11, 23, 35))


def family(A):
    total = 18 + A
    defining = {
        7: F(16), 11: F(16), 19: F(13),
        23: 13 + A, 35: F(13), 39: 13 + A,
    }
    low = (A + 2) / 3
    high = (46 - A) / 6
    x = (high, high, low, low, low, low)
    z = (F(6), F(6), A, F(4), F(1), F(1))
    reduced = (
        (F(6), F(6), F(4), F(4), (A - 2) / 2, (A - 2) / 2),
        (F(6), F(6), F(4), F(4), F(1), A - 3),
        (F(6), F(6), F(4), F(4), A - 3, F(1)),
    )
    return F(total), defining, x, z, reduced


def configure(A):
    total, defining, x, z, _reduced = family(A)
    independent.TOTAL = total
    independent.DEFINING = defining
    independent.X = x
    independent.Z = z
    independent.CX = CX
    return total, defining, x, z


def csum(point, coalition):
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def expected_value(A, coalition):
    if coalition == 63:
        return 18 + A
    if coalition & 3 != 3:
        return F(0)
    trace = coalition >> 2
    answer = F(12)
    if trace & 3:
        answer = max(answer, F(16))
    if trace & 12:
        answer = max(answer, F(13))
    if trace & 1 and trace & 12:
        answer = max(answer, 13 + A)
    return answer


def lower_envelope_with_points(defining):
    inequalities = independent.base_inequalities(defining)
    equalities = [([F(1)] * N, independent.TOTAL)]
    values, points = [], []
    for coalition in range(1 << N):
        objective = [F((coalition >> i) & 1) for i in range(N)]
        optimum, point = independent.lp_active(
            objective, inequalities, equalities, False
        )
        values.append(optimum)
        points.append(tuple(point))
    return tuple(values), tuple(points)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    endpoint_checks = []
    for A in (LO, HI):
        _total, defining, _x, _z = configure(A)
        values, points = lower_envelope_with_points(defining)
        if any(values[s] != expected_value(A, s) for s in range(64)):
            raise AssertionError(("endpoint formula", A))
        trace_minimizers = []
        for trace in range(16):
            coalition = 3 | (trace << 2)
            if csum(points[coalition], coalition) != values[coalition]:
                raise AssertionError(("endpoint minimizer", A, coalition))
            trace_minimizers.append({
                "trace_abjk": format(trace, "04b")[::-1],
                "coalition": coalition,
                "value": str(values[coalition]),
                "point": list(map(str, points[coalition])),
            })
        endpoint_checks.append({
            "A": str(A), "values": list(map(str, values)),
            "explicit_rh_trace_minimizers": trace_minimizers,
        })

    anchor_checks = []
    for A in ANCHORS:
        total, defining, x, z = configure(A)
        _t, _d, _x, _z, reduced = family(A)
        values = independent.lower_envelope(defining)
        if any(values[s] != expected_value(A, s) for s in range(64)):
            raise AssertionError(("value formula", A))
        if independent.sparse_selector(defining, "min") != x:
            raise AssertionError(("Lmin", A))
        if independent.sparse_selector(defining, "max") != z:
            raise AssertionError(("Lmax", A))
        xtight = tuple(s for s in range(1, 63) if csum(x, s) == values[s])
        ztight = tuple(s for s in range(1, 63) if csum(z, s) == values[s])
        if xtight != CX or ztight != (3, 11, 19, 23, 35, 39):
            raise AssertionError(("tight menu", A, xtight, ztight))

        complete = []
        for size in range(3):
            for rows in itertools.combinations(CX, size):
                constraints = {s: csum(x, s) for s in rows}
                if independent.sparse_selector(constraints, "min") == x:
                    complete.append(rows)
        if complete != [CX]:
            raise AssertionError(("complete Cx", A, complete))

        covers = independent.normalized_covers(values)
        if tuple(q[0] for q in covers) != COVERS:
            raise AssertionError(("covers", A, covers))
        lift_rows = []
        for index, (rows, weights, eta, alpha) in enumerate(covers):
            constraints = {s: csum(x, s) for s in CX}
            constraints.update({s: csum(z, s) for s in rows})
            lx = independent.sparse_selector(constraints, "min")
            lz = independent.sparse_selector(constraints, "max")
            if lx != x or lz != reduced[index] or lz == z:
                raise AssertionError(("lift", A, rows, lx, lz))
            lift_rows.append({
                "rows": list(rows), "weights": list(map(str, weights)),
                "eta": str(eta), "alpha": list(map(str, alpha)),
                "lmax": list(map(str, lz)),
            })

        inequalities = independent.base_inequalities(defining)
        equalities = [([F(1)] * N, total)]
        for player in range(N):
            objective = [F(0)] * N
            objective[player] = F(1)
            optimum, _point = independent.lp_active(
                objective, inequalities, equalities, False
            )
            if optimum != 0:
                raise AssertionError(("singleton normalization", A, player))

        equations = []
        for player in (0, 1):
            vector = [F(0)] * N
            vector[player] = F(1)
            equations.append(vector)
        for coalition in sorted({s for cover in COVERS for s in cover}):
            equations.append([F((coalition >> i) & 1) for i in range(N)])
        kernel = independent.rref_unique(equations, [F(0)] * len(equations), N)
        if kernel != (F(0),) * N:
            raise AssertionError(("common kernel", A, kernel))

        anchor_checks.append({
            "A": str(A), "lmin": list(map(str, x)),
            "lmax": list(map(str, z)), "tight_x": list(xtight),
            "tight_z": list(ztight), "covers_and_lifts": lift_rows,
            "common_kernel": list(map(str, kernel)),
        })

    payload = {
        "claim": "independent exact audit of the PXC105 rational family",
        "parameter_domain": "rational 4 < A < 11/2",
        "endpoint_lower_envelopes": endpoint_checks,
        "interior_anchors": anchor_checks,
        "continuum_logic": (
            "the 64 endpoint minimizers interpolate affinely while the "
            "displayed row/cover inequalities give the matching affine lower "
            "bounds throughout the closed interval"
        ),
        "independence": (
            "solver-free rational active-set engine; no project game, selector, "
            "cover, PXC104, PXC105, or discovery implementation"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
