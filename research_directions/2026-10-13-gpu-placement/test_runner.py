"""Runner/CLI checks using hand-built inputs and mocked collection only.

Never reads the research cases, calls its generator, or executes its comparison.
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import placement
import run_study
import solver
from verifier import strict_loads


def empty_manifest():
    return {
        'schema_version': 1,
        'nodes': [{'id': 'node', 'owner': 'owner', 'cpu_units': 1,
                   'ram_mib': 1, 'gpus': []}],
        'jobs': [],
    }


def row(case_id='fixture', kind='constructed', optimum=(0, 0), achieved=None):
    achieved = optimum if achieved is None else achieved
    return {
        'case_id': case_id,
        'kind': kind,
        'optimum': list(optimum),
        'policies': {
            name: {'objective': list(optimum if name == 'exact' else achieved),
                   'plan': {'schema_version': 1, 'placements': [], 'deferred': []}}
            for name in run_study.POLICIES
        },
        'properties': {'gpu_reuse_rejection': None},
    }


@contextlib.contextmanager
def mocked_collection():
    # Fixed-size hand-built fixtures satisfy only the runner's cohort-size guard.
    # The actual generator and saved cases file are replaced before run() executes.
    fixtures = [{'case_id': f'fixture{i}', 'kind': 'constructed',
                 'manifest': empty_manifest()} for i in range(140)]
    fake_root = MagicMock()
    fake_root.__truediv__.return_value.read_text.return_value = 'mocked-input'
    with patch.object(run_study, 'ROOT', fake_root), \
            patch.object(run_study, 'check_freeze', return_value='test-freeze'), \
            patch.object(run_study, 'strict_loads', return_value=fixtures), \
            patch.object(run_study, 'make_cases', return_value=copy.deepcopy(fixtures)) as generator, \
            patch.object(run_study.signal, 'signal', return_value='prior-handler') as handlers, \
            patch.object(run_study.signal, 'setitimer') as timers:
        yield fixtures, generator, handlers, timers


class SummaryTests(unittest.TestCase):
    def test_ratios_exclude_zero_and_preserve_secondary_loss(self):
        rows = [row('zero'),
                row('tie', optimum=(10, 2), achieved=(10, 1)),
                row('loss', kind='generated', optimum=(30, 3), achieved=(15, 1))]
        report = run_study.summarize(rows)
        all_rows = report['all']
        self.assertEqual((all_rows['cases'], all_rows['nonzero_optimum'],
                          all_rows['zero_optimum']), (3, 2, 1))
        policy = all_rows['policies']['priority_first']
        self.assertEqual(policy['priority_regret'], 15)
        self.assertEqual(policy['mean_priority_ratio_nonzero'], '3/4')
        self.assertEqual(policy['aggregate_priority_ratio'], '5/8')
        self.assertEqual(policy['secondary_tie_losses'], 1)
        self.assertEqual(policy['exact_objective_matches'], 1)
        self.assertEqual(policy['priority_matches'], 2)
        self.assertEqual(report['constructed']['cases'], 2)
        self.assertEqual(report['generated']['cases'], 1)
        self.assertEqual(all_rows['policies']['exact']['priority_regret'], 0)

    def test_all_zero_and_empty_cohorts_have_no_ratio(self):
        report = run_study.summarize([row()])
        for cohort in ('constructed', 'generated', 'all'):
            for policy in run_study.POLICIES:
                self.assertIsNone(report[cohort]['policies'][policy]['mean_priority_ratio_nonzero'])
                self.assertIsNone(report[cohort]['policies'][policy]['aggregate_priority_ratio'])


class RunnerTests(unittest.TestCase):
    def test_existing_output_unchanged_without_starting(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'saved.json'
            output.write_text('preexisting')
            with patch.object(run_study, 'check_freeze') as freeze:
                with self.assertRaises((ValueError, FileExistsError)):
                    run_study.run(output)
                freeze.assert_not_called()
            self.assertEqual(output.read_text(), 'preexisting')

    def test_concurrent_exclusive_writer_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory, mocked_collection():
            output = Path(directory) / 'saved.json'
            competing_write = []

            def attempt_competing_write(*_args, **_kwargs):
                try:
                    with output.open('x') as handle:
                        handle.write('competing-record')
                    competing_write.append(True)
                except FileExistsError:
                    competing_write.append(False)
                raise ValueError('end mocked collection')

            with patch.object(run_study, 'evaluate', side_effect=attempt_competing_write):
                try:
                    result = run_study.run(output)
                except FileExistsError:
                    result = None
            self.assertEqual(len(competing_write), 1)
            if competing_write[0]:
                self.assertEqual(output.read_text(), 'competing-record')
            else:
                self.assertIsNotNone(result)
                self.assertFalse(result['gate_pass'])

    def test_timeout_preserves_completed_rows_and_closes_gate(self):
        with tempfile.TemporaryDirectory() as directory, mocked_collection() as mocks:
            output = Path(directory) / 'partial.json'
            with patch.object(run_study, 'evaluate', side_effect=[row('fixture0'),
                              TimeoutError('mocked timeout')]):
                result = run_study.run(output)
            saved = json.loads(output.read_text())
            self.assertEqual(saved, result)
            self.assertEqual(result['status'], 'failed')
            self.assertFalse(result['gate_pass'])
            self.assertEqual(len(result['rows']), 1)
            self.assertEqual(result['active_case'], 'fixture1')
            self.assertIn('TimeoutError', result['error'])
            timers = mocks[3]
            self.assertEqual(timers.call_args_list[0].args,
                             (run_study.signal.ITIMER_REAL, 180))
            self.assertEqual(timers.call_args_list[-1].args,
                             (run_study.signal.ITIMER_REAL, 0))
            self.assertEqual(mocks[2].call_args_list[-1].args,
                             (run_study.signal.SIGALRM, 'prior-handler'))

    def test_invalid_raw_plan_is_saved_for_audit(self):
        invalid = {'schema_version': 1, 'placements': [], 'deferred': [],
                   'invalid_plan_sentinel': 'unrecognized-output'}
        with tempfile.TemporaryDirectory() as directory, mocked_collection():
            output = Path(directory) / 'invalid.json'
            with patch.object(run_study, 'greedy', return_value=invalid), \
                    patch.object(run_study, 'solve') as exact, \
                    patch.object(run_study, 'optimum') as oracle:
                result = run_study.run(output)
            self.assertFalse(result['gate_pass'])
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['rows'], [])
            self.assertIn('invalid_plan_sentinel', output.read_text())
            self.assertIn('unrecognized-output', output.read_text())
            exact.assert_not_called()
            oracle.assert_not_called()

    def test_oracle_disagreement_closes_gate(self):
        empty = {'schema_version': 1, 'placements': [], 'deferred': []}
        with tempfile.TemporaryDirectory() as directory, mocked_collection():
            output = Path(directory) / 'disagreement.json'
            with patch.object(run_study, 'greedy', return_value=empty), \
                    patch.object(run_study, 'solve', return_value=empty), \
                    patch.object(run_study, 'optimum', return_value=(1, 1)):
                result = run_study.run(output)
            self.assertEqual(result['status'], 'failed')
            self.assertFalse(result['gate_pass'])
            self.assertIn('independent optimum', result['error'])
            self.assertEqual(result['rows'], [])

    def test_producer_rejection_before_return_retains_plan_and_reason(self):
        rejection = {'valid': False, 'errors': ['injected pre-return rejection'],
                     'priority': None, 'admitted': None}
        with tempfile.TemporaryDirectory() as directory, mocked_collection():
            output = Path(directory) / 'producer-rejection.json'
            with patch.object(solver, 'verify_plan', return_value=rejection):
                result = run_study.run(output)
            self.assertEqual(result['status'], 'failed')
            self.assertFalse(result['gate_pass'])
            self.assertEqual(result['rows'], [])
            saved_text = output.read_text()
            strict_loads(saved_text)
            self.assertIn('"placements": []', saved_text)
            self.assertIn('injected pre-return rejection', saved_text)

    def test_non_json_candidate_still_saves_strict_failed_record(self):
        for malformed_value in (float('nan'), object()):
            with self.subTest(type=type(malformed_value).__name__), \
                    tempfile.TemporaryDirectory() as directory, mocked_collection():
                invalid = {'schema_version': 1, 'placements': [], 'deferred': [],
                           'invalid_plan_sentinel': malformed_value}
                output = Path(directory) / 'non-json.json'
                with patch.object(run_study, 'greedy', return_value=invalid):
                    result = run_study.run(output)
                self.assertEqual(result['status'], 'failed')
                self.assertFalse(result['gate_pass'])
                self.assertEqual(result['rows'], [])
                saved_text = output.read_text()
                strict_loads(saved_text)
                self.assertIn('invalid_plan_sentinel', saved_text)


class CLITests(unittest.TestCase):
    def invoke(self, args):
        stream = io.StringIO()
        with patch('sys.argv', ['placement.py'] + args), contextlib.redirect_stdout(stream):
            status = placement.main()
        return status, json.loads(stream.getvalue())

    def test_tiny_manifest_solves_and_verifies(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            plan = Path(directory) / 'plan.json'
            manifest.write_text(json.dumps(empty_manifest()))
            status, solved = self.invoke(['solve', str(manifest)])
            self.assertEqual(status, 0)
            plan.write_text(json.dumps(solved))
            status, checked = self.invoke(['verify', str(manifest), str(plan)])
            self.assertEqual(status, 0)
            self.assertEqual(checked, {'valid': True, 'errors': [], 'priority': 0, 'admitted': 0})

    def test_invalid_plan_has_nonzero_exit_and_no_score(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            plan = Path(directory) / 'plan.json'
            manifest.write_text(json.dumps(empty_manifest()))
            plan.write_text('{"schema_version": 1, "placements": [], "deferred": ["absent"]}')
            status, checked = self.invoke(['verify', str(manifest), str(plan)])
            self.assertEqual(status, 1)
            self.assertFalse(checked['valid'])
            self.assertIsNone(checked['priority'])
            self.assertIsNone(checked['admitted'])

    def test_duplicate_input_keys_fail_as_input_error(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            manifest.write_text('{"schema_version": 1, "schema_version": 1}')
            status, result = self.invoke(['solve', str(manifest)])
            self.assertEqual(status, 2)
            self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()
