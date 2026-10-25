"""Frozen retrospective illustration. Never interprets modeled risk capacity as cash."""
from pathlib import Path
from datetime import date,datetime,timezone
import csv,hashlib,json,math
import numpy as np
from scipy.optimize import linprog
from scipy.stats import norm
P=Path(__file__).parent
RAW=P.parent/'2026-10-24-risk-geometry/data/gsw-vintage-2026-10-24.csv'
RAW_SHA='59a802aa6f1661c3beb37a7880706627db2913601920e3be3c3dcdd6b5321278'
Q=np.array([[100,0],[0,80],[60,-30],[-80,0],[0,-70],[-60,20]],float)
ALPHA=.025;Z=float(norm.ppf(1-ALPHA));K=float(norm.pdf(Z)/ALPHA)
OPTIONS={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9}

def solve(c,A,b,E,f,bounds):
    fit=linprog(c,A_ub=A,b_ub=b,A_eq=E,b_eq=f,bounds=bounds,method='highs',options=OPTIONS)
    if fit.status==2:return None
    if not fit.success:raise RuntimeError(fit.message)
    return fit

def game(q,cov):
    n=len(q);M=np.array([[(mask>>i)&1 for i in range(n)] for mask in range(1,2**n)],float)
    costs=K*np.sqrt(np.maximum(np.einsum('ij,jk,ik->i',M@q,cov,M@q),0))
    b=K*np.sqrt(np.einsum('ij,jk,ik->i',q,cov,q));B=float(b.sum());r=float(costs[-1]);T=B-r
    if B<=0 or T<=1e-10*B:raise RuntimeError('nonpositive standalone risk or savings')
    v=(M@b-costs)/B
    return M,v,b/B,T/B,B,r

def constraints(M,v,b,T,cap):
    n=len(b);nv=n if cap is None else 2*n
    A=np.zeros((len(M)+(n+1 if cap is not None else 0),nv));rhs=np.zeros(len(A));A[:len(M),:n]=-M;rhs[:len(M)]=-v
    if cap is not None:
        for i in range(n):A[len(M)+i,i]=1;A[len(M)+i,n+i]=-1;rhs[len(M)+i]=b[i]
        A[-1,n:]=1;rhs[-1]=cap*T
    E=np.zeros((1,nv));E[0,:n]=1
    return A,rhs,E,np.array([T]),[(0,None)]*nv

def selector(M,v,b,T,kind,cap=None):
    n=len(b);A,rhs,E,f,bounds=constraints(M,v,b,T,cap);nv=A.shape[1]
    if solve(np.zeros(nv),A,rhs,E,f,bounds) is None:return None
    active=list(range(n));stages=[]
    while active:
        rows=np.zeros((len(A)+len(active),nv+1));rows[:len(A),:nv]=A;br=np.r_[rhs,np.zeros(len(active))]
        for j,i in enumerate(active):rows[len(A)+j,i]=-1 if kind=='ascending' else 1;rows[len(A)+j,-1]=1 if kind=='ascending' else -1
        eq=np.zeros((1,nv+1));eq[:,:nv]=E;c=np.zeros(nv+1);c[-1]=-1 if kind=='ascending' else 1
        fit=solve(c,rows,br,eq,f,bounds+[(0,None)])
        if fit is None:raise RuntimeError('lex stage infeasible after feasible face')
        t=float(fit.x[-1]);face=list(bounds)
        for i in active:face[i]=(t,face[i][1]) if kind=='ascending' else (face[i][0],t)
        frozen=[]
        for i in active:
            obj=np.zeros(nv);obj[i]=-1 if kind=='ascending' else 1
            probe=solve(obj,A,rhs,E,f,face)
            if probe is None:raise RuntimeError('optimal face infeasible')
            if abs(probe.x[i]-t)<=1e-8:frozen.append(i)
        if not frozen:raise RuntimeError('no universally fixed coordinate')
        for i in frozen:face[i]=(t,t)
        stages.append({'level_fraction_B':t,'fixed_indices':frozen});bounds=face;active=[i for i in active if i not in frozen]
    y=np.array([bounds[i][0] for i in range(n)])
    verify(y,M,v,b,T,cap)
    return y,stages

def verify(y,M,v,b,T,cap=None):
    coalition=max(0,float(np.max(v-M@y)));eff=abs(float(y.sum())-T);credit=float(np.maximum(y-b,0).sum());caperr=0 if cap is None else max(0,credit-cap*T)
    if max(coalition,eff,caperr,max(0,-float(y.min())))>1e-7:raise RuntimeError('allocation residual exceeds frozen gate')
    return {'coalition_violation_fraction_B':coalition,'efficiency_error_fraction_B':eff,'credit_demand_fraction_T':credit/T,'cap_violation_fraction_B':caperr,'min_charge_fraction_T':float(np.min(b-y))/T}

