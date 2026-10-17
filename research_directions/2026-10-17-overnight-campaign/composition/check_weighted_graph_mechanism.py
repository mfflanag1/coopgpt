#!/usr/bin/env python3
"""Exact all-coalition finite replay of weighted report/accounting implementation."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,random,json,ast
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('weighted',H/'weighted_graph_mechanism.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tree=ast.parse((H/'verify_matching_premium_lift.py').read_text())
ns={'__file__':str(H/'verify_matching_premium_lift.py')};keep=[z for z in tree.body if isinstance(z,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
exec(compile(ast.Module(body=keep,type_ignores=[]),'exact_dual','exec'),ns)
def check(c,s):
 if not c:raise RuntimeError(s)
rng=random.Random(17102026)
cases=[(6,[(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)],[1,4,2,7,3,5]),
 (4,[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)],[Q(1,2),Q(3,4),Q(5,4),Q(3,2),Q(1,4),2]),
 (3,[(0,1),(1,2),(2,0)],[1,2,3])]
profiles=coverage=transitions=0;examples=[]
for n,edges,w in cases:
 d=ns['duals'](n,edges,w)
 for trial in range(6):
  own=[[Q(rng.randrange(4),rng.randrange(1,4)) for v in range(n)] for i in range(3)]
  base=m.payments(own,edges,w);profiles+=1
  for mask in range(8):
   coalition=[i for i in range(3) if mask>>i&1]
   c=[sum(own[i][v] for i in coalition) for v in range(n)]
   value=min(sum(a*b for a,b in zip(c,p)) for p in d)
   paid=sum(base['owner_payments'][i] for i in coalition)
   check(paid>=value,'weighted coalition coverage');coverage+=1
   changed=[b[:] for b in own]
   for i in coalition:
    for v in range(n):changed[i][v]+=Q(rng.randrange(3),rng.randrange(1,4))
   after=m.payments(changed,edges,w);profiles+=1
   check(sum(after['owner_payments'][i] for i in coalition)>=paid,'whole-coalition bundle monotonicity');transitions+=1
  if trial==0:examples.append({'profits':w,'owner_bundles':own,'prices':base['prices'],'payments':base['owner_payments'],
   'funding':base['funding'],'production':base['value'],'copies':base['copy_count'],'lift_edges':base['lift_edge_count']})
# Explicit all-zero technology and all-zero profile.
check(m.payments([[1,2],[3,4]],[(0,1)],[0])['owner_payments']==[0,0],'zero technology')
check(m.payments([[0,0],[0,0]],[(0,1)],[Q(5,3)])['owner_payments']==[0,0],'zero profile')
print(json.dumps({'status':'PASS','arithmetic':'exact Fraction throughout','mechanism_profiles':profiles,
 'coalition_coverage_checks':coverage,'joint_report_increase_checks':transitions,'examples':examples},default=str,indent=2))
