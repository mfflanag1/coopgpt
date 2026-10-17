#!/usr/bin/env python3
"""Exact symbolic quarter-power common-cap TCWM rule. Outputs a+b*sqrt(q), never rounded payments."""
from fractions import Fraction as Q
from dataclasses import dataclass
from math import isqrt

def signq(x): return (x>0)-(x<0)
def sign_one(a,b,q):
    if not b or not q:return signq(a)
    if not a:return signq(b)
    if signq(a)==signq(b):return signq(a)
    t=a*a-b*b*q
    return signq(a)*signq(t)
def zero_two(a,b,q,d,r):
    if not b or not q:return sign_one(a,d,r)==0
    if not d or not r:return sign_one(a,b,q)==0
    if not a:return signq(b)==-signq(d) and b*b*q==d*d*r
    e=a*a+b*b*q-d*d*r
    if e*e!=4*a*a*b*b*q or signq(e)!=signq(-2*a*b):return False
    return sign_one(a,b,q)==-signq(d)
def sqrt_interval(q,bits):
    if not q:return Q(0),Q(0)
    scale=1<<bits
    k=isqrt((q.numerator*scale*scale)//q.denominator)
    lo=Q(k,scale)
    if k*k*q.denominator==q.numerator*scale*scale:return lo,lo
    return lo,Q(k+1,scale)
def sign_two(a,b,q,d,r):
    if zero_two(a,b,q,d,r):return 0
    for bits in [8,16,32,64,128,256,512,1024,2048]:
        lo=hi=a
        for coef,rad in [(b,q),(d,r)]:
            x,y=sqrt_interval(rad,bits)
            lo+=coef*(x if coef>=0 else y);hi+=coef*(y if coef>=0 else x)
        if lo>0:return 1
        if hi<0:return -1
    raise ArithmeticError('exact algebraic sign unresolved within interval guard; no approximate comparison returned')
@dataclass(frozen=True)
class Quadratic:
    constant: Q=Q(0)
    coefficient: Q=Q(0)
    radicand: Q=Q(0)
    def scale(self,t):return Quadratic(self.constant*t,self.coefficient*t,self.radicand)
    def compare(self,other):
        if not isinstance(other,Quadratic):other=Quadratic(Q(other))
        return sign_two(self.constant-other.constant,self.coefficient,self.radicand,-other.coefficient,other.radicand)
    def as_dict(self):return {'constant':str(self.constant),'sqrt_coefficient':str(self.coefficient),'radicand':str(self.radicand)}

def parameter(M):
    if not isinstance(M,int) or M<1:raise ValueError('positive integer branch count required')
    # Exact integer public parameter: smallest C>=1 with27 C^4>=16M.
    lo,hi=1,1
    while 27*hi**4<16*M:hi*=2
    while lo<hi:
        mid=(lo+hi)//2
        if 27*mid**4>=16*M:hi=mid
        else:lo=mid+1
    return Q(lo)

def coalition_payment(capacities,holdings,C=None):
    c=list(map(Q,capacities));s=list(map(Q,holdings))
    if len(c)<3 or len(c)%2!=1 or len(s)!=len(c):raise ValueError('P,a1,b1,... dimensions required')
    if any(v<0 for v in c) or any(x<0 or x>v for x,v in zip(s,c)):raise ValueError('0<=holdings<=capacities required')
    M=(len(c)-1)//2;C=parameter(M) if C is None else Q(C)
    if C<1:raise ValueError('public C must be>=1')
    P=c[0];g=[min(P/C,c[2*j+1],c[2*j+2]) for j in range(M)];G=sum(g)
    if not P or not G:return Quadratic()
    h=min(Q(1),C*G/P)
    z=Q(0)
    for j,gj in enumerate(g):
        for v in [2*j+1,2*j+2]:
            if c[v]:z+=gj*s[v]/c[v]
    rad=4*P/(27*C*G)
    if rad>=1:return Quadratic(s[0]*h+z)
    return Quadratic(s[0]*h,z,rad)

def production(capacities):
    c=list(map(Q,capacities));return min(c[0],sum(min(c[j],c[j+1]) for j in range(1,len(c),2)))

def owner_payments(bundles,C=None):
    if not bundles:raise ValueError('at least one fixed owner required')
    d=len(bundles[0])
    if any(len(b)!=d for b in bundles):raise ValueError('all owner bundles need same dimensions')
    bs=[list(map(Q,b)) for b in bundles]
    if any(v<0 for b in bs for v in b):raise ValueError('nonnegative owner reports required')
    caps=[sum(b[v] for b in bs) for v in range(d)]
    return [coalition_payment(caps,b,C) for b in bs]
