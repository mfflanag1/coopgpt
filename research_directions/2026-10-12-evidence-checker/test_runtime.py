"""Mocked collection regressions: no model, network, or live hardware calls."""
import copy
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
    controls = [dict(request_id='c_control'+str(i), case_id=c['request_id'],
                     candidate={'verdict': 'insufficient', 'evidence': []},
                     expected_accept=i % 2 == 0, pair_id='pair'+str(i//2), error_group='synthetic')
                for i, c in enumerate(cases)]
    return cases, controls


def wire(identifier, prompt, cap, schema):
    return dict(request_id=identifier, arrival_offset_s=0, prompt=prompt,
                max_output_tokens=cap, format=schema, think=False)


class Harness:
    def __init__(self, root, abort_after=None, output_count=20, checker_prompt_count=100, fault_id=None):
        self.root = root
        self.calls = []; self.hosts = []; self.proposals = {}; self.instances = 0; self.exits = 0
        self.cases, self.controls = assignments()
        self.config = dict(model=collect.MODEL, digest=collect.DIGEST, context=4096, budget_s=1800,
                           request_timeout_s=90, max_output_tokens=256, think=False,
                           options=dict(num_ctx=4096, num_predict=256, temperature=0, seed=0))
        self.abort_after = abort_after
        self.output_count = output_count
        self.checker_prompt_count = checker_prompt_count
        self.fault_id = fault_id

    def primary(self, case):
        return wire('p_'+case['request_id'], 'primary '+case['request_id'], 256, {'type': 'object'})

    def checker(self, case, proposal, request_id):
        self.proposals[request_id] = proposal
        return wire(request_id, 'checker '+case['request_id']+'\n'+proposal, 64, collect.CHECK_SCHEMA)

    def trace(self, endpoint, jobs, model, options, **kwargs):
        if endpoint != 'http://127.0.0.1:11562': raise AssertionError('wrong endpoint')
        if len(jobs) != 1: raise AssertionError('nonserial batch')
        job = jobs[0]; self.calls.append(copy.deepcopy(job))
        identifier = job['request_id']
        if identifier == 'warm':
            if kwargs['timeout_s'] != 60 or kwargs['hard_timeout_s'] != 65: raise AssertionError('warm limits')
            text = '{"accept":false}'
        else:
            if kwargs['timeout_s'] != 90 or kwargs['hard_timeout_s'] != 95: raise AssertionError('trial limits')
            text = '  malformed proposal '+identifier+'\n' if identifier.startswith('p_') else '{"accept":false}'
        value = raw(job, text, 1000*10**9+len(self.calls)*3*10**9, options,
                    prompt_count=self.checker_prompt_count if job['max_output_tokens'] == 64 else 100,
                    output_count=self.output_count if job['max_output_tokens'] == 64 else 20)
        kwargs['checkpoint'](value)
        if identifier == self.fault_id:
            raise RuntimeError('collector fault after checkpoint')
        return value

    def patches(self):
        outer = self
        class Server:
            def __init__(self, path, config):
                outer.instances += 1
                (path / 'SERVER.log').write_text('n_seq_max = 1\n')
            def __enter__(self): return self
            def __exit__(self, *args): outer.exits += 1; return False
            def verify_loaded(self): pass
            def stop_owned(self): raise AssertionError('watchdog should not fire')
            def check_host(self, phase):
                outer.hosts.append(phase)
                if phase == outer.abort_after: raise RuntimeError('host gate failed')
        return [patch.object(collect, 'OwnedServer', Server), patch.object(collect, 'run_trace', self.trace),
                patch.object(collect, 'primary_job', self.primary), patch.object(collect, 'checker_job', self.checker),
                patch.object(collect.time, 'sleep'), patch.object(collect, 'bridge_diagnostics', return_value={'valid': True}),
                patch('builtins.print')]

    def run(self):
        from contextlib import ExitStack
        with ExitStack() as stack:
            for item in self.patches(): stack.enter_context(item)
            return collect.stage(self.config, self.cases, self.controls, self.root/'collection', float('inf'))


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_single_server_all_24_primaries_before_sorted_48_checkers(self):
        harness = Harness(self.root); result = harness.run()
        cases, controls = assignments()
        expected_checkers = sorted(['n_'+c['request_id'] for c in cases]+[c['request_id'] for c in controls],
                                  key=lambda x: hashlib.sha256(('checker-order:'+x).encode()).hexdigest())
        ids = ['warm']+['p_'+c['request_id'] for c in cases]+expected_checkers
        self.assertEqual([c['request_id'] for c in harness.calls], ids)
        self.assertEqual(harness.instances, 1); self.assertEqual(harness.exits, 1)
        self.assertEqual(harness.hosts, [p+identifier for identifier in ids[1:] for p in ('before_', 'after_')])
        self.assertEqual(result['status'], 'completed'); self.assertEqual(len(result['requests']), 72)
        self.assertEqual(len(result['clock_stamps']), 4*72+2)
        self.assertEqual([r['phase'] for r in result['requests']], ['primary']*24+['checker']*48)
        self.assertFalse(any(k in result for k in ('qualified', 'quality_count', 'gate_passed')))

    def test_native_preserves_exact_raw_response_and_controls_use_compact_sorted_json(self):
        harness = Harness(self.root); harness.run()
        for case in harness.cases:
            self.assertEqual(harness.proposals['n_'+case['request_id']], '  malformed proposal p_'+case['request_id']+'\n')
        for control in harness.controls:
            self.assertEqual(harness.proposals[control['request_id']], '{"evidence":[],"verdict":"insufficient"}')
        self.assertEqual(set(harness.proposals), {'n_'+c['request_id'] for c in harness.cases}|{c['request_id'] for c in harness.controls})

    def test_checker_caps_are_64_and_context_allowance_uses_64_not_256(self):
        harness = Harness(self.root, checker_prompt_count=3900); result = harness.run()
        self.assertEqual([j['max_output_tokens'] for j in harness.calls], [32]+[256]*24+[64]*48)
        checkers = [r for r in result['requests'] if r['phase'] == 'checker']
        self.assertEqual({r['observed_context_margin'] for r in checkers}, {132})

    def test_checker_output_above_64_aborts_even_below_primary_cap(self):
        harness = Harness(self.root, output_count=65)
        with self.assertRaisesRegex(RuntimeError, 'exceeds request token cap'): harness.run()
        self.assertEqual(len(harness.calls), 26)
        result = json.loads((self.root/'collection/STAGE.json').read_text())
        self.assertEqual(result['status'], 'aborted'); self.assertEqual(len(result['requests']), 25)
        self.assertTrue((self.root/'collection'/(harness.calls[-1]['request_id']+'.json')).exists())

    def test_postflight_abort_preserves_orphan_and_does_not_build_checkers(self):
        harness = Harness(self.root, abort_after='after_p_case0')
        with self.assertRaisesRegex(RuntimeError, 'host gate failed'): harness.run()
        self.assertEqual([j['request_id'] for j in harness.calls], ['warm', 'p_case0'])
        self.assertEqual(harness.proposals, {})
        self.assertTrue((self.root/'collection/p_case0.json').exists())
        result = json.loads((self.root/'collection/STAGE.json').read_text())
        self.assertEqual(result['status'], 'aborted'); self.assertEqual(result['requests'], [])
        self.assertEqual(harness.exits, 1)

    def test_collector_exception_preserves_checkpoint_without_retry(self):
        harness = Harness(self.root, fault_id='p_case0')
        with self.assertRaisesRegex(RuntimeError, 'collector fault after checkpoint'): harness.run()
        self.assertEqual(len(harness.calls), 2)
        self.assertTrue((self.root/'collection/p_case0.json').exists())
        self.assertEqual(json.loads((self.root/'collection/STAGE.json').read_text())['status'], 'aborted')

    def test_non_thinking_contract_and_wire_cap_are_not_coerced(self):
        self.assertTrue(collect.no_thinking({'chunks': [{'data': {'thinking': ''}}]}))
        self.assertFalse(collect.no_thinking({'chunks': [{'data': {'thinking': 'hidden'}}]}))
        for change in ({'think': 0}, {'max_output_tokens': 64.0}, {'request_id': '../bad'}):
            job = wire('n_case', 'x', 64, collect.CHECK_SCHEMA); job.update(change)
            with self.assertRaises(ValueError): collect.checked_wire(job, 'n_case', 64)

    def test_budget_gate_prevents_server_start(self):
        harness = Harness(self.root)
        with patch.object(collect, 'OwnedServer') as owned:
            with self.assertRaisesRegex(RuntimeError, 'budget stopped before stage setup'):
                collect.stage(harness.config, harness.cases, harness.controls, self.root/'collection', -1)
        owned.assert_not_called()

    def test_main_uses_one_stage_without_qualification_claim(self):
        harness = Harness(self.root)
        (self.root/'CONFIG.json').write_text(json.dumps(harness.config))
        output = self.root/'capture'
        stage = dict(status='completed', completed_requests=72)
        with patch.object(collect, 'BASE', self.root), patch.object(collect, 'check_freeze', return_value='frozen'), \
             patch.object(collect, 'validate_inputs', return_value=(harness.cases, harness.controls)), \
             patch.object(collect, 'stage', return_value=stage) as called:
            result = collect.main(output)
        called.assert_called_once()
        self.assertEqual(result['scored_requests'], 72); self.assertEqual(result['stages'], [stage])
        self.assertNotIn('qualified', result)
        self.assertEqual(json.loads((output/'CAMPAIGN.json').read_text())['status'], 'completed')

    def test_main_abort_has_no_completion_or_retry(self):
        harness = Harness(self.root)
        (self.root/'CONFIG.json').write_text(json.dumps(harness.config))
        output = self.root/'capture'
        with patch.object(collect, 'BASE', self.root), patch.object(collect, 'check_freeze', return_value='frozen'), \
             patch.object(collect, 'validate_inputs', return_value=(harness.cases, harness.controls)), \
             patch.object(collect, 'stage', side_effect=RuntimeError('failed')) as called:
            with self.assertRaisesRegex(RuntimeError, 'failed'): collect.main(output)
        called.assert_called_once()
        result = json.loads((output/'CAMPAIGN.json').read_text())
        self.assertEqual(result['status'], 'aborted'); self.assertNotIn('scored_requests', result)

    def test_main_rejects_duplicate_control_identifiers_before_host(self):
        harness = Harness(self.root); harness.controls[1]['request_id'] = harness.controls[0]['request_id']
        (self.root/'CONFIG.json').write_text(json.dumps(harness.config))
        with patch.object(collect, 'BASE', self.root), patch.object(collect, 'check_freeze', return_value='frozen'), \
             patch.object(collect, 'validate_inputs', return_value=(harness.cases, harness.controls)), \
             patch.object(collect, 'stage') as called:
            with self.assertRaisesRegex(ValueError, 'distinct control'): collect.main(self.root/'capture')
        called.assert_not_called()

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
            data = {'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in self.root.iterdir() if p.name != 'FREEZE.json'}}
            (self.root/'FREEZE.json').write_text(json.dumps(data)); return data
        freeze()
        with patch.object(collect, 'BASE', self.root):
            self.assertEqual(len(collect.check_freeze()), 64)
            (self.root/'controls.json').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'controls.json'): collect.check_freeze()
            data = freeze(); del data['sha256']['source.txt']
            (self.root/'FREEZE.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'Source/license missing'): collect.check_freeze()


if __name__ == '__main__':
    unittest.main()
