#!/usr/bin/env python3
"""Read-only, hash-pinned descriptive audit; no optimization or missing-value imputation.

Usage: python3 analyze_traces.py --cache /path/to/raw --output NEWPATH
The source lock and download record are read beside this script. CSV parsing streams
rows; only counters, identifiers, and SHA256 row fingerprints remain in memory.
"""
import argparse
from collections import Counter
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

P23 = 'cluster-trace-gpu-v2023/csv/'
PSP = 'cluster-trace-v2026-spot-gpu/'
TABLES = {
    P23 + 'openb_node_list_gpu_node.csv': {
        'id': 'sn', 'numeric': ['cpu_milli', 'memory_mib', 'gpu'],
        'categorical': ['model'], 'kind': 'node'},
    P23 + 'openb_pod_list_default.csv': {
        'id': 'name', 'numeric': ['cpu_milli', 'memory_mib', 'num_gpu', 'gpu_milli',
                                'creation_time', 'deletion_time', 'scheduled_time'],
        'categorical': ['gpu_spec', 'qos', 'pod_phase'], 'kind': 'pod2023'},
    P23 + 'openb_pod_list_gpuspec33.csv': {
        'id': 'name', 'numeric': ['cpu_milli', 'memory_mib', 'num_gpu', 'gpu_milli',
                                'creation_time', 'deletion_time', 'scheduled_time'],
        'categorical': ['gpu_spec', 'qos', 'pod_phase'], 'kind': 'pod2023'},
    PSP + 'node_info_df.csv': {
        'id': 'node_name', 'numeric': ['gpu_capacity_num', 'cpu_num'],
        'categorical': ['gpu_model'], 'kind': 'node'},
    PSP + 'job_info_df.csv': {
        'id': 'job_name', 'numeric': ['cpu_request', 'gpu_request', 'worker_num',
                                   'submit_time', 'duration'],
        'categorical': ['organization', 'gpu_model', 'job_type'], 'kind': 'job2026'},
}
CANONICAL_COLUMNS = {
    'node': ['id', 'owner', 'cpu_units', 'ram_mib', 'gpus',
             'device_id', 'family', 'vram_mib', 'snapshot_time', 'current_reservations'],
    'job': ['id', 'priority', 'cpu_units', 'ram_mib', 'gpu_count', 'min_vram_mib',
            'allowed_families', 'allowed_owners', 'same_node_gang', 'snapshot_time'],
}
SAMPLE_LIMIT = 10
SOURCE_REPOSITORY = 'https://github.com/alibaba/clusterdata'
SOURCE_RAW_BASE = 'https://raw.githubusercontent.com/alibaba/clusterdata/'


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_json(path):
    with Path(path).open(encoding='utf-8') as handle:
        return json.load(handle, object_pairs_hook=_unique_object,
                         parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def file_hashes(path):
    size = path.stat().st_size
    sha = hashlib.sha256()
    blob = hashlib.sha1(('blob ' + str(size) + '\0').encode())
    read_size = 0
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            sha.update(block)
            blob.update(block)
            read_size += len(block)
    if read_size != size:
        raise ValueError('file changed size during hashing: ' + str(path))
    return {'bytes': size, 'sha256': sha.hexdigest(), 'git_blob_sha1': blob.hexdigest()}


def _indexed_files(metadata):
    entries = metadata.get('files')
    if not isinstance(entries, list) or not entries:
        raise ValueError('nonempty metadata files list required')
    result = {}
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get('path'), str):
            raise ValueError('invalid file entry')
        raw = item['path']
        path = PurePosixPath(raw)
        if path.is_absolute() or '..' in path.parts or raw != path.as_posix() or raw in ('', '.'):
            raise ValueError('unsafe or noncanonical cache path')
        if raw in result:
            raise ValueError('duplicate metadata path: ' + raw)
        result[raw] = item
    return result


