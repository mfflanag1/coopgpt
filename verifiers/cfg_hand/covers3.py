"""TARGET 2, round 3: identify the residue and test the remaining requirement.

Claim: the 60 survivors are ONE shape up to relabelling, namely
    S1 = {p,x},   S2 = {p,q,y},   S3 = {p,q,z},   beta = (1,1,1),
with loads p:3, q:2, x,y,z:1 -- so E = {p,q} with excess weights (2,1).
For it the cover inequality is equivalent to
    max_{y in Core} ( 2 y_p + y_q )  >=  3 lambda.                        (R)

LEMMA D (the eta >= 0 half).  Dualizing max sum_k w_k y_k over
Core = {y>=0, y(N)=T, y(S)<=f(S)} gives
    min { eta T + sum_S gamma_S f(S) : gamma >= 0, eta + Gamma_k >= w_k },
Gamma_k = sum_{S ni k} gamma_S.  If eta >= 0 then, using f(S) >= lambda|S|,
    eta T + sum_S gamma_S f(S) >= eta T + lambda sum_k Gamma_k
                               >= eta T + lambda sum_k (w_k - eta)
                               = 3 lambda + eta (T - 5 lambda)  >=  3 lambda,
since T >= 5 lambda.  So (R) can only fail through a dual optimum with eta < 0.
"""
import sys, itertools, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, z3

n = 5
PROPER = [S for S in range(1, (1 << n) - 1)]
def solve(A, b):
    k = len(A); M = [list(map(F, A[r])) + [F(b[r])] for r in range(k)]
    for c in range(k):
        p = next((r for r in range(c, k) if M[r][c] != 0), None)
        if p is None: return None
        M[c], M[p] = M[p], M[c]; pv = M[c][c]; M[c] = [q/pv for q in M[c]]
        for r in range(k):
            if r != c and M[r][c] != 0:
                fp = M[r][c]; M[r] = [M[r][j]-fp*M[c][j] for j in range(k+1)]
    return [M[r][k] for r in range(k)]
verts = set()
for s in range(1, n+1):
    for Sig in itertools.combinations(PROPER, s):
        for K in itertools.combinations(range(n), s):
            A = [[1 if (S>>k)&1 else 0 for S in Sig] for k in K]
            x = solve(A, [1]*s)
            if x is None or any(q <= 0 for q in x): continue
            load = tuple(sum(x[i] for i,S in enumerate(Sig) if (S>>k)&1) for k in range(n))
            if any(c < 1 for c in load): continue
            verts.add((Sig, tuple(x), load))
left = [v for v in verts
        if len([k for k in range(n) if v[2][k] > 1]) >= 2
        and len({v[2][k] for k in range(n) if v[2][k] > 1}) > 1]
print(f"residue: {len(left)}")
shapes = set()
for Sig, b, c in left:
    p = [k for k in range(n) if c[k] == 3][0]
    q = [k for k in range(n) if c[k] == 2][0]
    sizes = tuple(sorted(bin(S).count('1') for S in Sig))
    pat = tuple(sorted((bin(S).count('1'), (S>>p)&1, (S>>q)&1) for S in Sig))
    shapes.add((sizes, pat, tuple(sorted(str(x) for x in b))))
print(f"distinct shapes up to relabelling: {len(shapes)}")
for sh in shapes:
    print(f"   coalition sizes {sh[0]}, (size, contains p, contains q) = {sh[1]},"
          f" beta = {sh[2]}")
print("  -> S1 = {p,x}, S2 = {p,q,y}, S3 = {p,q,z}: confirmed"
      if len(shapes) == 1 else "  -> MORE THAN ONE SHAPE")

# empirical: does (R) ever come close to failing on genuine exact games?
print()
print("empirical margin of (R) on random exact 5-player games:")
rng = random.Random(3); worst = None; tested = 0
for _ in range(1200):
    total = rng.randint(5, 18); gens = []
    for _ in range(rng.randint(2, 5)):
        pp = [rng.randint(0, total) for _ in range(n-1)]; last = total - sum(pp)
        if last < 0: break
        gens.append(tuple(F(v) for v in pp + [last]))
    else:
        if any(min(g[i] for g in gens) != 0 for i in range(n)): continue
        w, sh = L.normalize(n, L.envelope(n, gens))
        T = w[(1<<n)-1]
        if T <= 0: continue
        f = {S: T - w[((1<<n)-1) ^ S] for S in PROPER}
        lam = min(F(f[S], bin(S).count('1')) for S in PROPER)
        tested += 1
        for p in range(n):
            for q in range(n):
                if p == q: continue
                x = [z3.Real(f"y{i}") for i in range(n)]
                o = z3.Optimize()
                o.add(z3.Sum(x) == L.to_z3(T))
                for S in PROPER:
                    o.add(z3.Sum([x[i] for i in range(n) if S>>i&1]) >= L.to_z3(w[S]))
                for i in range(n): o.add(x[i] >= 0)
                h = o.maximize(2*x[p] + x[q]); assert o.check() == z3.sat
                val = L.rat(o.upper(h))
                m = val - 3*lam
                if worst is None or m < worst[0]: worst = (m, T, p, q, lam, val)
print(f"  games tested {tested}; smallest margin max(2y_p+y_q) - 3*lambda = {worst[0]}")
print(f"    (T={worst[1]}, p={worst[2]}, q={worst[3]}, lambda={worst[4]}, max={worst[5]})")
print("  margin >= 0 in every case:", worst[0] >= 0)
