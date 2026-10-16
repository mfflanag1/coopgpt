import math,json,sys
import numpy as np
from scipy.optimize import differential_evolution
C=1+1/(2*math.e);c=C-1;K=math.e-1
MODE='low'
us=np.array([.75]);qq=.5*np.exp(1-1/us)

def calc(x,detail=False):
    M=x[0];Z=M*(1+c*x[1]);S=1+(Z if MODE=='low' else 4)*x[2]
    vmax=max(0,min(1,1+min(M,.5)-Z));v=vmax*x[3]
    lo=max(0,v-4/3*(1-M));hi=min(Z,1-v)
    if lo>hi:return 5
    zm=lo+(hi-lo)*x[4];zp=Z-zm;w=max(0,1+Z-S) if MODE=='low' else zp
    G=S-1+v;eta=qq/S;lam=1-qq*(1+1/us-1/S);A=lam-eta;mu=K*K*eta*eta/(4*A)
    q0=.5*math.exp(1-S);delta=C*M-Z
    vv=K*K*zm*v;r=math.sqrt(max(0,1-vv));L=2*math.exp(r-1)/(1+r)
    arr=1+lam*G+np.minimum(K*eta*zp,mu*zp+A*w)
    j=int(np.argmin(arr));value=float(arr[j]);pimin=max(1,S-Z);gridbound=1+.5*math.exp(1-pimin)*(pimin+.5*math.exp(-math.exp(-C*M)))
    if MODE!='low':value=min(value,gridbound)
    d={'M':M,'Z':Z,'S':S,'v':v,'zm':zm,'zp':zp,'w_upper':w,'u':float(us[j]),'bound':value,'grid_bound':gridbound,'PD_bound':float(arr[j])}
    return d if detail else -value
if __name__=='__main__':
    rr=differential_evolution(calc,[(0,1)]*5,popsize=25,maxiter=1800,tol=1e-10,seed=1601,workers=1,polish=True)
    out={'diagnostic_only':True,'case':'physical hardware, P<=H; aggregated constraints; grid800 dual minimization','result':calc(rr.x,True),'x':rr.x.tolist(),'success':bool(rr.success),'message':str(rr.message)}
    print(json.dumps(out,indent=2))
