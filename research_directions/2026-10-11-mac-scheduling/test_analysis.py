"""Synthetic offline captures only; no serving endpoint or GPU is contacted."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import analyze


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / 'data'
        self.source = self.root / 'source'
        self.data.mkdir()
        self.source.mkdir()
        for name in analyze.REQUIRED_FREEZE:
            raw = (analyze.BASE / name).read_bytes() if name == 'TRACE.json' else b'synthetic source fixture\n'
            (self.source / name).write_bytes(raw)
        self.save(self.source / 'PROTOCOL_FREEZE.json', {'sha256': {
            name: hashlib.sha256((self.source / name).read_bytes()).hexdigest()
            for name in analyze.REQUIRED_FREEZE}})
        self.save(self.data / 'OFFERED_TRACE.json', json.loads((self.source / 'TRACE.json').read_text()))
        for index, parallel in enumerate(analyze.ORDER, 1):
            self.make_window(index, parallel)
        self.sync_campaign()

    def save(self, path, value):
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

    def load(self, path):
        return json.loads(path.read_text())

    def path(self, index, filename):
        return self.data / f'window-{index:02d}-p{analyze.ORDER[index - 1]}' / filename

    def timestamp(self, seconds):
        return (datetime(2026, 10, 11, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat()

    def snapshot(self, seconds):
        return dict(utc=self.timestamp(seconds), power="Now drawing from 'AC Power'\n Battery 70%; charging",
                    thermal='Note: No thermal warning level has been recorded\nNote: No performance warning level has been recorded\nNote: No CPU power status has been recorded',
                    load_average=[2.0, 3.0, 4.0])

    def row(self, request_id, arrival, latency=1.0):
        final = dict(model=analyze.MODEL, done=True, response='', done_reason='length',
                     prompt_eval_count=7, eval_count=2, total_duration=100,
                     load_duration=2, prompt_eval_duration=20, eval_duration=78)
        return dict(request_id=request_id, arrival_offset_s=arrival,
                    dispatch_offset_s=arrival + .01, first_content_offset_s=arrival + .1,
                    terminal_offset_s=arrival + latency, completed=True, error=None, http_status=200,
                    chunks=[dict(offset_s=arrival + .1, data=dict(model=analyze.MODEL, response='hello ' + request_id, done=False)),
                            dict(offset_s=arrival + latency - .001, data=final)], final=copy.deepcopy(final))

    def make_window(self, index, parallel):
        directory = self.path(index, 'RUN.json').parent
        directory.mkdir()
        loaded = dict(models=[dict(name=analyze.MODEL, digest=analyze.DIGEST, context_length=2048, size_vram=3000000000)])
        settings = {'OLLAMA_HOST': 'http://127.0.0.1:11561', 'OLLAMA_NUM_PARALLEL': str(parallel),
                    'OLLAMA_MAX_LOADED_MODELS': '1', 'OLLAMA_MAX_QUEUE': '64',
                    'OLLAMA_CONTEXT_LENGTH': '2048', 'OLLAMA_FLASH_ATTENTION': '0',
                    'OLLAMA_KV_CACHE_TYPE': 'f16', 'OLLAMA_MULTIUSER_CACHE': '0',
                    'OLLAMA_NO_CLOUD': '1', 'OLLAMA_NOPRUNE': '1', 'OLLAMA_NOHISTORY': '1',
                    'OLLAMA_KEEP_ALIVE': '120s', 'OLLAMA_DEBUG': '1'}
        meta = dict(index=index, pair=(index + 1) // 2, parallel=parallel, model=analyze.MODEL,
                    options=analyze.OPTIONS, status='completed', server_settings=settings,
                    version={'version': '0.20.0'}, model_tag=dict(name=analyze.MODEL, digest=analyze.DIGEST),
                    runtime_parallel_values=[parallel], loaded_before=loaded, loaded_after=loaded,
                    loaded_after_unload={'models': []}, dedicated_server_pid=1000 + index,
                    dedicated_server_returncode=-15, before=self.snapshot(0), after=self.snapshot(21),
                    original_endpoint_idle_before=True, original_endpoint_idle_after=True)
        self.save(directory / 'RUN.json', meta)
        self.save(directory / 'WARMUP.json', dict(started_utc=self.timestamp(1), elapsed_seconds=.5,
                                                 requests=[self.row('warm1', 0, .4), self.row('warm2', 0, .4)]))
        timely = 10 if parallel == 1 else 12
        rows = [self.row(request_id, arrival, 1 if i < timely else 6)
                for i, (request_id, arrival) in enumerate(analyze.EXPECTED)]
        self.save(directory / 'REQUESTS.json', dict(started_utc=self.timestamp(4), elapsed_seconds=14, requests=rows))
        (directory / 'SERVER.log').write_text(f'n_seq_max = {parallel}\nParallel={parallel}\nKV buffer size 128 MiB\n')

    def sync_campaign(self):
        self.save(self.data / 'CAMPAIGN.json', dict(status='completed', planned_order=analyze.ORDER,
                  planned_offered=128, windows=[self.load(self.path(i, 'RUN.json')) for i in range(1, 9)]))

    def result(self):
        return analyze.analyze(self.data, self.source)

    def mutate_row(self, index, position, edit):
        path = self.path(index, 'REQUESTS.json')
        collection = self.load(path)
        edit(collection['requests'][position])
        self.save(path, collection)

    def test_valid_fixed_pairs_pass_and_determinism(self):
        result = self.result()
        self.assertTrue(result['valid'], result['validation_errors'] + result['windows'][0]['validation_errors'])
        self.assertTrue(result['gate']['passed'])
        self.assertEqual(result['offered_count'], 128)
        self.assertEqual(result['mean_on_time_count_difference_p2_minus_p1'], 2)
        self.assertEqual(result['mean_on_time_fraction_difference_p2_minus_p1'], .125)
        self.assertEqual([p['p1_window'] for p in result['pairs']], [1, 4, 5, 8])
        self.assertEqual([p['p2_window'] for p in result['pairs']], [2, 3, 6, 7])
        self.assertEqual([p['equal_output_count'] for p in result['pairs']], [16]*4)
        self.assertEqual(result['windows'][0]['reported_output_tokens'], 32)
        self.assertEqual(result['windows'][0]['completion_latency_s']['p95'], 6)
        encoded = json.dumps(result, sort_keys=True)
        self.save(self.data / 'SUMMARY.json', result)
        self.assertEqual(encoded, json.dumps(self.result(), sort_keys=True))

    def test_deadline_is_intended_arrival_not_dispatch(self):
        def edit(row):
            row['dispatch_offset_s'] = .09
            row['terminal_offset_s'] = 5.04
            row['chunks'][-1]['offset_s'] = 5.039
        self.mutate_row(1, 0, edit)
        result = self.result()
        row = result['windows'][0]['requests'][0]
        self.assertTrue(result['valid'], result['windows'][0]['validation_errors'])
        self.assertTrue(row['completed'])
        self.assertFalse(row['on_time'])
        self.assertEqual(result['windows'][0]['on_time_count'], 9)
        self.assertLess(row['completion_latency_s'] - row['dispatch_lag_s'], 5)

    def test_exact_deadline_is_on_time(self):
        def edit(row):
            row['terminal_offset_s'] = 5
            row['chunks'][-1]['offset_s'] = 4.999
        self.mutate_row(1, 0, edit)
        self.assertTrue(self.result()['windows'][0]['requests'][0]['on_time'])

    def test_transport_failure_stays_in_denominator(self):
        def fail(row):
            row.update(completed=False, error='HTTP 503 fixture', chunks=[], final=None,
                       first_content_offset_s=None, terminal_offset_s=.02)
        self.mutate_row(1, 0, fail)
        result = self.result()
        window = result['windows'][0]
        self.assertTrue(window['valid'], window['validation_errors'])
        self.assertEqual(window['offered_count'], 16)
        self.assertEqual(window['completed_count'], 15)
        self.assertEqual(window['failure_count'], 1)
        self.assertEqual(window['on_time_fraction'], 9/16)
        self.assertEqual(window['completion_latency_s']['n'], 15)
        self.assertFalse(result['gate']['passed'])

    def test_missing_duplicate_and_extra_rows_never_change_denominator(self):
        path = self.path(1, 'REQUESTS.json')
        collection = self.load(path)
        original = copy.deepcopy(collection)
        for rows in (original['requests'][1:], original['requests'] + [original['requests'][0]],
                     original['requests'] + [self.row('extra', 0)]):
            with self.subTest(count=len(rows)):
                collection['requests'] = rows
                self.save(path, collection)
                result = self.result()
                window = result['windows'][0]
                self.assertEqual(window['offered_count'], 16)
                self.assertEqual(len(window['requests']), 16)
                self.assertFalse(window['valid'])
                self.assertFalse(result['gate']['passed'])
                if len(rows) == 15 or rows[-1]['request_id'] == 'r01':
                    self.assertEqual(window['failure_count'], 1)

    def test_nearest_rank_including_even_median_and_small_sample_p95(self):
        self.assertEqual(analyze.nearest_rank(list(range(1, 17)), .5), 8)
        self.assertEqual(analyze.nearest_rank(list(range(1, 17)), .95), 16)
        self.assertEqual(analyze.nearest_rank([4], .95), 4)
        self.assertIsNone(analyze.nearest_rank([], .95))

    def test_claimed_success_is_revalidated_against_raw_stream(self):
        edits = [lambda row: row['final'].update(eval_count=True),
                 lambda row: row['chunks'][-1]['data'].update(done=False),
                 lambda row: row.update(first_content_offset_s=.11),
                 lambda row: row['chunks'][0]['data'].update(response=''),
                 lambda row: row['final'].update(model='wrong-model'),
                 lambda row: row['chunks'][0].update(offset_s=-.1),
                 lambda row: row.update(completed=1),
                 lambda row: row.update(arrival_offset_s=.2),
                 lambda row: row.update(http_status=503),
                 lambda row: row['chunks'][0]['data'].update(error='')]
        original = self.load(self.path(1, 'REQUESTS.json'))
        for edit in edits:
            with self.subTest(edit=edit):
                self.save(self.path(1, 'REQUESTS.json'), original)
                self.mutate_row(1, 0, edit)
                window = self.result()['windows'][0]
                self.assertFalse(window['valid'])
                self.assertFalse(window['requests'][0]['completed'])
                self.assertEqual(window['failure_count'], 1)

    def test_environment_invalidity_retains_metrics_and_blocks_gate(self):
        path = self.path(1, 'RUN.json')
        original = self.load(path)
        edits = [lambda meta: meta['loaded_after']['models'][0].update(digest='wrong'),
                 lambda meta: meta['loaded_before']['models'][0].update(context_length=4096),
                 lambda meta: meta['loaded_before']['models'][0].update(size_vram=0),
                 lambda meta: meta.update(original_endpoint_idle_after=False),
                 lambda meta: meta['before'].update(power="Now drawing from 'Battery Power'"),
                 lambda meta: meta['after'].update(thermal='Thermal warning level: 1'),
                 lambda meta: meta.update(loaded_after_unload={'models': [{}]})]
        for edit in edits:
            with self.subTest(edit=edit):
                meta = copy.deepcopy(original)
                edit(meta)
                self.save(path, meta)
                self.sync_campaign()
                result = self.result()
                window = result['windows'][0]
                self.assertFalse(window['valid'])
                self.assertEqual(window['on_time_count'], 10)
                self.assertEqual(window['completed_count'], 16)
                self.assertFalse(result['gate']['passed'])

    def test_log_evidence_required_not_just_desired_settings(self):
        self.path(1, 'SERVER.log').write_text('OLLAMA_NUM_PARALLEL=1\n')
        result = self.result()
        self.assertFalse(result['windows'][0]['valid'])
        self.assertFalse(result['gate']['passed'])
        self.assertTrue(any('actual parallelism' in x for x in result['windows'][0]['validation_errors']))

    def test_dispatch_slippage_invalidates_window(self):
        def edit(row):
            row['dispatch_offset_s'] = .11
            row['first_content_offset_s'] = .12
            row['chunks'][0]['offset_s'] = .12
        self.mutate_row(1, 0, edit)
        result = self.result()
        self.assertFalse(result['windows'][0]['valid'])
        self.assertFalse(result['gate']['passed'])
        self.assertEqual(result['windows'][0]['maximum_dispatch_lag_s'], .11)
        self.assertTrue(result['windows'][0]['requests'][0]['completed'])
        self.assertEqual(result['windows'][0]['completed_count'], 16)
        self.assertEqual(result['windows'][0]['on_time_count'], 10)
        self.assertEqual(result['windows'][0]['failure_count'], 0)

    def test_missing_window_yields_sixteen_failed_offers_and_still_four_pairs(self):
        for path in self.path(1, 'RUN.json').parent.iterdir():
            path.unlink()
        result = self.result()
        self.assertEqual(result['windows'][0]['failure_count'], 16)
        self.assertEqual(result['offered_count'], 128)
        self.assertEqual(len(result['pairs']), 4)
        self.assertFalse(result['gate']['passed'])

    def test_freeze_tampering_and_campaign_order_block_gate(self):
        (self.source / 'client.py').write_text('changed')
        result = self.result()
        self.assertFalse(result['valid'])
        self.assertTrue(any('changed client.py' in x for x in result['validation_errors']))
        self.assertTrue(all(not w['valid'] for w in result['windows']))
        campaign = self.load(self.data / 'CAMPAIGN.json')
        campaign['windows'][0], campaign['windows'][1] = campaign['windows'][1], campaign['windows'][0]
        self.save(self.data / 'CAMPAIGN.json', campaign)
        self.assertTrue(any('order mismatch' in x for x in self.result()['validation_errors']))

    def test_partial_output_and_differing_outputs_are_retained(self):
        self.mutate_row(2, 0, lambda row: row['chunks'][0]['data'].update(response='different'))
        result = self.result()
        self.assertTrue(result['valid'])
        self.assertEqual(result['windows'][1]['completed_count'], 16)
        self.assertEqual(result['pairs'][0]['equal_output_count'], 15)
        self.assertFalse(result['pairs'][0]['output_equality_by_request'][0]['output_equal'])

    def test_warmup_failure_and_wait_violation_block_gate(self):
        path = self.path(1, 'WARMUP.json')
        warm = self.load(path)
        warm['requests'][0]['final']['eval_count'] = -1
        warm['started_utc'] = self.timestamp(3)
        self.save(path, warm)
        result = self.result()
        self.assertFalse(result['gate']['passed'])
        self.assertEqual(result['windows'][0]['warmup_completed_count'], 1)
        self.assertTrue(any('post-warmup wait' in x for x in result['windows'][0]['validation_errors']))


if __name__ == '__main__':
    unittest.main()
