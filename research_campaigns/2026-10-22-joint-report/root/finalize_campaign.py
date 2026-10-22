"""Record closeout and artifact hashes after the bounded gate has ended."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import json
R=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc)
p=R/'CAMPAIGN.json'; campaign=json.loads(p.read_text())
start=datetime.fromisoformat(campaign['start_utc'])
deadline=datetime.fromisoformat(campaign['gate_deadline_utc'])
if now<deadline:
    raise SystemExit('Gate deadline has not arrived; no final status written.')
campaign.update({
    'status':'complete_gate_not_passed',
    'completed_utc':now.isoformat(),
    'elapsed_minutes':round((now-start).total_seconds()/60,3),
    'six_hour_extension_earned':False,
    'six_hour_extension_run':False,
    'unrestricted_bound_improved':False,
    'main_result':'Fixed-cap, fixed-power seed envelopes have a linear owner-count lower along an unbounded sequence; the cap-2 coefficient is 1/11. The elementary NC upper makes the owner order sharp in the stated sequential sense.',
    'priority_status':'Unconfirmed; free original-source comparisons and internal audits do not establish historical novelty.',
    'next_action':'Consolidate with existing envelope-obstruction paper candidate and seek specialist correctness, priority and relevance assessment; no outreach performed.',
    'canonical_repo_edited':False,
    'github_modified':False,
    'outreach_sent':False,
})
p.write_text(json.dumps(campaign,indent=2)+'\n')
p=R/'CAMPAIGN_REPORT.txt'; report=p.read_text()
report=report.replace('Draft prepared during the90-minute gate; final verification recorded below.',
                      'Completed the90-minute gate. The continuation condition was not met.\nThe exact closeout time and elapsed duration are recorded in CAMPAIGN.json.')
report=report.replace('No finding\ncurrently justifies the conditional six-hour extension under the frozen\ngate.',
                      'No finding\njustified the conditional six-hour extension under the frozen gate; that\nextension was not run.')
p.write_text(report)
inputs=json.loads((R/'INPUT_MANIFEST.json').read_text())
source_checks=[]
for local,meta in inputs.items():
    saved=R/local; source=Path(meta['source'])
    assert sha256(saved.read_bytes()).hexdigest()==meta['sha256'],local
    source_checks.append({'snapshot':local,'source':str(source),
                          'source_still_matches':source.is_file() and sha256(source.read_bytes()).hexdigest()==meta['sha256']})
files=[]
for f in sorted(R.rglob('*')):
    if not f.is_file() or '__pycache__' in f.parts or f.name=='FINAL_MANIFEST.json':continue
    data=f.read_bytes()
    files.append({'path':str(f.relative_to(R)),'bytes':len(data),'sha256':sha256(data).hexdigest()})
manifest={'closed_utc':now.isoformat(),
          'scope':'File-integrity/provenance index, not a mathematical correctness or novelty certificate. Excludes this manifest itself and Python cache files.',
          'third_party_material':'sources contains locally inspected original texts/PDFs and source screenshots; these are excluded from the first-party review zip.',
          'canonical_repository_note':'Read-only during this campaign. Existing unrelated modifications are not claimed clean or synchronized.',
          'input_source_checks':source_checks,'files':files}
(R/'FINAL_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Verify the just-written index and focused bundle against the recorded bytes.
for x in files:assert sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
print(json.dumps({'status':campaign['status'],'completed_utc':campaign['completed_utc'],
                  'elapsed_minutes':campaign['elapsed_minutes'],'manifest_files':len(files),
                  'source_matches':all(x['source_still_matches'] for x in source_checks),
                  'integrity':'PASS'}))
