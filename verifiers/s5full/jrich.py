"""CFG with an Lmin-RICH starved player: the case that could REFUTE s(5)=1/2.

Configuration: Lmin strata (3,2), Lmax strata (1,4) with the zero at j, and j
in the Lmin-RICH pair.  Normalise T = 1, so M = 1/4 and rho = (1-3mu)/2.
Label j = 0, poor L = {1,2,3}, rich R = {0,4}; so x = (rho,mu,mu,mu,rho) and
z = (0,1/4,1/4,1/4,1/4).

GAP ARITHMETIC.  x - z = (rho, mu-1/4, mu-1/4, mu-1/4, rho-1/4).  Since
mu <= 1/5 < 1/4 the three middle terms are negative, and rho >= 1/4 iff
mu <= 1/6.  So
    ratio = 3/2 - 6 mu   if mu <= 1/6,      ratio = 1 - 3 mu   if mu > 1/6,
hence   ratio > 1/2  <=>  mu < 1/6.
So the whole question is whether this configuration can occur with mu < 1/6.
A FEASIBLE case here refutes s(5) = 1/2.

Hypotheses encoded (the o2 set, mirrored to the rich labelling):
  z in Core; x in Core; mu = lambda (f(S) >= mu|S|, attained);
  nu = M = 1/4 attained at an anchor S0 (A3); the poor triple L pinned at mu
  (dual certificate, 354 vertices); and the failure hypothesis mu < 1/6.
"""
from __future__ import annotations
import itertools, json, sys
from fractions import Fraction as F
import z3
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/a3check"); sys.path.insert(0,SCR+"/sel/o2")
from cone import inequalities

N,FULL,J = 5,31,0
L,R = [1,2,3],[0,4]
sz = lambda S: bin(S).count("1")
nm = lambda S: "".join("abcde"[i] for i in range(N) if S>>i&1) or "0"

def pinverts_for(Lset):
    """Vertices of D_L for the given poor triple (recomputed: L is not {0,1,2})."""
    PROPER=[S for S in range(1,FULL)]
    rhs=[1 if k in Lset else 0 for k in range(N)]
    def solve(A,b):
        k=len(A); nc=len(A[0]); M=[[F(x) for x in A[r]]+[F(b[r])] for r in range(k)]
        piv,rr=[],0
        for c in range(nc):
            p=next((r for r in range(rr,k) if M[r][c]!=0),None)
            if p is None: return None
            M[rr],M[p]=M[p],M[rr]; pv=M[rr][c]; M[rr]=[q/pv for q in M[rr]]
            for r in range(k):
                if r!=rr and M[r][c]!=0:
                    f=M[r][c]; M[r]=[M[r][j]-f*M[rr][j] for j in range(nc+1)]
            piv.append(c); rr+=1
        return [M[i][nc] for i in range(nc)] if len(piv)==nc else None
    verts=set()
    for k in range(0,5):
        for W in itertools.combinations(PROPER,k):
            for I in itertools.combinations(range(N),k+1):
                A=[[1]+[1 if S>>i&1 else 0 for S in W] for i in I]
                sol=solve(A,[rhs[i] for i in I])
                if sol is None: continue
                al,be=sol[0],sol[1:]
                if any(x<=0 for x in be): continue
                if all(al+sum(be[jj] for jj,S in enumerate(W) if S>>kk&1)>=rhs[kk] for kk in range(N)):
                    verts.add((al,tuple(sorted((S,be[jj]) for jj,S in enumerate(W)))))
    return sorted(verts)

def prog(Sstar,pin,ineqs,budget=400):
    v=[z3.Real(f"v{S}") for S in range(32)]; mu=z3.Real("mu"); rho=(1-3*mu)/2
    s=z3.Solver(); s.add(v[0]==0)
    for i in range(N): s.add(v[1<<i]==0)
    s.add(v[FULL]==1)
    for S in range(1,FULL+1):
        s.add(v[S] <= F(sz(S)-(1 if S>>J&1 else 0),4))                      # z in Core
        s.add(4*v[S] <= sz(S))                                              # nu <= 1/4
        s.add(v[S] <= mu*len([i for i in L if S>>i&1])+rho*len([i for i in R if S>>i&1]))
        s.add(1 - v[FULL^S] >= mu*sz(S))                                    # lambda >= mu
    s.add(v[Sstar]==F(sz(Sstar),4))                                         # nu attained
    s.add(mu>=0); s.add(mu<F(1,6)); s.add(mu<F(1,5))                        # failure; rho>mu
    al,be=pin; fp=lambda S:(1-v[FULL^S])-mu*sz(S)
    s.add(z3.RealVal(f"{al.numerator}/{al.denominator}")*(1-5*mu)
          + z3.Sum([z3.RealVal(f"{x.numerator}/{x.denominator}")*fp(S) for S,x in be] or [z3.RealVal(0)])<=0)
    for _ in range(budget):
        r=s.check(); assert r in (z3.sat,z3.unsat), f"z3 said {r}"
        if r==z3.unsat: return None
        m=s.model()
        def val(e):
            q=z3.simplify(m.eval(e,model_completion=True))
            return F(q.as_long()) if z3.is_int_value(q) else F(q.numerator_as_long(),q.denominator_as_long())
        vv=[val(v[S]) for S in range(32)]
        bad=None
        for c in ineqs:
            if sum(F(c[S])*vv[S] for S in range(1,32) if c[S])>0: bad=c; break
        if bad is None: return {"v":[str(q) for q in vv],"mu":str(val(mu))}
        s.add(z3.Sum([z3.RealVal(bad[S])*v[S] for S in range(1,32) if bad[S]])<=0)
    raise RuntimeError("budget")

if __name__=="__main__":
    ineqs=inequalities(N); pins=pinverts_for(L)
    print(f"{len(pins)} pinning certificates for L={L}; {FULL} anchors -> {len(pins)*FULL} programs",flush=True)
    hits=[]
    for Sstar in range(1,FULL+1):
        for pin in pins:
            w=prog(Sstar,pin,ineqs)
            if w is not None:
                hits.append({"Sstar":nm(Sstar),"alpha":str(pin[0]),
                             "beta":{nm(S):str(x) for S,x in pin[1]},**w})
                print("  *** FEASIBLE ***",nm(Sstar),w["mu"],flush=True)
        if Sstar%8==0: print(f"  ... anchors done {Sstar}/{FULL}, {len(hits)} feasible",flush=True)
    print(f"RESULT: {len(hits)} feasible of {len(pins)*FULL}")
    json.dump({"pins":len(pins),"programs":len(pins)*FULL,"feasible":hits},
              open(f"{SCR}/sel/s5full/jrich.json","w"),indent=1)
