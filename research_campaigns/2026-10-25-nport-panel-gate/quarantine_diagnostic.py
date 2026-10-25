"""Post-result sensitivity only: never changes frozen eligibility or resolves a quarantine."""
import json
from fractions import Fraction as F
from pathlib import Path
from preflight import load_archive,METRICS
from analyze_panel import calculate,distribution
p=Path(__file__).parent
pre=json.loads((p/'complete_preflight.json').read_text())
tables,digest=load_archive(Path('/Users/maxf/Downloads/2025q2_nport.zip'))
if digest!=pre['archive_sha256']:raise ValueError('Archive hash changed')
fund={x['ACCESSION_NUMBER']:x for x in tables['FUND_REPORTED_INFO.tsv']}
reg={x['ACCESSION_NUMBER']:x for x in tables['REGISTRANT.tsv']}
quarantined=[]
for exc in pre['exclusions']:
 if exc['reason']!='nav_reconciliation_requires_source_check':continue
 acc=exc['accession'];f=fund[acc]
 usd=[x for x in tables['INTEREST_RATE_RISK.tsv'] if x['ACCESSION_NUMBER']==acc and x['CURRENCY_CODE']=='USD']
 if len(usd)!=1:raise ValueError('Unexpected USD cardinality')
 raw={k:usd[0][k] for k in METRICS}
 x=calculate({'series_id':f['SERIES_ID'],'accession':acc,'cik':reg[acc]['CIK'],'series_name':f['SERIES_NAME'],'nav':f['NET_ASSETS'],'raw_metrics':raw,'all_zero_vector':all(F(x)==0 for x in raw.values())})
 x['assets']=f['TOTAL_ASSETS'];x['liabilities']=f['TOTAL_LIABILITIES']
 x['nav_gap_exact']=str(F(x['assets'])-F(x['liabilities'])-F(x['nav']))
 x['status']='QUARANTINED; not restored by this diagnostic'
 quarantined.append(x)
base=json.loads((p/'reviewed_bulk_analysis/rows.json').read_text())
combined=base+quarantined
result={'label':'POST_RESULT_UNRECONCILED_SENSITIVITY_ONLY','count_quarantined':len(quarantined),'hypothetical_count_if_all_retained':len(combined),'quarantines_resolved':0,'primary_distribution_if_all_retained':distribution(combined,'primary_exact'),'thresholds_if_all_retained':[{'strictly_above_nav_bp':k,'fund_count':sum(F(r['primary_exact'])>k for r in combined)} for k in [1,10,100]],'quarantined_rows':quarantined}
(p/'quarantine_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='quarantined_rows'},indent=2))
