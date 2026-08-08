"""d8: faithfulness control for the n=5 lab.

The lab's UNSAT verdicts are worth nothing unless every condition it encodes is
genuinely satisfied by a REAL exact-domain monotonicity failure.  This driver
takes the five-player violation found by d7, verifies it end to end from the
generators, and then checks each of the lab's condition groups on it directly
(not by a z3 search over the shape, but by evaluating the group on the witness).

It also feeds the witness into the lab's own constraint system with every value
pinned, and asserts z3 returns sat: that proves the encoding admits it.
"""
import sys, json, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import d2_lab as lab
import d3_lemmaL as LL
import z3

n = 5
FULL = 31
ROWS = [(0, 3, 0, 3, 0), (0, 0, 0, 0, 6), (1, 0, 1, 0, 4)]
S = 0b11010          # {2,4,5}
ALPHA = F(1, 4)

print("witness rows (common total %d): %s" % (sum(ROWS[0]), ROWS))
v = L.envelope(n, [tuple(F(q) for q in r) for r in ROWS])
print("singleton-normalized:", L.is_sing_norm(n, v), " v(N) =", v[FULL])
okv, badv = L.exactness_report(n, v)
print("v exact (all 30 proper coalitions, z3-certified):", okv, badv[:3])
phi = L.lmin(n, v, both=True)
print("phi  =", [str(q) for q in phi], "(staged + ladder agree, ladder unique)")
w = L.bumped(v, S, ALPHA)
okw, badw = L.exactness_report(n, w)
print("S =", L.nm(n, S), " alpha =", ALPHA, " s_phi(S) =", L.slack(n, v, phi, S),
      " alpha_ex =", L.alpha_exact_max(n, v, S))
print("v' exact (all 30 proper coalitions, z3-certified):", okw, badw[:3])
phi2 = L.lmin(n, w, both=True)
print("phi' =", [str(q) for q in phi2], "(staged + ladder agree, ladder unique)")
Wl = [i for i in L.members(n, S) if phi2[i] < phi[i]]
Wm = sum(1 << i for i in Wl)
H, js = L.hstar(n, v, phi)
print("strata poor->rich:", [[i + 1 for i in b] for b in L.strata(n, phi)])
print("richer suffixes / slacks:",
      [(L.nm(n, Hj), str(s)) for _, Hj, s in L.suffixes(n, v, phi)])
print("H* =", L.nm(n, H), " W =", L.nm(n, Wm),
      " all losers =", L.nm(n, sum(1 << i for i in range(n) if phi2[i] < phi[i])),
      " gainers =", L.nm(n, sum(1 << i for i in range(n) if phi2[i] > phi[i])))
print("C-C left:", (Wm & ~H) == 0, "  C-C right:", (H & ~S) == 0)
assert okv and okw and Wl, "not a certified exact-domain violation"

print("\n--- each lab condition group evaluated on the witness ---")
D = [phi2[i] - phi[i] for i in range(n)]
res = {}
res["core"] = (L.xsum(phi, n, FULL) == v[FULL] and L.xsum(phi2, n, FULL) == w[FULL]
               and all(L.xsum(phi, n, T) >= v[T] for T in L.masks(n))
               and all(L.xsum(phi2, n, T) >= w[T] for T in L.masks(n)))
res["sup"] = all(v[A | B] >= v[A] + v[B] for A in L.masks(n) for B in L.masks(n)
                 if A < B and not (A & B))
res["exv"] = okv
res["exv2"] = okw
res["cert"] = all(LL.all_cuts_ok(n, v, phi))
res["cert2"] = all(LL.all_cuts_ok(n, w, phi2))
sg = [min(sum(phi2[i] for i in A) for A in itertools.combinations(range(n), m))
      for m in range(1, n + 1)]
sf = [min(sum(phi[i] for i in A) for A in itertools.combinations(range(n), m))
      for m in range(1, n + 1)]
res["worse"] = any(sg[m] < sf[m] and all(sg[l] == sf[l] for l in range(m))
                   for m in range(n))
suf = L.suffixes(n, v, phi)
res["hstar"] = (L.slack(n, v, phi, H) > 0 and
                all(s == 0 for j, Hj, s in suf if j > js))
for k in lab.ALLGROUPS:
    print("  %-6s %s" % (k, res[k]))
assert all(res.values()), "the witness violates a condition the lab encodes"

print("\n--- Prop D+, Lemma C+ and the master inequalities on the witness ---")
pd = all(L.xsum(D, n, T) >= 0 for T in L.masks(n) if L.xsum(phi, n, T) == v[T])
lc = all(L.xsum(D, n, T) <= 0 for T in L.masks(n)
         if T != S and L.xsum(phi2, n, T) == w[T])
print("  Prop D+  (every proper phi-tight T has Delta(T) >= 0):", pd)
print("  Lemma C+ (every proper phi'-tight T != S has Delta(T) <= 0):", lc)
print("  Delta(S) =", str(L.xsum(D, n, S)), " rho =", str(ALPHA - L.slack(n, v, phi, S)),
      " S phi'-tight:", L.xsum(phi2, n, S) == w[S])
assert pd and lc

print("\n--- the lab's own constraint system, with the witness pinned ---")
gaps, cstar = (4,), 4
s, Hd = lab.build(n, gaps, cstar, "control", lab.ALLGROUPS)
sc = F(1, v[FULL])                       # the lab normalizes v(N) = 1
for T in L.masks(n):
    s.add(Hd["v"][T] == lab.z3.RealVal("%d/%d" % ((v[T] * sc).numerator,
                                                  (v[T] * sc).denominator)))
for i in range(n):
    for x, val in ((Hd["phi"], phi), (Hd["ph2"], phi2)):
        q = val[i] * sc
        s.add(x[i] == lab.z3.RealVal("%d/%d" % (q.numerator, q.denominator)))
s.add(Hd["isS"][S])
q = ALPHA * sc
s.add(Hd["al"] == lab.z3.RealVal("%d/%d" % (q.numerator, q.denominator)))
s.set("timeout", 600000)
r = s.check()
print("  z3 on the pinned witness:", r, " (must be sat)")
assert r == z3.sat, "the lab encoding rejects a real violation -- UNSAT verdicts are void"
print("\nFAITHFULNESS CONTROL PASSED: the n=5 encoding admits a genuine, fully")
print("certified exact-domain monotonicity failure, so its UNSAT verdicts bite.")
