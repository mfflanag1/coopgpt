"""Bounded diagnostic: normalized-mass continuous RHS versus unit/deletion endpoints.
Numerical discovery only. Separate from the parent's H(A) search.
"""
import json,itertools,time
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import csc_matrix

def solve(A,i,endpoint=False,limit=2):
    r,n=A.shape; G=A@A.T; dim=2*r+1; off=A[:,i]==0
    rows=[];lo=[];hi=[]
    def add(x,l=-np.inf,h=np.inf):rows.append(x);lo.append(l);hi.append(h)
    x=np.zeros(dim);x[:r]=1;add(x,1,1)
    for k in range(r):
        x=np.zeros(dim);x[:r]=G[k];x[r]=-1;x[r+1+k]=n;add(x,h=n)
        if off[k]:
            x=np.zeros(dim);x[:r]=G[k];x[r]=-1;add(x,l=0)
        elif endpoint:
            x=np.zeros(dim);x[:r]=G[k];x[r]=-1;x[r+1+k]=-n;add(x,l=-n)
        x=np.zeros(dim);x[k]=1;x[r+1+k]=-1;add(x,h=0)
    c=np.zeros(dim);c[:r]=-A[:,i]
    lb=np.zeros(dim);ub=np.ones(dim);lb[r]=1/n;ub[r]=n
    sol=milp(c,integrality=np.r_[np.zeros(r+1),np.ones(r)],bounds=Bounds(lb,ub),constraints=LinearConstraint(csc_matrix(np.array(rows)),lo,hi),options={'time_limit':limit,'mip_rel_gap':1e-9,'presolve':False})
    if sol.x is None:return {'status':int(sol.status)}
    lam=sol.x[:r];q=A.T@lam
    return {'status':int(sol.status),'gap':float(sol.mip_gap),'theta':float(q[i]),'t':float(sol.x[r]),'mu':lam.tolist(),'v':q.tolist()}

if __name__=='__main__':
 rng=np.random.default_rng(101021);started=time.monotonic();best=0
 for trial in range(160):
    n=int(rng.integers(4,9));r=int(rng.integers(n,2*n+2));A=rng.binomial(1,rng.uniform(.25,.75),size=(r,n)).astype(float);A=A[A.sum(axis=1)>0];A=np.unique(A,axis=0)
    i=int(rng.integers(n));a=solve(A,i);b=solve(A,i,True)
    if 'theta' not in a or 'theta' not in b:continue
    diff=a['theta']-b['theta'];best=max(best,diff)
    if diff>1e-7 and a['status']==0 and b['status']==0:
        print(json.dumps({'finding':'normalized_endpoint_failure','trial':trial,'A':A.tolist(),'i':i,'continuous':a,'endpoint':b,'difference':diff}),flush=True);break
    if trial%20==0:print(json.dumps({'trial':trial,'max_difference':best,'elapsed_seconds':time.monotonic()-started}),flush=True)
 else:print(json.dumps({'finding':'no_counter_in_bounded_diagnostic','trials':160,'max_difference':best,'elapsed_seconds':time.monotonic()-started}),flush=True)
