"""SELECTOR MINING for (SINGLE/STRAT-CERT). For each star-fail, for each k in S record
   c_k = sigma - r_k (cover depth), r_k, stratum(k), gap g_k=phi_k-m_k, k in T*?, and
   whether {k} certifies (M^({k}) <= phi(S)).
Test selectors that would collapse the proof to a per-k statement:
  (A) EVERY max-c_k member of S certifies?
  (B) SOME max-c_k member certifies?  (= min-residual finding)
  (C) does cert-membership correlate monotonically with c_k?
Also: single-stratum subset-of-S cert of size<=2 exists (STRAT-CERT universal form).
Float LPs. Prints P(cert | max-c_k) vs P(cert | not), and exception samples.
"""
import random, sys, time, json
from fractions import Fraction as F
from scipy.optimize import linprog
from leximin import leximin_core_float
from hunt_exact_points import rand_point_sum, game_from_points
def members(S,n): return [i for i in range(n) if S>>i&1]
def core_ub(n,N,vF): return ([[-1.0 if U>>i&1 else 0.0 for i in range(n)] for U in range(1,N)],[-vF[U] for U in range(1,N)])
def MC(n,N,vF,A,b,S,C):
    r=linprog([-1.0 if S>>i&1 else 0.0 for i in range(n)],A_ub=A,b_ub=b,A_eq=[[1.0]*n,[1.0 if C>>i&1 else 0.0 for i in range(n)]],b_eq=[vF[N],vF[C]],bounds=[(None,None)]*n,method='highs')
    return None if not r.success else -r.fun
def cmaxS(n,N,vF,A,b,S):
    r=linprog([-1.0 if S>>i&1 else 0.0 for i in range(n)],A_ub=A,b_ub=b,A_eq=[[1.0]*n],b_eq=[vF[N]],bounds=[(None,None)]*n,method='highs'); return None if not r.success else -r.fun
def starmax(n,N,vF,A0,b0,phi,S):
    A=[r[:] for r in A0]; b=b0[:]
    for i in range(n):
        if S>>i&1: row=[0.0]*n; row[i]=-1.0; A.append(row); b.append(-phi[i])
    r=linprog([-1.0 if S>>i&1 else 0.0 for i in range(n)],A_ub=A,b_ub=b,A_eq=[[1.0]*n],b_eq=[vF[N]],bounds=[(None,None)]*n,method='highs'); return None if not r.success else -r.fun
def rescover(n,N,vF,phi,S,tights,tol=1e-6):
    m=len(tights); Sm=members(S,n); ai=m; nv=m+1+len(Sm); ridx={k:m+1+t for t,k in enumerate(Sm)}
    Aeq=[]; beq=[]
    for i in range(n):
        row=[0.0]*nv
        for t,U in enumerate(tights):
            if U>>i&1: row[t]=-1.0
        row[ai]=1.0
        if S>>i&1: row[ridx[i]]=-1.0
        Aeq.append(row); beq.append(0.0)
    c=[0.0]*nv
    for k in Sm: c[ridx[k]]=1.0
    r=linprog(c,A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*m+[(None,None)]+[(1,None)]*len(Sm),method='highs')
    if not r.success: return None,None
    return {k:r.x[ridx[k]] for k in Sm}, r.x[ai]
def bias(n,c,rng):
    k=rng.randint(2,3); base=rand_point_sum(n,c,rng); pts=[base]
    for _ in range(k-1):
        p=list(base); idx=rng.sample(range(n),rng.randint(1,n)); s=sum(p[i] for i in idx); nv=rand_point_sum(len(idx),s,rng)
        for j,i in enumerate(idx): p[i]=nv[j]
        pts.append(p)
    return pts
n=int(sys.argv[1]); rng=random.Random(int(sys.argv[2])); target=int(sys.argv[3]); log=sys.argv[4]; N=(1<<n)-1; TOL=1e-6
def out(s):
    print(s,flush=True)
    with open(log,'a') as f: f.write(s+'\n')
