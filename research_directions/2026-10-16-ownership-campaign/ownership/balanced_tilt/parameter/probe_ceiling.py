import random,math

def cases(x,z):
 A=sum(x);B=sum(z)
 if A>B: x,z=z,x;A,B=B,A
 if A<=0:return []
 x=[v/A for v in x];z=[v/A for v in z]
 s=max(x);d=[min(v,1) for v in z];D=sum(d);L=max(d);t=L/D
 if D<=1+1e-12:return []
 caps=sorted([s]+[v for v in d if v>0]);sm=0
 for j,c in enumerate(caps):
  la=(1+s-sm)/(len(caps)-j)
  if la<=c:break
  sm+=c
 P=math.prod(min(la,c)/c for c in caps)
 U=max(s-2/3,0);V=max(t-2/3,0);h1=V*V-U*U;cnt=sum(v>1 for v in z)
 out=[]
 for i,(xx,dd) in enumerate(zip(x,d)):
  if 0<z[i]<1:
   beta=-1/dd if dd>la else -1/la
   h1p=2*V*t*(1-t)/dd if dd==L else -2*V*t/D
   Q=1+beta*(dd-xx)
   b0=.5*Q;b1=h1*Q+h1p*(dd-xx)
   if b1< -1e-12:out.append((b0/-b1,'long',i,x,z,la,s,t,b0,b1))
  e=int(xx==s)
  beta=(1+e)/la-e/s-cnt if s>la else 1/la-cnt
  h1p=2*(V*t*(1-t)*(cnt==1)-U*(e-s))
  dprime=int(z[i]>1)
  b0=1+.5*P*(-1+dprime+beta*(dd-xx))
  b1=P*(h1*(-1+dprime+beta*(dd-xx))+h1p*(dd-xx))
  if b1< -1e-12:out.append((b0/-b1,'short',i,x,z,la,s,t,b0,b1))
 return out

if __name__=='__main__':
 rng=random.Random(119);best=(99,)
 for trial in range(400000):
  n=2+trial%7
  x=[0 if rng.random()<.45 else 10**rng.uniform(-4,2) for _ in range(n)]
  z=[0 if rng.random()<.45 else 10**rng.uniform(-4,2) for _ in range(n)]
  for r in cases(x,z):
   if r[0]<best[0]:
    best=r
    if best[0]<.76:print('best',trial,best,flush=True)
 print('FINAL',best)
