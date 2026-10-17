#!/usr/bin/env python3
"""Finite exact-structure LP gate for all support-respecting linear lifts.

Each type is an original color and membership bits in three positive covers.
All admissible edges preserve those covers. A negative objective exhibits
a unit-graph lift where the old six-profile functional is negative.
"""
from fractions import Fraction as Q
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog

base=((0,3),(1,3),(1,4),(2,4),(2,5),(0,5))
positive=((0,1,1,1,1,1),(1,0,1,1,0,1),(1,1,1,1,1,0))
active=[sum(1<<j for j,p in enumerate(positive) if p[v]) for v in range(6)]
types=[(v,mask) for v in range(6) for mask in range(8) if mask&~active[v]==0]
edges=[]
for i,(u,mu) in enumerate(types):
    for j,(v,mv) in enumerate(types):
        if (u,v) in base and (mu|mv)&(active[u]&active[v])==active[u]&active[v]:
            edges.append((i,j))
N=len(types);M=len(edges)
objective=np.asarray([mask.bit_count() for v,mask in types]+[-1]*M,dtype=float)
rows=[]
for i,(v,mask) in enumerate(types):
    for neighbor in range(6):
        if (v,neighbor) not in base and (neighbor,v) not in base:continue
        row=np.zeros(N+M);row[i]=-1
        for e,(a,b) in enumerate(edges):
            if (a==i and types[b][0]==neighbor) or (b==i and types[a][0]==neighbor):row[N+e]=1
        rows.append(row)
answer=linprog(objective,A_ub=rows,b_ub=np.zeros(len(rows)),
               A_eq=[np.r_[np.ones(N),np.zeros(M)]],b_eq=[1],bounds=(0,None),method='highs')
result={'status':'numerical scout; exact replay needed','success':answer.success,
        'message':answer.message,'types':len(types),'admissible_edges':len(edges)}
if answer.success:
    selected=[i for i in range(N) if answer.x[i]>1e-8]
    result.update({'objective':answer.fun,
       'rows':[{'id':i,'original_resource':types[i][0],'positive_cover_mask':types[i][1],
                'capacity_coefficient':str(Q(float(answer.x[i])).limit_denominator(100000))} for i in selected],
       'lift_edges':[(i,j) for i,j in edges if i in selected and j in selected],
       'negative_flow_certificate':[(edges[e],str(Q(float(answer.x[N+e])).limit_denominator(100000)))
                                    for e in range(M) if answer.x[N+e]>1e-8]})
print(json.dumps(result,indent=2))
