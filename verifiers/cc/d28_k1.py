"""d28: the k=1 scope hole.  paper4's thm:expart and cor:allfail quantify over
exact-partition phi.  A CONSTANT phi (one payoff stratum) has NO richer suffixes,
so it is vacuously exact-partition and has no slack richer suffix -- but the lab
enumerated only NONEMPTY gap patterns, i.e. k >= 2.  Is a failure possible there?
If yes, cor:allfail ("every five-player failure has a slack richer suffix") is FALSE.
"""
import sys, itertools, z3
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
n, FULL = 5, 31
props = list(range(1, FULL))
def bits(T): return [i for i in range(n) if T >> i & 1]
s = z3.Solver()
v = {T: z3.Real("v_%d" % T) for T in props}; v[FULL] = z3.RealVal(1)
phi = [z3.Real("p_%d" % i) for i in range(n)]
ph2 = [z3.Real("q_%d" % i) for i in range(n)]
al = z3.Real("alpha")
def tot(x, T): return z3.Sum([x[i] for i in bits(T)])
for i in range(n): s.add(v[1 << i] == 0)
s.add(al > 0)
for i in range(n - 1): s.add(phi[i] == phi[i + 1])        # k = 1: constant phi
cand = [T for T in props if bin(T).count("1") >= 2]
isS = {T: z3.Bool("isS_%d" % T) for T in cand}
s.add(z3.PbEq([(isS[T], 1) for T in cand], 1))
inS = [z3.Bool("inS_%d" % i) for i in range(n)]
for T in cand:
    s.add(z3.Implies(isS[T], z3.And([inS[i] for i in bits(T)] +
                                    [z3.Not(inS[i]) for i in range(n) if not T >> i & 1])))
v2 = {}
for T in props:
    w = z3.Real("w_%d" % T); v2[T] = w
    s.add(z3.If(isS[T], w == v[T] + al, w == v[T]) if T in isS else w == v[T])
v2[FULL] = z3.RealVal(1)
s.add(tot(phi, FULL) == v[FULL]); s.add(tot(ph2, FULL) == v2[FULL])
for T in props:
    s.add(tot(phi, T) >= v[T]); s.add(tot(ph2, T) >= v2[T])
for A in props:                                            # superadditivity
    for B in props:
        if A < B and not (A & B): s.add(v[A | B] >= v[A] + v[B])
for T in props:                                            # exactness of v and v'
    y = [z3.Real("y%d_%d" % (T, i)) for i in range(n)]
    s.add(tot(y, FULL) == v[FULL]); s.add(tot(y, T) == v[T])
    for U in props: s.add(tot(y, U) >= v[U])
    zz = [z3.Real("z%d_%d" % (T, i)) for i in range(n)]
    s.add(tot(zz, FULL) == v2[FULL]); s.add(tot(zz, T) == v2[T])
    for U in props: s.add(tot(zz, U) >= v2[U])
for m in range(n):                                         # Lemma L for phi'
    lam = {T: z3.Real("L%d_%d" % (m, T)) for T in props}; nu = z3.Real("nu%d" % m)
    for T in props:
        s.add(lam[T] >= 0)
        s.add(z3.Implies(lam[T] > 0, tot(ph2, T) == v2[T]))
    for i in range(n):
        cov = z3.Sum([lam[T] for T in props if T >> i & 1])
        s.add(z3.Implies(ph2[i] > ph2[m], cov == nu))
        s.add(z3.Implies(ph2[i] == ph2[m], cov <= nu - 1))
s.add(z3.Or([z3.And(inS[i], ph2[i] < phi[i]) for i in range(n)]))   # a failure in S
s.set("timeout", 900000)
r = s.check()
print("k=1 (constant phi), n=5, failure in S:", r)
print("  unsat => cor:allfail's scope hole is harmless; sat => cor:allfail is FALSE")
