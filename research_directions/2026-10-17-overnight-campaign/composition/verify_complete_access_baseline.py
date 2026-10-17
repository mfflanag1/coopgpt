#!/usr/bin/env python3
"""Independent exact LP-vertex checks of complete-access baseline closure."""
from fractions import Fraction as Q
from itertools import combinations
import json
import random

def require(condition,message):
    if not condition:raise RuntimeError(message)
def solve(matrix,rhs):
    n=len(rhs);a=[[Q(x) for x in matrix[i]]+[Q(rhs[i])] for i in range(n)]
    for col in range(n):
        pivot=next((r for r in range(col,n) if a[r][col]),None)
        if pivot is None:return None
        a[col],a[pivot]=a[pivot],a[col]
        t=a[col][col];a[col]=[x/t for x in a[col]]
        for r in range(n):
            if r!=col and a[r][col]:
                t=a[r][col];a[r]=[x-t*y for x,y in zip(a[r],a[col])]
    return tuple(row[-1] for row in a)
def vertices(n,edges,weights):
    rows=[];rhs=[]
    for v in range(n):
        row=[0]*n;row[v]=1;rows.append(row);rhs.append(Q(0))
    for (u,v),w in zip(edges,weights):
        if w<=0:continue
        row=[0]*n;row[u]=row[v]=1;rows.append(row);rhs.append(w)
    out=set()
    for active in combinations(range(len(rows)),n):
        p=solve([rows[j] for j in active],[rhs[j] for j in active])
        if p is not None and all(sum(x*y for x,y in zip(row,p))>=r for row,r in zip(rows,rhs)):
            out.add(p)
    require(bool(out),'dual enumeration empty')
    return out
def val(cap,dual):return min(sum(x*y for x,y in zip(cap,p)) for p in dual)

rng=random.Random(17102026)
cases=[]
matrices=[(1,1,1,2),(1,2,3,5),(1,4,8,2),(10,1,1,10),(1,10,10,1),(1,2,2,1)]
matrices += [tuple(Q(rng.randrange(9),rng.randrange(1,5)) for j in range(4)) for _ in range(16)]
for w in matrices:
    w=tuple(map(Q,w));m=min(w)
    cases.append(('K22',2,2,m,tuple(x-m for x in w)))
# Complete access with a genuinely unbounded-class pattern: positive residual
# is a spanning resource path; the concrete six-resource case is a regression.
cases.append(('K33_forest_premium',3,3,Q(2),(Q(1),Q(0),Q(0),Q(3),Q(2),Q(0),Q(0),Q(4),Q(1))))
# Identity itself is more general than the mechanism-transfer sufficient class.
cases.append(('K33_arbitrary_residual',3,3,Q(1,3),tuple(map(Q,[2,1,4,3,5,1,7,2,6]))))
results=[];comparisons=0
for label,left,right,m,q in cases:
    n=left+right;edges=[(u,left+v) for u in range(left) for v in range(right)]
    weighted=vertices(n,edges,[m+x for x in q]);residual=vertices(n,edges,q)
    for trial in range(8):
        owner=[[Q(rng.randrange(8),rng.randrange(1,5)) for v in range(n)] for i in range(3)]
        for coalition in range(8):
            cap=[sum(owner[i][v] for i in range(3) if coalition>>i&1) for v in range(n)]
            T=min(sum(cap[:left]),sum(cap[left:]))
            require(val(cap,weighted)==m*T+val(cap,residual),'baseline identity failed')
            comparisons+=1
    results.append({'case':label,'left':left,'right':right,'baseline':m,'residual_profits':q,
                    'actual_owner_count':3,'coalition_profiles':64})
print(json.dumps({'status':'PASS','arithmetic':'exact rational LP vertex enumeration',
                  'comparisons':comparisons,'cases':results,
                  'scope':'finite regression for all-real analytic identity; arbitrary residual identity does not itself prove a mechanism for that residual'},default=str,indent=2))
