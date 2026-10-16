import random,math,json

def phi(a,b):
 A=sum(a);B=sum(b);T=min(A,B)
 if not T:return [0.]*len(a)
 s,l=(a,b) if A<=B else (b,a)
 d=[min(v,T) for v in l];q=.5*math.exp(1-sum(d)/T)
 return [(1-q)*u+q*v for u,v in zip(s,d)]
rng=random.Random(325);best=0;witness=None
for it in range(100000):
 n=2+it%8
 h=[0 if rng.random()<.4 else 10**rng.uniform(-2,2) for _ in range(n)]
 l=[0 if rng.random()<.4 else 10**rng.uniform(-2,2) for _ in range(n)]
 H=sum(h)
 if not H:continue
 z=phi(h,l)
 i=it%n
 for f,g in ((0,0),(0,1),(1,0),(rng.random(),rng.random())):
  hh=h.copy();ll=l.copy();hh[i]*=f;ll[i]*=g;zz=phi(hh,ll)
  loss=sum(max(0,z[k]-zz[k]) for k in range(n) if k!=i)
  if loss/H>best:
   best=loss/H;witness={'h':h,'l':l,'i':i,'f':f,'g':g,'loss':loss,'H':H,'z':z,'zp':zz}
print(json.dumps({'ratio':best,'witness':witness},indent=2))