def evaluate(q,cov,caps=True):
    M,v,b,T,B,r=game(q,cov);out={'B_thousand_dollars':B,'residual_risk_thousand_dollars':r,'savings_T_thousand_dollars':T*B,'residual_fraction_B':r/B,'q':q.tolist(),'covariance_bps2':cov.tolist(),'caps':{}}
    vals={}
    for cap in ([None,0,.05,.25] if caps else [None]):
        key='unrestricted' if cap is None else str(cap);rec={}
        for kind in ['ascending','descending']:
            res=selector(M,v,b,T,kind,cap)
            if res is None:rec={'feasible':False};break
            y,stages=res;rec[kind]={'y_thousand_dollars':(y*B).tolist(),'charges_thousand_dollars':((b-y)*B).tolist(),'stages':stages,**verify(y,M,v,b,T,cap)}
            vals[(key,kind)]=y
        if rec.get('feasible') is not False:
            rec['feasible']=True;rec['reassigned_fraction_T']=float(np.abs(vals[(key,'ascending')]-vals[(key,'descending')]).sum()/(2*T))
        out['caps'][key]=rec
    a=q.sum(axis=0);sd=math.sqrt(float(a@cov@a))
    if sd>1e-10:
        euler_charge=K*(q@cov@a)/sd/B;euler=b-euler_charge;diagnostics=verify(euler,M,v,b,T)
        out['euler']={'charges_thousand_dollars':(euler_charge*B).tolist(),'y_thousand_dollars':(euler*B).tolist(),**diagnostics}
        for kind in ['ascending','descending']:
            out['caps']['unrestricted'][kind]['distance_from_euler_fraction_T']=float(np.abs(vals[('unrestricted',kind)]-euler).sum()/(2*T))
    else:out['euler']={'undefined_at_zero_aggregate':True}
    prop=T*b;out['proportional']={'y_thousand_dollars':(prop*B).tolist(),'coalition_violation_fraction_B':max(0,float(np.max(v-M@prop)))}
    A=K*q@np.linalg.cholesky(cov);G=sum(np.outer(a,a)/bi for a,bi in zip(A,b*B));delta=float(np.linalg.eigvalsh(G)[0]/B)
    out['spectral_delta']=delta;out['zero_aggregate_theorem_applies']=bool(sd<=1e-10 and delta>=.25-1e-10)
    return out

def tailmean(x):
    x=np.sort(np.asarray(x,float))[::-1];mass=len(x)*ALPHA;j=int(math.floor(mass));f=mass-j
    return float((x[:j].sum()+(f*x[j] if f else 0))/mass)

def calibration(z):
    return {'standardized_tail_ratio':tailmean(z)/K,'var_exceedance_rate':float(np.mean(np.asarray(z)>Z)),'n':len(z)}

def load_data():
    if hashlib.sha256(RAW.read_bytes()).hexdigest()!=RAW_SHA:raise RuntimeError('raw hash mismatch')
    lines=RAW.read_text().splitlines();header=next(i for i,s in enumerate(lines) if s.startswith('Date,'));rows=list(csv.DictReader(lines[header:]));dates=[r['Date'] for r in rows]
    if len(set(dates))!=len(dates):raise RuntimeError('duplicate dates')
    rows.sort(key=lambda r:r['Date']);last=None;out=[];excluded=[]
    for row in rows:
        day=date.fromisoformat(row['Date'])
        if day<date(2009,12,1) or day>date(2025,12,31):continue
        try:v=np.array([float(row['SVENY02']),float(row['SVENY10'])]);valid=bool(np.all(np.isfinite(v)) and np.all(v>-900))
        except ValueError:valid=False
        if not valid:excluded.append({'date':str(day),'reason':'invalid yield input'});last=None;continue
        if last is not None:
            gap=(day-last[0]).days
            if gap>7:excluded.append({'date':str(day),'reason':'gap over7 days','gap':gap})
            elif day>=date(2010,1,1):out.append((day,(v-last[1])*100))
        last=(day,v)
    ds=[x[0] for x in out];X=np.array([x[1] for x in out])
    if not all(a<b for a,b in zip(ds,ds[1:])):raise RuntimeError('date ordering')
    return ds,X,excluded

def self_checks():
    cov=np.eye(2);q=np.array([[2,0],[1,0],[-1,0],[-1,0],[-1,0]],float)
    M,v,b,T,B,r=game(q,cov);x=selector(M,v,b,T,'ascending')[0];z=selector(M,v,b,T,'descending')[0]
    if not np.allclose(x*B/K,[2,1,1,1,1],atol=1e-7):raise RuntimeError('ascending source calibration')
    if not np.allclose(z*B/K,[4/3,2/3,4/3,4/3,4/3],atol=1e-7):raise RuntimeError('descending source calibration')
    for kind in ['ascending','descending']:
        c=selector(M,v,b,T,kind,0)
        if c is None or not np.allclose(c[0],b,atol=1e-7):raise RuntimeError('zero-credit zero-aggregate calibration')
    if abs(tailmean(np.arange(1,101))-99.2)>1e-10:raise RuntimeError('fractional tail calibration')
    return {'source_selector_calibration':True,'zero_credit_calibration':True,'fractional_tail_calibration':True}

