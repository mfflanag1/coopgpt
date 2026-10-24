#!/usr/bin/env python3
"""Build and verify the first-party specialist packet; excludes downloaded originals."""
from pathlib import Path
from hashlib import sha256
import json
import zipfile

root = Path(__file__).resolve().parent
explicit = [
    'README.txt', 'SCOPE.txt', 'INPUT_MANIFEST.json',
    'consolidated_envelope_candidate.tex', 'CONTRIBUTION_AND_PRIORITY.txt',
    'SPECIALIST_REVIEW_PACKET.txt', 'replay_checks.py', 'make_packet.py',
    'sources/ROOT_SOURCE_CHECKS.txt', 'sources/PRIORITY_ADDENDUM.txt',
]
files = [root / name for name in explicit]
for directory in ['draft', 'inputs', 'checks']:
    files += [p for p in (root / directory).rglob('*')
              if p.is_file() and '__pycache__' not in p.parts]
for name in ['TRANSLATION_AUDIT.txt', 'TRANSLATION_SCOPE_ADDENDUM.txt',
             'LITERATURE_DELEGATION_ADJUDICATION.txt', 'PROOF_REVIEW.txt',
             'PROOF_REVIEW_REQUEST.json', 'PROOF_REVIEW_STATUS.json',
             'FINAL_REVIEW_ADJUDICATION.txt']:
    files.append(root / 'reviews' / name)
missing = [str(p.relative_to(root)) for p in files if not p.is_file()]
if missing:
    raise SystemExit('Missing expected packet files: ' + ', '.join(missing))
files = sorted(set(files))
manifest = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in files}
manifest_path = root / 'PACKET_MANIFEST.json'
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
archive = root / 'envelope-review-packet.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for p in files + [manifest_path]:
        z.write(p, str(Path('envelope-review-packet') / p.relative_to(root)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name, digest in manifest.items():
        assert sha256(z.read('envelope-review-packet/' + name)).hexdigest() == digest, name
print(json.dumps({'archive': str(archive), 'sha256': sha256(archive.read_bytes()).hexdigest(),
                  'first_party_files': len(files), 'bytes': archive.stat().st_size,
                  'verification': 'all manifest hashes and archive CRCs pass'}, indent=2))
