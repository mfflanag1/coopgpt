import math,json
import numpy as np
from scipy.optimize import linprog
c=1/(2*math.e);C=1+c;K=math.e-1
# variables M,Z,v,Zm,t. All nonnegative.
def lp(S,u):
 q=.5*math.exp(1-1/u);eta=q/S;A=1-q*(1+1/u);lam=A+eta;mu=K*K*eta*eta/(4*A);b=.4*math.exp(1-S-c)
 aa=[[1,-1,0,0,0],[-C,1,0,0,0],[0,-1,0,0,0],[-1,1,1,0,0],[0,1,1,0,0],[0,0,1,1,0],[4/3,0,1,-1,0],[0,-1,0,1,0],[0,-K*eta,0,K*eta,1],[0,-mu-A,0,mu,1]]
 bb=[0,0,1-S,1,1.5,1,4/3,0,0,A*(1-S)]
 obj=[0,0,-(lam-b),0,-1]
 r=linprog(obj,A_ub=aa,b_ub=bb,bounds=[(0,1),(0,None),(0,None),(0,None),(0,None)],method='highs')
 if not r.success:return None
 return {'S':S,'u':u,'bound':1+lam*(S-1)-r.fun,'point':r.x.tolist(),'dual':(-r.ineqlin.marginals).tolist(),'dual_Mupper':float(-r.upper.marginals[0])}
if __name__=='__main__':
 records=[]
 for S in np.linspace(1,1+C,121):
  rr=[lp(float(S),float(u)) for u in np.linspace(.35,.95,31)]
  rr=[r for r in rr if r]
  records.append(min(rr,key=lambda x:x['bound']))
 out={'diagnostic_only':True,'max':max(records,key=lambda x:x['bound']),'records':records}
 from pathlib import Path
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out['max'],indent=2))
