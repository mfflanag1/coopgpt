"""Verify structural facts supporting the reduction and subclass proof:
 (1) For every admissible coalition S of gamma-hat, gamma-hat|S is in the core of
     the subgame (S, v|S)  [claim: aspiration + tightness => subgame core].
 (2) Does every non-ES game have a HUB (player in every proper admissible coalition)?
 (3) ES <=> exists core point y <= gamma-hat (reduction sanity check, exact).
"""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, exact_lp_min
from es_check_main import egalitarian_procedure
from stES_test_construction import rand_point_sum, game_from_points, rand_balanced_superadd

def core_point_below(g, ub):
    """exact: exists core x with x_i <= ub_i? feasibility LP."""
    n,N=g.n,g.N
    A_ub,b_ub=[],[]
    for S in range(1,N):
        A_ub.append([-1 if S>>i&1 else 0 for i in range(n)]); b_ub.append(-g.v[S])
    for i in range(n):
        row=[0]*n; row[i]=1; A_ub.append(row); b_ub.append(ub[i])
    A_eq=[[1]*n]; b_eq=[g.v[N]]
    opt,x=exact_lp_min([0]*n,A_ub,b_ub,A_eq,b_eq)
    return opt is not None and opt!='unbounded'

def subgame_core_ok(g, gh, S):
    """gamma-hat|S in core(v|S)? need (gh|S)(T) >= v(T) for T subset S, and (gh|S)(S)=v(S)."""
    n=g.n
    if g.xS(gh,S)!=g.v[S]: return None  # not admissible
    mem=members(S,n)
    # check all subsets T of S
    sub=(S-1)&S
    while True:
        if sub!=0:
            if g.xS(gh,sub) < g.v[sub]: return False
        if sub==0: break
        sub=(sub-1)&S
    return True

def run(seed=1,n=5,ntrials=300):
    rng=random.Random(seed)
    st={"nonES":0,"has_hub":0,"subgame_core_all_ok":0,"reduction_ok":0,"reduction_bad":0}
    nohub=[]
    for t in range(ntrials):
        if rng.random()<0.6:
            k=rng.randint(2,4); c=rng.randint(n,20)
            g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        else:
            g=rand_balanced_superadd(n,rng)
        fixed,A,esN=egalitarian_procedure(n,list(g.v))
        gh=[fixed[i] for i in range(n)]
        if esN:
            continue
        st["nonES"]+=1
        N=g.N
        Ahat=[S for S in range(1,N) if g.xS(gh,S)==g.v[S]]  # proper admissible
        # (1) subgame-core property
        allok=all(subgame_core_ok(g,gh,S) for S in Ahat)
        if allok: st["subgame_core_all_ok"]+=1
        # (2) hub
        hub=[i for i in range(n) if all(S>>i&1 for S in Ahat)] if Ahat else []
        if hub: st["has_hub"]+=1
        else: nohub.append({"v":[str(x) for x in g.v],"gh":[str(x) for x in gh],
                            "Ahat":[members(S,n) for S in Ahat]})
        # (3) reduction: non-ES => NO core point <= gamma-hat
        below=core_point_below(g,gh)
        if not below: st["reduction_ok"]+=1
        else: st["reduction_bad"]+=1
        if st["nonES"]%40==0:
            print(f"  ...nonES={st['nonES']} hub={st['has_hub']} subg={st['subgame_core_all_ok']} "
                  f"redOK={st['reduction_ok']} redBAD={st['reduction_bad']}",flush=True)
    return st,nohub

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    ntr=int(sys.argv[2]) if len(sys.argv)>2 else 300
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    st,nohub=run(seed,n,ntr)
    print(json.dumps(st,indent=1))
    print(f"non-ES games with NO hub: {len(nohub)}")
    for c in nohub[:10]: print(json.dumps(c))
