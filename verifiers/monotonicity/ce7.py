"""Candidate counterexample to C-A(a): put an untouched RICH pair above the
loser block, by direct-summing the n=5 RST/monotonicity witness with a
2-player component of value 20.

Players 0..4 = a,b,c,d,e  (witness u = envelope of A,B,P)
Players 5,6 = f,g         (component: v(fg)=20, v(f)=v(g)=0)
Bump S = {a,c,d,e} by d=2, exactly as in the published 5-player witness.
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
import audit, z3

N5, N = 5, 7
FULL = (1 << N) - 1
gens = [tuple(F(q) for q in g) for g in [(2,0,12,6,0),(0,0,0,0,20),(0,2,10,4,4)]]
u = audit.envelope(N5, gens)                       # base 5-player witness
u2 = audit.envelope(N5, gens[:2])                  # bumped: envelope of {A,B}
assert all(u2[T] == u[T] for T in range(32) if T != 29)
assert u2[29] - u[29] == 2, (u[29], u2[29])
COMP = 20

def lift(u5):
    v = [F(0)] * (1 << N)
    for T in range(1 << N):
        c = T >> 5
        v[T] = u5[T & 31] + (F(COMP) if c == 3 else F(0))
    return v

v = lift(u)
S = 0b0011101                                      # {a,c,d,e} = 29
d = F(2)
vp = list(v); vp[S] = v[S] + d                     # GENUINE single-coalition bump
assert all(vp[T] == v[T] for T in range(1 << N) if T != S)
assert all(v[1 << i] == 0 for i in range(N)) and all(vp[1 << i] == 0 for i in range(N))
NAMES = "abcdefg"
def nm(m): return "{" + ",".join(NAMES[i] for i in range(N) if m >> i & 1) + "}"

# ---------- verification 1: staged z3 leximin (audit.lmin) ----------
phi  = audit.lmin(N, v)
phi2 = audit.lmin(N, vp)
print("phi  =", [str(q) for q in phi])
print("phi' =", [str(q) for q in phi2])

# ---------- verification 2: independent leximin via the Sigma_m ladder ----------
# theta(x) >=_lex theta(y)  iff  (Sigma_1,...,Sigma_n)(x) >=_lex (...)(y),
# Sigma_m(x) = min over |A|=m of x(A).  Maximize Sigma_1, then Sigma_2, ...
def lmin_ladder(n, val):
    full = (1 << n) - 1
    x = [z3.Real(f"y{i}") for i in range(n)]
    base = [z3.Sum(x) == audit.to_z3(val[full])] + [
        z3.Sum([x[i] for i in range(n) if T >> i & 1]) >= audit.to_z3(val[T])
        for T in range(1, full)]
    fixed = []
    for m in range(1, n + 1):
        s = z3.Real(f"s{m}")
        cons = base + fixed + [
            s <= z3.Sum([x[i] for i in A])
            for A in itertools.combinations(range(n), m)]
        o = z3.Optimize(); o.add(cons); h = o.maximize(s)
        assert o.check() == z3.sat
        best = audit.rat(o.upper(h))
        fixed.append(z3.And([z3.Sum([x[i] for i in A]) >= audit.to_z3(best)
                             for A in itertools.combinations(range(n), m)]))
    # recover the unique point
    o = z3.Optimize(); o.add(base + fixed)
    assert o.check() == z3.sat
    mdl = o.model()
    pt = [audit.rat(mdl.eval(x[i], model_completion=True)) for i in range(n)]
    # uniqueness check: no other core point satisfies the same ladder
    sv = z3.Solver(); sv.add(base + fixed)
    sv.add(z3.Or([x[i] != audit.to_z3(pt[i]) for i in range(n)]))
    assert sv.check() == z3.unsat, "ladder point not unique"
    return pt

lphi, lphi2 = lmin_ladder(N, v), lmin_ladder(N, vp)
print("ladder phi  =", [str(q) for q in lphi], "MATCH", lphi == phi)
print("ladder phi' =", [str(q) for q in lphi2], "MATCH", lphi2 == phi2)

# ---------- verification 3: product structure ----------
p5, p5b = audit.lmin(N5, u), audit.lmin(N5, u2)
print("5-player Lmin(base) =", [str(q) for q in p5],
      " Lmin(bumped) =", [str(q) for q in p5b])
print("product prediction MATCH:",
      phi == p5 + [F(COMP, 2)] * 2 and phi2 == p5b + [F(COMP, 2)] * 2)

# ---------- exactness of both games (exact rational LP, all coalitions) ----------
def exact_all(n, val):
    full = (1 << n) - 1
    x = [z3.Real(f"z{i}") for i in range(n)]
    base = [z3.Sum(x) == audit.to_z3(val[full])] + [
        z3.Sum([x[i] for i in range(n) if T >> i & 1]) >= audit.to_z3(val[T])
        for T in range(1, full)]
    for T in range(1, full):
        o = z3.Optimize(); o.add(base)
        h = o.minimize(z3.Sum([x[i] for i in range(n) if T >> i & 1]))
        if o.check() != z3.sat or audit.rat(o.lower(h)) != val[T]:
            return False, T
    return True, None
print("v  exact:", exact_all(N, v))
print("v' exact:", exact_all(N, vp))

# ---------- the C-A verdict ----------
blocks = audit.strata(phi)
print("strata (poor->rich):", [[NAMES[i] for i in b] for b in blocks],
      [str(phi[b[0]]) for b in blocks])
sufs = [sum(1 << i for b in blocks[j+1:] for i in b) for j in range(len(blocks)-1)]
print("richer suffixes and slacks:",
      [(nm(H), str(sum(phi[i] for i in range(N) if H >> i & 1) - v[H])) for H in sufs])
W = [i for i in range(N) if S >> i & 1 and phi2[i] < phi[i]]
Wm = sum(1 << i for i in W)
print("S =", nm(S), " d =", str(d))
print("W (strict losers in S) =", nm(Wm))
print("global strict losers =", nm(sum(1 << i for i in range(N) if phi2[i] < phi[i])))
print("W is a richer suffix?", Wm in sufs, "  <-- C-A(a) requires True")
print("s_phi(W) =", str(sum(phi[i] for i in range(N) if Wm >> i & 1) - v[Wm]),
      " loss on W =", str(sum(phi[i] - phi2[i] for i in W)))
for H in sufs:
    print("   H =", nm(H), " H&S =", nm(H & S), " equals W?", (H & S) == Wm,
          " slack", str(sum(phi[i] for i in range(N) if H >> i & 1) - v[H]))
