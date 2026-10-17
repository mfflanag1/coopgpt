import numpy as np,math,json
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
rng=np.random.default_rng(509)
out={'tests':0,'minratio':1e100,'counter':None}
for n in range(3,11):
 nv=(1<<n)-1;dim=nv+n;rr=[];cc=[];dd=[];r=0
 for s in range(1,1<<n):
  rr.append(r);cc.append(s-1);dd.append(1.)
  for i in range(n):
   if s>>i&1:rr.append(r);cc.append(nv+i);dd.append(-1.)
  r+=1
  for i in range(n):
   if not s>>i&1:
    rr.extend([r,r]);cc.extend([s-1,(s|(1<<i))-1]);dd.extend([1.,-1.]);r+=1
 A=csr_matrix((dd,(rr,cc)),shape=(r,dim));E=np.zeros((2,dim));E[0,nv-1]=1;E[1,nv:]=1
 sh=np.zeros((n,dim))
 for s in range(1<<n):
  sz=s.bit_count()
  if sz==n:continue
  w=1/(n*math.comb(n-1,sz))
  for i in range(n):
   if not s>>i&1:
    sh[i,(s|(1<<i))-1]+=w
    if s:sh[i,s-1]-=w
 for k in range(1,n):
  S=(1<<k)-1
  for start in range(40):
   q=np.exp(rng.uniform(-3,2,k))
   for step in range(20):
    obj=np.sum(sh[:k]/q[:,None],axis=0);obj[S-1]-=2
    sol=linprog(obj,A_ub=A,b_ub=np.zeros(r),A_eq=E,b_eq=[1,1],bounds=(0,None),method='highs')
    assert sol.success,sol.message
    phi=sh@sol.x;value=sol.x[S-1];covered=sum(np.sqrt(np.maximum(phi[:k],0)))
    out['tests']+=1
    if value>1e-10:out['minratio']=min(out['minratio'],float(covered/value))
    if covered+1e-8<value:
     out['counter']={'n':n,'k':k,'values':sol.x[:nv].tolist(),'core':sol.x[nv:].tolist(),'phi':phi.tolist(),'covered':covered,'value':value,'q':q.tolist()};break
    qnew=np.maximum(np.sqrt(np.maximum(phi[:k],0)),1e-8)
    if np.max(abs(qnew-q))<1e-8:break
    q=qnew
   if out['counter']:break
  if out['counter']:break
 if out['counter']:break
 print(json.dumps({'n':n,'tests':out['tests'],'minratio':out['minratio']}),flush=True)
print(json.dumps(out),flush=True)
