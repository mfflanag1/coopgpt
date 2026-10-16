#!/usr/bin/env python3
"""Exact rational interval certificates for the analytical scalar proof.

No report grids, numerical optimizers, floating assertions, or third-party
packages. Even/odd Taylor polynomials bound exp(-x) by Taylor's signed
integral remainder. Floating values in the output are explanatory only.
"""
from fractions import Fraction as F
import json
from pathlib import Path

class I:
    def __init__(self, lo, hi=None):
        self.lo=F(lo); self.hi=F(lo if hi is None else hi)
        if self.lo>self.hi: raise ValueError('reversed interval')
    def __add__(self,o):
        o=as_i(o); return I(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,o):return self+-as_i(o)
    def __rsub__(self,o):return as_i(o)+-self
    def __mul__(self,o):
        o=as_i(o); vals=[self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi]
        return I(min(vals),max(vals))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=as_i(o)
        if o.lo<=0<=o.hi:raise ZeroDivisionError('interval contains zero')
        return self*I(1/o.hi,1/o.lo)
    def __rtruediv__(self,o):return as_i(o)/self
    def __pow__(self,n):
        if n<0:return (1/self)**(-n)
        out=I(1)
        for _ in range(n):out=out*self
        return out

def as_i(x):return x if isinstance(x,I) else I(x)
def eminus(x):
    x=F(x)
    if x<0:raise ValueError('only nonnegative arguments')
    term=F(1); total=F(1)
    for j in range(1,41):
        term*= -x/j;total+=term
    upper=total
    lower=total+term*(-x)/41
    return I(lower,upper)

def k(t):
    t=F(t)
    if t==0:return I(1)
    return 1-eminus(1/t-1)/2 if t<=1 else eminus(t-1)/2

def q_short(t):return eminus(1/F(t)-1)/2
def d(t):
    t=F(t)
    return q_short(t)/(t*t) if t<=1 else k(t)

c=eminus(1)/2;C=1+c;a=(1-3*c)/C

def scalar(beta,u):
    beta=F(beta);u=F(u)
    return 1+k(beta)*(beta-1)-C*beta-k(u)*(beta-u)/3+(k(u)-k(beta))*(c+a*beta)
def scalar_u(beta,u):
    beta=F(beta);u=F(u)
    return (k(u)-d(u)*(u+3*c+(3*a-1)*beta))/3

def beta_derivative_upper(beta,ku):
    beta=F(beta)
    return -C+(1-a)*k(beta)+d(beta)*(C-(1-a)*beta)+(a-F(1,3))*ku

def grid_u(beta,u):
    beta=F(beta);u=F(u)
    return (k(u)-d(u)*(u+3*c+2*beta))/3

def U(beta):
    beta=F(beta)
    return 1+c+F(7,60)-(C*C-F(2,3))*beta-C*k(beta)
def Uprime(beta):return -(C*C-F(2,3))+C*d(beta)

checks=[]
def positive(name,expr):
    expr=as_i(expr)
    if expr.lo<=0:raise RuntimeError(f'{name}: not positive: {expr.lo}, {expr.hi}')
    checks.append({'name':name,'lower_exact':str(expr.lo),'upper_exact':str(expr.hi),'lower_approx':float(expr.lo),'upper_approx':float(expr.hi)})
def negative(name,expr):positive(name,-as_i(expr))

positive('c > 2/11',c-F(2,11))
positive('c < 3/16',F(3,16)-c)
positive('1/3 < a',a-F(1,3))
positive('a < 1/2',F(1,2)-a)
positive('C < 6/5',F(6,5)-C)
positive('M-dual quadratic margin',F(2,77)-F(1155,1888)/25)
negative('small-beta M-dual slope',20*c*F(51,100)/7-k(F(51,100))/3)
positive('large A in small-beta strip forces u < .46',k(F(51,100))+F(1,25)-k(F(23,50)))
positive('S_u(.51,.46)',scalar_u(F(51,100),F(23,50)))
positive('D(.5; k_u<=1) < 1/80',F(1,80)-beta_derivative_upper(F(1,2),I(1)))
negative('S(.5,.46) < -3/10000',scalar(F(1,2),F(23,50))+F(3,10000))
positive('S_u(1.2,.4)',scalar_u(F(6,5),F(2,5)))
negative('D(.51; k_u<=k(.4))',beta_derivative_upper(F(51,100),k(F(2,5))))
positive('S_u(.51,.49)',scalar_u(F(51,100),F(49,100)))
negative('S_u(.51,.5)',scalar_u(F(51,100),F(1,2)))
positive('q(.49) > 1/6',q_short(F(49,100))-F(1,6))
negative('S(.51,.5) < -1/50000',scalar(F(51,100),F(1,2))+F(1,50000))
positive('S_u(.51,.5) > -3/1000',scalar_u(F(51,100),F(1,2))+F(3,1000))
positive('concavity maximum margin',F(1,50000)-F(9,8)*F(3,1000)**2)
positive('A > C^2/4 forces beta > .7',C*C/4-(1-k(F(7,10))))
positive('A > C^2/4 forces u < .6',C*C/4-(k(F(3,5))-k(F(6,5))))
negative('grid scalar derivative at (.7,.35)',grid_u(F(7,10),F(7,20)))
negative('U(.75) < -.01',U(F(3,4))+F(1,100))
positive('Uprime(.75)>0',Uprime(F(3,4)))
positive('Uprime(.75)<.02',F(1,50)-Uprime(F(3,4)))
positive('large-A tangent margin',F(1,100)-F(1,50)*(F(6,5)-F(3,4)))

result={'status':'PASS','checks':len(checks),'proof_scope':'Exact scalar constants used with analytical monotonicity and concavity. This script does not establish the reduction or theorem by report enumeration.','records':checks}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':result['checks'],'smallest_positive_margin':min(x['lower_approx'] for x in checks)},indent=2))
