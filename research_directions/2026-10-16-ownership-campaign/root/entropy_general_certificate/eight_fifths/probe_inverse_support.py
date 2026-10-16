"""Floating pointwise diagnostic only; no funding conclusion."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,json,time
import numpy as np
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('candidate',BASE/'build_certificate.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

def inverse_rows(lo,hi,dl,dh):
 aa,bb=b.base_rows(lo,hi,dl,dh)
 q=b.old.en(lo-1,24)/2;bc=b.beta_hi*b.CB
 for s in b.CAP_SS:
  const=1-b.cl+dh/s;coef=(b.thi[s]-b.cl)/s-1
  aa.append([-q*bc*coef,-F(3,4)*q,-2*q,F(3,4)*q,F(1)])
  bb.append(2*q*(hi-1)+q*bc*const)
 return aa,bb

if __name__=='__main__':
 start=time.monotonic();best=(-1,None);count=0
 for S in np.linspace(1.7,2.,31):
  if S==2:S-=1e-9
  ss=F(str(S))
  for d in np.linspace(0.,float(b.cu),25):
   dd=F(str(d));aa,bb=inverse_rows(ss,ss,dd,dd)
   af=np.array(aa,dtype=float);bf=np.array(bb,dtype=float)
   for v in np.linspace(0,.4,25):
    save=.5*np.exp(1-S-d)
    obj=np.array([0,0,-save,save*(4/15)*float(b.KU)**2*v*v,1.])
    lp=linprog(-obj,A_ub=af,b_ub=bf,bounds=[(0,None),(0,None),(v,v),(0,None),(0,None)],method='highs')
    count+=1
    if lp.success and 1-lp.fun>best[0]:best=(1-lp.fun,{'S':S,'delta':d,'v':v,'x':list(lp.x)})
  if count%3000==0:print(json.dumps({'count':count,'max':best,'elapsed':time.monotonic()-start}),flush=True)
 out={'scope':'floating pointwise LP diagnostic, not a certificate','count':count,'max':best,'elapsed':time.monotonic()-start}
 (BASE/'inverse_support_probe.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
