#!/usr/bin/env python3
"""Exact LP certificates for failed nested doubled-matching interpolation."""
from fractions import Fraction as Q
import json
# Seven-vertex path, in path order. Heavy edges 0,2,4 form a matching.
c=list(map(Q,[1,4,3,3,3,2,1]));edges=[(i,i+1) for i in range(6)]
weights=[Q(7,4),Q(1),Q(5,4),Q(1),Q(3,2),Q(1)]
# Use only exact rational dual vertex enumeration to generate certificates.
from itertools import combinations
def check(c,m):
 if not c:raise RuntimeError(m)
def solve(a,b):
 n=len(b);a=[[Q(x) for x in row]+[Q(z)] for row,z in zip(a,b)]
 for j in range(n):
  k=next((k for k in range(j,n) if a[k][j]),None)
  if k is None:return None
  a[k],a[j]=a[j],a[k];t=a[j][j];a[j]=[x/t for x in a[j]]
  for k in range(n):
   if k!=j and a[k][j]:
    t=a[k][j];a[k]=[x-t*y for x,y in zip(a[k],a[j])]
 return [row[-1] for row in a]
def dual(w):
 rows=[];rhs=[]
 for i in range(7):
  row=[0]*7;row[i]=1;rows.append(row);rhs.append(0)
 for (u,v),z in zip(edges,w):
  row=[0]*7;row[u]=row[v]=1;rows.append(row);rhs.append(z)
 feasible=[]
 for ix in combinations(range(13),7):
  p=solve([rows[j] for j in ix],[rhs[j] for j in ix])
  if p is not None and all(sum(a*b for a,b in zip(row,p))>=z for row,z in zip(rows,rhs)):feasible.append(p)
 return min(feasible,key=lambda p:sum(a*b for a,b in zip(c,p)))
ws=[weights,[2,1,2,1,2,1],[2,1,1,1,2,1],[2,1,1,1,1,1],[1]*6]
flows=[[1,2,1,2,1,1],[1,0,3,0,2,0],[1,3,0,1,2,0],[1,3,0,3,0,1],[1,3,0,3,0,1]]
certs=[]
for w,x in zip(ws,flows):
 p=dual(w);degree=[Q(0)]*7
 for (u,v),z in zip(edges,x):degree[u]+=z;degree[v]+=z
 check(all(z>=0 for z in x) and all(a<=b for a,b in zip(degree,c)),'primal feasibility')
 primal=sum(a*b for a,b in zip(w,x));dualval=sum(a*b for a,b in zip(c,p))
 check(primal==dualval,'exact primal dual equality')
 certs.append({'weights':w,'primal_flow':x,'dual_prices':p,'value':primal})
check(certs[0]['value']==Q(19,2),'weighted value')
layer=sum(z['value'] for z in certs[1:])/4
check(layer==Q(39,4),'layer value')
print(json.dumps({'status':'PASS','capacity':c,'path_edges':edges,'certificates':certs,
 'weighted_value':certs[0]['value'],'nested_binary_layer_sum':layer,'gap':layer-certs[0]['value']},default=str,indent=2))
