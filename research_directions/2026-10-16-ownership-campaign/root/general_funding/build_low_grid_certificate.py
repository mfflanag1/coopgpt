"""Numerical dual search followed by exact rational certificate verification.
The separate verifier imports no optimizer. A solver only proposes nonnegative weights.
"""
from fractions import Fraction as F
from math import factorial,ceil
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog
CB=F(148,125);KB=F(7,4);K2B=F(3);cB=F(23,125)

def exp_neg(x,n):
 return sum(((-x)**k/F(factorial(k)) for k in range(n+1)),F(0))
def data(lo,hi,u):
 x=1/u-1;ql=exp_neg(x,25)/2;qh=exp_neg(x,24)/2
 ah=1-ql*(1+1/u);al=1-qh*(1+1/u)
 require(al>0 and ql>0,'positive coefficients')
 lam=1-ql*(1+1/u-1/lo);eta=qh/lo
 mu=K2B*eta*eta/(4*al);p=KB*eta
 bn=F(2,5)*exp_neg(hi-1+cB,25)
 theta=lam-bn
 aa=[[1,-1,0,0,0],[-CB,1,0,0,0],[0,-1,0,0,0],[-1,1,1,0,0],[0,1,1,0,0],[0,0,1,1,0],[F(4,3),0,1,-1,0],[0,-1,0,1,0],[0,-p,0,p,1],[0,-mu-ah,0,mu,1],[1,0,0,0,0]]
 bb=[0,0,1-lo,1,F(3,2),1,F(4,3),0,0,ah*(1-lo),1]
 obj=[0,0,theta,0,1]
 caps=[1,CB,1,CB,p*CB]
 return [[F(v) for v in row] for row in aa],list(map(F,bb)),list(map(F,obj)),list(map(F,caps)),1+lam*(hi-1)
def require(cond,label):
 if not cond:raise RuntimeError(label)
def certify(lo,hi,u,y):
 aa,bb,obj,caps,constant=data(lo,hi,u)
 require(len(y)==len(bb) and all(v>=0 for v in y),'dual weights')
 residual=[max(F(0),obj[j]-sum(y[i]*aa[i][j] for i in range(len(y)))) for j in range(5)]
 upper=constant+sum(y[i]*bb[i] for i in range(len(y)))+sum(residual[j]*caps[j] for j in range(5))
 return upper,residual

def main():
 intervals=[];N=128
 for k in range(N):
  lo=1+CB*k/N;hi=1+CB*(k+1)/N
  best=None
  for un in range(35,96,2):
   u=F(un,100);aa,bb,obj,caps,constant=data(lo,hi,u)
   result=linprog(-np.array(obj,dtype=float),A_ub=np.array(aa,dtype=float),b_ub=np.array(bb,dtype=float),bounds=[(0,None)]*5,method='highs')
   require(result.success,'LP proposal')
   y=[F(max(0,round(float(v)*10**12)),10**12) for v in -result.ineqlin.marginals]
   upper,residual=certify(lo,hi,u,y)
   if best is None or upper<best[0]:best=(upper,u,y,residual)
  upper,u,y,residual=best
  require(upper<F(8,5),f'target failed interval{k} upper{float(upper)}')
  intervals.append({'lo':str(lo),'hi':str(hi),'u':str(u),'dual':[str(v) for v in y],'residual':[str(v) for v in residual],'upper':str(upper)})
 out={'status':'PASS','theorem_target':'8/5','scope':'H=F=1,P<=1; exact interval LP weak-duality certificates, not report sampling','interval_count':N,'max_upper':str(max(F(r['upper']) for r in intervals)),'max_upper_decimal_display':max(float(F(r['upper'])) for r in intervals),'intervals':intervals}
 Path(__file__).with_name('low_grid_certificate.json').write_text(json.dumps(out,indent=2))
 print(json.dumps({k:v for k,v in out.items() if k!='intervals'},indent=2))
if __name__=='__main__':main()
