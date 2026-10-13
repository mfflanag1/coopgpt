"""Fetch only pinned public source files and verify their Git blob identities."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parent


def checked_bytes(data, entry):
    if len(data) != entry['bytes']:
        raise ValueError('Wrong byte length: ' + entry['path'])
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    if hashlib.sha1(blob).hexdigest() != entry['git_blob_sha1']:
        raise ValueError('Upstream Git blob mismatch: ' + entry['path'])
    return hashlib.sha256(data).hexdigest()


def fetch(cache):
    freeze = json.loads((ROOT / 'DESIGN_FREEZE.json').read_text())
    for name in ('PROTOCOL.txt', 'SOURCE_LOCK.json'):
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != freeze['sha256'][name]:
            raise ValueError('Frozen design changed: ' + name)
    lock = json.loads((ROOT / 'SOURCE_LOCK.json').read_text())
    if lock.get('repository') != 'https://github.com/alibaba/clusterdata' or re.fullmatch('[0-9a-f]{40}', lock.get('revision', '')) is None:
        raise ValueError('Unexpected repository/revision')
    cache.mkdir(parents=True, exist_ok=True)
    records = []
    for entry in lock['files']:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or type(entry['bytes']) is not int or not 0 <= entry['bytes'] <= 30_000_000:
            raise ValueError('Unsupported path/size')
        expected_url = 'https://raw.githubusercontent.com/alibaba/clusterdata/' + lock['revision'] + '/' + entry['path']
        if entry['url'] != expected_url:
            raise ValueError('URL does not match locked revision/path')
        target = cache / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.resolve().relative_to(cache.resolve())
        if target.exists():
            data = target.read_bytes()
            status = 'verified_existing'
        else:
            request = urllib.request.Request(entry['url'], headers={'User-Agent': 'CoopGPT-research-source-audit'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read(entry['bytes'] + 1)
            checked_bytes(data, entry)
            with target.open('xb') as stream:
                stream.write(data)
            status = 'downloaded'
        digest = checked_bytes(data, entry)
        records.append(dict(entry, sha256=digest, status=status))
    return {'revision': lock['revision'], 'checked_utc': datetime.now(timezone.utc).isoformat(),
            'files': records, 'total_bytes': sum(x['bytes'] for x in records)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', required=True, type=Path)
    parser.add_argument('--record', required=True, type=Path)
    args = parser.parse_args()
    result = fetch(args.cache)
    with args.record.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'files': len(result['files']), 'total_bytes': result['total_bytes']}))
