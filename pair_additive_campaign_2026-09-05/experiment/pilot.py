"""Bounded pair-additive triple pilot; float discovery, exact nominated checks."""
from pathlib import Path
from itertools import permutations, product
from fractions import Fraction as F
import argparse, hashlib, json, platform, random, sys, time
import numpy as np
import scipy
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parent
VERIFICATION = ROOT / 'verification_dependency'
sys.path.insert(0, str(VERIFICATION))
import exact_three
import z3

def require(ok, msg):
    if not ok:
        raise RuntimeError(msg)

def tensor(A, B, C):
    m = len(A)
    require(all(len(M) == m and all(len(row) == m and all(isinstance(v, int) and v >= 0 for v in row) for row in M) for M in (A,B,C)), 'invalid matrices')
    return [[[A[i][j] + B[i][k] + C[j][k] for k in range(m)] for j in range(m)] for i in range(m)]

def perfect_total(w):
    m = len(w)
    return max((sum(w[i][b[i]][c[i]] for i in range(m)), b, c) for b,c in product(permutations(range(m)), repeat=2))

def float_selector(A, b, T, upward):
    n = A.shape[1]
    fixed = {}
    stages = []
    while len(fixed) < n:
        free = [i for i in range(n) if i not in fixed]
        eq = [np.ones(n)] + [np.eye(n)[i] for i in fixed]
        rhs = [T] + list(fixed.values())
        AA = np.column_stack((A, np.zeros(len(b))))
        caps = []
        for i in free:
            row = np.zeros(n+1)
            row[i] = -1 if upward else 1
            row[-1] = 1 if upward else -1
            caps.append(row)
        objective = np.zeros(n+1); objective[-1] = -1 if upward else 1
        result = linprog(objective, A_ub=np.vstack((AA,caps)), b_ub=np.r_[b,np.zeros(len(caps))], A_eq=np.column_stack((eq,np.zeros(len(eq)))), b_eq=rhs, bounds=[(0,None)]*n+[(None,None)], method='highs')
        require(result.success, 'float level LP failure: '+result.message)
        value = result.x[-1]
        face = [np.eye(n)[i]*(-1 if upward else 1) for i in free]
        fb = [-value if upward else value]*len(free)
        pinned = []
        for i in free:
            objective = np.eye(n)[i]*(-1 if upward else 1)
            probe = linprog(objective, A_ub=np.vstack((A,face)), b_ub=np.r_[b,fb], A_eq=eq, b_eq=rhs, bounds=(0,None), method='highs')
            require(probe.success, 'float face probe failure: '+probe.message)
            optimum = probe.x[i]
            if abs(optimum-value) <= 1e-7*max(1,T):
                pinned.append(i)
        require(pinned, 'no coordinate fixed on float face')
        fixed.update({i:value for i in pinned})
        stages.append({'level':value,'players':pinned})
    return [fixed[i] for i in range(n)], stages

def float_check(A, B, C, label):
    w = tensor(A,B,C); m = len(w); n = 3*m
    T, p, q = perfect_total(w)
    record = dict(label=label,m=m,A=A,B=B,C=C,T=T,optimal_matching=[[i,p[i],q[i]] for i in range(m)])
    if T == 0:
        return dict(record,status='zero_total')
    rows=[]; rhs=[]
    for i,j,k in product(range(m),repeat=3):
        row=np.zeros(n); row[[i,m+j,2*m+k]]=-1
        rows.append(row); rhs.append(-w[i][j][k])
    rows=np.array(rows); rhs=np.array(rhs)
    feasible=linprog(np.zeros(n),A_ub=rows,b_ub=rhs,A_eq=[np.ones(n)],b_eq=[T],bounds=(0,None),method='highs')
    if feasible.status==2:
        return dict(record,status='empty_core_float')
    require(feasible.success,'float core status failure')
    x,xst=float_selector(rows,rhs,T,True)
    z,zst=float_selector(rows,rhs,T,False)
    H=[]
    for i in range(n):
        opt=linprog(-np.eye(n)[i],A_ub=rows,b_ub=rhs,A_eq=[np.ones(n)],b_eq=[T],bounds=(0,None),method='highs')
        require(opt.success,'float coordinate ideal failure')
        H.append(opt.x[i])
    ratio=min(a/h for a,h in zip(x,H) if h>1e-7)
    rho=sum(abs(a-b) for a,b in zip(x,z))/T
    return dict(record,status='nonempty_core_float',x=x,z=z,H=H,min_fraction=ratio,rho=rho,x_stages=xst,z_stages=zst)

