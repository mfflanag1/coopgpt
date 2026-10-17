"""Exact rate bounds and same-owner duplicate-resource identities."""
from fractions import Fraction as Q
from math import comb,isqrt
from random import Random
from pathlib import Path
import json

counts=dict(wallis_bounds=0,integer_owner_choices=0,duplicate_row_equalities=0)
for m in range(1,301):
    q=Q(4**m,2*comb(2*m,m))
    assert q*q>=Q(3*m+1,4)
    assert q*q<=m
    counts['wallis_bounds']+=1
    for rmax in range(1,51):
        r=min(rmax,max(1,isqrt(q.numerator//q.denominator)))
        low=max(Q(1),q*r/(r*r+q))
        assert 1<=r<=rmax
        if rmax**4<=m:
            assert low>=Q(rmax,8)
        else:
            assert low**4>=Q(m,8**4)
        counts['integer_owner_choices']+=1
rng=Random(202610170711)
for _ in range(2000):
    n=rng.randint(1,8)
    t=rng.randrange(8)
    rows=[[Q(rng.randrange(9),3) for _ in range(2+2*t)] for _ in range(n)]
    for mask in [0,(1<<n)-1,rng.randrange(1<<n)]:
        c=[sum(rows[i][j] for i in range(n) if mask&(1<<i))
           for j in range(2+2*t)]
        old=min(c[0],c[1]+sum(min(c[j],c[j+1]) for j in range(2,len(c),2)))
        copied=[[r[0],r[1],r[1]]+r[2:] for r in rows]
        cc=[sum(copied[i][j] for i in range(n) if mask&(1<<i))
            for j in range(3+2*t)]
        new=min(cc[0],sum(min(cc[j],cc[j+1]) for j in range(1,len(cc),2)))
        assert old==new
        counts['duplicate_row_equalities']+=1
result={'status':'PASS','arithmetic':'exact fractions',**counts}
Path(__file__).with_name('ownership_sensitive_frontier_checks.json').write_text(
    json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
