"""Discovery-only scan of common-grand-flow clipping and own reports."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
from scipy.stats import qmc
p=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt/research_campaigns/2026-10-06-monotone-envelope/verification/verify.py')
s=importlib.util.spec_from_file_location('v',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)

def evaluate(n,es,c,seed=7407,power=11):
    c=list(map(Q,c));m=len(es);cs=v.cutsets(n,es);T=v.maxflow(n,es,c)
    if not T:return None
    cf=np.array(c,float)/float(T);mat=np.array([[bool(C>>e&1) for e in range(m)] for C in cs],float)
    U=qmc.Sobol(m,scramble=True,seed=seed).random_base2(power)
    best=None
    for e in range(m):
        cc=c.copy();cc[e]=Q(0);T0=float(v.maxflow(n,es,cc)/T)
        if T0>=1 or not cf[e]:continue
        inc=mat[:,e]>0
        vals=[]
        for t in np.linspace(0,min(cf[e],1),21)[1:]:
            total=min(1,T0+t);a=np.minimum(cf,total);a[e]=t
            scores=(U*a)@mat.T
            A=scores[:,inc].min(axis=1)-t*U[:,e]
            B=scores[:,~inc].min(axis=1) if np.any(~inc) else np.full(len(U),np.inf)
            vals.append((float(t),float(np.clip(B-A,0,t).mean())))
        for (x,z),(xx,zz) in zip(vals,vals[1:]):
            drop=z-zz
            if best is None or drop>best['drop']:
                best=dict(drop=drop,edge=e,x0=x,x1=xx,z0=z,z1=zz,T0=T0,values=vals)
    return dict(n=n,edges=es,c=list(map(str,c)),K=len(cs),T=str(T),best=best)

def main():
    rng=np.random.default_rng(74771);rows=[]
    for it in range(600):
        n=int(rng.integers(3,8));es=[(a,b) for a in range(n) for b in range(a+1,n) if b==a+1 or rng.random()<.45]
        # Duplicate some edges to include unequal bundles.
        if rng.random()<.5:es += [es[int(rng.integers(len(es)))]]*int(rng.integers(1,4))
        c=[Q(int(rng.integers(1,41)),int(rng.choice([1,2,4,10]))) for e in es]
        row=evaluate(n,es,c);rows.append(row)
        if it%20==0 or row['best'] and row['best']['drop']>1e-5:
            print(json.dumps(dict(done=it+1,max_drop=max((r['best']['drop'] for r in rows if r['best']),default=0))),flush=True)
            Path('/tmp/coopgt_common_clip_scan.json').write_text(json.dumps(rows,indent=2))
        if row['best'] and row['best']['drop']>.001:
            print(json.dumps(row),flush=True);break
    Path('/tmp/coopgt_common_clip_scan.json').write_text(json.dumps(rows,indent=2))

if __name__=='__main__':main()
