"""Replay already acquired tar headers; no member payload or network access."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import tarfile
import re


def audit(root):
    ledger = (root / 'inputs/acquisition_ledger.jsonl').read_bytes()
    entries = [json.loads(line) for line in ledger.splitlines()]
    headers = sorted((r for r in entries if r['kind'] == 'dataset_june_header'),
                     key=lambda r: r['start'])
    next_offset = 0
    ended = False
    records = []
    archive_sizes = set()
    for r in headers:
        if ended or r['start'] != next_offset:
            raise ValueError('Missing, duplicate, or post-terminator header')
        raw = (root / 'inputs/june_headers' / Path(r['saved_path']).name).read_bytes()
        if len(raw) != 512 or hashlib.sha256(raw).hexdigest() != r['sha256']:
            raise ValueError('Inherited header body/hash mismatch')
        if r['body_bytes'] != 512 or r['status'] != 206:
            raise ValueError('Unexpected acquisition record')
        match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', r['content_range'])
        if not match or list(map(int, match.groups()[:2])) != [r['start'], r['start'] + 511]:
            raise ValueError('Unexpected header Content-Range')
        archive_sizes.add(int(match.group(3)))
        if raw == bytes(512):
            ended = True
            continue
        entry = tarfile.TarInfo.frombuf(raw, 'utf-8', 'strict')
        # Extended/PAX headers can override names; do not silently skip them.
        if entry.type not in (tarfile.REGTYPE, tarfile.DIRTYPE):
            raise ValueError('Unsupported header type; inventory not complete')
        if entry.size < 0:
            raise ValueError('Negative tar size')
        records.append({'name': entry.name, 'bytes': entry.size,
                        'type': entry.type.decode('ascii'),
                        'header_offset': r['start'], 'payload_offset': r['start'] + 512})
        next_offset += 512 + ((entry.size + 511) // 512) * 512
    if not ended:
        raise ValueError('No first tar terminator in retained header chain')
    if len(archive_sizes) != 1 or next_offset + 512 > next(iter(archive_sizes)):
        raise ValueError('Inconsistent archive size')
    plugins = Counter()
    for r in records:
        if r['type'] == '0':
            matches = [s[7:] for s in r['name'].split('/') if s.startswith('plugin=')]
            if len(matches) != 1:
                raise ValueError('Unexpected regular member path')
            plugins[matches[0]] += 1
    return {'source_ledger_sha256': hashlib.sha256(ledger).hexdigest(),
            'header_bodies_verified': len(headers),
            'regular_members': sum(r['type'] == '0' for r in records),
            'regular_members_by_plugin': dict(sorted(plugins.items())),
            'first_tar_terminator_offset': next_offset,
            'archive_bytes': next(iter(archive_sizes)),
            'uninspected_bytes_after_first_zero_header': next(iter(archive_sizes)) - next_offset - 512,
            'scope': 'Contiguous ordinary tar header chain to first zero terminator; no payloads or values inspected.',
            'records': records}


if __name__ == '__main__':
    print(json.dumps(audit(Path(__file__).resolve().parent), indent=2))
