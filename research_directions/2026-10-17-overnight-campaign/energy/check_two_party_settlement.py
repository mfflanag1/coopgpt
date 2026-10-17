"""Exact two-owner weighted-gain settlement and public baseline accounting."""
from fractions import Fraction as Q
from random import Random
from pathlib import Path
import json

rng=Random(202610170805)
counts=dict(profiles=0,bargaining_settlements=0,coalition_outside_checks=0,
            coverage_checks=0,half_marginal_floor_checks=0,
            optimal_plan_settlements=0,baseline_accounting_checks=0)

def dot(x,y): return sum(a*b for a,b in zip(x,y))
def settle(rows,f,lam):
    c=[rows[0][j]+rows[1][j] for j in range(len(rows[0]))]
    fi=[f(row) for row in rows]
    gain=f(c)-sum(fi)
    return [fi[0]+lam*gain,fi[1]+(1-lam)*gain]

for d in range(1,7):
    for trial in range(100):
        forms=[[Q(rng.randrange(9),rng.randrange(1,4)) for _ in range(d)]
               for _ in range(1+rng.randrange(7))]
        def f(c): return min(dot(w,c) for w in forms)
        rows=[[Q(rng.randrange(12),rng.randrange(1,5)) for _ in range(d)] for i in range(2)]
        c=[rows[0][j]+rows[1][j] for j in range(d)]
        t=f(c)
        fi=[f(row) for row in rows]
        for lam in [Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)]:
            y=settle(rows,f,lam)
            assert sum(y)==t
            for coal in [1,2,3]:
                members=[i for i in range(2) if coal>>i&1]
                own=[sum(rows[i][j] for i in members) for j in range(d)]
                assert sum(y[i] for i in members)>=f(own)
                counts['coverage_checks']+=1
                for repetition in range(6):
                    removed=[[rows[i][j]*Q(rng.randrange(5),4) if i in members else Q(0)
                              for j in range(d)] for i in range(2)]
                    low=[[rows[i][j]-removed[i][j] for j in range(d)] for i in range(2)]
                    ylow=settle(low,f,lam)
                    withdrawn=[sum(removed[i][j] for i in members) for j in range(d)]
                    assert sum(y[i]-ylow[i] for i in members)>=f(withdrawn)
                    counts['coalition_outside_checks']+=1
            if lam==Q(1,2):
                for i in range(2):
                    assert y[i]>=Q(1,2)*(t-fi[1-i])
                    counts['half_marginal_floor_checks']+=1
            counts['bargaining_settlements']+=1
        counts['profiles']+=1

for d in range(1,7):
    for trial in range(100):
        rows=[[Q(rng.randrange(12),4) for _ in range(d)] for i in range(2)]
        use=[Q(rng.randrange(1,6),3) for _ in range(d)]
        ell=[Q(rng.randrange(6),5) for _ in range(d)]
        margin=Q(rng.randrange(1,9),4)
        gross=dot(ell,use)+margin
        def net(c): return margin*min(c[j]/use[j] for j in range(d))
        c=[rows[0][j]+rows[1][j] for j in range(d)]
        activity=min(c[j]/use[j] for j in range(d))
        allocated=[[activity*use[j]*rows[i][j]/c[j] if c[j] else Q(0)
                    for j in range(d)] for i in range(2)]
        assert all(allocated[i][j]<=rows[i][j] for i in range(2) for j in range(d))
        lam=Q(rng.randrange(5),4)
        y=settle(rows,net,lam)
        cash=[dot(ell,allocated[i])+y[i] for i in range(2)]
        assert sum(cash)==gross*activity
        for i in range(2):
            outside=dot(ell,[rows[i][j]-allocated[i][j] for j in range(d)])
            assert cash[i]+outside==dot(ell,rows[i])+y[i]
            counts['baseline_accounting_checks']+=1
        counts['optimal_plan_settlements']+=1

# Exact floor-driven strong-coalition failure for theta>1/2.
theta=Q(3,4)
pure=[[Q(1),Q(0)],[Q(0),Q(1)]]
restored=[[Q(1),Q(1)],[Q(0),Q(1)]]
def floor_rule(rows):
    total=min(rows[0][j]+rows[1][j] for j in range(2))
    return [(1-theta)*min(rows[i])+theta*(total-min(rows[1-i])) for i in range(2)]
assert sum(floor_rule(pure))==2*theta
assert sum(floor_rule(restored))==1

result={'status':'PASS','arithmetic':'exact Fraction production and settlement',**counts}
Path(__file__).with_name('two_party_settlement_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
