#!/usr/bin/env python3
"""Exact finite scalar certificate plus actual-owner rational diagnostics."""
from fractions import Fraction as Q
import json
import random
from pathlib import Path


R=Q(8,9)
V=Q(49,72)/(1-R**14)
NODES=[Q(1,32),Q(3,32)]+[1-V*R**k for k in range(14)]
BETA=(1+NODES[-1])/2


def value(rows,x):
    return min(sum((a*b for a,b in zip(row,x)),Q()) for row in rows)


def prices(rows,x):
    result=[]
    for j,z in enumerate(x):
        if not z:
            result.append(Q())
            continue
        h=sum((value(rows,[amount if k==j else u*amount for k,amount in enumerate(x)])
               for u in NODES),Q())/16
        result.append(h/z)
    return result


def dot(x,y):
    return sum((a*b for a,b in zip(x,y)),Q())


def main():
    assert sum(NODES)==8
    assert BETA==Q(16795118763825,18478745943857)
    assert BETA>Q(9,10)
    assert 0<NODES[0] and NODES[-1]<1
    assert all(a<b for a,b in zip(NODES,NODES[1:]))
    certificates=[]
    for i in range(1,17):
        prefix=sum(NODES[:i],Q())/16
        coverage=prefix-Q(i*i,512)
        outside=(1+NODES[i-1])/2+sum((1-u for u in NODES[i:]),Q())/16-BETA
        assert coverage>=0 and outside>=0
        certificates.append(dict(i=i,prefix_slack=str(coverage),outside_slack=str(outside)))
    rng=random.Random(314823)
    counts=dict(profiles=0,finite_deviations=0,boundary_cases=0)
    for _ in range(240):
        dim=rng.randint(2,5)
        rows=[[Q(rng.choice([0,0,1,2,4])) for _ in range(dim)]
              for _ in range(rng.randint(1,6))]
        owners=[[Q(rng.choice([0,0,1,2,3])) for _ in range(dim)]
                for _ in range(rng.randint(2,7))]
        high=[sum((owner[j] for owner in owners),Q()) for j in range(dim)]
        ph=prices(rows,high)
        active=sum(z>0 for z in high)
        assert dot(high,ph)<=Q(active+1,2)*value(rows,high)
        for _ in range(3):
            selected=[i for i in range(len(owners)) if rng.randrange(2)]
            held=[sum((owners[i][j] for i in selected),Q()) for j in range(dim)]
            removed=[sum((owners[i][j]*rng.choice([Q(),Q(1,2),Q(1)]) for i in selected),Q()) for j in range(dim)]
            low=[a-b for a,b in zip(high,removed)]
            retained=[a-b for a,b in zip(held,removed)]
            pl=prices(rows,low)
            assert dot(held,ph)>=dot(retained,pl)+BETA*value(rows,removed)
            assert dot(held,ph)>=value(rows,held)
            counts['finite_deviations']+=1
            counts['boundary_cases']+=int(any(z==0 for z in high+low))
        counts['profiles']+=1
    result=dict(status='PASS',arithmetic='exact fractions for every assertion',
                beta=str(BETA),display_beta=float(BETA),nodes=[str(u) for u in NODES],
                scalar_certificates=certificates,diagnostic_counts=counts)
    Path(__file__).with_name('rational_ninety_percent_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('nodes','scalar_certificates')},indent=2))


if __name__=='__main__':
    main()
