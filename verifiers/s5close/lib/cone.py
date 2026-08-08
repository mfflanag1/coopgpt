"""Exact-cone description at n=5: the 280 permuted Studeny-Kratochvil facet
inequalities.  Verbatim reimplementation of verifiers/a3check/cone.py's
`inequalities`, with the dead scratchpad paths removed.

  v exact  <=>  v(empty)=0  and  sum_S c_S v(S) <= 0 for every returned c.
"""
from __future__ import annotations
import itertools
import catalogue


def inequalities(n):
    _, rows = catalogue.load(n)
    full = (1 << n) - 1
    out = set()
    for row in rows:
        for perm in itertools.permutations(range(n)):
            c = [0] * (1 << n)
            for S, lam in row["lam"].items():
                T = sum(1 << perm[i] for i in range(n) if S >> i & 1)
                c[T] += lam
            c[full] -= row["r"]
            out.add(tuple(c))
    return sorted(out)


def violations(n, v, ineqs):
    return [c for c in ineqs if sum(c[S] * v[S] for S in range(1, 1 << n)) > 0]


if __name__ == "__main__":
    for n in (4, 5):
        print(n, len(inequalities(n)))
