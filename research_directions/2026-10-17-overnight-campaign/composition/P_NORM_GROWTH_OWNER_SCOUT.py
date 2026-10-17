import numpy as np,json
rng=np.random.default_rng(202610170900)
for p in [2,3,4,8,16,32]:
 for K in [max(1,np.sqrt(p-1)),max(1,2*np.sqrt(p-1)),float(p-1)]:
  worst=(0,None)
  for dim in [2,3,5,10]:
   for batch in range(10):
    x=rng.normal(size=(2000,3,dim))*np.exp(rng.normal(size=(2000,3,1)))
    # Mostly aligned, but include arbitrary correlated cancellation.
    if batch%2:x+=rng.normal(size=(2000,1,dim))*3
    ns=np.sum(abs(x)**p,axis=2)**(1/p);S=np.sum(ns,axis=1);x=x/S[:,None,None];ns=ns/S[:,None]
    X=x.sum(axis=1);R=np.sum(abs(X)**p,axis=1)**(1/p);r=R
    active=1-K+K*r>0
    if not np.any(active):continue
    x=x[active];ns=ns[active];X=X[active];r=r[active]
    e=abs(X/r[:,None])**(p-2)*(X/r[:,None]);D=abs(X/r[:,None])**(p-2);a=1-K+K*r
    for coal in [1,3,7]:
     xa=sum(x[:,i,:] for i in range(3) if coal>>i&1);h=np.sum(xa*e,axis=1)
     for i in range(3):
      if not coal>>i&1:continue
      ei=abs(x[:,i,:]/ns[:,i,None])**(p-2)*(x[:,i,:]/ns[:,i,None])
      B=K*(1-h*r)[:,None]*ei+(a+K*h)[:,None]*e+(a*(p-1)/r)[:,None]*(D*xa-h[:,None]*e)
      nb=np.sum(abs(B)**(p/(p-1)),axis=1)**((p-1)/p)
      gap=nb-(K+1);idx=np.argmax(gap)
      if gap[idx]>worst[0]:worst=(float(gap[idx]),{'dim':dim,'x':x[idx].tolist(),'coal':coal,'owner':i,'r':float(r[idx])})
  print(json.dumps({'p':p,'K':K,'max_violation':worst[0],'witness':worst[1]}),flush=True)
