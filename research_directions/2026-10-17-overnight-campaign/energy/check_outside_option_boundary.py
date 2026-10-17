"""Exact finite diagnostics for IR versus marginal floors and baseline closure."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

counts=dict(profiles=0,coalition_coverage=0,full_out=0,positive_ir_ratios=0,
            weighted_bargaining_stationarity=0,opportunity_cost_identities=0)
def welfare(c,e): return e*(c[1]+c[2])+min(c)
def pay(c,e): return [min(c),e*c[1],e*c[2]]
for e in [Q(1,100),Q(1,10),Q(1,2),Q(1),Q(10)]:
    for c in product([Q(0),Q(1,2),Q(1),Q(2)],repeat=3):
        z=pay(c,e)
        assert sum(z)==welfare(c,e)
        counts['profiles']+=1
        for mask in range(8):
            s=[j for j in range(3) if mask & (1<<j)]
            own=[c[j] if j in s else Q(0) for j in range(3)]
            assert sum(z[j] for j in s)>=welfare(own,e)
            counts['coalition_coverage']+=1
            for ratios in product([Q(0),Q(1,2),Q(1)],repeat=len(s)):
                low=list(c)
                for j,r in zip(s,ratios): low[j]*=r
                wd=[c[j]-low[j] for j in range(3)]
                zl=pay(low,e)
                assert sum(z[j]-zl[j] for j in s)>=welfare(wd,e)
                counts['full_out']+=1
for theta in [Q(j,100) for j in range(1,101)]:
    e=theta/2
    c=[Q(1)]*3
    z=pay(c,e)
    marg=welfare(c,e)-welfare([1,0,1],e)
    assert marg==1+e
    assert z[1]==e>0
    assert z[1]/marg<theta
    counts['positive_ir_ratios']+=1
for theta in [Q(j,10) for j in range(1,10)]:
    for delta in [Q(j,7) for j in range(1,30)]:
        x=theta*delta
        assert theta/x-(1-theta)/(delta-x)==0
        assert -theta/x**2-(1-theta)/(delta-x)**2<0
        counts['weighted_bargaining_stationarity']+=1
for a,b,p,l_a,l_b,pi in product([Q(0),Q(1,2),Q(1),Q(2)],repeat=6):
    for r in [Q(0),Q(1,2),Q(1)]:
        x=r*min(a,b,p)
        gross=pi*x+l_a*(a-x)+l_b*(b-x)
        net=l_a*a+l_b*b+(pi-l_a-l_b)*x
        assert gross==net
        counts['opportunity_cost_identities']+=1
result={'status':'PASS','arithmetic':'exact fractions',**counts}
Path(__file__).with_name('outside_option_boundary_checks.json').write_text(
    json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
