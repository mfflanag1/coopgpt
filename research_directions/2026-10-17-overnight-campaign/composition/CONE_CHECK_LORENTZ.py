#!/usr/bin/env python3
"""Exact rational Lorentz-order and incentive certificates. Run without -O."""
from fractions import Fraction as F
from itertools import product
from math import isqrt
from pathlib import Path
import json, random

rng = random.Random(202610170748)
counts = dict(order_profiles=0, order_coefficients=0, grand_excess_bounds=0,
              exact_payment_profiles=0, coalition_coverage=0, individual_out=0,
              sharp_rule_examples=0, non_euclidean_obstructions=0)
def dot(a,b): return sum((x*y for x,y in zip(a,b)),F(0))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def scale(a,c): return tuple(c*x for x in a)
def neg(a): return scale(a,F(-1))
def sub(a,b): return add(a,neg(b))
def sumv(xs,d):
    ans=(F(0),)*d
    for x in xs: ans=add(ans,x)
    return ans
def root(q):
    a,b=isqrt(q.numerator),isqrt(q.denominator)
    if a*a!=q.numerator or b*b!=q.denominator: raise ValueError('irrational test norm')
    return F(a,b)
def norm(x): return root(dot(x,x))
def K(b): return b[0]>=0 and b[0]*b[0]>=dot(b[1:],b[1:])
def worth(b): return b[0]-norm(b[1:])
def pays(bs):
    C=sumv(bs,len(bs[0])); T=worth(C)
    return [T-worth(sub(C,b)) for b in bs]
def nonnegative_radical(a,b,s):
    assert b>=0 and s>=0
    return a>=0 or b*b*s>=a*a

# General rational boundary rays in dimensions 2 through 21. No floating point.
for d in range(1,21):
  for trial in range(70):
    n=rng.randrange(2,10); xs=[]; rs=[]
    for i in range(n):
      q=tuple(F(rng.randrange(-4,5),rng.randrange(1,6)) for _ in range(d-1))
      Q=dot(q,q)
      v=( (1-Q)/(1+Q), )+tuple(2*z/(1+Q) for z in q)
      r=F(rng.randrange(0,7),rng.randrange(1,5))
      x=scale(v,r)
      assert dot(x,x)==r*r
      xs.append(x);rs.append(r)
    R=sum(rs,F(0)); X=sumv(xs,d); s=dot(X,X); delta=R*R-s
    assert delta>=0
    if delta==0: continue
    alphas=[]
    for r,x in zip(rs,xs):
      alpha=2*(R*r-dot(X,x))/delta
      assert 0<=alpha<=1
      A=alpha*R-r; Y=sub(scale(X,alpha),x)
      assert A>=0 and A*A==dot(Y,Y)
      # Exact squared form of ||X-x|| <= alpha R-r+(1-alpha)||X||.
      target=sub(X,x)
      aa=A*A+(1-alpha)**2*s-dot(target,target)
      bb=2*A*(1-alpha)
      assert nonnegative_radical(aa,bb,s)
      alphas.append(alpha)
      counts['order_coefficients']+=1;counts['grand_excess_bounds']+=1
    assert sum(alphas,F(0))==2
    counts['order_profiles']+=1

# Noncollinear rational triangle: every coalition norm is rational.
rays=[(F(1),F(0)),(F(-7,25),F(24,25)),(F(-7,25),F(-24,25))]
for fs in product([F(0),F(1,3),F(1)],repeat=3):
  for extension in [0,1,5,11]:
    bs=[(F(1)+f,)+x+(F(0),)*extension for f,x in zip(fs,rays)]
    n=len(bs); d=len(bs[0]); C=sumv(bs,d); ys=pays(bs)
    S=sum((worth(b) for b in bs),F(0));G=worth(C)-S
    assert sum(ys,F(0))<=S+2*G
    counts['exact_payment_profiles']+=1
    for mask in range(1<<n):
      inds=[i for i in range(n) if mask>>i&1]
      assert sum((ys[i] for i in inds),F(0))>=worth(sumv([bs[i] for i in inds],d))
      counts['coalition_coverage']+=1
    for i in range(n):
      withdrawals=[bs[i],(fs[i],)+(F(0),)*(d-1),(F(1),)+bs[i][1:]]
      for w in withdrawals:
        assert K(w) and K(sub(bs[i],w))
        changed=bs.copy();changed[i]=sub(bs[i],w)
        assert ys[i]-pays(changed)[i]>=worth(w)
        counts['individual_out']+=1

bs=[(F(1),F(1)),(F(1),F(-1))]
assert sum(pays(bs))==2*worth(sumv(bs,2))==4
counts['sharp_rule_examples']+=1

# Infinity norm counterexample is exact and not a lower bound for all rules.
bs=[(1,1,1,1),(1,1,-1,-1),(1,-1,1,-1)]
def winf(b): return b[0]-max(abs(x) for x in b[1:])
C=sumv(bs,4);T=winf(C)
y=[T-winf(sub(C,b)) for b in bs]
assert T==2 and all(winf(b)==0 for b in bs) and sum(y)==6
counts['non_euclidean_obstructions']+=1

out={'status':'PASS','arithmetic':'fractions.Fraction and exact integer square roots',
     'counts':counts,'scope':'Exact finite certificates supplement the all-real analytic proof; no numerical tolerances.'}
Path(__file__).with_name('CONE_LORENTZ_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
