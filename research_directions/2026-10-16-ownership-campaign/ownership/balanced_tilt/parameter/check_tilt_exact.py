"""Exact finite diagnostics, separate from the all-real proofs. Fail closed."""
from fractions import Fraction as F
from itertools import product
import json,random,sys

COUNTS={'profiles':0,'coalitions':0,'own_comparisons':0,'attainers':0,'negative_controls':0}

def require(ok,msg):
 if not ok: raise RuntimeError(msg)

def cubic(s): return -36*s**3+27*s*s+4*s-2

def excess(s): return (1-F(3,2)*(s-F(2,3))**2)*(1+s)**3/(54*s)

lo=F(2,3);hi=F(1)
for _ in range(150):
 mid=(lo+hi)/2
 if cubic(mid)>0:lo=mid
 else:hi=mid
require(cubic(lo)>0 and cubic(hi)<0,'root isolation')
glower=1+excess(lo)
gupper=1+(1-F(3,2)*(lo-F(2,3))**2)*(1+hi)**3/(54*hi)
require(F('1.1314008171210423')<glower<gupper<F('1.1314008171210424'),'decimal interval')

# Water filling by increasing the common level through sorted cap thresholds.
def rule(reports,a):
 n=len(reports);sa=sum(r[0] for r in reports);sb=sum(r[1] for r in reports)
 if min(sa,sb)==0:return (F(0),)*n
 short=0 if sa<=sb else 1;long=1-short;A=min(sa,sb)
 x=[r[short] for r in reports];d=[min(r[long],A) for r in reports]
 M=max(x);D=sum(d);L=max(d);caps=[M]+[v for v in d if v>0]
 caps.sort();target=A+M;previous=F(0);used=F(0);left=len(caps)
 for cap in caps:
  needed=(cap-previous)*left
  if used+needed>=target:
   water=previous+(target-used)/left;break
  used+=needed;left-=1;previous=cap
 else:raise RuntimeError('water target exceeds cap sum')
 require(sum(min(c,water) for c in caps)==target,'water identity')
 P=F(1)
 for cap in caps:P*=min(cap,water)/cap
 psi=lambda z:max(F(0),z-F(2,3))**2
 h=F(1,2)+a*(psi(L/D)-psi(M/A));p=h*P
 return tuple((1-p)*u+p*v for u,v in zip(x,d))

maxima={}
for a in [F(1,4),F(3,4)]:
 bound=F(277,243) if a==F(1,4) else gupper
 maxratio=F(0);maxprofile=None
 for n in range(1,5):
  states=tuple(product(tuple(product((F(0),F(1),F(2)),repeat=2)),repeat=n))
  ys={r:rule(r,a) for r in states}
  for r,y in ys.items():
   COUNTS['profiles']+=1;T=min(sum(t[0] for t in r),sum(t[1] for t in r))
   require(all(v>=0 for v in y),'nonnegativity')
   require(sum(y)<=bound*T,'funding bound')
   if T and sum(y)/T>maxratio:maxratio=sum(y)/T;maxprofile=r
   for mask in range(1<<n):
    yy=sum(y[i] for i in range(n) if mask>>i&1)
    vv=min(sum(r[i][j] for i in range(n) if mask>>i&1) for j in (0,1))
    require(yy>=vv,'coalition coverage');COUNTS['coalitions']+=1
   for i in range(n):
    for j in (0,1):
     if r[i][j]==2:continue
     rr=[list(t) for t in r];rr[i][j]+=1;rr=tuple(tuple(t) for t in rr)
     require(ys[rr][i]>=y[i],'grid own monotonicity');COUNTS['own_comparisons']+=1
 rng=random.Random(719)
 for trial in range(4000):
  n=2+trial%7
  r=tuple((F(rng.randrange(20),rng.randrange(1,12)),F(rng.randrange(20),rng.randrange(1,12))) for _ in range(n))
  y=rule(r,a);T=min(sum(t[0] for t in r),sum(t[1] for t in r));COUNTS['profiles']+=1
  require(all(v>=0 for v in y) and sum(y)<=bound*T,'random funding/nonnegative')
  if T and sum(y)/T>maxratio:maxratio=sum(y)/T;maxprofile=r
  i=rng.randrange(n);j=rng.randrange(2)
  rr=[list(t) for t in r];rr[i][j]+=F(1,rng.choice((10,100,1000,100000)));rr=tuple(tuple(t) for t in rr)
  require(rule(rr,a)[i]>=y[i],'random small own increment');COUNTS['own_comparisons']+=1
 maxima[str(a)]={'observed_factor':str(maxratio),'decimal':float(maxratio),'profile':[[str(x) for x in t] for t in maxprofile]}
# Exact rational attainers for every concentration s>=1/2.
for k in range(50,101):
 s=F(k,100);r=((s,F(0)),(1-s,F(0)),(F(0),F(1)),(F(0),F(1)))
 y=rule(r,F(3,4));expected=1+(1-F(3,2)*max(s-F(2,3),0)**2)*(1+s)**3/(54*s)
 require(sum(y)==expected,'concentration attainer');COUNTS['attainers']+=1
# Failure beyond the ceiling: both ends are exact rational profiles on fixed owners.
high=((F(99,100),F(0)),(F(1,100),F(0)),(F(0),F(999999,1000000)),(F(0),F(1,1000000)))
low=list(high);low[0]=(high[0][0]-F(1,10**9),F(0));low=tuple(low)
negative=[]
for a in [F(4,5),F(751,1000)]:
 gap=rule(high,a)[0]-rule(low,a)[0]
 require(gap<0,'negative control beyond ceiling did not fail')
 negative.append({'a':str(a),'high_minus_low_own_payment':str(gap)});COUNTS['negative_controls']+=1
print(json.dumps({'status':'PASS','scope':'Exact finite diagnostics; not a substitute for the continuous proofs.','counts':COUNTS,'root_interval':[str(lo),str(hi)],'gamma_interval':[str(glower),str(gupper)],'gamma_decimal':float(glower),'observed_maxima':maxima,'negative_controls':negative},indent=2))
