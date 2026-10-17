#!/usr/bin/env python3
"""Exact finite checks of same-owner double-cover/source-price production identity.

Original weighted production: enumerate all fractional-cover LP vertices.
Layer production: enumerate all left subsets of the bipartite vertex-cover LP.
These are separate exact algorithms. Analytic proof remains in the theorem note.
No assertion statements: every check survives optimized execution.
"""
from fractions import Fraction as Q
from itertools import combinations
import json
import random

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def solve(matrix,rhs):
    n=len(rhs)
    a=[[Q(x) for x in matrix[i]]+[Q(rhs[i])] for i in range(n)]
    for col in range(n):
        pivot=next((r for r in range(col,n) if a[r][col]),None)
        if pivot is None:
            return None
        a[col],a[pivot]=a[pivot],a[col]
        t=a[col][col]
        a[col]=[x/t for x in a[col]]
        for r in range(n):
            if r!=col and a[r][col]:
                t=a[r][col]
                a[r]=[x-t*y for x,y in zip(a[r],a[col])]
    return tuple(row[-1] for row in a)

def weighted_dual_vertices(n,edges,weights):
    rows=[];rhs=[]
    for v in range(n):
        row=[0]*n;row[v]=1;rows.append(row);rhs.append(Q(0))
    for (u,v),w in zip(edges,weights):
        row=[0]*n;row[u]=row[v]=1;rows.append(row);rhs.append(w)
    answer=set()
    for active in combinations(range(len(rows)),n):
        p=solve([rows[j] for j in active],[rhs[j] for j in active])
        if p is not None and all(sum(x*y for x,y in zip(row,p))>=r for row,r in zip(rows,rhs)):
            answer.add(p)
    require(bool(answer),'nonempty exact dual vertex set')
    return tuple(sorted(answer))

def additive_potentials(n,edges,weights):
    adjacency=[[] for _ in range(n)]
    for (u,v),w in zip(edges,weights):
        adjacency[u].append((v,w));adjacency[v].append((u,w))
    sign=[None]*n;offset=[None]*n;alpha=[None]*n
    for root in range(n):
        if sign[root] is not None:
            continue
        sign[root]=1;offset[root]=Q(0)
        component=[];stack=[root];fixed=None
        while stack:
            u=stack.pop();component.append(u)
            for v,w in adjacency[u]:
                if sign[v] is None:
                    sign[v]=-sign[u];offset[v]=w-offset[u];stack.append(v)
                else:
                    coefficient=sign[u]+sign[v]
                    remainder=w-offset[u]-offset[v]
                    if coefficient==0:
                        if remainder:
                            return None
                    else:
                        forced=remainder/coefficient
                        if fixed is not None and forced!=fixed:
                            return None
                        fixed=forced
        parameter=fixed if fixed is not None else Q(0)
        for v in component:
            alpha[v]=sign[v]*parameter+offset[v]
    require(all(alpha[u]+alpha[v]==w for (u,v),w in zip(edges,weights)),'potential equation')
    return tuple(alpha)

def fixed_layers(n,edges,alpha):
    K=max(abs(x) for x in alpha)
    a=[K-x for x in alpha];d=[K+x for x in alpha]
    breaks=sorted(set(a+d))
    oriented=[(u,v) for u,v in edges]+[(v,u) for u,v in edges]
    layers=[]
    for lo,hi in zip(breaks,breaks[1:]):
        t=(lo+hi)/2
        active=[(u,v) for u,v in oriented if a[u]<=t<d[v]]
        covers=[]
        for left in range(1<<n):
            right=0
            for u,v in active:
                if not (left>>u)&1:
                    right|=1<<v
            covers.append((left,right))
        layers.append((hi-lo,covers))
    return layers

def layer_value(n,cap,layers):
    total=Q(0)
    for length,covers in layers:
        optimum=min(sum(cap[v]*(((left>>v)&1)+((right>>v)&1))/2 for v in range(n))
                    for left,right in covers)
        total+=length*optimum
    return total

cases=[
 ('weighted_path4',4,[(0,1),(1,2),(2,3)],[Q(1),Q(3),Q(1)]),
 ('weighted_fork5',5,[(0,1),(1,2),(1,3),(3,4)],[Q(2),Q(1,3),Q(5),Q(7,2)]),
 ('negative_potential_triangle',3,[(0,1),(1,2),(0,2)],[Q(1),Q(1),Q(100)]),
 ('weighted_odd_cycle5',5,[(0,1),(1,2),(2,3),(3,4),(0,4)],[Q(1),Q(4),Q(2),Q(7),Q(3)]),
 ('compatible_even_cycle4',4,[(0,1),(1,2),(2,3),(0,3)],[Q(1),Q(2),Q(4),Q(3)]),
 ('additive_complete4',4,[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)],
  [Q(3),Q(4),Q(5),Q(5),Q(6),Q(7)]),
]
rng=random.Random(20261017)
results=[];comparisons=0
for name,n,edges,weights in cases:
    alpha=additive_potentials(n,edges,weights)
    require(alpha is not None,'represented graph')
    dual=weighted_dual_vertices(n,edges,weights)
    layers=fixed_layers(n,edges,alpha)
    for trial in range(12):
        owner_bundles=[[Q(rng.randrange(7),rng.randrange(1,5)) for v in range(n)] for i in range(3)]
        for coalition in range(8):
            cap=[sum(owner_bundles[i][v] for i in range(3) if coalition>>i&1) for v in range(n)]
            original=min(sum(x*y for x,y in zip(cap,p)) for p in dual)
            layered=layer_value(n,cap,layers)
            require(original==layered,f'{name}: production mismatch trial{trial} coalition{coalition}')
            comparisons+=1
    results.append({'graph':name,'vertices':n,'edges':edges,'profits':weights,'potentials':alpha,
                    'public_layers':len(layers),'actual_owner_count':3,
                    'coalition_profiles_checked':96})
require(additive_potentials(4,[(0,1),(1,2),(2,3),(0,3)],list(map(Q,[1,1,1,2]))) is None,
        'incompatible even cycle must be rejected')
print(json.dumps({'status':'PASS','arithmetic':'exact rational','comparisons':comparisons,
 'cases':results,'negative_scope_check':'incompatible even cycle rejected',
 'scope':'finite verification of exact production reduction for every coalition in sampled fixed-owner profiles; analytic theorem separate'},
 default=str,indent=2))
