"""Exact arithmetic checks for the bounded compressed-price obstruction."""
from fractions import Fraction as Q
import json
from pathlib import Path

def cone(z):return z[0]>=abs(z[1]) and z[0]>=abs(z[2])
def value(z):return z[0]-max(abs(z[1]),z[2])
def plus(a,b):return tuple(x+y for x,y in zip(a,b))
def minus(a,b):return tuple(x-y for x,y in zip(a,b))
def scale(q,z):return tuple(q*x for x in z)

cases=0
for den in range(3,31):
    e=Q(1,den);s=1-e
    for power in (2,3):
        r=1-e**power;d=1-r;lam=d/e
        O=(Q(1),Q(0),Q(0));S=(Q(1),s,s);T=(Q(1),Q(0),r)
        R=(Q(1),r,Q(0));N=(Q(1),r,-r)
        assert r>=2*s/(1+s)
        transitions=[
          (scale(e,O),scale(e/2,(1,1,1)),scale(s,(1,1,1)),S),
          (scale(d,O),scale(d/2,(1,1,-1)),scale(r,(1,1,-1)),N),
          (scale(lam,S),scale(lam,((1+s)/2,(3*s-1)/2,(1+s)/2)),(1-lam,-lam*s,1-lam),T),
          (scale(lam,S),scale(lam,((1+s)/2,(1+s)/2,(3*s-1)/2)),(1-lam,1-lam,-lam*s),R),
        ]
        for aggregate,owner,restore,high in transitions:
            outsider=minus(aggregate,owner);newowner=plus(owner,restore)
            assert cone(owner) and cone(outsider) and cone(restore)
            assert plus(aggregate,restore)==high
            assert cone(newowner)
            assert value(restore)==0
            for b in (owner,outsider,newowner):assert cone(minus((4,0,0),b))
        expected=1+r*(2+10*s)/(3+r+7*s+5*r*s)
        # Reproduce the symbolic elimination's positive coefficient arithmetic.
        A=(3+r)/r+4*s*(1+r)/(r*(1+s))
        B=2+8*s/(1+s)
        assert 1+B/A==expected
        assert expected<Q(7,4)
        cases+=1
s=Q(9,10);r=Q(97,100)
bound=1+r*(2+10*s)/(3+r+7*s+5*r*s)
assert bound==Q(5061,2927)
print(json.dumps({'scope':'exact finite algebra and cone-feasibility checks; analytic proof gives limiting theorem','cases':cases,'comparisons':4*cases,'rational_witness':str(bound),'status':'PASS'},indent=2))
