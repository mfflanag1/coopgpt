#!/usr/bin/env python3
"""Exact finite checks of the public shifted positive-sum implementation."""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations
import importlib.util,ast,json
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('approx',H/'approx_weighted_graph_mechanism.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
t=ast.parse((H/'verify_matching_premium_lift.py').read_text());ns={'__file__':str(H/'verify_matching_premium_lift.py')}
exec(compile(ast.Module(body=[z for z in t.body if isinstance(z,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'defs','exec'),ns)
check=ns['require']
cases=[]
# Overlapping shift blocks, moderate sizes, exercising repeated-block coalescing.
cases.append((Q(1),[(0,1),(1,2),(2,3)],[1,13**6,13**7]))
# Large original bit magnitudes, but small normalized public blocks.
base=121**61
cases.append((Q(1,10),list(combinations(range(4),2)),[1,Q(6,5),base,Q(6,5)*base,base*base,Q(6,5)*base*base]))
own=[[Q(1),Q(0),Q(1,2),Q(0)],[Q(0),Q(1),Q(0),Q(1,2)],[Q(0),Q(0),Q(1,2),Q(1,2)]]
records=[];coverage=transitions=0
for eps,edges,w in cases:
 d=ns['duals'](4,edges,w);out=m.payments(own,edges,w,eps)
 c=[sum(b[v] for b in own) for v in range(4)]
 F=min(sum(a*b for a,b in zip(c,p)) for p in d)
 check(out['funding']<=out['proved_funding_factor']*F,'original funding comparison')
 check(F<=out['covering_value']<=out['proved_funding_factor']/Q(3,2)*F,'positive value approximation')
 for mask in range(8):
  cap=[sum(own[i][v] for i in range(3) if mask>>i&1) for v in range(4)]
  f=min(sum(a*b for a,b in zip(cap,p)) for p in d)
  check(sum(out['owner_payments'][i] for i in range(3) if mask>>i&1)>=f,'coalition coverage');coverage+=1
 changed=[b[:] for b in own];changed[0][0]+=Q(1,2);changed[0][3]+=Q(1,3);changed[2][2]+=Q(1,2)
 after=m.payments(changed,edges,w,eps)
 check(after['owner_payments'][0]+after['owner_payments'][2]>=out['owner_payments'][0]+out['owner_payments'][2],'coalition bundle increase');transitions+=1
 records.append({'epsilon':eps,'original_max_profit_bits':max(Q(z).numerator.bit_length() for z in w),
  'unique_blocks':len(out['block_evaluations']),'largest_expanded_copy_count':max(x['copy_count'] for x in out['block_evaluations']),
  'proved_factor':out['proved_funding_factor'],'actual_funding_ratio':out['funding']/F})
print(json.dumps({'status':'PASS','arithmetic':'exact Fraction throughout','coalition_cover_checks':coverage,
 'joint_coalition_increase_checks':transitions,'cases':records},default=str,indent=2))
