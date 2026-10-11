"""Synthetic stored-data tests. No physical endpoint or outcome is accessed."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import analyze


class MixedAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source, self.data = self.base/'source', self.base/'data'
        self.source.mkdir()
        self.data.mkdir()
        self.config = json.loads((analyze.BASE/'CONFIG.json').read_text())
        self.plan = json.loads((analyze.BASE/'PLAN.json').read_text())
        self.save(self.source/'CONFIG.json', self.config)
        self.save(self.source/'PLAN.json', self.plan)
        self.save(self.data/'CONFIG.json', self.config)
        self.save(self.data/'PLAN.json', self.plan)
        (self.source/'traces').mkdir()
        self.traces = {}
        for plan in self.plan:
            name = plan['trace_file']
            if name not in self.traces:
                self.traces[name] = json.loads((analyze.BASE/name).read_text())
                self.save(self.source/name, self.traces[name])
        for name in ('MODEL_LOCK.json', 'client.py', 'runstudy.py', 'power_capture.py', 'energy.py', 'analyze.py'):
            (self.source/name).write_text('synthetic freeze fixture\n')
        files = ['CONFIG.json', 'PLAN.json', 'MODEL_LOCK.json', 'client.py', 'runstudy.py', 'power_capture.py', 'energy.py', 'analyze.py'] + list(self.traces)
        self.save(self.source/'FREEZE.json', dict(frozen_utc=self.ts(0), sha256={name: hashlib.sha256((self.source/name).read_bytes()).hexdigest() for name in files}))
        for plan in self.plan:
            self.make_window(plan)

    def save(self, path, value):
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

    def load(self, path):
        return json.loads(path.read_text())

    def path(self, index, filename):
        return self.data/f'window-{index:02d}'/filename

    def ts(self, seconds):
        return (datetime(2026, 10, 11, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat()

    def row(self, job, latency=.5, text=None):
        arrival, cap = job['arrival_offset_s'], job['max_output_tokens']
        final = dict(model=analyze.MODEL, done=True, response='', done_reason='stop',
                     prompt_eval_count=100, eval_count=10, total_duration=1000,
                     load_duration=10, prompt_eval_duration=100, eval_duration=890)
        return dict(request_id=job['request_id'], arrival_offset_s=arrival,
                    request_options=dict(analyze.OPTIONS, num_predict=cap),
                    dispatch_offset_s=arrival+.01, first_content_offset_s=arrival+.1,
                    terminal_offset_s=arrival+latency, completed=True, error=None, http_status=200,
                    chunks=[dict(offset_s=arrival+.1, data=dict(model=analyze.MODEL, response=job.get('expected', 'warm') if text is None else text, done=False)),
                            dict(offset_s=arrival+latency-.001, data=copy.deepcopy(final))], final=final)

    def snapshot(self, seconds):
        return dict(utc=self.ts(seconds), power="Now drawing from 'AC Power'\nBattery charging 80%",
                    thermal='Note: No thermal warning level has been recorded\nNote: No performance warning level has been recorded\nNote: No CPU power status has been recorded',
                    load_average=[1.0, 2.0, 3.0])

    def make_window(self, plan):
        index, p = plan['index'], plan['parallel']
        directory = self.path(index, 'RUN.json').parent
        directory.mkdir()
        base = index*200
        loaded = {'models': [dict(name=analyze.MODEL, digest=analyze.DIGEST, context_length=4096, size_vram=3_000_000_000)]}
        phases = [dict(name=name, utc=self.ts(base+second)) for name, second in zip(analyze.PHASES, (2, 12, 103, 104, 114))]
        meta = dict(plan, model=analyze.MODEL, options=analyze.OPTIONS, status='completed',
                    server_settings=dict(self.config['server_settings_common'], OLLAMA_NUM_PARALLEL=str(p)),
                    version={'version': '0.20.0'}, model_tag=dict(name=analyze.MODEL, digest=analyze.DIGEST),
                    runtime_parallel_values=[p], loaded_before=loaded, loaded_after=loaded,
                    loaded_after_unload={'models': []}, dedicated_server_pid=1000+index,
                    dedicated_server_returncode=-15, phases=phases,
                    before=self.snapshot(base), after=self.snapshot(base+115),
                    original_endpoint_idle_before=True, original_endpoint_idle_after=True)
        self.save(directory/'RUN.json', meta)
        jobs = [dict(job, max_output_tokens=64, slo_s=8) for job in self.config['warmups']]
        self.save(directory/'WARMUP.json', dict(started_utc=self.ts(base+1), elapsed_seconds=1, requests=[self.row(job) for job in jobs]))
        trace = self.traces[plan['trace_file']]
        self.save(directory/'REQUESTS.json', dict(started_utc=self.ts(base+12), elapsed_seconds=91, requests=[self.row(job) for job in trace]))
        (directory/'SERVER.log').write_text(f'n_seq_max = {p}\nParallel={p}\nKV buffer size 256 MiB\n')

    def result(self):
        return analyze.analyze(self.data, self.source)

    def mutate_row(self, index, position, edit):
        path = self.path(index, 'REQUESTS.json')
        data = self.load(path)
        edit(data['requests'][position])
        self.save(path, data)

    def test_positive_campaign_all_offers_cells_matches_and_determinism(self):
        result = self.result()
        self.assertTrue(result['valid'], result['validation_errors'] + result['windows'][0]['validation_errors'])
        self.assertEqual(result['analyzed_planned_count'], 1134)
        self.assertEqual(len(result['windows']), 18)
        self.assertEqual(len(result['rate_parallel_cells']), 9)
        self.assertTrue(all(cell['finite_window_acceptable'] for cell in result['rate_parallel_cells']))
        self.assertEqual(len(result['matched_comparisons']), 12)
        self.assertTrue(all(row['difference']['quality_slo_fraction'] == 0 for row in result['matched_comparisons']))
        window = result['windows'][0]
        self.assertEqual(window['metrics']['quality_slo_count'], 27)
        self.assertEqual(window['metrics']['reported_output_tokens'], 270)
        self.assertEqual(window['by_output_cap']['64']['planned_count'], 9)
        self.assertEqual(window['by_cross_class']['32x64']['planned_count'], 3)
        self.assertEqual(window['offered_cohorts']['early_third']['planned_count'], 9)
        self.assertEqual(window['unfinished_offered_count']['90'], 0)
        self.assertFalse(window['energy']['intervals']['full_episode']['valid'])
        self.assertIsNone(window['energy']['intervals']['full_episode']['lower_j'])
        self.save(self.data/'SUMMARY.json', result)
        self.assertEqual(result, self.result())

    def test_quality_normalization_is_narrow_and_exact(self):
        expected = 'R0001=123;R0003=456'
        for text in (expected, expected+';', ' \nR0001 = 123 ; R0003=456\t', '```\n'+expected+';\n```'):
            self.assertTrue(analyze.quality_pass(text, expected), text)
        for text in ('Answer: '+expected, expected+' extra', expected+';;', '```text\n'+expected+'```',
                     'R0003=456;R0001=123', expected+';R0003=456', 'R0001=123', 'R0001=123;R0003=457'):
            self.assertFalse(analyze.quality_pass(text, expected), text)

    def test_wrong_quality_keeps_api_success_and_rejects_both_rep_cell(self):
        jobs = self.traces[self.plan[0]['trace_file']]
        positions = [i for i, job in enumerate(jobs) if job['max_output_tokens'] == 64][:2]
        for position in positions:
            self.mutate_row(1, position, lambda row: row['chunks'][0]['data'].update(response='wrong'))
        result = self.result()
        window = result['windows'][0]
        self.assertTrue(window['valid'])
        self.assertEqual(window['metrics']['api_completed_count'], 27)
        self.assertEqual(window['metrics']['quality_pass_count'], 25)
        self.assertGreaterEqual(window['metrics']['quality_slo_fraction'], .9)
        self.assertLess(window['by_output_cap']['64']['quality_slo_fraction'], .8)
        self.assertFalse(window['finite_window_screen']['passed'])
        cell = next(c for c in result['rate_parallel_cells'] if c['rate'] == .3 and c['parallel'] == 4)
        self.assertFalse(cell['finite_window_acceptable'])

    def test_class_deadline_origin_and_exact_boundary(self):
        for cap, deadline in analyze.SLOS.items():
            job = dict(request_id='x', arrival_offset_s=2, max_output_tokens=cap, slo_s=deadline, expected='R0001=123')
            row = self.row(job, latency=deadline+.04)
            row['dispatch_offset_s'] = 2.09
            result = analyze.validate_row(row, job, 100)
            self.assertTrue(result['api_completed'], result['validation_errors'])
            self.assertFalse(result['api_slo'])
            row['terminal_offset_s'] = 2+deadline
            row['chunks'][-1]['offset_s'] = 2+deadline-.001
            self.assertTrue(analyze.validate_row(row, job, 100)['quality_slo'])

    def test_untrusted_trace_deadline_cannot_relax_the_fixed_cap_slo(self):
        job = dict(request_id='x', arrival_offset_s=0, max_output_tokens=64, slo_s=999, expected='R0001=123')
        result = analyze.validate_row(self.row(job, latency=9), job, 100)
        self.assertTrue(result['api_completed'])
        self.assertEqual(result['slo_s'], 8)
        self.assertFalse(result['quality_slo'])

    def test_phase_mismatch_invalidates_but_preserves_outcomes(self):
        path = self.path(1, 'RUN.json')
        meta = self.load(path)
        meta['phases'][1]['utc'] = self.ts(211)
        self.save(path, meta)
        window = self.result()['windows'][0]
        self.assertFalse(window['valid'])
        self.assertEqual(window['metrics']['quality_slo_count'], 27)
        self.assertTrue(any('client epoch' in error for error in window['validation_errors']))

    def test_stream_http_model_usage_options_and_token_cap_validation(self):
        job = dict(request_id='x', arrival_offset_s=0, max_output_tokens=64, slo_s=8, expected='R0001=123')
        edits = [lambda row: row.update(http_status=503), lambda row: row['final'].update(eval_count=True),
                 lambda row: row['final'].update(eval_count=65), lambda row: row['final'].update(model='wrong'),
                 lambda row: row.update(request_options=dict(analyze.OPTIONS, num_predict=192)),
                 lambda row: row['chunks'][0]['data'].update(error=''), lambda row: row['chunks'][-1]['data'].update(done=False),
                 lambda row: row.update(first_content_offset_s=.11), lambda row: row.update(completed=1),
                 lambda row: row['chunks'][0].update(offset_s=-1)]
        for edit in edits:
            row = self.row(job)
            edit(row)
            result = analyze.validate_row(row, job, 100)
            self.assertFalse(result['api_completed'])
            self.assertTrue(result['validation_errors'])

    def test_missing_duplicate_and_failed_offers_stay_in_denominator(self):
        path = self.path(1, 'REQUESTS.json')
        original = self.load(path)
        for mode in ('missing', 'duplicate', 'failed'):
            data = copy.deepcopy(original)
            if mode == 'missing':
                data['requests'].pop(0)
            elif mode == 'duplicate':
                data['requests'].append(data['requests'][0])
            else:
                data['requests'][0].update(completed=False, error='HTTP 503', http_status=503, chunks=[], final=None,
                                           first_content_offset_s=None, terminal_offset_s=.02)
            self.save(path, data)
            result = self.result()
            window = result['windows'][0]
            self.assertEqual(result['analyzed_planned_count'], 1134)
            self.assertEqual(window['metrics']['planned_count'], 27)
            self.assertEqual(window['metrics']['api_completed_count'], 26)
            self.assertEqual(window['metrics']['quality_slo_fraction'], 26/27)
            self.assertFalse(window['finite_window_screen']['passed'])
            self.assertEqual(window['valid'], mode == 'failed')
            self.assertEqual(window['metrics']['recorded_failure_count'], int(mode == 'failed'))

    def test_missing_window_preserves_planned_offers_and_backlog_unknown(self):
        for path in self.path(1, 'RUN.json').parent.iterdir():
            path.unlink()
        result = self.result()
        window = result['windows'][0]
        self.assertEqual(result['analyzed_planned_count'], 1134)
        self.assertEqual(window['metrics']['unverified_outcome_count'], 27)
        self.assertEqual(window['unfinished_offered_count']['90'], 27)
        self.assertTrue(window['backlog_includes_unverified_records'])
        self.assertEqual(window['known_dispatched_unfinished_count']['90'], 0)
        self.assertFalse(window['valid'])

    def test_environment_invalidity_retains_metrics(self):
        path = self.path(1, 'RUN.json')
        meta = self.load(path)
        meta['loaded_after']['models'][0]['context_length'] = 2048
        meta['before']['power'] = "Now drawing from 'Battery Power'"
        meta['server_settings']['OLLAMA_MAX_QUEUE'] = '1'
        self.save(path, meta)
        result = self.result()
        window = result['windows'][0]
        self.assertFalse(window['valid'])
        self.assertEqual(window['metrics']['api_completed_count'], 27)
        self.assertEqual(window['metrics']['quality_slo_count'], 27)
        self.assertFalse(window['finite_window_screen']['passed'])

    def test_lag_diagnostic_keeps_scheduled_latency_denominator(self):
        def edit(row):
            row['dispatch_offset_s'] = .11
            row['first_content_offset_s'] = .12
            row['chunks'][0]['offset_s'] = .12
        self.mutate_row(1, 0, edit)
        window = self.result()['windows'][0]
        self.assertTrue(window['valid'])
        self.assertTrue(window['requests'][0]['dispatch_lag_over_100ms'])
        self.assertEqual(window['metrics']['api_completed_count'], 27)
        self.assertEqual(window['metrics']['quality_slo_count'], 27)

    def test_backlog_uses_terminal_including_failed_and_unknown_rows(self):
        def edit(row):
            row.update(completed=False, error='timeout', chunks=[], final=None, first_content_offset_s=None, terminal_offset_s=91)
        self.mutate_row(1, 0, edit)
        window = self.result()['windows'][0]
        self.assertEqual(window['unfinished_offered_count']['90'], 1)
        self.assertEqual(window['unfinished_offered_count']['120'], 0)
        self.assertEqual(window['metrics']['completion_latency_s']['n'], 26)

    def test_outputs_and_tokens_are_not_filtered_for_identity(self):
        self.mutate_row(1, 0, lambda row: row['chunks'][0]['data'].update(response='```\n'+row['chunks'][0]['data']['response']+'\n```'))
        result = self.result()
        self.assertTrue(result['valid'])
        matched = next(m for m in result['matched_comparisons'] if m['rate'] == .3 and m['rep'] == 1 and m['contrast'] == 'P4-P1')
        self.assertEqual(matched['difference']['quality_slo_count'], 0)
        self.assertEqual(matched['equal_output_count'], 26)
        self.assertEqual(matched['output_identity_by_id'][0]['treatment_eval_count'], 10)

    def test_undispatched_lifecycle_failure_needs_no_actual_request_options(self):
        job = dict(request_id='x', arrival_offset_s=4, max_output_tokens=64, slo_s=8, expected='R0001=123')
        row = self.row(job)
        row.pop('request_options')
        row.update(completed=False, error='worker start failed', dispatch_offset_s=None, first_content_offset_s=None, terminal_offset_s=1, chunks=[], final=None, http_status=None)
        result = analyze.validate_row(row, job, 10)
        self.assertFalse(result['api_completed'])
        self.assertEqual(result['validation_errors'], [])

    def test_bad_energy_archive_cannot_erase_serving_metrics(self):
        (self.data/'POWER.txt.gz').write_bytes(b'\x1f\x8b\x08')
        result = self.result()
        self.assertTrue(result['valid'])
        self.assertEqual(result['analyzed_planned_count'], 1134)
        self.assertTrue(result['energy_capture']['parse_errors'])
        self.assertIsNone(result['windows'][0]['energy']['intervals']['full_episode']['lower_j'])

    def test_nearest_rank_and_empty_strata(self):
        self.assertEqual(analyze.quantiles(list(range(1, 17)))['p50'], 8)
        self.assertEqual(analyze.quantiles(list(range(1, 17)))['p95'], 16)
        self.assertIsNone(analyze.metrics([])['quality_slo_fraction'])
        self.assertIsNone(analyze.quantiles([])['p95'])

    def test_energy_phase_windows_are_delegated_without_interpolation(self):
        import sys
        fake = type('FakeEnergy', (), {})()
        seen = []
        def bounds(samples, start, end):
            seen.append((start, end))
            return dict(valid=True, lower_j={'combined': 12}, upper_j={'combined': 24})
        fake.energy_bounds = bounds
        phases = dict(zip(analyze.PHASES, (self.ts(1), self.ts(11), self.ts(101), self.ts(102), self.ts(112))))
        with patch.dict(sys.modules, energy=fake):
            result = analyze.energy_diagnostics(dict(samples=[{}], errors=[]), phases)
        self.assertEqual(seen, [(self.ts(1), self.ts(11)), (self.ts(11), self.ts(101)), (self.ts(101), self.ts(102)), (self.ts(102), self.ts(112)), (self.ts(1), self.ts(112))])
        self.assertEqual(result['intervals']['full_episode']['lower_j']['combined'], 12)
        self.assertEqual(result['intervals']['full_episode']['upper_j']['combined'], 24)

    def test_freeze_change_blocks_acceptance(self):
        (self.source/'client.py').write_text('changed')
        result = self.result()
        self.assertFalse(result['valid'])
        self.assertTrue(all(not c['finite_window_acceptable'] for c in result['rate_parallel_cells']))
        self.assertTrue(any('FREEZE mismatch' in err for err in result['validation_errors']))


if __name__ == '__main__':
    unittest.main()
