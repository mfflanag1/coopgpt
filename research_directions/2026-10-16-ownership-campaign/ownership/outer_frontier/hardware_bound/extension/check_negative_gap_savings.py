"""Floating falsification diagnostics only; the analytical proof is load-bearing."""
import math,random,json
K=math.e-1;C=1+1/(2*math.e)
def phi(a,b):
 A=sum(a);B=sum(b);T=min(A,B)
 if T==0:return [0.0]*len(a)
 s,l=(a,b) if A<=B else (b,a)
 d=[min(x,T) for x in l];q=.5*math.exp(1-sum(d)/T)
 return [(1-q)*x+q*y for x,y in zip(s,d)]
def require(ok,message):
 if not ok:raise RuntimeError(message)
def local(h,l):
 z=[0.0]*len(h);M=0.0
 for j in range(len(h[0])):
  hh=[r[j] for r in h];ll=[r[j] for r in l];zz=phi(hh,ll)
  M+=min(sum(hh),sum(ll));z=[x+y for x,y in zip(z,zz)]
 return z,M
rng=random.Random(162116)
checks=0;max_excess=-float('inf');minimum_checks=0
for it in range(40000):
 n=2+it%7;m=1+(it//7)%4
 val=lambda: 0.0 if rng.random()<.35 else 10**rng.uniform(-2,2)
 h=[[val() for j in range(m)] for i in range(n)]
 l=[[val() for j in range(m)] for i in range(n)]
 p=[val() for i in range(n)]
 a=[sum(r) for r in h];H=sum(a)
 if not H:continue
 z,M=local(h,l)
 if sum(p)+M<H:continue
 z=[x/H for x in z];a=[x/H for x in a];p=[x/H for x in p];M/=H
 h=[[x/H for x in row] for row in h];l=[[x/H for x in row] for row in l]
 d=[min(1,p[i]+z[i]) for i in range(n)];S=sum(d);delta=C*M-sum(z);q0=.5*math.exp(1-S)
 require(delta>=-1e-12,'full budget')
 for i in range(n):
  g=a[i]-d[i]
  if g<0:continue
  r=math.sqrt(max(0,1-K*K*z[i]*g));L=2*math.exp(r-1)/(1+r)
  bound=a[i]-q0*math.exp(-delta)*g*L
  hh=[row.copy() for row in h];ll=[row.copy() for row in l];pp=p.copy()
  hh[i]=[x*rng.choice((0,1,rng.random())) for x in hh[i]]
  ll[i]=[x*rng.choice((0,1,rng.random())) for x in ll[i]]
  pp[i]*=rng.choice((0,1,rng.random()))
  zz,_=local(hh,ll);aa=[sum(row) for row in hh]
  payment=phi(aa,[x+y for x,y in zip(pp,zz)])[i]
  checks+=1;max_excess=max(max_excess,payment-bound)
  require(payment<=bound+1e-11,'actual negative-gap bound failed')
for it in range(5000):
 z=rng.random();g=(1-z)*rng.random();r=math.sqrt(1-K*K*z*g)
 formula=g*2*math.exp(r-1)/(1+r)
 root=(1-r)/(K*math.sqrt(z)) if z else 0
 D=root*root
 require(0<=D<=z+1e-12,'minimizer range')
 actual=(g+D)*math.exp(-K*math.sqrt(z*D))
 require(abs(actual-formula)<1e-12,'minimum formula')
 for j in range(101):
  dd=z*j/100
  require((g+dd)*math.exp(-K*math.sqrt(z*dd))>=formula-1e-12,'minimum inequality')
  minimum_checks+=1
print(json.dumps({'status':'PASS','scope':'Floating finite falsification only; no universal numerical proof.','actual_negative_gap_transitions':checks,'scalar_grid_checks':minimum_checks,'maximum_payment_minus_bound':max_excess,'uniform_savings_fraction':2*math.exp(math.sqrt(1-K*K/4)-1)/(1+math.sqrt(1-K*K/4))},sort_keys=True,indent=2))
