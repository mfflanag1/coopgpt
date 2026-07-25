"""Depth-2 search for an infeasible EXACT family: lattice-minus-top (multi-top, no
common core point). base b + single arms A,B,C + doubles AB,AC,BC (all EXACT),
top ABC EXCLUDED. If the top is unbalanced there is no common core point, so the
depth-1 pin obstruction is bypassed -- this is where a non-pin Farkas contradiction
could live. Float-screened; any infeasible hit confirmed exactly + Farkas.
Also tracks the fertile denominator: #families with all-7 exact AND top unbalanced.
"""
import random, sys, json
from itertools import combinations
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game
from floatscreen import is_balanced_float, is_exact_float, _core_min_xS_float, family_feasible_float
from family_infeasible import is_family_feasible, certify_infeasible

def vb(v,bumps):
    v2=list(v)
    for S,d in bumps: v2[S]+=d
    return v2

def confirm(gi_v, member_bumps, edges, out, tag):
    g=Game(4,[F(x) for x in gi_v])
    base=exactify(g)
    if base is None or not is_exact_game(base): return None
    games=[base]
    for bumps in member_bumps:
        gg=Game(4, vb(base.v, bumps))
        if not is_exact_game(gg):
            out(f"  [{tag}] member not exact (exact check), skip"); return None
    games=[base]+[Game(4,vb(base.v,bm)) for bm in member_bumps]
    if is_family_feasible(games, edges)[0]:
        out(f"  [{tag}] exact LP feasible (float false alarm), skip"); return None
    cert=certify_infeasible(games,edges)
    if not cert["infeasible"]:
        out(f"  [{tag}] exact recheck feasible, skip"); return None
    payload={"tag":tag,"games":[[str(u) for u in g.v] for g in games],"edges":edges,
             "exact_members":[is_exact_game(g) for g in games],
             "farkas": None if cert.get("farkas") is None else {
               "rhs":str(cert["farkas"]["rhs"]),
               "active_ineq":[(m,str(y)) for m,y in cert["farkas"]["active_ineq"]],
               "active_eq":[(m,str(y)) for m,y in cert["farkas"]["active_eq"]]}}
    out(f"*** CERTIFIED INFEASIBLE EXACT DEPTH-2 FAMILY [{tag}] ***")
    out(json.dumps(payload,indent=1))
    json.dump(payload, open("../results/WITNESS_family_exact_depth2.json","w"), indent=1)
    return payload

def run(trials, seed, dmax=3, logpath=None):
    rng=random.Random(seed)
    log=open(logpath,"a") if logpath else None
    def out(s):
        print(s,flush=True)
        if log: log.write(s+"\n"); log.flush()
    out(f"=== hunt_depth2 trials={trials} seed={seed} dmax={dmax} ===")
    bases=0; fertile=0; tested=0; topunb=0
    for t in range(trials):
        if t and t%3000==0:
            out(f"  [prog t={t}] bases={bases} topunb={topunb} fertile(all7exact&topunb)={fertile} tested={tested}")
        gi=rand_game(4,rng,"general"); vi=[float(x) for x in gi.v]
        if not is_balanced_float(4,vi): continue
        ve=[0.0]*16; ve[15]=vi[15]; ok=True
        for S in range(1,15):
            m=_core_min_xS_float(4,vi,S)
            if m is None: ok=False; break
            ve[S]=m
        if not ok: continue
        base=ve
        arms=[]
        for S in range(1,15):
            for d in range(1,dmax+1):
                if is_exact_float(4, vb(base,[(S,d)])): arms.append((S,d)); break
        if len(arms)<3: continue
        bases+=1
        for i,j,k in combinations(range(len(arms)),3):
            A,dA=arms[i]; B,dB=arms[j]; C,dC=arms[k]
            top=vb(base,[(A,dA),(B,dB),(C,dC)])
            if is_balanced_float(4,top):
                continue           # common core point exists -> feasible, skip
            topunb+=1
            # doubles must be exact
            dd={}; okd=True
            for (X,dx),(Y,dy) in combinations([(A,dA),(B,dB),(C,dC)],2):
                vv=vb(base,[(X,dx),(Y,dy)])
                if not is_exact_float(4,vv): okd=False; break
                dd[(X,Y)]=vv
            if not okd: continue
            fertile+=1
            G=[base, vb(base,[(A,dA)]), vb(base,[(B,dB)]), vb(base,[(C,dC)]),
               dd[(A,dA),(B,dB)], dd[(A,dA),(C,dC)], dd[(B,dB),(C,dC)]]
            E=[(0,1,A),(0,2,B),(0,3,C),(1,4,B),(2,4,A),(1,5,C),(3,5,A),(2,6,C),(3,6,B)]
            tested+=1
            if not family_feasible_float(4,G,E):
                confirm(gi.v, [[(A,dA)],[(B,dB)],[(C,dC)],
                              [(A,dA),(B,dB)],[(A,dA),(C,dC)],[(B,dB),(C,dC)]], E, out,
                        f"D2 A={A:b} B={B:b} C={C:b}")
    out(f"NO infeasible exact depth-2 family. bases={bases} topunb={topunb} "
        f"fertile(all7exact&topunb)={fertile} tested={tested}")

if __name__=="__main__":
    trials=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1
    logpath=sys.argv[3] if len(sys.argv)>3 else None
    run(trials,seed,logpath=logpath)
