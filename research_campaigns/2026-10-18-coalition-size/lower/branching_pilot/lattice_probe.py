#!/usr/bin/env python3
"""Full binary PG(3,2) pure-owner quotient, including inactive pointed orbits.
Finite binary institution only. No all-real upper mechanism inferred.
"""
from collections import deque,defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse,json,sys,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from binary_subset_orbit_probe import geometry
from pure_unit_transition_probe import production
OUT=Path(__file__).resolve().parent

def build():
 start=time.monotonic();d,edges,gens=geometry(4);N=1<<d
 maps=[]
 for g in gens:
  pm=np.zeros(N,dtype=np.int32)
  for mask in range(1,N):
   low=mask&-mask;pm[mask]=int(pm[mask^low])|(1<<g[low.bit_length()-1])
  maps.append(pm)
 profile=np.full(N,-1,dtype=np.int32);reps=[]
 for root in range(N):
  if profile[root]>=0:continue
  oid=len(reps);reps.append(root);profile[root]=oid;todo=deque([root])
  while todo:
   mask=todo.popleft()
   for pm in maps:
    new=int(pm[mask])
    if profile[new]<0:profile[new]=oid;todo.append(new)
 pointed=np.full(N*d,-1,dtype=np.int32);points=[];transitions=[]
 for root in range(N*d):
  if pointed[root]>=0:continue
  mask,i=divmod(root,d);oid=len(points);points.append((mask,i))
  if not mask&(1<<i):transitions.append((mask,i))
  pointed[root]=oid;todo=deque([root])
  while todo:
   p=todo.popleft();mask,i=divmod(p,d)
   for g,pm in zip(gens,maps):
    new=int(pm[mask])*d+g[i]
    if pointed[new]<0:pointed[new]=oid;todo.append(new)
 qmaps=pointed.reshape((N,d));oracles={}
 for mask in reps:
  val,x,y=production([(mask>>i)&1 for i in range(d)],edges)
  oracles[str(mask)]={'value':str(val),'primal':list(map(str,x)),'dual':list(map(str,y))}
 meta={'d':d,'n':d,'edges':edges,'generators':gens,'profile_reps':reps,'pointed_reps':points,'transitions':transitions,'oracles':oracles,'elapsed':time.monotonic()-start}
 np.savez_compressed(OUT/'quotient.npz',profile=profile,qmaps=qmaps)
 (OUT/'quotient.json').write_text(json.dumps(meta,indent=2)+'\n')
 print(json.dumps({'stage':'scope','profiles':N,'pointed_states':N*d,'profile_orbits':len(reps),'pointed_orbits':len(points),'transitions':len(transitions),'elapsed':meta['elapsed']}),flush=True)
 return meta,profile,qmaps

def load():
 if not (OUT/'quotient.json').exists():return build()
 meta=json.loads((OUT/'quotient.json').read_text());arr=np.load(OUT/'quotient.npz')
 return meta,arr['profile'],arr['qmaps']

