from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path

def F(x):
    a,b,c,d=x
    return min(a+c,b+d,b+c)

def H(x):
    a,b,c,d=x
    return (min(b,a+c)+min(c,b+d)+min(a,b)+min(c,d))/2

def game(a,b,S):
    return min(sum(a[i] for i in S),sum(b[i] for i in S))

counts={'support_identity':0,'all_capacity_formula':0,'coalitionwise_majorants':0}
edges={frozenset((0,1)),frozenset((1,2)),frozenset((2,3))}
# Finite support/algebra replay, separate from the analytic arbitrary-integral proof.
for assignments in product(range(3),repeat=4):
    A=[i for i,k in enumerate(assignments) if k==1]
    B=[i for i,k in enumerate(assignments) if k==2]
    if any(frozenset((i,j)) not in edges for i in A for j in B):continue
    for vals in product((Q(1,2),Q(1),Q(3)),repeat=len(A)+len(B)):
        a=[Q(0)]*4;b=[Q(0)]*4
        for i,v in zip(A,vals):a[i]=v
        for i,v in zip(B,vals[len(A):]):b[i]=v
        assert game(a,b,range(4))==game(a,b,(0,1,2))+game(a,b,(1,2,3))-game(a,b,(1,2))
        counts['support_identity']+=1
levels=[Q(0),Q(1,3),Q(1),Q(2),Q(7)]
for x in product(levels,repeat=4):
    a,b,c,d=x;L=min(a,b);R=min(c,d);U=max(Q(0),b-a);V=max(Q(0),c-d)
    assert F(x)==L+R+min(U,V)
    excess=min(U-V,R)/2 if U>=V else min(V-U,L)/2
    assert H(x)-F(x)==excess
    assert F(x)<=H(x)<=Q(3,2)*F(x)
    counts['all_capacity_formula']+=1
    for mask in range(16):
        z=tuple(v if mask>>i&1 else Q(0) for i,v in enumerate(x))
        assert F(z)<=H(z)<=Q(3,2)*F(z)
        counts['coalitionwise_majorants']+=1
assert H((Q(1),Q(1),Q(1),Q(1)))==2
assert H((Q(1),Q(1),Q(1),Q(0)))==Q(3,2)
assert H((Q(0),Q(1),Q(1),Q(1)))==Q(3,2)
assert H((Q(0),Q(1),Q(1),Q(0)))==1
# Paw inequality for every allowed support pattern and exact test weights.
counts['paw_marginal_inequality']=0
paw_edges={frozenset((0,1)),frozenset((0,2)),frozenset((1,2)),frozenset((0,3))}
for assignments in product(range(3),repeat=4):
    A=[i for i,k in enumerate(assignments) if k==1]
    B=[i for i,k in enumerate(assignments) if k==2]
    if any(frozenset((i,j)) not in paw_edges for i in A for j in B):continue
    for vals in product((Q(1,2),Q(1),Q(3)),repeat=len(A)+len(B)):
        a=[Q(0)]*4;b=[Q(0)]*4
        for i,v in zip(A,vals):a[i]=v
        for i,v in zip(B,vals[len(A):]):b[i]=v
        assert game(a,b,range(4))-game(a,b,(0,1,2))<=game(a,b,(0,1,3))-game(a,b,(0,1))
        counts['paw_marginal_inequality']+=1
assert Q(2)-Q(3,2)>Q(1)-Q(1)
result={'status':'PASS','counts':counts,'scope':'Exact finite rational replay; arbitrary-capacity and positive-integral results are proved analytically in companion note.'}
Path(__file__).with_name('P4_SIGNED_BINARY_LIFT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
