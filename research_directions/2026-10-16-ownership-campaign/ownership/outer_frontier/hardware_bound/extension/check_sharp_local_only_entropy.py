"""Floating attempted falsification of the analytic all-switch lemma, not proof."""
import math,random,json
from pathlib import Path
random.seed(161024)
K=math.e-1

def phi(a,b):
 A,B=sum(a),sum(b)
 if min(A,B)<=0:return [0.]*len(a)
 if A>B:return phi(b,a)
 d=[min(x,A)for x in b];q=.5*math.exp(1-sum(d)/A)
 return [(1-q)*x+q*y for x,y in zip(a,d)]
checks=0;switches=0;maxfirst=0.;maxentropy=0.
for case in range(60000):
 n=random.choice([2,3,4,5,10,30]);a=[random.expovariate(1) if random.random()>.15 else 0. for _ in range(n)]
 if sum(a)==0:continue
 a=[x/sum(a) for x in a];i=random.randrange(n)
 b=[random.expovariate(1)*random.choice([.01,.2,1,4])/n for _ in range(n)]
 if random.random()<.6:b[i]+=max(0,1-sum(b))+random.random()
 if sum(b)<1:b=[x/sum(b)for x in b]
 d=min(b[i],1);rho=sum(min(x,1)for x in b);q=.5*math.exp(1-rho);V=q*d
 old=phi(a,b);bb=b[:];bb[i]*=random.choice([0,random.random(),random.random()])
 new=phi(a,bb);inc=sum(max(0,new[j]-old[j])for j in range(n)if j!=i)
 first=q*math.expm1(d)*(rho-d)
 entropy=K*V*math.log(1/(2*V)) if V>0 else 0.
 if inc>first+2e-12 or first>entropy+2e-12:
  raise RuntimeError((case,inc,first,entropy,a,b,i,bb))
 if first>1e-15:maxfirst=max(maxfirst,inc/first)
 if entropy>1e-15:maxentropy=max(maxentropy,inc/entropy)
 checks+=1;switches+=sum(bb)<1
sharp=[]
for rho in [2,2.5,3,5,10,50]:
 b=[1.];remaining=rho-1
 while remaining>1e-13:
  val=min(1.,remaining);b.append(val);remaining-=val
 # Add one pure short owner, keeping all fixed identities.
 a=[0.]*len(b)+[1.];b=b+[0.]
 old=phi(a,b);bb=b[:];bb[0]=0.;new=phi(a,bb)
 inc=sum(max(0,new[j]-old[j])for j in range(1,len(b)))
 V=.5*math.exp(1-rho);bound=K*V*math.log(1/(2*V))
 if abs(inc-bound)>1e-12:raise RuntimeError(('sharp',rho,inc,bound))
 sharp.append({'rho':rho,'incoming':inc,'bound':bound})
out={'status':'PASS','scope':'Floating corroboration only','random_long_coordinate_checks':checks,'pool_switches':switches,'max_incoming_to_exact_cap_bound':maxfirst,'max_incoming_to_entropy_bound':maxentropy,'sharpness_replays':sharp}
Path(__file__).with_name('sharp_local_only_entropy_diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
