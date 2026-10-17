import itertools,math,json,sys,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
r=int(sys.argv[1]) if len(sys.argv)>1 else 3
n=int(sys.argv[2]) if len(sys.argv)>2 else 4
nt=1<<r

def comp(total,k,prefix=()):
 if k==1:
  yield prefix+(total,); return
 for a in range(total+1):yield from comp(total-a,k-1,prefix+(a,))
cs=list(comp(n,nt));ix={c:j for j,c in enumerate(cs)};vid={};nv=0
for c in cs:
 for t,a in enumerate(c):
  if a:vid[c,t]=nv;nv+=1
kv=nv;nv+=1
rr=[];cc=[];dd=[];rhs=[];labels=[]
def row(dic,b,label):
 j=len(rhs)
 for i,x in dic.items():
  if x:rr.append(j);cc.append(i);dd.append(x)
 rhs.append(b);labels.append(label)
def val(k):return min(sum(a for t,a in enumerate(k) if t>>e&1)for e in range(r))
for c in cs:
 row({**{vid[c,t]:a for t,a in enumerate(c)if a},kv:-val(c)},0,('budget',c))
 coal=list(itertools.product(*(range(a+1)for a in c)))
 for k in coal:
  v=val(k)
  if v:row({vid[c,t]:-a for t,a in enumerate(k)if a},-v,('cover',c,k))
 for t,a in enumerate(c):
  if not a:continue
  for e in range(r):
   if t>>e&1:continue
   u=t|(1<<e);c2=list(c);c2[t]-=1;c2[u]+=1;c2=tuple(c2)
   for k in coal:
    if not k[t]:continue
    k2=list(k);k2[t]-=1;k2[u]+=1
    d={vid[c,j]:q for j,q in enumerate(k)if q}
    for j,q in enumerate(k2):
     if q:d[vid[c2,j]]=d.get(vid[c2,j],0)-q
    row(d,0,('mono',c,t,e,k))
A=coo_matrix((dd,(rr,cc)),shape=(len(rhs),nv)).tocsr();obj=np.zeros(nv);obj[kv]=1
res=linprog(obj,A_ub=A,b_ub=np.array(rhs),bounds=(0,None),method='highs')
out={'r':r,'n':n,'profiles':len(cs),'variables':nv,'rows':len(rhs),'success':res.success,'message':res.message,'factor':float(res.fun) if res.success else None}
if res.success:
 inds=np.flatnonzero(abs(res.ineqlin.marginals)>1e-8)
 out['dual_nonzero']=len(inds)
 out['dual']=[{'weight':float(-res.ineqlin.marginals[i]),'label':labels[i]}for i in inds]
 out['max_violation']=float(np.max(A@res.x-np.array(rhs)))
 out['solution']=[{'c':c,'payments':[float(res.x[vid[c,t]])if c[t]else None for t in range(nt)]}for c in cs]
print(json.dumps(out))
