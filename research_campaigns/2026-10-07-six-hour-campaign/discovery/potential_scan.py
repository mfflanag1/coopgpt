"""Heuristic QMC discovery for a different truthful majorant; not a certificate.

Psi(c)=E maxflow(D(c)*U). Test whether Psi(c)-Psi(c_e=0)<=z_e(c).
If true, 2*deletion marginals of Psi would dominate the envelope at cost 2U(K)T.
The domination of z by 2*marginals is proved separately; the reverse inequality
being tested is only a conjecture. Near-zero QMC discrepancies are not findings.
"""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import json
import numpy as np
from scipy.stats import qmc

repo=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt')
spec=importlib.util.spec_from_file_location('v',repo/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


def evaluate(n,edges,c,power=11,seed=1707):
    m=len(edges);cuts=v.cutsets(n,edges)
    D=v.effective(n,edges,c);T=v.maxflow(n,edges,c)
    if T==0:return None
    D0=[]
    for e in range(m):
        ce=c.copy();ce[e]=Q(0);D0.append(v.effective(n,edges,ce))
    cutmatrix=np.array([[bool(C>>e&1) for e in range(m)] for C in cuts],float)
    ds=np.array(D,float)/float(T)
    zeros=np.array(D0,float)/float(T)
    U=qmc.Sobol(m,scramble=True,seed=seed).random_base2(power)
    scores=(U*ds)@cutmatrix.T
    phi=np.min(scores,axis=1)
    z=[];marg=[]
    for e in range(m):
        containing=cutmatrix[:,e]>0
        A=np.min(scores[:,containing]-ds[e]*U[:,e,None],axis=1)
        B=np.min(scores[:,~containing],axis=1) if np.any(~containing) else np.full(len(U),np.inf)
        z.append(float(np.mean(np.clip(B-A,0,ds[e]))))
        erased=np.min((U*zeros[e])@cutmatrix.T,axis=1)
        marg.append(float(np.mean(phi-erased)))
    difference=np.array(marg)-np.array(z)
    return dict(n=n,edges=edges,c=[str(x) for x in c],K=len(cuts),T=str(T),
                phi=float(np.mean(phi)),z=z,marginals=marg,
                worst_difference=float(np.max(difference)),focal=int(np.argmax(difference)),
                sum_z=float(sum(z)),sum_marginals=float(sum(marg)),power=power,seed=seed)


def main():
    rng=np.random.default_rng(20261007)
    records=[]
    examples=[]
    for n in (4,5,6,7):
        for _ in range(35):
            edges=[(a,b) for a in range(n) for b in range(a+1,n)
                   if b==a+1 or rng.random()<0.4]
            c=[Q(int(rng.choice([1,2,3,4,8,16,32])),8) for _ in edges]
            examples.append((n,edges,c))
    # Certified failure topology; exact nonmonotonicity is in prior campaign.
    for k in (2,5,10,20):
        edges=[(0,1),(0,2)]+[(1,3)]*k+[(2,3),(1,2),(0,3),(3,4),(3,4)]
        c=[Q(19,20),Q(1,20)]+[Q(2)]*k+[Q(2),Q(2),Q(2),Q(1,2),Q(1,2)]
        examples.append((5,edges,c))
    for j,(n,edges,c) in enumerate(examples):
        result=evaluate(n,edges,c)
        if result is not None:records.append(result)
        if (j+1)%20==0:
            print(json.dumps(dict(done=j+1,worst=max(x['worst_difference'] for x in records))),flush=True)
    records.sort(key=lambda x:x['worst_difference'],reverse=True)
    out=dict(status='HEURISTIC ONLY',cases=len(records),top=records[:12],
             max_aggregate_ratio=max(x['sum_marginals']/x['sum_z'] for x in records),all_cases=records)
    Path('/tmp/coopgt_potential_scan.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
