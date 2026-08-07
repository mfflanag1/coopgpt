"""CONTROL: on genuine CFG games, does some vertex of D_L certify the pinning?

If no vertex ever did, the main program would be infeasible for a vacuous
reason and would prove nothing.  Harvest real CFG games, relabel so that
j = 0 and L = {0,1,2}, R = {3,4}, and check
  (i)  directly, by LP, that max{x(L) : x in Core, x >= mu*1} = 3*mu (pinning);
  (ii) that some vertex (alpha,beta) of D_L has c*alpha + sum beta_S f'(S) <= 0.
Both must hold; (ii) is the encoding used by o2main.py.
"""
import json, random, sys
from fractions import Fraction as F
import z3
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/o2")
import audit, lmax as lmaxmod
from o2main import load_pinverts, sz

N=5; FULL=31
pins = load_pinverts()

def check_game(w):
    x = audit.lmin(N,w); z = lmaxmod.lmax(N,w)
    sx=[len(b) for b in audit.strata(x)]; sz_=[len(b) for b in audit.strata(z)]
    if not (sx==[3,2] and sorted(sz_)==[1,4] and min(z)==0): return None
    T=w[FULL]; js=[i for i in range(N) if z[i]==0]
    if len(js)!=1: return None
    j=js[0]; mu=min(x)
    if x[j]!=mu: return None                       # j must be poor
    Lset=[i for i in range(N) if x[i]==mu]; Rset=[i for i in range(N) if x[i]!=mu]
    if len(Lset)!=3: return None
    perm=[j]+[i for i in Lset if i!=j]+Rset        # relabel: j=0, L={0,1,2}, R={3,4}
    inv={p:k for k,p in enumerate(perm)}
    wp=[F(0)]*(32)
    for S in range(32):
        Sp=sum(1<<inv[i] for i in range(N) if S>>i&1)
        wp[Sp]=w[S]
    T=F(T); mu=F(mu)
    # scale to T = 1
    wp=[q/T for q in wp]; mu=mu/T
    f  = lambda S: 1 - wp[FULL^S]
    fp = lambda S: f(S) - mu*sz(S)
    c  = 1 - 5*mu
    # (i) direct LP: max x(L) subject to x in Core, x >= mu
    xv=[z3.Real(f"x{i}") for i in range(N)]
    o=z3.Optimize()
    o.add(z3.Sum(xv)==z3.RealVal(1))
    for S in range(1,FULL):
        o.add(z3.Sum([xv[i] for i in range(N) if S>>i&1]) >= audit.to_z3(wp[S]))
    for i in range(N): o.add(xv[i] >= audit.to_z3(mu))
    h=o.maximize(z3.Sum([xv[i] for i in range(3)]))
    assert o.check()==z3.sat
    pinned_direct = (audit.rat(o.upper(h)) == 3*mu)
    # (ii) certificate among the 354 vertices
    best=None
    for al,be in pins:
        obj = c*al + sum(x*fp(S) for S,x in be)
        if best is None or obj < best[0]: best=(obj,al,be)
    cert = best[0] <= 0
    return {"mu":str(mu),"f_j":str(f(1)),"pinned_direct":pinned_direct,
            "certificate_exists":cert,"best_obj":str(best[0])}

rng=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 3)
found=[]; tried=0
while len(found)<8 and tried<3000:
    tried+=1
    tot=rng.choice([4,5,6,8,12,16])
    gens=audit.rand_gens(N,rng,rng.randint(2,6),tot,tot)
    v=audit.envelope(N,gens); w,_=audit.normalize(N,v)
    if w[FULL]==0: continue
    r=check_game(w)
    if r: found.append(r); print("  CFG game:", r, flush=True)
print(f"\n{len(found)} CFG games examined ({tried} draws)")
print("  pinning true (direct LP) in", sum(r['pinned_direct'] for r in found))
print("  certificate found among the 354 vertices in", sum(r['certificate_exists'] for r in found))
json.dump(found, open(f"{SCR}/sel/o2/pincontrol.json","w"), indent=1)
