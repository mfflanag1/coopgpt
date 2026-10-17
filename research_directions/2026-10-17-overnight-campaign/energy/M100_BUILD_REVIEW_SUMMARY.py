"""Rebuild the small review packet from preserved derived reports."""
from pathlib import Path
import json,hashlib
r=Path('/private/tmp/coopgpt-overnight-20261017')
names=['M100_PANEL_INSPECTION.json','M100_PANEL_SUPPLEMENT.json','M100_RANGE_INTAKE.json','M100_REVIEW_FOLLOWUP.json']
d,s,i,f=[json.loads((r/'checks'/n).read_text())for n in names]
out={k:d[k]for k in ['utc','duckdb','scope','raw_by_metric','keys_by_metric','phase_counts','gap_summary','triples','states','verdict','audit_correction']}
out['simultaneity']={k:{a:b for a,b in v.items()if a!='node_count_per_time_histogram'}for k,v in d['simultaneity'].items()}
out['schema']=[{k:v for k,v in row.items()if k!='parquet_metadata'}for row in d['schema']]
out['intake']={k:i[k]for k in ['status','source','archive_bytes','downloaded_bytes','requests','next_offset','selected_members','end_padding_check','total_downloaded_bytes_including_initial_probe_and_end_check']}
for k in ['global_gaps','granularity','within_observed_range_20s_grid','psu_key_count']:out[k]=s[k]
out['review_followup']=f
out['derived_report_sha256']={n:hashlib.sha256((r/'checks'/n).read_bytes()).hexdigest()for n in names}
(r/'checks/M100_PANEL_SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
print('Rebuilt summary with source-report hashes')
