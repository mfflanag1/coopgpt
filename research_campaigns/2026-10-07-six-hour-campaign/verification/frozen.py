"""Exact arithmetic certificate for the finite frozen-marginal obstruction."""
from fractions import Fraction as Q
from math import factorial
import json

def mul(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out

def integral(x,eps,b):
    # Independently expand ell_x(b-a)*density_A(a), then integrate 0<=a<=b.
    ell=[2*b-b*b/x,-2+2*b/x,-1/x]
    density=[1/eps+1/(x+eps),-2/(eps*(x+eps))]
    return sum((v*b**(j+1)/Q(j+1) for j,v in enumerate(mul(ell,density))),Q())

def formula(x,eps,b):
    a=1/eps+1/(x+eps)
    return a*b*b-2*b**3/(3*eps*(x+eps))-a*b**3/(3*x)+b**4/(6*eps*(x+eps)*x)

def run():
    eps=Q(1,10);b=Q(1,20);N=100000;k=20
    x0=Q(1,2);x1=Q(3,5)
    j0=integral(x0,eps,b);j1=integral(x1,eps,b)
    assert j0==formula(x0,eps,b)==Q(773,28800)
    assert j1==formula(x1,eps,b)==Q(1073,40320)
    assert j0-j1==Q(23,100800)
    var=(1+Q(9,10)**2)/(12*N)
    assert var<=Q(1,6*N)
    assert all(1/eps+1/(x+eps)<=12 and 2/x<=4 for x in (x0,x1))
    bound=j0-j1-Q(4,N)-2*Q(2**k,factorial(k))
    assert bound==Q(558850546697,2969851084200000)>0
    return {'status':'PASS','J0':str(j0),'J1':str(j1),'limit_gap':str(j0-j1),
            'variance':str(var),'certified_finite_gap':str(bound),
            'K':5,'owners':2*N+k+4,
            'scope':'Exact arithmetic; analytic error and graph proofs are in companion text.'}

if __name__=='__main__':print(json.dumps(run(),indent=2))
