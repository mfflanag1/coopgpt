#!/usr/bin/env python3
"""Exact independent checks for composition_obstructions.txt; stdlib only."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json


def technology(b):
    if len(b)==1:
        return b[0]
    assert len(b)%4==0
    k=len(b)//4
    y=[technology(b[j*k:(j+1)*k]) for j in range(4)]
    return min(y[0]+y[1],y[2]+y[3])


def active_cut(b,offset=0):
    if len(b)==1:
        return (offset,)
    k=len(b)//4
    values=[technology(b[j*k:(j+1)*k]) for j in range(4)]
    branch=(0,1) if values[0]+values[1]<=values[2]+values[3] else (2,3)
    return tuple(i for j in branch
                 for i in active_cut(b[j*k:(j+1)*k],offset+j*k))


def coalition_value(b,mask):
    return technology(tuple(v if mask>>i&1 else 0 for i,v in enumerate(b)))


def base_calibration():
    root=Path(__file__).resolve().parents[1]
    cert=json.loads((root/'computations/two_pools.json').read_text())
    profiles=list(product((1,4),repeat=4))
    payments=[[F(v) for v in cert['primal'][4*j:4*j+4]] for j in range(16)]
    assert F(cert['primal'][-1])==F(9,8)
    lookup={p:j for j,p in enumerate(profiles)}
    coalitions=monotone=0
    for p,x in zip(profiles,payments):
        assert all(v>=0 for v in x)
        assert sum(x)<=F(9,8)*technology(p)
        for mask in range(1,16):
            assert sum(v for i,v in enumerate(x) if mask>>i&1)>=coalition_value(p,mask)
            coalitions+=1
        for i in range(4):
            if p[i]==1:
                q=list(p);q[i]=4
                assert x[i]<=payments[lookup[tuple(q)]][i]
                monotone+=1
    # Exact three-profile lower: (4+4+1)/(2*(2+2))=9/8.
    assert F(4+4+1,2*(2+2))==F(9,8)
    return {'beta':'9/8','coalitions':coalitions,'own_edges':monotone}


def verify_all_coalitions16(b,payments):
    # Coalition values use independent four-leaf tables, not active-cut logic.
    tables=[]
    for j in range(4):
        v=b[4*j:4*j+4]
        tables.append([min(sum(v[i] for i in (0,1) if s>>i&1),
                           sum(v[i] for i in (2,3) if s>>i&1)) for s in range(16)])
    sums=[0]*(1<<16)
    for s in range(1,1<<16):
        bit=s&-s
        sums[s]=sums[s^bit]+payments[bit.bit_length()-1]
        worth=min(tables[0][s&15]+tables[1][(s>>4)&15],
                  tables[2][(s>>8)&15]+tables[3][(s>>12)&15])
        assert sums[s]>=worth
    assert sums[-1]==sum(payments)
    return (1<<16)-1


def tensor_obstruction():
    base=list(product((1,4),repeat=4))
    tensors={tuple(a_i*c_i for a_i in a for c_i in c) for a in base for c in base}
    assert len(tensors)==255
    signatures={}
    for b in tensors:
        for i in range(16):
            key=(i,b[:i]+b[i+1:])
            assert key not in signatures or signatures[key]==b[i]
            signatures[key]=b[i]
    active=((1,1,1,1),(4,1,1,1),(1,1,1,4))
    checked=0
    for a,c in product(active,repeat=2):
        b=tuple(v*w for v in a for w in c)
        assert technology(b)==technology(a)*technology(c)==4
        cut=set(active_cut(b))
        x=tuple(v if i in cut else 0 for i,v in enumerate(b))
        assert sum(x)==technology(b)
        checked+=verify_all_coalitions16(b,x)
        for sa in range(16):
            for sc in range(16):
                mask=sum(1<<(4*i+j) for i in range(4) for j in range(4)
                         if sa>>i&1 and sc>>j&1)
                assert coalition_value(b,mask)==coalition_value(a,sa)*coalition_value(c,sc)
    return {'full_product_profiles':len(tensors),'own_edges':0,
            'active_product_profiles':9,'coalitions':checked,'exact_beta':'1'}


def aggregate_failure():
    results=[]
    for t in (1,4):
        b=(F(t),F(1),F(4),F(4))+(F(1),)*4+(F(1,2),)*8
        total=technology(b)
        without=technology((F(0),)+b[1:])
        assert total==without==2
        x=[total]*16
        x[1]+=without*b[1]/(b[0]+b[1])
        assert sum(x)<=17*total
        verify_all_coalitions16(b,x)
        results.append((technology(b[:4]),sum(x[:4]),x[0]))
    assert results==[(F(2),F(9),F(2)),(F(5),F(42,5),F(2))]
    return {'block_outputs':['2','5'],'block_payments':['9','42/5'],
            'controller_payments':['2','2'],'global_budget_factor':17}


def range_obstruction():
    rows=[]
    for h in range(1,7):
        n=4**h
        ones=(1,)*n
        cut=set(active_cut(ones))
        assert len(cut)==technology(ones)==2**h
        b=tuple(4 if i in cut else 1 for i in range(n))
        assert sum(b[i] for i in cut)==4*2**h
        assert technology(b)==2**h
        rows.append({'h':h,'owners':n,'fixed_cut_ratio':'4'})
    assert F(9,8)**11<4<F(9,8)**12
    return {'depth_checks':rows,'first_depth_power_gt_4':12}


if __name__=='__main__':
    print(json.dumps({'base':base_calibration(),'tensor':tensor_obstruction(),
                      'aggregation':aggregate_failure(),'range':range_obstruction()},indent=2))