def verify_inputs(cache, lock, record):
    """Check every locked file, including documentation, before any CSV parsing."""
    cache = Path(cache).resolve()
    if lock.get('repository') != SOURCE_REPOSITORY:
        raise ValueError('unexpected source repository')
    revision = lock.get('revision')
    if not isinstance(revision, str) or not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('revision must be a lowercase 40-hex Git identity')
    if revision != record.get('revision'):
        raise ValueError('revision mismatch')
    expected, downloads = _indexed_files(lock), _indexed_files(record)
    if set(expected) != set(downloads):
        raise ValueError('lock/download file-set mismatch')
    verified = {}
    for name in sorted(expected):
        upstream, downloaded = expected[name], downloads[name]
        if upstream.get('url') != SOURCE_RAW_BASE + revision + '/' + name:
            raise ValueError('source URL does not match pinned repository/revision/path: ' + name)
        for field in ('bytes', 'git_blob_sha1', 'url'):
            if upstream.get(field) != downloaded.get(field):
                raise ValueError('lock/download mismatch: ' + name + ':' + field)
        if type(upstream.get('bytes')) is not int or upstream['bytes'] < 0:
            raise ValueError('invalid locked size')
        if not re.fullmatch('[0-9a-f]{40}', upstream.get('git_blob_sha1', '')):
            raise ValueError('invalid Git blob identity')
        if not re.fullmatch('[0-9a-f]{64}', downloaded.get('sha256', '')):
            raise ValueError('invalid SHA256 identity')
        target = (cache / name).resolve()
        if not target.is_relative_to(cache) or not target.is_file():
            raise ValueError('missing file or escaped cache: ' + name)
        actual = file_hashes(target)
        for field in ('bytes', 'git_blob_sha1', 'sha256'):
            if actual[field] != downloaded[field]:
                raise ValueError('cache integrity mismatch: ' + name + ':' + field)
        verified[name] = dict(actual, url=upstream['url'])
    if record.get('total_bytes') != sum(row['bytes'] for row in verified.values()):
        raise ValueError('download total-byte mismatch')
    return verified


def verify_design(lock_path):
    """Enforce the pre-audit design freeze and return its own identity for rechecking."""
    lock_path = Path(lock_path).resolve()
    if lock_path.name != 'SOURCE_LOCK.json':
        raise ValueError('frozen source lock must be named SOURCE_LOCK.json')
    base = lock_path.parent
    freeze_path = base / 'DESIGN_FREEZE.json'
    freeze = load_json(freeze_path)
    hashes = freeze.get('sha256')
    if not isinstance(hashes, dict) or set(hashes) != {'PROTOCOL.txt', 'SOURCE_LOCK.json'}:
        raise ValueError('design freeze must cover exactly protocol and source lock')
    for name, expected in sorted(hashes.items()):
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('invalid design-freeze SHA256: ' + name)
        if file_hashes(base / name)['sha256'] != expected:
            raise ValueError('design freeze mismatch: ' + name)
    return {'freeze_sha256': file_hashes(freeze_path)['sha256'], 'sha256': hashes}


def number(value):
    """Classify without treating sentinels, signs, decimals, or blanks as missing zero."""
    if value is None:
        return 'absent_cell', None
    if value.strip() == '':
        return 'blank', None
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError):
        return 'invalid', None
    if not parsed.is_finite():
        return 'nonfinite', None
    return 'finite', parsed


