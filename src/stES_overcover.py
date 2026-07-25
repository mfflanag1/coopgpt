"""Characterization check: non-ES <=> admissible coalitions A-hat fractionally
OVER-cover N (exists lambda>=0 on proper admissible S with sum_{S ni i} lambda_S >= 1
for all i, and > 1 for some i -- i.e. a balanced cover by admissible coalitions
that is NOT achievable as an efficient partition).

Cleaner equivalent tested: min sum_S lambda_S  s.t. sum_{S ni i, S in Ahat} lambda_S >= 1
for all i, lambda>=0  (a fractional COVER LP over admissible coalitions). Call opt L*.
If N is admissible (ES) then {N} covers with weight 1 => L* <= 1. Claim: non-ES <=> L* > 1
is NOT quite it; rather we test the over-cover directly and also whether proper admissible
coalitions alone can cover N (they always do, each player in one) and must over-cover.
"""
import sys, random, json
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, exact_lp_min
from es_check_main import egalitarian_procedure
from stES_test_construction import rand_point_sum, game_from_points, rand_balanced_superadd

def proper_admissible(g, gh):
    N=g.N
    return [S for S in range(1,N) if g.xS(gh,S)==g.v[S]]

def min_cover(coalitions, n):
    """min sum lambda_S s.t. sum_{S ni i} lambda_S >= 1 all i, lambda>=0."""
    m=len(coalitions)
    if m==0: return None
    c=[1]*m
    A_ub=[]; b_ub=[]
    for i in range(n):
        A_ub.append([-1 if S>>i&1 else 0 for S in coalitions]); b_ub.append(-1)
    # lambda>=0
    for j in range(m):
        row=[0]*m; row[j]=-1; A_ub.append(row); b_ub.append(0)
    opt,x=exact_lp_min(c,A_ub,b_ub)
    return opt,x

def run(seed=1,n=5,ntrials=200):
    rng=random.Random(seed)
    st={"nonES":0,"L_gt_1":0,"L_eq_1":0,"L_lt_1":0}
    bad=[]
    for t in range(ntrials):
        if rng.random()<0.6:
            k=rng.randint(2,4); c=rng.randint(n,20)
            g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        else:
            g=rand_balanced_superadd(n,rng)
        fixed,A,esN=egalitarian_procedure(n,list(g.v))
        gh=[fixed[i] for i in range(n)]
        if esN: continue
        st["nonES"]+=1
        Ahat=proper_admissible(g,gh)
        opt,lam=min_cover(Ahat,n)
        if opt is None:
            bad.append({"v":[str(x) for x in g.v],"reason":"admissible cannot cover N"})
            continue
        if opt>1: st["L_gt_1"]+=1
        elif opt==1: st["L_eq_1"]+=1
        else:
            st["L_lt_1"]+=1
            bad.append({"v":[str(x) for x in g.v],"gh":[str(x) for x in gh],"L":str(opt)})
        if st["nonES"]%40==0:
            print(f"  ...nonES={st['nonES']} L>1={st['L_gt_1']} L=1={st['L_eq_1']} L<1={st['L_lt_1']}",flush=True)
    return st,bad

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    ntr=int(sys.argv[2]) if len(sys.argv)>2 else 200
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    st,bad=run(seed,n,ntr)
    print(json.dumps(st,indent=1))
    print(f"anomalies (L<1 or cannot cover): {len(bad)}")
    for b in bad[:8]: print(json.dumps(b))
