"""Exact algebraic outputs for common-cap k-private-input TCWM mechanisms."""
from fractions import Fraction as Q
from dataclasses import dataclass

def integer_root(n,k):
    if n<0 or k<1: raise ValueError('nonnegative n and positive k required')
    if n<2 or k==1:return n
    lo,hi=0,1<<((n.bit_length()+k-1)//k)
    while lo+1<hi:
        m=(lo+hi)//2
        if m**k<=n:lo=m
        else:hi=m
    return hi if hi**k==n else lo

def root_interval(q,k,bits):
    scale=1<<bits
    n=integer_root(q.numerator*scale**k//q.denominator,k)
    lo=Q(n,scale)
    if n**k*q.denominator==q.numerator*scale**k:return lo,lo
    return lo,Q(n+1,scale)

@dataclass(frozen=True)
class Radical:
    a: Q=Q(0)
    b: Q=Q(0)
    q: Q=Q(0)
    k: int=1
    def compare(self,other):
        if not isinstance(other,Radical):other=Radical(Q(other))
        a=self.a-other.a;b=self.b;d=-other.b;q=self.q;r=other.q
        k=self.k if b and q else other.k
        if b and q and d and r and self.k!=other.k:raise ValueError('same radical degree required')
        if not b or not q:b=Q(0)
        if not d or not r:d=Q(0)
        if b and d and q==r:b+=d;d=Q(0)
        if not a:
            if not b and not d:return 0
            if b>=0 and d>=0:return 1
            if b<=0 and d<=0:return -1
            # Opposite-sign positive roots: kth powers preserve order.
            val=abs(b)**k*q-abs(d)**k*r
            return ((val>0)-(val<0))*((b>0)-(b<0))
        if not d:
            if not b:return (a>0)-(a<0)
            if (a>0)==(b>0):return (a>0)-(a<0)
            val=abs(a)**k-abs(b)**k*q
            return ((val>0)-(val<0))*((a>0)-(a<0))
        if not b:
            return Radical(a,d,r,k).compare(0)
        for bits in (8,16,32,64,128,256,512,1024):
            lo=hi=a
            for coef,rad in ((b,q),(d,r)):
                x,y=root_interval(rad,k,bits)
                lo+=coef*(x if coef>0 else y);hi+=coef*(y if coef>0 else x)
            if lo>0:return 1
            if hi<0:return -1
        raise ArithmeticError('uncertified two-root comparison; equality oracle not implemented')

def parameter(M,k):
    if M<1 or k<1:raise ValueError('positive branch count and private arity required')
    target=k**(2*k)*M**(k-1)
    scale=(k+1)**(k+1)
    lo,hi=1,1
    while scale*hi**(2*k)<target:hi*=2
    while lo<hi:
        m=(lo+hi)//2
        if scale*m**(2*k)>=target:hi=m
        else:lo=m+1
    return Q(lo)

def production(c,k):
    c=list(map(Q,c))
    return min(c[0],sum(min(c[j:j+k]) for j in range(1,len(c),k)))

def coalition_payment(c,s,k,C=None):
    c=list(map(Q,c));s=list(map(Q,s))
    if k<1 or len(c)<k+1 or (len(c)-1)%k or len(s)!=len(c):raise ValueError('P followed by k-tuples required')
    if any(x<0 or y<0 or y>x for x,y in zip(c,s)):raise ValueError('0<=s<=c required')
    M=(len(c)-1)//k;C=parameter(M,k) if C is None else Q(C)
    if C<1:raise ValueError('public C>=1 required')
    P=c[0];gs=[min(P/C,*c[j:j+k]) for j in range(1,len(c),k)];G=sum(gs)
    if not P or not G:return Radical(k=k)
    h=min(Q(1),C*G/P);Z=Q(0)
    for index,g in enumerate(gs):
        for v in range(1+index*k,1+(index+1)*k):
            if c[v]:Z+=g*s[v]/c[v]
    rad=Q(k**k)*P/((k+1)**(k+1)*C*G)
    if rad>=1:return Radical(s[0]*h+Z,k=k)
    return Radical(s[0]*h,Z,rad,k)
