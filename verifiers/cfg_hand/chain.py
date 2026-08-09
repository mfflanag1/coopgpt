"""TEST the lead's chain-attainment reformulation BEFORE relying on it.

Claim offered: in an exact five-player game, a nested pair of f-caps is
SIMULTANEOUSLY ATTAINABLE -- some core point y has
    y_p = f({p})   AND   y_p + y_q = f({p,q}).
If true it gives (R) at once: 2y_p + y_q = f({p}) + f({p,q}) >= lambda + 2lambda.

Tested exactly over random genuine exact five-player games and ALL ordered
pairs (p,q).  Also reports, when it fails, whether (R) itself still holds --
(R) is strictly weaker, so a failure of chain-attainment is not a failure of
the target.
"""
import sys, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, z3
n, FULL = 5, 31
PROPER = [S for S in range(1, FULL)]

def core_cons(x, w):
    c = [z3.Sum(x) == L.to_z3(w[FULL])]
    for S in PROPER:
        c.append(z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= L.to_z3(w[S]))
    for i in range(n):
        c.append(x[i] >= 0)
    return c

rng = random.Random(31)
tested = chain_ok = chain_fail = 0
fails = []
while tested < 200:
    total = rng.randint(4, 16)
    gens = []
    for _ in range(rng.randint(2, 5)):
        cuts = sorted(rng.randrange(total + 1) for _ in range(n - 1))
        gens.append(tuple(F(b - a) for a, b in zip([0] + cuts, cuts + [total])))
    if any(min(g[i] for g in gens) != 0 for i in range(n)):
        continue
    w, sh = L.normalize(n, L.envelope(n, gens))
    T = w[FULL]
    if T <= 0:
        continue
    tested += 1
    lam = min(F(T - w[FULL ^ S], bin(S).count("1")) for S in PROPER)
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            fp = T - w[FULL ^ (1 << p)]
            fpq = T - w[FULL ^ ((1 << p) | (1 << q))]
            x = [z3.Real(f"x{i}") for i in range(n)]
            s = z3.Solver(); s.add(core_cons(x, w))
            s.add(x[p] == L.to_z3(fp))
            s.add(x[p] + x[q] == L.to_z3(fpq))
            r = s.check()
            assert r != z3.unknown
            if r == z3.sat:
                chain_ok += 1
            else:
                chain_fail += 1
                # does (R) still hold there?
                y = [z3.Real(f"y{i}") for i in range(n)]
                o = z3.Optimize(); o.add(core_cons(y, w))
                h = o.maximize(2 * y[p] + y[q]); assert o.check() == z3.sat
                val = L.rat(o.upper(h))
                fails.append((val - 3 * lam, T, p, q, fp, fpq, val, lam))
print(f"games tested {tested}; ordered pairs {chain_ok + chain_fail}")
print(f"  chain-attainable : {chain_ok}")
print(f"  NOT attainable   : {chain_fail}")
if fails:
    worst = min(fails)
    print(f"  VERDICT: the chain-attainment claim is FALSE at n = 5.")
    print(f"  On the failures, (R) itself: min margin max(2y_p+y_q) - 3*lambda"
          f" = {worst[0]}  (>= 0 in all {len(fails)}: "
          f"{all(f[0] >= 0 for f in fails)})")
    e = fails[0]
    print(f"  example failure: T={e[1]} p={e[2]} q={e[3]} f(p)={e[4]} "
          f"f(pq)={e[5]} max(2y_p+y_q)={e[6]} vs f(p)+f(pq)={e[4]+e[5]}, "
          f"lambda={e[7]}")
else:
    print("  VERDICT: chain-attainment held on every pair tested.")
