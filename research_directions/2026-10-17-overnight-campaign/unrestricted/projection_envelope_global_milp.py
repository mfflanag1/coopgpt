import numpy as np,json
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix,csc_matrix
rng=np.random.default_rng(931)
for n in [3,4,5]:
 A=np.array([[int(s>>i&1) for i in range(n)] for s in range(1,1<<n)],float);r=len(A);G=A@A.T
 iz=0;ib=n;il=n+r;ifl=il+n*r;dim=ifl+n*r
 rows=[];lo=[];hi=[]
 def add(items,l=-np.inf,h=np.inf):rows.append(items);lo.append(l);hi.append(h)
 add({i:1 for i in range(n)},1,1);add({ib+r-1:1},1,1)
 for k in range(r):add({ib+k:1,**{j:-A[k,j] for j in range(n) if A[k,j]}},h=0)
 for i in range(n):
  for k in range(r):
   base={il+i*r+j:G[k,j] for j in range(r) if G[k,j]};base[ib+k]=-1
   add({**base,ifl+i*r+k:A[k].sum()},h=A[k].sum())
   if not A[k,i]:add(base,l=0)
   add({il+i*r+k:1,ifl+i*r+k:-1},h=0)
 C=lil_matrix((len(rows),dim))
 for k,row in enumerate(rows):
  for j,a in row.items():C[k,j]=a
 C=csc_matrix(C);integrality=np.r_[np.zeros(ifl),np.ones(n*r)]
 for start in range(8):
  weights=np.ones(n) if start==0 else rng.uniform(.1,1,n)
  for step in range(4):
   obj=np.zeros(dim)
   for i in range(n):obj[il+i*r:il+(i+1)*r]=-weights[i]*A[:,i]
   sol=milp(obj,integrality=integrality,bounds=Bounds(np.zeros(dim),np.ones(dim)),constraints=LinearConstraint(C,lo,hi),options={'time_limit':25,'mip_rel_gap':1e-9})
   if sol.x is None:print(json.dumps({'n':n,'start':start,'step':step,'status':int(sol.status),'empty':True}),flush=True);break
   lam=sol.x[il:ifl].reshape(n,r);q=lam@A;M=np.diag(q);sq=float(M@M)
   rec={'n':n,'start':start,'step':step,'status':int(sol.status),'gap':float(sol.mip_gap),'objective':float(-sol.fun),'M':M.tolist(),'squared':sq,'sumratio':float(sum(M)/np.sqrt(n)),'core':sol.x[:n].tolist(),'b':sol.x[ib:il].tolist(),'q':q.tolist(),'lambda':lam.tolist()}
   print(json.dumps(rec),flush=True)
   if sq>1+1e-7:raise SystemExit
   newweights=M/max(np.linalg.norm(M),1e-12)
   if max(abs(newweights-weights))<1e-7:break
   weights=newweights
