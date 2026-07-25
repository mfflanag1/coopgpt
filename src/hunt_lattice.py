"""Search for infeasible 'lattice-minus-top' families.

Pick a base game b (n players) and three coalitions A,B,C with bump amounts
dA,dB,dC. Build the Boolean cube of bumps: 7 games below the top (base; +A,+B,+C;
+AB,+AC,+BC) with single-bump edges. The TOP (+ABC) is deliberately EXCLUDED.
Necessary condition for infeasibility (v(N) fixed): the top M must be UNBALANCED
(else its core point serves every member -> feasible). We require every one of the
7 members to be in class `cls` (balanced/exact) and the top unbalanced, then test
the joint core+monotonicity LP for infeasibility.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game, in_class
from family_infeasible import is_family_feasible, certify_infeasible

def add_bumps(base, bumps):
    v = list(base.v)
    for S, d in bumps:
        v[S] += d
    return Game(base.n, v)

def cube_family(base, A, B, C, dA, dB, dC):
    """Return the 7 games (indices 0..6) and lattice edges, top excluded."""
    bA=(A,dA); bB=(B,dB); bC=(C,dC)
    G = {
        (): add_bumps(base, []),
        ('A',): add_bumps(base, [bA]),
        ('B',): add_bumps(base, [bB]),
        ('C',): add_bumps(base, [bC]),
        ('A','B'): add_bumps(base, [bA,bB]),
        ('A','C'): add_bumps(base, [bA,bC]),
        ('B','C'): add_bumps(base, [bB,bC]),
    }
    top = add_bumps(base, [bA,bB,bC])
    keys = [(), ('A',),('B',),('C',),('A','B'),('A','C'),('B','C')]
    idx = {k:i for i,k in enumerate(keys)}
    coal = {'A':A,'B':B,'C':C}
    games = [G[k] for k in keys]
    edges = []
    for k in keys:
        for X in ('A','B','C'):
            if X not in k:
                kl = tuple(sorted(k+(X,)))
                if kl in idx:  # target still below top
                    edges.append((idx[k], idx[kl], coal[X]))
    return games, edges, top

def hunt(cls, n, trials, seed, dmax=3, logpath=None):
    rng = random.Random(seed)
    log = open(logpath,"a") if logpath else None
    def out(s):
        print(s, flush=True)
        if log: log.write(s+"\n"); log.flush()
    out(f"=== lattice hunt cls={cls} n={n} trials={trials} seed={seed} ===")
    N = (1<<n)-1
    coals = list(range(1, N))
    checked=0; bases=0; topunb=0
    for t in range(trials):
        g = rand_game(n, rng, "general")
        if not is_balanced_game(g):
            continue
        base = exactify(g) if cls=="exact" else g
        if base is None: continue
        if not in_class(base, cls): continue
        bases += 1
        # random triples of coalitions + depths
        for _ in range(40):
            A,B,C = rng.sample(coals, 3)
            dA,dB,dC = (rng.randint(1,dmax) for _ in range(3))
            games, edges, top = cube_family(base, A,B,C,dA,dB,dC)
            # necessary condition: top unbalanced
            if is_balanced_game(top):
                continue
            topunb += 1
            # all 7 members in class
            if not all(in_class(gm, cls) for gm in games):
                continue
            checked += 1
            feas, x = is_family_feasible(games, edges)
            if feas:
                continue
            out(f"[INFEASIBLE] trial={t} A={A:b} B={B:b} C={C:b} d=({dA},{dB},{dC})")
            cert = certify_infeasible(games, edges)
            if not cert["infeasible"]:
                out(f"  RECHECK FEASIBLE (skip): {cert.get('reason')}")
                continue
            payload = {
                "cls":cls,"n":n,"base":[str(u) for u in base.v],
                "A":A,"B":B,"C":C,"d":[dA,dB,dC],
                "games":[[str(u) for u in gm.v] for gm in games],
                "edges":edges,
                "exact_members":[is_exact_game(gm) for gm in games],
                "top_balanced": is_balanced_game(top),
                "farkas": None if cert.get("farkas") is None else {
                    "rhs": str(cert["farkas"]["rhs"]),
                    "active_ineq":[(m,str(y)) for m,y in cert["farkas"]["active_ineq"]],
                    "active_eq":[(m,str(y)) for m,y in cert["farkas"]["active_eq"]],
                },
            }
            out("CERTIFIED INFEASIBLE FAMILY:")
            out(json.dumps(payload, indent=1))
            with open(f"../results/WITNESS_family_{cls}_n{n}.json","w") as f:
                json.dump(payload, f, indent=1)
            return payload
    out(f"no infeasible: cls={cls} n={n} bases={bases} top-unbal-cases={topunb} full-checked={checked}")
    return None

if __name__ == "__main__":
    cls=sys.argv[1]; n=int(sys.argv[2]); trials=int(sys.argv[3])
    seed=int(sys.argv[4]) if len(sys.argv)>4 else 1
    logpath=sys.argv[5] if len(sys.argv)>5 else None
    hunt(cls,n,trials,seed,logpath=logpath)
