"""RIGOROUS escape search for one n=6 game. Float SOLVE for vertex generation
(fast) but the escape verdict is EXACT: every vertex that floats as an imputation
OUTSIDE the core is exact-certified with certify_undominated (exact imputation +
exact outside-core + exact undomination via all coalitions). No float domination
screen => no false negatives. If none certified across ALL C(68,5) vertices, the
core has no arrangement-vertex undominated escape; since every undominated point of
a polyhedral arrangement is a vertex, that means the core is (exactly) STABLE.

Usage: python3 stES_reliable_enum.py <cand_index>
"""
import sys, itertools
import numpy as np
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from core_stability import certify_undominated
from largeness_exact import exact_solve

CANDS=[
 [0,0,0,0,0,2,2,2,1,1,1,1,3,3,3,3,1,2,2,2,1,3,4,4,3,3,3,3,4,5,5,5,0,2,3,4,0,2,3,5,3,5,5,5,3,5,6,7,1,3,4,6,1,3,4,6,4,6,7,7,4,6,7,9],
 [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
]

def run(idx, worker=0, nworkers=1):
    V=CANDS[idx]; n=6; g=Game(n,[F(x) for x in V]); N=g.N
    vf=[float(x) for x in g.v]; lo=[vf[1<<i] for i in range(n)]
    rows=[]; rhs=[]; kind=[]
    for S in range(1,N):
        rows.append([1.0 if S>>i&1 else 0.0 for i in range(n)]); rhs.append(vf[S]); kind.append(('S',S))
    for i in range(n):
        r=[0.0]*n; r[i]=1.0; rows.append(r); rhs.append(lo[i]); kind.append(('x',i))
    m=len(rows); eff=[1.0]*n; effr=vf[N]
    def imp_outside_core(y):
        if abs(sum(y)-vf[N])>1e-6: return False
        if any(y[i]<lo[i]-1e-7 for i in range(n)): return False
        # outside core: some coalition strictly violated
        for S in range(1,N):
            if sum(y[i] for i in range(n) if S>>i&1) < vf[S]-1e-7:
                return True
        return False
    ckpt=f"/tmp/ck_rl_{idx}_{worker}.txt"
    start=0
    try:
        with open(ckpt) as f:
            for ln in f:
                ln=ln.strip()
                if ln.startswith("ORD "): start=int(ln.split()[1])
                if ln.startswith("ESCAPE"): print("  (already found) "+ln,flush=True); return None
                if ln.startswith("DONE"): print("  (already done) "+ln,flush=True); return None
    except FileNotFoundError:
        pass
    tested=0; checked=0; ordn=0
    it=itertools.combinations(range(m),n-1)
    if start>0:
        it=itertools.islice(it,start,None); ordn=start
        print(f"  [rc{idx}w{worker}] RESUME from ordinal {start}",flush=True)
    for combo in it:
        ordn+=1
        if combo[0] % nworkers != worker: continue
        Mx=np.array([rows[j] for j in combo]+[eff]); bb=np.array([rhs[j] for j in combo]+[effr])
        try:
            if abs(np.linalg.det(Mx))<1e-9: continue
            y=np.linalg.solve(Mx,bb)
        except np.linalg.LinAlgError:
            continue
        tested+=1
        if imp_outside_core(list(y)):
            checked+=1
            Me=[rows[j][:] for j in combo]+[[1]*n]
            be=[F(g.v[kind[j][1]]) if kind[j][0]=='S' else F(g.v[1<<kind[j][1]]) for j in combo]+[g.v[N]]
            ye=exact_solve([[F(a) for a in r] for r in Me], be, n)
            if ye is not None and certify_undominated(g,ye):
                msg=f"  EXACT ESCAPE cand{idx}: {[str(a) for a in ye]} basis={[kind[j] for j in combo]}"
                print(msg,flush=True)
                with open(ckpt,"a") as f: f.write("ESCAPE "+msg+"\n")
                return ye
        if ordn%50000==0:
            with open(ckpt,"a") as f: f.write(f"ORD {ordn}\n")
            print(f"  [rc{idx}w{worker}] ord={ordn} tested={tested} checked={checked}",flush=True)
    with open(ckpt,"a") as f: f.write(f"DONE cand{idx} w{worker}/{nworkers} tested={tested} checked={checked}\n")
    print(f"  DONE cand{idx} worker{worker}/{nworkers}: tested={tested} exact_checked={checked}, no escape in shard",flush=True)
    return None

if __name__=="__main__":
    idx=int(sys.argv[1])
    worker=int(sys.argv[2]) if len(sys.argv)>2 else 0
    nworkers=int(sys.argv[3]) if len(sys.argv)>3 else 1
    print(f"=== RELIABLE ENUM cand {idx} worker {worker}/{nworkers} ===",flush=True)
    run(idx,worker,nworkers)
