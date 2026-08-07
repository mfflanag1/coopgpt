"""Minimal unsat cores: which hypotheses actually kill the failure program?"""
import json, sys
from fractions import Fraction as F
import z3
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/o2")
from o2main import load_pinverts, sz, nm, N, FULL, J, L, R

def core_for(Sstar, pin):
    v=[z3.Real(f"v{S}") for S in range(32)]; mu=z3.Real("mu"); rho=(1-3*mu)/2
    s=z3.Solver(); s.set(unsat_core=True)
    s.add(v[0]==0)
    for i in range(N): s.add(v[1<<i]==0)
    s.add(v[FULL]==1)
    lab={}
    def tr(name, e):
        p=z3.Bool(name); lab[name]=e; s.assert_and_track(e,p)
    for S in range(1,FULL+1):
        tr(f"z0[{nm(S)}]", v[S] <= F(sz(S)-(1 if S>>J&1 else 0),4))
        tr(f"nu[{nm(S)}]", 4*v[S] <= sz(S))
        tr(f"x0[{nm(S)}]", v[S] <= mu*len([i for i in L if S>>i&1])+rho*len([i for i in R if S>>i&1]))
    tr("nu_attained", v[Sstar]==F(sz(Sstar),4))
    tr("mu=f(j)", mu == 1 - v[FULL^(1<<J)])
    tr("mu>=0", mu >= 0)
    tr("FAILURE mu<1/8", mu < F(1,8))
    al,be = pin
    fp = lambda S: (1 - v[FULL^S]) - mu*sz(S)
    tr("PINNING", z3.RealVal(f"{al.numerator}/{al.denominator}")*(1-5*mu)
       + z3.Sum([z3.RealVal(f"{x.numerator}/{x.denominator}")*fp(S) for S,x in be] or [z3.RealVal(0)]) <= 0)
    assert s.check()==z3.unsat
    return sorted(str(c) for c in s.unsat_core())

pins = load_pinverts()
out=[]
for name in ("cd","bde"):                       # S* = R  and  S* = {b} u R
    Sstar = sum(1<<"abcde".index(ch) for ch in name)
    best=None
    for k,pin in enumerate(pins):
        c = core_for(Sstar, pin)
        if best is None or len(c)<len(best[1]): best=(k,c,pin)
    k,c,pin = best
    print(f"\nS*={name}: smallest core has {len(c)} assertions (pin #{k}, alpha={pin[0]}, beta={ {nm(S):str(x) for S,x in pin[1]} })")
    for a in c: print("   ", a)
    out.append({"Sstar":name,"pin_alpha":str(pin[0]),
                "pin_beta":{nm(S):str(x) for S,x in pin[1]},"core":c})
json.dump(out, open(f"{SCR}/sel/o2/core.json","w"), indent=1)
