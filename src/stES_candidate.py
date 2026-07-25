"""Deep exact investigation of an n=6 CANDIDATE stable non-ES game.
Try: (A) all exact single-strips; (B) exact vertices with up to 3 players at floor
+ tight coalitions (bounded, exact); (C) exact vertices from float seeds via
tight-plane snapping. Report any exact-certified undominated escape, else escalate."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import certify_undominated, in_core, is_imputation, is_dominated_by_core
from largeness_exact import exact_solve

V=[0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,2,2,2,2,1,3,1,3,3,3,3,3,1,3,1,3,3,4,3,4,4,6,4,6,5,6,6,7,4,6,4,6,6,7,6,8]
n=6
g=Game(n,[F(x) for x in V]); N=g.N
fixed,A,esN=egalitarian_procedure(n,list(g.v))
gh=[fixed[i] for i in range(n)]; delta=sum(gh)-g.v[N]
M=[g.v[N]-g.v[N^(1<<i)] for i in range(n)]
floors=[g.v[1<<i] for i in range(n)]
print("gh",[str(x) for x in gh],"delta",delta,"ES",esN)
print("M",[str(x) for x in M],"floors",[str(x) for x in floors])
Ahat=[members(S,n) for S in range(1,N) if g.xS(gh,S)==g.v[S]]
print("A-hat proper:",Ahat)
print("balanced:", __import__('tugame').is_balanced_game(g))

def undom(y):
    return is_imputation(g,y) and (not in_core(g,y)) and (not is_dominated_by_core(g,y)[0])

found=[]
# (A) single strips
for p in range(n):
    if gh[p]-floors[p] < delta: continue
    y=list(gh); y[p]=gh[p]-delta
    if undom(y): found.append(("single",p,[str(x) for x in y]))
print("single-strip escapes:", found)

# (B) exact floor-vertices: choose F players at floor (|F|=1..3), fill with tight coalition planes
planes=[([1 if S>>i&1 else 0 for i in range(n)], g.v[S]) for S in range(1,N)]
floorplane={i:([1 if j==i else 0 for j in range(n)], floors[i]) for i in range(n)}
eff=([1]*n,g.v[N])
def search_floor(maxF, cap=400000):
    seen=set(); cnt=0
    for kF in range(1,maxF+1):
        need=n-1-kF
        if need<0: continue
        for Fset in itertools.combinations(range(n),kF):
            base=[floorplane[i] for i in Fset]
            for combo in itertools.combinations(range(len(planes)),need):
                cnt+=1
                if cnt>cap: return None
                M2=[b[0] for b in base]+[planes[c][0] for c in combo]+[eff[0]]
                b2=[b[1] for b in base]+[planes[c][1] for c in combo]+[eff[1]]
                y=exact_solve([r[:] for r in M2],b2[:],n)
                if y is None: continue
                key=tuple(y)
                if key in seen: continue
                seen.add(key)
                if undom(y): return ("floor",Fset,combo,[str(x) for x in y])
    return None
r=search_floor(2, cap=2000000)
print("floor-vertex (|F|<=2) escape:", r)
if r is None:
    r3=search_floor(3, cap=3000000)
    print("floor-vertex (|F|<=3) escape:", r3)
