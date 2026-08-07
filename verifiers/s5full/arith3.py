"""Sharpened arithmetic bound -- float screen, exact confirmation of the top.

Variables: x_0..x_{n-1}, z_0..z_{n-1}, mu, M   (2n+2 unknowns)
Constraints (all consequences of A3 + core membership of both vectors, with NO
game data):
   x,z >= 0 ; x(N) = z(N) = 1 ; x_i >= mu ; z_i <= M
   z_i = M for i in S0 ;  x(S0) >= M|S0|
   x_i = mu for i in S1 ;  z(S1) <= mu|S1|
Objective: maximise sum_i sgn_i (x_i - z_i) with sgn_i (x_i - z_i) >= 0.
"""
from __future__ import annotations
import itertools, json, sys
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import z3

def lp(n, S0, S1, sgn):
    nv = 2*n + 2
    xi = lambda i: i
    zi = lambda i: n + i
    MU, MM = 2*n, 2*n+1
    Aub, bub, Aeq, beq = [], [], [], []
    def row():
        return [0.0]*nv
    for i in range(n):
        r = row(); r[xi(i)] = -1.0; r[MU] = 1.0; Aub.append(r); bub.append(0.0)   # x_i >= mu
        r = row(); r[zi(i)] = 1.0; r[MM] = -1.0; Aub.append(r); bub.append(0.0)   # z_i <= M
        r = row(); r[xi(i)] = -sgn[i]; r[zi(i)] = sgn[i]; Aub.append(r); bub.append(0.0)
        if S0 >> i & 1:
            r = row(); r[zi(i)] = 1.0; r[MM] = -1.0; Aeq.append(r); beq.append(0.0)
        if S1 >> i & 1:
            r = row(); r[xi(i)] = 1.0; r[MU] = -1.0; Aeq.append(r); beq.append(0.0)
    r = row()
    for i in range(n): r[xi(i)] = 1.0
    Aeq.append(r); beq.append(1.0)
    r = row()
    for i in range(n): r[zi(i)] = 1.0
    Aeq.append(r); beq.append(1.0)
    a0 = [i for i in range(n) if S0 >> i & 1]; a1 = [i for i in range(n) if S1 >> i & 1]
    r = row()
    for i in a0: r[xi(i)] = -1.0
    r[MM] = float(len(a0)); Aub.append(r); bub.append(0.0)                        # x(S0) >= M|S0|
    r = row()
    for i in a1: r[zi(i)] = 1.0
    r[MU] = -float(len(a1)); Aub.append(r); bub.append(0.0)                       # z(S1) <= mu|S1|
    c = row()
    for i in range(n):
        c[xi(i)] = -float(sgn[i]); c[zi(i)] = float(sgn[i])
    bounds = [(0, None)]*(2*n) + [(None, None)]*2
    res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub),
                  A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=bounds, method="highs")
    if not res.success:
        return None
    return -res.fun, res.x

def exact_max(n, S0, S1, sgn):
    x=[z3.Real(f"x{i}") for i in range(n)]; z=[z3.Real(f"z{i}") for i in range(n)]
    mu,M=z3.Real("mu"),z3.Real("M"); o=z3.Optimize()
    for i in range(n):
        o.add(x[i]>=0,z[i]>=0,x[i]>=mu,z[i]<=M,sgn[i]*(x[i]-z[i])>=0)
        if S0>>i&1: o.add(z[i]==M)
        if S1>>i&1: o.add(x[i]==mu)
    o.add(z3.Sum(x)==1,z3.Sum(z)==1)
    a0=[i for i in range(n) if S0>>i&1]; a1=[i for i in range(n) if S1>>i&1]
    o.add(z3.Sum([x[i] for i in a0])>=M*len(a0))
    o.add(z3.Sum([z[i] for i in a1])<=mu*len(a1))
    h=o.maximize(z3.Sum([sgn[i]*(x[i]-z[i]) for i in range(n)]))
    if o.check()!=z3.sat: return None,None
    up=o.upper(h)
    if str(up) in ("oo","-oo"): return None,None
    e=z3.simplify(up)
    v=F(e.as_long()) if z3.is_int_value(e) else F(e.numerator_as_long(),e.denominator_as_long())
    m=o.model()
    return v, {"x":[str(m.eval(x[i],model_completion=True)) for i in range(n)],
               "z":[str(m.eval(z[i],model_completion=True)) for i in range(n)],
               "mu":str(m.eval(mu,model_completion=True)),"M":str(m.eval(M,model_completion=True))}

def run(n):
    FULL=(1<<n)-1
    cands=[]
    for S0 in range(1,FULL+1):
        for S1 in range(1,FULL+1):
            for sgn in itertools.product((1,-1),repeat=n):
                r=lp(n,S0,S1,sgn)
                if r is None: continue
                cands.append((r[0],S0,S1,sgn))
    cands.sort(reverse=True)
    top=cands[0][0]
    best=(F(0),None)
    for v,S0,S1,sgn in cands:
        if v < top-1e-7: break
        ev,wit=exact_max(n,S0,S1,sgn)
        if ev is not None and ev>best[0]:
            best=(ev,{"S0":[i for i in range(n) if S0>>i&1],
                      "S1":[i for i in range(n) if S1>>i&1],**wit})
    return best, top, len(cands)

if __name__=="__main__":
    for n in (4,5,6):
        (v,w),top,cnt=run(n)
        print(f"n={n}: {cnt} feasible LPs, float max {top:.6f}, EXACT bound = {v}")
        if w: print("   witness:", json.dumps(w))
        json.dump({"n":n,"bound":str(v),"witness":w},
                  open(f"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/"
                       f"scratchpad/sel/s5full/arith3_n{n}.json","w"),indent=1)
