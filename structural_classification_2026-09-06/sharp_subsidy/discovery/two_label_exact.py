"""Exhaustive rational packing vertices and independently checked LP duals."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog
from fractional_synthesis import Synthesis


def solve(A,b):
    a=[[F(x)for x in row]+[F(y)]for row,y in zip(A,b)];n=len(b)
    for k in range(n):
        pivot=next((j for j in range(k,n)if a[j][k]),None)
        if pivot is None:return None
        a[k],a[pivot]=a[pivot],a[k];v=a[k][k];a[k]=[x/v for x in a[k]]
        for j in range(n):
            if j!=k:
                v=a[j][k];a[j]=[x-v*y for x,y in zip(a[j],a[k])]
    return [row[-1]for row in a]


def vertices(inc):
    n,nt=inc.shape;out={tuple([F(0)]*nt)};bases=0
    for k in range(1,n+1):
        for support in combinations(range(nt),k):
            for tight in combinations(range(n),k):
                bases+=1
                x=solve([[int(inc[i,j])for j in support]for i in tight],[1]*k)
                if x is None or min(x)<0:continue
                if any(sum(int(inc[i,j])*v for j,v in zip(support,x))>1 for i in range(n)):continue
                lam=[F(0)]*nt
                for j,v in zip(support,x):lam[j]=v
                out.add(tuple(lam))
    return sorted(out),bases


def run():
    model=Synthesis(2);verts,bases=vertices(model.inc);rows=[]
    ub=model.ub.tocoo();eq=model.eq
    for lam in verts:
        d=[sum(int(model.inc[i,j])*lam[j] for j in range(len(lam)))for i in range(model.n)]
        obj=[F(0)]*len(model.eq[0])
        for p in range(model.offset):obj[p]=-sum(int(model.pair[p,j])*lam[j]for j in range(len(lam)))
        for i in range(model.n):obj[model.offset+i*(model.n+1)]=-(1-d[i])/3
        r=linprog(list(map(float,obj)),A_ub=model.ub,b_ub=np.zeros(model.ub.shape[0]),A_eq=eq,b_eq=np.ones(model.n+1),bounds=(0,None))
        if not r.success:raise ValueError(r.message)
        du=[F(float(x)).limit_denominator(10000) for x in r.ineqlin.marginals]
        de=[F(float(x)).limit_denominator(10000) for x in r.eqlin.marginals]
        if max(du)>0 or sum(de)<-1:raise ValueError('upper bound certificate failed')
        lhs=[F(0)]*len(obj)
        for i,j,v in zip(ub.row,ub.col,ub.data):lhs[j]+=int(v)*du[i]
        for i,row in enumerate(eq):
            for j in np.flatnonzero(row):lhs[j]+=int(row[j])*de[i]
        if any(a>b for a,b in zip(lhs,obj)):raise ValueError('dual infeasible after rationalization')
        rows.append({'packing':list(map(str,lam)),'inequality_dual':list(map(str,du)),'equality_dual':list(map(str,de)),'objective_upper':str(-sum(de))})
    result={'status':'PASS','market_size':2,'bases_enumerated':bases,'packing_vertices':len(verts),'fractional_vertices':sum(any(x.denominator>1 for x in lam)for lam in verts),'conclusion':'s_3=0 for every two-label market in the frozen class','certificates':rows}
    Path(__file__).with_name('TWO_LABEL_CERTIFICATES.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='certificates'}))


if __name__=='__main__':run()
