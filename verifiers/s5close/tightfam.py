"""Task #27, increment 2: the TIGHT-FAMILY closure lemmas, verified.

The protectors L11/L12 only assert that SOME tight coalition exists for each
ordered pair.  They say nothing about how tight coalitions interact.  Exact
games are monotone and superadditive (both immediate from v(S) = min over the
core of w(S), with w >= 0), and that gives closure properties which turn a
collection of protector-supplied tight sets into arithmetic on the levels.

Throughout, phi in {x, z} is a core point and "phi-tight" means phi(A) = v(A).

 L14 (DISJOINT UNION).  A, B disjoint and both phi-tight => A u B is phi-tight.
     PROOF.  phi(A u B) = phi(A) + phi(B) = v(A) + v(B) <= v(A u B) by
     superadditivity, and v(A u B) <= phi(A u B) because phi is a core point.
     So both inequalities are equalities.                                    []

 L15 (MONOTONE CROSS).  A x-tight, B z-tight, A subset B  =>  x(A) <= z(B).
     Symmetrically A z-tight, B x-tight, A subset B => z(A) <= x(B).
     PROOF.  x(A) = v(A) <= v(B) = z(B), the middle step by monotonicity.    []

 L16 (SUPERADDITIVE CROSS).  A x-tight, B z-tight, A and B disjoint =>
     x(A) + z(B) <= min( x(A u B), z(A u B) ).
     PROOF.  v(A) + v(B) <= v(A u B) by superadditivity, and v(A u B) is at
     most x(A u B) and at most z(A u B) since both are core points.          []

 L17 (DOUBLE TIGHT).  A both x-tight and z-tight  =>  x(A) = z(A) ( = v(A) ).

NOT TRUE, AND CHECKED SO I DO NOT USE IT: the tight family is NOT closed under
complementation.  A x-tight gives only v(N \\ A) <= 1 - v(A) = x(N \\ A), which
is core membership again, not tightness.  The script records how often the
complement of a tight set fails to be tight, to keep that honest.
"""
from __future__ import annotations
import json
import sys
from fractions import Fraction as F

HERE = sys.path[0]
N, FULL = 5, 31


def main():
    st = {"games": 0, "L14_cases": 0, "L14_fail": 0,
          "L15_cases": 0, "L15_fail": 0, "L16_cases": 0, "L16_fail": 0,
          "L17_cases": 0, "L17_fail": 0,
          "complement_cases": 0, "complement_NOT_tight": 0,
          "monotone_fail": 0, "superadd_fail": 0}
    for src in ("harvest_seed22.json", "harvest_seed777.json"):
        for r in json.load(open(f"{HERE}/{src}"))["records"]:
            T = F(r["T"])
            v = [F(t) / T for t in r["v"]]
            x = [F(t) / T for t in r["lmin"]]
            z = [F(t) / T for t in r["lmax"]]
            st["games"] += 1
            S = lambda p, A: sum(p[k] for k in range(N) if A >> k & 1)
            tx = {A for A in range(1, FULL) if S(x, A) == v[A]}
            tz = {A for A in range(1, FULL) if S(z, A) == v[A]}
            # the two background facts the lemmas rest on
            for A in range(1, FULL + 1):
                for B in range(1, FULL + 1):
                    if A & B == A and v[A] > v[B]:
                        st["monotone_fail"] += 1
                    if A & B == 0 and A and B and v[A] + v[B] > v[A | B]:
                        st["superadd_fail"] += 1
            for A in tx:
                st["complement_cases"] += 1
                if (FULL ^ A) not in tx:
                    st["complement_NOT_tight"] += 1
            for A in range(1, FULL):
                for B in range(1, FULL):
                    if A & B == 0 and (A | B) != FULL:
                        if A in tx and B in tx:
                            st["L14_cases"] += 1
                            if (A | B) not in tx:
                                st["L14_fail"] += 1
                        if A in tx and B in tz:
                            st["L16_cases"] += 1
                            if S(x, A) + S(z, B) > min(S(x, A | B),
                                                       S(z, A | B)):
                                st["L16_fail"] += 1
                    if A & B == A and A != B:
                        if A in tx and B in tz:
                            st["L15_cases"] += 1
                            if S(x, A) > S(z, B):
                                st["L15_fail"] += 1
                        if A in tz and B in tx:
                            st["L15_cases"] += 1
                            if S(z, A) > S(x, B):
                                st["L15_fail"] += 1
                if A in tx and A in tz:
                    st["L17_cases"] += 1
                    if S(x, A) != S(z, A):
                        st["L17_fail"] += 1
    print(json.dumps(st, indent=1))
    ok = all(st[k] == 0 for k in st if k.endswith("_fail"))
    print("TIGHT-FAMILY LEMMAS VERIFIED" if ok else "A LEMMA FAILED")
    print(f"(complement of a tight set was NOT tight in "
          f"{st['complement_NOT_tight']} of {st['complement_cases']} cases -- "
          f"confirming that closure is unavailable)")
    json.dump(st, open(f"{HERE}/tightfam.json", "w"), indent=1)


if __name__ == "__main__":
    main()