def sorted_expr(items):
    items=list(items)
    for end in range(1,len(items)):
        for j in range(end,0,-1):
            a,b=items[j-1],items[j]
            items[j-1],items[j]=z3.If(a<=b,a,b),z3.If(a<=b,b,a)
    return items

def lex_better(expressions, target, upward):
    prefix=[]; alternatives=[]
    for e,v in zip(expressions,target):
        alternatives.append(z3.And(*prefix,e>exact_three.Q(v) if upward else e<exact_three.Q(v)))
        prefix.append(e==exact_three.Q(v))
    return z3.Or(*alternatives)

def verdict(cons, expected):
    solver=z3.Solver(); solver.set(timeout=60000); solver.add(*cons)
    status=solver.check(); require(status==expected,'independent certificate: '+str(status))
    return str(status)

def exact_check(record, full=True):
    w=tensor(record['A'],record['B'],record['C'])
    result=exact_three.check(w,full=full)
    require(F(result['T'])==record['T'],'matching enumeration/DP total disagreement')
    result.update({key:record[key] for key in ('label','m','A','B','C','optimal_matching')})
    if not result['core_nonempty'] or not F(result['T']):
        return result
    p,cons,T,feasible=exact_three.core(w,full=full)
    require(feasible,'inconsistent exact feasibility')
    order=sorted_expr(p)
    certificate={}
    for name,upward in [('Lmin',True),('Lmax',False)]:
        point=list(map(F,result[name]))
        substitutions=list(zip(p,map(exact_three.Q,point)))
        require(all(z3.is_true(z3.simplify(z3.substitute(c,*substitutions))) for c in cons),'candidate violates coalition constraints')
        certificate[name+'_strict_sorted_improvement']=verdict(cons+[lex_better(order if upward else order[::-1],sorted(point,reverse=not upward),upward)],z3.unsat)
    H=list(map(F,result['core_maxima']))
    certificate['coordinate_ideal_bounds']=[verdict(cons+[p[i]>exact_three.Q(h)],z3.unsat) for i,h in enumerate(H)]
    certificate['coordinate_ideal_attainment']=[verdict(cons+[p[i]==exact_three.Q(h)],z3.sat) for i,h in enumerate(H)]
    x=list(map(F,result['Lmin']))
    result['violates_one_third']=any(3*a<h for a,h in zip(x,H))
    result['violates_four_thirds']=F(result['rho'])>F(4,3)
    result['independent_certificates']=certificate
    return result

