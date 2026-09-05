#!/usr/bin/env python3
"""Exact finite corroboration of manuscript.tex; no repository dependencies.

Run from the package root: python verification/run_checks.py
All proof gates are explicit checks, including under Python -O and -OO.
The all-parameter proof is in the manuscript, not inferred from this suite.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

import z3


CASES = ((2, 3), (2, 4), (3, 4), (3, 5), (4, 5))
TIMEOUT_MS = 120_000


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def q(value):
    require(not isinstance(value, float), "floating-point input is forbidden")
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def fraction(value):
    value = z3.simplify(value)
    require(z3.is_rational_value(value), f"non-rational solver value: {value}")
    return F(value.numerator_as_long(), value.denominator_as_long())


def fibonacci(index):
    require(isinstance(index, int) and index >= 0, "invalid Fibonacci index")
    a, b = 0, 1
    for _ in range(index):
        a, b = b, a + b
    return a


def generators(m, r, perturb=False):
    require(m >= 2 and r >= m + 1, "outside the construction's domain")
    denominator = fibonacci(m + 1)
    a = [F(fibonacci(m - i), denominator) for i in range(m)]
    if perturb:
        a[0] -= F(1, 10)
    b = [1 - value for value in a]
    u = [F(r - m)] + a + b + [F(0)] * r
    v = [F(0)] * (2 * m + 1) + [F(1)] * r
    require(sum(u) == sum(v) == r, "generators have different totals")
    require(min(u + v) >= 0, "negative generator coordinate")
    require(all(min(ui, vi) == 0 for ui, vi in zip(u, v)),
            "singleton normalization failed")
    return u, v


def subset_sums(point):
    sums = [F(0)] * (1 << len(point))
    for mask in range(1, len(sums)):
        bit = mask & -mask
        sums[mask] = sums[mask ^ bit] + point[bit.bit_length() - 1]
    return sums


def raw_core(u, v, variables):
    """Generate every coalition from the two raw additive allocations."""
    n = len(u)
    su, sv = subset_sums(u), subset_sums(v)
    worth = [min(a, b) for a, b in zip(su, sv)]
    symbolic = [z3.RealVal(0)] * (1 << n)
    constraints = [yi >= 0 for yi in variables]
    constraints.append(z3.Sum(variables) == q(sum(u)))
    for mask in range(1, (1 << n) - 1):
        bit = mask & -mask
        symbolic[mask] = symbolic[mask ^ bit] + variables[bit.bit_length() - 1]
        constraints.append(symbolic[mask] >= q(worth[mask]))
    return constraints, worth


def check_member(point, worth):
    sums = subset_sums(point)
    require(sums[-1] == worth[-1], "candidate is not efficient")
    require(all(got >= needed for got, needed in zip(sums, worth)),
            "candidate violates a raw coalition constraint")


def solver_verdict(constraints):
    solver = z3.Solver()
    solver.set(timeout=TIMEOUT_MS)
    solver.add(*constraints)
    result = solver.check()
    require(result != z3.unknown, f"solver UNKNOWN: {solver.reason_unknown()}")
    return result, solver


def optimum(constraints, objective, maximize):
    solver = z3.Optimize()
    solver.set(timeout=TIMEOUT_MS)
    solver.add(*constraints)
    handle = solver.maximize(objective) if maximize else solver.minimize(objective)
    result = solver.check()
    require(result == z3.sat, f"optimization did not return SAT: {result}")
    return fraction(handle.value())


def check_case(m, r):
    u, v = generators(m, r)
    n = len(u)
    y = z3.Reals(" ".join(f"y_{m}_{r}_{i}" for i in range(n)))
    constraints, worth = raw_core(u, v, y)
    check_member(u, worth)
    check_member(v, worth)

    # A receiver reconstructs the only possible segment parameter.
    t = 1 - y[-1]
    equations = [y[i] == q(v[i]) + t * q(u[i] - v[i]) for i in range(n)]
    result, _ = solver_verdict(constraints + [z3.Not(z3.And(*equations))])
    require(result == z3.unsat, f"off-segment core point for {(m, r)}")

    denominator = fibonacci(m + 1)
    tmin, tmax = F(denominator, denominator + 1), F(1, r - m + 1)
    require(0 <= tmax <= tmin <= 1, "invalid selector parameters")
    x = [tmin * ui + (1 - tmin) * vi for ui, vi in zip(u, v)]
    z = [tmax * ui + (1 - tmax) * vi for ui, vi in zip(u, v)]
    check_member(x, worth)
    check_member(z, worth)
    floor, ceiling = z3.Reals(f"floor_{m}_{r} ceiling_{m}_{r}")
    lower = optimum(constraints + [yi >= floor for yi in y], floor, True)
    upper = optimum(constraints + [yi <= ceiling for yi in y], ceiling, False)
    require(lower == min(x), "wrong maximin value")
    require(upper == max(z), "wrong minimax value")
    for point, level, is_floor in ((x, lower, True), (z, upper, False)):
        face = [yi >= q(level) if is_floor else yi <= q(level) for yi in y]
        other = z3.Or(*[yi != q(pi) for yi, pi in zip(y, point)])
        result, _ = solver_verdict(constraints + face + [other])
        require(result == z3.unsat, "optimal first-stage face is not the claimed singleton")

    overlap = sum(min(xi, zi) for xi, zi in zip(x, z))
    distance = sum(abs(xi - zi) for xi, zi in zip(x, z)) / r
    deficit = 2 * F(1, denominator + 1) + 2 * F(1, r - m + 1)
    require(2 - distance == 2 * overlap / r == deficit, "distance identity failed")
    require(overlap >= F(r, n - 1), "generic overlap bound failed")
    return {
        "m": m, "r": r, "n": n, "total": r,
        "proper_nonempty_coalitions": (1 << n) - 2,
        "generators": [[str(a) for a in row] for row in (u, v)],
        "leximin": [str(a) for a in x], "leximax_min": [str(a) for a in z],
        "first_stage_values": {"floor": str(lower), "ceiling": str(upper)},
        "whole_core_segment": True, "both_first_stage_faces_unique": True,
        "rho": str(distance), "deficit": str(deficit), "status": "PASS",
    }


def negative_control():
    u, v = generators(2, 3, perturb=True)
    y = z3.Reals(" ".join(f"perturbed_y_{i}" for i in range(len(u))))
    constraints, worth = raw_core(u, v, y)
    t = 1 - y[-1]
    equations = [y[i] == q(v[i]) + t * q(u[i] - v[i]) for i in range(len(u))]
    result, solver = solver_verdict(constraints + [z3.Not(z3.And(*equations))])
    require(result == z3.sat, "negative control failed to enlarge the segment")
    point = [fraction(solver.model().eval(yi, model_completion=True)) for yi in y]
    check_member(point, worth)
    tp = 1 - point[-1]
    require(any(pi != vi + tp * (ui - vi) for pi, ui, vi in zip(point, u, v)),
            "negative-control witness is on the segment")
    return {"m": 2, "r": 3, "status": "PASS",
            "kind": "perturbed unit-sum condition gives off-segment core point",
            "point": [str(a) for a in point]}


def arithmetic_checks():
    rows = []
    for m in range(2, 65):
        denominator = fibonacci(m + 1)
        a = [F(fibonacci(m - i), denominator) for i in range(m)]
        b = [1 - value for value in a]
        require(min(a + b) == F(1, denominator) and sum(a + b) == m,
                "Fibonacci positivity, minimum, or total failed")
        require(all(a[i + 1] + a[i + 2] + b[i] == 1 for i in range(m - 2)),
                "recurrence coalition is not unit-sum")
        require(a[-2] + b[-1] == 1 and a[0] + a[1] == 1,
                "boundary coalition is not unit-sum")
        rows.append({"m": m, "F": denominator})
    sequence = []
    for n in (128, 129, 255, 256, 257, 512, 1024, 4096, 65536):
        ell = (n - 1).bit_length()
        m, r = 4 * ell, n - 8 * ell - 1
        require(r >= m + 1 and fibonacci(m + 1) >= n * n,
                "all-n parameter choice failed")
        deficit = 2 * F(1, fibonacci(m + 1) + 1) + 2 * F(1, n - 12 * ell)
        require(F(2, n - 1) <= deficit <= F(2, n - 12 * ell) + F(2, n * n + 1),
                "finite squeeze failed")
        sequence.append({"n": n, "m": m, "r": r,
                         "deficit": str(deficit), "n_times_deficit": str(n * deficit)})
    return {"fibonacci_rows": rows, "all_n_examples": sequence}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parent / "results" / "verification.json")
    args = parser.parse_args()
    payload = {
        "status": "RUNNING",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_scope": "Finite rational corroboration; all-parameter proof is in manuscript.tex",
        "runtime": {"python": sys.version, "optimization": sys.flags.optimize,
                    "z3": z3.get_version_string()},
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Replace any old success before starting scientific work. Failed or
    # interrupted checks must not leave a previous PASS as this run's result.
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    try:
        records = []
        for m, r in CASES:
            records.append(check_case(m, r))
            print(f"PASS raw entire core and full selectors: m={m}, r={r}", flush=True)
        require(len(records) == 5 and [(a["m"], a["r"]) for a in records] == list(CASES),
                "verification case coverage changed")
        payload["negative_control"] = negative_control()
        payload["arithmetic"] = arithmetic_checks()
        payload["cases"] = records
        payload["status"] = "PASS"
    except BaseException as error:
        payload["status"] = "FAIL"
        payload["error"] = {"type": type(error).__name__, "message": str(error)}
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        raise
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS all 5 cases, closure negative control, and arithmetic checks; {args.output}")


if __name__ == "__main__":
    main()
