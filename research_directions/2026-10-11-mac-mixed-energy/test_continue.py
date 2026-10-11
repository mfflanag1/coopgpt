"""Offline continuation-contract regressions using tiny synthetic directories.

Neither imports the serving runtime nor reads actual capture directories.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch


WRAPPER = Path(__file__).with_name('continue_study.py')


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True) + '\n')


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='coop-continue-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.previous = self.root / 'original'
        self.source.mkdir()
        self.previous.mkdir()
        self.config = {'fixture': True, 'planned_offered': 4}
        self.plan = [dict(index=i, parallel=[1, 2, 4, 1][i-1], rep=1,
                          rate=0.3, trace_file='trace.json') for i in range(1, 5)]
        self.stop = dict(stop_confirmed=True, returncode=0)
        self.prior = dict(status='budget_stopped', windows=[dict(item, status='completed')
                         for item in self.plan[:2]], power_stop=copy.deepcopy(self.stop))
        for folder in (self.source, self.previous):
            write(folder / 'CONFIG.json', self.config)
            write(folder / 'PLAN.json', self.plan)
        write(self.source / 'trace.json', [{'request_id': 'fixture-only'}])
        write(self.source / 'FREEZE.json', {'sha256': {}})
        (self.source / 'continue_study.py').write_bytes(WRAPPER.read_bytes())
        (self.source / 'CONTINUATION_PROTOCOL.txt').write_text('Synthetic prospective amendment.\n')
        write(self.previous / 'POWER_STOP.json', self.stop)
        (self.previous / 'POWER.txt.gz').write_bytes(gzip.compress(b'SYNTHETIC FIXTURE ONLY\n', mtime=0))
        for record in self.prior['windows']:
            directory = self.previous / ('window-%02d' % record['index'])
            directory.mkdir()
            write(directory / 'RUN.json', record)
            write(directory / 'REQUESTS.json', {'requests': [{'request_id': 'fixture-only'}]})
        self.save_prior()

        # Stand-ins are injected before loading the wrapper, so importing it
        # cannot import or execute any real runtime or power-capture module.
        self.runtime = types.SimpleNamespace(check_lock=Mock(), write=write,
                                             utc=lambda: '2026-10-11T23:00:00+00:00',
                                             window=Mock(side_effect=self.fake_window))
        self.power = types.SimpleNamespace(launch=Mock(return_value={'fixture': True}),
                                           stop_and_archive=Mock(return_value=copy.deepcopy(self.stop)))
        spec = importlib.util.spec_from_file_location('coop_continue_offline_test', WRAPPER)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, runstudy=self.runtime, power_capture=self.power):
            spec.loader.exec_module(self.module)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(self.module, '__file__', str(self.source / 'continue_study.py')))
        # No real waiting is needed for the tiny fake collection.
        self.stack.enter_context(patch.object(self.module.time, 'monotonic', return_value=100.0))
        self.stack.enter_context(patch('builtins.print'))

    def save_prior(self):
        write(self.previous / 'CAMPAIGN.json', self.prior)

    def fake_window(self, item, config, output):
        directory = output / ('window-%02d' % item['index'])
        directory.mkdir()
        record = dict(item, status='completed')
        write(directory / 'RUN.json', record)
        write(directory / 'REQUESTS.json', {'requests': [{'request_id': 'fixture-only'}]})
        return record

    def eligible(self):
        return self.module.eligible_prefix(self.source, self.previous)

    def test_exact_completed_nonempty_prefix_is_eligible(self):
        config, plan, count = self.eligible()
        self.assertEqual(config, self.config)
        self.assertEqual(plan, self.plan)
        self.assertEqual(count, 2)

    def test_nonbudget_campaigns_are_rejected_before_any_new_capture(self):
        for status in ('aborted', 'running', 'completed', 'starting'):
            with self.subTest(status=status):
                self.prior['status'] = status
                self.save_prior()
                with self.assertRaises(ValueError):
                    self.module.main(self.previous, self.root / ('new-' + status))
        self.power.launch.assert_not_called()
        self.runtime.window.assert_not_called()

    def test_empty_or_complete_prefix_cannot_continue(self):
        for count in (0, 4):
            with self.subTest(count=count):
                self.prior['windows'] = [dict(item, status='completed') for item in self.plan[:count]]
                self.save_prior()
                with self.assertRaises(ValueError):
                    self.eligible()

    def test_incomplete_attempt_is_rejected(self):
        for status in ('starting', 'aborted', 'running'):
            with self.subTest(status=status):
                self.prior['windows'][1]['status'] = status
                self.save_prior()
                write(self.previous / 'window-02' / 'RUN.json', self.prior['windows'][1])
                with self.assertRaises(ValueError):
                    self.eligible()

    def test_missing_or_extra_attempt_directory_is_rejected(self):
        (self.previous / 'window-03').mkdir()
        with self.assertRaises(ValueError):
            self.eligible()
        (self.previous / 'window-03').rmdir()
        (self.previous / 'window-02').rename(self.previous / 'removed-window')
        with self.assertRaises(ValueError):
            self.eligible()

    def test_duplicate_window_records_are_rejected(self):
        self.prior['windows'][1] = copy.deepcopy(self.prior['windows'][0])
        self.save_prior()
        with self.assertRaises(ValueError):
            self.eligible()

    def test_reordered_window_records_are_rejected(self):
        self.prior['windows'].reverse()
        self.save_prior()
        with self.assertRaises(ValueError):
            self.eligible()

    def test_campaign_and_run_mismatch_is_rejected(self):
        record = copy.deepcopy(self.prior['windows'][0])
        record['fixture_extra_mismatch'] = True
        write(self.previous / 'window-01' / 'RUN.json', record)
        with self.assertRaises(ValueError):
            self.eligible()

    def test_missing_request_capture_is_rejected(self):
        (self.previous / 'window-01' / 'REQUESTS.json').unlink()
        with self.assertRaises(ValueError):
            self.eligible()

    def test_source_config_or_plan_mismatch_is_rejected(self):
        for name in ('CONFIG.json', 'PLAN.json'):
            with self.subTest(name=name):
                path = self.previous / name
                original = path.read_bytes()
                write(path, {'mismatched': True})
                with self.assertRaises(ValueError):
                    self.eligible()
                path.write_bytes(original)

    def test_source_config_type_changes_are_not_silently_equal(self):
        altered = copy.deepcopy(self.config)
        altered['fixture'] = 1  # Python says 1 == True; frozen JSON differs.
        write(self.previous / 'CONFIG.json', altered)
        with self.assertRaises(ValueError):
            self.eligible()

    def test_abnormal_or_unconfirmed_sampler_stop_is_rejected(self):
        cases = [dict(stop_confirmed=False, returncode=0),
                 dict(stop_confirmed='yes', returncode=0),
                 dict(stop_confirmed=True, returncode=130),
                 dict(stop_confirmed=True, returncode=-15),
                 dict(stop_confirmed=True), {}]
        for stop in cases:
            with self.subTest(stop=stop):
                write(self.previous / 'POWER_STOP.json', stop)
                self.prior['power_stop'] = copy.deepcopy(stop)
                self.save_prior()
                with self.assertRaises(ValueError):
                    self.eligible()

    def test_noninteger_success_code_is_not_a_normal_exit(self):
        for code in (False, 0.0, '0'):
            with self.subTest(code=repr(code)):
                stop = dict(stop_confirmed=True, returncode=code)
                write(self.previous / 'POWER_STOP.json', stop)
                self.prior['power_stop'] = copy.deepcopy(stop)
                self.save_prior()
                with self.assertRaises(ValueError):
                    self.eligible()

    def test_campaign_power_stop_disagreement_is_rejected(self):
        self.prior['power_stop'] = dict(stop_confirmed=False, returncode=1)
        self.save_prior()
        with self.assertRaises(ValueError):
            self.eligible()

    def test_only_unattempted_suffix_runs_without_rewriting_previous_files(self):
        before = {str(path.relative_to(self.previous)): path.read_bytes()
                  for path in self.previous.rglob('*') if path.is_file()}
        destination = self.root / 'continuation'
        self.module.main(self.previous, destination)
        self.assertEqual([call.args[0]['index'] for call in self.runtime.window.call_args_list], [3, 4])
        result = json.loads((destination / 'CAMPAIGN.json').read_text())
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['completed_prefix'], [1, 2])
        self.assertEqual(result['planned_offered'], 2)
        self.assertEqual(result['full_planned_offered'], self.config['planned_offered'])
        self.assertEqual(result['original_campaign_sha256'], hashlib.sha256(before['CAMPAIGN.json']).hexdigest())
        self.assertEqual(result['original_power_sha256'], hashlib.sha256(before['POWER.txt.gz']).hexdigest())
        self.assertEqual(result['continuation_script_sha256'],
                         hashlib.sha256((self.source / 'continue_study.py').read_bytes()).hexdigest())
        for relative, original_bytes in before.items():
            self.assertEqual((self.previous / relative).read_bytes(), original_bytes)
        self.power.stop_and_archive.assert_called_once()

    def test_same_original_cannot_be_continued_twice(self):
        self.module.main(self.previous, self.root / 'first-continuation')
        with self.assertRaises((ValueError, FileExistsError, RuntimeError)):
            self.module.main(self.previous, self.root / 'second-continuation')
        self.assertEqual(self.power.launch.call_count, 1)
        self.assertEqual([call.args[0]['index'] for call in self.runtime.window.call_args_list], [3, 4])

    def test_existing_atomic_claim_rejects_before_meter_or_workload(self):
        write(self.previous / 'CONTINUATION_CLAIM.json', {
            'output_directory': 'synthetic earlier claim', 'fixture': True})
        with self.assertRaises((ValueError, FileExistsError, RuntimeError)):
            self.module.main(self.previous, self.root / 'another-continuation')
        self.power.launch.assert_not_called()
        self.runtime.window.assert_not_called()

    def test_recorded_sampler_stop_error_prevents_continuation(self):
        self.prior['power_stop_error'] = 'synthetic archive interruption'
        self.save_prior()
        with self.assertRaises(ValueError):
            self.eligible()

    def test_window_abort_is_saved_without_attempting_later_window(self):
        def abort(item, config, output):
            directory = output / ('window-%02d' % item['index'])
            directory.mkdir()
            write(directory / 'RUN.json', dict(item, status='aborted', error='synthetic failure'))
            raise RuntimeError('synthetic failure')
        self.runtime.window.side_effect = abort
        destination = self.root / 'aborted-continuation'
        with self.assertRaisesRegex(RuntimeError, 'synthetic failure'):
            self.module.main(self.previous, destination)
        result = json.loads((destination / 'CAMPAIGN.json').read_text())
        self.assertEqual(result['status'], 'aborted')
        self.assertEqual([row['index'] for row in result['windows']], [3])
        self.assertEqual(self.runtime.window.call_count, 1)
        self.power.stop_and_archive.assert_called_once()


if __name__ == '__main__':
    unittest.main()
