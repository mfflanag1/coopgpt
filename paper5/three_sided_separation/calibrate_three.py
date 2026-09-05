"""Bounded raw matching/core calibration; no numerical solver acceptance."""
from exact_three import *
from pathlib import Path
import json
import random


def tensor(values,m):
    return [[[values[(i*m+j)*m+h] for h in range(m)] for j in range(m)] for i in range(m)]


def main():
    records=[]
    empty=[[[3,1],[1,4]],[[2,5],[5,4]]]
    source=check(empty,full=True)
    require(source['T']=='7' and not source['core_nonempty'],'sourced empty-core example failed')
    require(lucas_test(empty)==(7,False,[6,-3]),'sourced Lucas slack failed')
    for count,values in enumerate(product(range(2),repeat=8),1):
        w=tensor(values,2)
        result=check(w,full=True)
        T,balanced,slacks=lucas_test(w)
        require(F(result['T'])==T and result['core_nonempty']==balanced,'Lucas mismatch')
        result['Lucas_slacks']=slacks
        records.append(result)
        if count%32==0:
            print('Binary full-coalition calibration',count,flush=True)
    additive=[]
    for m in (2,3,4):
        w=[[[1+int(i==0)+int(j==0) for h in range(m)] for j in range(m)] for i in range(m)]
        result=check(w,full=m<=3)
        expected_x=[F(1,3)+int(i==0) for i in range(m)]*2+[F(1,3)]*m
        expected_z=[F(int(i==0)) for i in range(m)]*2+[F(1)]*m
        require(list(map(F,result['Lmin']))==expected_x and list(map(F,result['Lmax']))==expected_z,'additive selector mismatch')
        require(F(result['rho'])==F(4*m,3*(m+2)),'additive distance mismatch')
        additive.append(result)
    rng=random.Random(20260904)
    targeted=[]
    for index in range(12):
        w=tensor([rng.randrange(6) for _ in range(27)],3)
        result=check(w,full=True)
        result['case']=index
        targeted.append(result)
    payload=dict(scope='All 256 binary 2x2x2 arrays, including the zero control; 12 deterministic 3x3x3 arrays with weights0..5; additive family m2,3,4.',sourced_empty_core=source,binary_cases=records,additive_cases=additive,targeted_three=targeted)
    Path(__file__).with_name('three_calibration.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    good=[r for r in records if 'rho' in r]
    print('PASS',len(good),'positive balanced binary markets; max rho',max(F(r['rho']) for r in good),'min fraction',min(F(r['min_coordinate_fraction']) for r in good),flush=True)
    print('PASS additive and',len(targeted),'targeted markets;',sum(r['core_nonempty'] for r in targeted),'targeted balanced',flush=True)


if __name__=='__main__':
    main()
