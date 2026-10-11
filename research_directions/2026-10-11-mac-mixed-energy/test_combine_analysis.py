"""Offline guard tests and one synthetic integration through the frozen modules.

Set COMBINE_PATH/SOURCE_DIR to test staged files. No capture directory is read.
"""
import copy
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import gzip
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
COMBINE = Path(os.environ.get('COMBINE_PATH', str(HERE/'combine_analysis.py' if (HERE/'combine_analysis.py').exists() else Path('/tmp/coop-mixed-combine.py'))))
SOURCE = Path(os.environ.get('SOURCE_DIR', str(HERE if (HERE/'analyze.py').exists() else Path('/tmp/coop-mac-mixed'))))


def load_module(name, path):
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name, path))
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


combine = load_module('combine_under_test', COMBINE)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True)+'\n')


def read(path):
    return json.loads(path.read_text())


def ts(seconds):
    return (datetime(2026, 10, 11, tzinfo=timezone.utc)+timedelta(seconds=seconds)).isoformat()


def hashed(path):
    return combine.digest(path.read_bytes())


class Guards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root/'source'
        self.source.mkdir()
        self.config = {'planned_offered': 18}
        self.plan = [dict(index=i, rate=rate, parallel=p, rep=rep, trace_file=f'traces/{rate}-{rep}.json')
                     for i, (rate, rep, p) in enumerate(((r, j, p) for r in (.3, .6, 1.2) for j in (1, 2) for p in (1, 2, 4)), 1)]
        save(self.source/'CONFIG.json', self.config)
        save(self.source/'PLAN.json', self.plan)
        for name in {'analyze.py', 'energy.py', 'independent_check.py', 'continue_study.py', 'combine_analysis.py'}:
            (self.source/name).write_text('# synthetic source\n')
        shutil.copyfile(COMBINE, self.source/'combine_analysis.py')
        for plan in self.plan:
            save(self.source/plan['trace_file'], [])
        (self.source/'CONTINUATION_PROTOCOL.txt').write_text('Prospective synthetic suffix protocol.\n')
        files = ['CONFIG.json', 'PLAN.json', 'analyze.py', 'energy.py'] + sorted({p['trace_file'] for p in self.plan})
        save(self.source/'FREEZE.json', dict(frozen_utc=ts(0), sha256={name: hashed(self.source/name) for name in files}))
        self.first = self.segment('first', range(1, 10), 'budget_stopped', 1, 2000)
        self.second = self.segment('suffix', range(10, 19), 'completed', 2001, 4000)
        self.lineage()
        self.manifest()

    def segment(self, name, indices, status, start, finish):
        path = self.root/name
        path.mkdir()
        save(path/'CONFIG.json', self.config)
        save(path/'PLAN.json', self.plan)
        rows = [dict(self.plan[i-1], status='completed') for i in indices]
        for row in rows:
            save(path/f"window-{row['index']:02d}"/'RUN.json', row)
            save(path/f"window-{row['index']:02d}"/'REQUESTS.json', {'requests': []})
        save(path/'CAMPAIGN.json', dict(status=status, started_utc=ts(start), finished_utc=ts(finish), windows=rows,
                                       power_stop=dict(stop_confirmed=True, returncode=0)))
        (path/'POWER.txt.gz').write_bytes(gzip.compress(b'synthetic power'))
        save(path/'POWER_STOP.json', dict(stop_confirmed=True, returncode=0))
        return path

    def lineage(self):
        campaign = read(self.second/'CAMPAIGN.json')
        campaign.update(continuation_of=self.first.name, completed_prefix=[r['index'] for r in read(self.first/'CAMPAIGN.json')['windows']],
                        amendment='CONTINUATION_PROTOCOL.txt', amendment_sha256=hashed(self.source/'CONTINUATION_PROTOCOL.txt'),
                        source_freeze_sha256=hashed(self.source/'FREEZE.json'), original_campaign_sha256=hashed(self.first/'CAMPAIGN.json'),
                        original_power_sha256=hashed(self.first/'POWER.txt.gz'), continuation_script_sha256=hashed(self.source/'continue_study.py'))
        save(self.second/'CAMPAIGN.json', campaign)
        save(self.first/'CONTINUATION_CLAIM.json', dict(created_utc=ts(2000.5), output_directory=str(self.second), source_freeze_sha256=hashed(self.source/'FREEZE.json')))

    def validate(self, paths=None):
        config, plan, frozen = combine.frozen_inputs(self.source)
        return combine.validate_segments(self.source, paths or [self.first, self.second], config, plan, frozen)

    def mutate(self, path, function):
        data = read(path)
        function(data)
        save(path, data)

    def assertReject(self, expression=None):
        with self.assertRaises(combine.CombineError):
            (expression or self.validate)()

    def test_accept_consecutive_prefix_suffix_and_single_prefix(self):
        segments = self.validate()
        self.assertEqual([s['indices'] for s in segments], [list(range(1, 10)), list(range(10, 19))])
        self.assertEqual(len(self.validate([self.first])), 1)
        self.assertIn('CONTINUATION_CLAIM.json', segments[0]['provenance'])

    def test_accept_partial_suffix_and_empty_budget_suffix(self):
        shutil.rmtree(self.second)
        self.second = self.segment('suffix', range(10, 13), 'budget_stopped', 2001, 4000)
        self.lineage()
        self.assertEqual(self.validate()[1]['indices'], [10, 11, 12])
        shutil.rmtree(self.second)
        self.second = self.segment('suffix', [], 'budget_stopped', 2001, 4000)
        self.lineage()
        self.assertEqual(self.validate()[1]['indices'], [])

    def test_reject_empty_sole_segment(self):
        empty = self.segment('empty', [], 'budget_stopped', 1, 2000)
        self.assertReject(lambda: self.validate([empty]))

    def test_reject_overlap_or_gap(self):
        for indices in (range(9, 19), range(11, 19)):
            shutil.rmtree(self.second)
            self.second = self.segment('suffix', indices, 'completed', 2001, 4000)
            self.lineage()
            self.assertReject()

    def test_reject_duplicate_paths(self):
        self.assertReject(lambda: self.validate([self.first, self.first]))

    def test_reject_nonbudget_or_failed_attempt_prefix(self):
        self.mutate(self.first/'CAMPAIGN.json', lambda x: x.update(status='aborted'))
        self.lineage()
        self.assertReject()
        self.mutate(self.first/'CAMPAIGN.json', lambda x: (x.update(status='budget_stopped'), x['windows'][0].update(status='failed')))
        self.mutate(self.first/'window-01'/'RUN.json', lambda x: x.update(status='failed'))
        self.lineage()
        self.assertReject()

    def test_reject_extra_or_missing_directory(self):
        (self.second/'window-19').mkdir()
        self.assertReject()
        (self.second/'window-19').rmdir()
        shutil.rmtree(self.second/'window-18')
        self.assertReject()

    def test_reject_different_captured_config(self):
        self.mutate(self.second/'CONFIG.json', lambda x: x.update(planned_offered=17))
        self.assertReject()

    def test_reject_different_captured_plan(self):
        self.mutate(self.second/'PLAN.json', lambda x: x[0].update(parallel=4))
        self.assertReject()

    def test_reject_campaign_run_disagreement(self):
        self.mutate(self.second/'window-10'/'RUN.json', lambda x: x.update(extra='unrecorded'))
        self.assertReject()

    def test_reject_completed_status_with_missing_suffix(self):
        shutil.rmtree(self.second/'window-18')
        self.mutate(self.second/'CAMPAIGN.json', lambda x: x['windows'].pop())
        self.assertReject()

    def test_reject_lineage_and_recorded_hash_mismatch(self):
        for field, value in [('continuation_of', 'other'), ('completed_prefix', [1]), ('source_freeze_sha256', 'bad'),
                             ('amendment_sha256', 'bad'), ('original_campaign_sha256', 'bad'),
                             ('original_power_sha256', 'bad'), ('continuation_script_sha256', 'bad')]:
            self.lineage()
            self.mutate(self.second/'CAMPAIGN.json', lambda x: x.update({field: value}))
            with self.subTest(field=field):
                self.assertReject()

    def test_reject_claim_and_bad_chronology(self):
        for field, value in [('output_directory', str(self.first)), ('created_utc', ts(2002)), ('source_freeze_sha256', 'bad')]:
            self.lineage()
            self.mutate(self.first/'CONTINUATION_CLAIM.json', lambda x: x.update({field: value}))
            self.assertReject()
        self.lineage()
        self.mutate(self.second/'CAMPAIGN.json', lambda x: x.update(started_utc=ts(1999)))
        self.assertReject()

    def test_reject_missing_or_changed_amendment(self):
        (self.source/'CONTINUATION_PROTOCOL.txt').unlink()
        self.assertReject()

    def test_source_freeze_integrity(self):
        (self.source/'energy.py').write_text('changed')
        self.assertReject()

    def manifest(self, time=1999):
        names = ('CONTINUATION_PROTOCOL.txt', 'continue_study.py', 'combine_analysis.py', 'independent_check.py')
        save(self.source/'CONTINUATION_FREEZE.json', dict(frozen_utc=ts(time), sha256={n: hashed(self.source/n) for n in names}))

    def test_continuation_freeze_hashes_and_timestamp(self):
        self.manifest()
        self.assertEqual(self.validate()[1]['continuation_freeze']['frozen_utc'], ts(1999))
        self.manifest(2002)
        self.assertReject()
        self.manifest()
        (self.source/'independent_check.py').write_text('changed')
        self.assertReject()

    def test_reject_missing_continuation_freeze(self):
        (self.source/'CONTINUATION_FREEZE.json').unlink()
        self.assertReject()

    def test_reject_incomplete_continuation_freeze(self):
        for name in ('independent_check.py', 'combine_analysis.py', 'continue_study.py', 'CONTINUATION_PROTOCOL.txt'):
            self.manifest()
            self.mutate(self.source/'CONTINUATION_FREEZE.json', lambda x: x['sha256'].pop(name))
            with self.subTest(missing=name):
                self.assertReject()
    def test_continuation_freeze_paths_cannot_escape(self):
        self.mutate(self.source/'CONTINUATION_FREEZE.json', lambda x: x['sha256'].update({'../outside': 'x'}))
        self.assertReject()

    def test_bad_power_is_diagnostic_and_retains_samples(self):
        class Energy:
            @staticmethod
            def parse_text(text):
                return dict(samples=[{'marker': text}], errors=[])
        segment = self.validate()[0]
        self.mutate(self.first/'POWER_STOP.json', lambda x: x.update(returncode=-15))
        parsed = combine.segment_power(segment, Energy)
        self.assertEqual(len(parsed['samples']), 1)
        self.assertTrue(parsed['errors'])
        self.assertEqual(parsed['samples'][0]['marker'], 'synthetic power')

    def test_missing_power_not_zero_energy(self):
        (self.first/'POWER.txt.gz').unlink()
        segment = self.validate([self.first])[0]
        parsed = combine.segment_power(segment, object())
        self.assertEqual(parsed['samples'], [])
        self.assertTrue(parsed['errors'])


