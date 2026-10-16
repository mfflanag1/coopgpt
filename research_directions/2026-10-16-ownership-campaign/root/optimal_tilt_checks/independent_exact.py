"""Independent finite diagnostics for the optimal concentration price.
Payments are affine in the algebraic tangent slope. No floating comparison.
This is evidence for, not a proof of, the all-real theorem.
"""
from fractions import Fraction as F
from random import Random
from itertools import combinations
import json


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def cubic(x):
    return 53*x**3-91*x*x+55*x-12


def quintic(x):
    return 68*x**5-235*x**4+308*x**3-199*x*x+64*x-8


def ceiling(x):
    return x*x/(8*(1-x)*(2*x-1))-F(1,2)


def slope(x):
    return x*(3*x-2)/(8*(1-x)**2*(2*x-1)**2)


def conc(x):
    return (1+x)**3/(54*x)


def isolate(fn,lo,hi,increasing):
    for _ in range(120):
        mid=(lo+hi)/2
        if (fn(mid)<0)==increasing:
            lo=mid
        else:
            hi=mid
    return lo,hi

TL,TH=isolate(cubic,F(17,25),F(683,1000),True)
KL,KH=slope(TL),slope(TH)
RL,RH=isolate(quintic,F(2,3),F(27,40),False)
GL=1+(1-2*ceiling(RH))*conc(RL)
GH=1+(1-2*ceiling(RL))*conc(RH)
check(TL<TH and cubic(TL)<0<cubic(TH),'tau root bracket')
check(quintic(RL)>0>quintic(RH),'rho root bracket')
check(F(1,4)<KL<KH<F(5,16),'slope bracket')
check(F(1128751298487465,10**15)<GL<GH<F(1128751298487467,10**15),'gamma enclosure')

# Affine algebraic number a+b*kappa. All operations below stay affine.
def add(x,y): return x[0]+y[0],x[1]+y[1]
def sub(x,y): return x[0]-y[0],x[1]-y[1]
def mul(x,r): return x[0]*r,x[1]*r
def bounds(x):
    a,b=x
    return (a+b*KL,a+b*KH) if b>=0 else (a+b*KH,a+b*KL)
def nonnegative(x):
    if x==(0,0): return True
    lo,hi=bounds(x)
    check(not(lo<0<=hi),'algebraic sign unresolved; increase isolation')
    return lo>=0

def shape(u):
    if u<=F(2,3): return F(0),F(0)
    if cubic(u)<=0: return ceiling(u),F(0)
    return F(1,10),u-1

def payments(a,b):
    A,B=sum(a),sum(b)
    if A>B:
        a,b=b,a;A,B=B,A
    if A==0: return [(F(0),F(0)) for _ in a]
    M=max(a);d=[min(x,A) for x in b];D=sum(d);L=max(d)
    caps=sorted([M]+[x for x in d if x>0]);target=A+M
    if D==A:
        lam=max(caps)
    else:
        prefix=F(0)
        for j,cap in enumerate(caps):
            lam=(target-prefix)/(len(caps)-j)
            if lam<=cap: break
            prefix+=cap
        check(sum(min(x,lam) for x in caps)==target,'water equation')
    prod=F(1)
    for cap in caps: prod*=min(cap,lam)/cap
    h=add((F(1,2),F(0)),sub(shape(L/D),shape(M/A)))
    return [add((x,F(0)),mul(h,prod*(di-x))) for x,di in zip(a,d)]

rng=Random(6101622)
counts={'profiles':0,'coalitions':0,'whole_owner_underreports':0,'flat_residual_equalities':0,'orientation_ties':0}
worst_upper=F(0)

def examine(a,b):
    global worst_upper
    n=len(a);y=payments(a,b);counts['profiles']+=1
    total=(F(0),F(0))
    for yi in y:
        check(nonnegative(yi),'negative payment');total=add(total,yi)
    value=min(sum(a),sum(b))
    check(nonnegative(sub((GH*value,F(0)),total)),'funding bound')
    if value: worst_upper=max(worst_upper,bounds(total)[1]/value)
    for mask in range(1,1<<n):
        av=sum(a[i] for i in range(n) if mask>>i&1)
        bv=sum(b[i] for i in range(n) if mask>>i&1)
        pay=(F(0),F(0))
        for i in range(n):
            if mask>>i&1: pay=add(pay,y[i])
        check(nonnegative(sub(pay,(min(av,bv),F(0)))),'coalition coverage')
        counts['coalitions']+=1
    for i in range(n):
        for fa,fb in [(F(0),F(0)),(F(1,2),F(1)),(F(1),F(1,2)),(F(4,5),F(2,3))]:
            aa=list(a);bb=list(b);aa[i]*=fa;bb[i]*=fb
            yy=payments(aa,bb)
            check(nonnegative(sub(y[i],yy[i])),'profitable whole-owner underreport')
            counts['whole_owner_underreports']+=1
    if sum(a)==sum(b):
        yy=payments(b,a)
        check(all(y[i]==yy[i] for i in range(n)),'tie orientation mismatch')
        counts['orientation_ties']+=1

for n in range(2,9):
    for _ in range(120):
        a=[F(rng.randrange(0,41),rng.choice([3,7,11,25])) for _ in range(n)]
        b=[F(rng.randrange(0,41),rng.choice([3,7,11,25])) for _ in range(n)]
        examine(a,b)
for j in range(1,101):
    s=F(2,3)+F(j,6000)
    examine([s,1-s,F(0),F(0)],[F(0),F(0),F(1),F(1)])
    t=F(2,3)+F(j,10000)
    check(cubic(t)<0,'flat region outside ceiling')
    R=(1-t)/t
    y=payments([F(1,2),F(1,2),F(0),F(0)],[F(0),F(0),F(1),R])
    check(y[3]==(F(1,8),F(0)),'critical residual payment not exactly flat')
    counts['flat_residual_equalities']+=1
for j in range(1,51):
    a=[F(j,101),1-F(j,101),F(0),F(0)]
    b=[F(0),F(0),F(2*j,103),1-F(2*j,103)]
    examine(a,b)
print(json.dumps({'status':'PASS','scope':'Independent exact finite diagnostics, not an all-real proof','counts':counts,'tau_interval':[str(TL),str(TH)],'kappa_interval':[str(KL),str(KH)],'rho_interval':[str(RL),str(RH)],'gamma_interval':[str(GL),str(GH)],'gamma_display':float(GL),'largest_tested_factor_upper':float(worst_upper)},indent=2))