def main():
    checks=self_checks();ds,X,excluded=load_data();train=np.array([d<date(2019,1,1) for d in ds]);static_cov=np.cov(X[train],rowvar=False,ddof=1)
    monthly=[];zs=[];zstatic=[];daily=[];groups=np.vstack([Q,Q.sum(axis=0)]);month_keys=sorted(set(d.strftime('%Y-%m') for d in ds if d>=date(2019,1,1)))
    if len(month_keys)!=84:raise RuntimeError('holdout month coverage differs from84')
    for key in month_keys:
        idx=np.array([i for i,d in enumerate(ds) if d.strftime('%Y-%m')==key]);first=int(idx[0]);prior=np.arange(first-252,first)
        if first<252 or ds[prior[-1]]>=ds[first]:raise RuntimeError('rolling chronology failure')
        cov=np.cov(X[prior],rowvar=False,ddof=1)
        if np.linalg.eigvalsh(cov)[0]<=0:raise RuntimeError('nonpositive covariance')
        rec=evaluate(Q,cov);rec.update(month=key,first_scored_date=str(ds[first]),last_scored_date=str(ds[int(idx[-1])]),training_start=str(ds[int(prior[0])]),training_end=str(ds[int(prior[-1])]),training_n=252);monthly.append(rec)
        sd=np.sqrt(np.einsum('ij,jk,ik->i',groups,cov,groups));ss=np.sqrt(np.einsum('ij,jk,ik->i',groups,static_cov,groups))
        losses=X[idx]@groups.T;rz=losses/sd;sz=losses/ss;zs.extend(rz);zstatic.extend(sz)
        for j,i in enumerate(idx):daily.append({'date':str(ds[int(i)]),'month':key,'dy2_bp':float(X[i,0]),'dy10_bp':float(X[i,1]),'rolling_standardized_losses':rz[j].tolist(),'static_standardized_losses':sz[j].tolist()})
        print(json.dumps({'completed_month':key,'unrestricted_d':rec['caps']['unrestricted']['reassigned_fraction_T']}),flush=True)
    zz=np.array(zs);ss=np.array(zstatic);cal={'rolling':[calibration(zz[:,i]) for i in range(7)],'static':[calibration(ss[:,i]) for i in range(7)]}
    rng=np.random.default_rng(20261025);boot=[];nb=math.ceil(len(zz)/20)
    for _ in range(500):
        starts=rng.integers(0,len(zz),nb);idx=((starts[:,None]+np.arange(20))%len(zz)).ravel()[:len(zz)];boot.append(calibration(zz[idx,-1]))
    cal['aggregate_rolling_90pct_block_intervals']={k:np.quantile([r[k] for r in boot],[.05,.95]).tolist() for k in ['standardized_tail_ratio','var_exceedance_rate']}
    d=np.array([r['caps']['unrestricted']['reassigned_fraction_T'] for r in monthly]);split=np.array([r['month']<'2022' for r in monthly]);summary={'overall_median_d':float(np.median(d)),'2019_2021_median_d':float(np.median(d[split])),'2022_2025_median_d':float(np.median(d[~split])),'min_d':float(d.min()),'max_d':float(d.max()),'fraction_months_d_ge_05':float(np.mean(d>=.05))}
    summary['material_gate_passed']=bool(min(summary[k] for k in ['overall_median_d','2019_2021_median_d','2022_2025_median_d'])>=.05)
    summary['calibration_gate_passed']=bool(all(.8<=r['standardized_tail_ratio']<=1.25 for r in cal['rolling']))
    summary['institutional_gate']='unobserved contract/permissions/shadow rental rate; no actual pooling claim'
    sensitivity={'static_primary':evaluate(Q,static_cov),'split_unit1':evaluate(np.vstack([Q[0]/2,Q[0]/2,Q[1:]]),static_cov),'merge_units1_4':evaluate(np.vstack([Q[0]+Q[3],Q[[1,2,4,5]]]),static_cov)}
    zero=Q.copy();zero[-1]=[-80,20];sensitivity['zero_aggregate_changed_book']=evaluate(zero,static_cov)
    result={'completed_at_utc':datetime.now(timezone.utc).isoformat(),'evidence':'frozen retrospective illustration, revised vintage; modeled exposures; no causal or actual-capital claims','Q_thousand_dollars_per_bp':Q.tolist(),'z975':Z,'kappa_es':K,'data':{'raw_sha256':RAW_SHA,'training_start':str(ds[0]),'training_end':str(ds[np.where(train)[0][-1]]),'training_n':int(train.sum()),'holdout_start':daily[0]['date'],'holdout_end':daily[-1]['date'],'holdout_n':len(daily),'months':len(monthly),'excluded':excluded},'self_checks':checks,'summary':summary,'calibration':cal,'monthly':monthly,'sensitivity':sensitivity}
    (P/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(P/'daily_scores.json').write_text(json.dumps(daily,indent=2,allow_nan=False)+'\n')
    (P/'run_summary.json').write_text(json.dumps({'data':result['data'],'summary':summary,'calibration':cal},indent=2)+'\n')
    print(json.dumps({'FINAL':summary,'aggregate_rolling':cal['rolling'][-1]}))
if __name__=='__main__':main()
