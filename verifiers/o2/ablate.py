"""Which hypotheses are load-bearing?  Re-run the main sweep dropping one at a time."""
import json, sys
from fractions import Fraction as F
import z3
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/a3check"); sys.path.insert(0,SCR+"/sel/o2")
from cone import inequalities
from o2main import load_pinverts, sz, nm, N, FULL, J, L, R

def prog(Sstar, pin, ineqs, z0=True, nu=True, x0=True, pinning=True, cone=True, budget=400):
    v=[z3.Real(f"v{S}") for S in range(32)]; mu=z3.Real("mu"); rho=(1-3*mu)/2
    s=z3.Solver(); s.add(v[0]==0)
    for i in range(N): s.add(v[1<<i]==0)
    s.add(v[FULL]==1)
    for S in range(1,FULL+1):
        if z0: s.add(v[S] <= F(sz(S)-(1 if S>>J&1 else 0),4))
        if nu: s.add(4*v[S] <= sz(S))
        if x0: s.add(v[S] <= mu*len([i for i in L if S>>i&1])+rho*len([i for i in R if S>>i&1]))
    if nu: s.add(v[Sstar]==F(sz(Sstar),4))
    s.add(mu == 1 - v[FULL^(1<<J)]); s.add(mu>=0); s.add(mu<F(1,8))
    if pinning:
        al,be=pin; fp=lambda S:(1-v[FULL^S])-mu*sz(S)
        s.add(z3.RealVal(f"{al.numerator}/{al.denominator}")*(1-5*mu)
              + z3.Sum([z3.RealVal(f"{x.numerator}/{x.denominator}")*fp(S) for S,x in be] or [z3.RealVal(0)])<=0)
    if not cone: return s.check()==z3.sat
    for _ in range(budget):
        r=s.check(); assert r in (z3.sat,z3.unsat)
        if r==z3.unsat: return False
        m=s.model()
        def val(e):
            q=z3.simplify(m.eval(e,model_completion=True))
            return F(q.as_long()) if z3.is_int_value(q) else F(q.numerator_as_long(),q.denominator_as_long())
        vv=[val(v[S]) for S in range(32)]
        bad=None
        for c in ineqs:
            if sum(F(c[S])*vv[S] for S in range(1,32) if c[S])>0: bad=c; break
        if bad is None: return True
        s.add(z3.Sum([z3.RealVal(bad[S])*v[S] for S in range(1,32) if bad[S]])<=0)
    raise RuntimeError

ineqs=inequalities(N); pins=load_pinverts()
cases=[("FULL (all hypotheses)",{}),
       ("drop cone",{"cone":False}),
       ("drop nu = 1/4",{"nu":False}),
       ("drop x0 in Core",{"x0":False}),
       ("drop z0 in Core",{"z0":False}),
       ("drop PINNING",{"pinning":False})]
out={}
for label,kw in cases:
    cnt=0
    for Sstar in range(1,FULL+1):
        for pin in pins:
            if prog(Sstar,pin,ineqs,**kw): cnt+=1
            if kw.get("pinning") is False: break     # pinning unused: one pin suffices
    tot = FULL*len(pins) if kw.get("pinning") is not False else FULL
    out[label]=(cnt,tot)
    print(f"  {label:26s}: {cnt:6d} / {tot} programs feasible", flush=True)
json.dump(out, open(f"{SCR}/sel/o2/ablate.json","w"), indent=1)
