import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import in_core,is_imputation,is_dominated_by_core
from largeness_exact import exact_solve

V=[0,1,1,4,0,2,4,7,3,7,7,8,6,7,7,11,0,3,1,6,2,4,7,10,3,10,9,12,7,12,10,15]
n=5
g=Game(n,[F(x) for x in V]); N=g.N
fixed,A,esN=egalitarian_procedure(n,list(g.v))
gh=[fixed[i] for i in range(n)]; delta=sum(gh)-g.v[N]
M=[g.v[N]-g.v[N^(1<<i)] for i in range(n)]
print("gh",[str(x) for x in gh],"delta",delta,"ES",esN)
print("M ",[str(x) for x in M])
print("floors",[str(g.v[1<<i]) for i in range(n)])
Ahat=[members(S,n) for S in range(1,N) if g.xS(gh,S)==g.v[S]]
print("A-hat proper tight:",Ahat)
# enumerate ALL undominated escapes
planes=[]
for S in range(1,N): planes.append(([1 if S>>i&1 else 0 for i in range(n)],g.v[S]))
for i in range(n):
    row=[0]*n;row[i]=1;planes.append((row,g.v[1<<i]))
eff=([1]*n,g.v[N]);seen=set();escapes=[]
for combo in itertools.combinations(range(len(planes)),n-1):
    Mx=[planes[j][0] for j in combo]+[eff[0]];b=[planes[j][1] for j in combo]+[eff[1]]
    y=exact_solve([r[:] for r in Mx],b[:],n)
    if y is None: continue
    k=tuple(y)
    if k in seen: continue
    seen.add(k)
    if not is_imputation(g,y) or in_core(g,y): continue
    dom,_=is_dominated_by_core(g,y)
    if not dom: escapes.append(y)
print(f"\n#undominated escapes = {len(escapes)}")
for y in escapes:
    diff=[y[i]-gh[i] for i in range(n)]
    strip=[i for i in range(n) if y[i]<gh[i]]; boost=[i for i in range(n) if y[i]>gh[i]]
    atfloor=[i for i in range(n) if y[i]==g.v[1<<i]]
    print(f"  y={[str(x) for x in y]} y-gh={[str(d) for d in diff]} strip={strip} boost={boost} atfloor={atfloor}")
