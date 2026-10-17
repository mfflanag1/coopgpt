# Bounded discovery only: transitive uniform bases for the veto-amplification test.
import numpy as np,json,time
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
out='/private/tmp/coopgpt-overnight-20261017/unrestricted/uniform_circulant_target_probe.jsonl'
cases=[]
for n,k in [(7,3),(9,4),(11,4),(11,5),(13,5),(13,6),(17,6),(17,8)]:
    cases.append((n,tuple(range(k)),'interval'))
    S={0};j=1
    while len(S)<k:
        S.add((j*j+j//n)%n);j+=1
    cases.append((n,tuple(sorted(S)),'quadratic_spaced'))
with open(out,'w') as f:
 for n,S,name in cases:
    k=len(S);A=np.array([[int((j-r)%n in S) for j in range(n)] for r in range(n)],float)
    rho=n/k**2;G=A@A.T;big=max(0,k*rho-1)
    C=[np.hstack([G,big*np.eye(n)]),np.hstack([np.eye(n),-rho*np.eye(n)]),np.r_[np.ones(n),np.zeros(n)][None,:]]
    lo=[np.full(n,-np.inf),np.full(n,-np.inf),np.array([-np.inf])]
    hi=[np.full(n,1+big),np.zeros(n),np.array([rho])]
    off=np.where(A[:,0]==0)[0]
    C.append(np.hstack([G[off],np.zeros((len(off),n))]));lo.append(np.ones(len(off)));hi.append(np.full(len(off),np.inf))
    threshold=np.sqrt(2)*k/n
    obj=np.r_[threshold*np.ones(n)-A[:,0],np.zeros(n)]
    sol=milp(obj,integrality=np.r_[np.zeros(n),np.ones(n)],bounds=Bounds(np.zeros(2*n),np.r_[np.full(n,rho),np.ones(n)]),constraints=LinearConstraint(csc_matrix(np.vstack(C)),np.concatenate(lo),np.concatenate(hi)),options={'time_limit':4,'mip_rel_gap':1e-10})
    rec={'n':n,'k':k,'S':S,'name':name,'status':int(sol.status),'rho':rho}
    if sol.x is not None:
        lam=sol.x[:n];q=A.T@lam;L=sum(lam)
        rec.update(p=float(q[0]),L=float(L),dual_share_ratio=float(rho*n*(q[0]/L)**2),objective=float(-sol.fun),gap=float(sol.mip_gap),lambda_=lam.tolist(),q=q.tolist())
    f.write(json.dumps(rec)+'\n');f.flush()
    print({key:rec.get(key) for key in ('n','k','name','status','dual_share_ratio','objective')},flush=True)
    if rec.get('dual_share_ratio',0)>2+1e-7:
        print('CANDIDATE STRICT AMPLIFICATION OBSTRUCTION',flush=True);break
