#!/usr/bin/env python3
"""Exact independent dual normalization/cone/coupling diagnostics; no LP solver."""
from collections import defaultdict
from fractions import Fraction as Q
from itertools import combinations, permutations, product
from pathlib import Path
import json


def rank(matrix):
    a = [list(map(Q,row)) for row in matrix]
    at = 0
    for col in range(len(a[0])):
        pivot = next((j for j in range(at,len(a)) if a[j][col]),None)
        if pivot is None:
            continue
        a[at],a[pivot] = a[pivot],a[at]
        scale = a[at][col]
        a[at] = [v/scale for v in a[at]]
        for j in range(len(a)):
            if j != at and a[j][col]:
                fac = a[j][col]
                a[j] = [x-fac*y for x,y in zip(a[j],a[at])]
        at += 1
        if at == len(a):
            break
    return at


def graph_components(vertices,edges):
    adjacency = {v:set() for v in vertices}
    for a,b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen=set()
    components=0
    for start in vertices:
        if start in seen:
            continue
        components += 1
        stack=[start]
        while stack:
            v=stack.pop()
            if v in seen:
                continue
            seen.add(v)
            stack.extend(adjacency[v]-seen)
    return components,adjacency


def certificate():
    bundles={'0':(0,0,0),'L':(1,0,1),'R':(0,1,1)}
    lows=sorted(set(permutations(('0','L','R'))))
    highs=sorted(set(permutations(('L','L','R'))) | set(permutations(('R','R','L'))))
    worth=lambda p,C:min(sum(bundles[p[i]][j] for i in C) for j in range(3))
    g=defaultdict(Q)
    rows=[]
    for p in lows:
        rows.append({'kind':'coverage','profile':p,'coalition':(0,1,2),'weight':Q(1,4),'rhs':1})
    for p in highs:
        for C in combinations(range(3),2):
            if p[C[0]] != p[C[1]]:
                rows.append({'kind':'coverage','profile':p,'coalition':C,'weight':Q(1,2),'rhs':1})
    arcs=[]
    columns=[]
    for low in lows:
        zero=low.index('0')
        for typ in ('L','R'):
            incumbent=low.index(typ)
            high=list(low)
            high[zero]=typ
            high=tuple(high)
            C=tuple(sorted((zero,incumbent)))
            assert high in highs
            assert all(high[i]==low[i] for i in range(3) if i not in C)
            assert all(bundles[high[i]][j]>=bundles[low[i]][j] for i in C for j in range(3))
            col={(high,i):Q(1) for i in C}
            col.update({(low,i):Q(-1) for i in C})
            columns.append(col)
            arcs.append((low,high,C))
            rows.append({'kind':'tcwm','low':low,'high':high,'coalition':C,'weight':Q(1,4),'rhs':0})
    numerator=Q(0)
    for row in rows:
        w=row['weight']
        if row['kind']=='coverage':
            assert worth(row['profile'],row['coalition'])==row['rhs']
            numerator+=w*row['rhs']
            for i in row['coalition']:
                g[row['profile'],i]+=w
        else:
            for i in row['coalition']:
                g[row['high'],i]+=w
                g[row['low'],i]-=w
    for p in highs:
        assert worth(p,range(3))==1
        assert all(g[p,i]==1 for i in range(3))
    for p in lows:
        assert all(g[p,i]==(-Q(1,4) if p[i]=='0' else 0) for i in range(3))
    denominator=Q(len(highs))
    assert numerator/denominator==Q(5,4)
    vertices=set(lows+highs)
    comps,adj=graph_components(vertices,[(l,h) for l,h,C in arcs])
    assert comps==1 and len(arcs)==len(vertices)==12
    assert all(len(v)==2 for v in adj.values())
    per_coalition=[]
    for C in combinations(range(3),2):
        edges=[(l,h) for l,h,coal in arcs if coal==C]
        verts={p for edge in edges for p in edge}
        comp,_=graph_components(verts,edges)
        assert len(edges)==len(verts)-comp
        assert not ({l for l,h in edges}&{h for l,h in edges})
        per_coalition.append({'coalition':C,'edges':len(edges),'vertices':len(verts),'components':comp})
    coords=[(p,i) for p in sorted(vertices) for i in range(3)]
    matrix=[[col.get(coord,Q(0)) for col in columns] for coord in coords]
    actual_rank=rank(matrix)
    assert actual_rank==len(columns)==12
    for l,h,C in arcs:
        incumbent=next(i for i in C if l[i]!='0')
        assert sum((l,incumbent) in col for col in columns)==1
    serial_rows=[{key:(str(v) if isinstance(v,Q) else v) for key,v in row.items()} for row in rows]
    return {'arity':3,'owners':3,'protected_size':2,'coverage_rows':18,
            'comparison_rows':12,'budget_rows':6,'numerator':str(numerator),
            'denominator':str(denominator),'lower_ratio':'5/4',
            'unlabelled_graph':'one 12-cycle','actual_comparison_matrix_rank':actual_rank,
            'per_coalition_forests':per_coalition,'rows':serial_rows}


