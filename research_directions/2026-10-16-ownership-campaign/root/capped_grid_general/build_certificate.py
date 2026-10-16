"""Propose rational duals and verify them exactly for capped-grid13/8 theorem."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog
PB=F(51,40);CB=F(148,125);cB=F(23,125)
EL=sum((F(1,factorial(k)) for k in range(9)),F(0));EU=EL+F(1,factorial(9))*F(10,9)
CMIN=1+1/(2*EU);CMAX=1+1/(2*EL);KB=EU-1;K2B=KB*KB

def require(b,s):
 if not b:raise RuntimeError(s)
def expn(x,n):
 out=term=F(1)
 for k in range(1,n+1):term*=(-x)/k;out+=term
 return out
def data(lo,hi,dl,dh,u):
 ql=expn(1/u-1,25)/2;qh=expn(1/u-1,24)/2
 ah=1-ql*(1+1/u);al=1-qh*(1+1/u)
 require(al>0 and ql>0,'positivecoeff')
 lam=1-ql*(1+1/u-1/lo);eta=qh/lo;mu=K2B*eta*eta/(4*al);p=KB*eta
 bn=F(2,5)*expn(hi-1+dh,25);theta=lam-bn
 aa=[[1,-1,0,0,0],[-CMAX,1,0,0,0],[0,-1,0,0,0],[-1,1,1,0,0],[0,1,1,0,0],[0,0,1,1,0],[F(4,3),0,1,-1,0],[0,-1,0,1,0],[0,-p,0,p,1],[0,-mu-ah,0,mu,1],[1,0,0,0,0],[CMIN,-1,0,0,0],[-CMAX,1,0,0,0]]
 bb=[0,0,PB-lo,1,F(3,2),1,F(4,3),0,0,ah*(PB-lo),1,dh,-dl]
 obj=[0,0,theta,0,1];caps=[1,CB,1,CB,p*CB]
 return [[F(v) for v in row] for row in aa],list(map(F,bb)),list(map(F,obj)),list(map(F,caps)),1+lam*(hi-1)
def verify(lo,hi,dl,dh,u,y):
 aa,bb,obj,caps,const=data(lo,hi,dl,dh,u)
 require(len(y)==13 and all(v>=0 for v in y),'nonnegativeweights')
 residual=[max(F(0),obj[j]-sum(y[k]*aa[k][j] for k in range(13))) for j in range(5)]
 bound=const+sum(y[k]*bb[k] for k in range(13))+sum(residual[j]*caps[j] for j in range(5))
 return bound,residual

def main():
 out=[];NS=128;ND=8
 for k in range(NS):
  lo=1+(PB+CB-1)*k/NS;hi=1+(PB+CB-1)*(k+1)/NS
  for d in range(ND):
   dl=cB*d/ND;dh=cB*(d+1)/ND
   record={'s_lo':str(lo),'s_hi':str(hi),'d_lo':str(dl),'d_hi':str(dh)}
   if lo>PB+CMAX-dl:
    record['empty_reason']='S_lo > PB+CMAX-delta_lo';out.append(record);continue
   best=None
   for un in range(45,86,2):
    u=F(un,100);aa,bb,obj,caps,const=data(lo,hi,dl,dh,u)
    result=linprog(-np.array(obj,dtype=float),A_ub=np.array(aa,dtype=float),b_ub=np.array(bb,dtype=float),bounds=[(0,None)]*5,method='highs')
    require(result.success,'LPproposal')
    y=[F(max(0,round(float(v)*10**12)),10**12) for v in -result.ineqlin.marginals]
    bound,res=verify(lo,hi,dl,dh,u,y)
    if best is None or bound<best[0]:best=(bound,u,y,res)
   bound,u,y,res=best
   require(bound<F(13,8),f'targetfailedk{k},d{d},bound{float(bound)}')
   record.update({'u':str(u),'weights':[str(v) for v in y],'residual':[str(v) for v in res],'upper':str(bound)})
   out.append(record)
 result={'status':'PASS','target':'13/8','PB':str(PB),'S_intervals':NS,'delta_intervals':ND,'rectangles':len(out),'nonempty':sum('upper' in r for r in out),'max_upper':str(max(F(r['upper']) for r in out if 'upper'in r)),'cells':out}
 Path(__file__).with_name('certificate.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({**{k:v for k,v in result.items() if k!='cells'},'max_upper_display':float(F(result['max_upper']))},indent=2))
if __name__=='__main__':main()
