"""Exact adaptive rational certificate, with floating scheduling only.
All accepted and discarded boxes use rational inequalities. No scipy required.
"""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import json,time
K=F(7,4);ETA=F(5,4);CU=F(23,125);TARGET=F(7,5)
SCALE=1<<24

def exp_lo_minus(y):
 term=F(1);out=term
 for j in range(1,14):
  term*= -y/j;out+=term
 return max(F(0),out)

def exp_hi_minus(y):
 term=F(1);out=term
 for j in range(1,13):
  term*= -y/j;out+=term
 return out

def sqrt_hi(q):
 n=q.numerator*SCALE*SCALE//q.denominator
 r=isqrt(n)
 if r*r*q.denominator<q.numerator*SCALE*SCALE:r+=1
 return F(r,SCALE)

def kup(t):
 if t<=0:return F(1)
 if t<=1:return 1-exp_lo_minus(1/t-1)/2
 return exp_hi_minus(t-1)/2

def bound(box):
 gl,gh,sl,sh,dl,dh=box
 gl=max(gl,dl,sl-1);dh=min(dh,gh);sh=min(sh,1+gh)
 if gl>gh or dl>dh or sl>sh:return None,box
 box=(gl,gh,sl,sh,dl,dh)
 x=gh-dl
 if x<=F(2,5):return 1+x,box
 w=1+ETA*(1-gl)
 kap=K*(sqrt_hi(K*K*dh*dh+4*dh*w)-K*dh)/2
 t=max(x,sl-dh-kap)
 neg=max(F(0),1+gl-sh)
 qlo=exp_lo_minus(sh+CU-1)/2
 return 1+x*kup(t)-qlo*neg,box

def run():
 e_lower=F(1957,720);e_upper=F(11743,4320)
 constant_checks={
  'K_le_7_4':e_upper<F(11,4),
  'eta_le_5_4':e_lower>F(8,3),
  'c_le_23_125':e_lower>F(125,46),
  'seven_fifths_lt_C_squared':TARGET<(1+1/(2*e_upper))**2,
 }
 if not all(constant_checks.values()):raise RuntimeError('failed exact constant check')
 start=time.monotonic();stack=[(F(0),F(1),F(1),F(2),F(0),F(1))]
 seen=0;passed=0;discarded=0;max_depth=0;worst=F(0);worst_box=None
 while stack:
  box=stack.pop();seen+=1
  ub,box=bound(box)
  if ub is None:discarded+=1;continue
  if ub<=TARGET:
   passed+=1
   if ub>worst:worst=ub;worst_box=box
   continue
  widths=[box[1]-box[0],box[3]-box[2],box[5]-box[4]]
  j=max(range(3),key=lambda i:widths[i]);idx=2*j
  if widths[j]<F(1,1<<18):raise RuntimeError(f'unresolved {box} upper {float(ub)}')
  mid=(box[idx]+box[idx+1])/2
  left=list(box);right=list(box);left[idx+1]=mid;right[idx]=mid
  stack.extend((tuple(left),tuple(right)))
  if seen%10000==0:print(json.dumps(dict(seen=seen,remaining=len(stack),elapsed=time.monotonic()-start)),flush=True)
 out=dict(status='PASS',target=str(TARGET),constants=dict(K=str(K),eta=str(ETA),c_upper=str(CU)),constant_checks=constant_checks,seen=seen,passed=passed,discarded=discarded,worst_upper=str(worst),worst_upper_float=float(worst),worst_box=[str(x) for x in worst_box],elapsed=time.monotonic()-start,scope='Full no-overflow, at most one positive outer-gap actual owner; both owner and branch counts unbounded. Exact scalar relaxation certificate, not an optimality claim.')
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