class Integration(unittest.TestCase):
    def test_frozen_real_modules_with_full_and_partial_synthetic_segments(self):
        # Reuse only the frozen test fixture constructor, never any real capture.
        with combine.frozen_modules(SOURCE) as (analyzer, energy, checker):
            with patch.dict('sys.modules', {'analyze': analyzer}):
                fixtures = load_module('frozen_fixture', SOURCE/'test_analysis.py')
                fixture = fixtures.MixedAnalysisTests()
                fixture.setUp()
                self.addCleanup(fixture.doCleanups)
            source, original = fixture.source, fixture.data
            for name in ('analyze.py', 'energy.py', 'independent_check.py'):
                shutil.copyfile(SOURCE/name, source/name)
            freeze = read(source/'FREEZE.json')
            freeze['sha256'].update({name: hashed(source/name) for name in ('analyze.py', 'energy.py', 'independent_check.py')})
            save(source/'FREEZE.json', freeze)
            (source/'continue_study.py').write_text('# synthetic continuation wrapper\n')
            (source/'CONTINUATION_PROTOCOL.txt').write_text('Synthetic prospective continuation.\n')
            shutil.copyfile(COMBINE, source/'combine_analysis.py')
            names = ('CONTINUATION_PROTOCOL.txt', 'continue_study.py', 'combine_analysis.py', 'independent_check.py')
            save(source/'CONTINUATION_FREEZE.json', dict(frozen_utc=ts(1999), sha256={name: hashed(source/name) for name in names}))
            first, second = fixture.base/'prefix', fixture.base/'suffix'
            for path, indices, status, start, finish, watts in ((first, range(1, 10), 'budget_stopped', 0, 2000, 3),
                                                              (second, range(10, 19), 'completed', 2001, 4000, 6)):
                path.mkdir()
                for name in ('CONFIG.json', 'PLAN.json'):
                    shutil.copyfile(source/name, path/name)
                rows = []
                for index in indices:
                    shutil.move(str(original/f'window-{index:02d}'), path/f'window-{index:02d}')
                    rows.append(read(path/f'window-{index:02d}'/'RUN.json'))
                save(path/'CAMPAIGN.json', dict(status=status, started_utc=ts(start), finished_utc=ts(finish), windows=rows,
                                              power_stop=dict(stop_confirmed=True, returncode=0)))
                samples = []
                for sec in range(start-2, finish+3):
                    stamp = (datetime(2026, 10, 11, tzinfo=timezone.utc)+timedelta(seconds=sec)).strftime('%a %b %d %H:%M:%S %Y +0000')
                    samples.append(f'*** Sampled system activity ({stamp}) (1000ms elapsed) ***\n**** Processor usage ****\nCPU Power: 0 mW\nGPU Power: {watts*1000} mW\nANE Power: 0 mW\nCombined Power (CPU + GPU + ANE): {watts*1000} mW\n')
                (path/'POWER.txt.gz').write_bytes(gzip.compress(''.join(samples).encode()))
                save(path/'POWER_STOP.json', dict(stop_confirmed=True, returncode=0))
            campaign = read(second/'CAMPAIGN.json')
            campaign.update(continuation_of=first.name, completed_prefix=list(range(1, 10)),
                            amendment='CONTINUATION_PROTOCOL.txt', amendment_sha256=hashed(source/'CONTINUATION_PROTOCOL.txt'),
                            source_freeze_sha256=hashed(source/'FREEZE.json'), original_campaign_sha256=hashed(first/'CAMPAIGN.json'),
                            original_power_sha256=hashed(first/'POWER.txt.gz'), continuation_script_sha256=hashed(source/'continue_study.py'))
            save(second/'CAMPAIGN.json', campaign)
            save(first/'CONTINUATION_CLAIM.json', dict(created_utc=ts(2000.5), output_directory=str(second.resolve()), source_freeze_sha256=hashed(source/'FREEZE.json')))
            before = {str(p): hashed(p) for root in (source, first, second) for p in root.rglob('*') if p.is_file()}
            result = combine.combine(source, [first, second])
            self.assertTrue(result['full_collection_completed'])
            self.assertTrue(result['summary']['valid'])
            self.assertTrue(result['reproduction_checks']['passed'], result['reproduction_checks']['mismatches'][:3])
            self.assertGreater(result['reproduction_checks']['exact_comparisons'], 5000)
            self.assertEqual(result['independent_counts']['aggregate_mixed_class_totals']['overall']['quality_slo_count'], 1134)
            a, b = (result['summary']['windows'][i]['energy']['intervals']['full_episode'] for i in (0, 9))
            self.assertTrue(a['valid'], a['errors'])
            self.assertTrue(b['valid'], b['errors'])
            self.assertEqual(b['lower_j']['combined'], 2*a['lower_j']['combined'])
            self.assertEqual(b['combined_j_per_quality_slo_success']['lower'], b['lower_j']['combined']/result['summary']['windows'][9]['metrics']['quality_slo_count'])
            after = {str(p): hashed(p) for root in (source, first, second) for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            bad = copy.deepcopy(result['independent_counts'])
            bad['rate_parallel_cells'][0]['metrics']['overall']['completion_latency_s']['p95'] += .01
            checks = combine.compare_recounts(result['summary'], bad, analyzer)
            self.assertFalse(checks['passed'])
            self.assertTrue(any('completion_latency_s' in item['field'] for item in checks['mismatches']))
            bad['rate_parallel_cells'].pop()
            self.assertFalse(combine.compare_recounts(result['summary'], bad, analyzer)['passed'])
            # A terminal prefix still has all 1,134 planned denominator rows.
            partial = combine.combine(source, [first])
            self.assertFalse(partial['full_collection_completed'])
            self.assertEqual(partial['unrun_window_indices'], list(range(10, 19)))
            self.assertEqual(partial['summary']['analyzed_planned_count'], 1134)
            self.assertFalse(partial['summary']['valid'])
            self.assertTrue(partial['reproduction_checks']['passed'])
            self.assertEqual(partial['summary']['windows'][9]['metrics']['quality_slo_count'], 0)
            self.assertIsNone(partial['summary']['windows'][9]['energy']['intervals']['full_episode']['combined_j_per_quality_slo_success'])
            # Post-capture integration case: a failed attempted suffix is retained.
            last_path = second/'window-18'/'RUN.json'
            last = read(last_path)
            failed_campaign = copy.deepcopy(campaign)
            failed_campaign['status'] = 'aborted'
            failed_campaign['windows'][-1]['status'] = 'failed'
            save(last_path, dict(last, status='failed'))
            save(second/'CAMPAIGN.json', failed_campaign)
            failed = combine.combine(source, [first, second])
            self.assertFalse(failed['full_collection_completed'])
            self.assertEqual(failed['unrun_window_indices'], [])
            self.assertFalse(failed['summary']['valid'])
            self.assertTrue(failed['reproduction_checks']['passed'])
            self.assertEqual(failed['summary']['analyzed_planned_count'], 1134)
            self.assertEqual(failed['independent_counts']['recorded_request_rows'], 1134)
            # Post-capture integration case: one valid sample cannot cover an episode.
            save(last_path, last)
            save(second/'CAMPAIGN.json', campaign)
            (second/'POWER.txt.gz').write_bytes(gzip.compress(samples[-1].encode()))
            uncovered = combine.combine(source, [first, second])
            self.assertTrue(uncovered['full_collection_completed'])
            self.assertTrue(uncovered['summary']['valid'])
            self.assertTrue(uncovered['reproduction_checks']['passed'])
            self.assertTrue(uncovered['summary']['windows'][0]['energy']['intervals']['full_episode']['valid'])
            for window in uncovered['summary']['windows'][9:]:
                interval = window['energy']['intervals']['full_episode']
                self.assertFalse(interval['valid'])
                self.assertIsNone(interval['combined_j_per_quality_slo_success'])


if __name__ == '__main__':
    unittest.main()
