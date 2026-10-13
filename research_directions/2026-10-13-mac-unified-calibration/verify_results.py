#!/usr/bin/env python3
"""Independent stdlib audit of the frozen Mac calibration; never runs GPU work.

The mathematical oracle uses integer arithmetic and the input's row-7/column-11
periodicity. It imports no collector, Swift bridge, BLAS, or candidate reducer.
"""
import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import struct

ORDER = [256, 512, 1024, 1024, 256, 512, 512, 1024, 256]
CAP = 64 * 1024 * 1024
REQUIRED_FROZEN = {'PROTOCOL.txt', 'WORKLOAD.json', 'calibrate.swift',
                   'capture_inventory.py', 'run_calibration.py'}


def strict_json(path):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('Duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    def nonfinite(value):
        raise ValueError('Nonfinite JSON number: ' + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=nonfinite)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expected_hash(n):
    """Exact C[i,j] depends only on i mod 7 and j mod 11, for fixed n."""
    if type(n) is not int or not 1 <= n <= 1024:
        raise ValueError('Oracle supports prescribed bounded dimensions only')
    representatives = [[sum((((i + 3*k) % 7) - 3) * (((5*k + j) % 11) - 5)
                            for k in range(n)) for j in range(11)] for i in range(7)]
    # Conversion is exact: integer absolute values <= 15*n < 2**24. Integer zero
    # becomes positive Float32 zero. Each byte row excludes any GPU row padding.
    rows = [b''.join(struct.pack('<f', representatives[i][j % 11]) for j in range(n))
            for i in range(7)]
    sha = hashlib.sha256()
    for i in range(n):
        sha.update(rows[i % 7])
    return sha.hexdigest()


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def finite(value, minimum=0, strict=False):
    return (type(value) in (int, float) and math.isfinite(value) and
            (value > minimum if strict else value >= minimum))


def utc_time(value):
    if not isinstance(value, str):
        raise ValueError('Missing timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError('Timestamp is not UTC')
    return parsed


def audit_capture(root, capture, binary=None):
    root, capture = Path(root), Path(capture)
    errors, rows = [], []
    def check(ok, message):
        if not ok:
            errors.append(message)
    def expect_time_order(obj, start, end, label):
        try:
            check(utc_time(obj[end]) >= utc_time(obj[start]), label + ': reversed interval')
        except (ValueError, KeyError, TypeError):
            errors.append(label + ': missing/invalid UTC interval')
    result = {'schema_version': 1, 'audit_passed': False, 'errors': errors,
              'method': 'Independent integer periodic oracle; full row-major Float32-LE SHA256, +0 normalization; no collector imports',
              'interpretation': 'Checks recorded content and frozen-source provenance, not hardware attestation, energy, scheduling or pooling gains.',
              'rows': rows, 'binary_bytes_reverified': False,
              'auditor_source_sha256': digest(Path(__file__))}
    try:
        freeze_path = root / 'DESIGN_FREEZE.json'
        freeze = strict_json(freeze_path)
        sources = freeze['source_sha256']
        if not isinstance(sources, dict):
            raise ValueError('Frozen sources must be a mapping')
        check(REQUIRED_FROZEN <= set(sources), 'Freeze omits required source/protocol/oracle files')
        for name, expected in sources.items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or name != rel.as_posix():
                raise ValueError('Noncanonical frozen source path')
            check(isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected) is not None,
                  'Malformed source hash: ' + name)
            check(digest(root / name) == expected, 'Frozen source changed: ' + name)
        binary_sha = freeze['binary_sha256']
        check(isinstance(binary_sha, str) and re.fullmatch('[0-9a-f]{64}', binary_sha) is not None,
              'Malformed binary hash')
        if binary is not None:
            check(digest(binary) == binary_sha, 'Binary does not match frozen hash')
            result['binary_bytes_reverified'] = digest(binary) == binary_sha
        workload = strict_json(root / 'WORKLOAD.json')
        check(workload.get('dimensions') == ORDER and workload.get('warmup_dimension') == 64,
              'Workload dimensions differ from reviewed fixed experiment')
        check(workload.get('a_rule') == '((i+3*k)%7)-3' and
              workload.get('b_rule') == '((5*k+j)%11)-5', 'Workload formulas differ')
        check(workload.get('outer_timeout_seconds') == 120, 'Workload timeout differs')
        golden = [sum((((i + 3*k) % 7) - 3) * (((5*k + j) % 11) - 5)
                      for k in range(4)) for i in range(4) for j in range(4)]
        check(workload.get('golden_dimension') == 4 and workload.get('golden_rowmajor') == golden,
              'Golden values do not equal independent integer product')
        raw, execution, inventory = (strict_json(capture / name) for name in
                                    ('RAW.json', 'EXECUTION.json', 'INVENTORY.json'))
        result['input_sha256'] = {name: digest(capture / name) for name in
                                  ('RAW.json', 'EXECUTION.json', 'INVENTORY.json')}
        result['freeze_sha256'] = digest(freeze_path)
        check(execution.get('freeze_sha256') == result['freeze_sha256'], 'Execution/freeze identity mismatch')
        check(execution.get('returncode') == 0 and type(execution.get('returncode')) is int,
              'Execution did not return exact integer zero')
        check(execution.get('process_status') == 'completed', 'Process incomplete or timed out')
        check(execution.get('source_changed') is False, 'Execution source changed or status absent')
        check(execution.get('raw_output_present') is True, 'Execution does not confirm raw output')
        check(execution.get('timeout_seconds') == 120, 'Execution timeout differs')
        check(finite(execution.get('process_elapsed_seconds'), strict=True), 'Invalid process elapsed time')
        command = execution.get('command')
        check(isinstance(command, list) and len(command) == 3 and command[1] == '--output'
              and isinstance(command[2], str) and Path(command[2]).name == 'RAW.json',
              'Execution command does not name expected output')
        expect_time_order(execution, 'started_utc', 'finished_utc', 'Execution')
        expect_time_order(raw, 'started_at', 'completed_at', 'Native report')
        check(raw.get('schema_version') == 1 and type(raw.get('schema_version')) is int,
              'Wrong raw schema')
        check(raw.get('protocol_id') == 'mac-mps-f32-correctness-v1', 'Wrong protocol ID')
        check(raw.get('size_order') == ORDER, 'Recorded size order differs')
        for key, expected in [('dtype', 'Float32'), ('matrix_layout', 'row-major'), ('storage_mode', 'shared')]:
            check(raw.get(key) == expected, 'Wrong native ' + key)
        check(raw.get('gate_passed') is True and raw.get('cpu_self_test_passed') is True,
              'Native gate/self-test did not pass')
        check(raw.get('failure') is None, 'Native report contains failure')
        check(raw.get('has_unified_memory') is True, 'Device does not report unified memory')
        check(raw.get('explicit_buffer_and_reference_cap_bytes') == CAP, 'Memory cap differs')
        max_buffer = raw.get('max_buffer_length')
        check(integer(max_buffer, 1), 'Invalid maximum buffer length')
        check(integer(raw.get('recommended_max_working_set_size'), 1), 'Invalid advisory working-set quantity')
        hardware = inventory['hardware']
        check(hardware.get('platform') == 'Darwin', 'Inventory is not a Mac')
        ram = hardware.get('physical_ram_bytes', {})
        check(ram.get('status') == 'observed' and integer(ram.get('value'), 1), 'Physical RAM unavailable')
        gpu = hardware.get('gpu_inventory', {})
        devices = gpu.get('devices')
        check(gpu.get('status') == 'observed' and isinstance(devices, list) and
              any(isinstance(d, dict) and d.get('model') == raw.get('device_name') for d in devices),
              'Native device is not matched by selected hardware inventory')
        check(inventory.get('placement_ready') is False and inventory.get('capacity_kind') == 'hardware_totals',
              'Inventory improperly promoted to allocatable capacity')
        trials = raw.get('trials')
        if not isinstance(trials, list):
            raise ValueError('Native trials are not a list')
        check(len(trials) == 9, 'Missing or extra measured trials')
        planned = [(64, 0, 'warmup', raw.get('warmup'))] + [
            (n, i+1, 'measured', trials[i] if i < len(trials) else None) for i, n in enumerate(ORDER)]
        expected_hashes = {n: expected_hash(n) for n in [64, 256, 512, 1024]}
        result['expected_output_sha256'] = {str(n): h for n, h in expected_hashes.items()}
        for n, index, kind, row in planned:
            label = f'{kind}[{index}] N={n}'
            old_errors = len(errors)
            if not isinstance(row, dict):
                errors.append(label + ': missing/non-object row')
                continue
            check(row.get('n') == n and type(row.get('n')) is int and row.get('index') == index
                  and type(row.get('index')) is int and row.get('kind') == kind, label + ': order/identity mismatch')
            check(row.get('passed') is True and row.get('failure') is None, label + ': failed row')
            check(row.get('command_buffer_status') in ('completed', 'MTLCommandBufferStatus(rawValue: 4)') and row.get('command_buffer_error') is None,
                  label + ': command did not complete cleanly')
            for field in ['gpu_output_sha256', 'cpu_reference_sha256']:
                check(row.get(field) == expected_hashes[n], label + ': incorrect ' + field)
            measured = row.get('check', {})
            check(isinstance(measured, dict), label + ': missing comparison')
            if isinstance(measured, dict):
                for key, expected in [('compared_elements', n*n), ('mismatch_count', 0), ('nonfinite_count', 0)]:
                    check(measured.get(key) == expected and type(measured.get(key)) is int,
                          label + ': invalid ' + key)
                for key in ['max_abs_error', 'max_abs_finite_error']:
                    check(finite(measured.get(key)) and measured.get(key) == 0, label + ': nonzero/invalid ' + key)
            stride = row.get('row_bytes')
            check(integer(stride, 4*n) and stride % 4 == 0, label + ': invalid row stride')
            for key, expected in [('buffer_payload_bytes', 12*n*n), ('cpu_reference_payload_bytes', 4*n*n),
                                  ('cpu_hash_scratch_bytes', 4*n)]:
                check(row.get(key) == expected and type(row.get(key)) is int, label + ': wrong ' + key)
            length, allocated = row.get('buffer_length_bytes'), row.get('buffer_allocated_bytes')
            check(integer(length, 1) and integer(stride, 1) and length == 3*n*stride,
                  label + ': incorrect buffer-length accounting')
            check(integer(allocated, 1) and integer(length, 1) and allocated >= length,
                  label + ': invalid actual allocated bytes')
            explicit_bytes = allocated + 4*n*n + 4*n if integer(allocated) else None
            check(integer(explicit_bytes, 1) and explicit_bytes <= CAP, label + ': explicit cap exceeded')
            check(integer(stride, 1) and integer(max_buffer, 1) and n*stride <= max_buffer,
                  label + ': maximum per-buffer length exceeded')
            for key in ['device_allocated_before_buffers_sample', 'device_allocated_with_buffers_sample']:
                check(integer(row.get(key)), label + ': invalid allocation sample')
            host = row.get('submit_to_complete_seconds')
            check(finite(host, strict=True), label + ': invalid host interval')
            timestamps = [row.get(k) for k in ['gpu_start_time', 'gpu_end_time', 'gpu_interval_seconds']]
            if any(t is not None for t in timestamps):
                check(all(finite(t, strict=True) for t in timestamps), label + ': incomplete/invalid GPU interval')
                if all(finite(t, strict=True) for t in timestamps):
                    start, end, duration = timestamps
                    check(end > start and math.isclose(end-start, duration, rel_tol=1e-9, abs_tol=1e-12),
                          label + ': inconsistent GPU interval')
            rows.append({'index': index, 'kind': kind, 'n': n, 'verified_elements': n*n,
                         'expected_sha256': expected_hashes[n], 'checks_passed': len(errors) == old_errors,
                         'explicit_allocated_plus_reference_and_hash_bytes': explicit_bytes,
                         'submit_to_complete_seconds': host,
                         'gpu_interval_seconds': row.get('gpu_interval_seconds')})
        result['measured_elements'] = sum(n*n for n in ORDER)
        result['warmup_elements'] = 64*64
        result['checked_trial_rows'] = len(rows)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(type(exc).__name__ + ': ' + str(exc))
    result['audit_passed'] = not errors
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path, help='New audit JSON; never overwritten')
    parser.add_argument('--binary', type=Path, help='Optional exact executable to recheck against freeze')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Audit output already exists')
    result = audit_capture(Path(__file__).resolve().parent, args.capture, args.binary)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'audit_passed': result['audit_passed'], 'errors': result['errors'],
                      'output': str(args.output)}))
    return 0 if result['audit_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
