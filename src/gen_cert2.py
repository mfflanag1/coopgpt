"""paper2/supplement_data.json: exact certificates. Player i = index i.
Primary = canonical v(N)=4 witness (generator v=min(x1,x2)); plus two secondary
witnesses (hub, and the independently-found half-integer one). Exact rationals."""
import json
from fractions import Fraction as F
from tugame import Game, exact_lp_min, is_balanced_game
from hunt_sd import is_exact_game
from eshunt import egalitarian_procedure

def analyze(n, V, with_witnesses=True, generator=None):
    g = Game(n, [F(x) for x in V]); N = g.N
    lab = lambda S: "{" + ",".join(str(i+1) for i in range(n) if S>>i&1) + "}"
    xS = lambda x,S: sum(x[i] for i in range(n) if S>>i&1)
    # procedure + full trace
    coals=list(range(1,N+1)); P=0; gamma=[None]*n; rounds=[]
    while P!=N:
        chi={}
        for S in coals:
            fx=[i for i in range(n) if (S>>i&1) and (P>>i&1)]; fr=[i for i in range(n) if (S>>i&1) and not(P>>i&1)]
            if fr:
                sh=(g.v[S]-sum(gamma[i] for i in fx))/len(fr)
                chi[S]={i:(gamma[i] if (P>>i&1) else sh) for i in range(n) if S>>i&1}
            else: chi[S]={i:gamma[i] for i in fx}
        best={i:max(chi[S][i] for S in coals if i in chi[S]) for i in range(n)}
        A=[S for S in coals if sum(chi[S].values())==g.v[S] and all(chi[S][i]==best[i] for i in chi[S])]
        newP=0
        for S in A:
            newP|=S
            for i in chi[S]: gamma[i]=chi[S][i]
        P|=newP; rounds.append((A,{lab(S):{str(i+1):str(chi[S][i]) for i in chi[S]} for S in coals}))
    Ahat=A
    maximal=lambda C:[S for S in C if not any(S!=T and (S&T)==S for T in C)]
    M=maximal(Ahat); D=M[0]
    for S in M[1:]: D&=S
    strong=[i for i in range(n) if D>>i&1]; others=[i for i in range(n) if not D>>i&1]
    # PES: strong get their claim; the rest get min(claim_i, lambda) with lambda
    # chosen so the total equals v(N). Solve by water-filling (some claims may cap).
    budget=g.v[N]-sum(gamma[i] for i in strong)
    cs=sorted(gamma[i] for i in others); lam=cs[-1] if cs else F(0); cum=F(0)
    for idx in range(len(cs)):
        cand=(budget-cum)/(len(cs)-idx)
        if cand<=cs[idx]:
            lam=cand; break
        cum+=cs[idx]
    pes=[gamma[i] if (D>>i&1) else min(gamma[i],lam) for i in range(n)]
    out={
      "n":n, "game_v":{lab(S):str(g.v[S]) for S in range(1,N+1)}, "v_of_N":str(g.v[N]),
      "is_exact":bool(is_exact_game(g)), "is_balanced":bool(is_balanced_game(g)),
      "is_superadditive":bool(g.is_superadditive()), "is_monotone":bool(g.is_monotone_game()),
      "is_convex":bool(g.is_convex()),
      "egalitarian_claims":{str(i+1):str(gamma[i]) for i in range(n)},
      "sum_claims":str(sum(gamma)), "n_iterations":len(rounds),
      "admissible_collection_Ahat":[lab(S) for S in Ahat],
      "egalitarian_stable":bool(N in Ahat),
      "maximal_admissible":[lab(S) for S in M], "strong_claimants_D":[str(i+1) for i in strong],
      "procedural_egalitarian_solution_PES":{str(i+1):str(pes[i]) for i in range(n)},
      "lambda":str(lam),
      "PES_core_violations":{lab(S):str(g.v[S]-xS(pes,S)) for S in range(1,N) if xS(pes,S)<g.v[S]},
    }
    if generator is not None:
        out["generator_points"]={f"x{j+1}":[str(v) for v in pt] for j,pt in enumerate(generator)}
        out["generator_note"]="v(S)=min_j x^j(S); all points have equal sum "+str(sum(generator[0]))+"=v(N), so each lies in the core and v is exact (Schmeidler 1972 lower-envelope characterization)."
    if with_witnesses:
        out["chi_round1"]=rounds[0][1]; out["chi_round2"]=rounds[1][1] if len(rounds)>1 else {}
        wit={}
        for S in range(1,N):
            A_ub=[[-1 if T>>i&1 else 0 for i in range(n)] for T in range(1,N)]; b_ub=[-g.v[T] for T in range(1,N)]
            opt,x=exact_lp_min([1 if S>>i&1 else 0 for i in range(n)],A_ub,b_ub,[[1]*n],[g.v[N]])
            assert x is not None and xS(x,N)==g.v[N] and all(xS(x,T)>=g.v[T] for T in range(1,N)) and xS(x,S)==g.v[S]
            assert opt==g.v[S]
            wit[lab(S)]=[str(xi) for xi in x]
        out["exactness_witnesses"]=wit
    return out

PRIMARY=[0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
MINVAR=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,0,1,1,1,0,1,1,1,2,3,3,3,2,3,3,4]
HUB=[0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]
MINE=[0,0,3,3,0,1,5,5,2,4,7,8,2,4,7,9,0,0,3,3,0,2,5,5,3,4,8,8,3,5,8,10]
x1=[0,0,1,1,2]; x2=[1,1,0,2,0]

cert={
 "_note":"Exact games that are NOT egalitarian stable (Dietzenbacher 2021 open "
         "question, answered negatively). Player i = index i. Values exact "
         "rationals as strings. exactness_witnesses[S] is a core allocation x with "
         "x(S)=v(S) (certifies min_core x(S)=v(S)). Egalitarian procedure and "
         "procedural egalitarian solution as in Dietzenbacher (2021).",
 "primary_witness_vN4":analyze(5,PRIMARY,with_witnesses=True,
        generator=[[F(a) for a in x1],[F(a) for a in x2]]),
 "minimized_variant_mass41":analyze(5,MINVAR,with_witnesses=False),
 "secondary_witness_hub":analyze(5,HUB,with_witnesses=False),
 "secondary_witness_halfinteger":analyze(5,MINE,with_witnesses=False),
}
cert["primary_witness_vN4"]["core_vertices"]=[["0","0","1","1","2"],["1","1","0","2","0"]]
cert["primary_witness_vN4"]["core_note"]="Core = conv of these two vertices (1-dimensional segment); v = pointwise min of the two."
json.dump(cert,open("../paper2/supplement_data.json","w"),indent=1)
t=cert["primary_witness_vN4"]
print("primary: exact",t["is_exact"],"ES",t["egalitarian_stable"],"claims",t["egalitarian_claims"],
      "sum",t["sum_claims"],"PES",t["procedural_egalitarian_solution_PES"])
print("witnesses:",len(t["exactness_witnesses"]),"| secondaries:",
      cert["secondary_witness_hub"]["sum_claims"],cert["secondary_witness_halfinteger"]["sum_claims"])
