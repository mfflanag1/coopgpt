"""Redesigned exact-rigor arrangement re-enumeration (float speed, no false negatives).

Per basis vertex y (coalition+floor planes + efficiency):
  - float solve; skip unless float imputation OUTSIDE core (cheap).
  - exact-solve the vertex -> y_exact (one 6x6 rational solve).
  - CONSERVATIVE-MARGIN DOMINATION SCREEN: for each blocking coalition S, float-LP a core
    element x* tight on S maximizing min_i(x*_i - y_i). If margin > MARG, rationalize x* and
    EXACT-verify (x* in core, x*(S)=v(S), x*_i > y_exact_i for all i in S). If verified, the
    vertex is exactly dominated -> SKIP (rigorous: backed by an exact witness).
  - If NO coalition yields a verified exact dominator, the vertex is a SURVIVOR -> full exact
    certify_undominated (rare, expensive). If it certifies undominated => EXACT ESCAPE.
Guarantee: a vertex is skipped only with an exact dominating witness; every non-clearly-
dominated vertex is exact-certified. So the pass has NO false negatives at ~float speed.

Checkpoints every CK ordinals (append-only) for cheap resume; niced by launcher.
Usage: python3 stES_reenum2.py <idx> <worker> <nworkers>
"""
import sys, itertools, time
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from core_stability import certify_undominated
from largeness_exact import exact_solve

MARG=1e-4; CK=5000
CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}

def run(idx,worker,nworkers):
    V=CANDS[idx]; n=6; g=Game(n,[F(x) for x in V]); N=g.N
    vf=[float(x) for x in g.v]; lo=[vf[1<<i] for i in range(n)]
    rows=[]; rhs=[]; kind=[]
    for S in range(1,N):
        rows.append([1.0 if S>>i&1 else 0.0 for i in range(n)]); rhs.append(vf[S]); kind.append(('S',S))
    for i in range(n):
        r=[0.0]*n; r[i]=1.0; rows.append(r); rhs.append(lo[i]); kind.append(('x',i))
    m=len(rows); eff=[1.0]*n; effr=vf[N]
    core_A=[[-1.0 if T>>i&1 else 0.0 for i in range(n)] for T in range(1,N)]
    core_b=[-vf[T] for T in range(1,N)]
    def dom_margin(yf,S):
        A=[r+[0.0] for r in core_A]; b=list(core_b)
        A.append([1.0 if S>>i&1 else 0.0 for i in range(n)]+[0.0]); b.append(vf[S])
        for i in range(n):
            if S>>i&1:
                rr=[0.0]*(n+1); rr[i]=-1.0; rr[n]=1.0; A.append(rr); b.append(-yf[i])
        r=linprog([0.0]*n+[-1.0],A_ub=A,b_ub=b,A_eq=[[1.0]*n+[0.0]],b_eq=[vf[N]],
                  bounds=[(None,None)]*(n+1),method="highs")
        if not r.success: return None,None
        return -r.fun, r.x[:n]
    def exact_dom_ok(yx,S,xf):
        for D in (1,2,3,4,6,12,24,60,120,360):
            xr=[F(a).limit_denominator(D) for a in xf]
            if sum(xr)!=g.v[N]: continue
            if any(sum(xr[i] for i in range(n) if T>>i&1)<g.v[T] for T in range(1,N)): continue
            if sum(xr[i] for i in range(n) if S>>i&1)!=g.v[S]: continue
            if all(xr[i]>yx[i] for i in range(n) if S>>i&1): return True
        return False
    ckpt=f"/tmp/ck2_{idx}_{worker}.txt"; start=0
    try:
        for ln in open(ckpt):
            ln=ln.strip()
            if ln.startswith("ORD "): start=int(ln.split()[1])
            if ln.startswith("ESCAPE") or ln.startswith("DONE"):
                print("(already "+ln.split()[0]+") "+ln,flush=True); return
    except FileNotFoundError: pass
    it=itertools.combinations(range(m),n-1)
    ordn=start
    if start>0: it=itertools.islice(it,start,None); print(f"[c{idx}w{worker}] RESUME @{start}",flush=True)
    tested=0; outside=0; survivors=0; t0=time.time()
    for combo in it:
        ordn+=1
        if combo[0]%nworkers!=worker:
            if ordn%CK==0:
                open(ckpt,"a").write(f"ORD {ordn}\n")
            continue
        Mx=np.array([rows[j] for j in combo]+[eff]); bb=np.array([rhs[j] for j in combo]+[effr])
        try:
            if abs(np.linalg.det(Mx))<1e-9:
                if ordn%CK==0: open(ckpt,"a").write(f"ORD {ordn}\n")
                continue
            yf=np.linalg.solve(Mx,bb)
        except np.linalg.LinAlgError:
            continue
        tested+=1
        # float imputation-outside-core?
        ok=abs(sum(yf)-vf[N])<1e-6 and all(yf[i]>=lo[i]-1e-7 for i in range(n))
        blk=[S for S in range(1,N) if sum(yf[i] for i in range(n) if S>>i&1)<vf[S]-1e-7] if ok else []
        if ok and blk:
            outside+=1
            # exact vertex
            Me=[rows[j][:] for j in combo]+[[1]*n]
            be=[F(g.v[kind[j][1]]) if kind[j][0]=='S' else F(g.v[1<<kind[j][1]]) for j in combo]+[g.v[N]]
            yx=exact_solve([[F(a) for a in r] for r in Me], be, n)
            dominated=False
            if yx is not None:
                for S in blk:
                    t,xstar=dom_margin(list(yf),S)
                    if t is not None and t>MARG and exact_dom_ok(yx,S,xstar):
                        dominated=True; break
                if not dominated:
                    survivors+=1
                    if certify_undominated(g,yx):
                        msg=f"EXACT ESCAPE c{idx}: {[str(a) for a in yx]} basis={[kind[j] for j in combo]}"
                        print(msg,flush=True); open(ckpt,"a").write(msg+"\n"); return
        if ordn%CK==0:
            dt=time.time()-t0
            open(ckpt,"a").write(f"ORD {ordn}\n")
            print(f"[c{idx}w{worker}] ord={ordn} tested={tested} outside={outside} surv={survivors} {dt:.0f}s",flush=True)
    open(ckpt,"a").write(f"DONE c{idx} w{worker}/{nworkers} tested={tested} outside={outside} surv={survivors}\n")
    print(f"DONE c{idx} w{worker}: tested={tested} outside={outside} survivors={survivors} NO ESCAPE",flush=True)

if __name__=="__main__":
    run(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
