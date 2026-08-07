"""Sharpened arithmetic bound.  The anchors are TIGHT on both sides.

nu = M attained at S0:  z in Core gives z(S0) >= v(S0) = M|S0|, while z_i <= M
     forces z(S0) <= M|S0|.  Hence z_i = M for every i in S0: S0 sits inside
     the TOP stratum of Lmax.  And x in Core gives x(S0) >= M|S0|.
lambda = mu attained at S1:  x in Core gives x(S1) <= f(S1) = mu|S1|, while
     x_i >= mu forces x(S1) >= mu|S1|.  Hence x_i = mu on S1: S1 sits inside
     the BOTTOM stratum of Lmin.  And z(S1) <= f(S1) = mu|S1|.

So, with no game data at all:
   exists S0:  z|S0 == M  and  x(S0) >= M|S0|
   exists S1:  x|S1 == mu and  z(S1) <= mu|S1|
plus x,z >= 0, x(N) = z(N) = 1, x >= mu, z <= M.
"""
from __future__ import annotations
import itertools, json, sys
from fractions import Fraction as F
import z3

def val_of(o, h):
    up = o.upper(h)
    if str(up) in ("oo", "-oo"):
        return None
    e = z3.simplify(up)
    if z3.is_int_value(e): return F(e.as_long())
    if z3.is_rational_value(e): return F(e.numerator_as_long(), e.denominator_as_long())
    return None

def run(n, extra_leximin=False):
    FULL = (1 << n) - 1
    best = (F(0), None)
    for S0 in range(1, FULL + 1):
        for S1 in range(1, FULL + 1):
            for sgn in itertools.product((1, -1), repeat=n):
                x = [z3.Real(f"x{i}") for i in range(n)]
                z = [z3.Real(f"z{i}") for i in range(n)]
                mu, M = z3.Real("mu"), z3.Real("M")
                o = z3.Optimize()
                for i in range(n):
                    o.add(x[i] >= 0, z[i] >= 0, x[i] >= mu, z[i] <= M)
                    o.add(sgn[i]*(x[i]-z[i]) >= 0)
                    if S0 >> i & 1: o.add(z[i] == M)
                    if S1 >> i & 1: o.add(x[i] == mu)
                o.add(z3.Sum(x) == 1, z3.Sum(z) == 1)
                a0 = [i for i in range(n) if S0 >> i & 1]
                a1 = [i for i in range(n) if S1 >> i & 1]
                o.add(z3.Sum([x[i] for i in a0]) >= M*len(a0))
                o.add(z3.Sum([z[i] for i in a1]) <= mu*len(a1))
                h = o.maximize(z3.Sum([sgn[i]*(x[i]-z[i]) for i in range(n)]))
                if o.check() != z3.sat: continue
                v = val_of(o, h)
                if v is not None and v > best[0]:
                    m = o.model()
                    best = (v, {"S0": a0, "S1": a1,
                                "x": [str(m.eval(x[i], model_completion=True)) for i in range(n)],
                                "z": [str(m.eval(z[i], model_completion=True)) for i in range(n)],
                                "mu": str(m.eval(mu, model_completion=True)),
                                "M": str(m.eval(M, model_completion=True))})
    return best

if __name__ == "__main__":
    for n in (4, 5, 6):
        v, w = run(n)
        print(f"n={n}: sharpened arithmetic bound on the ratio = {v}")
        if n == 5: print("   witness:", json.dumps(w))
        json.dump({"n": n, "bound": str(v), "witness": w},
                  open(f"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/"
                       f"scratchpad/sel/s5full/arith2_n{n}.json","w"), indent=1)
