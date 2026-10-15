"""Floating discovery LPs for incidence-resource production; no theorem claim."""
from itertools import product
from fractions import Fraction
from pathlib import Path
import json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def normalized(v,p):
    first=next(x for x in v if x%p)
    inv=pow(first,-1,p)
    return tuple(x*inv%p for x in v)
class UF:
    def __init__(self,n):self.p=list(range(n))
    def find(self,x):
        while self.p[x]!=x:self.p[x]=self.p[self.p[x]];x=self.p[x]
        return x
    def union(self,a,b):
        a=self.find(a);b=self.find(b)
        if a!=b:self.p[b]=a

def setup(q):
    pts=sorted({normalized(x,q) for x in product(range(q),repeat=3) if any(x)})
    n=len(pts);ix={x:i for i,x in enumerate(pts)}
    transforms=[lambda x:(x[1],x[0],x[2]),lambda x:(x[0],x[2],x[1]),
                lambda x:((x[0]+x[1])%q,x[1],x[2])]
    perms=[[ix[normalized(t(x),q)] for x in pts] for t in transforms]
    inc=np.array([[sum(a*b for a,b in zip(x,l))%q==0 for l in pts] for x in pts],dtype=np.int16)
    if not np.all(inc.sum(axis=0)==q+1):raise RuntimeError('bad projective plane')
    M=1<<n;state=UF(M);pairs=UF(M*n)
    for perm in perms:
        maps=[0]*M
        for H in range(1,M):
            bit=H&-H;i=bit.bit_length()-1;maps[H]=maps[H^bit]|(1<<perm[i])
        for H,J in enumerate(maps):
            state.union(H,J)
            for i,j in enumerate(perm):pairs.union(H*n+i,J*n+j)
    reps=sorted({state.find(H) for H in range(M)})
    roots=sorted({pairs.find(x) for x in range(M*n)});vid={r:i for i,r in enumerate(roots)}
    variables=np.array([vid[pairs.find(x)] for x in range(M*n)]).reshape(M,n)
    bits=np.array([[(H>>i)&1 for i in range(n)] for H in range(M)],dtype=np.int16)
    transitions=sorted({(int(variables[H,i]),int(variables[H|(1<<i),i]))
                        for H in reps for i in range(n) if not((H>>i)&1)})
    return n,inc,reps,variables,bits,transitions,len(roots)

def solve(q,data,high):
    n,inc,reps,variables,bits,transitions,nvar=data
    rows=[];cols=[];vals=[];rhs=[]
    def row(coefs,b):
        r=len(rhs)
        for j,a in coefs.items():
            if a:rows.append(r);cols.append(j);vals.append(a)
        rhs.append(b)
    for H in reps:
        reports=1+(high-1)*bits[H]
        values=((bits*reports)@inc).min(axis=1)
        labels=variables[H];local=sorted(set(int(x) for x in labels))
        counts=np.stack([bits[:,labels==v].sum(axis=1) for v in local],axis=1)
        strongest={}
        for C in range(1,len(bits)):
            key=tuple(int(x) for x in counts[C]);worth=int(values[C])
            if worth>strongest.get(key,-1):strongest[key]=worth
        for key,worth in strongest.items():row({v:-a for v,a in zip(local,key)},-worth)
        budget={v:int((labels==v).sum()) for v in local};budget[nvar]=-int(values[-1]);row(budget,0)
    for left,right in transitions:
        if left!=right:row({left:1,right:-1},0)
    A=coo_matrix((vals,(rows,cols)),shape=(len(rhs),nvar+1)).tocsr()
    c=np.zeros(nvar+1);c[-1]=1
    start=time.monotonic();res=linprog(c,A_ub=A,b_ub=np.array(rhs),bounds=[(0,None)]*nvar+[(1,None)],method='highs')
    out={'q':q,'n':n,'resources':n,'high':high,'profile_orbits':len(reps),
         'payment_orbits':nvar,'constraints':len(rhs),'success':bool(res.success),
         'factor':float(res.fun) if res.success else None,
         'rational_guess':str(Fraction(float(res.fun)).limit_denominator(1000000)) if res.success else None,
         'seconds':time.monotonic()-start,'scope':'floating restricted-domain discovery only'}
    print(json.dumps(out),flush=True)
    return out

if __name__=='__main__':
    out=[]
    for q in (2,3):
        data=setup(q)
        for high in (2,3,5,10,30):out.append(solve(q,data,high))
    Path(__file__).with_name('PROJECTIVE_PLANE_DISCOVERY.json').write_text(json.dumps(out,indent=2)+'\n')
