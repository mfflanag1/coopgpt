"""Faster/instrumented hunt for an infeasible ALL-EXACT family.
For an exact base, find every (S,d) with 1<=d<=dmax such that the single bump is
still exact (arms). Then test V/star/lattice families built from arms. Report
yields so a null result is meaningful (denominator = #all-exact families tested).
Coalitions for arms: ALL proper coalitions.
"""
import random, sys, json
from itertools import combinations
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game
from family_infeasible import is_family_feasible, certify_infeasible

def bumpg(g,S,d):
    v=list(g.v); v[S]+=d; return Game(4,v)

def save_and_report(tag, games, edges, out):
    cert=certify_infeasible(games,edges)
    if not cert["infeasible"]:
        out(f"  [{tag}] recheck feasible, skip"); return None
    payload={"tag":tag,"games":[[str(u) for u in g.v] for g in games],"edges":edges,
             "exact_members":[is_exact_game(g) for g in games],
             "farkas": None if cert.get("farkas") is None else {
               "rhs":str(cert["farkas"]["rhs"]),
               "active_ineq":[(m,str(y)) for m,y in cert["farkas"]["active_ineq"]],
               "active_eq":[(m,str(y)) for m,y in cert["farkas"]["active_eq"]]}}
    out(f"CERTIFIED INFEASIBLE ALL-EXACT FAMILY [{tag}]:")
    out(json.dumps(payload,indent=1))
    json.dump(payload, open("../results/WITNESS_family_exact.json","w"), indent=1)
    return payload

def run(trials, seed, dmax=2, logpath=None):
    rng=random.Random(seed)
    log=open(logpath,"a") if logpath else None
    def out(s):
        print(s,flush=True)
        if log: log.write(s+"\n"); log.flush()
    out(f"=== scan_exact2 trials={trials} seed={seed} dmax={dmax} ===")
    exact_bases=0; total_arms=0; V=star=lat=0
    multi_arm_bases=0
    for t in range(trials):
        if t and t%100==0:
            out(f"  [prog t={t}] exact_bases={exact_bases} multiarm={multi_arm_bases} "
                f"arms_total={total_arms} V={V} star={star} lat={lat}")
        g=rand_game(4,rng,"general")
        if not is_balanced_game(g): continue
        base=exactify(g)
        if base is None: continue
        exact_bases+=1  # exactify output provably exact (verified 326/326)
        arms=[]
        for S in range(1,15):
            for d in range(1,dmax+1):
                if is_exact_game(bumpg(base,S,d)):
                    arms.append((S,d,bumpg(base,S,d))); break
        total_arms+=len(arms)
        if len(arms)<2: continue
        multi_arm_bases+=1
        for i,j in combinations(range(len(arms)),2):
            A,dA,tA=arms[i]; B,dB,tB=arms[j]
            games=[base,tA,tB]; edges=[(0,1,A),(0,2,B)]
            V+=1
            if not is_family_feasible(games,edges)[0]:
                if save_and_report(f"V A={A:b} B={B:b}",games,edges,out): return True
        for i,j,k in combinations(range(len(arms)),3):
            A,dA,tA=arms[i]; B,dB,tB=arms[j]; C,dC,tC=arms[k]
            games=[base,tA,tB,tC]; edges=[(0,1,A),(0,2,B),(0,3,C)]
            star+=1
            if not is_family_feasible(games,edges)[0]:
                if save_and_report(f"STAR A={A:b} B={B:b} C={C:b}",games,edges,out): return True
            # lattice with exact doubles
            dd={}
            ok=True
            for (X,dx),(Y,dy) in combinations([(A,dA),(B,dB),(C,dC)],2):
                g2=bumpg(bumpg(base,X,dx),Y,dy)
                if not is_exact_game(g2): ok=False; break
                dd[(X,Y)]=g2
            if ok:
                G=[base,tA,tB,tC,dd[(A,B)],dd[(A,C)],dd[(B,C)]]
                E=[(0,1,A),(0,2,B),(0,3,C),(1,4,B),(2,4,A),(1,5,C),(3,5,A),(2,6,C),(3,6,B)]
                lat+=1
                if not is_family_feasible(G,E)[0]:
                    if save_and_report(f"LATTICE A={A:b} B={B:b} C={C:b}",G,E,out): return True
    out(f"NO infeasible all-exact family. exact_bases={exact_bases} multiarm_bases={multi_arm_bases} "
        f"arms_total={total_arms} V_tested={V} star_tested={star} lat_tested={lat}")
    return False

if __name__=="__main__":
    trials=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1
    logpath=sys.argv[3] if len(sys.argv)>3 else None
    run(trials,seed,logpath=logpath)
