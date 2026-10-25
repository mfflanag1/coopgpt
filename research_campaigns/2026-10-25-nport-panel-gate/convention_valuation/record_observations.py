#!/usr/bin/env python3
"""Rebuild ledgers from recorded browser observations; does not re-fetch originals."""
from pathlib import Path
from decimal import Decimal as D
import json,html,re
Q=Path(__file__).resolve().parent
triples='''5042352092.060000 78835847.190000 4963516244.870001
56569343327.159996 33437807.170000 56535905519.989998
64413041345.589996 414270799.290000 63998770546.299995
23541305653.470001 16077897.350000 23525227756.120003
45068362697.589996 23319389.570000 45045043308.019997
12330479666.599998 8584796.070000 12321894870.529999
32387151762.839989 15012978.330000 32372138784.509987
20390723899.340000 27556377.330000 20363167522.009998
9533776265.519999 101284952.520000 9432491312.999998
27097735944.830006 16662947.380000 27081072997.450005
15421610962.930000 130875582.550000 15290735380.380001
14793177949.809998 9186753.190000 14783991196.619997
30345468865.370007 25501360.270000 30319967505.100006
77086211.20 50262443.36 26823767.81
1150929976.30 718735772.50 432194203.37
1408139202.000000 888706028.700000 519433173.240000
444807869.800000 315476851.600000 129331018.130000
40900238399.000000 25716447556.000000 15183790843.120000
1893548937.000000 1210156439.000000 683392497.450000
4331008591.000000 2845353144.000000 1485655446.920000
19678741629.000000 7074617213.600000 12604124416.000000
643301372.100000 60548067.240000 582753304.870000
2030063732.000000 357254896.640000 1672808836.000000
1850288038.328999800000 4314891.239000000000 1845973147.089999700000
2549134.12 2300.08 2546834.03
1819987304.000000 421803602.200000 1398183701.860000
720671863.300000 495060247.100000 225611616.260000
219507525.100000 138529312.700000 80978212.460000
47374462.050000000000 5436.610000000000 47379898.660000000000'''
rawnav=json.loads(html.unescape(re.search(r'<pre[^>]*>(.*?)</pre>',(Q/'nav_audit_input.html').read_text(),re.S).group(1)))
notes={0:'B5a returns exclude charges; no B1 precision explanation.',11:'B5a returns and partial-month class inception; no B1 precision explanation.',13:'B5a returns, swap payment directions and swaption premium valuation; no B1 precision explanation.',14:'Same topics as record13, reordered.',15:'Returns; unavailable dates; negative cash shown as zero due to B2f XML constraint; supranational country coding. No B1 precision or B3 shock convention.',23:'No explanatory notes beyond form instructions.'}
groups={**{i:0 for i in list(range(11))+[12]},11:11,13:13,14:14,**{i:15 for i in [15,16,17,18,19,20,21,22,25,26,27]},**{i:23 for i in [23,24,28]}}
rows=[]
for i,(r,line) in enumerate(zip(rawnav,triples.splitlines(),strict=True)):
 a,l,n=line.split();gap=D(a)-D(l)-D(n)
 if not all(D(x)==D(r[k]) for x,k in [(a,'assets'),(l,'liabilities'),(n,'nav')]):raise ValueError((i,'original/bulk mismatch'))
 if gap==0:raise ValueError('Expected unreconciled row')
 rows.append({'series_id':r['series_id'],'accession':r['accession'],'cik':r['cik'],'original_assets':a,'original_liabilities':l,'original_nav':n,'identity_gap_assets_minus_liabilities_minus_nav':str(gap),'original_rendered_url':r['filing_index'].rsplit('/',1)[0]+'/xslFormNPORT-P_X01/primary_doc.xml','identity_reference_date_confirmed':True,'all_three_numeric_fields_match_bulk':True,'notes_group':groups[i],'precision_justification_found':False,'decision':'RETAIN_QUARANTINE'})
ledger={'observed_date':'2026-10-25','method':'Normal SEC filing index links and rendered original documents read in browser; all29 series/CIK/reference date identities matched; all87 numeric fields matched. Full PartE inspected, grouped by identical observed text or stated topics. Numbers transcribed from tool output and rechecked with Decimal. This script reconstructs the ledger, not web evidence. Original full documents not saved.','rows':rows,'notes_summaries':notes,'restored':0,'retained':29,'precision_conclusion':'No numerical reconciliation tolerance established from inspected sources; no inference that SEC requires our exclusion or that small mismatches are material. Applicable technical precision rules remain unverified.'}
(Q/'nav_source_audit.json').write_text(json.dumps(ledger,indent=2)+'\n')
positions='''912803GM9 313749000 88524496.84 2052-11-15
912803GS6 344507000 95042356.90 2053-05-15
912803FP3 284113000 88771587.00 2050-05-15
912803FY4 270674000 80224858.44 2051-05-15
912803GA5 259086000 75897800.59 2051-08-15
912803FV0 289274000 86487921.56 2051-02-15
912803GC1 270598000 78567063.14 2051-11-15
912803FM0 270330000 84204286.12 2050-02-15
912803HD8 267094000 70935994.39 2054-08-15
912803GP2 322592000 89757098.05 2053-02-15
912803GK3 315141000 88873493.27 2052-08-15
912803GY3 209860000 56548495.75 2054-02-15
912803GW7 292606000 80003129.91 2053-11-15
912803GU1 345712000 94650455.69 2053-08-15
912803GE7 287108000 82450044.67 2052-02-15
912803HF3 284760000 75190983.36 2054-11-15
912803FR9 252881000 77357878.41 2050-08-15
912803GH0 282704000 80519139.81 2052-05-15
912803HB2 168696000 45220818.46 2054-05-15
912803FT5 253266000 76552935.89 2050-11-15'''
r=json.loads((Q/'target_holdings_raw.json').read_text());hs={h['ISSUER_CUSIP']:h for h in r['FUND_REPORTED_HOLDING.tsv']};ds={d['HOLDING_ID']:d for d in r['DEBT_SECURITY.tsv']};out=[]
from datetime import datetime
for line in positions.splitlines():
 c,f,v,m=line.split();h=hs[c];d=ds[h['HOLDING_ID']]
 if not (D(f)==D(h['BALANCE']) and D(v)==D(h['CURRENCY_VALUE']) and m==datetime.strptime(d['MATURITY_DATE'],'%d-%b-%Y').date().isoformat() and D(d['ANNUALIZED_RATE'])==0 and d['COUPON_TYPE']=='None'):raise ValueError(c)
 out.append({'cusip':c,'original_face_normalized':f,'original_mark_normalized':v,'original_maturity':m,'original_coupon_type':'None','original_rate':'0','original_currency':'United States Dollar','original_issuer_type':'U.S. Treasury','matched':True})
(Q/'holdings_source_audit.json').write_text(json.dumps({'original_url':'https://www.sec.gov/Archives/edgar/data/1450011/000145001125000308/xslFormNPORT-P_X01/primary_doc.xml','observed_date':'2026-10-25','positions_observed':20,'method':'Rendered original PartC text. Face, mark, maturity, coupon type and rate compared to bulk per CUSIP; original text also states USD and UST. Explicit radio-button selections (long/default/etc.) were not independently verified in browser; those restrictions rely on bulk fields. Preserved values are transcribed tool observations, not original-file downloads.','rows':out},indent=2)+'\n')
print('29 NAV records and20 holdings checked and recorded')
