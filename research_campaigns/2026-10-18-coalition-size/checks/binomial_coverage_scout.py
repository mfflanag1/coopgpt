"""Discovery-only floating LP probe; no finite success is a theorem."""
from itertools import combinations
from pathlib import Path
import json, random, time
import numpy as np
from scipy.optimize import linprog

def worths(A,profit,b):
    n=len(b); out=np.zeros(1<<n)
    for mask in range(1,1<<n):
        cap=np.sum([b[i] for i in range(n) if mask>>i&1],axis=0)
        z=linprog(-profit,A_ub=A,b_ub=cap,bounds=(0,None),method='highs')
        assert z.success,z.message
        out[mask]=-z.fun
    return out

def run(trials=1200,seed=1837,fixed_r=None):
    rng=random.Random(seed); best=(float('inf'),None); started=time.time()
    counts=0
    for trial in range(trials):
        n=rng.choice([3,4,5,6]); d=rng.choice([3,4,5,6]); r=fixed_r or rng.choice([2,3])
        supports=list(combinations(range(d),r))
        rng.shuffle(supports); supports=supports[:rng.randrange(1,len(supports)+1)]
        A=np.zeros((d,len(supports)))
        for j,support in enumerate(supports):
            for row in support:A[row,j]=rng.choice([1,1,1,2])
        profit=np.array([rng.choice([1,1,2,3]) for _ in supports])
        b=np.array([[rng.randrange(4) if rng.random()<.4 else 0 for _ in range(d)] for _ in range(n)])
        if trial%3==0:
            b=np.zeros((n,d),dtype=int)
            for i in range(n):b[i,rng.randrange(d)]=rng.randrange(1,4)
        v=worths(A,profit,b)
        if v[-1]<1e-8:continue
        for s in [2,3,4]:
            p=1/s; threshold=min(1,r*p**(r-1))
            m=np.array([sum(p**mask.bit_count()*(1-p)**(n-1-mask.bit_count())*(v[mask|1<<i]-v[mask]) for mask in range(1<<n) if not(mask>>i&1)) for i in range(n)])
            for C in range(1,1<<n):
                if v[C]<1e-8:continue
                ratio=sum(m[i] for i in range(n) if C>>i&1)/v[C]
                norm=ratio/threshold;counts+=1
                if norm<best[0]:
                    best=(norm,dict(trial=trial,r=r,s=s,coalition=C,n=n,d=d,A=A.tolist(),profit=profit.tolist(),b=b.tolist(),values=v.tolist(),marginals=m.tolist(),ratio=ratio,conjectured_threshold=threshold))
                if norm<1-1e-7:
                    return dict(status='floating_counterexample_needs_exact_replay',seed=seed,checks=counts,best_normalized_ratio=norm,witness=best[1],elapsed=time.time()-started)
        if trial%100==0:print(json.dumps(dict(progress=trial,best=best[0])),flush=True)
    return dict(status='no_counterexample_in_bounded_scout',seed=seed,trials=trials,checks=counts,best_normalized_ratio=best[0],witness=best[1],elapsed=time.time()-started)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--arity',type=int,choices=[2,3]);args=ap.parse_args()
    result=run(fixed_r=args.arity)
    dest=Path(__file__).with_suffix('.json') if args.arity is None else Path(__file__).with_name(f'binomial_coverage_scout_r{args.arity}.json')
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
