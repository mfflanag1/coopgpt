"""Is exactness essential to mu = lambda at n = 5?

By hand: the residual cover inequality for the single surviving shape reads
    v({q,y,z}) + v({x,z}) + v({x,y})  <=  2T - 3*lambda.
BALANCEDNESS alone gives only 2T (the collection above plus 2*{p} + {q} is
balanced with r = 2, and v of a singleton is 0), or at best 2T - v({p,q}) using
{p,q} + {p} instead.  Neither reaches 2T - 3*lambda.  So any proof must use
exactness somewhere.  This script tries to CONFIRM that by exhibiting a
balanced (nonempty core) but NOT exact five-player game with mu < lambda.
If one exists, exactness is not a convenience -- it is load-bearing.
"""
import sys, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, z3
n = 5; FULL = 31; PROPER = [S for S in range(1, FULL)]

def core_nonempty(w):
    x = [z3.Real(f"c{i}") for i in range(n)]
    s = z3.Solver()
    s.add(z3.Sum(x) == L.to_z3(w[FULL]))
    for S in PROPER:
        s.add(z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= L.to_z3(w[S]))
    for i in range(n):
        s.add(x[i] >= 0)
    return s.check() == z3.sat

def mu_of(w):
    x = [z3.Real(f"m{i}") for i in range(n)]; t = z3.Real("t")
    o = z3.Optimize()
    o.add(z3.Sum(x) == L.to_z3(w[FULL]))
    for S in PROPER:
        o.add(z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= L.to_z3(w[S]))
    for i in range(n):
        o.add(x[i] >= 0, x[i] >= t)
    h = o.maximize(t); assert o.check() == z3.sat
    return L.rat(o.upper(h))

rng = random.Random(23)
found = None; tested = 0
while tested < 3000 and not found:
    T = rng.randint(4, 12)
    w = [F(0)] * 32
    w[FULL] = F(T)
    for S in PROPER:
        k = bin(S).count("1")
        w[S] = F(rng.randint(0, max(0, (T * k) // 5)))
    for i in range(n):
        w[1 << i] = F(0)
    if not core_nonempty(w):
        continue
    tested += 1
    lam = min(F(w[FULL] - w[FULL ^ S], bin(S).count("1")) for S in PROPER)
    mu = mu_of(w)
    if mu < lam:
        ex, bad = L.is_exact_lp(n, w)
        found = (w, mu, lam, ex)
print(f"balanced games tested: {tested}")
if found:
    w, mu, lam, ex = found
    print(f"FOUND a balanced game with mu < lambda:")
    print(f"  T = {w[FULL]},  mu = {mu},  lambda = {lam},  gap = {lam - mu}")
    print(f"  exact? {ex}   (must be False -- else it would refute thm:n5closed)")
    print(f"  v = {{{', '.join(f'{L.nm(n,S)}:{w[S]}' for S in PROPER if w[S] != 0)}}}")
    print("  => exactness is LOAD-BEARING: mu = lambda is false for balanced games")
    print("     at n = 5, so no proof of the residual inequality can avoid it.")
else:
    print("no balanced counterexample found in this sample")
