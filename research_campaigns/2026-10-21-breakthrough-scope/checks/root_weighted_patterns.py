"""Discovery only: optimize multiplicities of owner incidence patterns.

The row count is fixed, while owner counts grow via column replication. We
normalize total multiplicity to one (scale invariance of H). Every positive
rational multiplicity represents an ordinary binary cover after clearing
denominators. This is an incidence-design search, not a proved general bound.
"""
import argparse, itertools, json, time
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

def patterns(m):
    return np.array([[int(mask>>r&1) for r in range(m)] for mask in range(1,2**m)],float)

def full_point(G):
    m=len(G)
    for size in range(m,0,-1):
        for support in itertools.combinations(range(m),size):
            try:
                u=np.linalg.solve(G[np.ix_(support,support)],np.ones(size))
            except np.linalg.LinAlgError:
                continue
            if min(u)<-1e-9 or sum(u)<=0:continue
            a=np.zeros(m);a[list(support)]=u/sum(u)
            R=float(a@G@a)
            if min(G@a-R)>=-1e-8:return a,R
    raise ValueError('no certified numeric full support')

def theta(G, own):
    m=len(G); best=(-1,None)
    for mask in range(1,2**m):
        supp=[r for r in range(m) if mask>>r&1]
        eq=[np.r_[np.ones(m),0]];rhs=[1.]
        ub=[]
        for r in range(m):
            v=np.r_[G[r],-1.]
            if not own[r]:ub.append(-v)
            if r in supp:
                if own[r]:ub.append(v)
                else:eq.append(v);rhs.append(0.)
        res=linprog(np.r_[-own,0],A_ub=np.array(ub) if ub else None,
                    b_ub=np.zeros(len(ub)) if ub else None,
                    A_eq=np.array(eq),b_eq=np.array(rhs),
                    bounds=[(0,1) if r in supp else (0,0) for r in range(m)]+[(0,None)],
                    method='highs',options={'presolve':False})
        if res.success and -res.fun>best[0]:
            best=(-float(res.fun),{'alpha':res.x[:m].tolist(),'t':float(res.x[m]),'support':supp})
    if best[0]<0:raise ValueError('no witness')
    return best

def evaluate(weights,P):
    weights=np.array(weights,float);weights/=sum(weights)
    G=P.T@np.diag(weights)@P
    a,R=full_point(G)
    tt=[]; witnesses=[]
    for p,w in zip(P,weights):
        if w>1e-12:
            t,cert=theta(G,p);tt.append(t);witnesses.append(cert)
        else:tt.append(0.);witnesses.append(None)
    H=float(weights@np.square(tt)/R)
    return {'H':H,'weights':weights.tolist(),'theta':tt,'full_alpha':a.tolist(),
            'full_normalized_norm2':R,'witnesses':witnesses}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rows',type=int,default=4)
    ap.add_argument('--trials',type=int,default=30);ap.add_argument('--seconds',type=float,default=300)
    ap.add_argument('--output',required=True);a=ap.parse_args()
    P=patterns(a.rows);rng=np.random.default_rng(20261021+a.rows);start=time.monotonic()
    best=None;history=[]
    for it in range(a.trials):
        if time.monotonic()-start>a.seconds:break
        if it==0:w=np.ones(len(P))
        elif it%5==0:w=np.exp(rng.uniform(-5,2,len(P)))
        else:
            w=np.array(best['weights'])*np.exp(rng.normal(0,1.0 if it%3 else 2.0,len(P)))
            if it%4==0:w[rng.integers(len(P))]=0
        res=evaluate(w,P);history.append({'trial':it,'H':res['H']})
        if best is None or res['H']>best['H']:
            best=res; print(json.dumps({'trial':it,'H':best['H'],'elapsed':time.monotonic()-start}),flush=True)
        out={'status':'numerical discovery only','rows':a.rows,'patterns':P.astype(int).tolist(),
             'trials':len(history),'elapsed':time.monotonic()-start,'best':best,'history':history}
        Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
        if best['H']>2.000001:break

if __name__=='__main__':main()
