"""FULL independent verification of the C-A(a) counterexample (n=6, exact
domain).  Every hypothesis of C-A is checked, and the conclusion fails."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3")
import audit, z3
from hunt2 import boundaries, nm
from probeA_sweep import exact_lp

N=6; FULL=63
GENS=[(3,16,2,7,2,0),(3,15,2,4,5,1),(5,5,3,0,17,0)]
gens=[tuple(F(q) for q in g) for g in GENS]
print("generators (common total %s):"%sum(gens[0]), GENS)
v=audit.envelope(N,gens); w,m=audit.normalize(N,v)
print("normalization shift m =",[str(q) for q in m],"(already singleton-normalized)" if all(q==0 for q in m) else "")
S=0b011111; d=F(9,16)
w2=list(w); w2[S]=w[S]+d
print("v(N)=%s  S=%s  v(S)=%s -> v'(S)=%s  d=%s"%(w[FULL],nm(N,S),w[S],w2[S],d))

# ---- hypothesis 1: singleton-normalized, S proper non-singleton, d>0
print("\n[H1] singleton-normalized v :", all(w[1<<i]==0 for i in range(N)))
print("[H1] singleton-normalized v':", all(w2[1<<i]==0 for i in range(N)))
print("[H1] S proper, |S|>=2, d>0 :", S!=FULL and bin(S).count('1')>=2 and d>0)
print("[H1] v' differs from v at S only:",
      all(w2[T]==w[T] for T in range(1<<N) if T!=S))

# ---- hypothesis 2: BOTH games exact (independent full certification)
def exact_all(val):
    x=[z3.Real(f"z{i}") for i in range(N)]
    base=[z3.Sum(x)==audit.to_z3(val[FULL])]+[
        z3.Sum([x[i] for i in range(N) if T>>i&1])>=audit.to_z3(val[T])
        for T in range(1,FULL)]
    bad=[]
    for T in range(1,FULL):
        o=z3.Optimize(); o.add(base)
        h=o.minimize(z3.Sum([x[i] for i in range(N) if T>>i&1]))
        if o.check()!=z3.sat: return False,[T]
        if audit.rat(o.lower(h))!=val[T]: bad.append(T)
    return (not bad), bad
e1=exact_all(w); e2=exact_all(w2)
print("[H2] v  exact:",e1[0]," v' exact:",e2[0], "(exact_lp agrees:",exact_lp(N,w2),")")

# ---- Lmin, two independent algorithms
def lmin_ladder(val):
    x=[z3.Real(f"y{i}") for i in range(N)]
    base=[z3.Sum(x)==audit.to_z3(val[FULL])]+[
        z3.Sum([x[i] for i in range(N) if T>>i&1])>=audit.to_z3(val[T])
        for T in range(1,FULL)]
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
    assert sv.check()==z3.unsat, "ladder optimum not unique"
    return pt
phi=audit.lmin(N,w); phi2=audit.lmin(N,w2)
lp1=lmin_ladder(w); lp2=lmin_ladder(w2)
print("\nphi  =",[str(q) for q in phi], " ladder agrees:",lp1==phi)
print("phi' =",[str(q) for q in phi2]," ladder agrees:",lp2==phi2)
print("both in their cores:",
      all(sum(phi[i] for i in range(N) if T>>i&1)>=w[T] for T in range(1,FULL)) and sum(phi)==w[FULL],
      all(sum(phi2[i] for i in range(N) if T>>i&1)>=w2[T] for T in range(1,FULL)) and sum(phi2)==w2[FULL])

# ---- the conclusion of C-A fails
blocks=audit.strata(phi)
print("\nstrata of phi (poor->rich):",[[i+1 for i in b] for b in blocks],
      [str(phi[b[0]]) for b in blocks])
bnd=boundaries(N,w,phi)
print("richer suffixes and slacks:",[(nm(N,H),str(s)) for H,s in bnd])
W=[i for i in range(N) if S>>i&1 and phi2[i]<phi[i]]; Wm=sum(1<<i for i in W)
G=[i for i in range(N) if phi2[i]<phi[i]]
print("s_phi(S) =",str(sum(phi[i] for i in range(N) if S>>i&1)-w[S]),
      "  d =",str(d),"  (d > s_phi(S):",d>sum(phi[i] for i in range(N) if S>>i&1)-w[S],")")
print("W  (strict losers in S) =",nm(N,Wm))
print("all strict losers       =",nm(N,sum(1<<i for i in G)))
print("gainers                 =",nm(N,sum(1<<i for i in range(N) if phi2[i]>phi[i])))
print("\n*** C-A(a): is W a richer suffix?", Wm in [H for H,_ in bnd], " <-- must be True")
print("*** is W a SLACK richer suffix?", Wm in [H for H,s in bnd if s>0])
H0=[H for H,s in bnd if s>0]
print("the unique slack suffix H =",[nm(N,H) for H in H0],
      "; H ∩ S =",[nm(N,H&S) for H in H0]," ; W =",nm(N,Wm))
print("SC1 (W = H_c ∩ S):", (sum(1<<i for i in range(N) if phi[i]>=min(phi[i] for i in W))&S)==Wm)
print("W subset of the slack suffix:", all((Wm & ~H)==0 for H in H0))
sW=sum(phi[i] for i in range(N) if Wm>>i&1)-w[Wm]
print("\nTheorem A still holds: s_phi(W) =",str(sW),
      " loss on W =",str(sum(phi[i]-phi2[i] for i in W)), " (loss <= slack:",
      sum(phi[i]-phi2[i] for i in W)<=sW,")")
print("Theorem A on EVERY losing coalition:",
      all(sum(phi[i]-phi2[i] for i in range(N) if T>>i&1) <=
          sum(phi[i] for i in range(N) if T>>i&1)-w[T]
          for T in range(1,FULL) if T!=S and
          sum(phi2[i] for i in range(N) if T>>i&1)<sum(phi[i] for i in range(N) if T>>i&1)))
