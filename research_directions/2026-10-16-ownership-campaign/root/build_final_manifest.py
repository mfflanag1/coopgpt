"""Content manifest for this campaign; excludes caches and this generated manifest."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
root=Path(__file__).resolve().parents[1]
out=root/'FINAL_ARTIFACT_MANIFEST.json'
files={}
for path in sorted(root.rglob('*')):
    if not path.is_file() or path==out or '__pycache__' in path.parts or path.suffix=='.pyc':continue
    files[str(path.relative_to(root))]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
record={'generated_utc':datetime.now(timezone.utc).isoformat(),'semantics':'Integrity inventory only; presence is not acceptance. CURRENT_RESULTS and numbered adjudications define scope/status.','files':files}
out.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'manifest':str(out),'files':len(files),'total_bytes':sum(v['bytes'] for v in files.values())}))
