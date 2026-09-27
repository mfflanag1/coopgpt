"""Bounded deterministic overlap/branch challenge to a1/6 protection bound."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json,sys,time
import numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint
import z3

ROOT=Path(__file__).resolve().parent
CAMPAIGN=ROOT.parents[1]
if not (CAMPAIGN/'experiment'/'reduced_counterexample.json').is_file():
    CAMPAIGN=Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/pair_additive_campaign_2026-09-05')
sys.path.insert(0,str(CAMPAIGN/'experiment'))
# The current file is itself pilot.py, so load the reviewed dependency by path.
import importlib.util
spec=importlib.util.spec_from_file_location('reviewed_float_pilot',CAMPAIGN/'experiment'/'pilot.py')
reviewed=importlib.util.module_from_spec(spec);spec.loader.exec_module(reviewed)
float_selector=reviewed.float_selector
sys.path.insert(0,str(CAMPAIGN/'experiment'/'verification_dependency'))
import exact_three
BASE=json.loads((CAMPAIGN/'experiment'/'reduced_counterexample.json').read_text())

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def save(name,obj):(ROOT/name).write_text(json.dumps(obj,indent=2,default=str)+'\n')

def build(blocks,changes):
    m=3*blocks;n=3*m
    matrices=[[[int(BASE[key][i%3][j%3]) if i//3==j//3 else 0 for j in range(m)] for i in range(m)] for key in ('A','B','C')]
    for pair,i,j,value in changes:
        require(i//3!=j//3 and value>=0,'only cross-block nonnegative increments')
        matrices[pair][i][j]+=value
    teams=list(product(range(m),repeat=3))
    w=np.array([matrices[0][i][j]+matrices[1][i][k]+matrices[2][j][k] for i,j,k in teams],dtype=float)
    incidence=np.zeros((n,len(teams)))
    for t,(i,j,k) in enumerate(teams):incidence[[i,m+j,2*m+k],t]=1
    return matrices,teams,w,incidence

def matching_at_fractional_total(teams,w,incidence,cover,total):
    # The dual of the covering LP is a matching relaxation. Integral dual
    # weights immediately provide a matching, with no integer search.
    dual=-cover.ineqlin.marginals
    if all(abs(a-round(a))<1e-7 for a in dual):
        chosen=[j for j,a in enumerate(dual) if round(a)==1]
        if len(chosen)*3==incidence.shape[0] and all(abs(a-1)<1e-7 for a in incidence[:,chosen].sum(axis=1)):
            value=sum(int(w[j]) for j in chosen)
            if abs(value-total)<1e-7:return chosen,'integral_cover_dual'
    if abs(total-round(total))>1e-7:return None,'noninteger_fractional_optimum_float'
    result=milp(c=-w,integrality=np.ones(len(w)),bounds=Bounds(np.zeros(len(w)),np.ones(len(w))),constraints=LinearConstraint(incidence,np.ones(incidence.shape[0]),np.ones(incidence.shape[0])),options={'time_limit':5.0,'mip_rel_gap':0.0})
    if result.x is None:return None,'integer_matching_no_witness_status_'+str(result.status)
    if any(abs(a-round(a))>1e-6 for a in result.x):return None,'integer_solver_nonintegral_output'
    chosen=[j for j,a in enumerate(result.x) if round(a)==1]
    if any(abs(a-1)>1e-7 for a in incidence[:,chosen].sum(axis=1)):return None,'integer_matching_invalid_coverage'
    value=sum(int(w[j]) for j in chosen)
    if abs(value-total)<1e-7:return chosen,'integer_matching_matches_cover'
    return None,'integer_fractional_gap_float' if result.status==0 else 'integer_search_unresolved_status_'+str(result.status)

def float_check(label,blocks,changes):
    matrices,teams,w,incidence=build(blocks,changes);n=incidence.shape[0]
    cover=linprog(np.ones(n),A_ub=-incidence.T,b_ub=-w,bounds=(0,None),method='highs')
    require(cover.success,'cover LP failure')
    fractional_total=cover.fun
    chosen,admission=matching_at_fractional_total(teams,w,incidence,cover,fractional_total)
    record=dict(label=label,blocks=blocks,changes=changes,fractional_total_float=fractional_total,admission=admission)
    if chosen is None:return dict(record,status='not_admitted_by_float_matching_cover_test')
    T=sum(int(w[j]) for j in chosen)
    if T==0:return dict(record,status='zero_total')
    A=-incidence.T;b=-w
    x,xst=float_selector(A,b,T,True)
    z,zst=float_selector(A,b,T,False)
    H=[]
    for i in range(n):
        result=linprog(-np.eye(n)[i],A_ub=A,b_ub=b,A_eq=[np.ones(n)],b_eq=[T],bounds=(0,None),method='highs')
        require(result.success,'ideal LP failure');H.append(result.x[i])
    local=[]
    for j in chosen:
        ids=np.flatnonzero(incidence[:,j]);weight=int(w[j])
        local.append(sum(abs(x[i]-z[i]) for i in ids)/weight if weight else None)
    return dict(record,status='admitted_nonempty_core_float',T=T,matching=[list(teams[j]) for j in chosen],x=x,z=z,H=H,x_stages=xst,z_stages=zst,min_fraction=min(a/h for a,h in zip(x,H) if h>1e-7),rho=sum(abs(a-b) for a,b in zip(x,z))/T,local_team_ratios=local)

def exact_check(record):
    matrices,teams,w,incidence=build(record['blocks'],record['changes']);n=incidence.shape[0];m=n//3;T=F(record['T'])
    p=[z3.FreshReal('overlap') for _ in range(n)]
    cons=[v>=0 for v in p]+[sum(p)==exact_three.Q(T)]
    cons.extend(p[i]+p[m+j]+p[2*m+k]>=int(weight) for (i,j,k),weight in zip(teams,w))
    selected=[(i,m+j,2*m+k) for i,j,k in record['matching']]
    require(sorted(i for t in selected for i in t)==list(range(n)),'exact matching does not partition players')
    require(sum(matrices[0][i][j]+matrices[1][i][k]+matrices[2][j][k] for i,j,k in record['matching'])==T,'exact matching total mismatch')
    x,xst=exact_three.selector(cons,p,True);z,zst=exact_three.selector(cons,p,False)
    H=[exact_three.optimize(cons,v,True) for v in p]
    for name,point in [('x',x),('z',z)]:
        require(all(v>=0 for v in point) and sum(point)==T,name+' total/nonnegative')
        require(all(point[i]+point[m+j]+point[2*m+k]>=int(weight) for (i,j,k),weight in zip(teams,w)),name+' exact triplecover')
    target=min((i for i in range(n) if H[i]),key=lambda i:x[i]/H[i])
    solver=z3.Solver();solver.set(timeout=60000);solver.add(*cons,p[target]==exact_three.Q(H[target]))
    require(solver.check()==z3.sat,'ideal point missing')
    model=solver.model();y=[exact_three.rational(model.eval(v,model_completion=True)) for v in p]
    require(all(v>=0 for v in y) and sum(y)==T and all(y[i]+y[m+j]+y[2*m+k]>=int(weight) for (i,j,k),weight in zip(teams,w)),'ideal point not exact fullcover')
    fraction=x[target]/H[target]
    return dict(label=record['label'],blocks=record['blocks'],changes=record['changes'],matrices=matrices,T=T,matching=record['matching'],status='exact_nonempty_core',x=x,z=z,H=H,x_stages=xst,z_stages=zst,target=target,target_ideal_witness=y,min_fraction=fraction,rho=sum(abs(a-b) for a,b in zip(x,z))/T,violates_one_sixth=fraction<F(1,6),local_team_ratios=[sum(abs(x[i]-z[i]) for i in ids)/sum(x[i] for i in ids) if sum(x[i] for i in ids) else None for ids in selected])

def planned_cases():
    cases=[]
    for i,j,k in product(range(3),repeat=3):
        for strength in (1,2,3):
            changes=[(0,i,3+j,strength),(1,i,6+k,strength),(2,3+j,6+k,strength)]
            cases.append((f'triangle_roles{i}{j}{k}_weight{strength}',changes))
    fork=[(0,2,3,2),(0,2,6,2)]
    forbidden={(s,i,j) for s,i,j,d in fork}
    for pair in range(3):
        for i,j in product(range(9),repeat=2):
            if i//3==j//3 or (pair,i,j) in forbidden:continue
            for delta in (1,2):cases.append((f'fork_plus_{pair}_{i}_{j}_delta{delta}',fork+[(pair,i,j,delta)]))
    require(len(cases)==401,'planned case count')
    return cases

def main():
    started=time.monotonic();cases=planned_cases();records=[];exact=[]
    save('manifest.json',dict(scope='Deterministic three-block overlapping interfaces and branching; stop at exact ratio<1/6 or15minute walltime, maximum401cells',max_cells=len(cases),max_wall_seconds=900,cases=[dict(label=l,changes=c) for l,c in cases],source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CAMPAIGN/'experiment'/'pilot.py',CAMPAIGN/'experiment'/'verification_dependency'/'exact_three.py',CAMPAIGN/'experiment'/'reduced_counterexample.json']}))
    nine=float_check('calibration_nine_player',1,[]);nine_exact=exact_check(nine)
    require(nine_exact['min_fraction']==F(5,18),'nineplayer calibration')
    chain=float_check('calibration_q3_path',3,[(0,2,3,2),(0,5,6,2)]);chain_exact=exact_check(chain)
    require(chain_exact['x'][13]==F(2,3) and chain_exact['H'][13]==2,'q3 internal e calibration')
    exact.extend((nine_exact,chain_exact));save('calibrations.json',exact)
    print('CALIBRATIONS PASS',round(time.monotonic()-started,2),flush=True)
    best=F(1);status='completed_initial_gate'
    for index,(label,changes) in enumerate(cases):
        record=float_check(label,3,changes);records.append(record)
        if record['status']=='admitted_nonempty_core_float':
            if record['min_fraction']<float(best)-1e-7:
                best=F(record['min_fraction']).limit_denominator(10**6)
                print('FRONTIER',index+1,label,'ratio',record['min_fraction'],'T',record['T'],flush=True)
            if record['min_fraction']<1/6-1e-7:
                candidate=exact_check(record)
                save('candidate_exact.json',candidate)
                require(candidate['violates_one_sixth'],'float candidate failed exact certification')
                print('EXACT BELOW ONE SIXTH',label,candidate['min_fraction'],flush=True)
                status='stopped_at_exact_counterexample';break
        if (index+1)%16==0:
            save('records.json',records);print('PROGRESS',index+1,round(time.monotonic()-started,2),flush=True)
        if time.monotonic()-started>=900:
            status='bounded_walltime_stop';break
    save('records.json',records)
    admitted=[r for r in records if r['status']=='admitted_nonempty_core_float']
    if status!='stopped_at_exact_counterexample' and admitted:
        bestrecord=min(admitted,key=lambda r:r['min_fraction'])
        print('EXACT BEST NOMINEE',bestrecord['label'],flush=True)
        nominated=exact_check(bestrecord);save('best_nominee_exact.json',nominated)
    save('summary.json',dict(status=status,completed_cells=len(records),planned_cells=len(cases),elapsed_seconds=time.monotonic()-started,admitted=len(admitted),admission_counts={key:sum(r['admission']==key for r in records) for key in sorted({r['admission'] for r in records})},minimum_observed_fraction=float(best)))
    print('FINISHED',status,len(records),'admitted',len(admitted),flush=True)

if __name__=='__main__':main()