def interval_decomposition(x,t):
    """Construct a distribution over subsets <=t with specified marginals x."""
    assert all(0<=v<=1 for v in x) and sum(x)<=t
    if t==0:
        return {():Q(1)}
    original=len(x)
    augmented=list(x)
    missing=Q(t)-sum(x)
    while missing:
        take=min(missing,Q(1))
        augmented.append(take)
        missing-=take
    endpoints=[Q(0)]
    for v in augmented:
        endpoints.append(endpoints[-1]+v)
    assert endpoints[-1]==t
    breaks=sorted({Q(0),Q(1)}|{v-v.numerator//v.denominator for v in endpoints})
    distribution=defaultdict(Q)
    for lo,hi in zip(breaks,breaks[1:]):
        u=(lo+hi)/2
        selected=tuple(j for j in range(original)
                       if any(endpoints[j]<=u+z<endpoints[j+1] for z in range(t)))
        assert len(selected)<=t
        distribution[selected]+=hi-lo
    assert sum(distribution.values())==1
    assert all(sum(w for subset,w in distribution.items() if i in subset)==x[i]
               for i in range(original))
    return distribution


def cone_checks():
    cases=0
    max_support=0
    for m in range(6):
        for t in range(m+1):
            for x in product((Q(0),Q(1,2),Q(1)),repeat=m):
                if sum(x)>t:
                    continue
                distribution=interval_decomposition(x,t)
                # Attach any fixed changed set D={0}; protect D union J.
                M=Q(3,2)
                changed_weight=sum(M*w for w in distribution.values())
                assert changed_weight==M
                assert all(len(subset)+1<=t+1 for subset in distribution)
                assert all(sum(M*w for subset,w in distribution.items() if i in subset)==M*x[i]
                           for i in range(m))
                cases+=1
                max_support=max(max_support,len(distribution))
    return {'exact_grid_decompositions':cases,'unchanged_owner_grid':['0','1/2','1'],
            'max_unchanged_owners':5,'largest_constructed_support':max_support}


def elementary_transforms():
    f=min
    p0=(Q(0),Q(0),Q(0)); p1=(Q(1),Q(0),Q(0)); p2=(Q(1),Q(1),Q(1))
    old=f(tuple(b-a for a,b in zip(p0,p1)))+f(tuple(b-a for a,b in zip(p1,p2)))
    new=f(tuple(b-a for a,b in zip(p0,p2)))
    assert old==0 and new==1
    a=(1,0,0); b=(0,1,0); x=(1,2,1); y=(2,1,1)
    cost=lambda l,h:Q(min(v-u for u,v in zip(l,h)))
    original={(a,x):Q(1),(a,y):Q(1),(b,x):Q(1),(b,y):Q(1)}
    reduced={(a,y):Q(2),(b,x):Q(2)}
    def divergence(edges):
        result=defaultdict(Q)
        for (l,h),w in edges.items():
            result[l]-=w; result[h]+=w
        return dict(result)
    assert divergence(original)==divergence(reduced)
    old_cycle=sum(w*cost(l,h) for (l,h),w in original.items())
    new_cycle=sum(w*cost(l,h) for (l,h),w in reduced.items())
    assert old_cycle==2 and new_cycle==4
    return {'path_outside_objective_before':str(old),'path_outside_objective_after':str(new),
            'transport_cycle_objective_before':str(old_cycle),
            'transport_cycle_objective_after':str(new_cycle),'balances_preserved':True}


def main():
    result={'status':'PASS','arithmetic':'fractions.Fraction',
            'scope':'finite exact diagnostics for analytic lemmas, no funding upper claim',
            'coupled_arity3_certificate':certificate(),
            'comparison_cone':cone_checks(),'elementary_transforms':elementary_transforms()}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    compact={k:v for k,v in result.items() if k!='coupled_arity3_certificate'}
    compact['certificate_summary']={k:v for k,v in result['coupled_arity3_certificate'].items() if k not in ('rows','per_coalition_forests')}
    print(json.dumps(compact,sort_keys=True))


if __name__=='__main__':
    main()
