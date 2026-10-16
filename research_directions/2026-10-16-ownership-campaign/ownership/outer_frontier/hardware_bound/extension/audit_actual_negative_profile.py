"""Independent interval replay of an actual report comparison, not a universal proof."""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import json
B=1<<64

def require(v,s):
 if not v:raise RuntimeError(s)

def down(x):return Q((x*B).numerator//(x*B).denominator,B)
def up(x):return -down(-x)
class I:
 def __init__(self,l,h=None):
  l=Q(l);h=l if h is None else Q(h)
  require(l<=h,'bad interval');self.l=down(l);self.h=up(h)
 def __add__(self,o):
  o=iv(o);return I(self.l+o.l,self.h+o.h)
 __radd__=__add__
 def __neg__(self):return I(-self.h,-self.l)
 def __sub__(self,o):return self+-iv(o)
 def __rsub__(self,o):return iv(o)+-self
 def __mul__(self,o):
  o=iv(o);v=[self.l*o.l,self.l*o.h,self.h*o.l,self.h*o.h];return I(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,o):
  o=iv(o);require(o.l>0,'nonpositive divisor');return self*I(1/o.h,1/o.l)
 def __rtruediv__(self,o):return iv(o)/self
 def mini(self,o):
  o=iv(o);return I(min(self.l,o.l),min(self.h,o.h))
 def ex(self):return I(er(self.l)[0],er(self.h)[1])
 def info(self):return {'lower':str(self.l),'upper':str(self.h),'mid_display':float((self.l+self.h)/2)}
def iv(x):return x if isinstance(x,I) else I(x)
@lru_cache(None)
def er(x):
 if x<0:
  l,h=er(-x);return Q(1)/h,Q(1)/l
 require(x<4,'exponential range')
 term=Q(1);s=term
 for k in range(1,25):term*=x/k;s+=term
 nxt=term*x/25;tail=nxt/(1-x/26)
 return down(s),up(s+tail)
def phi(a,b):
 a=list(map(iv,a));b=list(map(iv,b));A=sum(a,I(0));BB=sum(b,I(0))
 if A.h==0 or BB.h==0:return [I(0) for _ in a]
 if A.h<=BB.l:s,l,T=a,b,A
 elif BB.h<=A.l:s,l,T=b,a,BB
 else:raise RuntimeError('ambiguous pool ordering')
 d=[x.mini(T) for x in l];rho=sum(d,I(0))/T
 q=Q(1,2)*(1-rho).ex()
 return [(1-q)*x+q*y for x,y in zip(s,d)]
def profile(r,m,eps):
 n=2+2*m;h=[[Q(0) for _ in range(2*r)] for _ in range(n)];l=[[Q(0) for _ in range(2*r)] for _ in range(n)]
 for j in range(r):
  h[1][j]=Q(1,r);l[0][j]=(1-eps)/r
  for k in range(m):l[2+k][j]=Q(1,r*m)
 for j in range(r,2*r):
  h[0][j]=h[1][j]=Q(1,2*r)
  for k in range(m):l[2+m+k][j]=Q(1,2*r*m)
 p=[Q(0)]*n;p[1]=Q(2)
 z=[I(0) for _ in range(n)]
 for j in range(2*r):
  yy=phi([h[i][j] for i in range(n)],[l[i][j] for i in range(n)])
  z=[a+b for a,b in zip(z,yy)]
 H=[sum(x) for x in h];out=phi(H,[iv(x)+y for x,y in zip(p,z)])
 return H,z,out
out=[]
for r,m in [(1,1),(3,7),(5,11)]:
 h,z,y=profile(r,m,Q(0));hh,zz,yy=profile(r,m,Q(1,20))
 require(h==hh,'actual hardware changed')
 gain=yy[0]-y[0];loss=z[0]-zz[0]
 require(gain.l>0,'actual profitable local-only deviation not certified')
 require(loss.l>0,'own local payment did not decrease')
 require((iv(h[0])-z[0]).l>0,'full negative gap not certified')
 out.append({'branches':2*r,'owners':2*m+2,'epsilon':'1/20','actual_payment_gain':gain.info(),'own_local_loss':loss.info()})
result={'status':'PASS','arithmetic':'64-bit dyadic outward intervals; exact Fraction Taylor remainders','scope':'Three actual instances verify the formula and strict gain; the separate analytic family proves unbounded counts and asymptotic order.','results':out}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
