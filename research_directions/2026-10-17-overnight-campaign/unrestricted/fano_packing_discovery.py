"""Numerical discovery only: unrestricted payments on finite Fano report grids."""
import itertools, json, time
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = Path(__file__).resolve().parent
N = 7
LINES = sorted({tuple(sorted((a-1,b-1,(a^b)-1))) for a in range(1,8) for b in range(a+1,8)})
A = np.zeros((N,N))
for j,L in enumerate(LINES): A[list(L),j] = 1

def covers():
    # Exact postcheck of every retained candidate. Active-set exhaustion is
    # numerical here; this routine is discovery, not a complete certificate.
    C = np.vstack((A.T, np.eye(N)))
    rhs = np.r_[np.ones(N), np.zeros(N)]
    out = set()
    for active in itertools.combinations(range(2*N),N):
        try: w = np.linalg.solve(C[list(active)],rhs[list(active)])
        except np.linalg.LinAlgError: continue
        if min(w)<-1e-8 or min(A.T@w)<1-1e-8: continue
        q = tuple(Fraction(float(z)).limit_denominator(1000) for z in w)
        if min(q)<0 or any(sum(q[i] for i in L)<1 for L in LINES): continue
        if any(sum(Fraction(int(C[j,i]))*q[i] for i in range(N))!=Fraction(int(rhs[j])) for j in active): continue
        out.add(q)
    return sorted(out)

def solve(grid, tag):
    tick=time.time(); D=covers(); W=np.asarray([[float(z) for z in w] for w in D])
    grid=tuple(grid); k=len(grid)
    profiles=list(itertools.product(range(k),repeat=N)); index={p:j for j,p in enumerate(profiles)}
    coalitions=[tuple(i for i in range(N) if mask>>i&1) for mask in range(1,1<<N)]
    values={}
    def value(cap):
        cap=tuple(cap)
        if cap not in values: values[cap]=float(np.min(W@np.asarray(cap)))
        return values[cap]
    rows=[]; cols=[]; data=[]; rhs=[]; labels=[]
    def row(entries,b,label):
        r=len(rhs)
        for j,v in entries: rows.append(r); cols.append(j); data.append(v)
        rhs.append(b);labels.append(label)
    cvar=len(profiles)*N
    for pno,p in enumerate(profiles):
        cap=[grid[s] for s in p]; T=value(cap)
        row([(pno*N+i,1) for i in range(N)]+[(cvar,-T)],0,('budget',pno))
        for S in coalitions:
            val=value([cap[i] if i in S else 0 for i in range(N)])
            if val>0: row([(pno*N+i,-1) for i in S],-val,('cover',pno,S))
        for i in range(N):
            if p[i]+1<k:
                higher=list(p);higher[i]+=1; hno=index[tuple(higher)]
                row([(pno*N+i,1),(hno*N+i,-1)],0,('own',pno,i,hno))
    M=coo_matrix((data,(rows,cols)),shape=(len(rhs),cvar+1)).tocsr()
    obj=np.zeros(cvar+1);obj[-1]=1
    sol=linprog(obj,A_ub=M,b_ub=np.array(rhs),bounds=(0,None),method='highs')
    output={'status':'NUMERICAL_DISCOVERY_ONLY','technology':'fractional Fano-line packing',
        'grid':grid,'profiles':len(profiles),'variables':cvar+1,'rows':len(rhs),'covers':len(D),
        'solver_status':sol.status,'message':sol.message,'elapsed':time.time()-tick,
        'factor':float(sol.fun) if sol.success else None,'lines':LINES}
    if sol.success:
        dual=[]
        for j,v in enumerate(sol.ineqlin.marginals):
            if abs(v)>1e-9: dual.append({'label':labels[j],'weight':float(-v)})
        output['dual']=dual
        output['max_primal_violation']=float(np.max(M@sol.x-np.array(rhs)))
    (HERE/f'{tag}.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({a:b for a,b in output.items() if a!='dual'}),flush=True)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--grid',default='1,3');ap.add_argument('--tag',default='fano')
    args=ap.parse_args();solve([float(x) for x in args.grid.split(',')],args.tag)
