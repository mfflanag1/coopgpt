"""CPU-only preservation/deadline fixtures; subprocess calls are mocked."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import run_campaign as run


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / 'native'
        self.binary.write_bytes(b'fixture binary; never executed')
        self.window = {'index': 1, 'window_id': 'r1_rate10_c1', 'round': 1,
                       'rate': 10, 'concurrency': 1, 'jobs': 60}
        self.folder = self.root / 'window'
        self.diag = patch.object(run, 'diagnostic', return_value={'fixture': True})
        self.diag.start()
        self.addCleanup(self.diag.stop)
        self.freeze = patch.object(run, 'verify_freeze', return_value='fixture-freeze')
        self.audit = patch.object(run, 'audit_window', return_value={'checks_passed': True, 'errors': []})
        self.audit.start()
        self.addCleanup(self.audit.stop)
        self.freeze.start()
        self.addCleanup(self.freeze.stop)

    def completed(self, command, **kwargs):
        Path(command[-1]).write_text('{"gate_passed": true}')
        return subprocess.CompletedProcess(command, 0, 'fixture stdout', '')

    def run_window(self, **kwargs):
        return run.run_window(self.binary, self.folder, self.window, 90,
                              'fixture-freeze', audit_context=({}, {}, {'fixture'}), **kwargs)

    def test_fixed_command_and_preserved_success(self):
        with patch.object(run.subprocess, 'run', side_effect=self.completed) as call:
            meta, ok = self.run_window()
        self.assertTrue(ok)
        self.assertEqual(call.call_args.args[0], [str(self.binary), '--concurrency', '1',
                          '--rate', '10', '--output', str(self.folder / 'RAW.json')])
        self.assertFalse(call.call_args.kwargs['shell'])
        self.assertEqual((self.folder / 'STDOUT.txt').read_text(), 'fixture stdout')
        self.assertEqual(json.loads((self.folder / 'EXECUTION.json').read_text()), meta)

    def test_timeout_keeps_partial_output_and_failure(self):
        with patch.object(run.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fixture', 90,
                          output=b'partial', stderr=b'error')):
            meta, ok = self.run_window()
        self.assertFalse(ok)
        self.assertEqual(meta['process_status'], 'timed_out')
        self.assertEqual((self.folder / 'STDOUT.txt').read_bytes(), b'partial')
        self.assertFalse(meta['raw_output_present'])

    def test_deadline_recomputed_after_diagnostics(self):
        clock = [0.0]
        def diag(*args):
            clock[0] += 4
            return {'fixture': True}
        with patch.object(run, 'diagnostic', side_effect=diag), \
             patch.object(run.time, 'monotonic', side_effect=lambda: clock[0]), \
             patch.object(run.subprocess, 'run', side_effect=self.completed) as call:
            meta, ok = self.run_window(deadline=10)
        self.assertTrue(ok)
        self.assertEqual(call.call_args.kwargs['timeout'], 2)
        self.assertEqual(meta['timeout_seconds'], 2)

    def test_expired_budget_never_launches_native(self):
        with patch.object(run.time, 'monotonic', return_value=10), \
             patch.object(run.subprocess, 'run') as call:
            meta, ok = self.run_window(deadline=9)
        self.assertFalse(ok)
        call.assert_not_called()
        self.assertEqual(meta['timeout_seconds'], 0)

    def test_diagnostics_respect_shared_deadline(self):
        self.diag.stop()
        with patch.object(run.time, 'monotonic', return_value=8), \
             patch.object(run.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')) as call:
            run.diagnostic('batt', deadline=10)
            self.assertEqual(call.call_args.kwargs['timeout'], 2)
            call.reset_mock()
            result = run.diagnostic('therm', deadline=7)
            call.assert_not_called()
            self.assertEqual(result['error_type'], 'CampaignDeadline')

    def test_existing_capture_is_preserved(self):
        self.folder.mkdir()
        (self.folder / 'RAW.json').write_text('original')
        with self.assertRaises(FileExistsError):
            self.run_window()
        self.assertEqual((self.folder / 'RAW.json').read_text(), 'original')

    def test_after_diagnostic_interrupt_preserves_executed_window(self):
        values = [{'fixture': True}, {'fixture': True}, KeyboardInterrupt()]
        with patch.object(run.subprocess, 'run', side_effect=self.completed), \
             patch.object(run, 'diagnostic', side_effect=values):
            meta, ok = self.run_window()
        self.assertFalse(ok)
        self.assertTrue(meta['diagnostic_interrupted'])
        self.assertEqual(meta['process_status'], 'completed')
        self.assertTrue(meta['raw_output_present'])
        self.assertEqual((self.folder / 'STDOUT.txt').read_text(), 'fixture stdout')
        self.assertTrue((self.folder / 'EXECUTION.json').exists())

    def test_native_true_does_not_override_independent_failure(self):
        with patch.object(run.subprocess, 'run', side_effect=self.completed), \
             patch.object(run, 'audit_window', return_value={'checks_passed': False, 'errors': ['Missing row']}):
            meta, ok = self.run_window()
        self.assertFalse(ok)
        self.assertTrue(meta['raw_gate_passed'])
        self.assertFalse(meta['independent_window_checks_passed'])
        self.assertEqual(meta['independent_window_errors'], ['Missing row'])

    def test_source_change_closes_gate(self):
        with patch.object(run.subprocess, 'run', side_effect=self.completed), \
             patch.object(run, 'verify_freeze', return_value='changed'):
            meta, ok = self.run_window()
        self.assertFalse(ok)
        self.assertTrue(meta['source_changed'])

    def test_process_failure_cannot_be_overridden_by_raw_gate(self):
        def failed(command, **kwargs):
            self.completed(command, **kwargs)
            return subprocess.CompletedProcess(command, 3, '', '')
        with patch.object(run.subprocess, 'run', side_effect=failed):
            meta, ok = self.run_window()
        self.assertFalse(ok)
        self.assertTrue(meta['raw_gate_passed'])

    def plan(self):
        plan = {'campaign_timeout_seconds': 600, 'window_timeout_seconds': 90,
                'inter_window_idle_seconds': 1, 'warmup_dimensions': [256, 512, 1024], 'windows': [self.window,
                 dict(self.window, index=2, concurrency=2, window_id='r1_rate10_c2')]}
        (self.root / 'PLAN.json').write_text(json.dumps(plan))
        return plan

    def test_failed_window_stops_and_retains_unrun_denominator(self):
        self.plan()
        with patch.object(run, 'ROOT', self.root), \
             patch('capture_inventory.capture', return_value={'fixture': True}), \
             patch.object(run.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fixture', 90)):
            ok = run.collect(self.binary, self.root / 'capture')
        report = json.loads((self.root / 'capture/CAMPAIGN.json').read_text())
        self.assertFalse(ok)
        self.assertEqual(len(report['windows']), 1)
        self.assertEqual(report['unrun_window_ids'], ['r1_rate10_c2'])
        self.assertEqual(report['stop_reason'], 'invalid_window:r1_rate10_c1')

    def test_exception_after_window_attempt_not_mislabeled_unrun(self):
        self.plan()
        with patch.object(run, 'ROOT', self.root), \
             patch('capture_inventory.capture', return_value={'fixture': True}), \
             patch.object(run, 'run_window', side_effect=KeyboardInterrupt):
            ok = run.collect(self.binary, self.root / 'capture')
        report = json.loads((self.root / 'capture/CAMPAIGN.json').read_text())
        self.assertFalse(ok)
        self.assertEqual(report['windows'][0]['status'], 'started')
        self.assertEqual(report['unrun_window_ids'], ['r1_rate10_c2'])

    def test_inventory_failure_retains_campaign(self):
        self.plan()
        with patch.object(run, 'ROOT', self.root), \
             patch('capture_inventory.capture', side_effect=OSError('fixture')):
            ok = run.collect(self.binary, self.root / 'capture')
        report = json.loads((self.root / 'capture/CAMPAIGN.json').read_text())
        self.assertFalse(ok)
        self.assertEqual(len(report['unrun_window_ids']), 2)
        self.assertEqual(report['stop_reason'], 'collection_exception:OSError')

    def test_unavailable_gpu_inventory_preserves_unrun_campaign(self):
        self.plan()
        with patch.object(run, 'ROOT', self.root), \
             patch('capture_inventory.capture', return_value={'hardware': {'gpu_inventory': {'devices': None}}}), \
             patch.object(run, 'run_window') as call:
            ok = run.collect(self.binary, self.root / 'capture')
        report = json.loads((self.root / 'capture/CAMPAIGN.json').read_text())
        self.assertFalse(ok)
        call.assert_not_called()
        self.assertEqual(len(report['unrun_window_ids']), 2)
        self.assertEqual(report['stop_reason'], 'collection_exception:ValueError')

    def test_all_windows_in_fixed_order(self):
        self.plan()
        with patch.object(run, 'ROOT', self.root), \
             patch('capture_inventory.capture', return_value={'fixture': True}), \
             patch.object(run.time, 'sleep'), \
             patch.object(run.subprocess, 'run', side_effect=self.completed):
            ok = run.collect(self.binary, self.root / 'capture')
        report = json.loads((self.root / 'capture/CAMPAIGN.json').read_text())
        self.assertTrue(ok)
        self.assertEqual([w['concurrency'] for w in report['windows']], [1, 2])
        self.assertEqual(report['unrun_window_ids'], [])

    def test_freeze_detects_source_and_binary_changes(self):
        self.freeze.stop()
        source = self.root / 'source.txt'
        source.write_text('original')
        manifest = {'source_sha256': {'source.txt': run.digest(source)},
                    'binary_sha256': run.digest(self.binary)}
        (self.root / 'DESIGN_FREEZE.json').write_text(json.dumps(manifest))
        with patch.object(run, 'ROOT', self.root):
            run.verify_freeze(self.binary)
            source.write_text('changed')
            with self.assertRaises(ValueError):
                run.verify_freeze(self.binary)
            source.write_text('original')
            self.binary.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                run.verify_freeze(self.binary)

if __name__ == '__main__':
    unittest.main()
