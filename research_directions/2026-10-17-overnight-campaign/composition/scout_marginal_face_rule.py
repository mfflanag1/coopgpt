#!/usr/bin/env python3
"""Bounded exact falsification of a new net-face potential-free candidate."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import importlib.util,random,json
HERE=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=load('v',HERE/'verify_two_sparse_lift.py');f=load('f',HERE/'logarithmic_face_symbolic.py')
def duals(n,edges):
 rows=[];rhs=[]
 for j in range(n):row=[0]*n;row[j]=1;rows.append(row);rhs.append(0)
 for e in edges:rows.append([int(j in e) for j in range(n)]);rhs.append(1)
 out=set()
 for ix in combinations(range(len(rows)),n):
  p=v.linear_solve([rows[k] for k in ix],[rhs[k] for k in ix])
  if p is not None and all(sum(a*b for a,b in zip(row,p))>=z for row,z in zip(rows,rhs)):out.add(p)
 v.check(out,'no vertices');return out

def payments(owners,forms):
 n=len(owners[0]);C=[sum(o[j] for o in owners) for j in range(n)];prices=[]
 for j in range(n):
  if not C[j]:prices.append(Q(0));continue
  lines=[(p[j]*C[j],sum(p[l]*C[l] for l in range(n) if l!=j)) for p in forms]
  env=f.envelope(lines);raw=sum(a*(hi-lo)+b*(hi*hi-lo*lo)/2 for lo,hi,a,b in env['segments'])
  outside=min(b for a,b in lines);H=raw-outside/2
  v.check(H>=0,'negative net face');prices.append(H/C[j])
 return [sum(a*b for a,b in zip(o,prices)) for o in owners],prices
cases=[('path4',4,[(0,1),(1,2),(2,3)]),('star4',4,[(0,1),(0,2),(0,3)]),
 ('triangle',3,[(0,1),(1,2),(2,0)]),('rank3_overlap',4,[(0,1,2),(1,2,3)]),
 ('rank3_huber_obstruction',6,[(2,3,5),(2,3,4),(2,4,5),(0,1,2),(0,4,5)])]
rng=random.Random(17100611);count=0
for label,n,edges in cases:
 forms=duals(n,edges)
 for trial in range(3000):
  owners=[[Q(rng.randrange(6)) for _ in range(n)] for _ in range(2)];smaller=[o[:] for o in owners]
  for j in range(n):smaller[0][j]=Q(rng.randrange(int(owners[0][j])+1))
  high,ph=payments(owners,forms);low,pl=payments(smaller,forms);count+=1
  if low[0]>high[0]:
   print(json.dumps({'status':'EXACT_OBSTRUCTION','case':label,'edges':edges,'dual_vertices':sorted(forms),'owners_true':owners,'owners_low':smaller,'pay_true':high,'pay_low':low,'price_true':ph,'price_low':pl,'gain':low[0]-high[0],'profiles_tested':count},default=str,indent=2));raise SystemExit
print(json.dumps({'status':'NO_VIOLATION_IN_BOUNDED_CHECK','profiles':count}))
