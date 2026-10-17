#!/usr/bin/env python3
"""Finite positive-unit cone scout on C6, never a universal identity proof."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import importlib.util
import json
import numpy as np
from scipy.optimize import linprog

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('price_lp',HERE/'weighted_price_lp.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
edges=((0,3),(1,3),(1,4),(2,4),(2,5),(0,5))
caps=np.asarray(list(product(range(3),repeat=6)),dtype=int)
matrix=[]
for mask in range(1,64):
    covers=[]
    for left in range(8):
        right=0
        for e,(u,v) in enumerate(edges):
            if mask>>e&1 and not left>>u&1:
                right|=1<<(v-3)
        covers.append([(left>>v)&1 for v in range(3)]+[(right>>v)&1 for v in range(3)])
    matrix.append((caps@np.asarray(covers).T).min(axis=1))
matrix=np.asarray(matrix,dtype=float).T
results=[]
for weights in [(1,1,1,1,1,2),(1,2,3,4,5,6),(1,8,2,7,3,4),(2,3,4,1,5,7)]:
    vertices=mod.dual_vertices(6,edges,tuple(map(Q,weights)))
    target=(caps@np.asarray(vertices,dtype=float).T).min(axis=1)
    answer=linprog(np.zeros(63),A_eq=matrix,b_eq=target,bounds=(0,None),method='highs')
    results.append({'weights':weights,'success':answer.success,'message':answer.message,
                    'coefficients':None if not answer.success else [(j+1,float(x)) for j,x in enumerate(answer.x) if x>1e-8]})
print(json.dumps({'scope':'numerical finite cone scout only','profiles':len(caps),'edges':edges,'results':results},indent=2))
