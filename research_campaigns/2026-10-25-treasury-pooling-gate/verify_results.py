"""Independent source-to-result audit. Does not import either experiment script.

Recomputes all saved risk/constraint/calibration quantities. Certifies selected
full-lex stages with charges as LP variables, independently of the savings code.
Both implementations use SciPy/HiGHS: this is not a separate solver certificate.
"""
from pathlib import Path
from datetime import date
from statistics import NormalDist
import csv, hashlib, json, math
import numpy as np
from scipy.optimize import linprog

P = Path(__file__).parent
RAW = P.parent/'2026-10-24-risk-geometry/data/gsw-vintage-2026-10-24.csv'
SHA = '59a802aa6f1661c3beb37a7880706627db2913601920e3be3c3dcdd6b5321278'
Z = NormalDist().inv_cdf(.975)
K = math.exp(-Z*Z/2)/math.sqrt(2*math.pi)/.025
TOL = 1e-7
Q = np.array([[100,0],[0,80],[60,-30],[-80,0],[0,-70],[-60,20]], float)
COUNTS = {'allocation_vectors':0, 'coalition_inequalities':0, 'charge_lp_stages':0, 'cap_feasibility_lps':0}
MAX = {'saved_scaled_error':0., 'constraint_violation_B':0., 'lex_level_error_B':0.}

def close(actual, expected, scale=1., tol=1e-9):
    err = float(np.max(np.abs(np.asarray(actual)-np.asarray(expected)))) / scale
    MAX['saved_scaled_error'] = max(MAX['saved_scaled_error'], err)
    assert err < tol, (err, actual, expected)

