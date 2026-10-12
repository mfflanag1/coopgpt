"""Mocked collection regressions: no model, network, or live hardware calls."""
import copy
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import collect


def stamp(ns):
    return dict(monotonic_before_ns=ns, monotonic_after_ns=ns+100, wall_ns=ns+10**15+50)


def raw(job, text, ns, options, prompt_count=100, output_count=20):
    cap = job['max_output_tokens']
    final = dict(model=collect.MODEL, done=True, response='', prompt_eval_count=prompt_count,
                 eval_count=output_count, total_duration=700000000, load_duration=1000,
                 prompt_eval_duration=200000000, eval_duration=499999000, done_reason='stop')
    split = len(text)//2
    row = dict(request_id=job['request_id'], arrival_offset_s=0, dispatch_offset_s=.01,
               first_content_offset_s=.1, terminal_offset_s=.8, http_status=200, completed=True,
               error=None, deadline_exceeded=False, request_prompt=job['prompt'], request_model=collect.MODEL,
               request_options=dict(options, num_predict=cap), request_format=job['format'], request_think=False,
               chunks=[dict(offset_s=.1, data=dict(response=text[:split], done=False, model=collect.MODEL)),
                       dict(offset_s=.2, data=dict(response=text[split:], done=False, model=collect.MODEL)),
                       dict(offset_s=.8, data=copy.deepcopy(final))], final=final)
    start, end = stamp(ns), stamp(ns+10**9)
    return dict(started_stamp=start, finished_stamp=end, epoch_monotonic_ns=start['monotonic_after_ns'],
                elapsed_seconds=(end['monotonic_before_ns']-start['monotonic_after_ns'])/10**9, requests=[row])


