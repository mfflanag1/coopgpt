"""Exact quantifier-elimination check of core largeness for the four
monotonicity-example games of paper4 Section 7 (both bases and both bumps).

Largeness (Sharkey): every acceptable vector y (y(S) >= v(S) for all nonempty
S) dominates a core point x <= y.  The check asserts the negation --- some
acceptable y admits no dominated core point --- as a quantified LRA sentence
and reports UNSAT, which proves largeness.  No enumeration is involved.

Run from this directory:  python3 large_core_qe.py
Requires z3; imports the shared toolkit from ./lib.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
from fractions import Fraction as F
import z3
import audit

if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


def large_core(n, v, timeout_ms=300000):
    full = (1 << n) - 1
    y = [z3.Real(f"y{i}") for i in range(n)]
    x = [z3.Real(f"x{i}") for i in range(n)]
    s = z3.Solver()
    s.set("timeout", timeout_ms)
    for S in range(1, full + 1):
        s.add(z3.Sum([y[i] for i in range(n) if S >> i & 1])
              >= audit.to_z3(v[S]))
    core = [z3.Sum(x) == audit.to_z3(v[full])]
    core += [z3.Sum([x[i] for i in range(n) if S >> i & 1])
             >= audit.to_z3(v[S]) for S in range(1, full)]
    s.add(z3.Not(z3.Exists(x, z3.And(*core, *[x[i] <= y[i]
                                              for i in range(n)]))))
    r = str(s.check())
    return {"unsat": "LARGE (proved)", "sat": "NOT large",
            "unknown": "unknown"}[r]


GAMES = {
    "example-41 base": ([(0, 11, 0, 7, 0, 0), (0, 10, 0, 4, 3, 1),
                         (2, 0, 1, 0, 15, 0)], None),
    "example-41 bump": ([(0, 11, 0, 7, 0, 0), (0, 10, 0, 4, 3, 1),
                         (2, 0, 1, 0, 15, 0)], (31, F(9, 16))),
    "example-42 base": ([(0, 15, 0, 14, 0, 0), (0, 9, 0, 9, 6, 5),
                         (4, 0, 4, 0, 21, 0)], None),
    "example-42 bump": ([(0, 15, 0, 14, 0, 0), (0, 9, 0, 9, 6, 5),
                         (4, 0, 4, 0, 21, 0)], (31, F(23, 8))),
}

if __name__ == "__main__":
    for name, (gens, bump) in GAMES.items():
        v = audit.envelope(6, [tuple(map(F, g)) for g in gens])
        if bump is not None:
            S, d = bump
            v = list(v)
            v[S] = v[S] + d
        print(f"{name:18s} -> {large_core(6, v)}")
