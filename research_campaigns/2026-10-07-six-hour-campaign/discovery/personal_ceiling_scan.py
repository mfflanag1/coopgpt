"""Discovery-only test of owner-independent personal maxflow ceiling payments."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
from scipy.stats import qmc
p=Path('/tmp/coopgt_common_clip_scan.py')
s=importlib.util.spec_from_file_location('base',p);base=importlib.util.module_from_spec(s);s.loader.exec_module(base);v=base.v


def evaluate(n,es,c,seed=710723,power=12):
    c=list(map(Q,c));m=len(es);cs=v.cutsets(n,es);T=v.maxflow(n,es,c)
    if not T:return None
    c=np.array(c,float)/float(T)
    mat=np.array([[bool(C>>e&1) for e in range(m)] for C in cs],float)
    cutcost=mat@c;U=qmc.Sobol(m,scramble=True,seed=seed).random_base2(power)
    pay=[];ceilings=[]
    for e in range(m):
        inc=mat[:,e]>0;ceiling=cutcost[~inc].min() if np.any(~inc) else np.inf
        ceilings.append(float(ceiling));a=np.minimum(c,ceiling)
        scores=(U*a)@mat.T
        A=scores[:,inc].min(axis=1)-a[e]*U[:,e]
        B=scores[:,~inc].min(axis=1) if np.any(~inc) else np.full(len(U),np.inf)
        pay.append(float(np.clip(B-A,0,a[e]).mean()))
    coalition=np.array([[bool(S>>e&1) for e in range(m)] for S in range(1<<m)],float)
    values=((coalition*c)@mat.T).min(axis=1);sums=coalition@np.array(pay)
    gaps=values-sums;which=int(gaps.argmax())
    return dict(n=n,edges=es,c=c.tolist(),K=len(cs),pay=pay,ceilings=ceilings,
                worst_gap=float(gaps[which]),coalition=which,value=float(values[which]),paid=float(sums[which]),
                sum_pay=sum(pay),power=power,seed=seed)


def main():
    rng=np.random.default_rng(710727);rows=[]
    for it in range(1000):
        n=int(rng.choice([3,4,5,6]));es=[(a,b) for a in range(n) for b in range(a+1,n) if b==a+1 or rng.random()<.5]
        if rng.random()<.5:es += [es[int(rng.integers(len(es)))]]*int(rng.integers(1,4))
        if len(es)>12:continue
        c=[Q(int(rng.integers(1,41)),int(rng.choice([1,2,4,10]))) for e in es]
        row=evaluate(n,es,c);rows.append(row)
        if it%25==0 or row['worst_gap']>1e-3:
            print(json.dumps(dict(done=it+1,cases=len(rows),max_gap=max(r['worst_gap'] for r in rows))),flush=True)
            Path('/tmp/coopgt_personal_ceiling_scan.json').write_text(json.dumps(rows,indent=2))
        if row['worst_gap']>.002:
            print(json.dumps(row),flush=True);break
    Path('/tmp/coopgt_personal_ceiling_scan.json').write_text(json.dumps(rows,indent=2))


if __name__=='__main__':main()
