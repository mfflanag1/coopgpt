"""(D-cert) CERTIFICATE MINER — CORRECT target. Lemma D <=> star_S fails ==> EXISTS
coalition C != S with  M^(C) := max{x(S): x in core, x(C)=v(C)}  <=  phi(S).
(This is d*<=slack; NOT the stronger d*=0.) Mine the STRUCTURE of theorem-certs:
 - does a thm-cert always exist? (else THEOREM REFUTED -> flag)
 - min thm-cert: size, subset-of-S?, single leximin-stratum?, singleton?
 - EXISTS thm-cert that is a subset of S within a single stratum?
 - relation to cover W/T*/P/R.
Also tracks floor-certs (M^(C)=v(S), i.e. d*=0) as a sub-case. Float LPs; d* vs slack
uses float leximin (exact blows up on biased n=6). Any apparent theorem refutation is
re-checked and shouted.
"""
import random, sys, time, json
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import Game
from leximin import leximin_core_float
from hunt_exact_points import rand_point_sum, game_from_points
def members(S,n): return [i for i in range(n) if S>>i&1]

def core_ub(n,N,vF):
    return ([[-1.0 if U>>i&1 else 0.0 for i in range(n)] for U in range(1,N)],
            [-vF[U] for U in range(1,N)])
def maxxS_floorC(n,N,vF,A,b,S,C):
    Aeq=[[1.0]*n,[1.0 if C>>i&1 else 0.0 for i in range(n)]]; beq=[vF[N],vF[C]]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method='highs')
    return None if not r.success else -r.fun
def core_max_xS(n,N,vF,A,b,S):
    Aeq=[[1.0]*n]; beq=[vF[N]]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method='highs')
    return None if not r.success else -r.fun
def star_max(n,N,vF,A0,b0,phi,S):
    A=[row[:] for row in A0]; b=b0[:]
    for i in range(n):
        if S>>i&1:
            row=[0.0]*n; row[i]=-1.0; A.append(row); b.append(-phi[i])
    Aeq=[[1.0]*n]; beq=[vF[N]]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method='highs')
    return None if not r.success else -r.fun
def residual_cover_f(n,N,vF,phi,S,tights,tol=1e-6):
    m=len(tights); Sm=members(S,n)
    ai=m; nv=m+1+len(Sm); ridx={k:m+1+t for t,k in enumerate(Sm)}
    Aeq=[]; beq=[]
    for i in range(n):
        row=[0.0]*nv
        for t,U in enumerate(tights):
            if U>>i&1: row[t]=-1.0
        row[ai]=1.0
        if S>>i&1: row[ridx[i]]=-1.0
        Aeq.append(row); beq.append(0.0)
    bounds=[(0,None)]*m+[(None,None)]+[(1,None)]*len(Sm)
    c=[0.0]*nv
    for k in Sm: c[ridx[k]]=1.0
    r=linprog(c,A_eq=Aeq,b_eq=beq,bounds=bounds,method='highs')
    if not r.success: return 0
    W=0
    for t in range(m):
        if r.x[t]>tol: W|=tights[t]
    return W

n=int(sys.argv[1]); seed0=int(sys.argv[2]); target=int(sys.argv[3]); log=sys.argv[4]
def out(s):
    print(s,flush=True)
    with open(log,'a') as f: f.write(s+'\n')
TOL=1e-6; rng=random.Random(seed0*104729+7); N=(1<<n)-1; t0=time.time()
def biased(c):
    k=rng.randint(2,3); base=rand_point_sum(n,c,rng); pts=[base]
    for _ in range(k-1):
        p=list(base); idx=rng.sample(range(n),rng.randint(1,n))
        s=sum(p[i] for i in idx); nvv=rand_point_sum(len(idx),s,rng)
        for j,i in enumerate(idx): p[i]=nvv[j]
        pts.append(p)
    return pts

