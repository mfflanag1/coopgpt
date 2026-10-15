import numpy as np,random,json
rng=np.random.default_rng(525161);rr=random.Random(525161)
def covers(d):
 # vertices p,h_0..h_d-1,l_0..l_d-1
 cs=[]
 cs.append([0]+[1]*d+[0]*d)
 for hmask in range((1<<d)-1):
  h=[(hmask>>j)&1 for j in range(d)]
  cs.append([1]+h+[1-x for x in h])
 return np.array(cs,dtype=float)
def pay(b,cv,lam):
 accounts=cv@b.T;T=np.min(accounts.sum(axis=1))
 if T<=0:return np.zeros(len(b)),None
 cap=np.minimum(accounts,T);rho=cap.sum(axis=1)/T
 weights=np.exp(-lam*(rho-1));p=weights/weights.sum()
 return p@cap,dict(T=float(T),rho=rho.tolist(),weights=weights.tolist())
count=0
for branches in range(3,7):
 cv=covers(branches)
 for case in range(40000):
  n=rr.randrange(2,10);d=1+2*branches
  b=rng.choice([0,0,0,1,1,2,3,5,10],size=(n,d)).astype(float)
  if case%3==0:b*=rng.choice([0,1],size=(n,d),p=[.6,.4])
  if case%5==0:
   b=np.zeros((n,d))
   for j in range(d):b[rr.randrange(n),j]=rr.choice([1,1,1,2,3,5,10])
  i=rr.randrange(n);j=rr.randrange(d)
  b2=b.copy();b2[i,j]+=rr.choice([.001,.01,.1,.5,1,2])
  for lam in (1.,.9,.5):
   y,info=pay(b,cv,lam);y2,info2=pay(b2,cv,lam);count+=1
   if y2[i]<y[i]-1e-9:
    print(json.dumps(dict(status='COUNTER',checks=count,branches=branches,case=case,owner=i,coordinate=j,lam=lam,b=b.tolist(),b2=b2.tolist(),payment_before=float(y[i]),payment_after=float(y2[i]),T=info['T'],T2=info2['T'])),flush=True)
    raise SystemExit
 print('PASS',branches,count,flush=True)
