from fractions import Fraction as F
from itertools import product, permutations
import json, random, sys, time
from pathlib import Path
import z3

OUT = Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)

def frac(v):
    if z3.is_int_value(v): return F(v.as_long())
    if not z3.is_rational_value(v): raise RuntimeError(f'Nonfinite optimum {v}')
    return F(v.numerator_as_long(), v.denominator_as_long())

def solve(edges, matrices, m, k=4, known_T=None):
    teams=list(product(range(m),repeat=k))
    w={t:sum(A[t[a]][t[b]] for (a,b),A in zip(edges,matrices)) for t in teams}
    if known_T is None:
        perms=list(permutations(range(m)))
        T=max(sum(w[(i,)+tuple(p[i] for p in pp)] for i in range(m)) for pp in product(perms,repeat=k-1))
    else:
        T=known_T
    if T==0:return None
    p=[z3.Real(f'p{i}') for i in range(k*m)]
    raw=[v>=0 for v in p]+[z3.Sum(p)==T]
    raw += [z3.Sum([p[s*m+t[s]] for s in range(k)])>=val for t,val in w.items()]
    s=z3.Solver();s.add(raw)
    if s.check()!=z3.sat:return None
    def opt(expr,cons):
        o=z3.Optimize();o.set(timeout=15000);o.add(cons);h=o.maximize(expr)
        if o.check()!=z3.sat:raise RuntimeError('Optimization failed')
        return frac(o.lower(h))
    face=list(raw);left=set(range(k*m));x=[None]*(k*m);levels=[]
    while left:
        t=z3.Real('floor');val=opt(t,face+[p[i]>=t for i in left]);q=z3.Q(val.numerator,val.denominator)
        face += [p[i]>=q for i in left]
        forced=[]
        for i in sorted(left):
            s=z3.Solver();s.set(timeout=15000);s.add(face+[p[i]>q]);r=s.check()
            if r==z3.unsat:forced.append(i)
            elif r!=z3.sat:raise RuntimeError('Unknown face')
        if not forced:raise RuntimeError('No forced coordinates')
        for i in forced:x[i]=val;left.remove(i);face.append(p[i]==q)
        levels.append({'value':str(val),'players':forced})
    H=[opt(v,raw) for v in p]
    ratio=min(a/b for a,b in zip(x,H) if b)
    return {'edges':edges,'matrices':matrices,'m':m,'k':k,'T':T,'x':list(map(str,x)),'H':list(map(str,H)),'ratio':str(ratio),'levels':levels}
