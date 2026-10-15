from fractions import Fraction as Q
from itertools import product
from random import Random
import json
from verify_double_star import direct

def decompose(U,V,s,t,b,c,a):
    knots=sorted({Q(0),a}|{v for v in b if 0<v<a}|{a-v for v in c if 0<v<a})
    total=Q(0)
    for lo,hi in zip(knots,knots[1:]):
        mid=(lo+hi)/2
        Bs=sum(cap for cap,value in zip(s,b) if value>=mid)
        Ct=sum(cap for cap,value in zip(t,c) if value>=a-mid)
        total+=(hi-lo)*min(U+Ct,V+Bs,U+V)
    for center,caps,values in ((U,s,b),(V,t,c)):
        knots=sorted({a}|{v for v in values if v>a})
        for lo,hi in zip(knots,knots[1:]):
            mid=(lo+hi)/2
            selected=sum(cap for cap,value in zip(caps,values) if value>=mid)
            total+=(hi-lo)*min(center,selected)
    return total

checks=0
for a,b1,b2,c1,c2 in product(map(Q,[1,2,3]),repeat=5):
    b=(b1,b2);c=(c1,c2)
    for raw in product(map(Q,[0,1,2]),repeat=6):
        U,V=raw[:2];s=raw[2:4];t=raw[4:]
        oracle=direct(U,V,s,t,b,c,a)
        candidate=decompose(U,V,s,t,b,c,a)
        if oracle!=candidate:raise RuntimeError((a,b,c,raw,oracle,candidate))
        checks+=1
r=Random(14013)
for z in range(5000):
    nl=r.randrange(1,8);nr=r.randrange(1,8)
    b=tuple(Q(r.randrange(1,30),r.randrange(1,6)) for _ in range(nl))
    c=tuple(Q(r.randrange(1,30),r.randrange(1,6)) for _ in range(nr))
    a=Q(r.randrange(1,30),r.randrange(1,6))
    U,V=(Q(r.randrange(0,30),r.randrange(1,6)) for _ in range(2))
    s=tuple(Q(r.randrange(0,30),r.randrange(1,6)) for _ in range(nl))
    t=tuple(Q(r.randrange(0,30),r.randrange(1,6)) for _ in range(nr))
    oracle=direct(U,V,s,t,b,c,a)
    candidate=decompose(U,V,s,t,b,c,a)
    if oracle!=candidate:raise RuntimeError((a,b,c,U,V,s,t,oracle,candidate))
    checks+=1
print(json.dumps({'status':'PASS','exact_rational_checks':checks,
 'exhaustive_two_leaves_per_side':3**11,'random_rational_cases':5000,
 'scope':'finite corroboration of arbitrary double-star positive decomposition'},indent=2))
