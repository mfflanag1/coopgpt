"""STEP R: the key lemma must FAIL on genuine CFG games (mu = T/8 exactly).

If it held there, the hand proof of PROOF_A3.txt would prove mu > T/8, which is
FALSE -- CFG games with mu = T/8 exist.  So this is the sharpness control: it
must find the violating f-tight set, and that set must be of the predicted
shape S = {j, p_other} (complement U = {p_i} u R, shape (a,b,eps)=(1,2,0)).
"""
import sys, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L
import lmax as LM

n = 5
FULL = 31

def strata_of(vec):
    return L.strata(vec)

def cfg_scan(seed, tries):
    rng = random.Random(seed)
    out = []
    for _ in range(tries):
        total = rng.randint(5, 20)
        gens = []
        for _ in range(rng.randint(2, 5)):
            p = [rng.randint(0, total) for _ in range(n - 1)]
            last = total - sum(p)
            if last < 0:
                break
            gens.append(tuple(F(q) for q in p + [last]))
        else:
            if any(min(g[i] for g in gens) != 0 for i in range(n)):
                continue
            w, sh = L.normalize(n, L.envelope(n, gens))
            if w[FULL] <= 0:
                continue
            try:
                x = L.lmin(n, w); z = LM.lmax(n, w)
            except Exception:
                continue
            if x is None:
                continue
            T = w[FULL]
            sx, sz = strata_of(x), strata_of(z)
            # CFG: Lmin strata (3,2); Lmax strata (1,4) with the singleton at 0
            if [len(b) for b in sx] != [3, 2]:
                continue
            if [len(b) for b in sz] != [1, 4]:
                continue
            if z[sz[0][0]] != 0:
                continue
            out.append((w, x, z, T, sx, sz))
    return out

games = cfg_scan(11, 4000)
print(f"genuine CFG games found: {len(games)}")
shown = 0
allviol = []
for (w, x, z, T, sx, sz) in games:
    P = set(sx[0]); R = set(sx[1]); j = sz[0][0]
    mu = x[sx[0][0]]; rho = x[sx[1][0]]
    assert j in P, "j must be Lmin-poor (L2')"
    pp = sorted(P - {j})
    # f-tight sets S: x(S) = f(S) = T - v(N\S)
    viol = []
    for S in range(1, FULL):
        U = FULL ^ S
        xs = sum(x[i] for i in range(n) if S >> i & 1)
        if xs != T - w[U]:
            continue
        lhs = len([i for i in pp if S >> i & 1])
        rhs = len([i for i in R if S >> i & 1])
        if lhs > rhs:
            a = len([i for i in P if U >> i & 1]); b = len([i for i in R if U >> i & 1])
            e = 1 if (U >> j) & 1 else 0
            viol.append((L.nm(n, S), lhs, rhs, (a, b, e)))
    allviol.append(bool(viol))
    if shown < 3 and viol:
        shown += 1
        print(f"  game T={T} mu={mu} (mu/T={mu/T}) rho/T={rho/T} j={L.LETTERS[j]}")
        print(f"    violating f-tight sets: {viol}")
print()
print(f"games where the key lemma FAILS: {sum(allviol)}/{len(allviol)}"
      f"   (must be all of them, else the proof would prove too much)")
shapes = set()
for (w, x, z, T, sx, sz) in games:
    P = set(sx[0]); R = set(sx[1]); j = sz[0][0]; pp = sorted(P - {j})
    for S in range(1, FULL):
        U = FULL ^ S
        if sum(x[i] for i in range(n) if S >> i & 1) != T - w[U]:
            continue
        if len([i for i in pp if S >> i & 1]) > len([i for i in R if S >> i & 1]):
            a = len([i for i in P if U >> i & 1]); b = len([i for i in R if U >> i & 1])
            shapes.add((a, b, 1 if (U >> j) & 1 else 0))
print(f"violating shapes observed: {sorted(shapes)}   (predicted: [(1, 2, 0)])")
