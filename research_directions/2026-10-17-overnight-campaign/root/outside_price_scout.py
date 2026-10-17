"""Discovery only: homogeneous aggregate prices with full outside incentives.

Collocation LP is not an exact all-real certificate. It selects a possible
analytic successor to the elementary golden-ratio construction.
"""
from pathlib import Path
import argparse,json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def solve(n):
    grid=np.linspace(0,1,n+1);K=2*(n+1);rows=[];cols=[];vals=[];rhs=[]
    def add(co,b):
        row=len(rhs)
        for j,v in co.items():
            if v:rows.append(row);cols.append(j);vals.append(v)
        rhs.append(b)
    def combine(terms):
        co={}
        for factor,part in terms:
            for j,v in part.items():co[j]=co.get(j,0)+factor*v
        return co
    add({1:1/grid[1],n+1:1,K:-1},0)
    for j,t in enumerate(grid):
        add({j:1,n+1+j:t,K:-t},0)
    for j in range(n):
        dt=grid[j+1]-grid[j]
        dp={j:-1/dt,j+1:1/dt};dq={n+1+j:-1/dt,n+2+j:1/dt}
        for fraction in [0,.5,1]:
            t=grid[j]+fraction*dt
            p={j:1-fraction,j+1:fraction};q={n+1+j:1-fraction,n+2+j:fraction}
            for a in [0,1]:
                for b in [0,1]:
                    # Nonnegative derivative for either resource, and sum>=1.
                    add(combine([(-1,p),(t*a,dp),(t*t*b,dq)]),0)
                    add(combine([(-1,q),(-a,dp),(-t*b,dq)]),0)
                    add(combine([(-1,p),(-1,q),(-(1-t)*a,dp),(-t*(1-t)*b,dq)]),-1)
    mat=coo_matrix((vals,(rows,cols)),shape=(len(rhs),K+1)).tocsr()
    eq=coo_matrix(([1,1,-1],([0,1,1],[0,n,2*n+1])),shape=(2,K+1)).tocsr()
    obj=np.zeros(K+1);obj[K]=1
    result=linprog(obj,A_ub=mat,b_ub=rhs,A_eq=eq,b_eq=[0,0],bounds=(0,None),options={'time_limit':120})
    out={'status':int(result.status),'message':result.message,'n_intervals':n,'scope':'floating collocation discovery only'}
    if result.success:
        out.update(optimum=float(result.fun),grid=grid.tolist(),p=result.x[:n+1].tolist(),q=result.x[n+1:2*n+2].tolist())
        Path(__file__).with_name(f'outside_price_collocation_{n}.json').write_text(json.dumps(out,indent=2)+'\n')
        out={k:v for k,v in out.items() if k not in ['grid','p','q']}
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=100);a=ap.parse_args()
    print(json.dumps(solve(a.n),indent=2))
