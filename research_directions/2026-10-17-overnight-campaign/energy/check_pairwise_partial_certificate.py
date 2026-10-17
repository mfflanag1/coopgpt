"""Exact standard-library verification of the 19-row finite certificate.
No LP solver, floating payment values or optimization status is used.
"""
from collections import defaultdict,Counter
from fractions import Fraction as Q
from pathlib import Path
import json
base=Path(__file__).parent
cert=json.loads((base/'pairwise_partial_finite_certificate.json').read_text())['integer_certificate']
coef=defaultdict(Q);rhs=Q(0);readable=[]
def addp(row,state,t,v):
 row[('p',tuple(state),t)]+=Q(v)
for entry in cert:
 m=entry['multiplier'];label=entry['label'];kind=label[0];row=defaultdict(Q)
 assert isinstance(m,int) and m>0
 if kind=='coverage':
  _,state,selected=label
  counts=Counter(state)
  assert sum(state)==2 and len(state)==5
  for t,c in selected:
   assert 0<=c<=counts[t]
   assert t!=0 or c==0 # certificate uses only active coalition members
   addp(row,state,t,-c)
  worth=min(sum(max(t,0)*c for t,c in selected),sum(max(-t,0)*c for t,c in selected))
  b=-worth
 elif kind=='transfer':
  _,state,old,newstate,new,D=label
  remain=Counter(state)
  for t in old:
   assert remain[t]>0;remain[t]-=1
  for t in new:remain[t]+=1
  assert +remain==Counter(newstate)
  assert sum(old)==sum(new)
  assert D==min(abs(new[0]-old[0]),abs(new[0]-old[1]))
  assert D>0
  # Choose matching attaining D; minimal restoring bundles have totals(D,D).
  target=new if abs(new[0]-old[0])==D else new[::-1]
  changes=[target[j]-old[j] for j in range(2)]
  assert sum(max(x,0) for x in changes)==D
  assert sum(max(-x,0) for x in changes)==D
  for t in old:addp(row,state,t,1)
  for t in new:addp(row,newstate,t,-1)
  row[('beta',)]=Q(D)
  b=D+sum(min(t,0) for t in new)-sum(min(t,0) for t in old)
 elif kind=='two_active_upper':
  _,state=label
  assert sum(t!=0 for t in state)<=2
  for t in state:
   if t:addp(row,state,t,1)
  b=min(sum(max(t,0) for t in state),sum(max(-t,0) for t in state))
 elif kind=='q4_ge_one':
  addp(row,[-2,0,0,0,4],4,-1);b=-1
 else:raise AssertionError(kind)
 for k,v in row.items():coef[k]+=m*v
 rhs+=m*b
 readable.append({'multiplier':m,'kind':kind,'rhs':b,'label':label})
coef={k:v for k,v in coef.items() if v}
expected={('beta',):Q(28),('p',(-2,0,0,0,4),0):Q(1),('p',(-1,0,0,0,3),0):Q(-2),('p',(-2,0,1,1,2),0):Q(-3),('p',(-1,0,0,1,2),0):Q(-8),('p',(-1,0,1,1,1),0):Q(-6),('p',(0,0,0,1,1),0):Q(-6)}
assert coef==expected
assert rhs==27
weighted_negative_mass=0
for key,v in coef.items():
 if key[0]!='p' or v>=0:continue
 state=key[1];G=sum(max(-x,0) for x in state);r=sum(x!=0 for x in state)
 assert r<=4
 weighted_negative_mass+=int(-v)*G
assert weighted_negative_mass==22
out={'status':'PASS','certificate_rows':len(cert),'final_rhs':27,'beta_coefficient':28,'all_active_payment_coefficients_cancel':True,'null_coefficients':[{'state':list(k[1]),'coefficient':str(v)} for k,v in coef.items() if k[0]=='p'],'null_bound_total_coefficient':22,'proved_bound':'K_n(beta) >= (n-4)*max(0,28*beta-27)/22 for n>=5','scope':'Exact certificate of valid necessary inequalities, plus analytic translation/efficiency dependencies stated in note.'}
(base/'pairwise_partial_certificate_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
