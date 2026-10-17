"""Necessary homogeneous price LP; exact local-transition model, floating solver."""
import argparse
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path
import time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

ap=argparse.ArgumentParser()
ap.add_argument('--vertices',type=int,default=4)
ap.add_argument('--limit',type=int,default=5)
ap.add_argument('--seconds',type=int,default=40)
ap.add_argument('--method',choices=['highs','highs-ipm'],default='highs')
args=ap.parse_args()
n=args.vertices
edges=[(v,v+1) for v in range(n-1)]
covers=[z for z in itertools.product((0,1),repeat=n) if all(z[u]+z[v]>=1 for u,v in edges)]

@lru_cache(None)
def worth(c):
    return min(sum(a*b for a,b in zip(c,z)) for z in covers)

def key(c,v):
    divisor=math.gcd(*c)
    prim=tuple(x//divisor for x in c)
    return min((prim,v),(prim[::-1],n-1-v))

profiles=list(itertools.product(range(args.limit+1),repeat=n))
columns={}
for c in profiles:
    if not worth(c):
        continue
    for v in range(n):
        if c[v]:
            columns.setdefault(key(c,v),len(columns)+1)

def col(c,v):
    return columns[key(c,v)] if c[v] and worth(c) else None

rows=[];cols=[];data=[];rhs=[]
def row(terms,bound):
    r=len(rhs)
    for j,x in terms.items():
        if x:
            rows.append(r);cols.append(j);data.append(x)
    rhs.append(bound)

directions=[]
for v in range(n):
    d=[0]*n;d[v]=1;directions.append((tuple(d),0))
for u,v in edges:
    d=[0]*n;d[u]=d[v]=1;directions.append((tuple(d),1))

for c in profiles:
    f=worth(c)
    if not f:
        continue
    terms={0:-f}
    for v in range(n):
        j=col(c,v)
        if j is not None:
            terms[j]=terms.get(j,0)+c[v]
    row(terms,0)
    for d,benefit in directions:
        if any(d[v]>c[v] for v in range(n)):
            continue
        low=tuple(c[v]-d[v] for v in range(n))
        free=[v for v in range(n) if low[v]]
        for bits in itertools.product((0,1),repeat=len(free)):
            held=list(d)
            for v,bit in zip(free,bits):
                if bit:
                    held[v]=c[v]
            terms={}
            for v in range(n):
                if held[v]:
                    j=col(c,v)
                    if j is not None:
                        terms[j]=terms.get(j,0)-held[v]
                retained=held[v]-d[v]
                if retained:
                    j=col(low,v)
                    if j is not None:
                        terms[j]=terms.get(j,0)+retained
            row(terms,-benefit)

matrix=coo_matrix((data,(rows,cols)),shape=(len(rhs),len(columns)+1)).tocsr()
obj=np.zeros(len(columns)+1);obj[0]=1
started=time.monotonic()
sol=linprog(obj,A_ub=matrix,b_ub=rhs,bounds=[(1,2)]+[(0,None)]*len(columns),
 method=args.method,options={'time_limit':args.seconds})
report={'graph':'path','vertices':n,'max_integer_capacity':args.limit,
 'variables':len(columns)+1,'constraints':len(rhs),'status':sol.status,
 'message':sol.message,'method':args.method,'seconds':time.monotonic()-started,
 'factor':float(sol.fun) if sol.fun is not None else None,
 'scope':'floating necessary homogeneous-price LP; no theorem without exact certificate'}
if sol.success:
    report['max_residual']=float(np.max(matrix@sol.x-np.array(rhs)))
    report['active_dual_rows']=int(np.count_nonzero(np.abs(sol.ineqlin.marginals)>1e-10))
    report['prices']={str(c):[float(sol.x[col(c,v)]) if col(c,v) is not None else 0 for v in range(n)]
                      for c in profiles if worth(c) and math.gcd(*c)==1}
target=Path(__file__).parent/f'local_graph_outside_path{n}_{args.limit}_{args.method}.json'
target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='prices'},indent=2))
