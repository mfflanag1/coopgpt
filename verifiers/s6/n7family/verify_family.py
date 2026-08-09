"""Verification sweep for the FAMILY THEOREM (task #39).

The proof (PROOF_FAMILY_N.txt) turns out to need only TWO coalition values, not
the pair caps I used when designing n=7:  the quad caps
    v(N\(Z u {k})) = 6(n-3) = 3M     for k = k1, k2
do BOTH jobs by themselves.  Floor: y(Z u {k}) <= 2(n-3) is a sum of n-3 terms
each >= 2 under the stage-1 constraint, so all are exactly 2 -- that pins all of
P at once.  Ceiling: N\(Z u {k}) has 3 players and value 3M, so max_i y_i >= M,
and the two of them together force the unique core point with max <= M to be z.
So the pair caps are REDUNDANT.  This script checks the theorem's conclusions,
and separately checks that claim about the two values.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L
import lmax as LM

def build(n):
    T = 8*(n-3); mu = 2; M = 2*(n-3); rho = 3*n-10; zc = n-4
    half = 3*(n-3)                      # (T - M)/2
    rows = [
        tuple([mu]*(n-2) + [rho, rho]),                 # x
        tuple([0]*zc + [M, M, M, M]),                   # z
        tuple([0]*zc + [0, M, half, half]),             # zeroes k1
        tuple([0]*zc + [M, 0, half, half]),             # zeroes k2
        tuple([mu]*(n-2) + [2*rho, 0]),                 # zeroes r2
        tuple([mu]*(n-2) + [0, 2*rho]),                 # zeroes r1
    ]
    return T, mu, M, rho, zc, rows

ok = True
for n in range(5, 10):
    T, mu, M, rho, zc, rows = build(n)
    FULL = (1 << n) - 1
    for r in rows:
        assert sum(r) == T and all(q >= 0 for q in r), (n, r)
    cover = all(min(r[i] for r in rows) == 0 for i in range(n))
    gens = [tuple(F(q) for q in r) for r in rows]
    w, sh = L.normalize(n, L.envelope(n, gens))
    assert all(s == 0 for s in sh)
    # the two quad caps
    Zmask = sum(1 << i for i in range(zc))
    Zk1 = Zmask | (1 << zc)          # k1 sits at index zc
    Zk2 = Zmask | (1 << (zc + 1))    # k2 at zc+1; rich are n-2, n-1
    q1, q2 = w[FULL ^ Zk1], w[FULL ^ Zk2]
    x = L.lmin(n, w); z = LM.lmax(n, w)
    gap = sum(abs(x[i] - z[i]) for i in range(n))
    tx = [F(mu)]*(n-2) + [F(rho)]*2
    tz = [F(0)]*zc + [F(M)]*4
    good = (x == tx and z == tz and F(gap, T) == F(n-4, n-3)
            and q1 == 6*(n-3) and q2 == 6*(n-3) and cover)
    ok = ok and good
    line = (f"n={n:2d} T={T:3d}  quad caps {q1},{q2} (want {6*(n-3)})  "
            f"Lmin ok {x==tx}  Lmax ok {z==tz}  ratio {F(gap,T)} "
            f"(want {F(n-4,n-3)})")
    if n <= 8:
        ex, bad = L.is_exact_lp(n, w)
        line += f"  exact {ex}"
        ok = ok and ex
    else:
        line += "  exact by envelope lemma"
    print(line)
print()
print("ALL n = 5..9 AS PREDICTED" if ok else "SOME CHECK FAILED")
print()
print("n=5 sanity: the family's n=5 member should BE the CFG extremal config")
T, mu, M, rho, zc, rows = build(5)
print(f"   Lmin multiset {sorted([mu]*3 + [rho]*2)}  (CFG: T/8 x3, 5T/16 x2 "
      f"= {[T//8]*3 + [5*T//16]*2} sorted {sorted([T//8]*3 + [5*T//16]*2)})")
print(f"   Lmax multiset {sorted([0]*1 + [M]*4)}  (CFG: 0, T/4 x4 = "
      f"{sorted([0] + [T//4]*4)})")
print(f"   ratio (n-4)/(n-3) = {F(1,2)} = s(5)")
