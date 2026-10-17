#!/usr/bin/env python3
"""Exact finite checks for geometric dual-grid FPTAS; no floating point."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json,random
HERE=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('two_sparse',HERE/'two_sparse_mechanism.py')
v=load('independent_exact',HERE/'verify_two_sparse_lift.py')
def check(ok,message):
 if not ok:raise RuntimeError(message)
def value(c,vertices,gamma):return min(sum(a*b for a,b in zip(c,p)) for p in vertices)+sum(a*b for a,b in zip(c,gamma))

def main():
 cases=[
  ('single_edge',2,[(0,1,1,1,1)],[],Q(1,2)),
  ('gain_triangle',3,[(0,1,2,1,1),(1,2,2,1,1),(2,0,2,1,1)],[],Q(1)),
  ('parallel_two_resource',2,[(0,1,1,2,1),(0,1,2,1,1)],[],Q(1)),
  ('unary_residual',3,[(0,1,1,1,1),(1,2,1,1,2),(0,2,1,1,3)],[(0,1,1)],Q(1)),
  ('isolated_zero_worth',4,[(0,1,1,1,1)],[],Q(1)),
  ('fractional_coefficients',2,[(0,1,Q(1,2),Q(2,3),Q(3,5))],[],Q(1)),
  ('all_linear',2,[(0,1,1,1,1)],[(0,1,1),(1,1,2)],Q(1,3)),
 ]
 rng=random.Random(17100551);records=[];profiles=coalitions=transitions=primal=0
 for label,n,binary,unary,eps in cases:
  lift=m.public_lift(n,binary,eps,unary,copy_limit=20000)
  M,vertices=v.bounded_vertices(n,lift['activities'])
  for p in vertices:
   for x in p:check(x==0 or x>=lift['delta'],'Cramer vertex lower bound')
  bins=lift['bins'];edges=lift['edges'];by=[[] for _ in range(n)]
  for j,(r,lo,hi) in enumerate(bins):by[r].append(j)
  for trial in range(3):
   owners=[[Q(rng.randrange(4),rng.randrange(1,3)) for _ in range(n)] for _ in range(3)]
   if trial==0:owners[0]=[Q(0)]*n
   result=m.evaluate(lift,owners);c=[sum(o[j] for o in owners) for j in range(n)]
   F=value(c,vertices,lift['gamma']);check(result['total_payment']<=lift['funding_factor_bound']*F,'funding')
   for mask in range(8):
    cs=[sum(owners[i][j] for i in range(3) if mask>>i&1) for j in range(n)]
    f=value(cs,vertices,lift['gamma']);paid=sum(result['payments'][i] for i in range(3) if mask>>i&1)
    check(paid>=f,'coalition coverage');coalitions+=1
    p=min(vertices,key=lambda p:sum(a*b for a,b in zip(cs,p)))
    q=[next(t for t in lift['grids'][j] if t>=p[j]) for j in range(n)]
    check(all(t<=(1+lift['eta'])*s for s,t in zip(p,q)),'multiplicative rounding')
    cover=[int(lo<q[j]) for j,lo,hi in bins]
    check(all(cover[a]+cover[b]>=1 for a,b in edges),'rounded binary cover')
    cap=[(hi-lo)*cs[j] for j,lo,hi in bins];G=v.graph_value(cap,edges)
    original_res=f-sum(a*b for a,b in zip(cs,lift['gamma']))
    check(original_res<=G<=(1+lift['eta'])*original_res,'all-profile comparison')
    check(sum(a*b for a,b in zip(cap,cover))<= (1+lift['eta'])*original_res,'cover bound');profiles+=1
   old=result['payments'][0]+result['payments'][2]
   for i in (0,2):
    for j in range(n):owners[i][j]+=Q(rng.randrange(3),rng.randrange(1,3))
   result=m.evaluate(lift,owners)
   check(result['payments'][0]+result['payments'][2]>=old,'coalition increase');transitions+=1
  x=[Q(rng.randrange(4),rng.randrange(1,3)) for _ in lift['activities']];c=[Q(0)]*n
  for (u,t,a,b,w),z in zip(lift['activities'],x):c[u]+=a*z;c[t]+=b*z
  v.primal_embedding(n,lift['activities'],bins,edges,by,x,c);primal+=1
  records.append({'case':label,'epsilon':eps,'bins':len(bins),'edges':len(edges),
                  'delta':lift['delta'],'dual_vertices':len(vertices)})
 # Explicit zero-capacity/economic-worth face: one endpoint resource absent.
 lift=m.public_lift(2,[(0,1,1,1,1)],Q(1,2))
 z=m.evaluate(lift,[[1000000,0],[0,0]])
 check(z['total_payment']==0,'zero-worth profile must have exactly zero funding')
 # Guard must reject, never silently trim or alter public graph.
 guarded=False
 try:m.public_lift(2,[(0,1,1,1,1)],Q(1,10),copy_limit=1)
 except ValueError as exc:guarded='copy_limit exceeded' in str(exc)
 check(guarded,'size guard must reject')
 print(json.dumps({'status':'PASS','arithmetic':'Fraction with explicit checks; no float',
  'profiles':profiles,'coalition_coverage_checks':coalitions,'joint_increase_checks':transitions,
  'explicit_primal_embeddings':primal,'zero_worth_check':True,'guard_rejection_check':True,
  'cases':records},default=str,indent=2))
if __name__=='__main__':main()
