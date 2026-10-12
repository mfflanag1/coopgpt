"""Synthetic saved-capture regressions; no network, model, or controller imports."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import analyze as audit

MANIFEST = ('{"schemaVersion":2,"mediaType":"application/vnd.docker.distribution.manifest.v2+json",'
            '"config":{"mediaType":"application/vnd.docker.container.image.v1+json","digest":"sha256:afdf5c7585b363536f93782f1e44f1b81db4237847cd8b4bd2c5c33b0d76c94b","size":488},'
            '"layers":[{"mediaType":"application/vnd.ollama.image.model","digest":"sha256:3291abe70f16ee9682de7bfae08db5373ea9d6497e614aaad63340ad421d6312","size":20201240160},'
            '{"mediaType":"application/vnd.ollama.image.template","digest":"sha256:ae370d884f108d16e7cc8fd5259ebc5773a0afa6e078b11f4ed7e39a27e0dfc4","size":1723},'
            '{"mediaType":"application/vnd.ollama.image.license","digest":"sha256:d18a5cc71b84bc4af394a31116bd3932b42241de70c77d2b76d69a314ec8aa12","size":11338},'
            '{"mediaType":"application/vnd.ollama.image.params","digest":"sha256:cff3f395ef3756ab63e58b0ad1b32bb6f802905cae1472e6a12034e4246fbbdb","size":120}]}')


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True)+'\n')


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


class Fixture:
    def __init__(self, root):
        self.base, self.capture = root/'source', root/'capture'
        self.base.mkdir();self.capture.mkdir();(self.base/'sources').mkdir()
        self.config = dict(model=audit.MODEL, digest=audit.DIGEST, context=4096, think=False,
                           options=dict(num_ctx=4096, num_predict=256, temperature=0, seed=0),
                           allow_battery_quality=True, server_settings_common={'OLLAMA_CONTEXT_LENGTH':'4096'},
                           lock=dict(binary_sha256='binary', manifest_sha256=audit.DIGEST))
        self.instruction = 'Answer with one JSON answer field using the passage.\n/no_think\n'
        self.jobs = {};articles = []
        for part, repeat in [('development', 2), ('confirmation', 6)]:
            jobs = [];paragraphs = []
            for band, size in [('short', 300), ('medium', 800), ('long', 1600)]:
                for impossible in (False, True):
                    for _ in range(repeat):
                        identifier = part+'-'+str(len(jobs)+1).zfill(3)
                        passage = ('Beryl passage '+identifier+'. ').ljust(size, 'x')
                        question = 'What token is in case '+identifier+'?'
                        answers = [] if impossible else [dict(text='Beryl', answer_start=0)]
                        jobs.append(dict(request_id=identifier, qid=identifier, title=part, passage=passage,
                                         question=question, answers=answers, is_impossible=impossible,
                                         length_band=band, passage_chars=len(passage),
                                         context_sha256=hashlib.sha256(passage.encode()).hexdigest(), max_output_tokens=256))
                        paragraphs.append(dict(context=passage, qas=[dict(id=identifier, question=question,
                                                                         answers=answers, is_impossible=impossible)]))
            self.jobs[part] = jobs;save(self.base/(part+'.json'), jobs)
            articles.append(dict(title=part, paragraphs=paragraphs))
        save(self.base/'sources/dev-v2.0.json', dict(data=articles))
        self.source_sha = hashlib.sha256((self.base/'sources/dev-v2.0.json').read_bytes()).hexdigest()
        manifest = json.loads(MANIFEST)
        lock = dict(self.config['lock'], verified_utc='2026-01-01T00:00:00+00:00',
                    blob_checks={item['digest']:dict(bytes=item['size'], verified=True)
                                 for item in [manifest['config']]+manifest['layers']})
        save(self.base/'CONFIG.json', self.config);save(self.base/'MODEL_LOCK.json', lock)
        (self.base/'MODEL_MANIFEST.json').write_text(MANIFEST)
        (self.base/'design.py').write_text('INSTRUCTION = '+repr(self.instruction)+'\nSCHEMA = '+repr(audit.SCHEMA)+'\n')
        for name in ('client.py','calibrate.py','server_control.py','clock_bridge.py','PROTOCOL.txt'):
            (self.base/name).write_text('synthetic source only\n')
        self.freeze();self.stage_names = []

    def freeze(self):
        save(self.base/'FREEZE.json', {'sha256':{str(p.relative_to(self.base)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in self.base.rglob('*') if p.is_file() and p.name != 'FREEZE.json'}})

    def prompt(self, job):
        return self.instruction+'Passage:\n'+job['passage']+'\nQuestion:\n'+job['question']+'\nJSON answer:'

    def stage(self, part, bad=(), invalid_schema=(), gate=True):
        path = self.capture/part;path.mkdir();jobs = self.jobs[part]
        seq = len(self.stage_names);self.stage_names.append(part)
        ns = (1000+seq*1000)*10**9;stamps = [stamp(ns)];entries = []
        for i, job in enumerate(jobs):
            t = ns+(3*i+1)*10**9
            answer = None if job['is_impossible'] else 'Beryl'
            if i in bad:answer = 'wrong'
            text = 'broken JSON' if i in invalid_schema else json.dumps(dict(answer=answer))
            data = raw(job['request_id'], text, t+10**8, self.prompt(job), self.config['options'])
            save(path/(job['request_id']+'.json'), data)
            stamps.extend([stamp(t), data['started_stamp'], data['finished_stamp'], stamp(t+2*10**9)])
            ok = i not in bad and i not in invalid_schema
            entries.append(dict(request_id=job['request_id'], title=job['title'], is_impossible=job['is_impossible'],
                                length_band=job['length_band'], passage_chars=len(job['passage']), api_completed=True,
                                schema_valid=i not in invalid_schema, exact_match=ok, f1=float(ok),
                                abstained=answer is None and i not in invalid_schema,
                                observed_context_margin=4096-100-256, output_tokens=30, done_reason='stop',
                                completion_s=.8, raw_file=job['request_id']+'.json'))
        stamps.append(stamp(ns+(3*len(jobs)+3)*10**9))
        stage = dict(part=part, candidate=audit.MODEL, planned=len(jobs), status='completed', requests=entries,
                     started_utc=f'2026-01-01T00:{seq*3:02d}:00+00:00', finished_utc=f'2026-01-01T00:{seq*3+1:02d}:00+00:00',
                     quality_count=sum(e['exact_match'] for e in entries), gate_passed=gate,
                     clock_stamps=stamps, clock_diagnostics=audit.clock_check(stamps))
        save(path/'STAGE.json', stage)
        save(path/'WARMUP.json', raw('warm','{"answer":"ready"}',ns-2*10**9,
                                   audit.WARM_PROMPT,self.config['options'],32))
        state = dict(power="Now drawing from 'Battery Power'\n -InternalBattery-0 (id=REDACTED) 80%; discharging;",
                     power_source='Battery Power', battery_percent=80, external_power_connected=False,
                     thermal='No thermal warning level has been recorded\nNo performance warning level has been recorded')
        loaded = dict(name=audit.MODEL, digest=audit.DIGEST, context_length=4096, size_vram=20000000000)
        meta = dict(status='completed', errors=[], clean_unload_verified=True, loaded_after_unload={'models':[]},
                    dedicated_server_returncode=0, model=audit.MODEL, context=4096, parallel=1, runtime_parallel_values=[1],
                    version={'version':'0.20.0'}, model_tag={'name':audit.MODEL,'digest':audit.DIGEST}, options=self.config['options'],
                    server_settings=dict(self.config['server_settings_common'], OLLAMA_NUM_PARALLEL='1'), allow_battery_quality=True,
                    lock_verification=self.config['lock'], dedicated_server_pid=12345, dedicated_process_group=12345,
                    loaded_checks=[{'response':{'models':[loaded]}} for _ in range(3)], before=state, after=state,
                    original_endpoint_idle_before=True, original_endpoint_idle_after=True,
                    host_checks=[dict(phase=prefix+j['request_id'], passed=True, original_endpoint_idle=True, state=state)
                                 for j in jobs for prefix in ('before_','after_')])
        save(path/'SERVER_CONTROL.json',meta);(path/'SERVER.log').write_text('n_seq_max = 1\n')
        return path

    def campaign(self, selected=audit.MODEL, qualified=True, status='completed'):
        save(self.capture/'CAMPAIGN.json', dict(status=status, selected=selected, qualified=qualified,
             source_freeze_sha256=hashlib.sha256((self.base/'FREEZE.json').read_bytes()).hexdigest(),
             stages=[json.loads((self.capture/name/'STAGE.json').read_text()) for name in self.stage_names]))

    def passing(self):
        self.stage('development');self.stage('confirmation');self.campaign()

    def change(self, relative, fn):
        path = self.capture/relative;value = json.loads(path.read_text());fn(value);save(path,value)

    def analyze(self):
        with patch.object(audit, 'SOURCE_SHA256', self.source_sha):
            return audit.analyze(self.base, self.capture)


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.pos = dict(answers=[{'text':'The Black Cat','answer_start':0}, {'text':'cat','answer_start':10}], is_impossible=False)
        self.neg = dict(answers=[], is_impossible=True)

    def test_official_normalization_and_multiple_golds(self):
        self.assertEqual(audit.normalize(' The U.S., plan! '), 'us plan')
        self.assertTrue(audit.score_output('{"answer":"CAT!"}',self.pos)['exact_match'])
        self.assertEqual(audit.score_output('{"answer":"black"}',self.pos)['f1'],2/3)

    def test_unanswerable_requires_literal_null_not_normalized_empty(self):
        self.assertTrue(audit.score_output('{"answer":null}',self.neg)['exact_match'])
        for answer in ('', 'the', '...', 'null'):
            result = audit.score_output(json.dumps(dict(answer=answer)),self.neg)
            self.assertTrue(result['schema_valid']);self.assertFalse(result['exact_match']);self.assertFalse(result['abstained'])
        self.assertEqual(audit.score_output('{"answer":"the"}',self.neg)['f1'],1)
        self.assertFalse(audit.score_output('{"answer":null}',self.pos)['exact_match'])

    def test_invalid_single_field_json(self):
        for text in ('null','[]','{"answer":1}','{"answer":false}','{"answer":"cat","extra":1}',
                     '{"answer":"cat","answer":"cat"}','{"answer":NaN}','{"answer":"cat"} trailing',
                     '```json\n{"answer":"cat"}\n```'):
            with self.subTest(text=text):
                self.assertFalse(audit.score_output(text,self.pos)['schema_valid'])
                self.assertFalse(audit.score_output(text,self.pos)['exact_match'])

    def test_deeply_nested_generated_json_is_schema_invalid(self):
        result = audit.score_output('{"answer":'+'['*10000+'0'+']'*10000+'}', self.pos)
        self.assertFalse(result['schema_valid'])
        self.assertFalse(result['exact_match'])

    def test_normalize_empty_annotation_is_not_an_answerable_gold(self):
        job = dict(answers=[{'text':'.','answer_start':0},{'text':'Beryl','answer_start':2}],is_impossible=False)
        self.assertFalse(audit.score_output('{"answer":""}',job)['exact_match'])
        self.assertTrue(audit.score_output('{"answer":"beryl"}',job)['exact_match'])


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.fx = Fixture(Path(self.tmp.name))

    def test_passing_complete_fixture(self):
        self.fx.passing();out=self.fx.analyze()
        self.assertTrue(out['qualified'],out['faults']);self.assertTrue(out['data_complete_valid'])
        self.assertEqual(out['counts']['all']['raw_offered'],48)
        self.assertEqual(out['counts']['confirmation']['exact_quality'],36)

    def test_extended_lock_accepts_required_hash_projection(self):
        self.fx.passing()
        lock = json.loads((self.fx.base/'MODEL_LOCK.json').read_text())
        self.assertEqual(len(lock['blob_checks']), 5)
        self.assertIn('verified_utc', lock)
        self.assertNotEqual(lock, self.fx.config['lock'])
        out = self.fx.analyze()
        self.assertTrue(out['qualified'], out['faults'])

    def test_saved_blob_verification_requires_every_digest_size_and_success(self):
        mutations = [lambda checks, key:checks.pop(key),
                     lambda checks, key:checks[key].update(bytes=1),
                     lambda checks, key:checks[key].update(verified=False),
                     lambda checks, key:checks.update({'sha256:'+'0'*64:checks[key]})]
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                fx = Fixture(Path(directory));fx.passing()
                path = fx.base/'MODEL_LOCK.json';lock = json.loads(path.read_text())
                mutation(lock['blob_checks'], next(iter(lock['blob_checks'])))
                save(path, lock);fx.freeze();fx.campaign()
                out = fx.analyze()
                self.assertFalse(out['qualified'])
                self.assertTrue(any('blob' in fault for fault in out['faults']))

    def test_development_failure_is_valid_terminal_no_fallback(self):
        self.fx.stage('development',bad=(0,1),gate=False);self.fx.campaign(None,False)
        out=self.fx.analyze();self.assertTrue(out['data_complete_valid'],out['faults']);self.assertFalse(out['qualified'])
        self.assertEqual(out['counts']['development']['exact_quality'],10)
        self.assertEqual(out['counts']['confirmation']['raw_offered'],0)

    def test_schema_failure_is_quality_failure_even_with_eleven_correct(self):
        self.fx.stage('development',invalid_schema=(0,),gate=False);self.fx.campaign(None,False)
        out=self.fx.analyze();self.assertTrue(out['data_complete_valid'],out['faults']);self.assertFalse(out['qualified'])
        self.assertEqual(out['stages'][0]['gate']['exact_correct'],11)
        self.assertEqual(out['stages'][0]['gate']['schema_valid'],11)

    def test_one_development_miss_still_promotes(self):
        self.fx.stage('development',bad=(0,));self.fx.stage('confirmation');self.fx.campaign()
        out=self.fx.analyze();self.assertTrue(out['qualified'],out['faults'])

    def test_confirmation_cross_cell_floor_rejects_34_with_good_margins(self):
        self.fx.stage('development');self.fx.stage('confirmation',bad=(0,1),gate=False);self.fx.campaign(qualified=False)
        out=self.fx.analyze();self.assertTrue(out['data_complete_valid'],out['faults']);self.assertFalse(out['qualified'])
        gate=out['stages'][1]['gate']
        self.assertEqual(gate['exact_correct'],34)
        self.assertGreaterEqual(min(gate['correct_by_label'].values()),16)
        self.assertGreaterEqual(min(gate['correct_by_length'].values()),10)
        self.assertEqual(gate['correct_by_cell']['short:answerable'],4)

    def test_confirmation_33_spread_misses_pass(self):
        self.fx.stage('development');self.fx.stage('confirmation',bad=(0,6,12));self.fx.campaign()
        out=self.fx.analyze();self.assertTrue(out['qualified'],out['faults'])

    def test_missing_confirmation_remains_required_and_unobserved(self):
        self.fx.stage('development');self.fx.campaign(qualified=False,status='aborted')
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertFalse(out['data_complete_valid'])
        self.assertEqual(out['missing_stages'],['confirmation']);self.assertEqual(out['required_planned'],48)
        self.assertEqual(out['counts']['confirmation']['raw_offered'],0)

    def test_wrong_raw_answer_cannot_be_overridden_by_summary(self):
        self.fx.passing()
        self.fx.change('confirmation/confirmation-001.json',lambda x:x['requests'][0]['chunks'][0]['data'].update(response='{"answer":"wrong"}'))
        out=self.fx.analyze();self.assertFalse(out['qualified'])
        self.assertEqual(out['counts']['confirmation']['exact_quality'],35)
        self.assertTrue(any('summary exact_match differs' in f for f in out['faults']))

    def test_missing_file_keeps_planned_denominator(self):
        self.fx.passing();(self.fx.capture/'confirmation/confirmation-001.json').unlink()
        out=self.fx.analyze();self.assertFalse(out['qualified'])
        self.assertEqual(out['counts']['all']['planned'],48);self.assertEqual(out['counts']['all']['raw_offered'],47)
        self.assertEqual(out['stages'][1]['missing_ids'],['confirmation-001'])

    def test_postflight_fault_preserves_orphan_raw(self):
        self.fx.stage('development')
        for job in self.fx.jobs['development'][1:]:
            (self.fx.capture/'development'/(job['request_id']+'.json')).unlink()
        self.fx.change('development/STAGE.json',lambda x:x.update(status='aborted',requests=[],gate_passed=False))
        self.fx.change('development/SERVER_CONTROL.json',lambda x:x.update(status='aborted',errors=[{'stage':'postflight'}]))
        self.fx.campaign(None,False,'aborted')
        out=self.fx.analyze();self.assertFalse(out['qualified'])
        self.assertEqual(out['counts']['development']['planned'],12)
        self.assertEqual(out['counts']['development']['raw_offered'],1)
        self.assertEqual(out['counts']['development']['exact_quality'],1)
        self.assertEqual(out['stages'][0]['orphan_raw_ids'],['development-001'])

    def test_failed_transport_and_checkpoint_retained(self):
        self.fx.passing()
        self.fx.change('development/development-001.json',lambda x:x['requests'][0].update(completed=False,error='timeout'))
        self.fx.change('development/development-002.json',lambda x:x.update(collection_incomplete=True))
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertEqual(out['counts']['all']['raw_offered'],48)
        self.assertEqual(out['counts']['all']['api_completed'],47)

    def test_thinking_or_wrong_wire_contract_blocks(self):
        mutations=[lambda row:row.update(request_think=True),lambda row:row.pop('request_think'),
                   lambda row:row.update(request_model='llama3.2:3b'),lambda row:row.update(request_format={}),
                   lambda row:row['request_options'].update(num_predict=512),
                   lambda row:row.update(request_prompt=row['request_prompt']+'\nGold answer: Beryl'),
                   lambda row:row['chunks'][0]['data'].update(thinking='hidden reasoning')]
        for mutation in mutations:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                fx=Fixture(Path(directory));fx.passing()
                fx.change('development/development-001.json',lambda x:mutation(x['requests'][0]))
                self.assertFalse(fx.analyze()['qualified'])

    def test_malformed_stream_terminal_usage_and_error_keys_block(self):
        mutations=[lambda row:row['chunks'][0]['data'].update(error=''),
                   lambda row:row['final'].update(eval_count=-1),
                   lambda row:row['chunks'][0]['data'].update(done=True),
                   lambda row:row.update(terminal_offset_s=.7),lambda row:row.update(http_status=500)]
        for mutation in mutations:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                fx=Fixture(Path(directory));fx.passing()
                fx.change('development/development-001.json',lambda x:mutation(x['requests'][0]))
                self.assertFalse(fx.analyze()['qualified'])

    def test_cleanup_and_low_battery_fail_closed(self):
        self.fx.passing()
        self.fx.change('development/SERVER_CONTROL.json',lambda x:x.update(clean_unload_verified=False))
        self.fx.change('confirmation/SERVER_CONTROL.json',lambda x:x['host_checks'][0]['state'].update(power="Now drawing from 'Battery Power'\n -InternalBattery-0 (id=REDACTED) 59%; discharging;"))
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertEqual(out['counts']['all']['exact_quality'],48)

    def test_clock_mismatch_blocks_even_exact_answers(self):
        self.fx.passing()
        self.fx.change('development/development-001.json',lambda x:x.update(epoch_monotonic_ns=1))
        self.fx.change('confirmation/STAGE.json',lambda x:x['clock_stamps'][-1].update(wall_ns=x['clock_stamps'][-1]['wall_ns']+10**9))
        out=self.fx.analyze();self.assertFalse(out['qualified'])
        self.assertTrue(any('raw epoch differs' in f for f in out['faults']))
        self.assertTrue(any('stage clock diagnostics fail' in f for f in out['faults']))

    def test_context_limit_and_frozen_source_mismatch(self):
        self.fx.passing()
        def mutate(x):
            x['requests'][0]['final']['prompt_eval_count']=4000
            x['requests'][0]['chunks'][-1]['data']['prompt_eval_count']=4000
        self.fx.change('development/development-001.json',mutate)
        (self.fx.base/'PROTOCOL.txt').write_text('modified')
        out=self.fx.analyze();self.assertFalse(out['qualified'])
        self.assertEqual(out['counts']['all']['exact_quality'],48)

    def test_official_gold_mismatch_caught_even_after_refreeze(self):
        self.fx.passing()
        jobs=copy.deepcopy(self.fx.jobs['development']);jobs[0]['answers'][0]['text']='wrong'
        save(self.fx.base/'development.json',jobs);self.fx.freeze();self.fx.campaign()
        out=self.fx.analyze();self.assertFalse(out['qualified'])
        self.assertTrue(any('job differs from official source' in f for f in out['faults']))

    def test_duplicate_raw_job_is_retained_and_rejected(self):
        self.fx.passing();directory=self.fx.capture/'development'
        (directory/'duplicate.json').write_bytes((directory/'development-001.json').read_bytes())
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertEqual(out['counts']['all']['raw_offered'],49)
        self.assertTrue(any('duplicate/non-string raw IDs' in f for f in out['faults']))

    def test_unexpected_fallback_directory_rejected(self):
        self.fx.passing();(self.fx.capture/'development-retry').mkdir()
        self.assertFalse(self.fx.analyze()['qualified'])

    def test_unseen_infrastructure_abort_is_zero_offered_not_success(self):
        self.fx.campaign(None,False,'aborted')
        out=self.fx.analyze();self.assertFalse(out['data_complete_valid']);self.assertFalse(out['qualified'])
        self.assertEqual(out['counts']['all']['raw_offered'],0);self.assertEqual(out['required_planned'],12)


if __name__ == '__main__':
    unittest.main()
