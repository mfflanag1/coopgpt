import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import run_calibration as r


class ExecutionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / 'binary'
        self.binary.write_bytes(b'fixture, never executed')
        self.source = self.root / 'source'
        self.source.write_bytes(b'fixed')
        self.freeze = self.root / 'DESIGN_FREEZE.json'
        self.freeze.write_text(json.dumps({'source_sha256': {'source': r.digest(self.source)},
                                            'binary_sha256': r.digest(self.binary)}))
        self.root_patch = patch.object(r, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_freeze_source_and_binary_changes_rejected(self):
        r.verify_freeze(self.binary)
        self.source.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'source changed'):
            r.verify_freeze(self.binary)
        self.source.write_bytes(b'fixed')
        self.binary.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'binary'):
            r.verify_freeze(self.binary)

    def test_existing_output_is_preserved(self):
        output = self.root / 'existing'
        output.mkdir()
        (output / 'sentinel').write_bytes(b'keep')
        with patch.object(r.subprocess, 'run') as command:
            with self.assertRaises(FileExistsError):
                r.run(self.binary, output)
        command.assert_not_called()
        self.assertEqual((output / 'sentinel').read_bytes(), b'keep')

    def test_timeout_retains_diagnostics_and_fails(self):
        output = self.root / 'timed-out'
        with patch('capture_inventory.capture', return_value={'status': 'fixture'}), \
             patch.object(r, 'diagnostic', return_value={'status': 'fixture'}), \
             patch.object(r.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fixture', 120, b'partial', b'error')):
            self.assertFalse(r.run(self.binary, output))
        meta = json.loads((output / 'EXECUTION.json').read_text())
        self.assertEqual(meta['process_status'], 'timed_out')
        self.assertFalse(meta['raw_output_present'])
        self.assertEqual((output / 'STDOUT.txt').read_bytes(), b'partial')

    def test_exit_zero_without_output_does_not_pass(self):
        with patch('capture_inventory.capture', return_value={}), \
             patch.object(r, 'diagnostic', return_value={}), \
             patch.object(r.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')) as command:
            self.assertFalse(r.run(self.binary, self.root / 'no-record'))
        self.assertFalse(command.call_args.kwargs['shell'])
        self.assertEqual(command.call_args.kwargs['timeout'], 120)

    def test_during_run_mutation_and_failure_record_are_retained(self):
        output = self.root / 'modified'
        def fake_run(command, **kwargs):
            Path(command[-1]).write_text('{"gate_passed": false}')
            self.source.write_bytes(b'changed')
            return subprocess.CompletedProcess(command, 1, '', 'failed')
        with patch('capture_inventory.capture', return_value={}), \
             patch.object(r, 'diagnostic', return_value={}), \
             patch.object(r.subprocess, 'run', side_effect=fake_run):
            self.assertFalse(r.run(self.binary, output))
        meta = json.loads((output / 'EXECUTION.json').read_text())
        self.assertTrue(meta['source_changed'])
        self.assertTrue(meta['raw_output_present'])
        self.assertFalse(json.loads((output / 'RAW.json').read_text())['gate_passed'])


if __name__ == '__main__':
    unittest.main()
