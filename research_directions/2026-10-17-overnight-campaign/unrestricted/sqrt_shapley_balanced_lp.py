import numpy as np, math,json
from scipy.optimize import linprog
from scipy.sparse import lil_matrix,csr_matrix
rng=np.random.default_rng(123001)
out={'tests':0,'minratio':1e100,'counter':None}
for n in range(3,8):
 nv=(1<<n)-1;ix={};ixnext=nv
 for t in range(1,1<<n):
  for i in range(n):
   if t>>i&1:ix[t,i]=ixnext;ixnext+=1
 rows=[];cols=[];data=[];r=0;eqr=[];eqc=[];eqd=[];b=[]
 for t in range(1,1<<n):
  s=(t-1)&t
  while s:
   rows.append(r);cols.append(s-1);data.append(1.)
   for i in range(n):
    if s>>i&1:rows.append(r);cols.append(ix[t,i]);data.append(-1.)
   r+=1;s=(s-1)&t
  for i in range(n):
   if t>>i&1:eqr.append(len(b));eqc.append(ix[t,i]);eqd.append(1.)
  eqr.append(len(b));eqc.append(t-1);eqd.append(-1.);b.append(0.)
 eqr.append(len(b));eqc.append(nv-1);eqd.append(1.);b.append(1.)
 A=csr_matrix((data,(rows,cols)),shape=(r,ixnext));E=csr_matrix((eqd,(eqr,eqc)),shape=(len(b),ixnext))
 sh=np.zeros((n,ixnext))
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
  for start in range(50):
   q=np.exp(rng.uniform(-3,2,k))
   for step in range(20):
    obj=np.sum(sh[:k]/q[:,None],axis=0);obj[S-1]-=2
    sol=linprog(obj,A_ub=A,b_ub=np.zeros(r),A_eq=E,b_eq=b,bounds=(0,None),method='highs')
    assert sol.success,sol.message
    phi=sh@sol.x;value=sol.x[S-1];covered=sum(np.sqrt(np.maximum(phi[:k],0)))
    out['tests']+=1
    if value>1e-10:out['minratio']=min(out['minratio'],float(covered/value))
    if covered+1e-8<value:
     out['counter']={'n':n,'k':k,'values':sol.x[:nv].tolist(),'phi':phi.tolist(),'covered':covered,'value':value,'q':q.tolist()};break
    qnew=np.maximum(np.sqrt(np.maximum(phi[:k],0)),1e-8)
    if np.max(abs(qnew-q))<1e-8:break
    q=qnew
   if out['counter']:break
  if out['counter']:break
 if out['counter']:break
 print(json.dumps({'n':n,'tests':out['tests'],'minratio':out['minratio']}),flush=True)
print(json.dumps(out),flush=True)
