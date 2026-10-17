#!/usr/bin/env python3
"""Positive-sum (3/2+epsilon) weighted mechanism; fixed-epsilon bit-polynomial.

Uses established shifted weight bucketing and exact same-owner unfolding.
Exponential inverse-accuracy dependence is explicit; this is not an FPTAS.
"""
from fractions import Fraction as Q
from collections import Counter,defaultdict
from pathlib import Path
import importlib.util
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('weighted',H/'weighted_graph_mechanism.py')
wmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(wmod)
def require(c,m):
 if not c:raise RuntimeError(m)
def ceilq(x):return -(-x.numerator//x.denominator)
def plan_blocks(profits,epsilon):
 w=list(map(Q,profits));eps=Q(epsilon)
 require(0<eps<=1,'epsilon must be in (0,1]')
 require(all(z>=0 for z in w),'negative public profits')
 R=1+ceilq(12/eps);L=1+ceilq(6/eps);eta=eps/6
 positive=[i for i,z in enumerate(w) if z>0]
 if not positive:return {'blocks':[],'factor':Q(3,2),'epsilon':eps,'R':R,'L':L,'eta':eta}
 a=min(w[i] for i in positive);band={}
 for i in positive:
  ratio=w[i]/a;k=0
  while ratio>=R:ratio/=R;k+=1
  band[i]=k
 mult=Counter()
 for s in range(L):
  groups=defaultdict(list)
  for i,k in band.items():
   if k%L==s:continue
   start=s+1+((k-s-1)//L)*L
   groups[start].append(i)
  for ids in groups.values():mult[tuple(sorted(ids))]+=1
 retained=Counter();blocks=[];C=ceilq(Q(R**(L-1))/eta)
 for ids,count in sorted(mult.items()):
  base=min(w[i] for i in ids);scale=eta*base
  integer=[ceilq(w[i]/scale) for i in ids]
  require(max(integer)<=C,'bounded normalized block range')
  require(all(w[i]<=scale*z<=(1+eta)*w[i] for i,z in zip(ids,integer)),'relative upward rounding')
  for i in ids:retained[i]+=count
  blocks.append({'edge_indices':ids,'multiplicity':count,'integer_profits':integer,
   'scale':scale,'payment_coefficient':Q(count,L-1)*scale})
 require(all(retained[i]==L-1 for i in positive),'uniform public edge retention')
 factor=Q(3,2)*(1+eta)*(1+Q(2,R-1))*Q(L,L-1)
 require(factor<=Q(3,2)+eps,'stated funding factor')
 return {'blocks':blocks,'factor':factor,'epsilon':eps,'R':R,'L':L,'eta':eta,
  'normalized_weight_limit':C,'band_indices':band}
def payments(owner_bundles,edges,profits,epsilon,copy_limit=100000):
 own=[list(map(Q,b)) for b in owner_bundles];es=list(map(tuple,edges));w=list(map(Q,profits))
 require(bool(own) and len(es)==len(w),'input lengths')
 n=len(own[0]);require(all(len(b)==n and all(z>=0 for z in b) for b in own),'owner domains')
 # Validate original graph even when zero-profit edges disappear from the plan.
 require(all(len(e)==2 and 0<=e[0]<n and 0<=e[1]<n and e[0]!=e[1] for e in es),'edge endpoints')
 require(len({tuple(sorted(e)) for e in es})==len(es),'duplicate original edge')
 plan=plan_blocks(w,epsilon);prices=[Q(0)]*n;covering_value=Q(0);evaluations=[]
 for block in plan['blocks']:
  ids=block['edge_indices'];result=wmod.payments(own,[es[i] for i in ids],block['integer_profits'],copy_limit)
  coefficient=block['payment_coefficient']
  prices=[x+coefficient*y for x,y in zip(prices,result['prices'])]
  covering_value+=coefficient*result['value']
  evaluations.append({'edge_indices':ids,'coefficient':coefficient,'copy_count':result['copy_count'],
   'lift_edge_count':result['lift_edge_count'],'integer_production':result['value']})
 p=[sum(a*b for a,b in zip(owner,prices)) for owner in own];funding=sum(p)
 require(all(prices[u]+prices[v]>=z for (u,v),z in zip(es,w)),'original coalition cover prices')
 require(funding<=Q(3,2)*covering_value,'summed block funding')
 return {'owner_payments':p,'prices':prices,'funding':funding,'covering_value':covering_value,
  'proved_funding_factor':plan['factor'],'epsilon':plan['epsilon'],'block_evaluations':evaluations,'public_plan':plan}