def solve(s,seconds=90):
 meta,profile,qmaps=load();d=meta['d'];K=len(meta['pointed_reps']);start=time.monotonic()
 rows=[];rhs=[];tags=[];seen=set()
 def add(row,b,tag):
  c=defaultdict(F)
  for j,v in row:c[int(j)]+=v
  c={j:v for j,v in c.items() if v};key=(tuple(sorted(c.items())),F(b))
  if key in seen:return False
  seen.add(key);rows.append(c);rhs.append(F(b));tags.append(tag);return True
 for mask in meta['profile_reps']:
  q=qmaps[mask];val=F(meta['oracles'][str(mask)]['value'])
  add([(q[j],F(1)) for j in range(d)]+[(K,-val)],0,['budget',mask])
  for e in meta['edges']:
   if all(mask&(1<<j) for j in e):add([(q[j],F(-1)) for j in e],-1,['coverage',mask,e])
 for mask,i in meta['transitions']:
  new=mask|(1<<i);add([(qmaps[mask,i],F(1)),(qmaps[new,i],F(-1))],0,['tcwm',mask,new,i,[i]])
 history=[];z=None;complete=False
 for it in range(150):
  rr=[];cc=[];dd=[]
  for r,row in enumerate(rows):
   for c,v in row.items():rr.append(r);cc.append(c);dd.append(float(v))
  A=coo_matrix((dd,(rr,cc)),shape=(len(rows),K+1)).tocsr();obj=np.zeros(K+1);obj[K]=1
  remain=seconds-(time.monotonic()-start)
  if remain<=0:break
  z=linprog(obj,A_ub=A,b_ub=np.array(list(map(float,rhs))),bounds=(0,None),method='highs',options={'time_limit':remain})
  if not z.success:history.append({'failure':z.message});break
  cuts=0;worst=0
  for mask,i in meta['transitions']:
   new=mask|(1<<i);q=qmaps[mask];r=qmaps[new]
   losses=sorted([(z.x[q[j]]-z.x[r[j]],j) for j in range(d) if j!=i],reverse=True)
   C=[i]+[j for delta,j in losses[:max(0,s-1)] if delta>0]
   violation=sum(z.x[q[j]]-z.x[r[j]] for j in C);worst=max(worst,violation)
   if violation>1e-9:
    cuts+=add([(v,c) for j in C for v,c in [(q[j],F(1)),(r[j],F(-1))]],0,['tcwm',mask,new,i,C])
  rec={'iteration':it,'factor':z.fun,'cuts':cuts,'max_violation':worst,'elapsed':time.monotonic()-start};history.append(rec)
  if not cuts:complete=True;break
 result={'s':s,'n':d,'d':d,'complete':complete,'history':history,'payment_variables':K,'inequalities':len(rows),'scope':'Complete binary pure-owner institution when complete; no all-real upper mechanism.'}
 if z is None or not z.success:return result
 candidate=[F(float(v)).limit_denominator(10**8) for v in z.x]
 primal_ok=True;primal_res=[]
 for row,b in zip(rows,rhs):
  gap=sum(v*candidate[j] for j,v in row.items())-b
  if gap>0:primal_ok=False;primal_res.append(str(gap))
 for mask,i in meta['transitions']:
  new=mask|(1<<i);q=qmaps[mask];r=qmaps[new]
  losses=sorted([candidate[q[j]]-candidate[r[j]] for j in range(d) if j!=i],reverse=True)
  gap=candidate[q[i]]-candidate[r[i]]+sum(max(F(0),v) for v in losses[:s-1])
  if gap>0:primal_ok=False;primal_res.append(str(gap))
 cert=[];combo=defaultdict(F);right=F(0)
 for row,b,tag,m in zip(rows,rhs,tags,z.ineqlin.marginals):
  w=F(float(max(0,-m))).limit_denominator(10**7)
  if not w:continue
  cert.append({'weight':str(w),'row':tag})
  for j,v in row.items():combo[j]+=w*v
  right+=w*b
 repairs=0
 for mask in meta['profile_reps']:
  counts=defaultdict(int)
  for j in qmaps[mask]:counts[int(j)]+=1
  w=max([F(0)]+[-combo[j]/v for j,v in counts.items()])
  if w>0:
   for j,v in counts.items():combo[j]+=w*v
   combo[K]-=w*F(meta['oracles'][str(mask)]['value'])
   cert.append({'weight':str(w),'row':['budget',mask]});repairs+=1
 valid=combo[K]<0 and all(v>=0 for j,v in combo.items() if j!=K)
 result.update(float_factor=z.fun,exact_primal=primal_ok,exact_upper=str(candidate[K]) if primal_ok else None,primal_residuals=primal_res[:10],exact_lower=str(right/combo[K]) if valid else None,dual_valid=valid,repairs=repairs,certificate_rows=len(cert),certificate=cert,combo={str(j):str(v) for j,v in combo.items() if v},rhs=str(right),candidate_payments=list(map(str,candidate)),factor_index=K)
 (OUT/f'result_s{s}.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['history','certificate','combo','candidate_payments','primal_residuals']}),flush=True)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--s',type=int,nargs='*',default=[]);p.add_argument('--seconds',type=int,default=90);a=p.parse_args()
 if a.build:build()
 for s in a.s:
  assert 1<=s<=15
  solve(s,a.seconds)
