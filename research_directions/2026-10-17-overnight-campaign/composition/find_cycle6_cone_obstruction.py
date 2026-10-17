#!/usr/bin/env python3
"""Find a finite Farkas witness; separate exact replay must certify it."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import importlib.util
import json
import numpy as np
from scipy.optimize import linprog
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lp',HERE/'weighted_price_lp.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
edges=((0,3),(1,3),(1,4),(2,4),(2,5),(0,5));weights=(1,1,1,1,1,2)
caps=np.asarray(list(product(range(2),repeat=6)),dtype=int)
matrix=[]
for mask in range(64):
    covers=[]
    for left in range(8):
        right=0
        for e,(u,v) in enumerate(edges):
            if mask>>e&1 and not left>>u&1:right|=1<<(v-3)
        covers.append([(left>>v)&1 for v in range(3)]+[(right>>v)&1 for v in range(3)])
    matrix.append((caps@np.asarray(covers).T).min(axis=1))
A=np.asarray(matrix,dtype=float).T
vertices=mod.dual_vertices(6,edges,tuple(map(Q,weights)))
b=(caps@np.asarray(vertices,dtype=float).T).min(axis=1)
R=len(caps)
answer=linprog(np.ones(2*R),A_ub=np.hstack((-A.T,A.T)),b_ub=np.zeros(64),
               A_eq=np.asarray([np.r_[b,-b]]),b_eq=[-1],bounds=(0,None),method='highs')
result={'success':answer.success,'message':answer.message,'edges':edges,'weights':weights}
if answer.success:
    y=answer.x[:R]-answer.x[R:]
    result['profiles']=[{'capacity':caps[j].tolist(),'coefficient':str(Q(float(z)).limit_denominator(10000)),
                         'weighted_value':str(Q(float(b[j])).limit_denominator(10000))}
                        for j,z in enumerate(y) if abs(z)>1e-8]
    result['l1']=answer.fun
print(json.dumps(result,indent=2))
