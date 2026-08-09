"""TARGET 2, round 2: two more free-vertex lemmas, and what is left.

Recall the reduction: mu = lambda iff every cover vertex beta satisfies
sum_S beta_S g(S) >= g(N), g(S) = f(S) - lambda|S|.  For ANY core point y,
    sum_S beta_S g(S) - g(N)  >=  sum_k (c_k - 1)(y_k - lambda),
so a vertex is FREE as soon as some core point y has
    sum_{k in E} w_k (y_k - lambda) >= 0,    w_k := c_k - 1 > 0,  E = {c_k > 1}.

LEMMA C (equal excess).  If w is constant on E then the requirement is
y(E) >= lambda|E| for some core point, and max_y y(E) = f(E) >= lambda|E| by
the definition of lambda.  So every vertex with EQUAL excess loads is free.

COROLLARY (support 2).  A support-2 vertex has S1 u S2 = N with
A = S1\\S2, B = S2\\S1 both nonempty, beta = (1,1), and E = S1 n S2 carrying
c = 2 throughout -- equal excess.  Free by Lemma C.  (Directly:
g(S1)+g(S2) >= g(N) reads v(A)+v(B) <= T - lambda|C|, and v(A)+v(B) <=
T - max_y y(C) = T - f(C) <= T - lambda|C|.)

This script re-runs the enumeration and applies Lemma C.
"""
import sys, itertools, json
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")

n = 5
PROPER = [S for S in range(1, (1 << n) - 1)]

def solve(A, b):
    k = len(A); M = [list(map(F, A[r])) + [F(b[r])] for r in range(k)]
    for c in range(k):
        p = next((r for r in range(c, k) if M[r][c] != 0), None)
        if p is None: return None
        M[c], M[p] = M[p], M[c]; pv = M[c][c]; M[c] = [q / pv for q in M[c]]
        for r in range(k):
            if r != c and M[r][c] != 0:
                fp = M[r][c]; M[r] = [M[r][j] - fp * M[c][j] for j in range(k + 1)]
    return [M[r][k] for r in range(k)]

verts = set()
for s in range(1, n + 1):
    for Sig in itertools.combinations(PROPER, s):
        for K in itertools.combinations(range(n), s):
            A = [[1 if (S >> k) & 1 else 0 for S in Sig] for k in K]
            x = solve(A, [1] * s)
            if x is None or any(q <= 0 for q in x): continue
            load = tuple(sum(x[i] for i, S in enumerate(Sig) if (S >> k) & 1)
                         for k in range(n))
            if any(c < 1 for c in load): continue
            verts.add((Sig, tuple(x), load))

def excess(v):
    return [k for k in range(n) if v[2][k] > 1]

free_B = [v for v in verts if not excess(v)]                       # balanced
rest = [v for v in verts if excess(v)]
free_E1 = [v for v in rest if len(excess(v)) == 1]
rest2 = [v for v in rest if len(excess(v)) >= 2]
def equal_excess(v):
    E = excess(v); return len({v[2][k] for k in E}) == 1
free_C = [v for v in rest2 if equal_excess(v)]
left = [v for v in rest2 if not equal_excess(v)]

print(f"cover vertices at n=5                      : {len(verts)}")
print(f"  free by Lemma B  (balanced)              : {len(free_B)}")
print(f"  free by Lemma E1 (|E| = 1)               : {len(free_E1)}")
print(f"  free by Lemma C  (equal excess on E)     : {len(free_C)}")
print(f"  REMAINING                                : {len(left)}")
if left:
    by = {}
    for v in left:
        by[(len(v[0]), len(excess(v)))] = by.get((len(v[0]), len(excess(v))), 0) + 1
    print(f"  remaining by (support, |E|)              : {dict(sorted(by.items()))}")
    ws = {}
    for v in left:
        E = excess(v); w = tuple(sorted(v[2][k] - 1 for k in E))
        ws[w] = ws.get(w, 0) + 1
    print(f"  remaining by excess-weight multiset      :")
    for k, c in sorted(ws.items(), key=lambda kv: -kv[1])[:10]:
        print(f"      w = {tuple(str(q) for q in k)} : {c}")
    ex = left[0]
    print(f"  example: support {[bin(S).count('1') for S in ex[0]]}, "
          f"beta {[str(q) for q in ex[1]]}, loads {[str(q) for q in ex[2]]}")
json.dump({"vertices": len(verts), "freeB": len(free_B), "freeE1": len(free_E1),
           "freeC": len(free_C), "left": len(left)}, open("covers2.json","w"), indent=1)