SF=0
maxc_all=0; maxc_some=0; maxc_none=0    # among max-c_k members: all/some/none certify
cert_given_maxc=[0,0]; cert_given_notmaxc=[0,0]  # [cert,total]
strat_size2=0  # STRAT-CERT: single-stratum subset-of-S cert of size<=2 exists
uniquemax_cert=0; uniquemax_total=0
excs=[]
out(f"=== SELECTOR n={n} seed={sys.argv[2]} target={target} @ {time.strftime('%H:%M:%S')} ===")
while SF<target:
    vg=game_from_points(n,bias(n,rng.randint(n,6*n),rng)).v; vF=[float(x) for x in vg]
    phi=leximin_core_float(n,vg,tol=1e-9)
    if phi is None: continue
    A,b=core_ub(n,N,vF); tights=[C for C in range(1,N) if abs(sum(phi[i] for i in range(n) if C>>i&1)-vF[C])<TOL]
    gains=[phi[i]-vF[1<<i] for i in range(n)]; lv=sorted(set(round(g,6) for g in gains)); strat={i:lv.index(round(gains[i],6)) for i in range(n)}
    for S in range(1,N):
        if bin(S).count('1')<2: continue
        pS=sum(phi[i] for i in range(n) if S>>i&1); mx=cmaxS(n,N,vF,A,b,S)
        if mx is None or mx<=pS+TOL: continue
        sm=starmax(n,N,vF,A,b,phi,S)
        if sm is None or sm>pS+TOL: continue
        SF+=1
        rd,sigma=rescover(n,N,vF,phi,S,tights)
        if rd is None: continue
        Sm=members(S,n)
        cdep={k:sigma-rd[k] for k in Sm}
        cmax=max(cdep.values()); maxc=[k for k in Sm if abs(cdep[k]-cmax)<1e-6]
        cert={k:((MC(n,N,vF,A,b,S,1<<k) or 9e9)<=pS+TOL) for k in Sm}
        # selector A/B on max-c_k members
        nc=sum(cert[k] for k in maxc)
        if nc==len(maxc): maxc_all+=1
        elif nc>0: maxc_some+=1
        else: maxc_none+=1
        for k in Sm:
            if k in maxc: cert_given_maxc[1]+=1; cert_given_maxc[0]+=cert[k]
            else: cert_given_notmaxc[1]+=1; cert_given_notmaxc[0]+=cert[k]
        if len(maxc)==1:
            uniquemax_total+=1; uniquemax_cert+=cert[maxc[0]]
        # STRAT-CERT: single-stratum subset-of-S cert of size<=2
        found2=any(cert[k] for k in Sm)
        if not found2:
            for a in range(len(Sm)):
                for bb in range(a+1,len(Sm)):
                    k1,k2=Sm[a],Sm[bb]
                    if strat[k1]!=strat[k2]: continue
                    C=(1<<k1)|(1<<k2)
                    if (MC(n,N,vF,A,b,S,C) or 9e9)<=pS+TOL: found2=True; break
                if found2: break
        if found2: strat_size2+=1
        if nc==0 and len(excs)<15:
            excs.append(dict(v=[str(x) for x in vg],S=Sm,r={k:round(rd[k],3) for k in Sm},
                cdep={k:round(cdep[k],3) for k in Sm},cert_k=[k for k in Sm if cert[k]],maxc=maxc))
        if SF%250==0:
            def pc(x): return f"{100.0*x/max(1,SF):.1f}%"
            out(f"[prog] SF={SF} maxc:all={pc(maxc_all)} some={pc(maxc_some)} none={maxc_none} "
                f"| P(cert|maxc)={cert_given_maxc[0]}/{cert_given_maxc[1]} P(cert|not)={cert_given_notmaxc[0]}/{cert_given_notmaxc[1]} "
                f"| uniqmax cert={uniquemax_cert}/{uniquemax_total} | STRAT<=2={pc(strat_size2)}")
        if SF>=target: break
def pc(x): return f"{100.0*x/max(1,SF):.2f}%"
out(f"\nDONE n={n} SF={SF}")
out(f"  max-c_k members: ALL certify {pc(maxc_all)}  SOME certify {pc(maxc_all+maxc_some)}  NONE {maxc_none}")
out(f"  P(cert | k is max-c_k) = {cert_given_maxc[0]}/{cert_given_maxc[1]} = {100.0*cert_given_maxc[0]/max(1,cert_given_maxc[1]):.1f}%")
out(f"  P(cert | k not max-c_k) = {cert_given_notmaxc[0]}/{cert_given_notmaxc[1]} = {100.0*cert_given_notmaxc[0]/max(1,cert_given_notmaxc[1]):.1f}%")
out(f"  unique-max-c_k member certifies: {uniquemax_cert}/{uniquemax_total} = {100.0*uniquemax_cert/max(1,uniquemax_total):.1f}%")
out(f"  STRAT-CERT (single-stratum subset-of-S cert, size<=2) exists: {pc(strat_size2)}")
out("EXCEPTIONS (no max-c_k member certifies):")
for e in excs: out("  "+json.dumps(e))
