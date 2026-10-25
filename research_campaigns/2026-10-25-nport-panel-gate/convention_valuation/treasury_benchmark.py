#!/usr/bin/env python3
"""Post-result conditional revaluation, anchored to filed marks; not a filer error test."""
from pathlib import Path
from datetime import date,datetime
from decimal import Decimal,localcontext
import math,json,hashlib

NODES=[.25,1.,5.,10.,30.]
LABELS=['3MON','1YR','5YR','10YR','30YR']
REFERENCE=date(2025,3,31)

def weights(t):
    if t<=NODES[0]:return [1.,0.,0.,0.,0.]
    if t>=NODES[-1]:return [0.,0.,0.,0.,1.]
    for k in range(4):
        if NODES[k]<=t<=NODES[k+1]:
            u=(t-NODES[k])/(NODES[k+1]-NODES[k]);w=[0.]*5;w[k]=1-u;w[k+1]=u;return w
    raise ValueError('Invalid maturity')

def loss(mark,face,t,shock):
    if min(mark,face,t)<=0:raise ValueError('Positive mark, face and maturity required')
    q=math.exp(math.log(face/mark)/(2*t))
    if q+shock/2<=0:raise ValueError('Shock outside yield domain')
    return -mark*math.expm1(-2*t*math.log1p(shock/(2*q)))

def decimal_loss(mark,face,days,basis,shock):
    with localcontext() as ctx:
        ctx.prec=70
        p,f=Decimal(mark),Decimal(face);t=Decimal(days)/Decimal(basis);h=Decimal(shock)
        q=((f/p).ln()/(2*t)).exp()
        return p*(1-(2*t*(q/(q+h/2)).ln()).exp())

def tangent(mark,face,t):
    return mark*t/math.exp(math.log(face/mark)/(2*t))*0.0001

