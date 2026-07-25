"""(D0) CERTIFICATE STRUCTURE MINER. Over a fresh corpus of star-fails (biased thin-core
exact games), for each star-fail compute ALL certifying coalitions
   cert(S) = { C != S : max{x(S): x in core, x(C)=v(C)} = v(S) }   (float, tol)
and regress their structure against the failure data. Tests team-lead hypotheses:
 - does a certifying C always exist (d*=0)?
 - is some / the minimal certifying C phi-TIGHT?
 - C vs cover support W, vs T*=W∩S, vs P, vs R, |C∩S|
 - leximin STRATA span of C; is C a union/intersection of tight sets from >1 stratum?
Float throughout (exact leximin blows up on biased n=6). Prints aggregate distributions
and sample concrete (game,S,C_min).
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
    nl=m; ai=m; nv=m+1+len(Sm); ridx={k:m+1+t for t,k in enumerate(Sm)}
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
    if not r.success: return None
    sol=r.x
    W=0
    for t in range(m):
        if sol[t]>tol: W|=tights[t]
    sigma=sol[ai]; rd={k:sol[ridx[k]] for k in Sm}
    return W,sigma,rd

n=int(sys.argv[1]); seed0=int(sys.argv[2]); target=int(sys.argv[3])
log=sys.argv[4] if len(sys.argv)>4 else None
def out(s):
    print(s,flush=True)
    if log:
        with open(log,'a') as f: f.write(s+'\n')
TOL=1e-6
rng=random.Random(seed0*104729+7); N=(1<<n)-1; t0=time.time()

def biased(c):
    k=rng.randint(2,3); base=rand_point_sum(n,c,rng); pts=[base]
    for _ in range(k-1):
        p=list(base); idx=rng.sample(range(n),rng.randint(1,n))
        s=sum(p[i] for i in idx); nvv=rand_point_sum(len(idx),s,rng)
        for j,i in enumerate(idx): p[i]=nvv[j]
        pts.append(p)
    return pts

# aggregate counters
SF=0; d0_ok=0; d0_bad=0
some_cert_tight=0; min_cert_tight=0
cmin_supS=0; cmin_subS=0; cmin_eqTstar=0; cmin_supP=0; cmin_subW=0
cmin_capR_empty=0; cmin_is_singleton=0; cmin_is_pair=0
strata_span=[]; cmin_sizes=[]; cmin_capS_sizes=[]
tight_multistrata=0
_cC_single=0; _cC_singlestrat=0; _has_subS=0; _subS_singlestrat=0; _subS_sizes=[]
samples=[]; fail_samples=[]
out(f"=== D0-MINE n={n} seed0={seed0} target={target} @ {time.strftime('%H:%M:%S')} ===")
games=0
while SF<target:
    games+=1
    vg=game_from_points(n,biased(rng.randint(n,6*n))).v
    vF=[float(x) for x in vg]
    phi=leximin_core_float(n,vg,tol=1e-9)
    if phi is None: continue
    A,b=core_ub(n,N,vF)
    # strata: group players by gain phi_i - m_i (m_i=v[{i}])
    gains=[phi[i]-vF[1<<i] for i in range(n)]
    levels=sorted(set(round(gv,6) for gv in gains))
    strat={i:levels.index(round(gains[i],6)) for i in range(n)}
    # tight sets at phi (float)
    tights=[C for C in range(1,N) if abs(sum(phi[i] for i in range(n) if C>>i&1)-vF[C])<TOL]
    tset=set(tights)
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=sum(phi[i] for i in range(n) if S>>i&1)
        mx=core_max_xS(n,N,vF,A,b,S)
        if mx is None or mx<=pS+TOL: continue         # no room
        sm=star_max(n,N,vF,A,b,phi,S)
        if sm is None or sm>pS+TOL: continue           # star holds
        SF+=1
        # cover
        cov=residual_cover_f(n,N,vF,phi,S,tights)
        W=Tstar=Pset=R=0
        if cov:
            W,sigma,rd=cov; Tstar=W&S; Pset=N&~S; R=S&~W
        # certifying C's: max{x(S): x(C)=v(C)} == v(S)
        certs=[]
        for C in range(1,N):
            if C==S: continue
            m=maxxS_floorC(n,N,vF,A,b,S,C)
            if m is not None and abs(m-vF[S])<TOL: certs.append(C)
        if not certs:
            d0_bad+=1
            out(f"*** D0 VIOLATION (no cert C, d*>0) *** v={[str(x) for x in vg]} S={members(S,n)}")
            continue
        d0_ok+=1
        # --- Conjecture-C revival: singleton-in-S cert? single-stratum-subset-of-S cert? ---
        singleton_inS=[C for C in certs if bin(C).count('1')==1 and (C&S)==C]
        if singleton_inS: _cC_single+=1
        # cert that is a SUBSET OF S and within a single stratum:
        single_strat_inS=[C for C in certs if (C&S)==C and
                          len(set(strat[i] for i in members(C,n)))==1]
        if single_strat_inS: _cC_singlestrat+=1
        # minimal cert among subsets-of-S:
        subS_certs=[C for C in certs if (C&S)==C]
        if subS_certs:
            _has_subS+=1
            Csub=min(subS_certs,key=lambda C:(bin(C).count('1'),C))
            _subS_sizes.append(bin(Csub).count('1'))
            if len(set(strat[i] for i in members(Csub,n)))==1: _subS_singlestrat+=1
        # does some cert / min cert phi-tight?
        tight_certs=[C for C in certs if C in tset]
        if tight_certs: some_cert_tight+=1
        Cmin=min(certs,key=lambda C:(bin(C).count('1'),C))
        # prefer a tight minimal if exists
        if tight_certs:
            Cmt=min(tight_certs,key=lambda C:(bin(C).count('1'),C))
        else:
            Cmt=None
        if Cmt is not None and Cmt==Cmin: min_cert_tight+=1
        elif Cmin in tset: min_cert_tight+=1
        # features of Cmin
        sz=bin(Cmin).count('1'); cmin_sizes.append(sz)
        capS=bin(Cmin&S).count('1'); cmin_capS_sizes.append(capS)
        if sz==1: cmin_is_singleton+=1
        if sz==2: cmin_is_pair+=1
        if (Cmin&S)==S: cmin_supS+=1
        if (Cmin&~S)==0: cmin_subS+=1
        if Cmin==Tstar: cmin_eqTstar+=1
        if Pset and (Pset&~Cmin)==0: cmin_supP+=1
        if W and (Cmin&~W)==0: cmin_subW+=1
        if R and (Cmin&R)==0: cmin_capR_empty+=1
        # strata span of Cmin
        spa=len(set(strat[i] for i in members(Cmin,n))); strata_span.append(spa)
        if (Cmin in tset) and spa>1: tight_multistrata+=1
        if len(samples)<10:
            samples.append(dict(v=[str(x) for x in vg],S=members(S,n),Cmin=members(Cmin,n),
                W=members(W,n),Tstar=members(Tstar,n),R=members(R,n),ncerts=len(certs)))
        if not single_strat_inS and len(fail_samples)<20:
            # star-fail with NO subset-of-S single-stratum cert: the hard case
            fail_samples.append(dict(v=[str(x) for x in vg],S=members(S,n),
                Cmin=members(Cmin,n),Cmin_subS=((Cmin&S)==Cmin),Cmin_span=spa,
                strata={i:strat[i] for i in members(S,n)},R=members(R,n),
                allcerts=[members(C,n) for C in sorted(certs,key=lambda C:bin(C).count('1'))[:6]]))
        if SF%200==0:
            out(f"[prog] SF={SF} d0_ok={d0_ok} d0_bad={d0_bad} someCertTight={some_cert_tight} "
                f"minCertTight={min_cert_tight} tightMultiStrata={tight_multistrata} t={time.time()-t0:.0f}s")
        if SF>=target: break

def pct(a): return f"{100.0*a/max(1,SF):.1f}%"
out(f"\nDONE n={n} seed0={seed0}: games={games} star-fails SF={SF}")
out(f"  d0_ok(cert exists, d*=0)={d0_ok}  d0_BAD(d*>0)={d0_bad}")
out(f"  star-fails with SOME phi-tight cert C: {some_cert_tight} ({pct(some_cert_tight)})")
out(f"  minimal cert C is phi-tight: {min_cert_tight} ({pct(min_cert_tight)})")
out(f"  Cmin sizes: min={min(cmin_sizes)} max={max(cmin_sizes)} avg={sum(cmin_sizes)/len(cmin_sizes):.2f}")
out(f"  Cmin singleton: {cmin_is_singleton} ({pct(cmin_is_singleton)})  pair: {cmin_is_pair} ({pct(cmin_is_pair)})")
out(f"  |Cmin ∩ S| avg={sum(cmin_capS_sizes)/len(cmin_capS_sizes):.2f}")
out(f"  Cmin ⊇ S: {cmin_supS} ({pct(cmin_supS)})   Cmin ⊆ S: {cmin_subS} ({pct(cmin_subS)})")
out(f"  Cmin == T*(=W∩S): {cmin_eqTstar} ({pct(cmin_eqTstar)})")
out(f"  Cmin ⊇ P: {cmin_supP} ({pct(cmin_supP)})   Cmin ⊆ W: {cmin_subW} ({pct(cmin_subW)})   Cmin ∩ R=∅: {cmin_capR_empty} ({pct(cmin_capR_empty)})")
out(f"  Cmin strata-span: avg={sum(strata_span)/len(strata_span):.2f} dist={ {s:strata_span.count(s) for s in sorted(set(strata_span))} }")
out(f"  Cmin phi-tight AND spans>1 stratum: {tight_multistrata} ({pct(tight_multistrata)})")
out(f"  --- Conjecture-C revival ---")
out(f"  EXISTS singleton-in-S cert (M_k=v(S), k in S): {_cC_single} ({pct(_cC_single)})")
out(f"  EXISTS subset-of-S single-STRATUM cert: {_cC_singlestrat} ({pct(_cC_singlestrat)})")
out(f"  EXISTS subset-of-S cert (any): {_has_subS} ({pct(_has_subS)})")
if _subS_sizes:
    out(f"  minimal subset-of-S cert size: avg={sum(_subS_sizes)/len(_subS_sizes):.2f} max={max(_subS_sizes)}; single-stratum: {_subS_singlestrat} ({pct(_subS_singlestrat)})")
out("SAMPLES (generic):")
for s in samples[:10]: out("  "+json.dumps(s))
out("FAIL SAMPLES (no subset-of-S single-stratum cert):")
for s in fail_samples[:20]: out("  "+json.dumps(s))

