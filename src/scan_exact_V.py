"""Scan for INFEASIBLE families whose every member is EXACT.
Shapes: V (base + 2 overlapping-triple bumps), 3-arm star, and lattice-minus-top,
using overlapping coalitions A=7={0,1,2}, B=14={1,2,3}, C=13={0,2,3}, D=11={0,1,3}
(the four triples of n=4; pairwise overlaps of size 2).
A member is accepted only if is_exact_game is True (exact arithmetic).
Any infeasible all-exact family => THEOREM: no coalitionally monotonic core
selection on exact games. Certified with a verified Farkas certificate.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game
from family_infeasible import is_family_feasible, certify_infeasible

TRIPLES=[7,11,13,14]

def bumpg(g,S,d):
    v=list(g.v); v[S]+=d; return Game(4,v)

def report(tag, games, edges, cls_note, out):
    cert=certify_infeasible(games,edges)
    if not cert["infeasible"]:
        out(f"  [{tag}] recheck FEASIBLE, skip"); return None
    payload={"tag":tag,"note":cls_note,
             "games":[[str(u) for u in g.v] for g in games],"edges":edges,
             "exact_members":[is_exact_game(g) for g in games],
             "balanced":[is_balanced_game(g) for g in games],
             "farkas": None if cert.get("farkas") is None else {
               "rhs":str(cert["farkas"]["rhs"]),
               "active_ineq":[(m,str(y)) for m,y in cert["farkas"]["active_ineq"]],
               "active_eq":[(m,str(y)) for m,y in cert["farkas"]["active_eq"]]}}
    out(f"CERTIFIED INFEASIBLE ALL-EXACT FAMILY [{tag}]:")
    out(json.dumps(payload,indent=1))
    with open("../results/WITNESS_family_exact.json","w") as f: json.dump(payload,f,indent=1)
    return payload

def run(trials, seed, dmax=4, logpath=None):
    rng=random.Random(seed)
    log=open(logpath,"a") if logpath else None
    def out(s):
        print(s,flush=True)
        if log: log.write(s+"\n"); log.flush()
    out(f"=== scan_exact_V trials={trials} seed={seed} dmax={dmax} ===")
    V_tested=star_tested=lat_tested=0
    nearmiss=0
    for t in range(trials):
        g=rand_game(4,rng,"general")
        if not is_balanced_game(g): continue
        base=exactify(g)
        if base is None or not is_exact_game(base): continue
        # exact single bumps on each triple (choose smallest d keeping exact, else skip)
        arms={}
        for S in TRIPLES:
            for d in range(1,dmax+1):
                tg=bumpg(base,S,d)
                if is_exact_game(tg):
                    arms[S]=(d,tg); break
        keys=list(arms)
        if len(keys)<2: continue
        # V families over all pairs of exact-bump arms
        from itertools import combinations
        for A,B in combinations(keys,2):
            dA,tA=arms[A]; dB,tB=arms[B]
            games=[base,tA,tB]; edges=[(0,1,A),(0,2,B)]
            V_tested+=1
            feas,_=is_family_feasible(games,edges)
            if not feas:
                if report(f"V A={A:b} B={B:b} d=({dA},{dB})",games,edges,"all-exact V",out):
                    return True
        # 3-arm star + lattice if >=3 arms
        if len(keys)>=3:
            for A,B,C in combinations(keys,3):
                dA,tA=arms[A]; dB,tB=arms[B]; dC,tC=arms[C]
                games=[base,tA,tB,tC]; edges=[(0,1,A),(0,2,B),(0,3,C)]
                star_tested+=1
                feas,_=is_family_feasible(games,edges)
                if not feas:
                    if report(f"STAR A={A:b} B={B:b} C={C:b}",games,edges,"all-exact star",out):
                        return True
                # lattice: need exact doubles
                dbl={}
                ok=True
                for (X,dx),(Y,dy) in combinations([(A,dA),(B,dB),(C,dC)],2):
                    g2=bumpg(bumpg(base,X,dx),Y,dy)
                    if not is_exact_game(g2): ok=False; break
                    dbl[(X,Y)]=g2
                if ok:
                    dAB=dbl[(A,B)]; dAC=dbl[(A,C)]; dBC=dbl[(B,C)]
                    G=[base,tA,tB,tC,dAB,dAC,dBC]
                    E=[(0,1,A),(0,2,B),(0,3,C),(1,4,B),(2,4,A),(1,5,C),(3,5,A),(2,6,C),(3,6,B)]
                    lat_tested+=1
                    feas,_=is_family_feasible(G,E)
                    if not feas:
                        if report(f"LATTICE A={A:b} B={B:b} C={C:b}",G,E,"all-exact lattice",out):
                            return True
    out(f"NO infeasible all-exact family: V_tested={V_tested} star_tested={star_tested} lat_tested={lat_tested}")
    return False

if __name__=="__main__":
    trials=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1
    logpath=sys.argv[3] if len(sys.argv)>3 else None
    run(trials,seed,logpath=logpath)
