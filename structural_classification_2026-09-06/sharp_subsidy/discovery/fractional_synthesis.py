"""Discovery only: alternate two LPs; floating outputs are not proofs."""
from itertools import product
from pathlib import Path
import argparse, json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


class Synthesis:
    def __init__(self, m):
        self.m=m; self.n=n=3*m; self.offset=offset=3*m*m
        self.teams=list(product(range(m),repeat=3)); nt=len(self.teams)
        self.inc=np.zeros((n,nt)); self.pair=np.zeros((offset,nt))
        for z,(a,b,c) in enumerate(self.teams):
            self.inc[[a,m+b,2*m+c],z]=1
            self.pair[[a*m+b,m*m+a*m+c,2*m*m+b*m+c],z]=1
        rr=[];cc=[];vv=[]
        for i in range(n):
            for z,t in enumerate(self.teams):
                row=i*nt+z
                for p in np.flatnonzero(self.pair[:,z]):rr.append(row);cc.append(p);vv.append(1)
                for p in np.flatnonzero(self.inc[:,z]):rr.append(row);cc.append(offset+i*n+p);vv.append(-1)
        self.ub=coo_matrix((vv,(rr,cc)),shape=(n*nt,offset+n*n)).tocsr()
        self.eq=np.zeros((n+1,offset+n*n))
        for j in range(m):self.eq[0,:offset]+=self.pair[:,self.teams.index((j,j,j))]
        for i in range(n):self.eq[i+1,offset+i*n:offset+(i+1)*n]=1

    def synth(self, lam):
        d=self.inc@lam
        if min(lam)<-1e-8 or max(d)>1+1e-8:raise ValueError('invalid packing')
        obj=np.zeros(self.offset+self.n*self.n);obj[:self.offset]=-self.pair@lam
        obj[self.offset+np.arange(self.n)*(self.n+1)]=-(1-d)/3
        r=linprog(obj,A_ub=self.ub,b_ub=np.zeros(self.ub.shape[0]),A_eq=self.eq,b_eq=np.ones(self.n+1),bounds=(0,None))
        if not r.success:raise ValueError(r.message)
        return -r.fun-1,r.x[:self.offset],r.x[self.offset:].reshape(self.n,self.n)

    def ideals(self, pairs):
        w=self.pair.T@pairs;H=[]
        for i in range(self.n):
            obj=np.zeros(self.n);obj[i]=-1
            r=linprog(obj,A_ub=-self.inc.T,b_ub=-w,A_eq=np.ones((1,self.n)),b_eq=[1],bounds=(0,None))
            if not r.success:raise ValueError(r.message)
            H.append(-r.fun)
        return np.array(H)

    def packing(self, pairs, H):
        gains=self.pair.T@pairs-self.inc.T@H/3
        r=linprog(-gains,A_ub=self.inc,b_ub=np.ones(self.n),bounds=(0,None))
        if not r.success:raise ValueError(r.message)
        return r.x,-r.fun+sum(H)/3-1


def run():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=40);args=ap.parse_args()
    rng=np.random.default_rng(9072026);best=0; records=[]
    for m in [2,3,4,5,6,8]:
        model=Synthesis(m); nt=len(model.teams);fractional=0
        for trial in range(args.trials):
            # Sparse random support favors partial, genuinely fractional vertices.
            gains=-np.ones(nt)
            support=rng.choice(nt,size=min(nt,rng.integers(m,4*m+1)),replace=False)
            gains[support]=rng.uniform(.5,1.5,len(support))
            r=linprog(-gains,A_ub=model.inc,b_ub=np.ones(model.n),bounds=(0,None))
            lam=r.x
            fractional+=bool(np.any((lam>1e-7)&(lam<1-1e-7)))
            old=-1
            for step in range(5):
                value,pairs,witnesses=model.synth(lam)
                H=model.ideals(pairs); newlam,value=model.packing(pairs,H)
                if value>best+1e-8:
                    best=value
                    record={'m':m,'trial':trial,'step':step,'ratio':value,'matrices':pairs.reshape(3,m,m).tolist(),'H':H.tolist(),'packing':[(model.teams[j],float(v))for j,v in enumerate(newlam)if v>1e-8]}
                    records.append(record);print(json.dumps(record),flush=True)
                    Path(__file__).with_name('fractional_best.json').write_text(json.dumps(records,indent=2)+'\n')
                if value<=old+1e-8:break
                old=value;lam=newlam
        print(json.dumps({'m':m,'trials':args.trials,'fractional_starts':fractional,'best':best}),flush=True)


if __name__=='__main__':run()
