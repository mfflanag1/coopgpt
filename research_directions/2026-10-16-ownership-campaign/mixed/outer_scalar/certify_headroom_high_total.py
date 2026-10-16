"""Exact one-dimensional certificate for the cap-safe high-total chord bound.
All arithmetic and branch decisions use Fraction. No optimizer or floating proof.
"""
from fractions import Fraction as F
from pathlib import Path
import json
TARGET=F(14017,10000)

def series(x,n):
 term=F(1);value=term
 for j in range(1,n+1):
  term*=x/j;value+=term
 return value,term

def exp_upper(x):
 if x<0:return series(x,16)[0]
 value,term=series(x,16)
 return value+term*x/17/(1-x/18)

def exp_lower(x):
 return series(x,17 if x<0 else 16)[0]

EL=exp_lower(F(1));EU=exp_upper(F(1))
CL=1/(2*EU);CU=1/(2*EL);A0=exp_upper(F(1,2))

def line_max(slope,intercept,lo,hi):
 if lo>hi:raise ValueError('inverted interval')
 stationary=1-intercept/slope
 point=max(lo,min(hi,stationary))
 return exp_upper(-point)*(slope*point+intercept),point

def interval_upper(lo,hi):
 blo=F(1,2)-hi;bhi=F(1,2)-lo
 if blo<=0:raise ValueError('nonpositive b')
 B_lo=F(4,5)*exp_lower(lo-CU)
 B_hi=F(4,5)*exp_upper(hi-CL)
 p1=bhi*(A0-B_lo)
 alpha=(A0+B_hi*blo)/(1+blo)
 beta=(A0-B_lo)*(1+hi)/(1+blo)
 if not (A0>alpha>0 and p1>=0 and beta>=0):raise RuntimeError('line signs')
 crossing=(beta-p1)/(A0-alpha)
 a=F(1,2);b=F(1)
 if crossing<=a:
  upper,point=line_max(alpha,beta,a,b)
 elif crossing>=b:
  upper,point=line_max(A0,p1,a,b)
 else:
  left,lp=line_max(A0,p1,a,crossing)
  right,rp=line_max(alpha,beta,crossing,b)
  upper,point=(left,lp) if left>=right else (right,rp)
 return 1+upper/2,point

def main():
 if not TARGET<(1+1/(2*EU))**2:raise RuntimeError('target not below C squared')
 stack=[(F(0),CU)];count=0;leaves=[];worst=F(0);worst_interval=None
 while stack:
  lo,hi=stack.pop();count+=1
  bound,point=interval_upper(lo,hi)
  if bound<=TARGET:
   leaves.append((lo,hi))
   if bound>worst:worst=bound;worst_interval=(lo,hi,point)
  else:
   if hi-lo<F(1,1<<20):raise RuntimeError('unresolved interval')
   midpoint=(lo+hi)/2;stack.extend(((lo,midpoint),(midpoint,hi)))
 leaves.sort()
 if not leaves or leaves[0][0]!=0 or leaves[-1][1]!=CU:
  raise RuntimeError('coverage endpoints')
 if any(leaves[j][1]!=leaves[j+1][0] for j in range(len(leaves)-1)):
  raise RuntimeError('coverage gaps')
 scale=10**12
 rounded_worst=F((worst.numerator*scale+worst.denominator-1)//worst.denominator,scale)
 if rounded_worst>TARGET:raise RuntimeError('display upper exceeded target')
 r=worst_interval[2]
 rlo=F(r.numerator*scale//r.denominator,scale);rhi=rlo+F(1,scale)
 out={'status':'PASS','target':str(TARGET),'target_below_C_squared':True,'evaluated_intervals':count,'accepted_intervals':len(leaves),'epsilon_upper':str(CU),'worst_upper_rounded_up':str(rounded_worst),'worst_upper_float':float(worst),'worst_epsilon_interval':[str(x) for x in worst_interval[:2]],'worst_r_interval':[str(rlo),str(rhi)],'scope':'High-S chord relaxation for M=H and uniform no-variable-cap/headroom condition. All r>=1/2 reduced analytically to[1/2,1].'}
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
