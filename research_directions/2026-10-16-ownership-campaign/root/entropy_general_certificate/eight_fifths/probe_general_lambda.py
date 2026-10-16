"""Diagnostic only: baseline concentration scalar is numerically maximized."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,math
import numpy as np
from scipy.optimize import linprog,minimize_scalar
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('p',B/'probe_inverse_support.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p);b=p.b
S=F(47,25);d=F(1,125);v=F(1,30)
aa,bb=p.inverse_rows(S,S,d,d);aa=[list(map(float,r))for r in aa];bb=list(map(float,bb))
c=1/(2*math.e);alpha=1-c;K=math.e-1;C=1+c;q0=.5*math.exp(1-float(S));bestscalars=[]
for lam in np.linspace(1.05,3.5,50):
 def f(z):return min(1,(1-z)/alpha)*max(0,math.exp(K*z)-lam)/z
 zs=np.linspace(1e-8,1,1001);vs=[f(z) for z in zs];j=int(np.argmax(vs));opt=minimize_scalar(lambda z:-f(z),bounds=(zs[max(0,j-1)],zs[min(1000,j+1)]),method='bounded')
 mu=max(max(vs),-opt.fun);beta=max(0,math.exp(K)-lam)/alpha
 for ss in np.linspace(.02,1,50):
  t=.5*math.exp(ss-1);coef=(t-c)/ss-1;con=alpha+float(d)/ss
  aa.append([-q0*beta*C*coef,-q0*mu,-q0*lam,q0*mu,1]);bb.append(q0*lam*float(S-1)+q0*beta*C*con)
 bestscalars.append([lam,mu])
save=.5*math.exp(float(1-S-d));obj=np.array([0,0,-save,save*4/15*K*K*float(v)**2,1])
lp=linprog(-obj,A_ub=aa,b_ub=bb,bounds=[(0,None),(0,None),(float(v),float(v)),(0,None),(0,None)],method='highs')
out={'scope':'floating numerical scalar support diagnostic','S':str(S),'delta':str(d),'v':str(v),'value':1-lp.fun,'x':list(lp.x),'duals':[(i,float(-w))for i,w in enumerate(lp.ineqlin.marginals)if w< -1e-10],'scalars':bestscalars}
print(json.dumps(out,indent=2));(B/'general_lambda_point.json').write_text(json.dumps(out,indent=2))
