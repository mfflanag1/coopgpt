import numpy as np,math,json
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
rng=np.random.default_rng(5013)
out={'tests':0,'best':1e99,'counter':None,'curves':[]}
for k in [1,2,3,4,6,10,20]:
 for m in [1,2,5,10,20,40,80]:
  n=1+k+m;D=(k+1)*(m+1);ix=lambda a,b:a*(m+1)+b
  rr=[];cc=[];dd=[];r=0
  for a in range(k+1):
   for b in range(m+1):
    if a<k:rr.extend([r,r]);cc.extend([ix(a,b),ix(a+1,b)]);dd.extend([1.,-1.]);r+=1
    if b<m:rr.extend([r,r]);cc.extend([ix(a,b),ix(a,b+1)]);dd.extend([1.,-1.]);r+=1
  A=csr_matrix((dd,(rr,cc)),shape=(r,D));E=np.zeros((2,D));E[0,ix(k,m)]=1;E[1,ix(k,0)]=1
  sh0=np.zeros(D);shs=np.zeros(D)
  for a in range(k+1):
   for b in range(m+1):sh0[ix(a,b)]=math.comb(k,a)*math.comb(m,b)/(n*math.comb(n-1,a+b))
  for a in range(k):
   for b in range(m+1):
    w=k*math.comb(k-1,a)*math.comb(m,b)/(n*math.comb(n-1,1+a+b));shs[ix(a+1,b)]+=w;shs[ix(a,b)]-=w
  for alpha in [.1,.25,.5,.75,1.]:
   for start in range(20):
    q=np.exp(rng.uniform(-3,1,2))
    for step in range(20):
     obj=sh0/q[0]+shs/q[1]
     sol=linprog(obj,A_ub=A,b_ub=np.zeros(r),A_eq=E,b_eq=[1,alpha],bounds=(0,1),method='highs');assert sol.success
     p0=float(sh0@sol.x);ps=float(shs@sol.x);ratio=(math.sqrt(max(p0,0))+math.sqrt(k*max(ps,0)))/alpha;out['tests']+=1;out['best']=min(out['best'],ratio)
     if ratio<1-1e-8:out['counter']={'k':k,'m':m,'alpha':alpha,'values':sol.x.reshape(k+1,m+1).tolist(),'phi0':p0,'phis':ps,'ratio':ratio};break
     qnew=np.array([math.sqrt(max(p0,0)),math.sqrt(max(ps,0)/k)]);qnew=np.maximum(qnew,1e-10)
     if max(abs(q-qnew))<1e-8:break
     q=qnew
    if out['counter']:break
   if out['counter']:break
  print(json.dumps({'k':k,'m':m,'tests':out['tests'],'best':out['best']}),flush=True)
  if out['counter']:break
 if out['counter']:break
print(json.dumps(out),flush=True)