def player_additive(sectors):
    m=len(sectors[0])
    # alpha+beta carried by A; gamma carried by B, C=0.
    return [[sectors[0][i]+sectors[1][j] for j in range(m)] for i in range(m)], [[sectors[2][k] for k in range(m)] for i in range(m)], [[0]*m for _ in range(m)]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--per-size',type=int,default=192);parser.add_argument('--seed',type=int,default=20260905);args=parser.parse_args()
    started=time.time();rng=random.Random(args.seed);records=[];exact=[]
    for old in ('PASS', 'pilot_summary.json', 'exact_counterexample_candidates.json', 'screen_records.json'):
        (ROOT/old).unlink(missing_ok=True)
    (ROOT/'RUNNING').write_text('Pair-additive pilot started\n')
    for m in (2,3):
        sectors=[[2]+[1]*(m-1),[1]+[0]*(m-1),[0]*m]
        record=float_check(*player_additive(sectors),label=f'calibration_sharp_player_additive_m{m}')
        checked=exact_check(record)
        require(F(checked['rho'])==F(4*m,3*(m+2)),'additive rho calibration failed')
        require(F(checked['min_coordinate_fraction'])==F(1,3),'additive fraction calibration failed')
        records.append(record);exact.append(checked)
    print('PASS exact additive calibrations',flush=True)
    for m in (2,3):
        best_ratio=1.;best_rho=0.
        for case in range(args.per_size):
            mode=case%4
            if mode==0:
                matrices=[[[rng.randrange(2) for _ in range(m)] for _ in range(m)] for _ in range(3)]
            elif mode==1:
                matrices=[[[rng.randrange(7) for _ in range(m)] for _ in range(m)] for _ in range(3)]
            elif mode==2:
                matrices=[[[rng.randrange(1,10) if rng.random()<.35 else 0 for _ in range(m)] for _ in range(m)] for _ in range(3)]
            else:
                sectors=[[rng.randrange(5) for _ in range(m)] for _ in range(3)]
                matrices=list(player_additive(sectors))
                for _ in range(1+m):
                    matrices[rng.randrange(3)][rng.randrange(m)][rng.randrange(m)]+=rng.randrange(1,5)
            label=f'm{m}_case{case}_mode{mode}'
            record=float_check(*matrices,label=label);records.append(record)
            if record['status']=='nonempty_core_float':
                if record['min_fraction']<best_ratio-1e-7 or record['rho']>best_rho+1e-7:
                    best_ratio=min(best_ratio,record['min_fraction']);best_rho=max(best_rho,record['rho'])
                    print('FRONTIER',label,'fraction',record['min_fraction'],'rho',record['rho'],flush=True)
                if record['min_fraction']<1/3-1e-7 or record['rho']>4/3+1e-7:
                    checked=exact_check(record);exact.append(checked)
                    (ROOT/'exact_counterexample_candidates.json').write_text(json.dumps(exact,indent=2)+'\n')
                    require(checked['violates_one_third'] or checked['violates_four_thirds'],'float candidate failed exact certification')
                    print('EXACT COUNTEREXAMPLE',label,checked['min_coordinate_fraction'],checked['rho'],flush=True)
                    # A decisive new mechanism ends discovery; avoid a blind census.
                    (ROOT/'screen_records.json').write_text(json.dumps(records,indent=2)+'\n')
                    finish(records,exact,args,started,'exact_counterexample')
                    return
            if case%32==31:
                print('PROGRESS',m,case+1,round(time.time()-started,2),flush=True)
                (ROOT/'screen_records.json').write_text(json.dumps(records,indent=2)+'\n')
    nominated=[]
    for m in (2,3):
        candidates=[r for r in records if r['m']==m and r['status']=='nonempty_core_float' and not r['label'].startswith('calibration')]
        nominated.extend(sorted(candidates,key=lambda r:r['min_fraction'])[:2])
        nominated.extend(sorted(candidates,key=lambda r:-r['rho'])[:2])
    seen={r['label'] for r in exact}
    for record in nominated:
        if record['label'] not in seen:
            print('EXACT NOMINEE',record['label'],flush=True)
            exact.append(exact_check(record));seen.add(record['label'])
    (ROOT/'screen_records.json').write_text(json.dumps(records,indent=2)+'\n')
    finish(records,exact,args,started,'bounded_screen_complete')

def finish(records,exact,args,started,status):
    counts={s:sum(r['status']==s for r in records) for s in sorted({r['status'] for r in records})}
    summary=dict(status=status,seed=args.seed,per_size_limit=args.per_size,elapsed_seconds=time.time()-started,counts=counts,exact_records=exact,versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,z3=z3.get_version_string()),reused_source=dict(path=str(VERIFICATION/'exact_three.py'),sha256=hashlib.sha256((VERIFICATION/'exact_three.py').read_bytes()).hexdigest()))
    (ROOT/'pilot_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'RUNNING').unlink();(ROOT/'PASS').write_text(status+'\n')
    print('PASS',status,counts,flush=True)

if __name__=='__main__':
    main()
