import numpy as np,math,json
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
out={'tests':0,'best':1e99,'counter':None,'curves':[]}
for k in [2,3,4,6]:
 for m in [1,2,5,10,20,40,80]:
  n=k+m;D=(k+1)*(m+1);dim=3*D;ix=lambda a,b:a*(m+1)+b
  rr=[];cc=[];dd=[];r=0;er=[];ec=[];ed=[];be=[]
  for a in range(k+1):
   for b in range(m+1):
    if not a+b:continue
    j=ix(a,b);er.extend([len(be)]*3);ec.extend([j,D+j,2*D+j]);ed.extend([-1.,a,b]);be.append(0.)
    for u in range(a+1):
     for v in range(b+1):
      if not(u+v) or(u==a and v==b):continue
      rr.extend([r]*3);cc.extend([ix(u,v),D+j,2*D+j]);dd.extend([1.,-u,-v]);r+=1
  for j,value in [(ix(0,0),0.),(ix(k,m),1.),(ix(k,0),0.)]:
   er.append(len(be));ec.append(j);ed.append(1.);be.append(value)
  A=csr_matrix((dd,(rr,cc)),shape=(r,dim));E=csr_matrix((ed,(er,ec)),shape=(len(be),dim));obj=np.zeros(dim)
  for a in range(k):
   for b in range(m+1):
    w=k*math.comb(k-1,a)*math.comb(m,b)/(n*math.comb(n-1,a+b));obj[ix(a+1,b)]+=w;obj[ix(a,b)]-=w
  curve=[]
  for alpha in [.1,.25,.5,.75,1.]:
   be[-1]=alpha
   sol=linprog(obj,A_ub=A,b_ub=np.zeros(r),A_eq=E,b_eq=be,bounds=(0,None),method='highs');assert sol.success,sol.message
   total=sol.fun;ratio=math.sqrt(k*max(total,0))/alpha;out['tests']+=1;out['best']=min(out['best'],ratio);curve.append([alpha,total,ratio])
   if ratio<1-1e-8:out['counter']={'k':k,'m':m,'alpha':alpha,'values':sol.x[:D].reshape(k+1,m+1).tolist(),'core':[[sol.x[D+ix(k,m)],sol.x[2*D+ix(k,m)]]],'totalphi':total,'ratio':ratio};break
  out['curves'].append({'k':k,'m':m,'curve':curve});print(json.dumps({'k':k,'m':m,'curve':curve}),flush=True)
  if out['counter']:break
 if out['counter']:break
print(json.dumps(out),flush=True)