def run(raw,reported,basis=365.25):
    fund=raw['FUND_REPORTED_INFO.tsv'][0]
    debts={r['HOLDING_ID']:r for r in raw['DEBT_SECURITY.tsv']}
    if len(debts)!=len(raw['DEBT_SECURITY.tsv']):raise ValueError('Duplicate debt key')
    assets=float(fund['TOTAL_ASSETS']);nav=float(fund['NET_ASSETS']);positions=[];excluded=[]
    totals={f'{method}_{direction}_{bp}':[0.]*5 for method in ['A','B'] for direction in ['up','down'] for bp in [1,100]}
    totals['tangent_DV01']=[0.]*5
    for h in raw['FUND_REPORTED_HOLDING.tsv']:
        d=debts.get(h['HOLDING_ID']);reason=[]
        if not d:reason.append('no_debt_terms')
        if h['UNIT']!='PA' or h['CURRENCY_CODE']!='USD' or h['PAYOFF_PROFILE']!='Long' or h['ISSUER_TYPE']!='UST' or h['ASSET_CAT']!='DBT':reason.append('not_ordinary_long_USD_Treasury')
        if d and (Decimal(d['ANNUALIZED_RATE'])!=0 or d['COUPON_TYPE']!='None' or d['IS_DEFAULT']!='N' or d['ARE_ANY_INTEREST_PAYMENT']!='N' or d['IS_ANY_PORTION_INTEREST_PAID']!='N' or d['IS_CONVTIBLE_MANDATORY'] or d['IS_CONVTIBLE_CONTINGENT']):reason.append('not_clean_zero_coupon')
        if h['DERIVATIVE_CAT']:reason.append('derivative')
        if reason:excluded.append({'holding_id':h['HOLDING_ID'],'reasons':reason,'value':h['CURRENCY_VALUE']});continue
        maturity=datetime.strptime(d['MATURITY_DATE'],'%d-%b-%Y').date();days=(maturity-REFERENCE).days
        p,f=float(h['CURRENCY_VALUE']),float(h['BALANCE']);t=days/basis
        if min(p,f,t)<=0:raise ValueError('Invalid position')
        w=weights(t)
        implied=2*math.expm1(math.log(f/p)/(2*t))
        for direction,sgn in [('up',1),('down',-1)]:
            for bp in [1,100]:
                shock=sgn*bp/10000
                whole=loss(p,f,t,shock)
                independent=float(decimal_loss(h['CURRENCY_VALUE'],h['BALANCE'],days,str(basis),str(shock)))
                if abs(whole-independent)>1e-10*max(1,abs(independent)):raise ArithmeticError('Float/Decimal repricing disagreement')
                for k in range(5):
                    totals[f'A_{direction}_{bp}'][k]+=w[k]*whole
                    totals[f'B_{direction}_{bp}'][k]+=loss(p,f,t,w[k]*shock)
        for k in range(5):totals['tangent_DV01'][k]+=w[k]*tangent(p,f,t)
        positions.append({'id':h['HOLDING_ID'],'cusip':h['ISSUER_CUSIP'],'title':h['ISSUER_TITLE'],'maturity':maturity.isoformat(),'days':days,'mark':h['CURRENCY_VALUE'],'face':h['BALANCE'],'implied_nominal_semiannual_yield':implied,'weights':w})
    coverage=sum(float(x['mark']) for x in positions)/assets
    paired={}
    for method in ['A','B']:
        paired[method]=[]
        for k,n in enumerate(LABELS):
            d01=float(reported[f'INTRST_RATE_CHANGE_{n}_DV01']);d100=float(reported[f'INTRST_RATE_CHANGE_{n}_DV100'])
            model1=totals[f'{method}_up_1'][k];model100=totals[f'{method}_up_100'][k];res=d100-100*d01;modelres=model100-100*model1
            paired[method].append({'node':n,'reported_dv01':d01,'reported_dv100':d100,'model_finite_dv01':model1,'model_dv100':model100,'reported_residual_nav_bp':res/nav*10000,'model_residual_nav_bp':modelres/nav*10000,'model_minus_reported_dv01_nav_bp':(model1-d01)/nav*10000,'model_minus_reported_dv100_nav_bp':(model100-d100)/nav*10000,'model_minus_reported_residual_nav_bp':(modelres-res)/nav*10000,'tangent_dv01':totals['tangent_DV01'][k],'tangent_minus_reported_dv01_nav_bp':(totals['tangent_DV01'][k]-d01)/nav*10000,'tangent_residual_nav_bp':(model100-100*totals['tangent_DV01'][k])/nav*10000})
    return {'basis_days':basis,'reference_date':REFERENCE.isoformat(),'positions':positions,'matched_positions':len(positions),'unmatched_positions':excluded,'matched_asset_share':coverage,'passes_99pct_coverage':coverage>=.99,'total_assets':fund['TOTAL_ASSETS'],'nav':fund['NET_ASSETS'],'unmatched_assets':assets-sum(float(x['mark']) for x in positions),'cash_disclosed':fund['CASH_NOT_RPTD_IN_C_OR_D'],'model_node_losses':totals,'node_comparisons':paired,'interpretation':'Conditional deterministic cash-flow benchmark anchored to filed marks; no independent market-price validation and no claim of exact filer convention. Down-shock output is signed loss (negative for gains). Model A sums to its own parallel repricing by construction; does not identify a joint shock from reported node values.'}

def main():
    q=Path(__file__).resolve().parent;p=q.parent
    raw=json.loads((q/'target_holdings_raw.json').read_text())
    r=next(x for x in json.loads((p/'reviewed_bulk_analysis/rows.json').read_text()) if x['series_id']=='S000026750')
    results={'status':'CONDITIONAL_BENCHMARK_ONLY','scope_sha256':hashlib.sha256((q/'SCOPE.txt').read_bytes()).hexdigest(),'holdings_sha256':hashlib.sha256((q/'target_holdings_raw.json').read_bytes()).hexdigest(),'series_id':r['series_id'],'accession':r['accession'],'selection':'Post-result case, selected for simple mandate; not holdout or prevalence evidence','primary':run(raw,r['raw_metrics']),'day_count_sensitivity':run(raw,r['raw_metrics'],365.0)}
    out=q/'treasury_result.json'
    if out.exists():raise FileExistsError('Preserve existing result')
    out.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:results['primary'][k] for k in ['matched_positions','unmatched_positions','matched_asset_share','passes_99pct_coverage','unmatched_assets','cash_disclosed','node_comparisons']},indent=2))
if __name__=='__main__':main()
