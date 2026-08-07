"""The exact-cone description at n=5, and its validation.

SOURCE (Studeny-Kratochvil 2022, "Facets of the cone of exact games", MMOR 95
pp. 35-80; catalogue front page, verbatim):

  * a min-semi-balanced system S is assigned the STANDARDIZED INEQUALITY
        sum_{S in S} lambda_S * m(S)  <=  r * m(N)
    for a set function m with m(empty) = 0, where sum_S lambda_S chi_S is the
    semi-conic combination yielding the constant vector with component r;
  * "the minimal set of linear inequalities defining the cone of exact games
    over N consists of those that are assigned to indecomposable
    min-semi-balanced set systems on N."

So, for |N| = 5,

  v is exact  <=>  v(empty) = 0  and  sum_S lambda_S v(S) <= r v(N)
                   for each of the 16 catalogued types under every permutation.

NOTE the direction of the theorem being used: this is a COMPLETE description of
the cone, so no separate balancedness (Bondareva-Shapley) condition has to be
imposed -- the balanced inequalities must be implied.  That implication is
checked below rather than assumed.

VALIDATION performed here:
  (V-a) every inequality is satisfied by every random EXACT game;
  (V-b) some inequality is violated by random NON-exact games;
  (V-c) every minimal balanced inequality (Bondareva-Shapley) is implied by the
        16-type system, i.e. the description entails a nonempty core.
"""
from __future__ import annotations

import itertools
import json
import random
import sys
from fractions import Fraction as F

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
import audit
import catalogue
import pack


def inequalities(n):
    """All distinct exact-cone inequalities: lists c with sum_S c_S v(S) <= 0,
    indexed by S = 0..2^n-1 (c_N carries the -r)."""
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


def main():
    n = 5
    ineqs = inequalities(n)
    print(f"n={n}: {len(ineqs)} distinct exact-cone inequalities "
          f"(16 types under S_{n})")

    rng = random.Random(20260806)
    full = (1 << n) - 1
    stats = {"exact_games": 0, "exact_with_violation": 0,
             "nonexact_games": 0, "nonexact_certified": 0}

    # (V-a) lower envelopes of common-total nonnegative rows are exact
    # (Lemma "lower-envelope realization"), so no exactness test is needed.
    for _ in range(2000):
        tot = rng.choice([6, 8, 12, 16])
        gens = audit.rand_gens(n, rng, rng.randint(2, 6), tot, tot)
        v = audit.envelope(n, gens)
        w, _ = audit.normalize(n, v)
        if w[full] == 0:
            continue
        stats["exact_games"] += 1
        if violations(n, w, ineqs):
            stats["exact_with_violation"] += 1
            print("  FAIL (V-a):", [str(q) for q in w])

    # (V-b) non-exact games must be certified by some inequality.
    # Exactness is decided by 2^n-2 exact LPs (z3), far cheaper than vertex
    # enumeration.
    import z3

    def is_exact_lp(w):
        x = [z3.Real(f"x{i}") for i in range(n)]
        base = [z3.Sum(x) == to_z3(w[full])] + [
            z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= to_z3(w[S])
            for S in range(1, full)]
        for S in range(1, full):
            o = z3.Optimize()
            o.add(base)
            hh = o.minimize(z3.Sum([x[i] for i in range(n) if S >> i & 1]))
            if o.check() != z3.sat:
                return False            # empty core: not exact
            if audit.rat(o.lower(hh)) != w[S]:
                return False
        return True

    def to_z3(q):
        q = F(q)
        return z3.RealVal(f"{q.numerator}/{q.denominator}")

    tries = 0
    while stats["nonexact_games"] < 150 and tries < 4000:
        tries += 1
        w = [F(0)] * (1 << n)
        w[full] = F(rng.randint(1, 8))
        for S in range(1, full):
            if bin(S).count("1") == 1:
                continue
            w[S] = F(rng.randint(0, int(w[full])))
        if is_exact_lp(w):
            continue
        stats["nonexact_games"] += 1
        if violations(n, w, ineqs):
            stats["nonexact_certified"] += 1

    # (V-c) the description entails a nonempty core: every minimal balanced
    # inequality must be implied.  Test: maximise the balanced functional over
    # the cone; implied iff no cone point violates it.
    import z3
    bad = []
    import os
    mbfile = f"{SCR}/sel/a3check/minbal5.json"
    if os.path.exists(mbfile):
        mb = [(tuple(c), {int(k): F(x) for k, x in b.items()})
              for c, b in json.load(open(mbfile))]
    else:
        mb = pack.min_balanced(list(range(n)))
        json.dump([[list(c), {str(k): str(x) for k, x in b.items()}]
                   for c, b in mb], open(mbfile, "w"))
    for coll, beta in mb:
        c = [F(0)] * (1 << n)
        for S in coll:
            c[S] += beta[S]
        c[full] -= 1
        x = [z3.Real(f"v{S}") for S in range(1 << n)]
        s = z3.Solver()
        s.add(x[0] == 0)
        for ineq in ineqs:
            s.add(z3.Sum([z3.RealVal(ineq[S]) * x[S]
                          for S in range(1, 1 << n) if ineq[S]]) <= 0)
        s.add(z3.Sum([z3.RealVal(f"{c[S].numerator}/{c[S].denominator}") * x[S]
                      for S in range(1, 1 << n) if c[S]]) >= 1)
        if s.check() == z3.sat:
            bad.append([catalogue.pretty(n, {S: 1 for S in coll})])
    print(f"  (V-a) {stats['exact_games']} exact games, "
          f"{stats['exact_with_violation']} violating an inequality "
          f"(must be 0)")
    print(f"  (V-b) {stats['nonexact_games']} non-exact games, "
          f"{stats['nonexact_certified']} certified by some inequality "
          f"(must equal the previous number)")
    print(f"  (V-c) {len(mb)} minimal balanced collections, "
          f"{len(bad)} NOT implied by the 16-type system (must be 0)")
    ok = (stats["exact_with_violation"] == 0
          and stats["nonexact_certified"] == stats["nonexact_games"]
          and not bad)
    print("EXACT-CONE DESCRIPTION VALIDATED" if ok else "VALIDATION FAILED")
    json.dump({"n": n, "n_inequalities": len(ineqs), "stats": stats,
               "balanced_not_implied": bad, "validated": ok},
              open(f"{SCR}/sel/a3check/cone.json", "w"), indent=1)


if __name__ == "__main__":
    main()
