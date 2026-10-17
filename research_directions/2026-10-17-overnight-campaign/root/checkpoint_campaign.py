"""Copy this campaign only, preserving unrelated canonical work and recording hashes."""
from pathlib import Path
import hashlib,json,shutil,datetime
src=Path('/private/tmp/coopgpt-overnight-20261017')
dst=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt/research_directions/2026-10-17-overnight-campaign')
if dst.exists() and not dst.is_dir():raise RuntimeError('checkpoint path not directory')
records=[]
for p in sorted(src.rglob('*')):
    rel=p.relative_to(src)
    if any(s in ('.venv','__pycache__','.git') for s in rel.parts) or not p.is_file():continue
    # Keep downloaded third-party originals and rendered/extracted copies local.
    # The checkpoint carries our comparisons and source URLs, not redistributed papers.
    if rel.parts[0]=='sources' and (p.suffix.lower() in ('.pdf','.png') or p.name.endswith('.extracted-original.txt') or p.name in ('Dogan2013-absence-proofness.txt','Rice-withholding.txt','BranzeiSolymosiTijs2003.txt','FINAL_GATE_SPRUMONT2004.txt')):continue
    if p.is_symlink():raise RuntimeError('refuse symlink '+str(p))
    q=dst/rel;q.parent.mkdir(parents=True,exist_ok=True)
    data=p.read_bytes();q.write_bytes(data)
    records.append({'path':str(rel),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
campaign=json.loads((src/'CAMPAIGN_STATUS.json').read_text())
checkpoint_status='complete-campaign' if campaign.get('status')=='complete' else 'interim-active-campaign'
manifest={'status':checkpoint_status,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records}
(dst/'CHECKPOINT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'destination':str(dst),'files':len(records),'bytes':sum(r['bytes'] for r in records),'status':checkpoint_status}))