SF=0; thm_ok=0; thm_bad=0
exists_subS=0; exists_subS_singlestrat=0; exists_singleton=0
min_sizes=[]; min_subS=0; min_singlestrat=0; min_singleton=0
floor_exists=0  # d*=0 (M^(C)=v(S)) exists
samples=[]; hard=[]
out(f"=== DCERT-MINE n={n} seed0={seed0} target={target} @ {time.strftime('%H:%M:%S')} ===")
games=0
while SF<target:
    games+=1
    vg=game_from_points(n,biased(rng.randint(n,6*n))).v; vF=[float(x) for x in vg]
    phi=leximin_core_float(n,vg,tol=1e-9)
    if phi is None: continue
    A,b=core_ub(n,N,vF)
    gains=[phi[i]-vF[1<<i] for i in range(n)]
    levels=sorted(set(round(gv,6) for gv in gains)); strat={i:levels.index(round(gains[i],6)) for i in range(n)}
    tights=[C for C in range(1,N) if abs(sum(phi[i] for i in range(n) if C>>i&1)-vF[C])<TOL]
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=sum(phi[i] for i in range(n) if S>>i&1)
        mx=core_max_xS(n,N,vF,A,b,S)
        if mx is None or mx<=pS+TOL: continue
        sm=star_max(n,N,vF,A,b,phi,S)
        if sm is None or sm>pS+TOL: continue
        SF+=1
        W=residual_cover_f(n,N,vF,phi,S,tights); Tstar=W&S; R=S&~W; Pset=N&~S
        # M^(C) for all C; theorem-certs: M^(C)<=phi(S)+tol
        thm_certs=[]; floor_certs=[]
        for C in range(1,N):
            if C==S: continue
            M=maxxS_floorC(n,N,vF,A,b,S,C)
            if M is None: continue
            if M<=pS+TOL: thm_certs.append(C)
            if abs(M-vF[S])<TOL: floor_certs.append(C)
        if not thm_certs:
            thm_bad+=1
            out(f"*** THEOREM-CERT MISSING (d*>slack?) *** v={[str(x) for x in vg]} S={members(S,n)}")
            continue
        thm_ok+=1
        if floor_certs: floor_exists+=1
        subS=[C for C in thm_certs if (C&S)==C]
        subS_ss=[C for C in subS if len(set(strat[i] for i in members(C,n)))==1]
        singl=[C for C in thm_certs if bin(C).count('1')==1]
        if subS: exists_subS+=1
        if subS_ss: exists_subS_singlestrat+=1
        if singl: exists_singleton+=1
        Cmin=min(thm_certs,key=lambda C:(bin(C).count('1'),C))
        min_sizes.append(bin(Cmin).count('1'))
        if (Cmin&S)==Cmin: min_subS+=1
        if len(set(strat[i] for i in members(Cmin,n)))==1: min_singlestrat+=1
        if bin(Cmin).count('1')==1: min_singleton+=1
        if not subS_ss and len(hard)<25:
            hard.append(dict(v=[str(x) for x in vg],S=members(S,n),
                Cmin=members(Cmin,n),Cmin_subS=((Cmin&S)==Cmin),
                strata_S={i:strat[i] for i in members(S,n)},
                thm_certs_small=[members(C,n) for C in sorted(thm_certs,key=lambda C:bin(C).count('1'))[:6]],
                W=members(W,n),R=members(R,n)))
        if len(samples)<8:
            samples.append(dict(S=members(S,n),Cmin=members(Cmin,n),subS_ss=[members(C,n) for C in subS_ss[:3]]))
        if SF%250==0:
            out(f"[prog] SF={SF} thmOK={thm_ok} thmBAD={thm_bad} | Ex subS={exists_subS} "
                f"subS_1strat={exists_subS_singlestrat} singleton={exists_singleton} floor(d*=0)={floor_exists} "
                f"| minSubS={min_subS} min1strat={min_singlestrat} t={time.time()-t0:.0f}s")
        if SF>=target: break

def pct(a): return f"{100.0*a/max(1,SF):.1f}%"
out(f"\nDONE n={n} s={seed0}: games={games} SF={SF}")
out(f"  THEOREM cert exists (M^(C)<=phi(S)): {thm_ok} ({pct(thm_ok)})  MISSING(refutation): {thm_bad}")
out(f"  floor-cert exists (d*=0, M^(C)=v(S)): {floor_exists} ({pct(floor_exists)})")
out(f"  EXISTS thm-cert subset-of-S: {exists_subS} ({pct(exists_subS)})")
out(f"  EXISTS thm-cert subset-of-S SINGLE-STRATUM: {exists_subS_singlestrat} ({pct(exists_subS_singlestrat)})")
out(f"  EXISTS thm-cert singleton: {exists_singleton} ({pct(exists_singleton)})")
out(f"  min thm-cert: size avg={sum(min_sizes)/len(min_sizes):.2f} max={max(min_sizes)}; subS={pct(min_subS)} singlestrat={pct(min_singlestrat)} singleton={pct(min_singleton)}")
out("SAMPLES: "+json.dumps(samples))
out("HARD (no subset-of-S single-stratum thm-cert):")
for h in hard[:25]: out("  "+json.dumps(h))
