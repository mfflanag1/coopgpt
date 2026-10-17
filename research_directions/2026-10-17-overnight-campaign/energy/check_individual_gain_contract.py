"""Exact checks, not substitutes for the proofs in INDIVIDUAL_GAIN_ONLY_CONTRACT."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from random import Random
import json

rng=Random(202610170712)
counts=dict(two_pool_profiles=0,coalition_coverages=0,individual_outside_checks=0,
            residual_lipschitz_checks=0,grand_marginal_profiles=0,
            grand_marginal_outside_checks=0,multipool_residual_failures=0)

def minprod(rows,r):
    return min(sum(row[j] for row in rows) for j in range(r))

def huber_pay(rows):
    f=[min(row) for row in rows]
    x=[row[0]-fi for row,fi in zip(rows,f)]
    z=[row[1]-fi for row,fi in zip(rows,f)]
    a,b=sum(x),sum(z)
    if a==b==0: return f
    if a<=b: pa,pb=1-a/(2*b),a/(2*b)
    else: pa,pb=b/(2*a),1-b/(2*a)
    return [fi+xi*pa+zi*pb for fi,xi,zi in zip(f,x,z)]

def pure_pay(q,o,d):
    c=q+o
    if c==d==0: return Q(0)
    return q*(1-c/(2*d) if c<=d else d/(2*c))

for n in range(1,6):
    for trial in range(180):
        rows=[[Q(rng.randrange(17),rng.randrange(1,8)) for _ in range(2)]
              for _ in range(n)]
        y=huber_pay(rows)
        f=minprod(rows,2)
        s=sum(min(row) for row in rows)
        g=f-s
        assert g>=0
        assert sum(y)<=s+Q(3,2)*g
        if g==0: assert sum(y)==s
        for mask in range(1<<n):
            coalition=[i for i in range(n) if mask>>i&1]
            assert sum(y[i] for i in coalition)>=minprod([rows[i] for i in coalition],2)
            counts['coalition_coverages']+=1
        for i in range(n):
            for fa,fb in product([Q(0),Q(1,3),Q(1,2),Q(1)],repeat=2):
                d=[rows[i][0]*fa,rows[i][1]*fb]
                low=[list(row) for row in rows]
                low[i]=[rows[i][j]-d[j] for j in range(2)]
                assert y[i]-huber_pay(low)[i]>=min(d)
                counts['individual_outside_checks']+=1
        counts['two_pool_profiles']+=1

grid=[Q(v,4) for v in range(13)]
for o,d,lo,hi in product(grid,repeat=4):
    if hi<lo: continue
    difference=pure_pay(hi,o,d)-pure_pay(lo,o,d)
    assert 0<=difference<=hi-lo
    counts['residual_lipschitz_checks']+=1

for r in range(1,7):
    for n in range(1,6):
        for trial in range(60):
            rows=[[Q(rng.randrange(11),rng.randrange(1,5)) for _ in range(r)]
                  for _ in range(n)]
            c=[sum(row[j] for row in rows) for j in range(r)]
            total=min(c)
            own=[min(row) for row in rows]
            standalone=sum(own)
            gain=total-standalone
            m=[total-min(c[j]-rows[i][j] for j in range(r)) for i in range(n)]
            assert sum(m)<=standalone+min(n,r)*gain
            for i in range(n):
                residual_totals=[c[j]-standalone for j in range(r)]
                residual=[rows[i][j]-own[i] for j in range(r)]
                assert m[i]==own[i]+gain-min(residual_totals[j]-residual[j] for j in range(r))
                d=[rows[i][j]*Q(rng.randrange(5),4) for j in range(r)]
                lowtotal=min(c[j]-d[j] for j in range(r))
                lowmargin=lowtotal-min(c[j]-rows[i][j] for j in range(r))
                assert m[i]-lowmargin>=min(d)
                counts['grand_marginal_outside_checks']+=1
            counts['grand_marginal_profiles']+=1

low=[[Q(1),Q(0)],[Q(1),Q(0)],[Q(0),Q(1)]]
high=[[Q(1),Q(0)],[Q(1),Q(0)],[Q(1),Q(1)]]
assert huber_pay(low)==[Q(1,4),Q(1,4),Q(3,4)]
assert huber_pay(high)==[Q(0),Q(0),Q(1)]

def integral_prices(c):
    """Exact polynomial integration for the accepted min-r integral prices."""
    t=min(c)
    if t==0: return [Q(0)]*len(c)
    result=[]
    for j,cj in enumerate(c):
        coeff=[Q(1)]
        for k,ck in enumerate(c):
            if k==j: continue
            out=[Q(0)]*(len(coeff)+1)
            for degree,value in enumerate(coeff):
                out[degree]+=value
                out[degree+1]-=value/ck
            coeff=out
        result.append(sum(value*t**(degree+1)/(degree+1) for degree,value in enumerate(coeff))/cj)
    return result

def wrapped_integral(rows):
    n,r=len(rows),len(rows[0])
    base=[min(row) for row in rows]
    residual=[[v-fi for v in row] for row,fi in zip(rows,base)]
    c=[sum(row[j] for row in residual) for j in range(r)]
    prices=integral_prices(c)
    return [fi+sum(row[j]*prices[j] for j in range(r)) for fi,row in zip(base,residual)]

original=[[Q(1,10),Q(10),Q(0)],[Q(9,10),Q(0),Q(100)]]
restore=[[Q(1,10),Q(10),Q(1,100)],[Q(9,10),Q(0),Q(100)]]
before=wrapped_integral(original)[0]
after=wrapped_integral(restore)[0]
assert after<before
counts['multipool_residual_failures']+=1
result={'status':'PASS','arithmetic':'fractions.Fraction; deterministic exact checks',
        **counts,'TCWM_failure_total_before':'5/4','TCWM_failure_total_after':'1',
        'three_pool_wrapper_owner_before':str(before),
        'three_pool_wrapper_owner_after':str(after),
        'three_pool_wrapper_loss':str(before-after)}
Path(__file__).with_name('individual_gain_contract_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
