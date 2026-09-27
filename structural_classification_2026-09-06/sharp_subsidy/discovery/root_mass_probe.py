import two_hub_blocks as tb
import numpy as np,json
from scipy.optimize import linprog
from pathlib import Path
for same in (False,True):
 m,P=tb.example(same,0);types,stride,rows,rhs,eq,erhs,bounds,A,E=tb.model(m,P);L=tb.structure(m,P)[4];obj=np.zeros(len(bounds))
 for k,(b,t,s)in enumerate(types):obj[k*stride+b]=L[b][t]
 r=linprog(obj,A_ub=A,b_ub=rhs,A_eq=E,b_eq=erhs,bounds=bounds)
 print(same,r.status,r.fun,flush=True)
 if r.success:Path(__file__).with_name('ROOT_MASS_MIN_'+str(same)+'.json').write_text(json.dumps({'same':same,'m':m,'P':P,'types':types,'stride':stride,'values':r.x.tolist(),'minimum':r.fun,'dual_ub':r.ineqlin.marginals.tolist(),'dual_eq':r.eqlin.marginals.tolist(),'dual_lower':r.lower.marginals.tolist(),'dual_upper':r.upper.marginals.tolist()})+'\n')
