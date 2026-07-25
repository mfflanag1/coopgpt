"""Float-screened hunt for an infeasible ALL-EXACT family; every hit re-confirmed
with the exact-rational stack (exact exactify, exact is_exact_game, exact family LP,
verified Farkas certificate). Screens V / star / lattice-minus-top families built
from exact single-coalition-bump arms of an exact base.
"""
import random, sys, json
from itertools import combinations
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game
from floatscreen import is_balanced_float, is_exact_float, _core_min_xS_float, family_feasible_float
from family_infeasible import is_family_feasible, certify_infeasible

def vbump(v,bumps):
    v2=list(v)
    for S,d in bumps: v2[S]+=d
    return v2

def confirm_exact(int_v, arm_bumps, edges, family_bumps, out, tag):
    """int_v: original integer game. Recompute exact base, build exact family, confirm."""
    g=Game(4,[F(x) for x in int_v])
    if not is_balanced_game(g): return None
    base=exactify(g)
    if base is None or not is_exact_game(base):
        out(f"  [{tag}] base not exact under exact check, skip"); return None
    games=[base]
    for bumps in family_bumps:
        gg=Game(4, vbump(base.v, bumps))
        if not is_exact_game(gg):
            out(f"  [{tag}] a member not exact under exact check, skip"); return None
        games.append(gg)
    feas,_=is_family_feasible(games, edges)
    if feas:
        out(f"  [{tag}] EXACT LP says feasible (float false alarm), skip"); return None
    cert=certify_infeasible(games, edges)
    if not cert["infeasible"]:
        out(f"  [{tag}] exact recheck feasible, skip"); return None
    payload={"tag":tag,"games":[[str(u) for u in gm.v] for gm in games],"edges":edges,
             "exact_members":[is_exact_game(gm) for gm in games],
             "farkas": None if cert.get("farkas") is None else {
               "rhs":str(cert["farkas"]["rhs"]),
               "active_ineq":[(m,str(y)) for m,y in cert["farkas"]["active_ineq"]],
               "active_eq":[(m,str(y)) for m,y in cert["farkas"]["active_eq"]]}}
    out(f"*** CERTIFIED INFEASIBLE ALL-EXACT FAMILY [{tag}] ***")
    out(json.dumps(payload,indent=1))
    json.dump(payload, open("../results/WITNESS_family_exact.json","w"), indent=1)
    return payload

def run(trials, seed, dmax=3, logpath=None):
    rng=random.Random(seed)
    log=open(logpath,"a") if logpath else None
    def out(s):
        print(s,flush=True)
        if log: log.write(s+"\n"); log.flush()
    out(f"=== hunt_exact_float trials={trials} seed={seed} dmax={dmax} ===")
    bases=0; V=star=lat=0; Vhit=starhit=lathit=0
    for t in range(trials):
        if t and t%2000==0:
            out(f"  [prog t={t}] bases={bases} V={V}(hit{Vhit}) star={star}(hit{starhit}) lat={lat}(hit{lathit})")
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
                if is_exact_float(4, vbump(base,[(S,d)])): arms.append((S,d)); break
        if len(arms)<2: continue
        bases+=1
        for ai,aj in combinations(range(len(arms)),2):
            A,dA=arms[ai]; B,dB=arms[aj]
            gv=[base, vbump(base,[(A,dA)]), vbump(base,[(B,dB)])]
            edges=[(0,1,A),(0,2,B)]
            V+=1
            if not family_feasible_float(4, gv, edges):
                Vhit+=1
                confirm_exact(gi.v,[(A,dA),(B,dB)],edges,[[(A,dA)],[(B,dB)]],out,f"V A={A:b} B={B:b}")
        for ai,aj,ak in combinations(range(len(arms)),3):
            A,dA=arms[ai]; B,dB=arms[aj]; C,dC=arms[ak]
            gv=[base, vbump(base,[(A,dA)]), vbump(base,[(B,dB)]), vbump(base,[(C,dC)])]
            edges=[(0,1,A),(0,2,B),(0,3,C)]
            star+=1
            if not family_feasible_float(4, gv, edges):
                starhit+=1
                confirm_exact(gi.v,None,edges,[[(A,dA)],[(B,dB)],[(C,dC)]],out,f"STAR {A:b},{B:b},{C:b}")
            # lattice: exact doubles (float screen)
            dd={}; okd=True
            for (X,dx),(Y,dy) in combinations([(A,dA),(B,dB),(C,dC)],2):
                vv=vbump(base,[(X,dx),(Y,dy)])
                if not is_exact_float(4,vv): okd=False; break
                dd[(X,Y)]=vv
            if okd:
                gv2=[base, vbump(base,[(A,dA)]), vbump(base,[(B,dB)]), vbump(base,[(C,dC)]),
                     dd[(A,B)],dd[(A,C)],dd[(B,C)]]
                E=[(0,1,A),(0,2,B),(0,3,C),(1,4,B),(2,4,A),(1,5,C),(3,5,A),(2,6,C),(3,6,B)]
                lat+=1
                if not family_feasible_float(4,gv2,E):
                    lathit+=1
                    confirm_exact(gi.v,None,E,[[(A,dA)],[(B,dB)],[(C,dC)],
                        [(A,dA),(B,dB)],[(A,dA),(C,dC)],[(B,dB),(C,dC)]],out,f"LAT {A:b},{B:b},{C:b}")
    out(f"NO infeasible all-exact family. bases={bases} V={V}(hit{Vhit}) star={star}(hit{starhit}) lat={lat}(hit{lathit})")

if __name__=="__main__":
    trials=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1
    logpath=sys.argv[3] if len(sys.argv)>3 else None
    run(trials,seed,logpath=logpath)
