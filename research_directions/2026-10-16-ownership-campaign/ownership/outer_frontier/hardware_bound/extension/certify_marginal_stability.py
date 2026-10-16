"""Exact rational certificate for the marginal-floor stability scalar lemma."""
from fractions import Fraction as F
from pathlib import Path
import json

def exp_lo_minus(x):
 t=s=F(1)
 for j in range(1,14):t*=-x/j;s+=t
 return s

def exp_hi_minus(x):
 t=s=F(1)
 for j in range(1,13):t*=-x/j;s+=t
 return s

def require(x,msg):
 if not x:raise RuntimeError(msg)

def run():
 elo=F(1957,720);ehi=F(11743,4320);clo=1/(2*ehi)
 A2=F(16,25)
 # (e-1)^2/(2e) is increasing for e>1.
 short_constant=(ehi-1)**2/(2*ehi)
 require(short_constant<A2,'short-stage constant')
 # Long deficit decreases for all u>=0 because q<=1/2<1-c.
 F_at_three_quarters=(1-clo)/4-exp_lo_minus(F(3,4))/2
 require(F_at_three_quarters<0,'long tail sign')
 worst=F(0);worst_box=None;active=0
 N=512
 for j in range(N):
  lo=F(3*j,4*N);hi=F(3*(j+1),4*N)
  # F(u)=(1-c)(1-u)-exp(-u)/2 is decreasing.
  Fhi=(1-clo)*(1-lo)-exp_lo_minus(lo)/2
  if Fhi<=0:continue
  # delta(u)=c-u exp(-u)/2 decreases on [0,1].
  delta_lo=clo-hi*exp_hi_minus(hi)/2
  require(delta_lo>0,'interval delta positivity')
  require(Fhi*Fhi<=A2*delta_lo,'marginal stability interval')
  ratio=Fhi*Fhi/delta_lo;active+=1
  if ratio>worst:worst=ratio;worst_box=[str(lo),str(hi)]
 out={'status':'PASS','scope':'Exact all-real one-variable certificate, not an empirical grid test.','constant_squared':str(A2),'short_constant_upper':str(short_constant),'short_constant_check':True,'long_tail_check':True,'boxes':N,'active_boxes':active,'worst_ratio':str(worst),'worst_ratio_float':float(worst),'worst_box':worst_box}
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':run()
