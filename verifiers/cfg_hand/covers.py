"""TARGET 2 groundwork: reduce  mu = lambda  to a finite family of covers.

DERIVATION (by hand; this script only enumerates and tests).
  mu = max{t : exists y in Core, y >= t*1}.  Put u = y - t*1 and
  g_t(S) = f(S) - t|S|.  Feasibility needs g_t >= 0, i.e. t <= lambda -- that is
  A2.  At t = lambda,
      mu = lambda  <=>  max{u(N) : u >= 0, u(S) <= g(S) for proper S} >= g(N),
  where g := g_lambda >= 0 and g(N) := T - n*lambda.  LP duality turns the max
  into a min over FRACTIONAL COVERS (beta >= 0 with load c_k = sum_{S ni k}
  beta_S >= 1 for every k):
      mu = lambda  <=>  sum_S beta_S g(S) >= g(N)  for every fractional cover.
  The min is attained at a vertex, so only vertices matter.

  LEMMA (balanced covers are free).  If c_k = 1 for every k then, for any core
  point y, sum_S beta_S g(S) >= sum_k c_k (y_k - lambda) = sum_k (y_k - lambda)
  = g(N).  So a BALANCED cover can never witness failure, for any game with a
  nonempty core, at any n.
  COROLLARY (localization).  mu = lambda can only fail through a vertex cover
  carrying STRICT EXCESS LOAD on some player.

This script enumerates the vertices at n = 5, splits them by that criterion,
and measures the surviving ones on genuine exact games.
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L

n = 5
PROPER = [S for S in range(1, (1 << n) - 1)]

def solve(A, b):
    k = len(A)
    M = [list(map(F, A[r])) + [F(b[r])] for r in range(k)]
    for c in range(k):
        p = next((r for r in range(c, k) if M[r][c] != 0), None)
        if p is None:
            return None
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [q / pv for q in M[c]]
        for r in range(k):
            if r != c and M[r][c] != 0:
                fpar = M[r][c]
                M[r] = [M[r][j] - fpar * M[c][j] for j in range(k + 1)]
    return [M[r][k] for r in range(k)]

verts = set()
for s in range(1, n + 1):
    for Sig in itertools.combinations(PROPER, s):
        for K in itertools.combinations(range(n), s):
            A = [[1 if (S >> k) & 1 else 0 for S in Sig] for k in K]
            x = solve(A, [1] * s)
            if x is None or any(q <= 0 for q in x):
                continue
            load = [sum(x[i] for i, S in enumerate(Sig) if (S >> k) & 1)
                    for k in range(n)]
            if any(c < 1 for c in load):
                continue
            verts.add((Sig, tuple(x), tuple(load)))

bal = [v for v in verts if all(c == 1 for c in v[2])]
exc = [v for v in verts if any(c > 1 for c in v[2])]
print(f"vertices of the fractional-cover polyhedron at n=5 : {len(verts)}")
print(f"  balanced (load == 1 everywhere), provably harmless : {len(bal)}")
print(f"  carrying strict excess load, the only candidates   : {len(exc)}")
sizes = {}
for Sig, b, c in exc:
    sizes[len(Sig)] = sizes.get(len(Sig), 0) + 1
print(f"  excess-load vertices by support size               : {dict(sorted(sizes.items()))}")
shapes = {}
for Sig, b, c in exc:
    key = tuple(sorted(bin(S).count("1") for S in Sig))
    shapes[key] = shapes.get(key, 0) + 1
print(f"  excess-load vertices by coalition-size multiset (top 8):")
for k, v in sorted(shapes.items(), key=lambda kv: -kv[1])[:8]:
    print(f"      sizes {k}: {v}")
import json
json.dump({"total": len(verts), "balanced": len(bal), "excess": len(exc),
           "excess_by_support": {str(k): v for k, v in sizes.items()}},
          open("covers.json", "w"), indent=1)

# ---------------------------------------------------------------- refinement
# SHARPER LEMMA.  The cover inequality holds as soon as SOME core point y has
# y_k >= lambda for every k in the EXCESS SET E = {k : c_k > 1}: then
#   sum_S beta_S g(S) >= sum_k c_k (y_k - lambda) >= sum_k (y_k - lambda) = g(N),
# the middle step because (c_k - 1)(y_k - lambda) >= 0 termwise.
# For |E| = 1, E = {k}, such a y exists: exactness at {k} gives a core point
# with y_k = f({k}) >= lambda.  So |E| = 1 vertices are harmless too.
print()
print("REFINEMENT by excess set E = {k : c_k > 1}")
dist = {}
for Sig, b, c in exc:
    e = sum(1 for q in c if q > 1)
    dist[e] = dist.get(e, 0) + 1
print(f"  excess-load vertices by |E| : {dict(sorted(dist.items()))}")
killed = dist.get(1, 0)
print(f"  |E| = 1 killed by exactness at a singleton   : {killed}")
rem = len(exc) - killed
print(f"  REMAINING candidates (|E| >= 2)              : {rem}"
      f"   ({100*rem/len(verts):.1f}% of all vertices)")
shapes2 = {}
for Sig, b, c in exc:
    if sum(1 for q in c if q > 1) < 2:
        continue
    key = (len(Sig), sum(1 for q in c if q > 1))
    shapes2[key] = shapes2.get(key, 0) + 1
print(f"  remaining by (support size, |E|) : {dict(sorted(shapes2.items()))}")
