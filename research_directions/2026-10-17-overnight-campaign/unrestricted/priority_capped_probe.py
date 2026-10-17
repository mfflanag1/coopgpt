import numpy as np,json
rng=np.random.default_rng(413)
for trial in range(20000):
 n=int(rng.integers(3,9));d=int(rng.integers(2,7));k=int(rng.integers(2,9));f=rng.integers(0,8,(k,d));b=rng.integers(0,8,(n,d));M=np.array([[s>>i&1 for i in range(n)]for s in range(1<<n)]);v=np.min(M@b@f.T,axis=1)
 u=np.array([v[-1]-v[((1<<n)-1)^(1<<i)]for i in range(n)])
 y=np.array([min(u[i],max(v[s|(1<<i)]-v[s]for s in range(1<<i)))for i in range(n)])
 viol=v-M@y
 if max(viol)>0:
  print(json.dumps({'trial':trial,'n':n,'forms':f.tolist(),'b':b.tolist(),'v':v.tolist(),'u':u.tolist(),'y':y.tolist(),'bad':int(np.argmax(viol))}));break
else:print('no violation')
