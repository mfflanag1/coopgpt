"""Exact tests for the three-owner Banzhaf/pair-OUT/gain theorem."""
from fractions import Fraction as Q
from itertools import product
from random import Random
from pathlib import Path
import json

rng=Random(202610170825)
counts=dict(profiles=0,coalition_coverage_checks=0,pair_outside_checks=0,
            pair_cancellation_identities=0,gain_budget_checks=0,
            finite_lower_checks=0)
def dot(x,y):return sum(a*b for a,b in zip(x,y))
def pay(rows,f):
    n=len(rows);d=len(rows[0]);out=[]
    for i in range(n):
        others=[j for j in range(n) if j!=i]
        value=Q(0)
        for bits in product([0,1],repeat=n-1):
            c=[sum(rows[j][e] for j,bit in zip(others,bits) if bit) for e in range(d)]
            value+=f([c[e]+rows[i][e] for e in range(d)])-f(c)
        out.append(value/2**(n-1))
    return out
for trial in range(600):
    forms=[[Q(rng.randrange(7),rng.randrange(1,5)) for e in range(2)]
           for _ in range(1+rng.randrange(8))]
    def f(c):return min(dot(w,c) for w in forms)
    rows=[[Q(rng.randrange(13),rng.randrange(1,5)) for e in range(2)] for i in range(3)]
    y=pay(rows,f)
    c=[sum(row[e] for row in rows) for e in range(2)]
    t=f(c);s=sum(f(row) for row in rows);g=t-s
    assert t<=sum(y)<=s+Q(5,4)*g
    if not g:assert y==[f(row) for row in rows]
    counts['gain_budget_checks']+=1
    for mask in range(1,8):
        members=[i for i in range(3) if mask>>i&1]
        coalition=[sum(rows[i][e] for i in members) for e in range(2)]
        assert sum(y[i] for i in members)>=f(coalition)
        counts['coalition_coverage_checks']+=1
        if len(members)==2:
            outside=next(i for i in range(3) if i not in members)
            assert sum(y[i] for i in members)==(f(coalition)+t-f(rows[outside]))/2
            counts['pair_cancellation_identities']+=1
        if len(members)>2:continue
        for repetition in range(8):
            withdrawn=[[rows[i][e]*Q(rng.randrange(5),4) if i in members else Q(0)
                        for e in range(2)] for i in range(3)]
            low=[[rows[i][e]-withdrawn[i][e] for e in range(2)] for i in range(3)]
            yl=pay(low,f)
            d=[sum(withdrawn[i][e] for i in members) for e in range(2)]
            assert sum(y[i]-yl[i] for i in members)>=f(d)
            counts['pair_outside_checks']+=1
    counts['profiles']+=1
for b in [Q(1,2),Q(2,3),Q(1),Q(3)]:
    for w in [Q(0),Q(1,9),Q(1)]:
        x=(b+w)/2
        q=max(Q(0),1-x)
        assert 2*x+q>=Q(5,4)
        counts['finite_lower_checks']+=1
rows=[[Q(2),Q(0)],[Q(0),Q(1)],[Q(0),Q(1)],[Q(1),Q(0)]]
y=pay(rows,min)
assert y==[Q(5,8),Q(5,8),Q(5,8),Q(3,8)]
assert sum(y[:3])==Q(15,8)<2
result={'status':'PASS','arithmetic':'exact rational finite expectations',**counts,
        'four_owner_raw_banzhaf_deficient_coalition_payment':'15/8',
        'four_owner_coalition_value':'2'}
Path(__file__).with_name('pairwise_gain_three_owner_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
