"""QMC falsification of one-sided deletion cut repair. Heuristic, not proof."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import json
import numpy as np
from scipy.stats import qmc

REPO=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt')
spec=importlib.util.spec_from_file_location('v',REPO/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def fibonacci_cuts(n,es):
    result=[]
    for b in range((n-2)//2+1):
        for a in range(1,n-2*b):
            c=n-2*b-a
            word=[1]*a+[x for _ in range(b) for x in (0,1)]+[0]*c
            result.append(sum(1<<e for e,(i,j) in enumerate(es) if word[i] and not word[j]))
    return sorted(result)

def effective(n,edges,c):
    pre={a:v.maxflow(n,edges,c,0,a) for a in set(a for a,b in edges) if a}
    suf={b:v.maxflow(n,edges,c,b,n-1) for b in set(b for a,b in edges) if b!=n-1}
    return [min([c[e]]+([pre[a]] if a else [])+([suf[b]] if b!=n-1 else []))
            for e,(a,b) in enumerate(edges)]

def evaluate(n,edges,c,cuts=None,power=10,seed=71027,label='random'):
    m=len(edges)
    if cuts is None:cuts=v.cutsets(n,edges)
    D=effective(n,edges,c);T=v.maxflow(n,edges,c)
    if not T:return None
    zeros=[]
    for e in range(m):
        ce=c.copy();ce[e]=Q(0);zeros.append(effective(n,edges,ce))
    matrix=np.array([[bool(C>>e&1) for e in range(m)] for C in cuts],float)
    d=np.array(D,float)/float(T);d0=np.array(zeros,float)/float(T)
    U=qmc.Sobol(m,scramble=True,seed=seed).random_base2(power)
    scores=(U*d)@matrix.T
    z=[];p=[]
    for e in range(m):
        inc=matrix[:,e]>0
        B=scores[:,~inc].min(axis=1) if np.any(~inc) else np.full(len(U),np.inf)
        A=scores[:,inc].min(axis=1)-d[e]*U[:,e]
        A0=((U*d0[e])@matrix[inc].T).min(axis=1)
        ze=float(np.mean(np.clip(B-A,0,d[e])))
        pe=float(np.mean(np.clip(B-A0,0,d[e])))
        assert pe+1e-12>=ze
        z.append(ze);p.append(pe)
    return dict(label=label,n=n,m=m,K=len(cuts),T=str(T),edges=edges,
                capacities=list(map(str,c)),z=z,p=p,sum_z=sum(z),sum_p=sum(p),
                inflation=sum(p)/sum(z),excess=sum(p)-sum(z),power=power,seed=seed)

def main():
    rng=np.random.default_rng(7102701);cases=[]
    for n in (4,5,6,7,8):
        for _ in range(25):
            es=[(a,b) for a in range(n) for b in range(a+1,n)
                if b==a+1 or rng.random()<.35]
            c=[Q(int(rng.choice([1,2,4,8,16,32,64])),8) for _ in es]
            cases.append((n,es,c,None,'random'))
    for r in (2,3,4,6,8):
        n=2*r;es=[(a,b) for a in range(n) for b in range(a+1,min(a+3,n))]
        cs=fibonacci_cuts(n,es)
        for mode in range(8):
            c=[Q(int(rng.choice([1,2,4,8,16,32])),8) for _ in es]
            if mode==0:c=[Q(1)]*len(es)
            if mode==1:c=[Q(1) if b==a+1 else Q(1,100) for a,b in es]
            if mode==2:c=[Q(1,100) if b==a+1 else Q(1) for a,b in es]
            cases.append((n,es,c,cs,f'fibonacci-{r}-{mode}'))
    for k in (2,5,10,20):
        es=[(0,1),(0,2)]+[(1,3)]*k+[(2,3),(1,2),(0,3),(3,4),(3,4)]
        c=[Q(19,20),Q(1,20)]+[Q(2)]*k+[Q(2),Q(2),Q(2),Q(1,2),Q(1,2)]
        cases.append((5,es,c,None,f'wheatstone-{k}'))
    rows=[]
    for j,(n,es,c,cs,label) in enumerate(cases):
        row=evaluate(n,es,c,cs,label=label)
        if row:rows.append(row)
        if (j+1)%10==0:
            print(json.dumps(dict(done=j+1,max_excess=max(x['excess'] for x in rows),
                                 max_payment=max(x['sum_p'] for x in rows))),flush=True)
    rows.sort(key=lambda x:x['excess'],reverse=True)
    out=dict(status='HEURISTIC ONLY',cases=len(rows),results=rows)
    Path('/tmp/coopgt_one_sided_scan.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'top':rows[:5]}),flush=True)

if __name__=='__main__':main()
