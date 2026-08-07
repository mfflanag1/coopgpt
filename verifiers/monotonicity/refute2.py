"""Full independent verification of the C-B counterexample found by the
constructive family (n=6, exact domain)."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3")
import audit, z3
from hunt2 import boundaries, nm, core_expr, dmax
from probeA_sweep import exact_lp
N=6; FULL=63
ROWS=[(0,15,0,14,0,0),(0,9,0,9,6,5),(4,0,4,0,21,0)]
print("rows (common total %d):"%sum(ROWS[0]), ROWS)
gens=[tuple(F(q) for q in r) for r in ROWS]
w=audit.envelope(N,gens)
print("singleton-normalized:", all(w[1<<i]==0 for i in range(N)), " v(N) =", w[FULL])

def exact_all(val):
    x=[z3.Real(f"z{i}") for i in range(N)]
    base=[z3.Sum(x)==audit.to_z3(val[FULL])]+[
        z3.Sum([x[i] for i in range(N) if T>>i&1])>=audit.to_z3(val[T]) for T in range(1,FULL)]
    bad=[]
    for T in range(1,FULL):
        o=z3.Optimize(); o.add(base)
        h=o.minimize(z3.Sum([x[i] for i in range(N) if T>>i&1]))
        if o.check()!=z3.sat: return False,[T]
        if audit.rat(o.lower(h))!=val[T]: bad.append(T)
    return (not bad), bad

def lmin_ladder(val):
    x=[z3.Real(f"y{i}") for i in range(N)]
    base=[z3.Sum(x)==audit.to_z3(val[FULL])]+[
        z3.Sum([x[i] for i in range(N) if T>>i&1])>=audit.to_z3(val[T]) for T in range(1,FULL)]
    fixed=[]
    for mm in range(1,N+1):
        s=z3.Real(f"s{mm}")
        o=z3.Optimize(); o.add(base+fixed+[s<=z3.Sum([x[i] for i in A])
                        for A in itertools.combinations(range(N),mm)])
        h=o.maximize(s); assert o.check()==z3.sat
        best=audit.rat(o.upper(h))
        fixed.append(z3.And([z3.Sum([x[i] for i in A])>=audit.to_z3(best)
                             for A in itertools.combinations(range(N),mm)]))
    o=z3.Optimize(); o.add(base+fixed); assert o.check()==z3.sat
    mdl=o.model(); pt=[audit.rat(mdl.eval(x[i],model_completion=True)) for i in range(N)]
    sv=z3.Solver(); sv.add(base+fixed)
    sv.add(z3.Or([x[i]!=audit.to_z3(pt[i]) for i in range(N)]))
    assert sv.check()==z3.unsat,"ladder optimum not unique"
    return pt

phi=audit.lmin(N,w); assert lmin_ladder(w)==phi
print("phi =",[str(q) for q in phi],"(staged z3 and Sigma_m ladder agree)")
blocks=audit.strata(phi); bnd=boundaries(N,w,phi)
print("strata poor->rich:",[[i+1 for i in b] for b in blocks],[str(phi[b[0]]) for b in blocks])
print("richer suffixes / slacks:",[(nm(N,H),str(s)) for H,s in bnd])
print("v exact:",exact_all(w)[0])
x,base=core_expr(N,w)
sl=[q for q,(H,s) in enumerate(bnd) if s>0]; jstar=max(sl)
pred=sum(1<<q for q in blocks[jstar+1]); Hstar=bnd[jstar][0]
print("H* (innermost slack suffix) =",nm(N,Hstar)," C-B predicts W =",nm(N,pred))
found=False
for S in range(1,FULL):
    if bin(S).count("1")<2: continue
    sS=sum(phi[q] for q in range(N) if S>>q&1)-w[S]
    g=min(w[S|(1<<q)]-w[S] for q in range(N) if not S>>q&1)
    if g<=sS: continue
    dm=dmax(N,w,S,x,base)
    if dm is None or dm<=sS: continue
    for d in sorted({dm,sS+(dm-sS)/2,sS+(dm-sS)/4}):
        if d<=sS: continue
        w2=list(w); w2[S]=w[S]+d
        if not exact_lp(N,w2): continue
        phi2=audit.lmin(N,w2)
        if phi2 is None: continue
        W=[q for q in range(N) if S>>q&1 and phi2[q]<phi[q]]
        if not W: continue
        Wm=sum(1<<q for q in W)
        ok2,_=exact_all(w2); assert lmin_ladder(w2)==phi2
        print("\n--- violation ---")
        print("S =",nm(N,S)," s_phi(S) =",str(sS)," d =",str(d)," d_max =",str(dm))
        print("v' exact (full certification):",ok2,"  phi' =",[str(q) for q in phi2],
              "(both algorithms agree)")
        print("W =",nm(N,Wm)," all strict losers =",
              nm(N,sum(1<<q for q in range(N) if phi2[q]<phi[q])),
              " gainers =",nm(N,sum(1<<q for q in range(N) if phi2[q]>phi[q])))
        print("C-A (W a slack suffix):",Wm in [H for H,s in bnd if s>0])
        print("C-B (W = predicted stratum %s):"%nm(N,pred), Wm==pred)
        print("W a single stratum:", any(Wm==sum(1<<q for q in b) for b in blocks))
        print("W inside H*:", (Wm & ~Hstar)==0, "   S contains H*:", (Hstar & ~S)==0)
        sW=sum(phi[q] for q in range(N) if Wm>>q&1)-w[Wm]
        print("Theorem A: s_phi(W) =",str(sW)," loss =",
              str(sum(phi[q]-phi2[q] for q in W))," ok:",sum(phi[q]-phi2[q] for q in W)<=sW)
        print("top stratum %s: phi'=%s (tight suffix cannot lose in aggregate:"%(
              nm(N,sum(1<<q for q in blocks[-1])),
              [str(phi2[q]) for q in blocks[-1]]),
              sum(phi2[q] for q in blocks[-1])>=sum(phi[q] for q in blocks[-1]),")")
        found=True; break
    if found: break
