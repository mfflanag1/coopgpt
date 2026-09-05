from verification_io import RESULTS
"""Independent exact checks of the source-class exclusion certificates.

The all-parameter arguments are in THREE_SIDED_PRIORITY_ADDENDUM.md. This
script checks the displayed raw cube and the strictly-positive recurrence
matrices. It imports the independent, previously verified raw generator.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
from triple_recurrence_family import build_family, require


def multiply(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def verify(levels):
    game=build_family(levels,0)
    cube=[['G:0','U:L0:0'],['G:1','V:L0:0'],['G:2','D:L0:0']]
    entries={''.join(map(str,bits)):game['weights'].get(tuple(cube[i][b] for i,b in enumerate(bits)),0) for bits in product(range(2),repeat=3)}
    third=sum((-1)**(3-sum(map(int,key)))*value for key,value in entries.items())
    require(entries=={'000':0,'001':0,'010':0,'011':0,'100':1,'101':0,'110':2,'111':2},'raw cube differs')
    require(third==1,'pair-additive obstruction fails')
    matrix=[[int(i!=j) for j in range(3)] for i in range(3)]
    power=[[int(i==j) for j in range(3)] for i in range(3)]
    for _ in range(levels): power=multiply(power,matrix)
    require(all(x>0 for row in power for x in row),'positive matrix certificate failed')
    # Positive uniform q0 yields a raw feasible point with every root U>1.
    q0=F(1,2**(levels+1))
    pay={name:F(0) for sector in game['sectors'] for name in sector}
    for level in range(levels+1):
        for i in range(3):
            u,v,d=game['pairs'][f'L{level}',i]
            pay[u]=2**level*q0+(1 if level==0 else 0)
            pay[v]=1-2**level*q0
    require(sum(pay.values())==game['total'],'positive witness inefficient')
    require(all(x>=0 for x in pay.values()),'positive witness negative')
    require(all(sum(pay[n] for n in edge)>=value for edge,value in game['weights'].items()),'positive witness fails raw core')
    require(all(pay[game['pairs']['L0',i][0]]>1 for i in range(3)),'root maxima fail to exceed1')
    return dict(L=levels,cube=entries,third_mixed_difference=third,M_power=power,
                positive_root_increment=str(q0),raw_core_positive_witness_verified=True)

if __name__=='__main__':
    records=[verify(L) for L in [2,3,4,8]]
    (RESULTS/'priority_exclusion_checks.json').write_text(json.dumps(records,indent=2)+'\n')
    print('PASS raw cube and recurrence positivity/feasibility checks for L=2,3,4,8')
