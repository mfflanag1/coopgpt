#!/usr/bin/env python3
"""Exact fractional-capacity replay of separated weight-block aggregation."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import ast,random,json
H=Path(__file__).resolve().parent
tr=ast.parse((H/'verify_matching_premium_lift.py').read_text());ns={'__file__':str(H/'verify_matching_premium_lift.py')}
exec(compile(ast.Module(body=[z for z in tr.body if isinstance(z,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'defs','exec'),ns)
solve=ns['solve'];duals=ns['duals'];require=ns['require']
def primal(c,es,w):
 m=len(es)
 if not m:return []
 rows=[];rhs=[]
 for v,z in enumerate(c):rows.append([int(v in e) for e in es]);rhs.append(z)
 for j in range(m):
  row=[0]*m;row[j]=-1;rows.append(row);rhs.append(0)
 feasible=[]
 for ix in combinations(range(len(rows)),m):
  x=solve([rows[i] for i in ix],[rhs[i] for i in ix])
  if x is not None and all(sum(a*b for a,b in zip(row,x))<=z for row,z in zip(rows,rhs)):feasible.append(x)
 require(feasible,'empty primal vertex set')
 return list(max(feasible,key=lambda x:sum(a*b for a,b in zip(x,w))))
def value(c,d):return min(sum(a*b for a,b in zip(c,p)) for p in d)
rng=random.Random(17102026);edges=list(combinations(range(4),2));checks=0;maxratio=Q(1);maxlossratio=Q(0)
for trial in range(16):
 levels=[rng.randrange(3) for e in edges]
 w=[Q((1+rng.randrange(2))*9**k) for k in levels]
 groups=[([e for e,k in zip(edges,levels) if k==j],[z for z,k in zip(w,levels) if k==j]) for j in sorted(set(levels))]
 d=duals(4,edges,w)
 owners=[[Q(rng.randrange(6),rng.randrange(1,4)) for v in range(4)] for i in range(3)]
 for mask in range(8):
  c=[sum(owners[i][v] for i in range(3) if mask>>i&1) for v in range(4)]
  residual=c[:];accepted=[];sumblocks=Q(0);total=Q(0);removed=Q(0);charge=Q(0)
  for es,ws in reversed(groups):
   x=primal(c,es,ws);before=sum(a*b for a,b in zip(x,ws));sumblocks+=before
   higher=[c[v]-residual[v] for v in range(4)]
   initialoverflow=[max(Q(0),sum(x[j] for j,e in enumerate(es) if v in e)-residual[v]) for v in range(4)]
   deleted=Q(0)
   for v in range(4):
    excess=max(Q(0),sum(x[j] for j,e in enumerate(es) if v in e)-residual[v])
    for j,e in enumerate(es):
     if v in e and excess:
      z=min(excess,x[j]);x[j]-=z;excess-=z;deleted+=z
    require(excess==0,'trim cannot meet residual')
   require(deleted<=sum(initialoverflow)<=sum(higher),'capacity deletion charge')
   after=sum(a*b for a,b in zip(x,ws));require(before-after<=max(ws)*sum(higher),'weighted deletion charge')
   removed+=before-after;charge+=max(ws)*sum(higher);total+=after
   for j,(u,v) in enumerate(es):residual[u]-=x[j];residual[v]-=x[j]
   require(all(z>=0 for z in residual),'combined flow feasibility')
  optimum=value(c,d)
  require(optimum<=sumblocks<=Q(5,3)*optimum,'block inequality R=4')
  require(sumblocks-total==removed<=charge and sumblocks<=Q(5,3)*total,'greedy bound')
  if optimum:maxratio=max(maxratio,sumblocks/optimum)
  if total:maxlossratio=max(maxlossratio,removed/total)
  checks+=1
print(json.dumps({'status':'PASS','arithmetic':'exact Fraction LP vertices and explicit greedy trimming','coalition_profiles':checks,
 'separation_parameter':4,'max_observed_block_sum_over_optimum':str(maxratio),
 'max_observed_trim_loss_over_accepted_value':str(maxlossratio),'proved_bound':'1+2/(R-1)'},indent=2))
