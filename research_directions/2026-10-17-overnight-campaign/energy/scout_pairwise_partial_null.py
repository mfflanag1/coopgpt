"""One finite necessary-inequality scout on the exact five-owner merger family.
No finite feasible result is promoted to an all-profile construction.
"""
from itertools import combinations_with_replacement,product
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import numpy as np,json
from scipy.optimize import linprog
states=[x for x in combinations_with_replacement(range(-2,5),5) if sum(x)==2 and sum(max(-t,0) for t in x)<=2]
keys=[(s,t) for s in states for t in sorted(set(s)) if t]
index={k:j for j,k in enumerate(keys)}; beta=len(keys)
rows=[];rhs=[];labels=[]
def add(coeff,b,label):
 row=np.zeros(len(keys)+1)
 for j,v in coeff.items():row[j]+=v
 rows.append(row);rhs.append(b);labels.append(label)
def p(row,s,t,c):
 if t:row[index[(s,t)]]=row.get(index[(s,t)],0)+c
for s in states:
 ct=Counter(s);present=sorted(ct)
 for counts in product(*(range(ct[t]+1) for t in present)):
  if not sum(counts):continue
  worth=min(sum(c*max(t,0) for t,c in zip(present,counts)),sum(c*max(-t,0) for t,c in zip(present,counts)))
  row={}
  for t,c in zip(present,counts):p(row,s,t,-c)
  add(row,-worth,['coverage',s,list(zip(present,counts))])
 if sum(t!=0 for t in s)<=2:
  row={}
  for t in s:p(row,s,t,1)
  worth=sum(max(-t,0) for t in s)
  add(row,worth,['two_active_upper',s])
 for x,y in combinations_with_replacement(present,2):
  if x==y and ct[x]<2:continue
  for u in range(-2,5):
   v=x+y-u
   if v<u or v>4 or v<-2:continue
   ns=list(s);ns.remove(x);ns.remove(y);ns+= [u,v];ns=tuple(sorted(ns))
   if ns not in states:continue
   D=min(abs(u-x),abs(u-y))
   if not D:continue
   # DeltaH=DeltaP + min(u,0)+min(v,0)-min(x,0)-min(y,0).
   delta_min=min(u,0)+min(v,0)-min(x,0)-min(y,0)
   row={beta:D}
   p(row,ns,u,-1);p(row,ns,v,-1);p(row,s,x,1);p(row,s,y,1)
   add(row,D+delta_min,['transfer',s,[x,y],ns,[u,v],D])
add({index[((-2,0,0,0,4),4)]:-1},-1,['q4_ge_one'])
obj=np.zeros(len(keys)+1);obj[beta]=-1
res=linprog(obj,A_ub=np.array(rows),b_ub=np.array(rhs),bounds=[(0,None)]*len(keys)+[(0,1)],method='highs',options={'time_limit':30})
out={'status':res.status,'message':res.message,'variables':len(keys)+1,'constraints':len(rows),'states':len(states)}
if res.success:
 out['beta_max']=float(res.x[beta]);out['payments']=[{'profile':s,'type':t,'pay':float(res.x[j])} for (s,t),j in index.items()]
 out['dual']=[{'row':j,'label':labels[j],'multiplier':float(v)} for j,v in enumerate(res.ineqlin.marginals) if abs(v)>1e-10]
 # Reconstruct a rational inequality from the minimization dual.
 weights=[Q(float(-v)).limit_denominator(1000000) for v in res.ineqlin.marginals]
 final=[Q(0) for _ in range(len(keys)+1)];b=Q(0)
 for wt,row,rv in zip(weights,rows,rhs):
  if not wt:continue
  for j,x in enumerate(row):
   if x:final[j]+=wt*int(x)
  b+=wt*int(rv)
 out['exact_dual_rhs']=str(b);out['exact_beta_coeff']=str(final[beta]);out['exact_payment_coefficients']=[{'key':keys[j],'coefficient':str(v)} for j,v in enumerate(final[:-1]) if v]
 # Positive payment coefficients may be dropped using nonnegativity.
 out['exact_dual_valid']=all(x>=0 for x in final[:-1]) and final[beta]>0
 out['exact_beta_bound']=str(b/final[beta]) if out['exact_dual_valid'] else None
Path(__file__).with_name('pairwise_partial_null_scout.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['payments','dual','exact_payment_coefficients']},indent=2))
