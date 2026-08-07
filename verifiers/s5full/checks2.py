"""(a) CONTROL for jrich.py: dropping the pinning must restore feasibility.
   (b) Corollary 23's second hypothesis: in CFG (j poor) must some nu-attaining
       coalition have three players?  Encode "every 3-set is strictly below the
       nu line" and decide."""
import json, sys
from fractions import Fraction as F
import z3
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/a3check"); sys.path.insert(0,SCR+"/sel/o2"); sys.path.insert(0,SCR+"/sel/s5full")
from cone import inequalities
import jrich as JR
from o2main import load_pinverts
N,FULL=5,31
sz=lambda S: bin(S).count("1"); nm=JR.nm
ineqs=inequalities(N)

def base(J, Lset, Rset, cap, pin=None, nu_anchor=None, no_triple=False, budget=400):
    v=[z3.Real(f"v{S}") for S in range(32)]; mu=z3.Real("mu"); rho=(1-3*mu)/2
    s=z3.Solver(); s.add(v[0]==0)
    for i in range(N): s.add(v[1<<i]==0)
    s.add(v[FULL]==1)
    for S in range(1,FULL+1):
        s.add(v[S] <= F(sz(S)-(1 if S>>J&1 else 0),4))
        s.add(4*v[S] <= sz(S))
        s.add(v[S] <= mu*len([i for i in Lset if S>>i&1])+rho*len([i for i in Rset if S>>i&1]))
        s.add(1 - v[FULL^S] >= mu*sz(S))
    s.add(mu>=0); s.add(mu<cap); s.add(mu<F(1,5))
    if nu_anchor is not None: s.add(v[nu_anchor]==F(sz(nu_anchor),4))
    if no_triple:
        for S in range(1,FULL+1):
            if sz(S)==3: s.add(4*v[S] < 3)
    if pin is not None:
        al,be=pin; fp=lambda S:(1-v[FULL^S])-mu*sz(S)
        s.add(z3.RealVal(f"{al.numerator}/{al.denominator}")*(1-5*mu)
              + z3.Sum([z3.RealVal(f"{x.numerator}/{x.denominator}")*fp(S) for S,x in be] or [z3.RealVal(0)])<=0)
    for _ in range(budget):
        r=s.check(); assert r in (z3.sat,z3.unsat)
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
    raise RuntimeError

# (a) control: j-rich, no pinning
cnt=0; wit=None
for Sstar in range(1,FULL+1):
    w=base(0,[1,2,3],[0,4],F(1,6),pin=None,nu_anchor=Sstar)
    if w is not None: cnt+=1; wit=wit or (nm(Sstar),w["mu"])
print(f"(a) CONTROL j-rich WITHOUT pinning: {cnt}/{FULL} anchors feasible  e.g. {wit}")

# (b) Corollary 23 hypothesis 2: CFG j-poor, mu < 1/8 is already excluded, so ask
#     instead: can CFG (j poor) have NO nu-attaining 3-set?  mu is then free in
#     [1/8, 1/5); we test feasibility of "no 3-set attains nu" outright.
pins=load_pinverts()
cnt=0; wit=None
for pin in pins:
    w=base(0,[0,1,2],[3,4],F(1,5),pin=pin,nu_anchor=None,no_triple=True)
    if w is not None:
        cnt+=1
        if wit is None: wit=w
print(f"(b) CFG (j poor) with NO nu-attaining 3-set: {cnt}/{len(pins)} certificates feasible")
if wit: print("    witness mu =",wit["mu"])
json.dump({"control_jrich_no_pinning":cnt if False else None,
           "a_control_feasible_anchors":cnt,"b_witness":wit},
          open(f"{SCR}/sel/s5full/checks2.json","w"),indent=1)