def decimal_text(value):
    if value == 0:
        return '0'
    # format 'f' avoids JSON floats and preserves exact decimal values.
    text = format(value, 'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text


class Numeric:
    def __init__(self):
        self.counts = Counter()
        self.values = Counter()
        self.examples = {'invalid': [], 'nonfinite': [], 'negative': [], 'nonintegral': []}

    def add(self, raw):
        category, value = number(raw)
        self.counts[category] += 1
        if category != 'finite':
            if category in self.examples and raw not in self.examples[category]:
                if len(self.examples[category]) < SAMPLE_LIMIT:
                    self.examples[category].append(raw)
            return
        sign = 'negative' if value < 0 else ('positive' if value > 0 else 'zero')
        integral = 'integral' if value == value.to_integral_value() else 'nonintegral'
        self.counts[sign] += 1
        self.counts[integral] += 1
        self.values[value] += 1
        for kind in (sign, integral):
            if kind in self.examples and raw not in self.examples[kind]:
                if len(self.examples[kind]) < SAMPLE_LIMIT:
                    self.examples[kind].append(raw)

    def report(self):
        keys = ['absent_cell', 'blank', 'invalid', 'nonfinite', 'finite',
                'negative', 'zero', 'positive', 'integral', 'nonintegral']
        items = sorted(self.values.items(), key=lambda item: (-item[1], item[0]))
        return {'counts': {key: self.counts[key] for key in keys},
                'minimum': decimal_text(min(self.values)) if self.values else None,
                'maximum': decimal_text(max(self.values)) if self.values else None,
                'distinct_finite_values': len(self.values),
                'most_frequent_values': [{'value': decimal_text(v), 'rows': n} for v, n in items[:20]],
                'distribution_truncated': len(items) > 20,
                'examples_first_seen': self.examples}


def category_report(counter):
    # These actual categorical columns have small support, except organizations.
    items = sorted(counter.items(), key=lambda item: (-item[1], '' if item[0] is None else item[0]))
    return {'distinct_values': len(counter),
            'values': [{'value': v, 'rows': n} for v, n in items]}


def gpu2023_category(row):
    n_kind, n = number(row.get('num_gpu'))
    if n_kind != 'finite' or n != n.to_integral_value() or not 0 <= n <= 8:
        return 'unexpected_num_gpu'
    if n == 0:
        return 'cpu_only'
    if n >= 2:
        return 'full_gpu_multi'
    g_kind, g = number(row.get('gpu_milli'))
    if g_kind != 'finite':
        return 'unexpected_single_gpu_milli'
    if g == 1000:
        return 'full_gpu_single'
    if 0 < g < 1000:
        return 'fractional_gpu_single'
    return 'unexpected_single_gpu_milli'


def csv_rows(path):
    """Yield exact header and every parsed record, including width anomalies."""
    with Path(path).open(encoding='utf-8', newline='') as handle:
        reader = csv.reader(handle, strict=True)
        header = next(reader, None)
        if header is None or not header or len(set(header)) != len(header):
            raise ValueError('empty or duplicate CSV header')
        yield header
        for cells in reader:
            yield cells


def audit_table(path, spec):
    iterator = csv_rows(path)
    header = next(iterator)
    numeric = {key: Numeric() for key in spec['numeric']}
    categorical = {key: Counter() for key in spec['categorical']}
    blanks, absent, identifiers, row_hashes = Counter(), Counter(), Counter(), Counter()
    shape_examples, gpu_examples = [], []
    shape_count, rows, blank_ids, missing_ids = 0, 0, 0, 0
    gpu_counts, milli_non_single = Counter(), Counter()
    negative_time_rows = Counter()
    for cells in iterator:
        rows += 1
        if len(cells) != len(header):
            shape_count += 1
            if len(shape_examples) < SAMPLE_LIMIT:
                shape_examples.append({'record': rows, 'cells': len(cells)})
        row = {key: cells[i] if i < len(cells) else None for i, key in enumerate(header)}
        row_hashes[hashlib.sha256(json.dumps(cells, ensure_ascii=False, separators=(',', ':')).encode()).digest()] += 1
        for key in header:
            if row[key] is None:
                absent[key] += 1
            elif row[key].strip() == '':
                blanks[key] += 1
        identifier = row.get(spec['id'])
        if identifier is None:
            missing_ids += 1
        elif not identifier.strip():
            blank_ids += 1
        else:
            identifiers[identifier] += 1
        for key, stats in numeric.items():
            stats.add(row.get(key))
        for key, counter in categorical.items():
            counter[row.get(key)] += 1
        if spec['kind'] == 'pod2023':
            category = gpu2023_category(row)
            gpu_counts[category] += 1
            if category.startswith('unexpected') and len(gpu_examples) < SAMPLE_LIMIT:
                gpu_examples.append({'id': identifier, 'category': category,
                                     'num_gpu': row.get('num_gpu'), 'gpu_milli': row.get('gpu_milli')})
            if category in ('cpu_only', 'full_gpu_multi'):
                milli_non_single[(category, row.get('gpu_milli'))] += 1
            for key in ('creation_time', 'scheduled_time', 'deletion_time'):
                kind, value = number(row.get(key))
                if kind == 'finite' and value < 0:
                    negative_time_rows[key] += 1
    required = CANONICAL_COLUMNS['node' if spec['kind'] == 'node' else 'job']
    result = {
        'header': header, 'rows': rows, 'id_column': spec['id'],
        'unique_nonblank_ids': len(identifiers), 'blank_id_rows': blank_ids,
        'absent_id_rows': missing_ids,
        'ids_with_duplicates': sum(n > 1 for n in identifiers.values()),
        'duplicate_id_rows_beyond_first': sum(n - 1 for n in identifiers.values()),
        'duplicate_ids_sample': sorted(k for k, n in identifiers.items() if n > 1)[:SAMPLE_LIMIT],
        'duplicate_row_fingerprints_beyond_first': sum(n - 1 for n in row_hashes.values()),
        'row_duplicate_method': 'SHA256 of exact parsed cell sequence; cryptographic fingerprint, not raw line bytes',
        'row_width_anomalies': {'rows': shape_count, 'first_records': shape_examples},
        'blank_cells_by_column': {key: blanks[key] for key in header},
        'absent_cells_by_column': {key: absent[key] for key in header},
        'numeric': {key: value.report() for key, value in numeric.items()},
        'categorical': {key: category_report(value) for key, value in categorical.items()},
        'literal_contract_columns_absent': sorted(set(required) - set(header)),
        'literal_contract_columns_present': sorted(set(required) & set(header)),
        'column_comparison_caution': 'Literal names only; aliases, units, derived fields and scientific completeness are not inferred.',
    }
    if spec['kind'] == 'pod2023':
        result['gpu_request_categories'] = {key: gpu_counts[key] for key in (
            'cpu_only', 'full_gpu_single', 'full_gpu_multi', 'fractional_gpu_single',
            'unexpected_num_gpu', 'unexpected_single_gpu_milli')}
        result['gpu_request_category_examples'] = gpu_examples
        result['gpu_milli_outside_single_gpu_rows'] = [
            {'category': cat, 'raw_gpu_milli': raw, 'rows': count}
            for (cat, raw), count in sorted(milli_non_single.items(), key=lambda p: (p[0][0], str(p[0][1]))) ]
        result['negative_timestamp_rows'] = dict(sorted(negative_time_rows.items()))
        result['gpu_category_semantics'] = (
            'README: num_gpu is integer 0..8; gpu_milli applies to num_gpu==1. '
            '0 is CPU-only; 1 with 1000 milli is whole; 1 with 0<milli<1000 is fractional; '
            '2..8 is full-GPU multi. gpu_milli for 0 or 2..8 is retained but not interpreted. '
            'Signs, nonintegrality and timestamps are descriptive; negative values are not silently rejected or repaired.')
    return result


def _rows_by_id(path):
    iterator = csv_rows(path)
    header = next(iterator)
    if 'name' not in header:
        raise ValueError('augmentation comparison requires name column')
    rows = {}
    for cells in iterator:
        if len(cells) != len(header):
            raise ValueError('ambiguous augmentation join: malformed row width')
        row = dict(zip(header, cells))
        key = row['name']
        if not key.strip() or key in rows:
            raise ValueError('ambiguous augmentation join: blank or duplicate name')
        rows[key] = row
    return header, rows


def _nonblank_compatibility(row):
    raw = row.get('gpu_spec', '')
    return bool(raw.strip())


def _source_type_constraint(row):
    raw = row.get('gpu_spec', '')
    # README explicitly calls nan unconstrained. Empty CSV cells remain a separate
    # descriptive category, not an inferred compatibility list.
    return bool(raw.strip()) and raw.strip().lower() != 'nan'


def compare_augmentation(default_path, augmented_path):
    left_header, left = _rows_by_id(default_path)
    right_header, right = _rows_by_id(augmented_path)
    common = sorted(set(left) & set(right))
    fields = sorted(set(left_header) | set(right_header))
    changed = Counter()
    examples = []
    changed_rows = 0
    for key in common:
        differences = {field: {'default': left[key].get(field), 'augmented': right[key].get(field)}
                       for field in fields if left[key].get(field) != right[key].get(field)}
        if differences:
            changed_rows += 1
            changed.update(differences.keys())
            if len(examples) < SAMPLE_LIMIT:
                examples.append({'name': key, 'changes': differences})
    return {
        'join_key': 'name', 'default_rows': len(left), 'augmented_rows': len(right),
        'identical_id_sets': set(left) == set(right), 'shared_ids': len(common),
        'default_only_ids': len(set(left) - set(right)),
        'augmented_only_ids': len(set(right) - set(left)),
        'default_only_sample': sorted(set(left) - set(right))[:SAMPLE_LIMIT],
        'augmented_only_sample': sorted(set(right) - set(left))[:SAMPLE_LIMIT],
        'identical_headers': left_header == right_header,
        'changed_shared_rows': changed_rows,
        'changed_cells_by_field': {field: changed[field] for field in fields},
        'modification_examples': examples,
        'nonblank_gpu_spec_rows': {'default': sum(map(_nonblank_compatibility, left.values())),
                                  'augmented': sum(map(_nonblank_compatibility, right.values()))},
        'nonblank_non_nan_gpu_spec_rows': {'default': sum(map(_source_type_constraint, left.values())),
                                          'augmented': sum(map(_source_type_constraint, right.values()))},
        'qualification': 'Source README calls gpuspec traces augmented. Modified requirements are not established as observed per-job GPU-type restrictions. Literal nan is documented as no constraint; blank cells are reported separately.'}


def run(cache, lock_path, record_path):
    frozen_design = verify_design(lock_path)
    lock, record = load_json(lock_path), load_json(record_path)
    verified = verify_inputs(cache, lock, record)
    if not set(TABLES).issubset(verified):
        raise ValueError('required analysis tables missing from lock')
    tables = {name: audit_table(Path(cache) / name, spec) for name, spec in sorted(TABLES.items())}
    augmentation = compare_augmentation(Path(cache) / (P23 + 'openb_pod_list_default.csv'),
                                       Path(cache) / (P23 + 'openb_pod_list_gpuspec33.csv'))
    if verify_inputs(cache, lock, record) != verified:
        raise ValueError('cache changed during analysis')
    if verify_design(lock_path) != frozen_design:
        raise ValueError('design freeze changed during analysis')
    return {'schema_version': 1, 'source_repository': lock.get('repository'),
            'source_revision': lock['revision'], 'verified_inputs': verified,
            'tables': tables, 'augmentation_comparison': augmentation,
            'interpretation_limits': [
                'Every parsed CSV record is counted. No anomaly filtering, imputation, optimizer or cross-release join.',
                'Numeric signs and nonintegrality are descriptive categories, not a judgment of source-record validity.',
                'Spot2026 worker_num, cpu_request and gpu_request are separate observed columns; no per-worker multiplication is inferred.',
                'Declared node capacities are not current free capacity; organization is not resource-owner permission.',
                'No real placement comparison, performance, energy, welfare or novelty conclusion follows from this audit.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', required=True, type=Path, help='Raw source-cache directory')
    parser.add_argument('--output', required=True, type=Path, help='New JSON output path; never overwritten')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output already exists; choose a new path')
    base = Path(__file__).resolve().parent
    try:
        result = run(args.cache, base / 'SOURCE_LOCK.json', base / 'DOWNLOAD_RECORD.json')
        with args.output.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write('\n')
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, 'audit failed: ' + str(error) + '\n')
    print(json.dumps({'output': str(args.output), 'rows': {
        name: table['rows'] for name, table in result['tables'].items()},
        'augmentation_changed_rows': result['augmentation_comparison']['changed_shared_rows']}, sort_keys=True))


if __name__ == '__main__':
    main()
