from pathlib import Path
from fractions import Fraction as F
import importlib.util,json
import numpy as np
from scipy.optimize import linprog
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('p',B/'probe_inverse_support.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p);b=p.b
S=F(47,25);d=F('0.007664163648141897');v=F(1,30)
result=[]
for mode in ['original','fine_u','fine_both']:
 if mode!='original':
  b.CAP_US=[F(i,100) for i in range(20,99)]
  b.qdata={u:(b.old.en(1/u-1,25)/2,b.old.en(1/u-1,24)/2) for u in b.CAP_US}
 if mode=='fine_both':
  b.CAP_SS=[F(i,64) for i in range(1,65)]
  b.thi={s:b.old.en(1-s,24)/2 for s in b.CAP_SS}
 aa,bb=p.inverse_rows(S,S,d,d);save=.5*np.exp(float(1-S-d))
 obj=np.array([0,0,-save,save*4/15*float(b.KU)**2*float(v)**2,1])
 lp=linprog(-obj,A_ub=np.array(aa,dtype=float),b_ub=np.array(bb,dtype=float),bounds=[(0,None),(0,None),(float(v),float(v)),(0,None),(0,None)],method='highs')
 result.append({'mode':mode,'value':1-lp.fun,'x':list(lp.x),'duals':[(i,float(-w))for i,w in enumerate(lp.ineqlin.marginals)if w< -1e-10]})
print(json.dumps(result,indent=2));(B/'point_refinement.json').write_text(json.dumps(result,indent=2))
