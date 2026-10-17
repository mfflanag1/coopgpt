import numpy as np,math,json
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
out={'tests':0,'best':1e99,'counter':None,'curves':[]}
for k in [2,3,4,6,10,15]:
 for m in [1,2,5,10,20,40,80]:
  n=k+m;D=(k+1)*(m+1);ix=lambda a,b:a*(m+1)+b
  rr=[];cc=[];dd=[];r=0
  for a in range(k+1):
   for b in range(m+1):
    rr.extend([r,r,r]);cc.extend([ix(a,b),D,D+1]);dd.extend([1.,-a,-b]);r+=1
    if a<k:rr.extend([r,r]);cc.extend([ix(a,b),ix(a+1,b)]);dd.extend([1.,-1.]);r+=1
    if b<m:rr.extend([r,r]);cc.extend([ix(a,b),ix(a,b+1)]);dd.extend([1.,-1.]);r+=1
  A=csr_matrix((dd,(rr,cc)),shape=(r,D+2));E=np.zeros((4,D+2));E[0,ix(0,0)]=1;E[1,ix(k,m)]=1;E[2,D]=k;E[2,D+1]=m;E[3,ix(k,0)]=1
  obj=np.zeros(D+2)
  for a in range(k):
   for b in range(m+1):
    w=k*math.comb(k-1,a)*math.comb(m,b)/(n*math.comb(n-1,a+b));obj[ix(a+1,b)]+=w;obj[ix(a,b)]-=w
  curve=[]
  for alpha in [.1,.25,.5,.75,1.]:
   sol=linprog(obj,A_ub=A,b_ub=np.zeros(r),A_eq=E,b_eq=[0,1,1,alpha],bounds=(0,None),method='highs');assert sol.success
   total=sol.fun;ratio=math.sqrt(k*total)/alpha;out['tests']+=1;out['best']=min(out['best'],ratio);curve.append([alpha,total,ratio])
   if ratio<1-1e-8:out['counter']={'k':k,'m':m,'alpha':alpha,'values':sol.x[:D].reshape(k+1,m+1).tolist(),'core':sol.x[D:].tolist(),'totalphi':total,'ratio':ratio};break
  out['curves'].append({'k':k,'m':m,'curve':curve})
  if out['counter']:break
 if out['counter']:break
print(json.dumps(out))
