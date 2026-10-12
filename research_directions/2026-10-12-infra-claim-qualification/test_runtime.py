"""Synthetic offline regressions; never call a model or inspect live hardware."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import audit_runtime as audit
import collect


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True) + '\n')


def stamp(ns):
    return dict(monotonic_before_ns=ns, monotonic_after_ns=ns+100, wall_ns=ns+10**15+50)


def raw(identifier, text, ns, prompt, options, cap=256):
    final = dict(model=audit.MODEL, done=True, response='', prompt_eval_count=100, eval_count=30,
                 total_duration=700000000, load_duration=1000, prompt_eval_duration=200000000,
                 eval_duration=499999000, done_reason='stop')
    row = dict(request_id=identifier, arrival_offset_s=0, dispatch_offset_s=.01,
               first_content_offset_s=.1, terminal_offset_s=.8, http_status=200, completed=True,
               error=None, deadline_exceeded=False, request_prompt=prompt, request_model=audit.MODEL,
               request_options=dict(options, num_predict=cap), request_format=audit.SCHEMA, request_think=False,
               chunks=[dict(offset_s=.1, data=dict(response=text, done=False, model=audit.MODEL)),
                       dict(offset_s=.8, data=copy.deepcopy(final))], final=final)
    start, end = stamp(ns), stamp(ns+10**9)
    return dict(started_stamp=start, finished_stamp=end, epoch_monotonic_ns=start['monotonic_after_ns'],
                elapsed_seconds=(end['monotonic_before_ns']-start['monotonic_after_ns'])/10**9, requests=[row])


def cases():
    return [dict(request_id='c'+str(i), source_id='manual',
                 passages=[dict(id='p1', text='The component has the stated specification.'),
                           dict(id='p2', text='An unrelated component is blue.'),
                           dict(id='p3', text='A relevant condition holds.')],
                 claim='Case ' + str(i), label=label,
                 acceptable_evidence=[] if label == 'insufficient' else [['p1']],
                 relevant_evidence=[] if label == 'insufficient' else ['p1', 'p3'])
            for i, label in enumerate(label for label in audit.LABELS for _ in range(8))]


def prediction(job):
    return dict(verdict=job['label'], evidence=[] if job['label'] == 'insufficient' else ['p1'])


class Fixture:
    def __init__(self, root, bad=None):
        self.base, self.capture = root / 'source', root / 'capture'
        self.base.mkdir(); self.capture.mkdir()
        self.config = dict(model=audit.MODEL, context=4096, think=False, budget_s=1800,
                           request_timeout_s=90, max_output_tokens=256,
                           options=dict(num_ctx=4096, num_predict=256, temperature=0, seed=0),
                           allow_battery_quality=True, server_settings_common={'OLLAMA_CONTEXT_LENGTH': '4096'})
        manifest = dict(config=dict(digest='sha256:'+'0'*64, size=1),
                        layers=[dict(digest='sha256:'+str(i)*64, size=i+1) for i in range(1, 5)])
        save(self.base / 'MODEL_MANIFEST.json', manifest)
        self.digest = hashlib.sha256((self.base / 'MODEL_MANIFEST.json').read_bytes()).hexdigest()
        self.config.update(digest=self.digest, lock=dict(binary_sha256='binary', manifest_sha256=self.digest))
        save(self.base / 'MODEL_LOCK.json', dict(self.config['lock'], blob_checks={
            d['digest']: dict(verified=True, bytes=d['size']) for d in [manifest['config']]+manifest['layers']}))
        save(self.base / 'CONFIG.json', self.config)
        self.jobs = cases(); save(self.base / 'cases.json', self.jobs)
        self.instruction = 'Assess the claim only against the packet. /no_think'
        (self.base / 'contract.py').write_text('INSTRUCTION = '+repr(self.instruction)+'\nSCHEMA = '+repr(audit.SCHEMA)+'\n')
        for name in ('collect.py', 'audit_runtime.py', 'transport_audit.py', 'client.py', 'server_control.py', 'clock_bridge.py', 'PROTOCOL.txt'):
            (self.base / name).write_text('synthetic frozen source\n')
        (self.base / 'source.txt').write_text('Synthetic source text.\n')
        (self.base / 'license.txt').write_text('Synthetic license.\n')
        save(self.base / 'SOURCE_MANIFEST.json', [dict(id='manual', source_file='source.txt',
             sha256=hashlib.sha256((self.base / 'source.txt').read_bytes()).hexdigest(),
             license_file='license.txt', license_sha256=hashlib.sha256((self.base / 'license.txt').read_bytes()).hexdigest())])
        self.freeze()
        self.path = self.capture / 'qualification'; self.path.mkdir()
        ns = 1000 * 10**9; stamps = [stamp(ns)]; entries = []
        for i, job in enumerate(self.jobs):
            answer = prediction(job)
            if bad and i in bad:
                answer = bad[i]
            text = answer if type(answer) is str else json.dumps(answer)
            data = raw(job['request_id'], text, ns+(3*i+1)*10**9+10**8,
                       audit.prompt_for(job, self.instruction), self.config['options'])
            save(self.path / (job['request_id']+'.json'), data)
            t = ns+(3*i+1)*10**9
            stamps.extend([stamp(t), data['started_stamp'], data['finished_stamp'], stamp(t+2*10**9)])
            entries.append(dict(request_id=job['request_id'], source_id=job['source_id'], label=job['label'],
                raw_file=job['request_id']+'.json', api_completed=True, output_tokens=30, done_reason='stop',
                observed_context_margin=4096-100-256, **audit.score_output(text, job)))
        stamps.append(stamp(ns+(3*24+3)*10**9))
        gate = audit.gate_counts(self.jobs, entries)
        stage = dict(part='qualification', candidate=audit.MODEL, planned=24, status='completed', requests=entries,
                     started_utc='2026-01-01T00:01:00+00:00', finished_utc='2026-01-01T00:03:00+00:00',
                     quality_count=gate['quality_correct'], gate_passed=gate['passed'],
                     clock_stamps=stamps, clock_diagnostics=audit.clock_check(stamps))
        save(self.path / 'STAGE.json', stage)
        save(self.path / 'WARMUP.json', raw('warm', '{"verdict":"insufficient","evidence":[]}', ns-2*10**9,
                                          audit.WARM_PROMPT, self.config['options'], 32))
        state = dict(power="Now drawing from 'Battery Power'\n -InternalBattery-0 (id=REDACTED) 80%; discharging;",
                     power_source='Battery Power', battery_percent=80, external_power_connected=False,
                     thermal='No thermal warning level has been recorded\nNo performance warning level has been recorded')
        loaded = dict(name=audit.MODEL, digest=self.digest, context_length=4096, size_vram=20000000000)
        meta = dict(status='completed', errors=[], clean_unload_verified=True, loaded_after_unload={'models': []},
                    dedicated_server_returncode=0, model=audit.MODEL, context=4096, parallel=1, runtime_parallel_values=[1],
                    version={'version': '0.20.0'}, model_tag={'name': audit.MODEL, 'digest': self.digest}, options=self.config['options'],
                    server_settings=dict(self.config['server_settings_common'], OLLAMA_NUM_PARALLEL='1'), allow_battery_quality=True,
                    lock_verification=self.config['lock'], dedicated_server_pid=12345, dedicated_process_group=12345,
                    loaded_checks=[{'response': {'models': [loaded]}} for _ in range(3)], before=state, after=state,
                    original_endpoint_idle_before=True, original_endpoint_idle_after=True,
                    host_checks=[dict(phase=prefix+j['request_id'], passed=True, original_endpoint_idle=True, state=state)
                                 for j in self.jobs for prefix in ('before_', 'after_')])
        save(self.path / 'SERVER_CONTROL.json', meta); (self.path / 'SERVER.log').write_text('n_seq_max = 1\n')
        self.campaign()

    def freeze(self):
        save(self.base / 'FREEZE.json', {'sha256': {str(p.relative_to(self.base)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in self.base.rglob('*') if p.is_file() and p.name != 'FREEZE.json'}})

    def campaign(self):
        stage = json.loads((self.path / 'STAGE.json').read_text())
        save(self.capture / 'CAMPAIGN.json', dict(started_utc='2026-01-01T00:00:00+00:00',
             finished_utc='2026-01-01T00:04:00+00:00', status='completed', selected=audit.MODEL,
             qualified=stage.get('gate_passed', False), stages=[stage],
             source_freeze_sha256=hashlib.sha256((self.base / 'FREEZE.json').read_bytes()).hexdigest()))

    def change(self, name, update):
        path = self.path / name; value = json.loads(path.read_text()); update(value); save(path, value)

    def analyze(self):
        with patch.object(audit, 'DIGEST', self.digest):
            return audit.analyze(self.base, self.capture)


class ScoreTests(unittest.TestCase):
    def test_sufficient_relevant_citations(self):
        job = cases()[0]
        for ids in (['p1'], ['p1', 'p3']):
            self.assertTrue(audit.score_output(json.dumps(dict(verdict='supported', evidence=ids)), job)['quality_pass'])
        for ids in ([], ['p3'], ['p1', 'unknown'], ['p1', 'p2']):
            self.assertFalse(audit.score_output(json.dumps(dict(verdict='supported', evidence=ids)), job)['quality_pass'])

    def test_multi_passage_evidence_requires_complete_set(self):
        job = dict(cases()[0], acceptable_evidence=[['p1', 'p3']])
        self.assertFalse(audit.score_output('{"verdict":"supported","evidence":["p1"]}', job)['quality_pass'])
        self.assertTrue(audit.score_output('{"verdict":"supported","evidence":["p3","p1"]}', job)['quality_pass'])

    def test_wrong_verdict_and_nonempty_abstention(self):
        self.assertFalse(audit.score_output('{"verdict":"contradicted","evidence":["p1"]}', cases()[0])['quality_pass'])
        self.assertFalse(audit.score_output('{"verdict":"insufficient","evidence":["p1"]}', cases()[-1])['quality_pass'])
        self.assertTrue(audit.score_output('{"verdict":"insufficient","evidence":[]}', cases()[-1])['quality_pass'])

    def test_strict_schema(self):
        for text in ('[]', '{"verdict":"supported","evidence":["p1","p1"]}',
                     '{"verdict":"supported","verdict":"supported","evidence":["p1"]}',
                     '{"verdict":"supported","evidence":[1]}', '{"verdict":"other","evidence":[]}',
                     '{"verdict":"supported","evidence":["p1"],"reason":"because"}',
                     '{"verdict":"supported","evidence":[]} trailing',
                     '{"verdict":"supported","evidence":["a","b","c","d"]}'):
            self.assertFalse(audit.score_output(text, cases()[0])['schema_valid'], text)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)

    def fixture(self, bad=None):
        return Fixture(Path(self.tmp.name), bad)

    def test_complete_passing_fixture(self):
        result = self.fixture().analyze()
        self.assertTrue(result['data_complete_valid'], result['faults'])
        self.assertTrue(result['qualified']); self.assertEqual(result['counts']['quality_correct'], 24)

    def test_schema_failure_closes_gate_but_is_valid_negative_result(self):
        result = self.fixture({0: 'invalid JSON'}).analyze()
        self.assertTrue(result['data_complete_valid'], result['faults']); self.assertFalse(result['qualified'])
        self.assertEqual(result['counts']['raw_offered'], 24)

    def test_two_allowed_misses_pass(self):
        result = self.fixture({0: dict(verdict='insufficient', evidence=[]),
                               8: dict(verdict='insufficient', evidence=[])}).analyze()
        self.assertTrue(result['qualified'], result['faults'])

    def test_false_support_closes_otherwise_passing_gate(self):
        result = self.fixture({8: dict(verdict='supported', evidence=['p1'])}).analyze()
        self.assertTrue(result['data_complete_valid'], result['faults']); self.assertFalse(result['qualified'])
        self.assertEqual(result['stages'][0]['gate']['false_support'], 1)

    def test_any_insufficient_miss_fails(self):
        result = self.fixture({23: dict(verdict='contradicted', evidence=['p1'])}).analyze()
        self.assertTrue(result['data_complete_valid'], result['faults']); self.assertFalse(result['qualified'])

    def test_missing_case_cannot_pass_by_dropping_denominator(self):
        fx = self.fixture(); (fx.path / 'c23.json').unlink()
        result = fx.analyze(); self.assertFalse(result['qualified']); self.assertFalse(result['data_complete_valid'])
        self.assertEqual(result['stages'][0]['missing_ids'], ['c23'])

    def test_postflight_orphan_remains_visible(self):
        fx = self.fixture(); fx.change('STAGE.json', lambda s: s.update(status='aborted', requests=s['requests'][:1], gate_passed=False))
        fx.campaign(); result = fx.analyze()
        self.assertFalse(result['qualified']); self.assertEqual(result['counts']['raw_offered'], 24)
        self.assertEqual(len(result['stages'][0]['orphan_raw_ids']), 23)
        self.assertEqual(result['counts']['summary_recorded'], 1)

    def test_prompt_and_source_tampering_are_detected(self):
        fx = self.fixture(); fx.change('c0.json', lambda r: r['requests'][0].update(request_prompt='different'))
        result = fx.analyze(); self.assertFalse(result['data_complete_valid'])
        self.assertTrue(any('canonical prompt' in s for s in result['faults']))
        (fx.base / 'cases.json').write_text((fx.base / 'cases.json').read_text()+' ')
        result = fx.analyze(); self.assertTrue(any('freeze mismatch: cases.json' in s for s in result['faults']))

    def test_source_manifest_cannot_omit_source_file_from_freeze(self):
        fx = self.fixture()
        path = fx.base / 'FREEZE.json'; value = json.loads(path.read_text())
        del value['sha256']['source.txt']; save(path, value); fx.campaign()
        result = fx.analyze(); self.assertFalse(result['data_complete_valid'])
        self.assertTrue(any('source/license file missing from freeze' in s for s in result['faults']))

    def test_claimed_skipped_stage_and_extra_stage_are_rejected(self):
        fx = self.fixture(); (fx.capture / 'confirmation').mkdir()
        result = fx.analyze(); self.assertFalse(result['data_complete_valid'])
        self.assertTrue(any('unexpected stage' in s for s in result['faults']))


class CollectorTests(unittest.TestCase):
    def test_one_stage_no_retry_on_failed_gate(self):
        calls = []
        def run():
            calls.append('qualification'); return dict(status='completed', gate_passed=False)
        result = collect.run_gate(run)
        self.assertEqual(calls, ['qualification']); self.assertFalse(result['qualified'])

    def test_infrastructure_abort_is_not_quality_fallback(self):
        def run():
            raise RuntimeError('host gate')
        with self.assertRaisesRegex(RuntimeError, 'host gate'):
            collect.run_gate(run)

    def run_mocked(self, parent, fail_postflight=False):
        jobs = cases(); calls = []; hosts = []
        class Server:
            def __init__(self, path, config):
                (path / 'SERVER.log').write_text('n_seq_max = 1\n')
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def verify_loaded(self): pass
            def stop_owned(self): raise AssertionError('watchdog should not fire')
            def check_host(self, phase):
                hosts.append(phase)
                if fail_postflight and phase == 'after_c0': raise RuntimeError('power failed')
        def trace(url, offered, model, options, **kwargs):
            job = offered[0]; calls.append(job['request_id'])
            value = raw(job['request_id'], '{"verdict":"insufficient","evidence":[]}',
                        1000*10**9+len(calls)*3*10**9, job['prompt'], options, job['max_output_tokens'])
            kwargs['checkpoint'](value); return value
        config = dict(model=audit.MODEL, context=4096, options=dict(num_ctx=4096, num_predict=256, temperature=0, seed=0))
        with patch.object(collect, 'OwnedServer', Server), patch.object(collect, 'run_trace', trace), \
             patch.object(collect.time, 'sleep'), patch.object(collect, 'bridge_diagnostics', return_value={'valid': True}):
            if fail_postflight:
                with self.assertRaisesRegex(RuntimeError, 'power failed'):
                    collect.stage(config, jobs, parent / 'qualification', float('inf'))
                result = json.loads((parent / 'qualification/STAGE.json').read_text())
            else:
                result = collect.stage(config, jobs, parent / 'qualification', float('inf'))
        return calls, hosts, result

    def test_all_24_collected_even_when_first_semantic_result_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            calls, hosts, result = self.run_mocked(Path(directory))
        self.assertEqual(calls, ['warm']+[j['request_id'] for j in cases()])
        self.assertEqual(hosts, [p+j['request_id'] for j in cases() for p in ('before_', 'after_')])
        self.assertEqual(result['status'], 'completed'); self.assertFalse(result['gate_passed'])
        self.assertEqual(len(result['requests']), 24)

    def test_postflight_abort_retains_raw_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory); calls, hosts, result = self.run_mocked(parent, True)
            self.assertTrue((parent / 'qualification/c0.json').is_file())
        self.assertEqual(calls, ['warm', 'c0']); self.assertEqual(result['status'], 'aborted')
        self.assertEqual(result['requests'], []); self.assertFalse(result['gate_passed'])


if __name__ == '__main__':
    unittest.main()
