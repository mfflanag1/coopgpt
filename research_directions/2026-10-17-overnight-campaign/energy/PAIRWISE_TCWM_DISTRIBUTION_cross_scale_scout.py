"""Discovery only: analytic cross-scale four-owner proof's merge closure."""
from itertools import combinations_with_replacement,product
from collections import Counter,defaultdict
from fractions import Fraction as Q
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog

seeds=[(-2,-2,2,4),(-3,-3,3,6),(-6,-6,2,12)]
states=set(tuple(sorted(s)) for s in seeds)
queue=list(states)
while queue:
    s=queue.pop()
    for i in range(4):
        for j in range(i):
            t=list(s); a=t.pop(i);b=t.pop(j);t+= [0,a+b]
            t=tuple(sorted(t))
            if t not in states:states.add(t);queue.append(t)
for s in list(states):
    if sum(t!=0 for t in s)==2:
        a=sum(max(-t,0) for t in s)
        if a: states.add((-a,0,0,a))
states=sorted(states)
keys=[(s,t) for s in states for t in sorted(set(s)) if t]
index={k:j for j,k in enumerate(keys)};beta=len(keys)
rows=[];rhs=[];labels=[]
def add(coeff,b,label):
    row=np.zeros(len(keys)+1)
    for j,v in coeff.items():row[j]+=v
    rows.append(row);rhs.append(b);labels.append(label)
def p(row,s,t,c):
    if t:row[index[(s,t)]]=row.get(index[(s,t)],0)+c
groups=defaultdict(list)
for s in states:
    ct=Counter(s);present=sorted(ct)
    for counts in product(*(range(ct[t]+1) for t in present)):
        if not sum(counts):continue
        worth=min(sum(c*max(t,0) for t,c in zip(present,counts)),sum(c*max(-t,0) for t,c in zip(present,counts)))
        row={}
        for t,c in zip(present,counts):p(row,s,t,-c)
        add(row,-worth,['coverage',s,list(zip(present,counts))])
    if sum(t!=0 for t in s)<=2:
        worth=min(sum(max(t,0) for t in s),sum(max(-t,0) for t in s))
        row={}
        for t in s:p(row,s,t,1)
        add(row,worth,['two_active_upper',s])
        if sum(s)==0 and worth:
            t=max(s)
            add({index[(s,t)]:-2},-worth,['balanced_lower',s,t])
            add({index[(s,t)]:2},worth,['balanced_upper',s,t])
    for x,y in combinations_with_replacement(present,2):
        if x==y and ct[x]<2:continue
        outsiders=list(s);outsiders.remove(x);outsiders.remove(y)
        groups[tuple(outsiders)].append((s,(x,y)))
for outs,entries in groups.items():
    for s,(x,y) in entries:
        for ns,(u,v) in entries:
            if s==ns and (x,y)==(u,v):continue
            for uu,vv in set(((u,v),(v,u))):
                P=max(uu-x,0)+max(vv-y,0)
                N=max(x-uu,0)+max(y-vv,0)
                row={beta:min(P,N)}
                p(row,s,x,1);p(row,s,y,1);p(row,ns,u,-1);p(row,ns,v,-1)
                b=N+min(u,0)+min(v,0)-min(x,0)-min(y,0)
                add(row,b,['transition',s,[x,y],ns,[uu,vv],P,N])
obj=np.zeros(len(keys)+1);obj[beta]=-1
res=linprog(obj,A_ub=np.array(rows),b_ub=np.array(rhs),bounds=[(0,None)]*len(keys)+[(0,1)],method='highs',options={'time_limit':30})
out={'status':res.status,'message':res.message,'variables':len(keys)+1,'constraints':len(rows),'states':len(states),'seeds':seeds}
if res.success:
    out['beta_max']=float(res.x[beta])
    weights=[Q(float(-v)).limit_denominator(1000000) for v in res.ineqlin.marginals]
    final=[Q(0) for _ in range(len(keys)+1)];b=Q(0);certificate=[]
    for j,(wt,row,rv) in enumerate(zip(weights,rows,rhs)):
        if not wt:continue
        for k,x in enumerate(row):
            if x:final[k]+=wt*int(x)
        b+=wt*int(rv)
        certificate.append({'weight':str(wt),'label':labels[j]})
    out['certificate']=certificate
    out['exact_dual_rhs']=str(b);out['exact_beta_coeff']=str(final[beta])
    out['exact_payment_coefficients']=[{'key':keys[j],'coefficient':str(v)} for j,v in enumerate(final[:-1]) if v]
    out['exact_dual_valid']=all(x>=0 for x in final[:-1]) and final[beta]>0
    out['exact_beta_bound']=str(b/final[beta]) if out['exact_dual_valid'] else None
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_cross_scale_scout.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['certificate','exact_payment_coefficients']},indent=2))
