import math,json
import numpy as np
from scipy.optimize import differential_evolution, minimize_scalar
C=1+1/(2*math.e)
def v(p,m):
 k=p+C*m; f=min(1,p+m)
 if k<=1 or p>=1 or f<=0: return -1
 q0=.5*math.exp(1-k);q1=.5*math.exp(1-1/p) if p>0 else 0
 return (1.5+p-q1*(p+.5)+q0*(C*m-1.5))/f
res=differential_evolution(lambda z:-v(*z),[(0,1),(0,1)],seed=7182,tol=1e-11,polish=True,maxiter=2000)
out={'label':'discovery numerical only, not a certified bound','intermediate':{'p':res.x[0],'m':res.x[1],'value':-res.fun},'C':C,'case_low_coarse':1.5*C}
r2=minimize_scalar(lambda p:-v(p,1),bounds=(0,1),method='bounded',options={'xatol':1e-14})
out['m1']={'p':r2.x,'value':-r2.fun}
print(json.dumps(out,indent=2))
