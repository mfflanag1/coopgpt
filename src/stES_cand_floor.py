"""Deterministic exact floor-vertex escape search for the n=6 candidate.
Enumerate arrangement vertices where a subset Z (|Z|=k) of players sits at its
floor v({i}); the remaining n-1-k tight planes are coalition planes. Cheap for
larger k. Reliable (exact), unlike float sampling. Reports any undominated escape."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import in_core,is_imputation,is_dominated_by_core
from largeness_exact import exact_solve

V=[0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,2,2,2,2,1,3,1,3,3,3,3,3,1,3,1,3,3,4,3,4,4,6,4,6,5,6,6,7,4,6,4,6,6,7,6,8]
n=6; g=Game(n,[F(x) for x in V]); N=g.N
fl=[g.v[1<<i] for i in range(n)]
def undom(y):
    return is_imputation(g,y) and (not in_core(g,y)) and (not is_dominated_by_core(g,y)[0])
planes=[([1 if S>>i&1 else 0 for i in range(n)], g.v[S]) for S in range(1,N)]
floorplane={i:([1 if j==i else 0 for j in range(n)], fl[i]) for i in range(n)}
eff=([1]*n,g.v[N])
hits=[]; seen=set()
# k = number at floor; go k high->low (cheaper first)
for k in [5,4,3,2]:
    need=n-1-k
    if need<0: continue
    for Z in itertools.combinations(range(n),k):
        base=[floorplane[i] for i in Z]
        for combo in itertools.combinations(range(len(planes)),need):
            M=[b[0] for b in base]+[planes[c][0] for c in combo]+[eff[0]]
            b=[b[1] for b in base]+[planes[c][1] for c in combo]+[eff[1]]
            y=exact_solve([r[:] for r in M],b[:],n)
            if y is None: continue
            key=tuple(y)
            if key in seen: continue
            seen.add(key)
            if undom(y):
                hits.append((k,Z,combo,[str(x) for x in y]))
                print(f"ESCAPE k={k} Z={Z} y={[str(x) for x in y]}",flush=True)
                if len(hits)>=3: break
        if len(hits)>=3: break
    print(f"  finished k={k}, hits so far={len(hits)}, vertices seen={len(seen)}",flush=True)
    if len(hits)>=3: break
print("TOTAL undominated floor-vertex escapes:",len(hits))
if not hits:
    print("NO floor-vertex escape with 2<=k<=5 at floor. Escalating needed (k<=1 or non-floor vertices).")
