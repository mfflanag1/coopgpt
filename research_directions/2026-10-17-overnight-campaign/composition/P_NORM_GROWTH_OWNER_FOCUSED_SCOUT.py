import numpy as np,json
for p in [2,3,4,8,16,32,64,128,256]:
 for K in [1,max(1,np.sqrt(p-1)/2),max(1,np.sqrt(p-1)),max(1,2*np.sqrt(p-1))]:
  worst=(0,None)
  for delta in np.linspace(.00001,.499,1000):
   x=np.array([[.5+delta,.5-delta],[.5-delta,.5+delta]])
   ns=np.sum(abs(x)**p,axis=1)**(1/p);S=sum(ns);x=x/S;ns=ns/S;X=x.sum(axis=0);R=np.sum(abs(X)**p)**(1/p);r=R
   a=1-K+K*r
   if a<=0:continue
   e=abs(X/R)**(p-2)*(X/R);D=abs(X/R)**(p-2);xa=x[0];h=np.dot(xa,e);ei=abs(xa/ns[0])**(p-2)*(xa/ns[0])
   B=K*(1-h*r)*ei+(a+K*h)*e+a*(p-1)/r*(D*xa-h*e)
   nb=np.sum(abs(B)**(p/(p-1)))**((p-1)/p);gap=nb-(K+1)
   if gap>worst[0]:worst=(float(gap),float(delta))
  print(json.dumps({'p':p,'K':K,'max_violation':worst[0],'delta':worst[1]}),flush=True)
