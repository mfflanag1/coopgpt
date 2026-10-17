#!/usr/bin/env python3
"""Exact dual-enumeration/original-primal-certificate regression for lift theorem."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import importlib.util,random,json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('huber',HERE/'exact_huber_solver.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def require(c,m):
 if not c:raise RuntimeError(m)
def solve(matrix,rhs):
 n=len(rhs);a=[[Q(x) for x in matrix[i]]+[Q(rhs[i])] for i in range(n)]
 for j in range(n):
  pivot=next((k for k in range(j,n) if a[k][j]),None)
  if pivot is None:return None
  a[j],a[pivot]=a[pivot],a[j];z=a[j][j];a[j]=[x/z for x in a[j]]
  for k in range(n):
   if k!=j and a[k][j]:
    z=a[k][j];a[k]=[x-z*y for x,y in zip(a[k],a[j])]
 return tuple(row[-1] for row in a)
def duals(n,edges,w):
 rows=[];rhs=[]
 for v in range(n):
  row=[0]*n;row[v]=1;rows.append(row);rhs.append(Q(0))
 for (u,v),x in zip(edges,w):
  row=[0]*n;row[u]=row[v]=1;rows.append(row);rhs.append(Q(x))
 out=set()
 for ix in combinations(range(len(rows)),n):
  p=solve([rows[k] for k in ix],[rhs[k] for k in ix])
  if p is not None and all(sum(a*b for a,b in zip(row,p))>=z for row,z in zip(rows,rhs)):out.add(p)
 require(out,'no dual vertices');return out
def lift(n,edges,heavy):
 color=list(range(n));es=list(edges)
 for j in heavy:
  u,v=edges[j];a=len(color);color.extend([u,v]);es.extend([(a,v),(u,a+1)])
 return color,es
def production(c,edges):return sum(h.certificate(c,edges)['lambda'])
cases=[('C6_one',6,[(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)],[5]),
 ('C6_two',6,[(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)],[0,3]),
 ('C6_perfect',6,[(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)],[0,2,4]),
 ('triangle',3,[(0,1),(1,2),(2,0)],[0]),
 ('K4',4,list(combinations(range(4),2)),[0,5]),
 ('path5',5,[(0,1),(1,2),(2,3),(3,4)],[0,3]),
 ('odd5',5,[(0,1),(1,2),(2,3),(3,4),(4,0)],[0,2])]
rng=random.Random(17102026);checked=0;out=[]
for label,n,edges,heavy in cases:
 w=[2 if j in heavy else 1 for j in range(len(edges))];d=duals(n,edges,w);color,le=lift(n,edges,heavy)
 for trial in range(12):
  owners=[[Q(rng.randrange(7),rng.randrange(1,4)) for v in range(n)] for i in range(3)]
  for mask in range(8):
   c=[sum(owners[i][v] for i in range(3) if mask>>i&1) for v in range(n)]
   target=min(sum(a*b for a,b in zip(c,p)) for p in d)
   actual=production([c[v] for v in color],le)
   require(target==actual,f'identity failed {label} {c}');checked+=1
 out.append({'case':label,'coalition_profiles':96,'dual_vertices':len(d),'lift_vertices':len(color)})
# Replay six-profile functional exactly.
edges=cases[0][2];color,le=lift(6,edges,[5])
profiles=((0,1,1,1,0,1),(0,1,1,1,1,1),(1,0,1,1,0,1),(1,0,1,1,1,0),(1,1,0,0,1,1),(1,1,1,1,1,0))
values=[production([Q(c[v]) for v in color],le) for c in profiles]
functional=sum(s*v for s,v in zip((-1,1,1,-1,-1,1),values));require(functional==-1,'functional witness')
# Scaled-leaf shortcut exact counterexample.
c=list(map(Q,[9,9,10,10,11,8]));d=duals(6,edges,[1,1,1,1,1,Q(3,2)])
target=min(sum(a*b for a,b in zip(c,p)) for p in d)
lc=[c[v] for v in color];lc[-2]/=2;lc[-1]/=2;actual=production(lc,le)
require(target==32 and actual==Q(65,2),'scaled leaf witness')
# Nonmatching doubled-star obstruction.
es=[(0,1),(0,2),(0,3)];co,ls=lift(4,es,[0,1,2]);star=production([Q(1) for v in co],ls)
require(star>=3,'star obstruction')
print(json.dumps({'status':'PASS','arithmetic':'Fraction throughout; weighted dual vertices vs certified unit primal/dual',
 'coalition_profiles':checked,'cases':out,'six_profile_values':values,'six_profile_functional':functional,
 'scaled_leaf_counterexample':{'capacity':c,'weighted':target,'lift':actual},
 'nonmatching_star':{'weighted':2,'lift':star}},default=str,indent=2))
