#!/usr/bin/env python3
"""All 0/1/2 Fano pure-owner reports; all coalitions; arbitrary payments.
Finite grid only: a feasible solution here is not an all-real mechanism.
"""
from collections import deque, defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse,json,sys,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from binary_subset_orbit_probe import geometry
from pure_unit_transition_probe import production
P=Path(__file__).resolve().parent

def build():
 start=time.monotonic();d,edges,gens=geometry(3);N=3**d;pow3=[3**i for i in range(d)]
 caps=np.array([[(c//pow3[i])%3 for i in range(d)] for c in range(N)],dtype=np.int8)
 maps=[np.array([sum(int(caps[c,i])*pow3[g[i]] for i in range(d)) for c in range(N)],dtype=np.int32) for g in gens]
 profile=np.full(N,-1,dtype=np.int32);reps=[]
 for root in range(N):
  if profile[root]>=0:continue
  oid=len(reps);reps.append(root);profile[root]=oid;todo=deque([root])
  while todo:
   c=todo.popleft()
   for pm in maps:
    v=int(pm[c])
    if profile[v]<0:profile[v]=oid;todo.append(v)
 pointed=np.full(N*d,-1,dtype=np.int32);points=[];trans=[]
 for root in range(N*d):
  if pointed[root]>=0:continue
  c,i=divmod(root,d);oid=len(points);points.append((c,i))
  if caps[c,i]<2:trans.append((c,c+pow3[i],i))
  pointed[root]=oid;todo=deque([root])
  while todo:
   c,i=divmod(todo.popleft(),d)
   for g,pm in zip(gens,maps):
    v=int(pm[c])*d+g[i]
    if pointed[v]<0:pointed[v]=oid;todo.append(v)
 oracles={}
 for c in reps:
  val,x,y=production(caps[c],edges)
  oracles[str(c)]={'value':str(val),'primal':list(map(str,x)),'dual':list(map(str,y))}
 meta={'d':d,'n':d,'levels':[0,1,2],'pow3':pow3,'edges':edges,'generators':gens,'profile_reps':reps,'pointed_reps':points,'transitions':trans,'oracles':oracles,'elapsed':time.monotonic()-start}
 np.savez_compressed(P/'ternary_quotient.npz',profile=profile,qmaps=pointed.reshape(N,d),caps=caps)
 (P/'ternary_quotient.json').write_text(json.dumps(meta,indent=2)+'\n')
 print(json.dumps({'stage':'scope','profiles':N,'profile_orbits':len(reps),'pointed_orbits':len(points),'transitions':len(trans),'elapsed':meta['elapsed']}),flush=True)
 return meta,profile,pointed.reshape(N,d),caps

def load():
 if not (P/'ternary_quotient.json').exists():return build()
 meta=json.loads((P/'ternary_quotient.json').read_text());a=np.load(P/'ternary_quotient.npz');return meta,a['profile'],a['qmaps'],a['caps']

def solve(s,seconds):
 meta,profile,qmaps,caps=load();d=meta['d'];K=len(meta['pointed_reps']);start=time.monotonic();rows=[];rhs=[];tags=[];seen=set();pow3=meta['pow3'];reps=meta['profile_reps']
 values=[F(meta['oracles'][str(c)]['value']) for c in reps]
 def add(entries,b,tag):
  row=defaultdict(F)
  for j,v in entries:row[int(j)]+=v
  row={j:v for j,v in row.items() if v};key=(tuple(sorted(row.items())),F(b))
  if key in seen:return False
  seen.add(key);rows.append(row);rhs.append(F(b));tags.append(tag);return True
 for c in reps:
  q=qmaps[c];val=values[int(profile[c])];add([(q[j],F(1)) for j in range(d)]+[(K,-val)],0,['budget',c])
  for mask in range(1,1<<d):
   sub=sum(int(caps[c,j])*pow3[j] for j in range(d) if mask>>j&1);v=values[int(profile[sub])]
   if v:add([(q[j],F(-1)) for j in range(d) if mask>>j&1],-v,['coverage',c,mask])
 for old,new,i in meta['transitions']:add([(qmaps[old,i],F(1)),(qmaps[new,i],F(-1))],0,['tcwm',old,new,i,[i]])
 history=[];z=None;complete=False
 for it in range(100):
  rr=[];cc=[];dd=[]
  for r,row in enumerate(rows):
   for c,v in row.items():rr.append(r);cc.append(c);dd.append(float(v))
  A=coo_matrix((dd,(rr,cc)),shape=(len(rows),K+1)).tocsr();obj=np.zeros(K+1);obj[K]=1;remain=seconds-(time.monotonic()-start)
  if remain<=0:break
  z=linprog(obj,A_ub=A,b_ub=np.array(list(map(float,rhs))),bounds=(0,None),method='highs',options={'time_limit':remain})
  if not z.success:history.append({'failure':z.message});break
  cuts=0;worst=0
  for old,new,i in meta['transitions']:
   q=qmaps[old];r=qmaps[new];losses=sorted([(z.x[q[j]]-z.x[r[j]],j) for j in range(d) if j!=i],reverse=True)
   C=[i]+[j for v,j in losses[:s-1] if v>0];gap=sum(z.x[q[j]]-z.x[r[j]] for j in C);worst=max(worst,gap)
   if gap>1e-9:cuts+=add([(v,k) for j in C for v,k in [(q[j],F(1)),(r[j],F(-1))]],0,['tcwm',old,new,i,C])
  history.append({'iteration':it,'factor':z.fun,'cuts':cuts,'max_violation':worst,'elapsed':time.monotonic()-start})
  if not cuts:complete=True;break
 result={'s':s,'d':d,'n':d,'complete':complete,'history':history,'payment_variables':K,'inequalities':len(rows),'scope':'All ternary Fano pure-owner profiles and all coalition coverage; no all-real upper claim.'}
 if z is None or not z.success:return result
 candidate=[F(float(v)).limit_denominator(10**8) for v in z.x];ok=all(sum(v*candidate[j] for j,v in row.items())<=b for row,b in zip(rows,rhs))
 for old,new,i in meta['transitions']:
  q=qmaps[old];r=qmaps[new];losses=sorted([max(F(0),candidate[q[j]]-candidate[r[j]]) for j in range(d) if j!=i],reverse=True)
  ok=ok and candidate[r[i]]-candidate[q[i]]>=sum(losses[:s-1])
 cert=[];combo=defaultdict(F);right=F(0)
 for row,b,tag,m in zip(rows,rhs,tags,z.ineqlin.marginals):
  w=F(float(max(0,-m))).limit_denominator(10**7)
  if not w:continue
  cert.append({'weight':str(w),'row':tag})
  for j,v in row.items():combo[j]+=w*v
  right+=w*b
 repairs=0
 for c in reps:
  counts=defaultdict(int)
  for j in qmaps[c]:counts[int(j)]+=1
  w=max([F(0)]+[-combo[j]/v for j,v in counts.items()])
  if w:
   for j,v in counts.items():combo[j]+=w*v
   combo[K]-=w*values[int(profile[c])];cert.append({'weight':str(w),'row':['budget',c]});repairs+=1
 valid=combo[K]<0 and all(v>=0 for j,v in combo.items() if j!=K)
 result.update(float_factor=z.fun,exact_primal=ok,exact_upper=str(candidate[K]) if ok else None,exact_lower=str(right/combo[K]) if valid else None,dual_valid=valid,repairs=repairs,certificate_rows=len(cert),certificate=cert,combo={str(j):str(v) for j,v in combo.items() if v},rhs=str(right),candidate_payments=list(map(str,candidate)),factor_index=K)
 (P/f'ternary_result_s{s}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['history','certificate','combo','candidate_payments']}),flush=True);return result

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--s',type=int,nargs='*',default=[1,2,3,4,7]);a.add_argument('--seconds',type=int,default=60);v=a.parse_args()
 for s in v.s:assert 1<=s<=7;solve(s,v.seconds)