def assignments():
    cases = [dict(request_id='case'+str(i)) for i in range(24)]
    controls = [dict(request_id='c_control'+str(i), case_id=cases[(i//2)*2]['request_id'],
                     candidate={'verdict': 'insufficient', 'evidence': []},
                     expected_accept=i % 2 == 0, pair_id='pair'+str(i//2), error_group='synthetic')
                for i in range(24)]
    return cases, controls


def ordered_ids(cases):
    return sorted((case['request_id'] for case in cases),
                  key=lambda identifier: hashlib.sha256(('order:'+identifier).encode()).hexdigest())


def wire(identifier, prompt, cap, schema):
    return dict(request_id=identifier, arrival_offset_s=0, prompt=prompt,
                max_output_tokens=cap, format=schema, think=False)


class Harness:
    def __init__(self, root, abort_after=None, fault_id=None, inventory_prompt_count=100,
                 inventory_output_count=20, primary_output_count=20, warm_output_count=20,
                 thinking_id=None, incomplete_id=None, watchdog_id=None):
        self.root = root
        self.calls = []; self.hosts = []; self.built = []; self.timers = []
        self.instances = self.exits = self.stops = self.verifies = 0
        self.ns = 1000*10**9
        self.cases, self.controls = assignments()
        self.config = dict(model=collect.MODEL, digest=collect.DIGEST, context=4096, budget_s=1800,
                           request_timeout_s=90, max_output_tokens=256, think=False,
                           options=dict(num_ctx=4096, num_predict=256, temperature=0, seed=0))
        self.abort_after = abort_after
        self.fault_id = fault_id
        self.inventory_prompt_count = inventory_prompt_count
        self.inventory_output_count = inventory_output_count
        self.primary_output_count = primary_output_count
        self.warm_output_count = warm_output_count
        self.thinking_id = thinking_id
        self.incomplete_id = incomplete_id
        self.watchdog_id = watchdog_id

    def now(self):
        self.ns += 1000
        return stamp(self.ns)

    def primary(self, case):
        if self.calls: raise AssertionError('job constructed after inference began')
        self.built.append(('primary', case['request_id']))
        return wire('p_'+case['request_id'], 'primary '+case['request_id'], 256, collect.SCHEMA)

    def inventory(self, case):
        if self.calls: raise AssertionError('job constructed after inference began')
        self.built.append(('inventory', case['request_id']))
        return wire('i_'+case['request_id'], 'inventory '+case['request_id'], 384, collect.INVENTORY_SCHEMA)

    def trace(self, endpoint, jobs, model, options, **kwargs):
        if endpoint != 'http://127.0.0.1:11562': raise AssertionError('wrong endpoint')
        if len(jobs) != 1: raise AssertionError('nonserial batch')
        if model != collect.MODEL: raise AssertionError('wrong model')
        job = jobs[0]; self.calls.append(copy.deepcopy(job))
        identifier = job['request_id']
        if identifier == 'warm':
            if kwargs['timeout_s'] != 60 or kwargs['hard_timeout_s'] != 65: raise AssertionError('warm limits')
            text = '{"verdict":"insufficient","evidence":[]}'
            output_count = self.warm_output_count
        else:
            if kwargs['timeout_s'] != 90 or kwargs['hard_timeout_s'] != 95: raise AssertionError('trial limits')
            # Semantically invalid responses must not alter admission or later prompts.
            text = '  malformed response '+identifier+'\n'
            output_count = self.inventory_output_count if identifier.startswith('i_') else self.primary_output_count
        value = raw(job, text, self.ns+1000, options,
                    prompt_count=self.inventory_prompt_count if identifier.startswith('i_') else 100,
                    output_count=output_count)
        self.ns += 2*10**9
        if identifier == self.thinking_id: value['requests'][0]['chunks'][0]['data']['thinking'] = 'hidden'
        if identifier == self.incomplete_id: value['requests'][0]['completed'] = False
        kwargs['checkpoint'](value)
        if identifier == self.watchdog_id: self.timers[-1].callback()
        if identifier == self.fault_id: raise RuntimeError('collector fault after checkpoint')
        return value

    def patches(self):
        outer = self
        class Server:
            def __init__(self, path, config):
                outer.instances += 1
                (path / 'SERVER.log').write_text('n_seq_max = 1\n')
            def __enter__(self): return self
            def __exit__(self, *args): outer.exits += 1; return False
            def verify_loaded(self): outer.verifies += 1
            def stop_owned(self): outer.stops += 1
            def check_host(self, phase):
                outer.hosts.append(phase)
                if phase == outer.abort_after: raise RuntimeError('host gate failed')
        class Timer:
            def __init__(self, seconds, callback):
                if seconds != 100: raise AssertionError('wrong watchdog limit')
                self.callback = callback
                self.started = self.cancelled = self.joined = False
                outer.timers.append(self)
            def start(self): self.started = True
            def cancel(self): self.cancelled = True
            def join(self): self.joined = True
        return [patch.object(collect, 'OwnedServer', Server), patch.object(collect, 'run_trace', self.trace),
                patch.object(collect, 'primary_job', self.primary), patch.object(collect, 'inventory_job', self.inventory),
                patch.object(collect.threading, 'Timer', Timer), patch.object(collect, 'paired_stamp', self.now),
                patch.object(collect.time, 'sleep'), patch('builtins.print')]

    def run(self, deadline=float('inf')):
        with ExitStack() as stack:
            for item in self.patches(): stack.enter_context(item)
            return collect.stage(self.config, self.cases, self.controls, self.root/'collection', deadline)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_single_server_blind_inventory_then_primary_in_same_hash_order(self):
        harness = Harness(self.root); result = harness.run()
        ordered = ordered_ids(harness.cases)
        ids = ['warm']+['i_'+identifier for identifier in ordered]+['p_'+identifier for identifier in ordered]
        self.assertEqual([job['request_id'] for job in harness.calls], ids)
        self.assertEqual([entry['request_id'] for entry in result['requests']], ids[1:])
        self.assertEqual(harness.instances, 1); self.assertEqual(harness.exits, 1)
        self.assertEqual(harness.verifies, 2); self.assertEqual(harness.stops, 0)
        self.assertEqual(harness.hosts, [prefix+identifier for identifier in ids[1:] for prefix in ('before_', 'after_')])
        self.assertEqual(result['status'], 'completed'); self.assertEqual(result['completed_requests'], 48)
        self.assertEqual(len(result['clock_stamps']), 4*48+2)
        self.assertTrue(result['clock_diagnostics']['valid'])
        self.assertEqual([row['phase'] for row in result['requests']], ['inventory']*24+['primary']*24)
        self.assertEqual([row['case_id'] for row in result['requests']], ordered*2)
        self.assertTrue(all(timer.started and timer.cancelled and timer.joined for timer in harness.timers))
        self.assertEqual(len(harness.timers), 48)
        self.assertFalse(any(key in result for key in ('qualified', 'quality_count', 'gate_passed')))

    def test_inputs_prebuilt_and_controls_never_sent_despite_malformed_answers(self):
        harness = Harness(self.root)
        for control in harness.controls: control['candidate'] = 'CONTROL PROPOSAL SENTINEL'
        harness.run()
        ordered = ordered_ids(harness.cases)
        self.assertEqual(harness.built, [(phase, identifier) for phase in ('inventory', 'primary') for identifier in ordered])
        for job in harness.calls:
            self.assertNotIn('CONTROL PROPOSAL SENTINEL', job['prompt'])
            self.assertNotIn('malformed response', job['prompt'])
        for job in harness.calls[1:]:
            captured = json.loads((self.root/'collection'/(job['request_id']+'.json')).read_text())
            exact = ''.join(chunk['data'].get('response', '') for chunk in captured['requests'][0]['chunks'])
            self.assertEqual(exact, '  malformed response '+job['request_id']+'\n')

    def test_actual_factories_exclude_gold_and_inventory_excludes_combined_claim(self):
        cases, _ = assignments()
        for case in cases:
            case.update(claim='COMBINED_CLAIM_SENTINEL', label='GOLD_SENTINEL',
                        acceptable_evidence=[['GOLD_SENTINEL']], relevant_evidence=['GOLD_SENTINEL'],
                        passages=[{'id': 'D1', 'text': 'Synthetic document.'}],
                        components=[{'id': 'a1', 'claim': 'First component.'},
                                    {'id': 'a2', 'claim': 'Second component.'}])
        jobs = collect.planned_jobs(cases)
        self.assertEqual(len(jobs), 48)
        for job, phase, _ in jobs:
            self.assertNotIn('GOLD_SENTINEL', job['prompt'])
            if phase == 'inventory':
                self.assertNotIn('COMBINED_CLAIM_SENTINEL', job['prompt'])
                self.assertIn('[a1] First component.', job['prompt'])
                self.assertIn('[a2] Second component.', job['prompt'])
            else:
                self.assertIn('COMBINED_CLAIM_SENTINEL', job['prompt'])

    def test_inventory_cap_and_context_margin_use_384(self):
        harness = Harness(self.root, inventory_prompt_count=3584); result = harness.run()
        self.assertEqual([job['max_output_tokens'] for job in harness.calls], [32]+[384]*24+[256]*24)
        self.assertEqual(harness.calls[0]['prompt'], collect.WARM_PROMPT)
        self.assertEqual(harness.calls[0]['format'], collect.SCHEMA)
        self.assertEqual({row['observed_context_margin'] for row in result['requests'][:24]}, {128})

    def test_inventory_context_margin_below_128_aborts_without_primary(self):
        harness = Harness(self.root, inventory_prompt_count=3585)
        with self.assertRaisesRegex(RuntimeError, 'context allowance'): harness.run()
        self.assertEqual(len(harness.calls), 2)
        self.assertEqual(harness.exits, 1)

    def test_inventory_output_above_384_aborts(self):
        harness = Harness(self.root, inventory_output_count=385)
        with self.assertRaisesRegex(RuntimeError, 'exceeds request token cap'): harness.run()
        self.assertEqual(len(harness.calls), 2)
        result = json.loads((self.root/'collection/STAGE.json').read_text())
        self.assertEqual(result['status'], 'aborted'); self.assertEqual(len(result['requests']), 1)
        self.assertTrue((self.root/'collection'/(harness.calls[-1]['request_id']+'.json')).exists())

    def test_primary_output_above_256_aborts_even_below_inventory_cap(self):
        harness = Harness(self.root, primary_output_count=257)
        with self.assertRaisesRegex(RuntimeError, 'exceeds request token cap'): harness.run()
        self.assertEqual(len(harness.calls), 26)
        self.assertTrue(harness.calls[-1]['request_id'].startswith('p_'))
        self.assertEqual(harness.exits, 1)

    def test_warmup_output_above_32_aborts_before_scored_calls(self):
        harness = Harness(self.root, warm_output_count=33)
        with self.assertRaisesRegex(RuntimeError, 'Warmup output/context cap'): harness.run()
        self.assertEqual([job['request_id'] for job in harness.calls], ['warm'])
        self.assertEqual(harness.hosts, []); self.assertEqual(harness.exits, 1)

    def test_postflight_abort_preserves_orphan_without_retry(self):
        harness = Harness(self.root)
        first = 'i_'+ordered_ids(harness.cases)[0]
        harness.abort_after = 'after_'+first
        with self.assertRaisesRegex(RuntimeError, 'host gate failed'): harness.run()
        self.assertEqual([job['request_id'] for job in harness.calls], ['warm', first])
        self.assertTrue((self.root/'collection'/(first+'.json')).exists())
        result = json.loads((self.root/'collection/STAGE.json').read_text())
        self.assertEqual(result['status'], 'aborted'); self.assertEqual(result['requests'], [])
        self.assertEqual(harness.exits, 1)

    def test_collector_exception_preserves_checkpoint_and_cleans_watchdog(self):
        harness = Harness(self.root)
        first = 'i_'+ordered_ids(harness.cases)[0]; harness.fault_id = first
        with self.assertRaisesRegex(RuntimeError, 'collector fault after checkpoint'): harness.run()
        self.assertEqual(len(harness.calls), 2)
        self.assertTrue((self.root/'collection'/(first+'.json')).exists())
        self.assertEqual(json.loads((self.root/'collection/STAGE.json').read_text())['status'], 'aborted')
        self.assertTrue(harness.timers[0].cancelled and harness.timers[0].joined)
        self.assertEqual(harness.exits, 1)

    def test_watchdog_stops_only_owned_server_and_aborts(self):
        harness = Harness(self.root)
        harness.watchdog_id = 'i_'+ordered_ids(harness.cases)[0]
        with self.assertRaisesRegex(RuntimeError, 'watchdog fired'): harness.run()
        self.assertEqual(len(harness.calls), 2)
        self.assertEqual(harness.stops, 1); self.assertEqual(harness.exits, 1)

    def test_thinking_and_incomplete_transport_abort_without_retry(self):
        for parameter in ('thinking_id', 'incomplete_id'):
            with self.subTest(parameter=parameter), tempfile.TemporaryDirectory() as directory:
                harness = Harness(Path(directory))
                setattr(harness, parameter, 'i_'+ordered_ids(harness.cases)[0])
                with self.assertRaisesRegex(RuntimeError, 'Transport or non-thinking'): harness.run()
                self.assertEqual(len(harness.calls), 2); self.assertEqual(harness.exits, 1)

    def test_non_thinking_schema_and_wire_cap_are_not_coerced(self):
        self.assertTrue(collect.no_thinking({'chunks': [{'data': {'thinking': ''}}]}))
        self.assertFalse(collect.no_thinking({'chunks': [{'data': {'thinking': 'hidden'}}]}))
        for change in ({'think': 0}, {'max_output_tokens': 384.0}, {'max_output_tokens': 256},
                       {'request_id': '../bad'}, {'format': {'wrong_schema': True}}):
            job = wire('i_case', 'x', 384, collect.INVENTORY_SCHEMA); job.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                collect.checked_wire(job, 'i_case', 384, collect.INVENTORY_SCHEMA)

    def test_budget_gate_prevents_server_start(self):
        harness = Harness(self.root)
        with patch.object(collect, 'OwnedServer') as owned:
            with self.assertRaisesRegex(RuntimeError, 'budget stopped before stage setup'):
                collect.stage(harness.config, harness.cases, harness.controls, self.root/'collection', -1)
        owned.assert_not_called()

    def test_budget_reserve_stops_before_first_scored_request(self):
        harness = Harness(self.root)
        with patch.object(collect.time, 'monotonic', side_effect=[0, 1501]):
            with self.assertRaisesRegex(RuntimeError, 'budget stopped before next request'):
                harness.run(deadline=1800)
        self.assertEqual([job['request_id'] for job in harness.calls], ['warm'])
        self.assertEqual(harness.hosts, []); self.assertEqual(harness.exits, 1)

    def test_all_wire_jobs_validate_before_host_start(self):
        harness = Harness(self.root)
        with ExitStack() as stack:
            for item in harness.patches(): stack.enter_context(item)
            stack.enter_context(patch.object(collect, 'primary_job', return_value=wire('p_case', 'x', 384, collect.SCHEMA)))
            with self.assertRaisesRegex(ValueError, 'Wire job'):
                collect.stage(harness.config, harness.cases, harness.controls, self.root/'collection', float('inf'))
        self.assertEqual(harness.instances, 0); self.assertEqual(harness.calls, [])

    def main_patches(self, harness, **stage_kwargs):
        (self.root/'CONFIG.json').write_text(json.dumps(harness.config))
        return [patch.object(collect, 'BASE', self.root), patch.object(collect, 'check_freeze', return_value='frozen'),
                patch.object(collect, 'validate_inputs', return_value=(harness.cases, harness.controls)),
                patch.object(collect, 'stage', **stage_kwargs)]

    def test_main_uses_one_stage_without_qualification_claim(self):
        harness = Harness(self.root); output = self.root/'capture'
        stage = dict(status='completed', completed_requests=48)
        with ExitStack() as stack:
            mocks = [stack.enter_context(item) for item in self.main_patches(harness, return_value=stage)]
            result = collect.main(output)
        mocks[-1].assert_called_once()
        self.assertEqual(result['scored_requests'], 48); self.assertEqual(result['stages'], [stage])
        self.assertEqual(result['planned_requests'], 48); self.assertNotIn('qualified', result)
        self.assertEqual(json.loads((output/'CAMPAIGN.json').read_text())['status'], 'completed')

    def test_main_abort_has_no_completion_or_retry(self):
        harness = Harness(self.root); output = self.root/'capture'
        with ExitStack() as stack:
            mocks = [stack.enter_context(item) for item in self.main_patches(harness, side_effect=RuntimeError('failed'))]
            with self.assertRaisesRegex(RuntimeError, 'failed'): collect.main(output)
        mocks[-1].assert_called_once()
        result = json.loads((output/'CAMPAIGN.json').read_text())
        self.assertEqual(result['status'], 'aborted'); self.assertNotIn('scored_requests', result)

    def test_main_rejects_duplicate_controls_bad_pairs_and_wrong_config_before_host(self):
        for mode in ('duplicate_control', 'bad_pairs', 'bad_config', 'duplicate_case'):
            with self.subTest(mode=mode):
                harness = Harness(self.root)
                if mode == 'duplicate_control': harness.controls[1]['request_id'] = harness.controls[0]['request_id']
                if mode == 'bad_pairs': harness.controls[0]['pair_id'] = 'extra_pair'
                if mode == 'bad_config': harness.config['context'] = 8192
                if mode == 'duplicate_case': harness.cases[1]['request_id'] = harness.cases[0]['request_id']
                with ExitStack() as stack:
                    mocks = [stack.enter_context(item) for item in self.main_patches(harness)]
                    with self.assertRaises(ValueError): collect.main(self.root/'capture')
                mocks[-1].assert_not_called()
                self.assertFalse((self.root/'capture').exists())

    def test_freeze_binds_controls_and_source_files(self):
        names = ('CONFIG.json', 'MODEL_LOCK.json', 'MODEL_MANIFEST.json', 'cases.json', 'controls.json',
                 'contract.py', 'collect.py', 'audit_runtime.py', 'transport_audit.py', 'client.py',
                 'server_control.py', 'clock_bridge.py', 'PROTOCOL.txt', 'PRIOR_CLAIMS.json', 'source.txt', 'license.txt')
        for name in names: (self.root/name).write_text('synthetic '+name)
        manifest = [dict(source_file='source.txt', license_file='license.txt',
                        sha256=hashlib.sha256((self.root/'source.txt').read_bytes()).hexdigest(),
                        license_sha256=hashlib.sha256((self.root/'license.txt').read_bytes()).hexdigest())]
        (self.root/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest))
        def freeze():
            data = {'sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in self.root.iterdir() if path.name != 'FREEZE.json'}}
            (self.root/'FREEZE.json').write_text(json.dumps(data)); return data
        freeze()
        with patch.object(collect, 'BASE', self.root):
            self.assertEqual(len(collect.check_freeze()), 64)
            (self.root/'controls.json').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'controls.json'): collect.check_freeze()
            data = freeze(); del data['sha256']['source.txt']
            (self.root/'FREEZE.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'Source/license missing'): collect.check_freeze()
            data = freeze(); del data['sha256']['contract.py']
            (self.root/'FREEZE.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'missing required'): collect.check_freeze()


if __name__ == '__main__':
    unittest.main()
