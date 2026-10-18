#!/usr/bin/env python3
"""Exact full-fiber lift and all-coalition full-OUT replay; no optimizer."""
# Hardened owned copy; original sealed code and inputs are not modified.
# Original SHA256: acf11628c384d85e2f2ea03bb41c8c6a2cb2a31da150f59b724d282a2cdd493d
# Added quotient primal/dual nonnegativity guards and exact per-R s metadata.
from fractions import Fraction as F
from pathlib import Path
import json, numpy as np
P=Path('/Users/maxf/.codex/visualizations/2026/09/04/01a06e8a-dcbb-7c81-9929-e72831a14ac8/research-campaigns/2026-10-18-coalition-size/lower/branching_pilot');meta=json.loads((P/'ternary_quotient.json').read_text());a=np.load(P/'ternary_quotient.npz');prof=a['profile'];reps=meta['profile_reps'];qe=[tuple(i+1 for i in e) for e in meta['edges']];oracles=meta['oracles'];vals={};cert={}
# Each binary quotient state is transformed to its representative by explicit
# generator search, carrying its primal and dual, independently of pointed maps.
from collections import deque
for mask in range(128):
 code=sum((mask>>i&1)*3**i for i in range(7));target=reps[int(prof[code])];todo=deque([(code,tuple(range(7)))]);seen={code};found=None
 while todo:
  c,perm=todo.popleft()
  if c==target:found=perm;break
  caps=[c//3**i%3 for i in range(7)]
  for g in meta['generators']:
   new=sum(caps[i]*3**g[i] for i in range(7))
   if new not in seen:seen.add(new);todo.append((new,tuple(g[perm[i]] for i in range(7))))
 assert found is not None;o=oracles[str(target)];x=list(map(F,o['primal']));p=list(map(F,o['dual']));qprice=[p[found[i]] for i in range(7)]
 eidx={tuple(sorted(e)):j for j,e in enumerate(meta['edges'])};qx=[x[eidx[tuple(sorted(found[i-1] for i in e))]] for e in qe];val=F(o['value'])
 assert all(t>=0 for t in qx), 'negative quotient primal intensity'
 assert all(t>=0 for t in qprice), 'negative quotient dual price'
 assert sum(qx)==sum(qprice[i] for i in range(7) if mask>>i&1)==val
 assert all(sum(qprice[i-1] for i in e)>=1 for e in qe)
 assert all(sum(qx[j] for j,e in enumerate(qe) if i+1 in e)<= (mask>>i&1) for i in range(7))
 vals[mask]=val;cert[mask]=(qx,qprice)
ideal=[S for S in range(128) if vals[S]<=1];counts={'lifted_full_LP_pairs':0,'funding_checks':0,'full_OUT_endpoint_checks':0,'actual_edge_coverage_checks':0}
for R in [1,2,4]:
 n=8*R-1;edges=[(u,v,u^v) for u in range(1,n+1) for v in range(u+1,n+1) if u^v>v]
 for S in range(128):
  qx,qp=cert[S];x={e:F(0) for e in edges}
  for j,(a,b,c) in enumerate(qe):
   for u in range(a*R,(a+1)*R):
    for v in range(b*R,(b+1)*R):x[tuple(sorted((u,v,u^v)))]+=qx[j]/R
  price={u:(F(1) if u<R else qp[u//R-1]) for u in range(1,n+1)}
  active={u for u in range(R,n+1) if S>>(u//R-1)&1}
  assert all(sum(t for e,t in x.items() if u in e)<=(u in active) for u in range(1,n+1))
  assert all(sum(price[u] for u in e)>=1 for e in edges)
  assert sum(x.values())==sum(price[u] for u in active)==R*vals[S];counts['lifted_full_LP_pairs']+=1
 for s in range(R,33):
  q={1:F(1,3)}
  for m in range(2,s//R+5):
   L=min(s-R,2*R*(m-1));q[m]=F(L,R+L)*q[m-1]
  B=max(F(1)+2*(m-1)*v for m,v in q.items());ys={}
  for S in ideal:
   y=[F(0)]*7
   if vals[S]:
    es=[e for e in qe if all(S>>(i-1)&1 for i in e)];common=set(es[0]).intersection(*map(set,es[1:]));assert common;cap=min(common);m=len(es)
    for e in es:
     for i in e:y[i-1]=q[m]
    y[cap-1]=1-2*q[m]
   ys[S]=y;assert sum(y)<=B*vals[S];counts['funding_checks']+=1
   for e in edges:
    if all(u>=R and S>>(u//R-1)&1 for u in e):assert sum(y[u//R-1] for u in e)>=1;counts['actual_edge_coverage_checks']+=1
  for T in ideal:
   S=T
   while True:
    D=T^S;d=R*D.bit_count()
    if d<=s:
     delta=[ys[T][i]-ys[S][i] for i in range(7)];gain=R*sum(delta[i] for i in range(7) if D>>i&1);loss=sorted([max(F(0),-delta[i]) for i in range(7) if not D>>i&1 for _ in range(R)],reverse=True)
     assert gain-sum(loss[:s-d])>=R*vals[D];counts['full_OUT_endpoint_checks']+=1
    if S==0:break
    S=(S-1)&T
print(json.dumps({'status':'PASS','fiber_sizes':[1,2,4],'quotient':'Fano(2^3-1 points)','quotient_ideal_profiles':len(ideal),'protected_s_by_R':{str(R):list(range(R,33)) for R in [1,2,4]},**counts,'scope':'Exact fiber projection and intrinsic rule on the full-fiber quotient-unit-worth ideal; partial fibers excluded.'},indent=2))
