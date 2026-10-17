#!/usr/bin/env python3
"""Bounded numerical positive-unit cone gate; a feasible grid is not a theorem."""
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
edges=((0,2),(0,3),(1,2),(1,3))
caps=list(product([Q(0),Q(1),Q(2),Q(3)],repeat=4))
def unit(c,mask):
    best=None
    for left in range(4):
        right=0
        for e,(u,v) in enumerate(edges):
            if mask>>e&1 and not left>>u&1:
                right|=1<<(v-2)
        value=sum(c[v] for v in range(2) if left>>v&1)+sum(c[v+2] for v in range(2) if right>>v&1)
        best=value if best is None else min(best,value)
    return best
matrix=np.asarray([[float(unit(c,m)) for m in range(1,16)] for c in caps])
results=[]
for weights in [(1,1,1,2),(1,2,3,5),(1,4,8,2),(10,1,1,10),(1,10,10,1),(1,2,2,1)]:
    vertices=mod.dual_vertices(4,edges,tuple(map(Q,weights)))
    target=np.asarray([float(min(sum(x*y for x,y in zip(c,p)) for p in vertices)) for c in caps])
    answer=linprog(np.zeros(15),A_eq=matrix,b_eq=target,bounds=(0,None),method='highs')
    results.append({'weights':weights,'success':answer.success,'message':answer.message,
                    'coefficients':None if not answer.success else [(j+1,float(x)) for j,x in enumerate(answer.x) if x>1e-8]})
print(json.dumps({'scope':'numerical finite cone scout only','profiles':len(caps),'results':results},indent=2))
