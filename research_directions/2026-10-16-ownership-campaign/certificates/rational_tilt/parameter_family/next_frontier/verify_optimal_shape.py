#!/usr/bin/env python3
"""Certified rational intervals and exact linear-in-kappa finite diagnostics.
No floating constant enters a payment, branch choice, or validation.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from random import Random
import json

BASE=Path(__file__).parent
COUNTS=dict(profiles=0,coalitions=0,own_comparisons=0,balance_checks=0,
            critical_checks=0,attainers=0,ceiling_equalities=0)

def require(ok,message):
    if not ok:raise RuntimeError(message)

def T(s):return 53*s**3-91*s*s+55*s-12

def J(s):return 68*s**5-235*s**4+308*s**3-199*s*s+64*s-8

def C(s):return s*s/(8*(1-s)*(2*s-1))-Q(1,2)

def dC(s):return (C(s)+Q(1,2))*(3*s-2)/(s*(1-s)*(2*s-1))

def F(s):return Q(1,8) if s<=Q(1,2) else (1+s)**3/(54*s)

def gc(s):return (1-2*C(s))*F(s)

TAU_LO,TAU_HI=Q(17,25),Q(683,1000)
for _ in range(180):
    mid=(TAU_LO+TAU_HI)/2
    if T(mid)<0:TAU_LO=mid
    else:TAU_HI=mid
require(T(TAU_LO)<0<T(TAU_HI),'tau isolation')
K_LO,K_HI=dC(TAU_LO),dC(TAU_HI)
require(Q(1,4)<K_LO<K_HI<Q(5,16),'kappa bounds')
RHO_LO,RHO_HI=Q(2,3),Q(27,40)
for _ in range(180):
    mid=(RHO_LO+RHO_HI)/2
    if J(mid)>0:RHO_LO=mid
    else:RHO_HI=mid
require(J(RHO_LO)>0>J(RHO_HI),'rho isolation')
GAMMA_LO=1+gc(RHO_LO)
GAMMA_HI=1+(1-2*C(RHO_LO))*F(RHO_HI)
require(Q('1.1287512984874658')<GAMMA_LO<GAMMA_HI<Q('1.1287512984874660'),
        'gamma decimal enclosure')

class LK:
    """Exact A+B*kappa; sign is certified by rational isolating intervals."""
    __slots__=('a','b')
    def __init__(self,a=0,b=0):self.a,self.b=Q(a),Q(b)
    @staticmethod
    def get(x):return x if isinstance(x,LK) else LK(x)
    def __add__(self,x):
        x=LK.get(x);return LK(self.a+x.a,self.b+x.b)
    __radd__=__add__
    def __neg__(self):return LK(-self.a,-self.b)
    def __sub__(self,x):return self+-LK.get(x)
    def __rsub__(self,x):return LK.get(x)+-self
    def __mul__(self,x):
        require(not isinstance(x,LK),'only rational scaling is needed')
        x=Q(x);return LK(self.a*x,self.b*x)
    __rmul__=__mul__
    def __truediv__(self,x):return self*(1/Q(x))
    def sign(self):
        if self.b==0:return (self.a>0)-(self.a<0)
        if self.b>0:lo,hi=self.a+self.b*K_LO,self.a+self.b*K_HI
        else:lo,hi=self.a+self.b*K_HI,self.a+self.b*K_LO
        if lo>0:return 1
        if hi<0:return -1
        raise RuntimeError(('unresolved algebraic sign',str(self.a),str(self.b)))
    def __ge__(self,x):return (self-LK.get(x)).sign()>=0
    def __le__(self,x):return (self-LK.get(x)).sign()<=0
    def __eq__(self,x):
        x=LK.get(x);return self.a==x.a and self.b==x.b
    def __repr__(self):return f'LK({self.a},{self.b})'

def f(s):
    s=Q(s)
    if s<=Q(2,3):return LK(0)
    # T is strictly increasing with unique root tau, so this is exact.
    if T(s)<=0:return LK(C(s))
    return LK(Q(1,10),s-1)

def df(s):
    s=Q(s)
    if s<=Q(2,3):return LK(0)
    return LK(dC(s)) if T(s)<=0 else LK(0,1)

def g(s):return (LK(1)-2*f(s))*F(s)

def rule(reports):
    n=len(reports)
    totals=[sum(row[j] for row in reports) for j in(0,1)]
    short=0 if totals[0]<=totals[1] else 1
    A=totals[short]
    if A==0:return (LK(0),)*n
    x=[row[short] for row in reports]
    d=[min(row[1-short],A) for row in reports]
    M,D,L=max(x),sum(d),max(d)
    caps=sorted([M]+[v for v in d if v>0])
    prefix=Q(0);previous=Q(0)
    for k,cap in enumerate(caps):
        water=(A+M-prefix)/(len(caps)-k)
        if previous<=water<=cap:break
        prefix+=cap;previous=cap
    else:raise RuntimeError('water level not found')
    require(sum(min(v,water) for v in caps)==A+M,'water equation')
    P=Q(1)
    for v in caps:P*=min(v,water)/v
    h=LK(Q(1,2))+f(L/D)-f(M/A)
    p=h*P
    return tuple(LK(a)+p*(b-a) for a,b in zip(x,d))

def check_profile(r,y,coalitions=True):
    COUNTS['profiles']+=1
    value=min(sum(row[j] for row in r) for j in(0,1))
    require(all(v>=0 for v in y),('nonnegative',r,y))
    require(sum(y)<=GAMMA_HI*value,('funding',r,y))
    if coalitions:
        for mask in range(1<<len(r)):
            v=min(sum(r[i][j] for i in range(len(r)) if mask>>i&1) for j in(0,1))
            pay=sum(y[i] for i in range(len(r)) if mask>>i&1)
            require(pay>=v,('coverage',r,mask,y))
            COUNTS['coalitions']+=1

def run():
    for n in range(1,5):
        values=tuple(product((Q(0),Q(1),Q(2)),repeat=2))
        states=tuple(product(values,repeat=n))
        payments={r:rule(r) for r in states}
        for r,y in payments.items():
            check_profile(r,y)
            for i in range(n):
                for j in(0,1):
                    if r[i][j]==2:continue
                    high=[list(row) for row in r];high[i][j]+=1
                    high=tuple(tuple(row) for row in high)
                    require(payments[high][i]>=y[i],('grid own monotonicity',r,high,i))
                    COUNTS['own_comparisons']+=1
    rng=Random(16112875)
    for trial in range(5000):
        n=2+trial%7
        r=tuple((Q(rng.randrange(25),rng.randrange(1,14)),Q(rng.randrange(25),rng.randrange(1,14))) for _ in range(n))
        y=rule(r);check_profile(r,y,trial<300)
        i,j=rng.randrange(n),rng.randrange(2)
        high=[list(row) for row in r]
        high[i][j]+=Q(1,rng.choice([10,100,1000,10**6]))
        high=tuple(tuple(row) for row in high)
        require(rule(high)[i]>=y[i],('mixed own increment',r,high,i))
        COUNTS['own_comparisons']+=1
    for k in range(1,100):
        s=Q(k,100)
        require(df(s)*s*(1-s)<=Q(5,72),('derivative product',s))
        if s>Q(2,3):
            critical=(LK(Q(1,2))+f(s))*((3*s-2)/(2*s-1))-df(s)*s*(1-s)
            require(critical>=0,('critical inequality',s))
            COUNTS['critical_checks']+=1
        for j in range(k,101):
            L=Q(j,100)
            lhs=(f(L)-f(s))*(L+s)-df(s)*(L*s*(1-s))
            require(lhs<=Q(1,2)*(L-s),('all-L balance',s,L))
            COUNTS['balance_checks']+=1
    for k in range(50,101):
        s=Q(k,100)
        r=((s,Q(0)),(1-s,Q(0)),(Q(0),Q(1)),(Q(0),Q(1)))
        require(sum(rule(r))==LK(1)+g(s),('exact concentration attainer',s))
        COUNTS['attainers']+=1
    # Exact flat residual payment on the entire ceiling portion, represented
    # by rational points. The endpoint t=q is included; tau is not rounded.
    for k in range(101):
        t=Q(2,3)+Q(k,10000)
        require(T(t)<0,'chosen point belongs to ceiling segment')
        R=(1-t)/t
        r=((Q(1,2),Q(0)),(Q(1,2),Q(0)),(Q(0),Q(1)),(Q(0),R))
        require(rule(r)[3]==LK(Q(1,8)),('ceiling payment equality',t))
        COUNTS['ceiling_equalities']+=1
    result=dict(status='PASS: exact rational/algebraic finite diagnostics',
                scope='All comparisons use rational arithmetic and certified kappa bounds. Finite tests do not replace the continuous proof.',
                counts=COUNTS,tau_interval=[str(TAU_LO),str(TAU_HI)],
                kappa_interval=[str(K_LO),str(K_HI)],rho_interval=[str(RHO_LO),str(RHO_HI)],
                gamma_interval=[str(GAMMA_LO),str(GAMMA_HI)],
                tau_decimal=float(TAU_LO),kappa_decimal=float(K_LO),
                rho_decimal=float(RHO_LO),gamma_decimal=float(GAMMA_LO))
    (BASE/'optimal-shape-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
