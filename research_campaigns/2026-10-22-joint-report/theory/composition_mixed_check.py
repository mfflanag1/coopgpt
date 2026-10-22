#!/usr/bin/env python3
"""Exact mixed-bundle identities and recursive exposed-edge diagnostics."""
from fractions import Fraction as F
from math import isqrt
import json


def physical_value(rows,k,t,S):
    resources=[sum(row[i]*t[i] for i in range(4) if S>>i&1) for row in rows]
    return sum(sorted(resources)[:k])


def lower_combo(rows,k,R):
    p0=(1,1,1,1);pa=(R,1,1,1);pb=(1,1,1,R)
    rhs=physical_value(rows,k,p0,9)
    rhs+=sum(physical_value(rows,k,pa,s) for s in (6,10,13))
    rhs+=sum(physical_value(rows,k,pb,s) for s in (5,6,11))
    denominator=2*(physical_value(rows,k,pa,15)+physical_value(rows,k,pb,15))
    return rhs/denominator


def mixed_bundle_checks():
    first=[]
    for R in (2,4,16,256):
        eps=F(1,4*R)
        rows=[(1,1,eps,eps),(eps,eps,1,1)]
        beta=lower_combo(rows,1,R)
        assert beta==(9+(2*R+5)*eps)/(8+4*(R+1)*eps)>1
        first.append({'R':R,'epsilon':str(eps),'lower':str(beta)})
    general=[]
    for k in (1,2,3,4,8,16,64,256):
        eps,delta=F(1,8),F(1,8*k)
        rows=[(1,1,eps,eps),(eps,eps,1,1)]+[(delta,)*4]*(k-1)
        assert len(rows)==k+1 and all(v>0 for row in rows for v in row)
        beta=lower_combo(rows,k,2)
        expected=(9+9*eps+18*(k-1)*delta)/(8+12*eps+20*(k-1)*delta)
        assert beta==expected>F(33,32)
        for t in ((1,1,1,1),(2,1,1,1),(1,1,1,2)):
            for S in range(16):
                total=sum(t[i] for i in range(4) if S>>i&1)
                original=min(sum(t[i] for i in (0,1) if S>>i&1),
                             sum(t[i] for i in (2,3) if S>>i&1))
                assert physical_value(rows,k,t,S)==(eps+(k-1)*delta)*total+(1-eps)*original
        general.append({'k':k,'d':k+1,'strict_positive_lower':str(beta)})
    return {'two_resource':first,'all_k':general}


def cuts(h):
    if h==0:
        return [1]
    sub=cuts(h-1)
    width=4**(h-1)
    left=[a|(b<<width) for a in sub for b in sub]
    return left+[a<<(2*width) for a in left]


def dimension_lower(c):
    E=c*c//4
    d=(1+isqrt(1+8*E))//2
    if d*(d-1)//2<E:
        d+=1
    assert d*(d-1)//2>=E and (d-1)*(d-2)//2<E
    return d


def geometry_checks():
    records=[]
    for h in range(1,4):
        vertices=cuts(h)
        n,L=4**h,2**h
        expected=2**(2**h-1)
        assert len(set(vertices))==len(vertices)==expected
        assert all(v.bit_count()==L for v in vertices)
        left=[v for v in vertices if v>>(n//2)==0]
        right=[v for v in vertices if v&((1<<(n//2))-1)==0]
        assert len(left)==len(right)==expected//2
        directions=set()
        for a in left:
            for b in right:
                union=a|b
                costs={v:L+(v&~union).bit_count() for v in vertices}
                exposed={v for v,c in costs.items() if c==min(costs.values())}
                assert exposed=={a,b}
                direction=tuple((1 if a>>i&1 else 0)-(1 if b>>i&1 else 0) for i in range(n))
                assert direction not in directions
                directions.add(direction)
        assert len(directions)==expected*expected//4
        records.append({'h':h,'owners':n,'cut_vertices':expected,
                        'exposed_distinct_cross_directions':len(directions),
                        'minimum_resource_lower':dimension_lower(expected)})
    assert dimension_lower(32768)==23171
    return records


if __name__=='__main__':
    print(json.dumps({'mixed_bundles':mixed_bundle_checks(),
                      'geometry':geometry_checks()},indent=2))
