from pathlib import Path
import hashlib,json
base=Path(__file__).parent
entries=json.loads((base/'SHA256.json').read_text())
for name,digest in entries.items():
    p=base/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise RuntimeError('Integrity failure: '+name)
print('PASS:',len(entries),'payload hashes')
