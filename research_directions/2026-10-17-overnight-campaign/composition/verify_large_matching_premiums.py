#!/usr/bin/env python3
"""Exact checks of arbitrary large, disjoint public premiums."""
import ast,types,json,random
from pathlib import Path
from fractions import Fraction as Q
H=Path(__file__).resolve().parent
# Reuse definitions only, avoiding execution of the separate regression suite.
tree=ast.parse((H/'verify_matching_premium_lift.py').read_text())
keep=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
ns={'__file__':str(H/'verify_matching_premium_lift.py')}
exec(compile(ast.Module(body=keep,type_ignores=[]),'exact_definitions','exec'),ns)
duals=ns['duals'];require=ns['require']
rng=random.Random(17102026)
cases=[(6,[(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)],[0,2,4]),
 (5,[(0,1),(1,2),(2,3),(3,4),(4,0)],[0,2]),
 (4,[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)],[0,5])]
checks=0
for n,edges,heavy in cases:
 w=[Q(rng.randrange(4,31),2) if j in heavy else Q(1) for j in range(len(edges))]
 d=duals(n,edges,w);d2=duals(n,edges,[2 if j in heavy else 1 for j in range(len(edges))])
 for trial in range(12):
  own=[[Q(rng.randrange(8),rng.randrange(1,4)) for v in range(n)] for i in range(3)]
  for mask in range(8):
   c=[sum(own[i][v] for i in range(3) if mask>>i&1) for v in range(n)]
   val=min(sum(a*b for a,b in zip(c,p)) for p in d)
   val2=min(sum(a*b for a,b in zip(c,p)) for p in d2)
   remainder=sum((w[j]-2)*min(c[edges[j][0]],c[edges[j][1]]) for j in heavy)
   require(val==val2+remainder,'large matching premium identity');checks+=1
print(json.dumps({'status':'PASS','arithmetic':'exact Fraction dual vertex enumeration','coalition_profiles':checks},indent=2))
