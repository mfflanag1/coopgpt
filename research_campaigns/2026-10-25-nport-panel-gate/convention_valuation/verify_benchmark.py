#!/usr/bin/env python3
"""Independent high-precision node calculation and frozen-run reproduction."""
from pathlib import Path
from decimal import Decimal as D,localcontext
from datetime import datetime,date
import argparse,hashlib,json
from treasury_benchmark import run

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('Use a fresh output')
    q=Path(__file__).resolve().parent;p=q.parent
    raw=json.loads((q/'target_holdings_raw.json').read_text());saved=json.loads((q/'treasury_result.json').read_text())
    if hashlib.sha256((q/'SCOPE.txt').read_bytes()).hexdigest()!=saved['scope_sha256']:raise ValueError('Scope changed')
    if hashlib.sha256((q/'target_holdings_raw.json').read_bytes()).hexdigest()!=saved['holdings_sha256']:raise ValueError('Holdings changed')
    r=next(x for x in json.loads((p/'reviewed_bulk_analysis/rows.json').read_text()) if x['series_id']=='S000026750')
    audit=next(x for x in json.loads((p/'source_audit.json').read_text())['rows'] if x['series_id']==r['series_id'])
    if not audit['series_cik_reference_date_usd_nav_matched'] or not audit['filing_index_accession_and_reference_date_matched']:raise ValueError('Reference-date source gate')
    if r['accession']!=saved['accession']:raise ValueError('Accession mismatch')
    ds={r['HOLDING_ID']:r for r in raw['DEBT_SECURITY.tsv']};hs=raw['FUND_REPORTED_HOLDING.tsv']
    if len({h['HOLDING_ID'] for h in hs})!=len(hs) or len(ds)!=len(raw['DEBT_SECURITY.tsv']):raise ValueError('Duplicate key')
    checked=0;maxdiff=D(0);records=[]
    with localcontext() as ctx:
        ctx.prec=70
        for basis,key in [('365.25','primary'),('365.0','day_count_sensitivity')]:
            out=run(raw,r['raw_metrics'],float(basis))
            if out!=saved[key]:raise ValueError('Frozen calculation no longer reproduces')
            sums={k:[D(0)]*5 for k in out['model_node_losses']};nodes=[D('.25'),D(1),D(5),D(10),D(30)]
            for h in hs:
                debt=ds[h['HOLDING_ID']];days=(datetime.strptime(debt['MATURITY_DATE'],'%d-%b-%Y').date()-date(2025,3,31)).days
                t=D(days)/D(basis);p0=D(h['CURRENCY_VALUE']);face=D(h['BALANCE']);q0=((face/p0).ln()/(2*t)).exp()
                ws=[D(0)]*5
                if t<=nodes[0]:ws[0]=D(1)
                elif t>=nodes[-1]:ws[-1]=D(1)
                else:
                    k=next(k for k in range(4) if nodes[k]<=t<=nodes[k+1]);ws[k+1]=(t-nodes[k])/(nodes[k+1]-nodes[k]);ws[k]=1-ws[k+1]
                def dv(shift):return p0*(1-(-2*t*(1+shift/(2*q0)).ln()).exp())
                for k,w in enumerate(ws):
                    sums['tangent_DV01'][k]+=w*p0*t/q0/D(10000)
                    for direction,sign in [('up',1),('down',-1)]:
                        for bp in [1,100]:
                            shock=D(sign*bp)/D(10000)
                            sums[f'A_{direction}_{bp}'][k]+=w*dv(shock)
                            sums[f'B_{direction}_{bp}'][k]+=dv(w*shock)
            for name,vs in sums.items():
                for k,v in enumerate(vs):
                    error=abs(v-D(str(out['model_node_losses'][name][k])));maxdiff=max(maxdiff,error);checked+=1
                    if error>max(D('1e-8'),abs(v)*D('1e-10')):raise ArithmeticError((basis,name,k,error))
            records.append({'basis':basis,'replays_frozen_output':True,'node_values_checked':sum(map(len,sums.values()))})
        fund=raw['FUND_REPORTED_INFO.tsv'][0];marks=sum(D(h['CURRENCY_VALUE']) for h in hs);assets=D(fund['TOTAL_ASSETS']);cash=D(fund['CASH_NOT_RPTD_IN_C_OR_D'])
        residual=assets-marks
        if residual!=cash:raise ArithmeticError('Holdings plus cash do not equal total assets')
        if assets-D(fund['TOTAL_LIABILITIES'])!=D(fund['NET_ASSETS']):raise ArithmeticError('NAV identity')
        result={'status':'PASS','coverage_exact_decimal':str(marks/assets),'matched_value':str(marks),'unmatched_assets_exact':str(residual),'cash_matches_residual':True,'node_calculations_checked':checked,'maximum_absolute_float_decimal_difference_dollars':str(maxdiff),'checks':records,'source_reference_date_check':'Prior original-filing audit record; not a new independent source retrieval','limit':'Numerical correctness under declared conventions, not validation of filer methodology or actual risk.'}
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
