#!/usr/bin/env python3
"""Finite necessary homogeneous-price OUT LP. Numerical lower-bound discovery only.

The aggregate-price representation theorem justifies these as necessary for
uniform-over-owner-count mechanisms; no finite actual-owner rate is inferred.
"""
import argparse,itertools,json,math,time
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def run(name,limit,geometric=False):
    graphs={'edge':(2,[(0,1)]),'path4':(4,[(0,1),(1,2),(2,3)]),
            'triangle':(3,[(0,1),(1,2),(0,2)]),
            'cycle4':(4,[(0,1),(1,2),(2,3),(0,3)]),
            'K4':(4,list(itertools.combinations(range(4),2)))}
    d,edges=graphs[name]
    levels=[0]+[4**k for k in range(limit)] if geometric else list(range(limit+1))
    profiles=list(itertools.product(levels,repeat=d))
    covers=[z for z in itertools.product((0,1,2),repeat=d)
            if all(z[u]+z[v]>=2 for u,v in edges)]
    from functools import lru_cache
    @lru_cache(None)
    def value(c):return min(sum(x*y for x,y in zip(c,z)) for z in covers)/2
    def primitive(c):
        g=math.gcd(*c)
        return tuple(x//g for x in c) if g else c
    representatives={c:primitive(c) for c in profiles}
    columns={};nextcol=1
    for c in sorted(set(representatives.values())):
        for v in range(d):
            if c[v]:columns[c,v]=nextcol;nextcol+=1
    def col(c,v):return columns.get((representatives[c],v))
    rr=[];cc=[];data=[];rhs=[]
    def row(terms,b):
        # terms already combined; no nonzero is assigned to absent-price slots.
        r=len(rhs)
        for j,x in terms.items():
            if x:rr.append(r);cc.append(j);data.append(x)
        rhs.append(b)
    for c in profiles:
        if not any(c):continue
        row({0:-value(c),**{col(c,v):c[v] for v in range(d) if c[v]}},0)
        for u,v in edges:
            if c[u] and c[v]:row({col(c,u):-1,col(c,v):-1},-1)
        for low in itertools.product(*([x for x in levels if x<=cv] for cv in c)):
            if low==c:continue
            withdrawal=tuple(x-y for x,y in zip(c,low))
            variable=[v for v in range(d) if low[v]]
            for highheld in itertools.product((0,1),repeat=len(variable)):
                holding=list(withdrawal)
                for v,bit in zip(variable,highheld):
                    if bit:holding[v]=c[v]
                terms={}
                for v in range(d):
                    if holding[v]:
                        j=col(c,v);terms[j]=terms.get(j,0)-holding[v]
                    retained=holding[v]-withdrawal[v]
                    if retained:
                        j=col(low,v);terms[j]=terms.get(j,0)+retained
                row(terms,-value(withdrawal))
    A=coo_matrix((data,(rr,cc)),shape=(len(rhs),nextcol)).tocsr()
    objective=np.zeros(nextcol);objective[0]=1
    start=time.monotonic()
    result=linprog(objective,A_ub=A,b_ub=rhs,bounds=[(1,2)]+[(0,None)]*(nextcol-1),
                   method='highs',options={'time_limit':120})
    report={'graph':name,'limit':limit,'levels':levels,'variables':nextcol,'constraints':len(rhs),
            'status':int(result.status),'message':result.message,'seconds':time.monotonic()-start,
            'factor':float(result.fun) if result.fun is not None else None,
            'scope':'floating finite necessary LP; no certified theorem until exact dual reconstruction'}
    if result.success:
        report['max_residual']=float(np.max(A@result.x-np.array(rhs)))
        report['prices']={str(c):[float(result.x[col(c,v)]) if c[v] else 0 for v in range(d)]
                          for c in sorted(set(representatives.values()))}
    label='geom' if geometric else 'uniform'
    path=Path(__file__).resolve().parent/f'graph_outside_price_{name}_{label}_{limit}.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='prices'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('graph');p.add_argument('limit',type=int)
    p.add_argument('--geometric',action='store_true')
    a=p.parse_args();run(a.graph,a.limit,a.geometric)
