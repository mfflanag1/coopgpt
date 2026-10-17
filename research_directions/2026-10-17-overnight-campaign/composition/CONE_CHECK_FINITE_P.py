#!/usr/bin/env python3
"""Exact finite checks supplementing the all-real-p analytic cone proof."""
from fractions import Fraction as F
from pathlib import Path
import json, random
Z=(0,0,0,0)
def const(a):return {} if not a else {Z:F(a)}
def var(i):
 k=list(Z);k[i]=1;return {tuple(k):F(1)}
def add(*ps):
 out={}
 for p in ps:
  for k,v in p.items():out[k]=out.get(k,F(0))+v
 return {k:v for k,v in out.items() if v}
def sc(p,a):return {k:v*a for k,v in p.items() if v*a}
def mul(p,q):
 out={}
 for k,v in p.items():
  for l,w in q.items():
   z=tuple(a+b for a,b in zip(k,l));out[z]=out.get(z,F(0))+v*w
 return {k:v for k,v in out.items() if v}
def power(p,n):
 out=const(1)
 for _ in range(n):out=mul(out,p)
 return out
t,X,h,k=(var(i) for i in range(4));r=add(const(1),sc(t,-1))
u=add(X,mul(r,h));v=add(X,sc(mul(t,h),-1));d=add(X,k)
counts=dict(symbolic_bregman_identities=0,symbolic_quadratic_identities=0,scalar_signed_tests=0,
 profiles=0,coverage=0,budget=0,coalition_tcwm=0,coalition_full_out=0,temporal_minima=0)
for p in [2,4,6,8,10]:
 m=p-1;L=add(const(1),sc(t,m))
 def bf(z):return add(sc(add(power(z,p),sc(power(X,p),-1)),F(1,p)),sc(mul(power(X,m),add(z,sc(X,-1))),-1))
 original=add(sc(mul(mul(t,r),power(u,p)),F(m,p)),sc(mul(power(r,2),power(v,p)),F(m,p)),sc(mul(L,power(d,p)),F(1,p)),sc(mul(d,power(X,m)),-1),sc(mul(mul(mul(t,u),d),power(X,p-2)),-m),sc(mul(mul(t,u),power(X,m)),m))
 breg=add(mul(L,bf(d)),sc(mul(r,add(mul(t,bf(u)),mul(r,bf(v)))),m),sc(mul(mul(mul(mul(t,r),power(X,p-2)),h),k),-m))
 assert original==breg
 counts['symbolic_bregman_identities']+=1
 # Clear denominator L from the completed quadratic square identity.
 left=mul(L,add(mul(L,power(k,2)),sc(mul(mul(t,power(r,2)),power(h,2)),m),sc(mul(mul(mul(t,r),h),k),-2*m)))
 right=add(power(add(mul(L,k),sc(mul(mul(t,r),h),-m)),2),sc(mul(mul(t,power(r,2)),power(h,2)),m))
 assert left==right
 counts['symbolic_quadratic_identities']+=1
rng=random.Random(202610170825)
ps=[2,3,4,5,6,8,10]
for p in ps:
 m=p-1
 for _ in range(200):
  th=F(rng.randrange(21),20);rr=1-th;uu,vv,dd=[F(rng.randrange(-20,21),rng.randrange(1,9)) for _ in range(3)]
  XX=th*uu+rr*vv;xx=th*uu;hh=uu-vv;kk=dd-XX;LL=1+m*th
  J=abs(XX)**(p-2)*XX;curv=abs(XX)**(p-2)
  gap=(m*th*rr*abs(uu)**p+m*rr*rr*abs(vv)**p+LL*abs(dd)**p)/p-(dd*J+m*xx*dd*curv-m*xx*J)
  def bf(z):return (abs(z)**p-abs(XX)**p)/p-J*(z-XX)
  breg=LL*bf(dd)+m*rr*(th*bf(uu)+rr*bf(vv))-m*th*rr*curv*hh*kk
  lower=curv*(LL*(kk-m*th*rr*hh/LL)**2+m*th*rr*rr*hh*hh/LL)/2
  assert gap==breg and gap>=lower>=0
  assert all(bf(z)>=curv*(z-XX)**2/2 for z in [uu,vv,dd])
  counts['scalar_signed_tests']+=1

def sumv(xs,dim):return tuple(sum((x[j] for x in xs),F(0)) for j in range(dim))
def addv(a,b):return tuple(x+y for x,y in zip(a,b))
def npow(x,p):return sum((abs(v)**p for v in x),F(0))
def cone(b,p):return b[0]>=0 and b[0]**p>=npow(b[1:],p)
def cover(amount,b,p):
 gap=b[0]-amount
 return gap<=0 or gap**p<=npow(b[1:],p)
def pay(bs,p):
 C=sumv(bs,len(bs[0]));T=C[0];X=C[1:]
 if not T:return [F(0)]*len(bs)
 return [b[0]-sum((xx*abs(XX)**(p-2)*XX for xx,XX in zip(b[1:],X)),F(0))/T**(p-1) for b in bs]
def make(dim,p):
 if rng.randrange(3)==0:
  x=[F(0)]*dim;x[rng.randrange(dim)]=F(rng.randrange(-6,7),3)
 else:x=[F(rng.randrange(-3,4),3) for _ in range(dim)]
 tt=F(0)
 while tt**p<npow(x,p):tt+=F(1,3)
 tt+=F(rng.randrange(2),7)
 ans=(tt,)+tuple(x);assert cone(ans,p);return ans
for p in ps:
 scale=F(2*p**p,2*p**p-(p-1)**p)
 s=F(p-1,p);hh=(s-1)/2
 assert 1+(p-1)*s**(p-1)*hh==1/scale
 counts['temporal_minima']+=1
 for dim in [1,2,3,8]:
  for trial in range(12):
   lows=[make(dim,p) for _ in range(3)];adds=[make(dim,p) for _ in range(3)]
   bymask={}
   for mask in range(8):
    bs=[addv(lows[i],adds[i]) if mask>>i&1 else lows[i] for i in range(3)]
    ys=pay(bs,p);C=sumv(bs,dim+1);T=C[0]
    assert all(cone(bb,p) for bb in bs) and all(y>=0 for y in ys)
    rhs=T-sum(ys)/p
    assert rhs>=0 and rhs**p>=npow(C[1:],p)
    bymask[mask]=ys;counts['profiles']+=1;counts['budget']+=1
    for coal in range(8):
     ids=[i for i in range(3) if coal>>i&1]
     assert cover(sum((ys[i] for i in ids),F(0)),sumv([bs[i] for i in ids],dim+1),p)
     counts['coverage']+=1
   for low in range(8):
    for high in range(8):
     if low&high!=low:continue
     changed=high^low;wd=sumv([adds[i] for i in range(3) if changed>>i&1],dim+1)
     for coal in range(8):
      if coal&changed!=changed:continue
      inc=sum((bymask[high][i]-bymask[low][i] for i in range(3) if coal>>i&1),F(0))
      assert inc>=0 and cover(scale*inc,wd,p)
      counts['coalition_tcwm']+=1;counts['coalition_full_out']+=1
out={'status':'PASS','arithmetic':'Exact Fraction identities and integer power inequalities; no numerical norms',
 'counts':counts,'exponents':ps,'dimensions':[1,2,3,8],
 'scope':'Finite checks supplement analytic proof for every real p>=2, all dimensions, and all profiles.'}
Path(__file__).with_name('CONE_FINITE_P_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
