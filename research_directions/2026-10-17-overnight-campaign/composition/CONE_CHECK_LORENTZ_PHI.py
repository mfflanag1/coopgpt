#!/usr/bin/env python3
"""Exact certificates over Q(c), c^2+c=1 and c>0. No numerical tolerances."""
from fractions import Fraction as F
from itertools import product
from math import isqrt
from pathlib import Path
import json

class Q:
    __slots__=('a','b')
    def __init__(self,a=0,b=0):
        if isinstance(a,Q): self.a,self.b=a.a,a.b
        else: self.a,self.b=F(a),F(b)
    def __add__(self,o):
        o=Q(o);return Q(self.a+o.a,self.b+o.b)
    __radd__=__add__
    def __neg__(self):return Q(-self.a,-self.b)
    def __sub__(self,o):return self+-Q(o)
    def __rsub__(self,o):return Q(o)+-self
    def __mul__(self,o):
        o=Q(o);return Q(self.a*o.a+self.b*o.b,self.a*o.b+self.b*o.a-self.b*o.b)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=Q(o);norm=o.a*o.a-o.a*o.b-o.b*o.b
        assert norm
        return self*Q((o.a-o.b)/norm,-o.b/norm)
    def __rtruediv__(self,o):return Q(o)/self
    def __pow__(self,n):
        if n<0:return (Q(1)/self)**(-n)
        out=Q(1)
        for _ in range(n):out=out*self
        return out
    def sign(self):
        # 2(a+b c)=(2a-b)+b sqrt(5).
        A=2*self.a-self.b;B=self.b
        if B==0:return (A>0)-(A<0)
        if B>0:
            if A>=0:return 1
            return (5*B*B>A*A)-(5*B*B<A*A)
        if A<=0:return -1
        return (A*A>5*B*B)-(A*A<5*B*B)
    def __eq__(self,o):o=Q(o);return self.a==o.a and self.b==o.b
    def __ge__(self,o):return (self-Q(o)).sign()>=0
    def __gt__(self,o):return (self-Q(o)).sign()>0
    def __le__(self,o):return (self-Q(o)).sign()<=0
    def __lt__(self,o):return (self-Q(o)).sign()<0

c=Q(0,1);b=1-c;phi=1+c
assert c*c+c==1 and c>F(1,2) and 7-11*c>0 and 2-3*c>0
counts=dict(radial_slack=0,vertex_location=0,endpoint_factorizations=0,
            profiles=0,coverage=0,coalition_transitions=0,budget=0,
            outside_failure=0,gain_only_failure=0)
for si in range(1,100):
    s=F(si,100);D=c+b*s;a=s/D;ap=c/D**2
    A2=(1+s)*(D**2-c*c)
    A1=-4*s*c*b*D-2*c*c*s*(1+s)
    A0=4*c*D**2*(D+s)-4*s*s*c*b*D-c*c*(1+s)*s*s-D**2*(1+s)
    assert A2>0 and -(A1)/(2*A2)>=1
    assert c*(2*b*D+c*(1+s))-(1+s)*b*(D+c)==(1-s)*((7-11*c)+(2-3*c)*s)
    counts['vertex_location']+=1
    for qi in range(-20,21):
        q=F(qi,20);h=(s+q)/2;w2=(1-s*s)*(1-q*q)/4
        At=1+s*ap*h
        slack=At**2-(a+ap*h)**2-(a/s)**2*w2
        assert At>0 and slack>=0
        assert A2*q*q+A1*q+A0==4*(1+s)*D**4*slack/(1-s*s)
        counts['radial_slack']+=1
    h=(1+s)/2
    assert 1+s*ap*h-a-ap*h==c*(c-F(1,2))*(1-s)**2/D**2
    counts['endpoint_factorizations']+=1

def dot(x,y):return sum((a*b for a,b in zip(x,y)),F(0))
def add(x,y):return tuple(a+b for a,b in zip(x,y))
def scale(x,k):return tuple(a*k for a in x)
def sub(x,y):return add(x,scale(y,-1))
def sumv(xs,d):
    ans=(F(0),)*d
    for x in xs:ans=add(ans,x)
    return ans
def root(v):
    a,bb=isqrt(v.numerator),isqrt(v.denominator)
    assert a*a==v.numerator and bb*bb==v.denominator
    return F(a,bb)
def norm(x):return root(dot(x,x))
def val(x):return x[0]-norm(x[1:])
def pay(bs):
    C=sumv(bs,len(bs[0]));T=C[0];X=C[1:];R=norm(X)
    if not T:return [Q(0) for _ in bs]
    return [Q(z[0])-dot(z[1:],X)/(c*T+b*R) for z in bs]
rays=[(F(1),F(0)),(F(-7,25),F(24,25)),(F(-7,25),F(-24,25))]
for fs in product([F(0),F(1,3),F(1)],repeat=3):
  for ext in [0,4,13]:
    full=[(1+f,)+x+(F(0),)*ext for f,x in zip(fs,rays)]
    n=3;d=len(full[0]);zero=(F(0),)*d
    bymask={}
    for mask in range(1<<n):
      bs=[full[i] if mask>>i&1 else zero for i in range(n)]
      ys=pay(bs);bymask[mask]=ys;C=sumv(bs,d)
      assert all(y>=0 for y in ys)
      assert sum(ys,Q(0))<=phi*val(C)
      counts['profiles']+=1;counts['budget']+=1
      for coal in range(1<<n):
        inds=[i for i in range(n) if coal>>i&1]
        assert sum((ys[i] for i in inds),Q(0))>=val(sumv([bs[i] for i in inds],d))
        counts['coverage']+=1
    for low in range(1<<n):
      for high in range(1<<n):
        if low&high!=low:continue
        changed=high^low
        for coal in range(1<<n):
          if coal&changed!=changed:continue
          assert sum((bymask[high][i]-bymask[low][i] for i in range(n) if coal>>i&1),Q(0))>=0
          counts['coalition_transitions']+=1

old=[(F(1),F(-1)),(F(3),F(2))]
new=[(F(2),F(-1)),(F(3),F(2))]
change=pay(new)[0]-pay(old)[0]
assert change==1+1/(1+4*c)-1/(1+3*c) and 0<=change<1
counts['outside_failure']+=1
single=[(F(2),F(1))]
assert pay(single)[0]>val(single[0])
counts['gain_only_failure']+=1
out={'status':'PASS','arithmetic':'exact quadratic field Q((sqrt(5)-1)/2), Fraction and integer square roots','counts':counts,
     'scope':'Exact finite derivative and transition certificates supplement the all-profile proof; no floating-point tolerance.'}
Path(__file__).with_name('CONE_LORENTZ_PHI_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
