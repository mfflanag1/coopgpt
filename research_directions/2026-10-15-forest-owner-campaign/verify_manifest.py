"""Check the frozen campaign payload without writing files."""
from pathlib import Path
import hashlib
import json

base = Path(__file__).resolve().parent
manifest = json.loads((base/'SHA256.json').read_text())
for name, expected in manifest.items():
    path = base/name
    if not path.is_file():
        raise RuntimeError('missing payload: '+name)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError('hash mismatch: '+name)
print(f'PASS: {len(manifest)} frozen payload files')
