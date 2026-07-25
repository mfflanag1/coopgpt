"""Find non-ES games where the single-strip escape FAILS, and dump full structure
of the escape that DOES work, to read off the correct selection rule."""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0, '/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, is_balanced_game
from es_check_main import egalitarian_procedure
from core_stability import in_core, is_imputation, is_dominated_by_core, certify_undominated
from largeness_exact import exact_solve
from stES_test_construction import (rand_point_sum, game_from_points,
    rand_balanced_superadd, single_strips, undominated)

def full_structure(g, want=4, seed=1, n=5, maxtrials=4000):
    rng = random.Random(seed); found=0
    for t in range(maxtrials):
        if found>=want: break
        if rng.random()<0.6:
            k=rng.randint(2,4); c=rng.randint(n,20)
            g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        else:
            g=rand_balanced_superadd(n,rng)
        fixed,A,esN = egalitarian_procedure(n,list(g.v))
        if esN: continue
        gh=[fixed[i] for i in range(n)]; delta=sum(gh)-g.v[g.N]
        # single strip works?
        ss=[(p,y) for p,y in single_strips(g,gh,delta) if undominated(g,y)]
        if ss: continue
        # single strip failed -> enumerate ALL escapes
        escapes=enum_all(g)
        found+=1
        Ahat=[members(S,g.n) for S in range(1,g.N+1) if g.xS(gh,S)==g.v[S]]
        proper=[S for S in range(1,g.N) if g.xS(gh,S)==g.v[S]]
        hubs=[i for i in range(g.n) if all(S>>i&1 for S in proper)] if proper else []
        M=[g.v[g.N]-g.v[g.N^(1<<i)] for i in range(g.n)]
        floors=[g.v[1<<i] for i in range(g.n)]
        print(f"\n##### FAIL CASE {found} (seed={seed} t={t}) #####")
        print(f" v = {[str(x) for x in g.v]}")
        print(f" claims gh = {[str(x) for x in gh]} delta={delta}")
        print(f" floors v(i) = {[str(x) for x in floors]}  marginals M_i = {[str(x) for x in M]}")
        print(f" A-hat = {Ahat}   hub(s)={hubs}")
        print(f" feasible single strips (p): {[p for p,_ in single_strips(g,gh,delta)]}")
        print(f" #undominated escapes total = {len(escapes)}")
        for y in escapes[:6]:
            strip=[i for i in range(g.n) if y[i]<gh[i]]
            boost=[i for i in range(g.n) if y[i]>gh[i]]
            atfloor=[i for i in range(g.n) if y[i]==floors[i]]
            print(f"   y={[str(x) for x in y]} strip={strip} boost={boost} atfloor={atfloor}")
    if found==0:
        print("no single-strip-failure case found in budget")

def enum_all(g):
    n,N=g.n,g.N; planes=[]
    for S in range(1,N): planes.append(([1 if S>>i&1 else 0 for i in range(n)],g.v[S]))
    for i in range(n):
        row=[0]*n; row[i]=1; planes.append((row,g.v[1<<i]))
    eff=([1]*n,g.v[N]); seen=set(); out=[]
    for combo in itertools.combinations(range(len(planes)),n-1):
        M=[planes[j][0] for j in combo]+[eff[0]]; b=[planes[j][1] for j in combo]+[eff[1]]
        y=exact_solve([r[:] for r in M],b[:],n)
        if y is None: continue
        key=tuple(y)
        if key in seen: continue
        seen.add(key)
        if undominated(g,y): out.append(y)
    return out

if __name__=="__main__":
    seed=int(sys.argv[1]) if len(sys.argv)>1 else 1
    full_structure(None, want=5, seed=seed)
