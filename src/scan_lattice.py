"""Focused scan: fix three bumped coalitions to a BALANCED COLLECTION so that
bumping all three drives the pointwise-max (top) game unbalanced -- the necessary
condition for infeasibility. Then scan base games and test the lattice-minus-top
family for infeasibility. n=4.

Balanced collection used: A={0,1,2}=7, B={0,1,3}=11, C={2,3}=12; each player in
exactly 2 of them => weights 1/2, sum of indicators = 1_N. So if the (bumped)
values satisfy v(7)+v(11)+v(12) > 2 v(N) the top is unbalanced.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_sd import exactify, is_exact_game, in_class
from hunt_lattice import cube_family
from family_infeasible import is_family_feasible, certify_infeasible

N=15
def rand_base(rng, hi=12):
    # random superadditive-ish balanced integer game on n=4
    from hunt_monotonic import rand_game
    return rand_game(4, rng, "general", vmax=hi)

def run(cls, trials, seed, A=7,B=11,C=12, dmax=6, logpath=None):
    rng=random.Random(seed)
    log=open(logpath,"a") if logpath else None
    def out(s):
        print(s,flush=True)
        if log: log.write(s+"\n"); log.flush()
    out(f"=== scan_lattice cls={cls} A={A:b} B={B:b} C={C:b} trials={trials} seed={seed} ===")
    tested=0; topunb=0
    for t in range(trials):
        g=rand_base(rng)
        if not is_balanced_game(g): continue
        base= exactify(g) if cls=="exact" else g
        if base is None or not in_class(base, cls): continue
        for _ in range(30):
            dA,dB,dC=(rng.randint(1,dmax) for _ in range(3))
            games,edges,top=cube_family(base,A,B,C,dA,dB,dC)
            if is_balanced_game(top): continue
            topunb+=1
            if not all(in_class(gm,cls) for gm in games): continue
            tested+=1
            feas,x=is_family_feasible(games,edges)
            if feas: continue
            out(f"[INFEASIBLE] t={t} d=({dA},{dB},{dC}) cls={cls}")
            cert=certify_infeasible(games,edges)
            if not cert["infeasible"]:
                out("  recheck feasible, skip"); continue
            payload={"cls":cls,"n":4,"A":A,"B":B,"C":C,"d":[dA,dB,dC],
                     "base":[str(u) for u in base.v],
                     "games":[[str(u) for u in gm.v] for gm in games],"edges":edges,
                     "exact_members":[is_exact_game(gm) for gm in games],
                     "farkas": None if cert.get("farkas") is None else {
                       "rhs":str(cert["farkas"]["rhs"]),
                       "active_ineq":[(m,str(y)) for m,y in cert["farkas"]["active_ineq"]],
                       "active_eq":[(m,str(y)) for m,y in cert["farkas"]["active_eq"]]}}
            out("CERTIFIED INFEASIBLE:"); out(json.dumps(payload,indent=1))
            with open(f"../results/WITNESS_family_{cls}.json","w") as f: json.dump(payload,f,indent=1)
            return payload
    out(f"no infeasible: cls={cls} topunb-cases={topunb} tested(all-in-class)={tested}")
    return None

if __name__=="__main__":
    cls=sys.argv[1]; trials=int(sys.argv[2]); seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    logpath=sys.argv[4] if len(sys.argv)>4 else None
    run(cls,trials,seed,logpath=logpath)
