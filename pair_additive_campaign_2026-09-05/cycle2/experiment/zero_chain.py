"""Bounded mechanism probe: zero-small-team path of1,2,3 reduced blocks."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,sys,time
import numpy as np
from scipy.optimize import linprog
import z3
from coupling import ROOT,BASE,require,save,exact_three,float_selector

def build(blocks,small=F(0)):
    m=3*blocks;n=3*m;matrices=[]
    for key in ('A','B','C'):
        mat=[[F(BASE[key][i%3][j%3]) if i//3==j//3 else F(0) for j in range(m)] for i in range(m)]
        matrices.append(mat)
    for b in range(blocks):matrices[1][3*b][3*b+2]=small
    for b in range(blocks-1):matrices[0][3*b+2][3*(b+1)]=F(2)
    matching=[(3*b+i,m+3*b+j,2*m+3*b+k) for b in range(blocks) for i,j,k in ((0,2,2),(1,0,1),(2,1,0))]
    rows=[];weights={}
    for i in range(n):
        a=[F(0)]*n;a[i]=-1;rows.append(dict(label=f'nonnegative_{i}',a=a,b=F(0)))
    for i,j,k in product(range(m),repeat=3):
        w=matrices[0][i][j]+matrices[1][i][k]+matrices[2][j][k]
        a=[F(0)]*n
        for h in (i,m+j,2*m+k):a[h]=-1
        rows.append(dict(label=f'triple_{i}_{j}_{k}',a=a,b=-w));weights[(i,m+j,2*m+k)]=w
    T=blocks*(F(7)+small)
    require(sum(weights[t] for t in matching)==T,'chain integral matching total')
    return n,T,matrices,matching,rows

def check(blocks):
    n,T,matrices,matching,rows=build(blocks)
    A=np.array([r['a'] for r in rows],dtype=float);b=np.array([r['b'] for r in rows],dtype=float)
    feasibility=linprog(np.zeros(n),A_ub=A,b_ub=b,A_eq=[np.ones(n)],b_eq=[float(T)],bounds=[(None,None)]*n,method='highs')
    out=dict(blocks=blocks,m=3*blocks,small_team_weight='0',fixed_total=str(T),matrices=matrices,matching=matching)
    if feasibility.status==2:
        return dict(out,status='infeasible_at_fixed_total_float')
    require(feasibility.success,'chain floatfeasibility')
    xf,xfs=float_selector(A,b,float(T),True)
    print('FLOAT CHAIN',blocks,'secondpositivelevel',min(q for q in xf if q>1e-7),'predicted',str(F(3,blocks+3)),flush=True)
    p=[z3.FreshReal('zerochain') for _ in range(n)]
    cons=[sum(p)==exact_three.Q(T)]+[sum(exact_three.Q(a)*v for a,v in zip(r['a'],p))<=exact_three.Q(r['b']) for r in rows]
    x,xst=exact_three.selector(cons,p,True)
    z,zst=exact_three.selector(cons,p,False)
    H=[exact_three.optimize(cons,v,True) for v in p]
    for point in (x,z):require(sum(point)==T and all(sum(a*v for a,v in zip(r['a'],point))<=r['b'] for r in rows),'exact chaincover failure')
    target=3*blocks
    solver=z3.Solver();solver.set(timeout=60000);solver.add(*cons,p[target]==exact_three.Q(H[target]))
    require(solver.check()==z3.sat,'ideal attainment failed')
    model=solver.model();y=[exact_three.rational(model.eval(v,model_completion=True)) for v in p]
    require(sum(y)==T and all(sum(a*v for a,v in zip(r['a'],y))<=r['b'] for r in rows),'ideal witness not fulltriplecover')
    ratios=[(i,a/h) for i,(a,h) in enumerate(zip(x,H)) if h]
    local=[sum(abs(x[i]-z[i]) for i in t)/sum(x[i] for i in t) if sum(x[i] for i in t) else None for t in matching]
    out.update(status='feasible_at_fixed_total_exact',integral_optimum_certified_by_matching_and_cover=True,x=x,z=z,H=H,min_fraction=min(a for i,a in ratios),x_stages=xst,z_stages=zst,target=target,target_ratio=x[target]/H[target] if H[target] else None,target_ideal_witness=y,rho=sum(abs(a-b) for a,b in zip(x,z))/T,local_team_ratios=local)
    return out

def main():
    records=[]
    for blocks in (1,2,3):
        record=check(blocks);records.append(record)
        save(ROOT/f'zero_chain_{blocks}.json',record)
        print('EXACT CHAIN',blocks,record['status'],record.get('min_fraction'),record.get('target_ratio'),record.get('rho'),flush=True)
    save(ROOT/'zero_chain_summary.json',records)

if __name__=='__main__':main()
