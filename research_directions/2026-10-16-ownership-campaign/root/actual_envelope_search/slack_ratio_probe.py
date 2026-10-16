"""Discover actual incentive gain relative to raw composition-budget slack.
Only lower witnesses, not universal inequalities; tiny denominators excluded.
"""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
from probe_v2 import actual, masks


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--n',type=int,default=4)
    ap.add_argument('--m',type=int,default=2)
    ap.add_argument('--kind',default='all')
    ap.add_argument('--seconds',type=float,default=420)
    ap.add_argument('--seed',type=int,default=931)
    args=ap.parse_args();n,m=args.n,args.m
    mask=masks(n,m,args.kind);count=int(mask.sum());start=time.monotonic()
    C2=(1+1/(2*np.e))**2;best=[0.,None];runs=[]
    dest=Path(__file__).with_name(f'slack_{n}_{m}_{args.kind}_{args.seed}.json')
    def unpack(x):
        a=np.asarray(x);a=a.T if a.ndim==2 else a[None,:]
        base=np.zeros((len(a),n,2*m+1));frac=np.ones_like(base)
        base[:,mask]=a[:,:count];frac[:,mask]=a[:,count:]
        return base,frac
    def measures(base,frac):
        _,pay,F=actual(base,frac,n,m)
        raw,full,_=actual(base,np.ones_like(frac),n,m)
        chosen=np.maximum(pay,full)
        gain=(chosen-full).sum(axis=-1)
        slack=C2*F-full.sum(axis=-1)
        score=np.divide(gain,slack,out=np.zeros_like(gain),where=(slack>1e-5*F)&(F>1e-9))
        return score,gain,slack,chosen,full,F,raw,pay
    def objective(x):
        base,frac=unpack(x);scores,*_=measures(base,frac)
        at=int(np.argmax(scores))
        if scores[at]>best[0]:
            best[:]=[float(scores[at]),np.r_[base[at][mask],frac[at][mask]].tolist()]
        return -scores if np.asarray(x).ndim==2 else -float(scores[0])
    def save():
        if best[1] is None:return
        base,frac=unpack(np.array(best[1]))
        score,gain,slack,pay,full,F,raw,dev=measures(base,frac)
        under=np.where((dev>=full)[...,None],base*frac,base)
        data={'status':'numerical actual-report lower witness only',
              'score':float(score[0]),'gain':float(gain[0]),'slack':float(slack[0]),
              'ratio':float(pay[0].sum()/F[0]),'raw_ratio':float(raw[0]),
              'F':float(F[0]),'C_squared':float(C2),
              'base':base[0].tolist(),'own_underreports':under[0].tolist(),
              'payments':pay[0].tolist(),'raw_payments':full[0].tolist(),
              'n':n,'m':m,'kind':args.kind,'seed':args.seed,
              'elapsed_seconds':time.monotonic()-start,'runs':runs}
        dest.write_text(json.dumps(data,indent=2)+'\n')
    for rep in range(100):
        rng=np.random.default_rng(args.seed+rep)
        init=rng.uniform(0,1,(16*2*count,2*count))
        if n>=3:
            b=np.zeros((n,2*m+1));b[0,0]=b[1,0]=.5;b[2,m]=1
            fr=np.ones_like(b);fr[2,m]=.8
            center=np.r_[b[mask],fr[mask]];init[0]=center
            for row in range(1,len(init)//3):
                init[row]=np.clip(center+rng.normal(0,.1 if rep%2==0 else .35,len(center)),0,1)
        def callback(x,convergence):
            save();return time.monotonic()-start>=args.seconds
        res=differential_evolution(objective,[(0.,1.)]*(2*count),init=init,
               seed=args.seed+rep,maxiter=3000,tol=1e-9,polish=False,
               vectorized=True,updating='deferred',callback=callback)
        runs.append({'rep':rep,'best_score':-float(res.fun),'iterations':int(res.nit)})
        save();print(json.dumps({'rep':rep,'best_score':best[0],
                               'elapsed':time.monotonic()-start}),flush=True)
        if time.monotonic()-start>=args.seconds:break
    print(dest,flush=True)


if __name__=='__main__':main()
