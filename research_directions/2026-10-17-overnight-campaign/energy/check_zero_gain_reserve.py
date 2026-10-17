"""Exact restoration and finite zero-gain reserve diagnostics."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

counts=dict(binary_profiles=0,zero_gain_anchors=0,exact_reserve_bounds=0,
            multipool_restoration_profiles=0,
            nonnegative_null_payment_cases=0)
def f(rows): return min(sum(r[0] for r in rows),sum(r[1] for r in rows))
def standalone(rows): return sum(min(r) for r in rows)
for n in range(1,6):
    for bits in product([0,1],repeat=2*n):
        rows=[list(bits[2*i:2*i+2]) for i in range(n)]
        a=sum(r[0] for r in rows)
        b=sum(r[1] for r in rows)
        high=[[max(x,y),y] for x,y in rows] if a>=b else [
            [x,max(x,y)] for x,y in rows]
        assert all(high[i][j]>=rows[i][j] for i in range(n) for j in range(2))
        assert f(high)==f(rows)
        assert standalone(high)==f(high)
        assert all(0<=z<=1 for row in high for z in row)
        counts['binary_profiles']+=1
        counts['zero_gain_anchors']+=1
for r in range(1,6):
    for n in range(1,4):
        for bits in product([0,1],repeat=r*n):
            rows=[list(bits[r*i:r*(i+1)]) for i in range(n)]
            totals=[sum(row[j] for row in rows) for j in range(r)]
            jstar=min(range(r),key=lambda j:totals[j])
            high=[[max(row[j],row[jstar]) for j in range(r)] for row in rows]
            totalhigh=[sum(row[j] for row in high) for j in range(r)]
            assert min(totalhigh)==min(totals)==sum(min(row) for row in high)
            assert all(high[i][j]>=rows[i][j] for i in range(n) for j in range(r))
            assert all(0<=v<=1 for row in high for v in row)
            counts['multipool_restoration_profiles']+=1
for s in range(2,401):
    lower=1+Q(s-1,2*s)
    assert lower==Q(3,2)-Q(1,2*s)
    p0=[[1,0],[0,1]]+[[0,0] for _ in range(s-1)]
    p1=[[1,0],[0,1]]+[[1,0] for _ in range(s-1)]
    h1=[[1,0],[1,1]]+[[1,0] for _ in range(s-1)]
    assert f(p0)==f(p1)==f(h1)==1
    assert standalone(h1)==1
    for w in [Q(0),Q(1,100),Q(1),Q(7)]:
        for b in [Q(1,2),Q(2,3),Q(1),Q(3)]:
            x=(b+(s-1)*w)/s
            q=max(Q(0),1-x)
            assert s*x+q>=lower
            counts['nonnegative_null_payment_cases']+=1
    counts['exact_reserve_bounds']+=1
assert Q(3,2)-Q(1,4)==Q(5,4)
result={'status':'PASS','arithmetic':'exact rational identities',**counts,
        'three_owner_zero_gain_funding_lower':'5/4',
        'three_owner_reserve_fraction_lower':'1/4'}
Path(__file__).with_name('zero_gain_reserve_checks.json').write_text(
    json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
