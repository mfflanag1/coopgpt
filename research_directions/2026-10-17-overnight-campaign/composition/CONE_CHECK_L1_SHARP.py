#!/usr/bin/env python3
"""Exact rational TCWM and certified log-interval full-OUT L1 lift checks."""
from fractions import Fraction as F
from pathlib import Path
from functools import lru_cache
import random,json
cl=F(543063389825,10**12);ch=F(543063389826,10**12)
def expneg(x):
 term=S=F(1)
 for k in range(1,61):term=term*x/k;S+=term
 nxt=term*x/61;upper=S+nxt/(1-x/62)
 return 1/upper,1/S
assert cl*(2-expneg(1/cl)[0])-1<0
assert ch*(2-expneg(1/ch)[1])-1>0
tlo,thi=1/ch-1,1/cl-1
@lru_cache(None)
def logbound(z):
 assert 0<z<=1
 a=(1-z)/(1+z);term=a;S=F(0)
 for k in range(70):S+=term/F(2*k+1);term*=a*a
 tail=2*term/(141*(1-a*a))
 return -2*S-tail,-2*S
class E:
 # a+c*(b+sum coefficient*log(rational argument))
 def __init__(self,a=0,b=0,logs=None):self.a=F(a);self.b=F(b);self.logs={k:F(v) for k,v in (logs or {}).items() if v}
 def __add__(self,o):
  if not isinstance(o,E):o=E(o)
  z=self.logs.copy()
  for k,v in o.logs.items():z[k]=z.get(k,F(0))+v
  return E(self.a+o.a,self.b+o.b,z)
 __radd__=__add__
 def __mul__(self,z):return E(self.a*z,self.b*z,{k:v*z for k,v in self.logs.items()})
 __rmul__=__mul__
 def __neg__(self):return self*-1
 def __sub__(self,o):return self+-o
 def zero(self):return not self.a and not self.b and not self.logs
 def bounds(self):
  lo=hi=self.b
  for z,v in self.logs.items():
   l,h=logbound(z)
   if v<0:l,h=h,l
   lo+=v*l;hi+=v*h
  vals=[cl*lo,cl*hi,ch*lo,ch*hi]
  return self.a+min(vals),self.a+max(vals)
 def nonnegative(self):return self.zero() or self.bounds()[0]>=0
kappa=E(1,1)
def qp(r):
 assert 0<r<=1
 if r<tlo:return E(1,-1,{1-r:-(1-r)/r}),E(0,1/r,{1-r:1/(r*r)})
 assert r>thi
 return E(0,1/r),E(0,-1/(r*r))
counts=dict(root_bracket_certificates=2,scalar_derivative_checks=0,profiles=0,tcwm_profiles=0,coverage=0,
 funding=0,coalition_tcwm=0,coalition_full_out=0,signed_transfer_checks=0)
# Scalar pair derivative bounds, including mixed coalition holdings.
for j in range(1,21):
 r=F(j,20);q,dq=qp(r)
 for u in map(lambda z:F(z,4),range(5)):
  for v in map(lambda z:F(z,4),range(5)):
   al=E(0,r*(1-u))-dq*(v*r*r);be=q+E(0,u)+dq*(v*r)
   for ex in [al,be,kappa-al,kappa-be,al+be-1,kappa-al-be]:assert ex.nonnegative(),(r,u,v,ex.bounds())
   counts['scalar_derivative_checks']+=6
# Independent finite sign-lemma validation over rational feasible coefficients.
for kap in [F(3,2),F(8,5),F(2)]:
 for aa in [kap*j/6 for j in range(7)]:
  for bb in [kap*j/6 for j in range(7)]:
   if not 1<=aa+bb<=2*kap-1:continue
   for r in map(F,range(-3,4)):
    for v in map(F,range(-3,4)):
     sl=(kap-1)*(abs(r)+abs(v))+2*aa*r+2*bb*v-kap*(r+v)+abs(r-v)
     assert sl>=0;counts['signed_transfer_checks']+=1

def sumv(xs,d):return tuple(sum((x[j] for x in xs),F(0)) for j in range(d))
def norm(x):return sum(map(abs,x),F(0))
def val(b):return b[0]-norm(b[1:])
def addv(a,b):return tuple(x+y for x,y in zip(a,b))
def payments(bs,full):
 n=len(bs);dim=len(bs[0])-1
 ys=[kappa*val(b) if full else F(3,2)*val(b) for b in bs]
 for j in range(dim):
  aa=[max(b[j+1],0) for b in bs];bb=[max(-b[j+1],0) for b in bs]
  A=sum(aa);B=sum(bb)
  if not A or not B:continue
  if A<B:aa,bb=bb,aa;A,B=B,A
  r=B/A
  if full:
   q,dq=qp(r)
   for i in range(n):ys[i]+=2*(E(0,aa[i]*r)+q*bb[i])
  else:
   for i in range(n):ys[i]+=aa[i]*r+bb[i]*(2-r)
 return ys
rng=random.Random(202610170845)
def make(dim):
 x=tuple(F(rng.randrange(-5,6),3) for _ in range(dim))
 return (norm(x)+F(rng.randrange(3),4),)+x
for dim in [1,2,3,7]:
 for trial in range(12):
  lows=[make(dim) for _ in range(3)];adds=[make(dim) for _ in range(3)]
  tpay={};opay={}
  for mask in range(8):
   bs=[addv(lows[i],adds[i]) if mask>>i&1 else lows[i] for i in range(3)]
   yy=payments(bs,False);zz=payments(bs,True);C=sumv(bs,dim+1)
   assert sum(yy)<=F(3,2)*val(C)
   assert (kappa*val(C)-sum(zz,E())).nonnegative()
   counts['funding']+=2;counts['profiles']+=1
   for coal in range(8):
    ids=[i for i in range(3) if coal>>i&1];vv=val(sumv([bs[i] for i in ids],dim+1))
    assert sum((yy[i] for i in ids),F(0))>=vv
    assert (sum((zz[i] for i in ids),E())-vv).nonnegative()
    counts['coverage']+=2
   tpay[mask]=yy;opay[mask]=zz
  for lo in range(8):
   for hi in range(8):
    if lo&hi!=lo:continue
    chg=lo^hi;wd=sumv([adds[i] for i in range(3) if chg>>i&1],dim+1)
    for coal in range(8):
     if coal&chg!=chg:continue
     ids=[i for i in range(3) if coal>>i&1]
     inc=sum((tpay[hi][i]-tpay[lo][i] for i in ids),F(0))
     outinc=sum((opay[hi][i]-opay[lo][i] for i in ids),E())
     assert inc>=0
     assert (outinc-val(wd)).nonnegative(),(dim,trial,lo,hi,coal,(outinc-val(wd)).bounds())
     counts['coalition_tcwm']+=1;counts['coalition_full_out']+=1
out={'status':'PASS','arithmetic':'Exact Fraction TCWM; exact rational log/exp enclosures and symbolic cancellation for full OUT',
'counts':counts,'c_interval':[str(cl),str(ch)],'dimensions':[1,2,3,7],
'scope':'Finite L1 tests validate the explicit rules; analytic signed-transfer proof covers every fixed L1 embedding.'}
Path(__file__).with_name('CONE_L1_SHARP_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
