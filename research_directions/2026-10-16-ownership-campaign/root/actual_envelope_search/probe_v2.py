"""Numerical lower witnesses for the actual nested own-report envelope.
No numerical upper bounds or proof claims. Each candidate contains actual underreports.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution

def phi(a,b):
    A=a.sum(axis=-1,keepdims=True); B=b.sum(axis=-1,keepdims=True)
    short=np.where(A<=B,a,b); long=np.where(A<=B,b,a)
    T=np.minimum(A,B); capped=np.minimum(long,T)
    rho=np.divide(capped.sum(axis=-1,keepdims=True),T,out=np.zeros_like(T),where=T>0)
    q=.5*np.exp(1-rho)
    out=(1-q)*short+q*capped
    return np.where(T>0,out,0.)

def actual(base,frac,n,m):
    batch=len(base)
    profiles=np.broadcast_to(base[:,None,:,:],(batch,n,n,2*m+1)).copy()
    for i in range(n):profiles[:,i,i,:]*=frac[:,i,:]
    h=profiles[...,:m];l=profiles[...,m:2*m];p=profiles[...,-1]
    local=phi(np.moveaxis(h,-1,-2),np.moveaxis(l,-1,-2))
    z=local.sum(axis=-2)
    outer=phi(h.sum(axis=-1),p+z)
    diagonal=np.diagonal(outer,axis1=1,axis2=2)
    H=base[...,:m].sum(axis=1);L=base[...,m:2*m].sum(axis=1);P=base[...,-1].sum(axis=1)
    F=np.minimum(H.sum(axis=-1),P+np.minimum(H,L).sum(axis=-1))
    return np.divide(diagonal.sum(axis=-1),F,out=np.zeros_like(F),where=F>1e-12),diagonal,F

def masks(n,m,kind):
    mask=np.ones((n,2*m+1),dtype=bool)
    if kind=='no_grid':mask[:,-1]=False
    if kind=='hardware_power':
        cut=max(1,n//2);mask[:cut,m:]=False;mask[cut:,:m]=False
    if kind=='local_grid':
        mask[:]=False;mask[:n-2,:m]=True;mask[n-2,m:2*m]=True;mask[n-1,-1]=True
    return mask

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=4);ap.add_argument('--m',type=int,default=2)
    ap.add_argument('--kind',default='all');ap.add_argument('--seconds',type=float,default=300);ap.add_argument('--seed',type=int,default=711);ap.add_argument('--seeded',action='store_true')
    args=ap.parse_args();n,m=args.n,args.m;mask=masks(n,m,args.kind);count=int(mask.sum());start=time.monotonic();best=[0.,None];runs=[]
    dest=Path(__file__).parent/f'witness_v2_{n}_{m}_{args.kind}_{args.seed}.json'
    def unpack(x):
        a=np.asarray(x); a=a.T if a.ndim==2 else a[None,:]
        base=np.zeros((len(a),n,2*m+1));frac=np.ones_like(base)
        base[:,mask]=a[:,:count];frac[:,mask]=a[:,count:]
        return base,frac
    def objective(x):
        base,frac=unpack(x);ratios,pays,F=actual(base,frac,n,m)
        _,fullpay,_=actual(base,np.ones_like(frac),n,m)
        ratios=np.divide(np.maximum(pays,fullpay).sum(axis=-1),F,out=np.zeros_like(F),where=F>1e-12)
        at=int(np.argmax(ratios))
        if ratios[at]>best[0]:
            best[:]=[float(ratios[at]),np.r_[base[at][mask],frac[at][mask]].tolist()]
        return -ratios if np.asarray(x).ndim==2 else -float(ratios[0])
    def save():
        if best[1] is None:return
        base,frac=unpack(np.array(best[1]));ratio,pay,F=actual(base,frac,n,m)
        full,fullpay,_=actual(base,np.ones_like(frac),n,m)
        chosen=np.where((pay>=fullpay)[...,None],base*frac,base)
        ratio=np.divide(np.maximum(pay,fullpay).sum(axis=-1),F,out=np.zeros_like(F),where=F>1e-12)
        data={'status':'numerical lower witness only','n':n,'m':m,'kind':args.kind,'seed':args.seed,'elapsed_seconds':time.monotonic()-start,'ratio':float(ratio[0]),'raw_ratio':float(full[0]),'C_squared':float((1+1/(2*np.e))**2),'F':float(F[0]),'base':base[0].tolist(),'own_underreports':chosen[0].tolist(),'payments_at_distinct_actual_profiles':np.maximum(pay,fullpay)[0].tolist(),'full_profile_payments':fullpay[0].tolist(),'runs':runs}
        dest.write_text(json.dumps(data,indent=2)+'\n')
    for rep in range(100):
        def callback(xk,convergence):
            save();return time.monotonic()-start>=args.seconds
        init='latinhypercube'
        if args.seeded and n>=4 and m>=2:
            rng=np.random.default_rng(args.seed+rep);init=rng.uniform(0,1,(12*2*count,2*count))
            b=np.zeros((n,2*m+1));c=1/(2*np.e);b[0,0]=1+2*c;b[0,1]=1;b[1,0]=1;b[2,1]=1+2*c;b[3,m:m+2]=1;b/=1+2*c
            center=np.r_[b[mask],np.ones(count)];init[0]=center
            for row in range(1,len(init)//2):
                init[row]=np.clip(center+rng.normal(0, .03 if rep%2==0 else .2,len(center)),0,1)
        res=differential_evolution(objective,[(0.,1.)]*(2*count),seed=args.seed+rep,init=init,popsize=12,maxiter=2500,tol=1e-8,polish=False,vectorized=True,updating='deferred',callback=callback)
        runs.append({'rep':rep,'ratio':-float(res.fun),'nit':int(res.nit),'nfev_batches':int(res.nfev)});save()
        print(json.dumps({'rep':rep,'best':best[0],'elapsed':time.monotonic()-start}),flush=True)
        if time.monotonic()-start>=args.seconds:break
    print(dest,flush=True)
if __name__=='__main__':main()
