"""One defined interface family: cross-block pair-entry increases at total16."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json,sys,time
import numpy as np
from scipy.optimize import linprog
import z3

ROOT=Path(__file__).resolve().parent
CAMPAIGN=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(CAMPAIGN/'experiment'))
from pilot import float_selector
sys.path.insert(0,str(CAMPAIGN/'experiment'/'verification_dependency'))
import exact_three

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

BASE=json.loads((CAMPAIGN/'experiment'/'reduced_counterexample.json').read_text())
MATRICES=[[[F(BASE[key][i%3][j%3]) if i//3==j//3 else F(0) for j in range(6)] for i in range(6)] for key in ('A','B','C')]
N=18;T=F(16)
MATCHING=[(s+i,6+s+j,12+s+k) for s in (0,3) for i,j,k in ((0,2,2),(1,0,1),(2,1,0))]

def rows_for(changes):
    matrices=[[row[:] for row in M] for M in MATRICES]
    for s,i,j,delta in changes:
        require(i//3!=j//3 and delta>=0,'interface must add a nonnegative cross-block entry')
        matrices[s][i][j]+=delta
    rows=[]
    for i in range(N):
        a=[F(0)]*N;a[i]=-1
        rows.append(dict(label=f'nonnegative_{i}',a=a,b=F(0)))
    teamweights={}
    for i,j,k in product(range(6),repeat=3):
        w=matrices[0][i][j]+matrices[1][i][k]+matrices[2][j][k]
        a=[F(0)]*N
        for h in (i,6+j,12+k):a[h]=-1
        rows.append(dict(label=f'triple_{i}_{j}_{k}',a=a,b=-w))
        teamweights[(i,6+j,12+k)]=w
    require(sum(teamweights[t] for t in MATCHING)==T,'old integral matching must remain16')
    return matrices,rows

def float_check(changes):
    matrices,rows=rows_for(changes)
    A=np.array([r['a'] for r in rows],dtype=float);b=np.array([r['b'] for r in rows],dtype=float)
    feasibility=linprog(np.zeros(N),A_ub=A,b_ub=b,A_eq=[np.ones(N)],b_eq=[float(T)],bounds=[(None,None)]*N,method='highs')
    out=dict(changes=[[s,i,j,str(d)] for s,i,j,d in changes],fixed_total='16')
    if feasibility.status==2:return dict(out,status='infeasible_at_fixed_total_float')
    require(feasibility.success,'float feasibility '+feasibility.message)
    x,xst=float_selector(A,b,float(T),True)
    z,zst=float_selector(A,b,float(T),False)
    H=[]
    for i in range(N):
        opt=linprog(-np.eye(N)[i],A_ub=A,b_ub=b,A_eq=[np.ones(N)],b_eq=[float(T)],bounds=[(None,None)]*N,method='highs')
        require(opt.success,'float ideal failure');H.append(opt.x[i])
    return dict(out,status='feasible_at_fixed_total_float',x=x,z=z,H=H,min_fraction=min(a/h for a,h in zip(x,H) if h>1e-7),rho=sum(abs(a-b) for a,b in zip(x,z))/float(T),x_stages=xst,z_stages=zst)

def exact_check(record):
    changes=[(s,i,j,F(d)) for s,i,j,d in record['changes']]
    matrices,rows=rows_for(changes)
    p=[z3.FreshReal('coupled') for _ in range(N)]
    cons=[sum(p)==exact_three.Q(T)]+[sum(exact_three.Q(a)*v for a,v in zip(r['a'],p))<=exact_three.Q(r['b']) for r in rows]
    solver=z3.Solver();solver.set(timeout=60000);solver.add(*cons)
    status=solver.check();require(status in (z3.sat,z3.unsat),'exact feasibility UNKNOWN')
    out=dict(changes=record['changes'],fixed_total='16',matrices=matrices,matching=MATCHING)
    if status==z3.unsat:return dict(out,status='infeasible_at_fixed_total_exact')
    x,xst=exact_three.selector(cons,p,True);z,zst=exact_three.selector(cons,p,False)
    H=[exact_three.optimize(cons,v,True) for v in p]
    for point in (x,z):
        require(sum(point)==T and all(sum(a*v for a,v in zip(r['a'],point))<=r['b'] for r in rows),'exact corepoint constraint failure')
    frac=min(a/h for a,h in zip(x,H) if h)
    return dict(out,status='feasible_at_fixed_total_exact',integral_optimum_certified_by_matching_and_cover=True,x=x,z=z,H=H,min_fraction=frac,rho=sum(abs(a-b) for a,b in zip(x,z))/T,x_stages=xst,z_stages=zst,strict_contraction=frac<F(5,18))

def save(path,obj):path.write_text(json.dumps(obj,indent=2,default=str)+'\n')

def main():
    started=time.time();records=[]
    grid=[F(1,2),F(1),F(2),F(3)]
    entries=[(s,i,j) for s in range(3) for i in range(6) for j in range(6) if i//3!=j//3]
    manifest=dict(scope='All54 directed cross-block pair entries at increments1/2,1,2,3 unless a certified contraction stops the cycle',entries=entries,grid=grid,maximum_cells=len(entries)*len(grid),fixed_total='16',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CAMPAIGN/'experiment'/'pilot.py',CAMPAIGN/'experiment'/'verification_dependency'/'exact_three.py',CAMPAIGN/'experiment'/'reduced_counterexample.json']})
    save(ROOT/'manifest.json',manifest)
    baseline=float_check([]);exact=exact_check(baseline)
    require(exact['min_fraction']==F(5,18) and exact['rho']==F(11,24),'baseline duplication calibration')
    save(ROOT/'baseline_exact.json',exact)
    print('BASELINE PASS',flush=True)
    for entry in entries:
        for delta in grid:
            record=float_check([(*entry,delta)]);records.append(record)
            if record.get('min_fraction',1)<float(F(5,18))-1e-7:
                result=exact_check(record)
                require(result.get('strict_contraction'),'float contraction did not certify')
                save(ROOT/'candidate_exact.json',result);save(ROOT/'single_entry_records.json',records)
                print('EXACT CONTRACTION',entry,delta,result['min_fraction'],result['rho'],flush=True)
                save(ROOT/'summary.json',dict(status='stopped_at_first_exact_contraction',completed_cells=len(records),maximum_cells=len(entries)*len(grid),elapsed_seconds=time.time()-started))
                return
        if len(records)%24==0:
            save(ROOT/'single_entry_records.json',records)
            print('PROGRESS',len(records),round(time.time()-started,2),flush=True)
    save(ROOT/'single_entry_records.json',records)
    save(ROOT/'summary.json',dict(status='single_entry_grid_complete_no_contraction',completed_cells=len(records),maximum_cells=len(entries)*len(grid),elapsed_seconds=time.time()-started,feasible=sum(r['status']=='feasible_at_fixed_total_float' for r in records)))
    print('COMPLETE',len(records),flush=True)

if __name__=='__main__':main()
