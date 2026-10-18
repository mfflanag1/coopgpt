#!/usr/bin/env python3
"""Verify the included metadata-byte ledger without network or outcome decoding.

This checks saved-byte integrity and archive placement, not physical feasibility,
remote authenticity, complete network traffic, or ownership/sponsor rights.
Sparse Parquet wrappers and downloaded documentation are not needed.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import struct
import tarfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(root):
    def read(name):
        return json.loads((root / name).read_text())

    rows = []
    documentation_bytes = 0
    inputs = {}
    for folder, name in [('metadata', 'metadata_requests.jsonl'),
                         ('m100_may_metadata', 'm100_may_metadata/requests.jsonl'),
                         ('m100_may_footers', 'm100_may_footers/requests.jsonl')]:
        raw = (root / name).read_bytes()
        inputs[name] = digest(raw)
        for row in map(json.loads, raw.decode().splitlines()):
            if not row['kind'].startswith('dataset_'):
                documentation_bytes += row['body_bytes']
                continue
            require(row['kind'] in {'dataset_archive_metadata', 'dataset_footer_metadata'}, 'Unexpected dataset request kind')
            require(row['status'] == 206 and not row.get('error'), 'Dataset request was not a successful range')
            require(isinstance(row['start'], int) and row['start'] >= 0, 'Invalid range start')
            require(row['body_bytes'] == row['length'] and row['length'] > 0, 'Invalid range length')
            found = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', row['content_range'])
            require(found is not None, 'Malformed Content-Range')
            start, end, total = map(int, found.groups())
            require(start == row['start'] and end == start + row['length'] - 1 and end < total, 'Inconsistent Content-Range')
            path = f"{folder}/range_{start}_{row['length']}.bin"
            body = (root / path).read_bytes()
            require(len(body) == row['length'] and digest(body) == row['sha256'], 'Saved range mismatch: ' + path)
            inputs[path] = digest(body)
            rows.append((row, body))

    dataset_bytes = sum(row['body_bytes'] for row, _ in rows)
    require(dataset_bytes == 468255 and len(rows) == 334, 'Unexpected frozen acquisition totals')
    require(documentation_bytes == 68537, 'Documentation ledger total changed')
    require(dataset_bytes <= 100000000, 'Dataset-byte cap exceeded')
    by_range = {(row['kind'], row['start'], row['length']): body for row, body in rows}
    require(len(by_range) == len(rows), 'Duplicate range keys need explicit accounting')
    headers = read('m100_may_metadata/report.json')
    footers = read('m100_may_footers/report.json')
    for name in ['m100_may_metadata/report.json', 'm100_may_footers/report.json']:
        inputs[name] = digest((root / name).read_bytes())
    require(headers['status'] == 'COMPLETE_TO_FIRST_END_MARKER' and headers['error'] is None, 'Incomplete tar ledger')
    validated_entries = {}
    expected_header_offset = 0
    expected_header_ranges = set()
    for entry in headers['entries']:
        require(entry['offset'] == expected_header_offset + 512, 'Tar traversal offset disagreement')
        key = ('dataset_archive_metadata', expected_header_offset, 512)
        raw = by_range[key]
        expected_header_ranges.add(key)
        parsed = tarfile.TarInfo.frombuf(raw, 'utf-8', 'surrogateescape')
        require((parsed.name, parsed.size, parsed.type.decode()) == (entry['name'], entry['size'], entry['type']), 'Tar header disagreement')
        require(entry['name'] not in validated_entries, 'Duplicate tar name needs explicit resolution')
        validated_entries[entry['name']] = (entry['offset'], entry['size'], entry['type'])
        expected_header_offset = entry['offset'] + 512 * ((entry['size'] + 511) // 512)
    end_key = ('dataset_archive_metadata', expected_header_offset, 512)
    require(by_range[end_key] == bytes(512), 'First tar end marker is not zero')
    require(headers['next_offset'] == expected_header_offset, 'Tar end position disagreement')
    expected_header_ranges.add(end_key)
    require({key for key in by_range if key[0] == 'dataset_archive_metadata'} == expected_header_ranges,
            'Unaccounted tar-header ranges')
    selected = {}
    for entry in headers['selected_members']:
        require(entry['name'] not in selected, 'Duplicate selected member name')
        require(validated_entries.get(entry['name']) == (entry['offset'], entry['size'], entry['type']),
                'Selected member not bound to a validated tar entry')
        require(entry['type'] == '0', 'Selected member is not a regular file')
        selected[entry['name']] = entry
    require(footers['status'] == 'COMPLETE_METADATA_ONLY' and footers['error'] is None, 'Incomplete footer ledger')
    require(footers['cumulative_dataset_bytes'] == dataset_bytes, 'Footer cumulative mismatch')
    require(footers['power_state_payload_values_read'] == 0, 'Recorded value-read boundary changed')
    expected_footer_ranges = set()
    footer_names = set()
    for member in footers['members']:
        require(member['name'] not in footer_names, 'Duplicate footer member')
        footer_names.add(member['name'])
        require(member['name'] in selected, 'Footer member absent from selected validated entries')
        source = selected[member['name']]
        require(member['member_size'] == source['size'], 'Footer member-size disagreement')
        start, size = source['offset'], source['size']
        require(by_range[('dataset_footer_metadata', start, 4)] == b'PAR1', 'Invalid Parquet header marker')
        tail = by_range[('dataset_footer_metadata', start + size - 8, 8)]
        length = struct.unpack('<I', tail[:4])[0]
        require(tail[4:] == b'PAR1' and length == member['footer_size'], 'Invalid Parquet tail marker or footer length')
        raw = by_range[('dataset_footer_metadata', start + size - 8 - length, length)]
        require(digest(raw) == member['footer_sha256'], 'Footer hash mismatch')
        expected_footer_ranges.update({('dataset_footer_metadata', start, 4),
                                       ('dataset_footer_metadata', start + size - 8, 8),
                                       ('dataset_footer_metadata', start + size - 8 - length, length)})
    require({key for key in by_range if key[0] == 'dataset_footer_metadata'} == expected_footer_ranges,
            'Unaccounted footer ranges')
    require(all(int(row['content_range'].rsplit('/', 1)[1]) == headers['archive_bytes'] for row, _ in rows),
            'Remote archive-size metadata disagreement')
    require(sum(row['body_bytes'] for row, _ in rows if row['kind'] == 'dataset_archive_metadata') == 166400, 'Header-byte mismatch')
    require(sum(row['body_bytes'] for row, _ in rows if row['kind'] == 'dataset_footer_metadata') == 301855, 'Footer-byte mismatch')
    return {'status': 'PASS', 'checked_utc': datetime.now(timezone.utc).isoformat(),
            'dataset_range_requests': len(rows), 'dataset_body_bytes': dataset_bytes,
            'tar_header_bytes': 166400, 'footer_marker_and_footer_bytes': 301855,
            'documentation_body_bytes_from_ledger_only': documentation_bytes,
            'footer_members': len(footers['members']), 'inputs_sha256': inputs,
            'scope': 'Saved metadata bytes and ledger placement only; no decoding of power/state values or footer statistics, no network, no sparse wrapper, no new outcome inspection.',
            'limits': 'Recorded documentation totals are not a fresh body-integrity check of excluded originals. Saved hashes do not independently authenticate the remote release or validate economic/physical feasibility.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent,
                        help='Included application evidence directory; defaults beside this script')
    args = parser.parse_args()
    print(json.dumps(verify(args.root.resolve()), indent=2))


if __name__ == '__main__':
    main()
