#!/usr/bin/env python3
from fractions import Fraction as Q
if not __debug__:
    raise RuntimeError('Run without -O: exact assertions are required')
checks=0
for k in range(2,501):
    h=Q(5,2*k+3)
    a=2*(1-h)/(k-1)
    b=(1-h)/(k-1)
    assert h+(k-1)*b==1
    assert 2*h+(k-1)*a==2
    assert a==2*b
    assert 4*h-10*(1-h)/(k-1)==0
    gap=k*h*h-2*h
    assert gap==Q(5*(k-6),(2*k+3)**2)
    assert (gap>0)==(k>6)
    assert k*(h*h+Q(1,k*k)) < 9
    checks+=7
# Exact coalition reduction: each pool contributes capacity0,1,2,3 at hub;
# at low profile the focal pool has two unit owners. Enumerate small k fully.
from itertools import product
for k in range(2,7):
    h=Q(5,2*k+3);a=2*(1-h)/(k-1);b=(1-h)/(k-1)
    for choices in product(range(4),repeat=k):
        hubcap=[(0,2,1,3)[c] for c in choices]
        hubpay=sum((Q(0),Q(2,k),Q(1,k),Q(3,k))[c] for c in choices)
        assert hubpay>=min(hubcap)
        cap=[(0,1,1,2)[choices[0]]]+[(0,2,1,3)[c] for c in choices[1:]]
        pay=(0,h,h,2*h)[choices[0]]+sum((0,a,b,a+b)[c] for c in choices[1:])
        assert pay>=min(cap)
        checks+=2
print('PASS:',checks,'exact support/KKT/coalition checks')
