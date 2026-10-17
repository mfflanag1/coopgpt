#!/usr/bin/env python3
"""Independent exact rational certificates for the universal integer-profit lift."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import importlib.util,json,random,ast
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('flow',HERE/'exact_huber_solver.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
# Import the independent elementary weighted-dual enumerator, definitions only.
tree=ast.parse((HERE/'verify_matching_premium_lift.py').read_text())
keep=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
ns={'__file__':str(HERE/'verify_matching_premium_lift.py')}
exec(compile(ast.Module(body=keep,type_ignores=[]),'exact_dual_enumerator','exec'),ns)
duals=ns['duals']
def require(c,m):
 if not c:raise RuntimeError(m)
def lift(n,edges,weights):
 W=max(weights,default=0);es=[]
 for (u,v),w in zip(edges,weights):
  for a in range(w):
   for b in range(w-a):es.append((u*W+a,v*W+b))
 return W,es

def unit_value(c,edges):
 # Arbitrary unit graph fractional matching equals half its bipartite double-cover
 # maxflow. Symmetrizing an oriented flow provides the original primal certificate.
 n=len(c);s,t=2*n,2*n+1;flow=h.ExactFlow(2*n+2);infinite=2*sum(c)+1
 for v,z in enumerate(c):flow.add(s,v,z);flow.add(n+v,t,z)
 for u,v in edges:flow.add(u,n+v,infinite);flow.add(v,n+u,infinite)
 f=flow.solve(s,t);x=[];degree=[Q(0)]*n
 for u,v in edges:
  z=Q(flow.used(u,n+v)+flow.used(v,n+u),2);x.append(z);degree[u]+=z;degree[v]+=z
 require(all(a<=b for a,b in zip(degree,c)) and sum(x)==f/2,'symmetrized primal')
 return f/2
rng=random.Random(17102026)
cases=[('triangle',3,[(0,1),(1,2),(2,0)],[1,5,13]),
 ('C6',6,[(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)],[1,4,2,7,3,5]),
 ('K4',4,list(combinations(range(4),2)),[1,2,3,4,5,7]),
 ('K23',5,[(i,j) for i in range(2) for j in range(2,5)],[2,1,6,4,7,3]),
 ('odd5',5,[(0,1),(1,2),(2,3),(3,4),(4,0)],[1,2,7,4,3]),
 ('weighted_star',5,[(0,j) for j in range(1,5)],[1,4,8,3]),
 ('zero_edge',4,[(0,1),(1,2),(2,3)],[0,2,3])]
checks=0;records=[]
for label,n,edges,w in cases:
 filtered=[(e,z) for e,z in zip(edges,w) if z>0];edges=[e for e,z in filtered];w=[z for e,z in filtered]
 d=duals(n,edges,w);W,le=lift(n,edges,w)
 for trial in range(8):
  owner=[[Q(rng.randrange(6),rng.randrange(1,4)) for v in range(n)] for i in range(3)]
  for mask in range(8):
   c=[sum(owner[i][v] for i in range(3) if mask>>i&1) for v in range(n)]
   p=min(d,key=lambda p:sum(a*b for a,b in zip(c,p)));p=[min(Q(W),z) for z in p]
   target=sum(a*b for a,b in zip(c,p))
   lc=[c[v] for v in range(n) for a in range(W)]
   rp=[min(Q(1),max(Q(0),p[v]-a)) for v in range(n) for a in range(W)]
   require(all(rp[u]+rp[v]>=1 for u,v in le),'clipped lifted cover')
   require(sum(a*b for a,b in zip(lc,rp))==target,'telescoping dual cost')
   actual=unit_value(lc,le)
   require(actual==target,'universal lift identity')
   checks+=1
 records.append({'case':label,'profits':w,'original_vertices':n,'original_edges':len(edges),
  'lift_vertices':n*W,'lift_edges':len(le),'coalition_profiles':64})
# Rational normalization is algebraic, recorded explicitly on an incompatible cycle.
q=6;integer=[1,3,5,2];weights=[Q(k,q) for k in integer]
edges=[(0,2),(1,2),(1,3),(0,3)];c=[Q(2,3),Q(5,2),Q(3,2),Q(7,3)]
p=min(duals(4,edges,weights),key=lambda p:sum(a*b for a,b in zip(c,p)))
target=sum(a*b for a,b in zip(c,p));W,le=lift(4,edges,integer)
actual=unit_value([c[v] for v in range(4) for a in range(W)],le)/q
require(actual==target,'rational rescaling');checks+=1
print(json.dumps({'status':'PASS','arithmetic':'Fraction throughout; independent weighted dual enumeration, clipped lifted dual, and exact symmetrized maxflow primal',
 'coalition_profiles':checks,'cases':records,'rational_example':{'profits':weights,'capacity':c,'value':target}},default=str,indent=2))
