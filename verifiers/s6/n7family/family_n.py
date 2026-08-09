"""The CFG family, general n: one constructor, verified at n = 6, 7, 8.

Scale T = 8(n-3), so mu = 2, M = T/4 = 2(n-3), rho = 3n-10, and the Lmax
zero-set Z has |Z| = n-4.  Players: Z = 1..n-4 (Lmax zeros, Lmin poor),
then two more poor players k1,k2, then two rich r1,r2.
    Lmin x = (2, ..., 2, rho, rho)          (n-2 twos)
    Lmax z = (0, ..., 0, M, M, M, M)        (n-4 zeros)
    predicted ratio (n-4)/(n-3)

PINS (the design):  v(N\{i,j}) = T - 2mu for {i,j} in Z            [pairs]
                    v(N\(Z u {k})) = T - (|Z|+1)mu for k in {k1,k2} [quads]
The quad value equals M * (n - |Z| - 1) automatically -- T - (n-3)*2 = 3T/4 and
M*3 = 3T/4 -- so ONE pair of coalitions serves as both the floor pins and the
nu-anchors that fix the ceiling level.  That coincidence is why the family
exists at every n, and it is what the two-generator attempt could not see.

ROW CONSTRAINTS: g_i+g_j <= 2mu on Z; g(Z u {k}) <= (|Z|+1)mu for k1,k2;
total T; nonnegative; and the rows must zero every coordinate.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L
import lmax as LM

def build(n):
    T = 8 * (n - 3); mu = 2; M = T // 4; rho = 3 * n - 10; zc = n - 4
    Z = [0] * zc
    rows = []
    rows.append(tuple([mu]*(n-2) + [rho, rho]))            # x
    rows.append(tuple(Z + [M, M, M, M]))                   # z ; zeroes Z
    rows.append(tuple(Z + [0, M] + [(T - M)//2]*2))        # zeroes k1
    rows.append(tuple(Z + [M, 0] + [(T - M)//2]*2))        # zeroes k2
    rows.append(tuple([mu]*zc + [mu, mu, 6*n-20, 0]))      # zeroes r2
    rows.append(tuple([mu]*zc + [mu, mu, 0, 6*n-20]))      # zeroes r1
    return T, rows

for n in (6, 7, 8):
    T, rows = build(n)
    print("=" * 68)
    print(f"n = {n},  T = {T}")
    for r in rows:
        assert sum(r) == T, (r, sum(r))
        assert all(q >= 0 for q in r), r
    print("  rows:", rows)
    print("  zero cover:", all(min(r[i] for r in rows) == 0 for i in range(n)))
    gens = [tuple(F(q) for q in r) for r in rows]
    w, sh = L.normalize(n, L.envelope(n, gens))
    assert all(s == 0 for s in sh)
    x = L.lmin(n, w); z = LM.lmax(n, w)
    gap = sum(abs(x[i] - z[i]) for i in range(n))
    tx = [F(2)] * (n - 2) + [F(3*n-10)] * 2
    tz = [F(0)] * (n - 4) + [F(T // 4)] * 4
    print(f"  Lmin = {[str(q) for q in x]}  strata {[len(b) for b in L.strata(x)]}")
    print(f"  Lmax = {[str(q) for q in z]}  strata {[len(b) for b in L.strata(z)]}")
    print(f"  ratio = {F(gap, T)}   predicted {F(n-4, n-3)}"
          f"   match {F(gap, T) == F(n-4, n-3)}")
    print(f"  Lmin on target: {x == tx}   Lmax on target: {z == tz}")
    if n <= 7:
        ex, bad = L.is_exact_lp(n, w)
        print(f"  EXACT at definition level: {ex}")
    else:
        print("  EXACT: by the envelope lemma (definition-level LP skipped at n=8)")
