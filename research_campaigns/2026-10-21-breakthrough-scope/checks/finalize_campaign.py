from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'CAMPAIGN.json';state=json.loads(p.read_text())
now=datetime.now(timezone.utc)
assert now>=datetime.fromisoformat(state['end_deadline_utc']), 'Campaign deadline not yet reached'
state.update(status='complete',phase='completed',completed_at_utc=now.isoformat(),
 actual_elapsed_seconds=round((now-datetime.fromisoformat(state['start_utc'])).total_seconds()),
 final_deliverables=['handoff.html','proofs/FINAL_ENVELOPE_OBSTRUCTION.txt',
 'proofs/mass_geometry_qary_sharp_audit.txt','REVIEW_PACKET.txt','review-bundle.zip'],
 validation='Main theorem internally audited; all five exact replay programs passed, including fresh-bundle replay; fixed-Q refinement independently audited with scope recorded.')
p.write_text(json.dumps(state,indent=2)+'\n')
p=R/'CAMPAIGN_REPORT.txt';text=p.read_text().replace(
 'This report is being finalized within the campaign. See CAMPAIGN.json for\nthe observed completion status and final timestamp.',
 'The three-hour campaign is complete. See CAMPAIGN.json for the observed\ncompletion timestamp, validation record and final deliverables.')
p.write_text(text)
for script in ['build_handoff.py','build_review_bundle.py']:
 subprocess.run(['python3',str(R/'checks'/script)],cwd=R,check=True)
print(json.dumps({'status':'complete','completed_at_utc':state['completed_at_utc'],'elapsed_seconds':state['actual_elapsed_seconds']}))
