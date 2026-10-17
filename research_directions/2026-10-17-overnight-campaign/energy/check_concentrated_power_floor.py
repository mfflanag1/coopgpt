"""Exact consequences of the finite active-owner recurrence, no numerical LP."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

def d_value(m,s):
    z=Q(m-1)
    for j in range(2,m+1):
        k=min(s-1,2*j-2)
        z*=Q(k,k+1)
    return z

counts=dict(full_ladders=0,bounded_ladders=0,recurrence_ratios=0,
            exact_maxima=0,all_floor_seed_profiles=0)
for m in range(1,301):
    a=Q(4**m,2*comb(2*m,m))
    d=d_value(m,max(2,2*m-1))
    assert d==Q(m-1,m)*a
    if m>1:
        prev=Q(4**(m-1),2*comb(2*(m-1),m-1))
        assert a==Q(2*m,2*m-1)*prev
    counts['full_ladders']+=1
for s in range(2,131):
    vals=[]
    for m in range(1,2*s+3):
        d=d_value(m,s)
        vals.append(d)
        if m>1:
            k=min(s-1,2*m)
            assert d_value(m+1,s)==d*Q(m,m-1)*Q(k,k+1)
            counts['recurrence_ratios']+=1
        for theta in [Q(0),Q(1,10),Q(1,2),Q(1)]:
            q=theta
            for j in range(2,m+1):
                k=min(s-1,2*j-2)
                q*=Q(k,k+1)
            t=2*m*q
            assert 1+Q(m-1,m)*t==1+2*theta*d
        counts['bounded_ladders']+=1
    assert max(vals)==d_value(s,s)==d_value(s+1,s)
    m0=(s+1)//2
    closed=Q(s-1,m0)*Q(4**m0,2*comb(2*m0,m0))*Q(s-1,s)**(s-m0)
    assert closed==d_value(s,s)
    counts['exact_maxima']+=1

# Direct marginal seed: each active hardware deletion removes the sole branch.
def f(c): return min(c[0],sum(min(c[j],c[j+1]) for j in range(1,len(c),2)))
for m in range(1,301):
    c=[1,1,1]+[z for _ in range(m-1) for z in (0,1)]
    assert f(c)==1
    for j in [1,2]:
        low=c[:]
        low[j]=0
        assert f(c)-f(low)==1
        counts['all_floor_seed_profiles']+=1

certificate=1+2*d_value(4,7)
assert certificate==Q(131,35)
result={'status':'PASS','arithmetic':'exact fractions',**counts,
        'nine_owner_full_floor_lower':str(certificate)}
Path(__file__).with_name('concentrated_power_floor_checks.json').write_text(
    json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
