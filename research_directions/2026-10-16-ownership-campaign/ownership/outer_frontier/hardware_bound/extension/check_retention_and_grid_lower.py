"""Floating falsification/replay of analytic claims; not a proof."""
import math,random,json
from pathlib import Path
random.seed(161025);K=math.e-1;c=1/(2*math.e);C=1+c

def phi(a,b):
 A,B=sum(a),sum(b)
 if min(A,B)<=0:return [0.]*len(a)
 if A>B:return phi(b,a)
 d=[min(x,A)for x in b];q=.5*math.exp(1-sum(d)/A)
 return [(1-q)*x+q*y for x,y in zip(a,d)]
checks=0;switches=0;maxratio=0.
for case in range(50000):
 n=random.choice([2,3,5,10,30]);a=[random.expovariate(1)for _ in range(n)]
 total=sum(a);a=[x/total for x in a];i=random.randrange(n)
 b=[random.expovariate(1)*random.choice([.01,.2,1,4])/n for _ in range(n)]
 if random.random()<.7:b[i]+=max(0,1-sum(b))+random.random()
 if sum(b)<1:
  total=sum(b);b=[x/total for x in b]
 rho=sum(min(x,1)for x in b);d=min(b[i],1);v=rho-d;q=.5*math.exp(1-rho);V=q*d
 old=phi(a,b);bb=b[:];bb[i]*=random.choice([0,random.random()]);new=phi(a,bb)
 I=sum(max(0,new[j]-old[j])for j in range(n)if j!=i);D=old[i]-new[i]
 rhs=v*((K-1)*V+D)
 if D< -1e-12 or I>rhs+2e-12:raise RuntimeError(('retention',I,rhs,D,a,b,i,bb))
 if rhs>1e-15:maxratio=max(maxratio,I/rhs)
 checks+=1;switches+=sum(bb)<1

L=8.;eps=math.exp(-L);T=1/L;k=8;rho=1+math.log(T/(2*eps));q=eps/T;t=2*math.e*eps
caps=[1.]*int(rho)
if rho-int(rho)>1e-14:caps.append(rho-int(rho))
num_local=len(caps);m=max(2,math.ceil((1-q)*T/(k*eps)))
core_start=num_local;tiny_start=core_start+k*m;G=tiny_start+6;A=G+1;n=A+1
h=[[0.]*n for _ in range(k+2)];local=[[0.]*n for _ in range(k+2)];p=[0.]*n
for j in range(k):
 for i,d in enumerate(caps):local[j][i]=d*T/k
 for r in range(m):h[j][core_start+j*m+r]=T/(k*m)
for r in range(6):h[k][tiny_start+r]=t/6
local[k][G]=local[k][A]=t;h[k+1][0]=1-T-t
Zcore=T+eps*(rho-1);p[G]=1;p[A]=1-Zcore-t

def state(ll):
 z=[0.]*n
 for hh,lr in zip(h,ll):
  vals=phi(hh,lr)
  for i,x in enumerate(vals):z[i]+=x
 aa=[sum(row[i]for row in h)for i in range(n)]
 opp=[p[i]+z[i]for i in range(n)]
 return phi(aa,opp),z,sum(min(x,1)for x in opp)
full,z,S=state(local)
ll=[row[:]for row in local]
for j in range(k):ll[j][0]=0
changed,_,S1=state(ll);gain1=changed[0]-full[0]
ll=[row[:]for row in local];ll[k][A]=0;changed,_,SA=state(ll);gainA=changed[A]-full[A]
Delta=eps*(K*rho-(2*math.e-1));bA=1-Zcore-t+eps
expected1=c*((1-T-t)*(-math.expm1(-Delta))-eps)
expectedA=c*(math.expm1(math.e*eps)*bA-math.exp(math.e*eps)*eps)
if max(z)>eps+1e-12 or abs(S-2)>1e-12 or abs(sum(full)-C)>1e-12 or abs(S1-(2+Delta))>1e-12 or abs(SA-(2-math.e*eps))>1e-12 or abs(gain1-expected1)>1e-12 or abs(gainA-expectedA)>1e-12:
 raise RuntimeError(('explicit lower',S,S1,SA,max(z),gain1,expected1,gainA,expectedA))
sequence=[]
for L in [12,20,50,100,200,500]:
 ep=math.exp(-L);tt=1/L;rr=L-math.log(L)+1-math.log(2);tiny=2*math.e*ep
 dc=ep*(K*(L-math.log(L)-math.log(2))-math.e)
 b=1-tt-ep*(rr-1)-tiny+ep
 scaled1=c*((1-tt-tiny)*(-math.expm1(-dc))/ep-1)
 scaledA=c*(math.expm1(math.e*ep)*b/ep-math.exp(math.e*ep))
 residual=scaled1+scaledA-c*K*(L-math.log(L))
 sequence.append({'L':L,'scaled_residual':residual})
out={'status':'PASS','scope':'Floating corroboration only','retention_checks':checks,'pool_switches':switches,'max_incoming_to_retention_bound':maxratio,'explicit_fixed_owner_lower':{'owners':n,'productive_branches':k+1,'epsilon':eps,'max_local_payment':max(z),'full_S':S,'raw_budget':sum(full),'core_gain':gain1,'grid_gain':gainA,'envelope_budget_lower':C+gain1+gainA},'asymptotic_residual_sequence':sequence,'predicted_residual_limit':-c*(math.e+1+K*math.log(2))}
Path(__file__).with_name('retention_and_grid_lower_diagnostic.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
