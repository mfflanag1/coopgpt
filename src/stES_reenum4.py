"""COMPLETE arrangement re-enumeration for a 1-D (segment) core, exact-rigor at float
speed. Planes: coalition y(S)=v(S) + floor y_i=v({i}) + endpoint-coordinate y_i=A_i,B_i
+ PAIRWISE SEGMENT-SUPPORT (y_i-A_i)(B_j-A_j)=(y_j-A_j)(B_i-A_i). The last class captures
undominated-set vertices on anti-monotone projected core faces (the completeness gap of the
coalition+floor / coordinate arrangements). For a segment core [A,B] these classes contain
ALL vertices of the undominated set, so "no escape here" is a rigorous stability certificate.

Same conservative-margin screen (no false negatives): each outside-core vertex is float-
solved, then a blocking coalition that dominates with margin > 1e-4 AND passes an exact
rational domination witness lets us SKIP; true survivors get full exact certify_undominated.

Usage: python3 stES_reenum4.py <idx> <worker> <nworkers>
Requires /tmp/cvx_<idx>.json = list of core vertices (>=2) as decimal-string vectors.
"""
import sys, itertools, time, json
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from core_stability import certify_undominated
from largeness_exact import exact_solve

MARG=1e-4; CK=5000
CANDS={
 0:[0,0,0,0,0,2,2,2,1,1,1,1,3,3,3,3,1,2,2,2,1,3,4,4,3,3,3,3,4,5,5,5,0,2,3,4,0,2,3,5,3,5,5,5,3,5,6,7,1,3,4,6,1,3,4,6,4,6,7,7,4,6,7,9],
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}

def build_planes(g, idx):
    n,N=g.n,g.N
    planes=[]  # (exact_row(list F), exact_rhs F, tag)
    for S in range(1,N):
        planes.append(([F(1) if S>>i&1 else F(0) for i in range(n)], F(g.v[S]), ('S',S)))
    for i in range(n):
        r=[F(0)]*n; r[i]=F(1); planes.append((r, F(g.v[1<<i]), ('x',i)))
    verts=[[F(x) for x in v] for v in json.load(open(f"/tmp/cvx_{idx}.json"))]
    # endpoint-coordinate planes (dedup vs floors and each other)
    seen=set((i,g.v[1<<i]) for i in range(n))
    for v in verts:
        for i in range(n):
            if (i,v[i]) in seen: continue
            seen.add((i,v[i]))
            r=[F(0)]*n; r[i]=F(1); planes.append((r, v[i], ('v',i)))
    # pairwise segment-support planes, using the two extreme endpoints A,B (segment core)
    A,B=verts[0],verts[1]
    pseen=set()
    for i in range(n):
        for j in range(i+1,n):
            di=B[i]-A[i]; dj=B[j]-A[j]
            if di==0 and dj==0: continue
            # dj*y_i - di*y_j = dj*A_i - di*A_j
            r=[F(0)]*n; r[i]=dj; r[j]=-di; rhs=dj*A[i]-di*A[j]
            key=(i,j,str(dj),str(di),str(rhs))
            if key in pseen: continue
            pseen.add(key)
            planes.append((r, rhs, ('p',i,j)))
    return planes

def run(idx,worker,nworkers):
    V=CANDS[idx]; n=6; g=Game(n,[F(x) for x in V]); N=g.N
    vf=[float(x) for x in g.v]; lo=[vf[1<<i] for i in range(n)]
    planes=build_planes(g,idx)
    frows=[[float(a) for a in p[0]] for p in planes]
    frhs=[float(p[1]) for p in planes]
    m=len(planes); eff=[1.0]*n; effr=vf[N]
    print(f"[c{idx}w{worker}] COMPLETE arrangement m={m} planes "
          f"(S/x/v/p), pairs={sum(1 for p in planes if p[2][0]=='p')}",flush=True)
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
    ckpt=f"/tmp/ck4_{idx}_{worker}.txt"; start=0
    try:
        for ln in open(ckpt):
            ln=ln.strip()
            if ln.startswith("ORD "): start=int(ln.split()[1])
            if ln.startswith("ESCAPE") or ln.startswith("DONE"):
                print("(already "+ln.split()[0]+") "+ln,flush=True); return
    except FileNotFoundError: pass
    it=itertools.combinations(range(m),n-1); ordn=start
    if start>0: it=itertools.islice(it,start,None); print(f"[c{idx}w{worker}] RESUME @{start}",flush=True)
    tested=outside=survivors=0; t0=time.time()
    for combo in it:
        ordn+=1
        if combo[0]%nworkers!=worker:
            if ordn%CK==0: open(ckpt,"a").write(f"ORD {ordn}\n")
            continue
        Mx=np.array([frows[j] for j in combo]+[eff]); bb=np.array([frhs[j] for j in combo]+[effr])
        try:
            if abs(np.linalg.det(Mx))<1e-9:
                if ordn%CK==0: open(ckpt,"a").write(f"ORD {ordn}\n")
                continue
            yf=np.linalg.solve(Mx,bb)
        except np.linalg.LinAlgError: continue
        tested+=1
        ok=abs(sum(yf)-vf[N])<1e-6 and all(yf[i]>=lo[i]-1e-7 for i in range(n))
        blk=[S for S in range(1,N) if sum(yf[i] for i in range(n) if S>>i&1)<vf[S]-1e-7] if ok else []
        if ok and blk:
            outside+=1
            Me=[list(planes[j][0]) for j in combo]+[[F(1)]*n]
            be=[planes[j][1] for j in combo]+[g.v[N]]
            yx=exact_solve([r[:] for r in Me], be, n)
            if yx is not None:
                dominated=False
                for S in blk:
                    t,xstar=dom_margin(list(yf),S)
                    if t is not None and t>MARG and exact_dom_ok(yx,S,xstar):
                        dominated=True; break
                if not dominated:
                    survivors+=1
                    if certify_undominated(g,yx):
                        msg=f"EXACT ESCAPE c{idx}: {[str(a) for a in yx]} tags={[planes[j][2] for j in combo]}"
                        print(msg,flush=True); open(ckpt,"a").write(msg+"\n"); return
        if ordn%CK==0:
            open(ckpt,"a").write(f"ORD {ordn}\n")
            print(f"[c{idx}w{worker}] ord={ordn} tested={tested} outside={outside} surv={survivors} {time.time()-t0:.0f}s",flush=True)
    open(ckpt,"a").write(f"DONE c{idx} w{worker}/{nworkers} tested={tested} outside={outside} surv={survivors}\n")
    print(f"DONE c{idx} w{worker}: tested={tested} outside={outside} survivors={survivors} NO ESCAPE",flush=True)

if __name__=="__main__":
    run(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
