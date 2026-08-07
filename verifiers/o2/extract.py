"""Extract the mu>0 candidate models and test them END TO END:
is the model a genuine exact game in CFG with f({j}) < T/8?"""
import sys, json
from fractions import Fraction as F
import z3
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/a3check"); sys.path.insert(0,SCR+"/sel/o2")
import audit, lmax as lmaxmod
from cone import inequalities
import o2check as O

ineqs = inequalities(5)
N=5; FULL=31; J=0; L=[0,1,2]; R=[3,4]

def prog(Sstar, extra=None, budget=300):
    v=[z3.Real(f"v{S}") for S in range(32)]; mu=z3.Real("mu"); rho=(1-3*mu)/2
    s=z3.Solver(); s.add(v[0]==0)
    for i in range(N): s.add(v[1<<i]==0)
    s.add(v[FULL]==1)
    for S in range(1,FULL+1):
        s.add(v[S] <= F(O.sz(S)-(1 if S>>J&1 else 0),4))
        s.add(4*v[S] <= O.sz(S))
        s.add(v[S] <= mu*len([i for i in L if S>>i&1]) + rho*len([i for i in R if S>>i&1]))
    s.add(v[Sstar]==F(O.sz(Sstar),4))
    s.add(mu == 1 - v[FULL^(1<<J)]); s.add(mu > 0); s.add(mu < F(1,8))
    if extra: extra(s, v, mu)
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
        if bad is None: return vv, val(mu)
        s.add(z3.Sum([z3.RealVal(bad[S])*v[S] for S in range(1,32) if bad[S]])<=0)
    raise RuntimeError("budget")

def audit_model(vv, mu, tag):
    print(f"\n=== {tag}:  mu = {mu} ===")
    print("  v =", [str(q) for q in vv])
    assert all(vv[1<<i]==0 for i in range(N)), "not singleton-normalized"
    ex = audit.is_exact(N, vv)
    print("  exact (independent vertex-enumeration check):", ex)
    if not ex:
        print("  -> the LP model is NOT an exact game; the 280 inequalities were")
        print("     satisfied, so this would contradict the cone description")
        return {"tag":tag,"exact":ex}
    phi = audit.lmin(N, vv); psi = lmaxmod.lmax(N, vv)
    T = vv[FULL]
    fj = T - vv[FULL^(1<<J)]
    st = lambda p: [len(b) for b in audit.strata(p)]
    print("  Lmin =", [str(q) for q in phi], " strata", st(phi))
    print("  Lmax =", [str(q) for q in psi], " strata", st(psi))
    print(f"  f({{j}}) = {fj},  T/8 = {F(T,8)},  (*) holds: {fj >= F(T,8)}")
    cfg = (sorted(st(phi))==[2,3] and sorted(st(psi))==[1,4] and min(psi)==0
           and len(audit.strata(phi)[0])==3)
    print("  in CFG:", cfg)
    if not cfg:
        print("  -> CERTIFICATE NOT REALIZABLE: the LP's x0 is not the leximin point")
        print("     (min Lmin =", str(min(phi)), "vs the LP's mu =", str(mu), ")")
    return {"tag":tag,"exact":ex,"lmin":[str(q) for q in phi],"lmax":[str(q) for q in psi],
            "lmin_strata":st(phi),"lmax_strata":st(psi),"f_j":str(fj),"mu_LP":str(mu),
            "star_holds": fj>=F(T,8), "in_CFG":cfg}

out=[]
for name in ("de","bde","cde"):
    Sstar = sum(1<<"abcde".index(ch) for ch in name)
    got = prog(Sstar)
    if got is None:
        print(f"{name}: infeasible"); continue
    vv, mu = got
    out.append(audit_model(vv, mu, f"S*={name}"))
json.dump(out, open(f"{SCR}/sel/o2/extract.json","w"), indent=1)
