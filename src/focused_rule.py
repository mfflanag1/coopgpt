import random, sys
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from eshunt import is_ES, egalitarian_procedure
from pes import pes, _cea_lambda
from core_stability import is_dominated_by_core, in_core, is_imputation

def rand_game(rng,n,hi=3):
    v=[F(0)]*(1<<n)
    for S in range(1,1<<n):
        mem=[i for i in range(n) if S>>i&1]
        v[S]=F(0) if len(mem)==1 else max((v[S^(1<<i)] for i in mem),default=F(0))+F(rng.randint(0,hi))
    return Game(n,v)

def run(n,trials,seed):
    rng=random.Random(seed)
    games=0; any_work=0; below_exists_and_works=0; no_work=[]
    below_fail=0; below_total=0
    for t in range(trials):
        g=rand_game(rng,n)
        if not is_balanced_game(g): continue
        es,_=is_ES(g)
        if es: continue
        games+=1
        gamma,A,k,Nadm=egalitarian_procedure(g); p,D=pes(g)
        e=sum(gamma)-g.v[g.N]
        M=[g.v[g.N]-g.v[g.N^(1<<i)] for i in range(n)]
        strong=[i for i in range(n) if D>>i&1]
        nonstrong=[i for i in range(n) if not D>>i&1]
        lam=_cea_lambda([gamma[i] for i in nonstrong], g.v[g.N]-sum(gamma[i] for i in strong))
        aw=False; bew=False
        for j in range(n):
            capped=gamma[j]>lam
            if not capped or gamma[j]<e: continue
            y=list(gamma); y[j]=gamma[j]-e
            if not is_imputation(g,y) or in_core(g,y): continue
            dom,_=is_dominated_by_core(g,y)
            below = gamma[j]<M[j]
            if below:
                below_total+=1
                if dom: below_fail+=1
            if not dom:
                aw=True
                if below: bew=True
        if aw: any_work+=1
        if bew: below_exists_and_works+=1
        if not aw: no_work.append([str(x) for x in g.v])
    print(f'n={n} seed={seed}: nonES={games} ANY_strip_works={any_work} below_ceiling_works_exists={below_exists_and_works} NO_strip={len(no_work)} below_ceiling_strips(total={below_total},dominated={below_fail})',flush=True)
    for w in no_work[:3]: print('   NO-STRIP GAME:',w,flush=True)

for n in [int(x) for x in sys.argv[1].split(',')]:
    for seed in range(int(sys.argv[2])):
        run(n,int(sys.argv[3]),seed)
