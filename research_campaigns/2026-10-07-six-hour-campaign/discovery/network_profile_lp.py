"""Discovery LP for fixed-owner, positive two-report finite restrictions.

Primal variables are unrestricted nonnegative owner/profile payments and one
worst-profile budget factor. This is a lower-bound restriction, not an all-real-
profile mechanism. Dual candidates are reconstructed and independently checked
with Fraction arithmetic against every variable before reporting a certificate.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import importlib.util,json,time,random
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

vp=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt/research_campaigns/2026-10-06-monotone-envelope/verification/verify.py')
spec=importlib.util.spec_from_file_location('v',vp);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


def build(n,es,low,high):
    m=len(es);P=1<<m;beta=P*m;cuts=v.cutsets(n,es)
    coalitions=np.array([[bool(S>>e&1) for e in range(m)] for S in range(P)],dtype=np.int64)
    cm=np.array([[bool(C>>e&1) for e in range(m)] for C in cuts],dtype=np.int64)
    entries=[];bounds=[];types=[]
    def row(coeff,rhs,kind):
        entries.append(coeff);bounds.append(rhs);types.append(kind)
    for p in range(P):
        c=np.array([high[e] if p>>e&1 else low[e] for e in range(m)],dtype=np.int64)
        values=((coalitions*c)@cm.T).min(axis=1)
        for S in range(1,P):
            val=int(values[S])
            if not val:continue
            owners=[e for e in range(m) if S>>e&1]
            if any(values[S^(1<<e)]==val for e in owners):continue
            row([(p*m+e,-1) for e in owners],-val,('cover',p,S))
        row([(p*m+e,1) for e in range(m)]+[(beta,-int(values[-1]))],0,('budget',p))
        for e in range(m):
            if not p>>e&1:
                row([(p*m+e,1),((p|(1<<e))*m+e,-1)],0,('monotone',p,e))
    rr=[];cc=[];dd=[]
    for j,row in enumerate(entries):
        for k,x in row:rr.append(j);cc.append(k);dd.append(x)
    a=coo_matrix((dd,(rr,cc)),shape=(len(entries),beta+1)).tocsr()
    return a,np.array(bounds),entries,types,cuts


def verify_dual(entries,bounds,dual,beta):
    # A x<=b, x>=0, min c x: multipliers d<=0, A^T d<=c.
    # Reconstruct -d as positive multipliers; allow scaling the beta coefficient.
    for den in [10000,1000000,1000000000]:
        multipliers={j:Q(float(-x)).limit_denominator(den) for j,x in enumerate(dual) if x < -1e-9}
        sums={};constant=Q(0)
        for j,w in multipliers.items():
            assert w>=0
            constant -= w*int(bounds[j])
            for e,x in entries[j]:sums[e]=sums.get(e,Q(0))+w*x
        # sum w*A has all payment coefficients >=0 and beta coefficient <0.
        # 0<=sum owner coeff*p <= -constant + B*(-sum beta coeff).
        if all(x>=0 for e,x in sums.items() if e!=beta) and sums.get(beta,0)<0:
            bound=constant/-sums[beta]
            return dict(bound=str(bound),denominator_limit=den,
                        multipliers={str(j):str(w) for j,w in multipliers.items()},
                        owner_residual_min=str(min((x for e,x in sums.items() if e!=beta),default=0)),
                        budget_coefficient=str(-sums[beta]),constant=str(constant))
    return None


def solve(n,es,low,high,label,seconds=45):
    begin=time.monotonic();a,b,entries,types,cuts=build(n,es,low,high)
    obj=np.zeros(a.shape[1]);obj[-1]=1
    result=linprog(obj,A_ub=a,b_ub=b,bounds=(0,None),method='highs',options={'time_limit':seconds})
    row=dict(label=label,n=n,edges=es,low=low,high=high,K=len(cuts),
             variables=a.shape[1],rows=a.shape[0],success=bool(result.success),
             message=result.message,elapsed=time.monotonic()-begin)
    if result.success:
        row['optimum']=float(result.fun)
        cert=verify_dual(entries,b,result.ineqlin.marginals,a.shape[1]-1)
        row['certificate']=cert
        if cert:
            row['certificate_rows']={j:dict(type=types[int(j)],coeff=entries[int(j)],rhs=int(b[int(j)])) for j in cert['multipliers']}
    return row


def main():
    rng=random.Random(710712);rows=[]
    cases=[(3,[(0,1),(0,1),(1,2),(1,2)],'two-pools'),
           (4,[(0,1),(0,2),(1,2),(1,3),(2,3)],'wheatstone'),
           (4,[(0,1),(0,2),(1,2),(1,3),(1,3),(2,3)],'augmented-wheatstone'),
           (5,[(0,1),(0,2),(1,2),(1,3),(2,3),(2,4),(3,4)],'fibonacci-5'),
           (5,[(0,1),(0,2),(1,2),(1,3),(2,3),(2,4),(3,4),(0,3)],'interacting-5')]
    for i in range(12):
        n=5;es=[(a,b) for a in range(n) for b in range(a+1,n) if b==a+1 or rng.random()<.4]
        if len(es)<=8:cases.append((n,es,'random-'+str(i)))
    for n,es,label in cases:
        for high in [2,4,10]:
            row=solve(n,es,[1]*len(es),[high]*len(es),label+'-'+str(high));rows.append(row)
            print(json.dumps({k:v for k,v in row.items() if k not in ['certificate','certificate_rows','edges','low','high']},default=str),flush=True)
            Path('/tmp/coopgt_network_profile_lp.json').write_text(json.dumps(rows,indent=2))
    return rows


if __name__=='__main__':main()
