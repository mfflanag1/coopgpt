"""Replay frozen depth inputs without regenerating the discovery manifest."""
from pathlib import Path
import hashlib
import json
from family import verify

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT/'manifest.json').read_text())
if manifest['depths'] != [1, 2, 3, 4]:
    raise RuntimeError('unexpected declared depths')
reports = []
for q in manifest['depths']:
    source = ROOT/('depth_'+str(q)+'.json')
    raw = source.read_bytes()
    candidate = json.loads(raw)
    if candidate['depth'] != q:
        raise RuntimeError('depth file mismatch')
    report = verify(candidate)
    report['input_sha256'] = hashlib.sha256(raw).hexdigest()
    reports.append(report)
result = dict(status='PASS', checked_depths=manifest['depths'],
              all_triple_checks=sum(r['all_triple_checks'] for r in reports),
              reports=reports,
              scope='Frozen finite certificates; the all-parameter conclusion is proved in the accompanying conventional notes')
(ROOT/'BUILD_VERIFICATION.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'status':'PASS', 'saved_depths':manifest['depths'],
                  'triple_checks':result['all_triple_checks'],
                  'ratios':[r['ratio'] for r in reports]}))
