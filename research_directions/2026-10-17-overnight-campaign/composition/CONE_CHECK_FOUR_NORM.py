#!/usr/bin/env python3
"""Exact scalar SOS identity and all-sign fourth-norm coalition certificates."""
from fractions import Fraction as F
from pathlib import Path
import random,json
# Four-variable polynomial arithmetic, variables(theta,X,h,k), integer coefficients.
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
t,X,h,k=(var(i) for i in range(4));r=add(const(1),sc(t,-1));L=add(const(1),sc(t,3))
M=add(const(1),sc(t,-3),sc(power(t,2),3))
W=add(const(1),sc(t,-1),sc(power(t,2),7),sc(power(t,3),-6))
u=add(X,mul(r,h));v=add(X,sc(mul(t,h),-1));d=add(X,k)
T=add(mul(d,power(X,3)),sc(mul(mul(mul(t,u),d),power(X,2)),3),sc(mul(mul(t,u),power(X,3)),-3))
original=mul(mul(L,M),add(sc(mul(mul(t,r),power(u,4)),3),sc(mul(power(r,2),power(v,4)),3),mul(L,power(d,4)),sc(T,-4)))
sos=add(mul(mul(power(L,2),M),mul(power(k,2),power(add(k,sc(X,2)),2))),
 sc(mul(mul(mul(mul(t,power(r,2)),L),power(h,2)),power(add(mul(M,h),sc(mul(add(const(1),sc(t,-2)),X),2)),2)),3),
 sc(mul(mul(M,power(X,2)),power(add(mul(L,k),sc(mul(mul(t,r),h),-3)),2)),2),
 sc(mul(mul(mul(mul(t,power(r,2)),W),power(X,2)),power(h,2)),6))
assert original==sos
counts=dict(symbolic_sos_identities=1,symbolic_monomials=len(original),scalar_signed_tests=0,
            profiles=0,coverage=0,budget=0,coalition_tcwm=0,coalition_full_out=0)
rng=random.Random(202610170815)
for _ in range(1500):
 th=F(rng.randrange(21),20);rr=1-th;uu,vv,dd=[F(rng.randrange(-20,21),rng.randrange(1,9)) for _ in range(3)]
 xx=th*uu;zz=rr*vv;XX=xx+zz;hh=uu-vv;kk=dd-XX;LL=1+3*th;MM=1-3*th+3*th*th
 left=(3*th*rr*uu**4+3*rr*rr*vv**4+LL*dd**4)/4-(dd*XX**3+3*xx*dd*XX**2-3*xx*XX**3)
 right=LL/4*kk**2*(kk+2*XX)**2+3*th*rr**2*MM/4*hh**2*(hh+2*(1-2*th)*XX/MM)**2+LL/2*XX**2*(kk-3*th*rr*hh/LL)**2+3*th*rr**2*(1-th+7*th**2-6*th**3)/(2*LL*MM)*XX**2*hh**2
 assert left==right>=0
 counts['scalar_signed_tests']+=1

def sumv(xs,dim):return tuple(sum((x[j] for x in xs),F(0)) for j in range(dim))
def addv(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def n4(x):return sum((v**4 for v in x),F(0))
def cone(b):return b[0]>=0 and b[0]**4>=n4(b[1:])
def cover(amount,b):
 gap=b[0]-amount
 return gap<=0 or gap**4<=n4(b[1:])
def pay(bs):
 C=sumv(bs,len(bs[0]));T=C[0];X=C[1:]
 if not T:return [F(0)]*len(bs)
 return [b[0]-sum((xx*XX**3 for xx,XX in zip(b[1:],X)),F(0))/T**3 for b in bs]
def make(dim):
 if rng.randrange(3)==0:
  x=[F(0)]*dim;x[rng.randrange(dim)]=F(rng.randrange(-6,7),3)
 else:x=[F(rng.randrange(-3,4),3) for _ in range(dim)]
 tt=F(0)
 while tt**4<n4(x):tt+=F(1,3)
 tt+=F(rng.randrange(2),7)
 ans=(tt,)+tuple(x);assert cone(ans);return ans
for dim in [1,2,3,5,16,25]:
 for trial in range(24):
  lowparts=[make(dim) for _ in range(3)];adds=[make(dim) for _ in range(3)]
  # Include flat-boundary signed high-dimensional profiles.
  if dim==16 and trial%3==0:
   lowparts=[(F(2),)+tuple(F(rng.choice([-1,1])) for _ in range(dim)) for _ in range(3)]
  bymask={};reports={}
  for mask in range(8):
   bs=[addv(lowparts[i],adds[i]) if mask>>i&1 else lowparts[i] for i in range(3)]
   ys=pay(bs);C=sumv(bs,dim+1);T=C[0]
   assert all(cone(bb) for bb in bs) and all(y>=0 for y in ys)
   # total<=4(T-||X||4), checked by nonnegative fourth powers exactly.
   rhs=T-sum(ys)/4
   assert rhs>=0 and rhs**4>=n4(C[1:])
   bymask[mask]=ys;reports[mask]=bs;counts['profiles']+=1;counts['budget']+=1
   for coal in range(8):
    inds=[i for i in range(3) if coal>>i&1]
    assert cover(sum((ys[i] for i in inds),F(0)),sumv([bs[i] for i in inds],dim+1))
    counts['coverage']+=1
  for low in range(8):
   for high in range(8):
    if low&high!=low:continue
    changed=high^low;wd=sumv([adds[i] for i in range(3) if changed>>i&1],dim+1)
    for coal in range(8):
     if coal&changed!=changed:continue
     inc=sum((bymask[high][i]-bymask[low][i] for i in range(3) if coal>>i&1),F(0))
     assert inc>=0 and cover(F(512,431)*inc,wd)
     counts['coalition_tcwm']+=1;counts['coalition_full_out']+=1
# Uniform multiplier's temporal minimum is exact and attained collinearly.
s=F(3,4);h=(s-1)/2
assert 1+3*s**3*h==F(431,512)
out={'status':'PASS','arithmetic':'Exact Fraction polynomial identity and fourth-power inequalities; no numerical norms',
 'counts':counts,'dimensions':[1,2,3,5,16,25],
 'scope':'SOS identity proves arbitrary scalar inputs and any dimension; finite owner-profile checks supplement all-profile calculus proof.'}
Path(__file__).with_name('CONE_FOUR_NORM_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