def source():
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == SHA
    text = RAW.read_text()
    rows = list(csv.DictReader(text[text.index('Date,'):].splitlines()))
    assert len({r['Date'] for r in rows}) == len(rows)
    rows = sorted(rows, key=lambda r:r['Date'])
    strict, available, invalid, omitted = [], [], [], []
    last_raw = last_valid = None
    for r in rows:
        d = date.fromisoformat(r['Date'])
        if not date(2009,12,1) <= d <= date(2025,12,31): continue
        try:
            v = tuple(float(r[x]) for x in ('SVENY02','SVENY10'))
            valid = all(math.isfinite(x) and x > -900 for x in v)
        except ValueError:
            valid = False
        if not valid:
            invalid.append(str(d)); last_raw = None; continue
        current = (d, v)
        for prev, target in [(last_raw, strict),(last_valid,available)]:
            if prev is not None and (d-prev[0]).days <= 7 and d >= date(2010,1,1):
                target.append((d, [(v[j]-prev[1][j])*100 for j in (0,1)]))
        if last_raw is None and last_valid is not None and (d-last_valid[0]).days <=7 and d>=date(2010,1,1):
            omitted.append({'date':str(d),'prior_valid_date':str(last_valid[0]),
                            'interval_days':(d-last_valid[0]).days,
                            'dy_bp':[(v[j]-last_valid[1][j])*100 for j in (0,1)]})
        last_raw = last_valid = current
    audit = {'raw_sha256':SHA,'invalid_source_dates':invalid,'additional_differences_dropped_by_strict_rule':omitted,
             'strict_training_n':sum(d.year<2019 for d,_ in strict),
             'available_training_n':sum(d.year<2019 for d,_ in available),
             'strict_holdout_n':sum(d.year>=2019 for d,_ in strict),
             'available_holdout_n':sum(d.year>=2019 for d,_ in available),
             'interpretation':'Invalid rows are not all asserted to be holidays. Available quotes are differenced without interpolation. Strict primary retained unchanged.'}
    (P/'data_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    return strict, available

def covariance(x):
    centered=x-x.mean(axis=0)
    return centered.T@centered/(len(x)-1)

def costs(q,cov):
    n=len(q);M=np.array([[int(i in s) for i in range(n)] for s in
                        [set(i for i in range(n) if mask & (1<<i)) for mask in range(1,2**n)]],float)
    def risk(vec): return K*math.sqrt(max(0,float(vec@cov@vec)))
    c=np.array([risk(vec) for vec in M@q]); b=np.array([risk(vec) for vec in q])
    return M,c,b,b.sum(),c[-1],b.sum()-c[-1]

def charge_lp_base(M,c,b,B,r,T,cap):
    n=len(b); m=n if cap is None else 2*n
    A=np.zeros((len(M)+(n+1 if cap is not None else 0),m));rhs=np.r_[c/B,np.zeros(n+1) if cap is not None else []]
    A[:len(M),:n]=M
    if cap is not None:
        for i in range(n): A[len(M)+i,i]=-1; A[len(M)+i,n+i]=-1
        A[-1,n:]=1;rhs[-1]=cap*T/B
    E=np.zeros((1,m));E[0,:n]=1
    bounds=[(None,float(bi/B)) for bi in b]+([] if cap is None else [(0,None)]*n)
    return A,rhs,E,np.array([r/B]),bounds

def lp(obj,A,rhs,E,f,bounds):
    result=linprog(obj,A_ub=A,b_ub=rhs,A_eq=E,b_eq=f,bounds=bounds,
                   method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    assert result.status in (0,2),result.message
    return result

def audit_lex(rec,kind,cap,M,c,b,B,r,T):
    A,rhs,E,f,bounds=charge_lp_base(M,c,b,B,r,T,cap);m=len(bounds);n=len(b); active=set(range(n))
    for stage in rec['stages']:
        obj=np.zeros(m+1);obj[-1]=-1 if kind=='ascending' else 1
        aa=np.zeros((len(A)+len(active),m+1));aa[:len(A),:m]=A
        rr=list(rhs)
        for row,i in enumerate(sorted(active),start=len(A)):
            # Savings y=b-k: y>=t becomes k+t<=b; y<=t becomes -k-t<=-b.
            sign=1 if kind=='ascending' else -1
            aa[row,i]=sign;aa[row,-1]=sign;rr.append(sign*b[i]/B)
        ee=np.zeros((1,m+1));ee[:,:m]=E
        fit=lp(obj,aa,np.array(rr),ee,f,bounds+[(0,None)])
        assert fit.success
        t=float(fit.x[-1]); expected=stage['level_fraction_B']
        MAX['lex_level_error_B']=max(MAX['lex_level_error_B'],abs(t-expected))
        assert abs(t-expected)<TOL
        face=list(bounds)
        for i in active:
            lo,hi=face[i]
            if kind=='ascending':hi=min(hi,b[i]/B-t)
            else:lo=max(-np.inf if lo is None else lo,b[i]/B-t)
            face[i]=(lo,hi)
        fixed=set(stage['fixed_indices']);assert fixed and fixed<=active
        independently_fixed=set()
        for i in active:
            e=np.zeros(m);e[i]=1 if kind=='ascending' else -1
            extremum=lp(e,A,rhs,E,f,face);assert extremum.success
            if abs(extremum.x[i]-(b[i]/B-t))<=1e-8:independently_fixed.add(i)
        assert independently_fixed==fixed,(kind,fixed,independently_fixed)
        for i in fixed:face[i]=(b[i]/B-t,b[i]/B-t)
        active-=fixed;bounds=face;COUNTS['charge_lp_stages']+=1
    assert not active
    close([bounds[i][0] for i in range(n)],np.array(rec['charges_thousand_dollars'])/B,tol=TOL)

def audit_record(record,certify_stages=False):
    q=np.array(record['q']);cov=np.array(record['covariance_bps2']);M,c,b,B,r,T=costs(q,cov)
    close([record['B_thousand_dollars'],record['residual_risk_thousand_dollars'],record['savings_T_thousand_dollars']],[B,r,T],B)
    for key,caprec in record['caps'].items():
        cap=None if key=='unrestricted' else float(key)
        A,rhs,E,f,bounds=charge_lp_base(M,c,b,B,r,T,cap)
        feasible=lp(np.zeros(len(bounds)),A,rhs,E,f,bounds).success
        COUNTS['cap_feasibility_lps']+=1
        assert feasible==caprec['feasible'],(key,feasible)
        if not feasible:continue
        ys=[]
        for kind in ('ascending','descending'):
            rec=caprec[kind];y=np.array(rec['y_thousand_dollars']);charge=np.array(rec['charges_thousand_dollars'])
            close(y+charge,b,B);ys.append(y)
            violation=max(0.,float(np.max(M@charge-c))/B,abs(charge.sum()-r)/B,-float(y.min())/B)
            credit=np.maximum(-charge,0).sum()
            if cap is not None:violation=max(violation,(credit-cap*T)/B)
            assert violation<TOL;MAX['constraint_violation_B']=max(MAX['constraint_violation_B'],violation)
            close(rec['credit_demand_fraction_T'],credit/T)
            COUNTS['allocation_vectors']+=1;COUNTS['coalition_inequalities']+=len(M)
            if certify_stages:audit_lex(rec,kind,cap,M,c,b,B,r,T)
        close(caprec['reassigned_fraction_T'],np.abs(ys[0]-ys[1]).sum()/(2*T))
    total=q.sum(axis=0);sd=math.sqrt(max(0,float(total@cov@total)))
    if sd>1e-10:
        charge=K*(q@cov@total)/sd;rec=record['euler'];close(charge,rec['charges_thousand_dollars'],B)
        assert np.max(M@charge-c)/B<TOL
        for kind in ('ascending','descending'):
            y=np.array(record['caps']['unrestricted'][kind]['y_thousand_dollars'])
            close(record['caps']['unrestricted'][kind]['distance_from_euler_fraction_T'],np.abs(y-(b-charge)).sum()/(2*T))
    else: assert record['euler']['undefined_at_zero_aggregate']
    prop=T*b/B;close(prop,record['proportional']['y_thousand_dollars'],B)
    close(record['proportional']['coalition_violation_fraction_B'],max(0,float(np.max(M@(b-prop)-c)))/B)
    # Symmetric eigen-root, not the producer's Cholesky transform.
    eigenvalues,eigenvectors=np.linalg.eigh(cov);root=(eigenvectors*np.sqrt(eigenvalues))@eigenvectors.T
    a=K*q@root;G=(a.T/b)@a
    delta=np.linalg.eigvalsh(G)[0]/B
    close(delta,record['spectral_delta'])
    assert record['zero_aggregate_theorem_applies']==bool(sd<=1e-10 and delta>=.25-1e-10)

def calibration(values):
    values=np.asarray(values);ordered=np.sort(values);n=len(ordered);cut=.975*n
    # Integrate the empirical quantile step function on [.975,1].
    tail=sum(float(ordered[i])*max(0,min(i+1,n)-max(i,cut)) for i in range(int(cut),n))/(n-cut)
    return {'standardized_tail_ratio':tail/K,'var_exceedance_rate':float(np.count_nonzero(values>Z)/n),'n':n}

def audit_run(path,observations):
    result=json.loads((path/'results.json').read_text());daily=json.loads((path/'daily_scores.json').read_text())
    ds=[d for d,_ in observations];X=np.array([x for _,x in observations]);bydate={str(d):i for i,d in enumerate(ds)}
    train=X[[d.year<2019 for d in ds]];static=covariance(train);groups=np.vstack([Q,Q.sum(axis=0)])
    assert result['data']['training_n']==len(train)
    holdout=[d for d in ds if d.year>=2019];assert len(holdout)==len(daily)==result['data']['holdout_n']
    assert [str(d) for d in holdout]==[r['date'] for r in daily]
    covs={}
    for record in result['monthly']:
        month=record['month'];indices=[i for i,d in enumerate(ds) if d.strftime('%Y-%m')==month];first=indices[0]
        prior=X[first-252:first];cov=covariance(prior);covs[month]=cov
        assert ds[first-1]<ds[first] and str(ds[first-252])==record['training_start'] and str(ds[first-1])==record['training_end']
        close(record['covariance_bps2'],cov,max(1,float(np.max(cov))))
        audit_record(record,month in ('2019-01','2022-01','2025-12'))
    for record in result['sensitivity'].values():audit_record(record,True)
    for row in daily:
        dx=X[bydate[row['date']]];close([row['dy2_bp'],row['dy10_bp']],dx)
        for key,cov in [('rolling',covs[row['month']]),('static',static)]:
            expected=np.array([float(q@dx)/math.sqrt(float(q@cov@q)) for q in groups])
            close(row[key+'_standardized_losses'],expected)
    for key in ('rolling','static'):
        scores=np.array([r[key+'_standardized_losses'] for r in daily]);close(scores[:,0],scores[:,-1])
        for i in range(7):
            observed=calibration(scores[:,i]);saved=result['calibration'][key][i]
            for field,value in observed.items():close(saved[field],value)
    d=np.array([r['caps']['unrestricted']['reassigned_fraction_T'] for r in result['monthly']]);split=np.array([r['month']<'2022' for r in result['monthly']])
    medians=[float(np.median(d)),float(np.median(d[split])),float(np.median(d[~split]))]
    for key,val in zip(['overall_median_d','2019_2021_median_d','2022_2025_median_d'],medians):close(result['summary'][key],val)
    assert result['summary']['material_gate_passed']==bool(min(medians)>=.05)
    assert result['summary']['calibration_gate_passed']==all(.8<=x['standardized_tail_ratio']<=1.25 for x in result['calibration']['rolling'])
    scores=np.array([r['rolling_standardized_losses'][-1] for r in daily]);rng=np.random.default_rng(20261025);stats=[]
    for _ in range(500):
        starts=rng.integers(len(scores),size=math.ceil(len(scores)/20))
        indices=[(int(start)+j)%len(scores) for start in starts for j in range(20)][:len(scores)]
        stats.append(calibration(scores[indices]))
    for field,interval in result['calibration']['aggregate_rolling_90pct_block_intervals'].items():
        close(interval,np.quantile([s[field] for s in stats],[.05,.95]))
    return {'path':str(path),'months':len(result['monthly']),'daily_n':len(daily),'all_checks_passed':True,
            'charge_lex_months':['2019-01','2022-01','2025-12'],'all_static_partition_lex_stages_checked':True}

if __name__=='__main__':
    strict,available=source()
    reports=[audit_run(P,strict),audit_run(P/'quote_interval_diagnostic',available)]
    out={'passed':True,'independence':'Separate raw parser, manual covariance, charge-coordinate LP stages, quantile-integral tail computation; same SciPy/HiGHS solver library.',
         'limitations':'Floating-point numerical certification of specified cases, not a general theorem or real-time financial validation.',
         'runs':reports,'counts':COUNTS,'max_errors':MAX}
    (P/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
