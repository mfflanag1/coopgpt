"""Floating nonlinear-loss falsification checks; analytic proof remains load-bearing."""
import math,itertools,random,json

def phi(a,b):
 A=sum(a);B=sum(b);T=min(A,B)
 if not T:return [0.]*len(a)
 s,l=(a,b) if A<=B else (b,a)
 ds=[min(v,T) for v in l];q=.5*math.exp(1-sum(ds)/T)
 return [(1-q)*u+q*v for u,v in zip(s,ds)]
def require(v,msg):
 if not v:raise RuntimeError(msg)
count=0;maximum=0;witness=None

def check(a,b,i,aa,bb):
 global count,maximum,witness
 z=phi(a,b);zp=phi(aa,bb);loss=sum(max(0,z[k]-zp[k]) for k in range(len(a)) if k!=i)
 count+=1;scale=max(1,sum(a),sum(b))
 require(loss<=(math.e-1)*z[i]+1e-11*scale,'linear outgoing bound failed')
 D=z[i]-zp[i]
 require(D>=-1e-11*scale,'own monotonicity prerequisite')
 B2=(math.e-1)**2
 require(loss**2<=B2*z[i]*max(0,D)+1e-10*scale**2,'nonlinear outgoing bound failed')
 if z[i]>1e-10*scale and D>1e-10*scale and loss/math.sqrt(z[i]*D)>maximum:
  maximum=loss/math.sqrt(z[i]*D);witness={'h':a,'l':b,'i':i,'h_prime':aa,'l_prime':bb,'loss':loss,'own_payment':z[i],'own_payment_loss':D}
for n in range(1,5):
 for r in itertools.product(tuple(itertools.product((0.,1.,2.),repeat=2)),repeat=n):
  a=[x[0] for x in r];b=[x[1] for x in r]
  for i in range(n):
   for ai in range(int(a[i])+1):
    for bi in range(int(b[i])+1):
     aa=a.copy();bb=b.copy();aa[i]=float(ai);bb[i]=float(bi);check(a,b,i,aa,bb)
rng=random.Random(191)
for it in range(50000):
 n=2+it%10;a=[0 if rng.random()<.35 else 10**rng.uniform(-4,4) for _ in range(n)];b=[0 if rng.random()<.35 else 10**rng.uniform(-4,4) for _ in range(n)]
 i=it%n;aa=a.copy();bb=b.copy();aa[i]*=rng.choice((0,1,rng.random()));bb[i]*=rng.choice((0,1,rng.random()));check(a,b,i,aa,bb)
# Sharpness and a negative control: 4/e is too small for the whole lemma.
c=1/(2*math.e);loss=.5-c
require(abs(loss-(math.e-1)*c)<1e-15,'sharpness identity')
require(loss>(4/math.e)*c,'smaller-constant negative control')
print(json.dumps({'status':'PASS','scope':'Floating finite falsification only; no numerical proof or general upper-bound certificate.','owner_transitions_checked':count,'largest_observed_ratio':maximum,'proved_nonlinear_constant':math.e-1,'witness':witness,'negative_control_4_over_e_rejected':True},sort_keys=True,indent=2))
