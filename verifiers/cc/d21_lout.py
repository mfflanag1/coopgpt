"""d21: the OUTSIDER SLACK lemma, and how much of the two-strata case it buys.

LEMMA (L-out).  Let v' = v^{S,alpha} and suppose only that v'(T) is attained on
core(v') for every T containing S (the same fragment Theorem B consumes).  Then
for EVERY nonempty A contained in N \\ S,
                        s_phi(A)  >=  alpha - s_phi(S)  =  rho .

PROOF.  Put T = S u A.  If T is proper, exactness of v' at T gives z in core(v')
with z(T) = v'(T) = v(T) (T =/= S since A is nonempty); if T = N take any
z in core(v'), for which z(N) = v(N) automatically.  Either way
   v(T) = z(S) + z(A) >= (v(S) + alpha) + v(A).
Since phi(T) >= v(T) and phi(T) = phi(S) + phi(A),
   phi(A) - v(A) >= v(S) + alpha - phi(S) = alpha - s_phi(S) = rho .   []

paper4's Theorem B states only the two extreme cases A = {j} (part ii, giving
phi_j >= rho) and A = N \\ S (part iii).  The general A is free and strictly
stronger: it says EVERY sub-coalition of the outsiders carries slack at least
rho, not just the singletons and the whole.

This driver (a) checks L-out on every certified violation on record, and
(b) asks whether L-out can REPLACE the full exactness of v' in the two-strata
case that d19 isolated -- if yes the hand proof needs only core + Lemma L +
L-out, if no, exactness of v' at coalitions NOT containing S is doing work that
L-out does not capture, which is exactly what summary2's localization test
predicted.
"""
import sys, json, glob
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import itertools, z3

# ---------------------------------------------------------------- (a) check
print("(a) L-out on every certified violation on record")


def check(n, v, S, alpha, tag):
    phi = L.lmin_staged(n, v)
    rho = alpha - L.slack(n, v, phi, S)
    out = [i for i in range(n) if not S >> i & 1]
    worst = None
    for k in range(1, len(out) + 1):
        for A in itertools.combinations(out, k):
            Am = sum(1 << i for i in A)
            sl = L.slack(n, v, phi, Am)
            if worst is None or sl < worst[0]:
                worst = (sl, Am)
    ok = worst[0] >= rho
    return ok, rho, worst, phi


rows_cases = [
    ("notsuffix n=6", 6, [(0, 11, 0, 7, 0, 0), (0, 10, 0, 4, 3, 1), (2, 0, 1, 0, 15, 0)],
     0b011111, F(9, 16)),
    ("notstratum n=6", 6, [(0, 15, 0, 14, 0, 0), (0, 9, 0, 9, 6, 5), (4, 0, 4, 0, 21, 0)],
     0b011111, F(23, 8)),
    ("n5 faithfulness witness", 5, [(0, 3, 0, 3, 0), (0, 0, 0, 0, 6), (1, 0, 1, 0, 4)],
     0b11010, F(1, 4)),
    ("n6 counterexample A", 6, [(6, 7, 11, 0, 13, 3), (0, 22, 0, 10, 0, 8),
                                (0, 0, 21, 0, 19, 0)], 0b111110, F(25, 16)),
    ("n6 counterexample B", 6, [(3, 0, 37, 0, 0, 0), (5, 4, 22, 0, 5, 4),
                                (0, 18, 0, 11, 11, 0)], 0b011110, F(17, 6)),
]
tot = good = 0
for tag, n, rows, S, al in rows_cases:
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    ok, rho, worst, phi = check(n, v, S, al, tag)
    tot += 1
    good += ok
    print("  %-26s rho=%-7s min_A s_phi(A)=%-7s at A=%-10s  L-out: %s"
          % (tag, rho, worst[0], L.nm(n, worst[1]), ok))

CE = [F(q) for q in
      [0, 0, 0, 106, 0, 136, 0, 136, 0, 161, 0, 161, 176, 297, 176, 297,
       0, 242, 0, 242, 242, 393, 242, 484, 176, 418, 176, 418, 418, 534, 418, 660]]
ok, rho, worst, phi = check(5, CE, 0b11101, F(20), "CC counterexample")
tot += 1
good += ok
print("  %-26s rho=%-7s min_A s_phi(A)=%-7s at A=%-10s  L-out: %s"
      % ("CC-left counterexample", rho, worst[0], L.nm(5, worst[1]), ok))

for f in glob.glob("n5_hits_log.json"):
    for h in json.load(open(f))["hits"]:
        v = L.envelope(5, [tuple(F(q) for q in r) for r in h["rows"]])
        o, _, _, _ = check(5, v, h["Smask"], F(h["alpha"]), "corpus")
        tot += 1
        good += o
print("  L-out holds on %d/%d certified instances (paper4 examples, both n=6"
      " counterexamples, the n=5 counterexample, and the n=5 corpus)" % (good, tot))
assert good == tot

# ------------------------------------------------- (b) can L-out replace exv2?
print("\n(b) two-strata case: does L-out replace the full exactness of v'?")
n, FULL = 5, 31
props = list(range(1, FULL))


def bits(T):
    return [i for i in range(n) if T >> i & 1]


def build(m, mode):
    S = (1 << m) - 1
    s = z3.Solver()
    v = {T: z3.Real("v_%d" % T) for T in props}
    v[FULL] = z3.RealVal(1)
    phi = [z3.Real("p_%d" % i) for i in range(n)]
    al = z3.Real("alpha")

    def tot_(x, T):
        return z3.Sum([x[i] for i in bits(T)])
    for i in range(n):
        s.add(v[1 << i] == 0)
    s.add(al > 0)
    for i in range(3):
        s.add(phi[i] == phi[i + 1])
    s.add(phi[3] < phi[4])
    s.add(tot_(phi, FULL) == v[FULL])
    for T in props:
        s.add(tot_(phi, T) >= v[T])
    lam = {T: z3.Real("l_%d" % T) for T in props}
    nu = z3.Real("nu")
    for T in props:
        s.add(lam[T] >= 0)
        s.add(z3.Implies(lam[T] > 0, tot_(phi, T) == v[T]))
    s.add(z3.Sum([lam[T] for T in props if T >> 4 & 1]) == nu)
    for i in range(4):
        s.add(z3.Sum([lam[T] for T in props if T >> i & 1]) <= nu - 1)
    rho = al - (tot_(phi, S) - v[S])
    s.add(rho > 0)
    if mode == "exv2":
        v2 = {T: (v[T] + al if T == S else v[T]) for T in props}
        v2[FULL] = z3.RealVal(1)
        for T in props:
            z = [z3.Real("z%d_%d" % (T, i)) for i in range(n)]
            s.add(z3.Sum(z) == v2[FULL])
            for U in props:
                s.add(tot_(z, U) >= v2[U])
            s.add(tot_(z, T) == v2[T])
    else:                                     # only L-out
        outs = [i for i in range(n) if not S >> i & 1]
        for k in range(1, len(outs) + 1):
            for A in itertools.combinations(outs, k):
                Am = sum(1 << i for i in A)
                s.add(tot_(phi, Am) - v[Am] >= rho)
    return s


for m in (2, 3, 4):
    for mode in ("exv2", "Lout"):
        s = build(m, mode)
        s.set("timeout", 300000)
        print("  S={1..%d}  hypotheses core+cert+%-5s ->  %s" % (m, mode, s.check()))
