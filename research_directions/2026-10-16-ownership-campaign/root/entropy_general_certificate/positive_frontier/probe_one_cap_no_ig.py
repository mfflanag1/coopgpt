"""Floating exploratory LP only. NOT a universal certificate or actual profile."""
import math,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import linprog, minimize_scalar, brentq
c=1/(2*math.e);C=1+c;K=math.e-1;alpha=1-c;Pi=11/8
us=np.linspace(.35,.95,31);lams=np.linspace(1,4.5,29)
def profile(M,delta,S):
 Z=C*M-delta;err=K*math.sqrt(c*M*delta);Q=c if delta<=0 else (.5 if delta/M>=c-1e-14 else brentq(lambda q:c+q*math.log(2*q)-delta/M,c,.5));B=min(2-M+err,1+alpha-M+M*Q);r=S-1;q0=.5*math.exp(-r);bn=.8*q0*math.exp(-delta)
 aa=[[1,0,0],[1,0,0],[1,1,0],[1,-1,0],[alpha,-c,0]]
 bb=[1-Z+M,1.5-Z,1,4*(1-M)/3,2*(1-M)+err]
 for t in np.linspace(0,.98,12):
  aa +=[[1-t,0,0],[1-t,0,0]]
  bb +=[1+.5*math.exp(-t)-Z,1-t+M*(1+.5*t*math.exp(-1/t) if t>0 else 1)-Z]
 for tau in np.linspace(c,.5,16):
  slope=1+math.log(2*tau);coef=slope+c-tau
  aa.append([coef,c-tau,0]);bb.append(delta+(.5+coef)*(1-M))
 aa.append([.5+c,c-.5,0]);bb.append(4*delta+(65/64)*(1-M))
 for eta in [2,8,32,128]:
  aa.append([.5+c,c-.5,0]);bb.append(eta*delta+(1+1/(16*eta))*(1-M))
 for u in us:
  q=.5*math.exp(1-1/u);A=1-q*(1+1/u);eta=q/S;lam=A+eta;mu=K*K*eta*eta/(4*A);p=K*eta
  aa +=[[-lam,p,1],[-lam,mu,1]]
  bb +=[lam*r+p*Z,lam*r+mu*Z+A*max(0,Pi+Z-S)]
  if S<2 and mu<p:
   penalty=B*(p-mu)*(1-lam)/(1-lam+alpha*p)
   aa.append([-lam,mu,1]);bb.append(lam*r+mu*Z+penalty)
 # mu from dense+local scalar search; finite numeric approximation only.
 for lam in []:
  def f(z): return max(0,min(1,(B-z)/alpha)*(math.exp(K*z)-lam)/z) if z>0 else 0
  zz=np.linspace(max(1e-9,M/1000),M,100)
  vals=[f(z) for z in zz];k=int(np.argmax(vals))
  opt=minimize_scalar(lambda z:-f(z),bounds=(zz[max(0,k-1)],zz[min(99,k+1)]),method='bounded')
  mu=max(max(vals),-opt.fun)
  aa.append([-q0*lam,q0*mu,1]);bb.append(q0*(lam*r+mu*Z))
 bn=q0*math.exp(-delta);worst=(-1,None)
 for vl,vh in zip(np.linspace(0,1,21)[:-1],np.linspace(0,1,21)[1:]):
  out=linprog([bn,-bn*(4*K*K/15)*vh*vh,-1],A_ub=aa,b_ub=bb,bounds=[(vl,vh),(0,Z),(0,None)],method='highs')
  if out.success and 1-out.fun>worst[0]:worst=(1-out.fun,list(out.x))
 return (None,None) if worst[1] is None else worst

start=time.monotonic();best=(-1,None);count=0
for M in np.linspace(.1,1,10):
 for frac in np.linspace(0,1,8):
  delta=c*M*frac;Z=C*M-delta
  for S in np.linspace(1,Pi+Z,24):
   val,x=profile(M,delta,S);count+=1
   if val is not None and val>best[0]:best=(val,dict(M=M,delta=delta,S=S,Z=Z,x=x))
 result=dict(status='FLOATING_DIAGNOSTIC_ONLY',count=count,best=best,elapsed=time.monotonic()-start)
 Path(__file__).with_name('one_cap_no_ig_probe.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
