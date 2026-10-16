"""Falsification-only finite support approximation; not a proof certificate."""
from math import e, exp
import numpy as np
from scipy.optimize import linprog, differential_evolution
c=1/(2*e);C=1+c

def k(t):
    return 1 if t<=0 else (1-.5*exp(1-1/t) if t<=1 else .5*exp(1-t))
r=np.unique(np.r_[np.linspace(1,5,161),np.linspace(5.1,20,60),[30,50,100,200,1000]])
q=.5*np.exp(1-r)
# Columns: all hardware short, all power short, unused hardware.
m=np.r_[np.ones_like(r),1/r,0]
z=np.r_[1+q*(r-1),(1+q*(r-1))/r,0]
l=np.r_[q*r,(1-q)/r,0]
AE=np.array([z,np.ones_like(z)])

def max_role(A,beta):
    fit=linprog(-(A*l-C*c*m),A_eq=AE,b_eq=[beta,1],bounds=(0,None),method='highs')
    if not fit.success:raise ValueError(fit.message)
    return -fit.fun, [(int(i),float(v)) for i,v in enumerate(fit.x) if v>1e-8]
def gap(beta,u, detail=False):
    A=k(u)-k(beta)
    support,cols=max_role(A,beta)
    G=1+k(beta)*(beta-1)-beta-k(u)*(beta-u)/3+support
    if detail:
        return G,dict(beta=beta,u=u,A=A,support=support,columns=[dict(index=i,weight=v,local_rho=(float(r[i]) if i<len(r) else float(r[i-len(r)]) if i<2*len(r) else None),orientation=('hardware_short' if i<len(r) else 'power_short' if i<2*len(r) else 'unused')) for i,v in cols])
    return G
if __name__=='__main__':
    for b,u in[(2/3,3/8),(.808,.2505),(.5919698603,.3908926331),(.6,.5),(.55,.4),(.5,.5)]:
        print(gap(b,u,True),flush=True)
    res=differential_evolution(lambda x:-gap(x[0],x[0]*x[1]),[(.5,C-1e-8),(0,1)],popsize=8,maxiter=60,tol=1e-8,seed=3)
    print('maximum approximation',gap(res.x[0],res.x[0]*res.x[1],True),flush=True)
