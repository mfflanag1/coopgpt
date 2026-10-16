"""Floating falsification diagnostics only; proofs are analytical."""
import math,random,json,itertools

def phi(a,b):
 A=sum(a);B=sum(b);T=min(A,B)
 if not T:return [0.]*len(a)
 s,l=(a,b) if A<=B else (b,a)
 ds=[min(v,T) for v in l];q=.5*math.exp(1-sum(ds)/T)
 return [(1-q)*u+q*v for u,v in zip(s,ds)]

def require(x,msg):
 if not x:raise RuntimeError(msg)

count=0;recipient_checks=0;maxratio=0;witness=None
rng=random.Random(811)
def check(a,b):
 global count,recipient_checks,maxratio,witness
 z=phi(a,b);H=sum(a);n=len(a);count+=1
 for k in range(n):
  # Cross-monotonicity predicts deletion of the recipient's greater own input.
  beneficial=0 if a[k]>=b[k] else 1
  gain=0
  for i in range(n):
   if i==k:continue
   aa=a.copy();bb=b.copy();(aa if beneficial==0 else bb)[i]=0
   gain+=max(0,phi(aa,bb)[k]-z[k])
  slack=H-z[k];recipient_checks+=1
  require(gain<=slack+1e-10*max(1,H),'recipient response inequality')
  if slack>1e-10*max(1,H) and gain/slack>maxratio:
   maxratio=gain/slack;witness={'a':a,'b':b,'recipient':k,'gain':gain,'H_minus_z':slack}
for n in range(1,5):
 for r in itertools.product(tuple(itertools.product((0.,1.,2.),repeat=2)),repeat=n):
  check([t[0] for t in r],[t[1] for t in r])
for trial in range(20000):
 n=2+trial%9
 a=[0 if rng.random()<.35 else 10**rng.uniform(-3,3) for _ in range(n)]
 b=[0 if rng.random()<.35 else 10**rng.uniform(-3,3) for _ in range(n)]
 check(a,b)
print(json.dumps({'status':'PASS','scope':'Floating finite falsification diagnostics only, not proof.','profiles':count,'recipient_checks':recipient_checks,'max_observed_response_ratio':maxratio,'witness':witness},indent=2))
