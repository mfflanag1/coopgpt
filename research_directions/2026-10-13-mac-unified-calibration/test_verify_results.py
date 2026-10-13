"""Independent audit mutation controls; all captures here are synthetic fixtures."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

import verify_results as audit


class MathematicalOracle(unittest.TestCase):
    def test_golden_digest(self):
        self.assertEqual(audit.expected_hash(4),
                         '3528d12e2f4ce4f09b261bebe1f87a9bf13961f72a9f8fb5e8b10517db08d24a')

    def test_periodicity_matches_direct_full_integer_loop(self):
        for n in (1, 4, 7, 11, 19):
            direct = [sum((((i + 3*k) % 7) - 3) * (((5*k + j) % 11) - 5)
                          for k in range(n)) for i in range(n) for j in range(n)]
            expected = hashlib.sha256(b''.join(struct.pack('<f', x) for x in direct)).hexdigest()
            self.assertEqual(audit.expected_hash(n), expected)


class MutationControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.capture = self.root / 'capture'; self.capture.mkdir()
        self.binary = self.root / 'fixture-binary'; self.binary.write_bytes(b'never executed')
        for name in audit.REQUIRED_FROZEN:
            (self.root / name).write_text('fixture: ' + name)
        source_workload = Path(__file__).with_name('WORKLOAD.json')
        (self.root / 'WORKLOAD.json').write_bytes(source_workload.read_bytes())
        self.freeze = {'source_sha256': {name: audit.digest(self.root/name) for name in audit.REQUIRED_FROZEN},
                       'binary_sha256': audit.digest(self.binary)}
        self.save('DESIGN_FREEZE.json', self.freeze, self.root)
        self.hashes = {n: audit.expected_hash(n) for n in (64, 256, 512, 1024)}
        def row(n, index, kind):
            return {'n': n, 'index': index, 'kind': kind, 'row_bytes': 4*n,
                    'buffer_payload_bytes': 12*n*n, 'buffer_length_bytes': 12*n*n,
                    'buffer_allocated_bytes': 12*n*n, 'cpu_reference_payload_bytes': 4*n*n,
                    'cpu_hash_scratch_bytes': 4*n, 'device_allocated_before_buffers_sample': 0,
                    'device_allocated_with_buffers_sample': 12*n*n,
                    'submit_to_complete_seconds': .01, 'gpu_start_time': 1.0,
                    'gpu_end_time': 1.001, 'gpu_interval_seconds': 1.001-1.0,
                    'gpu_output_sha256': self.hashes[n], 'cpu_reference_sha256': self.hashes[n],
                    'command_buffer_status': 'completed', 'passed': True,
                    'check': {'compared_elements': n*n, 'mismatch_count': 0, 'nonfinite_count': 0,
                              'max_abs_error': 0, 'max_abs_finite_error': 0}}
        self.raw = {'schema_version': 1, 'protocol_id': 'mac-mps-f32-correctness-v1',
                    'started_at': '2026-10-13T00:00:00Z', 'completed_at': '2026-10-13T00:00:01Z',
                    'size_order': audit.ORDER, 'dtype': 'Float32', 'matrix_layout': 'row-major',
                    'storage_mode': 'shared', 'device_name': 'Fixture GPU', 'has_unified_memory': True,
                    'max_buffer_length': 64*1024*1024, 'recommended_max_working_set_size': 1024**3,
                    'explicit_buffer_and_reference_cap_bytes': audit.CAP,
                    'cpu_self_test_passed': True, 'gate_passed': True,
                    'warmup': row(64, 0, 'warmup'),
                    'trials': [row(n, i+1, 'measured') for i, n in enumerate(audit.ORDER)]}
        self.execution = {'returncode': 0, 'process_status': 'completed', 'source_changed': False,
                          'raw_output_present': True, 'timeout_seconds': 120,
                          'process_elapsed_seconds': 1.0, 'freeze_sha256': audit.digest(self.root/'DESIGN_FREEZE.json'),
                          'command': [str(self.binary), '--output', str(self.capture/'RAW.json')],
                          'started_utc': '2026-10-13T00:00:00Z', 'finished_utc': '2026-10-13T00:00:01Z'}
        self.inventory = {'placement_ready': False, 'capacity_kind': 'hardware_totals',
                          'hardware': {'platform': 'Darwin',
                                       'physical_ram_bytes': {'status': 'observed', 'value': 8*1024**3},
                                       'gpu_inventory': {'status': 'observed', 'devices': [{'model': 'Fixture GPU'}]}}}

    def save(self, name, data, directory=None):
        ((directory or self.capture)/name).write_text(json.dumps(data))

    def check(self):
        for name, data in [('RAW.json', self.raw), ('EXECUTION.json', self.execution), ('INVENTORY.json', self.inventory)]:
            self.save(name, data)
        return audit.audit_capture(self.root, self.capture, self.binary)

    def test_valid_fixture_and_raw_enum_representation(self):
        self.assertTrue(self.check()['audit_passed'])
        self.raw['warmup']['command_buffer_status'] = 'MTLCommandBufferStatus(rawValue: 4)'
        self.assertTrue(self.check()['audit_passed'])

    def test_independent_gpu_and_cpu_hash_mutations_are_rejected(self):
        for key in ('gpu_output_sha256', 'cpu_reference_sha256'):
            original = self.raw['trials'][0][key]
            self.raw['trials'][0][key] = '0'*64
            self.assertFalse(self.check()['audit_passed'])
            self.raw['trials'][0][key] = original

    def test_counts_failures_and_order_cannot_be_hidden_by_gate_flag(self):
        original = copy.deepcopy(self.raw)
        mutations = [lambda r:r['trials'].pop(),
                     lambda r:r['trials'].reverse(),
                     lambda r:r['trials'][0]['check'].update(compared_elements=1),
                     lambda r:r['trials'][0]['check'].update(mismatch_count=1),
                     lambda r:r['trials'][0]['check'].update(nonfinite_count=1),
                     lambda r:r['trials'][0]['check'].update(max_abs_error=None),
                     lambda r:r['trials'][0].update(passed=False),
                     lambda r:r.update(gate_passed=False)]
        for mutate in mutations:
            self.raw = copy.deepcopy(original); mutate(self.raw)
            self.assertFalse(self.check()['audit_passed'])

    def test_cap_timing_and_boolean_counts_are_rejected(self):
        original = copy.deepcopy(self.raw)
        for mutation in ({'buffer_allocated_bytes': audit.CAP}, {'submit_to_complete_seconds': 0},
                         {'gpu_interval_seconds': -.1}, {'gpu_end_time': None}):
            self.raw = copy.deepcopy(original); self.raw['trials'][0].update(mutation)
            self.assertFalse(self.check()['audit_passed'])
        self.raw = copy.deepcopy(original); self.raw['trials'][0]['check']['mismatch_count'] = False
        self.assertFalse(self.check()['audit_passed'])

    def test_missing_gpu_timestamps_are_unknown_not_fake_zero(self):
        for key in ('gpu_start_time', 'gpu_end_time', 'gpu_interval_seconds'):
            self.raw['trials'][0].pop(key)
        self.assertTrue(self.check()['audit_passed'])

    def test_freeze_identity_required_source_and_binary_mutations_rejected(self):
        self.execution['freeze_sha256'] = '0'*64
        self.assertFalse(self.check()['audit_passed'])
        self.execution['freeze_sha256'] = audit.digest(self.root/'DESIGN_FREEZE.json')
        self.binary.write_bytes(b'changed')
        self.assertFalse(self.check()['audit_passed'])
        self.binary.write_bytes(b'never executed')
        del self.freeze['source_sha256']['calibrate.swift']
        self.save('DESIGN_FREEZE.json', self.freeze, self.root)
        self.execution['freeze_sha256'] = audit.digest(self.root/'DESIGN_FREEZE.json')
        self.assertFalse(self.check()['audit_passed'])

    def test_nonfinite_and_duplicate_json_rejected(self):
        self.check()
        for raw in ('{"gate_passed":true,"gate_passed":false}', '{"x":NaN}'):
            (self.capture/'RAW.json').write_text(raw)
            self.assertFalse(audit.audit_capture(self.root, self.capture)['audit_passed'])


if __name__ == '__main__':
    unittest.main()
