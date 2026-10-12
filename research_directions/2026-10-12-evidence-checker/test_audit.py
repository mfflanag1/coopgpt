"""Offline synthetic checks; no collector, model, host or primary scorer calls."""
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get('COOP_CHECKER_SOURCE', str(HERE if (HERE/'transport_audit.py').exists() else Path('/tmp/coop-checker-study'))))
sys.path.insert(0, str(SOURCE))
spec = importlib.util.spec_from_file_location('independent_checker_audit_under_test', HERE/'audit_runtime.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')


def good(case):
    return dict(verdict=case['label'], evidence=[] if case['label']=='insufficient' else ['D1'])


def synthetic_cases():
    cases = []
    for i in range(24):
        source = 'source'+str(i//4)
        claim = 'Fresh synthetic claim '+str(i)
        key = hashlib.sha256(('coop-evidence-check-20261012:'+source+':'+claim).encode()).hexdigest()[:20]
        label = audit.LABELS[i % 3]
        passages = [dict(id='D'+str(k+1), text='Evidence '+str(k)) for k in range(4)]
        cases.append(dict(request_id=key, label=label, claim=claim, source_id=source,
                          max_output_tokens=256, passages=passages,
                          acceptable_evidence=[] if label=='insufficient' else [['D1']],
                          relevant_evidence=[] if label=='insufficient' else ['D1', 'D2']))
    return sorted(cases, key=lambda c: hashlib.sha256(('order:'+c['request_id']).encode()).hexdigest())


def synthetic_controls(cases):
    groups = {label: [c for c in cases if c['label']==label] for label in audit.LABELS}
    chosen = [('missing_premise', c) for c in groups['insufficient'][:4]]
    chosen += [('wrong_verdict', c) for c in groups['supported'][:2]+groups['contradicted'][:2]]
    chosen += [('citation', c) for c in groups['supported'][2:4]+groups['contradicted'][2:4]]
    controls = []
    for i,(group,case) in enumerate(chosen):
        for valid in (False, True):
            candidate = good(case)
            if not valid:
                if group=='missing_premise':
                    candidate = dict(verdict=('supported' if i%2 else 'contradicted'), evidence=['D1'])
                elif group=='wrong_verdict':
                    candidate['verdict'] = 'contradicted' if case['label']=='supported' else 'supported'
                else:
                    candidate['evidence'] = []
            controls.append(dict(request_id='c_'+hashlib.sha256(f'{i}-{valid}'.encode()).hexdigest()[:20],
                                 case_id=case['request_id'], pair_id='pair'+str(i), error_group=group,
                                 expected_accept=valid, candidate=candidate))
    return controls


def answer_maps(cases, controls):
    primary = {c['request_id']: json.dumps(good(c)) for c in cases}
    checker = {'n_'+c['request_id']: '{"accept":true}' for c in cases}
    checker.update({c['request_id']: json.dumps({'accept':c['expected_accept']}) for c in controls})
    return primary, checker


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.cases=synthetic_cases(); self.controls=synthetic_controls(self.cases)
        self.primary,self.checker=answer_maps(self.cases,self.controls)
        self.case=next(c for c in self.cases if c['label']=='supported')
    def summary(self):
        return audit.quality_summary(self.cases,self.controls,self.primary,self.checker)
    def test_proof_and_relevant_corroboration(self):
        self.assertTrue(audit.score_output('{"evidence":["D2","D1"],"verdict":"supported"}',self.case)['quality_pass'])
        for evidence in [[],['D2'],['D1','D3'],['D9']]:
            self.assertFalse(audit.score_output(json.dumps(dict(verdict='supported',evidence=evidence)),self.case)['quality_pass'])
    def test_insufficient_requires_empty_evidence(self):
        c=next(c for c in self.cases if c['label']=='insufficient')
        self.assertTrue(audit.score_output('{"verdict":"insufficient","evidence":[]}',c)['quality_pass'])
        self.assertFalse(audit.score_output('{"verdict":"insufficient","evidence":["D1"]}',c)['quality_pass'])
    def test_primary_bad_schema(self):
        for text in ['null','[]','{"verdict":"supported","evidence":["D1","D1"]}',
                     '{"verdict":"supported","verdict":"supported","evidence":["D1"]}',
                     '{"verdict":"supported","evidence":["D1"],"extra":0}',
                     '{"verdict":"supported","evidence":[NaN]}','['*2000+']'*2000]:
            with self.subTest(text=text[:40]):self.assertFalse(audit.score_output(text,self.case)['schema_valid'])
    def test_checker_strict_actual_boolean(self):
        for text in ['{"accept":1}','{"accept":"false"}','{"accept":null}','{"accept":false,"x":0}',
                     '{"accept":false,"accept":true}','{"accept":NaN}','['*2000+']'*2000]:
            self.assertEqual(audit.parse_checker(text),dict(schema_valid=False,accept=False))
        self.assertEqual(audit.parse_checker('{"accept":true}'),dict(schema_valid=True,accept=True))
    def test_positive_and_sensitivity_unobserved(self):
        s=self.summary();self.assertTrue(s['engineering_gate_passed']);self.assertEqual(s['automatic_correct'],24)
        self.assertFalse(s['native_sensitivity_observed']);self.assertEqual(s['constructed_invalid_rejected'],12)
    def test_accepted_semantic_error_blocks(self):
        self.primary[self.case['request_id']]='{"verdict":"contradicted","evidence":["D1"]}'
        s=self.summary();self.assertEqual(s['automatic_errors'],1);self.assertFalse(s['native_gate_passed'])
    def test_rejected_error_is_referral_not_corrected(self):
        key=self.case['request_id'];self.primary[key]='{"verdict":"contradicted","evidence":["D1"]}'
        self.checker['n_'+key]='{"accept":false}'
        s=self.summary();self.assertTrue(s['engineering_gate_passed']);self.assertEqual(s['semantic_errors_caught'],1)
        self.assertEqual(s['automatic_correct'],23);self.assertEqual(s['referrals'],1)
    def test_bad_primary_format_never_automatic_or_semantic_catch(self):
        self.primary[self.case['request_id']]='not JSON'
        s=self.summary();self.assertEqual(s['format_referrals'],1);self.assertEqual(s['semantic_errors_caught'],0)
        self.assertEqual(s['automatic_errors'],0);self.assertEqual(s['referrals'],1)
        self.assertEqual(s['checker_accepted_malformed'],1)
        self.assertFalse(s['native_sensitivity_observed'])
    def test_malformed_acceptance_diagnostic_requires_valid_true_checker(self):
        key=self.case['request_id'];self.primary[key]='not JSON'
        self.checker['n_'+key]='{"accept":false}'
        self.assertEqual(self.summary()['checker_accepted_malformed'],0)
        self.checker['n_'+key]='{"accept":1}'
        s=self.summary();self.assertEqual(s['checker_accepted_malformed'],0)
        self.assertEqual(s['format_referrals'],1);self.assertEqual(s['automatic_errors'],0)
    def test_retention_integer_threshold(self):
        for c in self.cases[:2]:self.checker['n_'+c['request_id']]='{"accept":false}'
        self.assertTrue(self.summary()['native_gate_passed'])
        self.checker['n_'+self.cases[2]['request_id']]='{"accept":false}'
        self.assertFalse(self.summary()['native_gate_passed'])
    def test_18_retained_floor_independent_of_fraction(self):
        for c in self.cases[:7]:
            self.primary[c['request_id']]='bad JSON'
            self.checker['n_'+c['request_id']]='{"accept":false}'
        s=self.summary();self.assertEqual(s['automatic_correct'],17);self.assertFalse(s['native_gate_passed'])
    def test_all_invalid_controls_must_be_rejected(self):
        bad=next(c for c in self.controls if not c['expected_accept'])
        self.checker[bad['request_id']]='{"accept":true}'
        self.assertFalse(self.summary()['control_gate_passed'])
    def test_valid_control_threshold(self):
        good_controls=[c for c in self.controls if c['expected_accept']]
        self.checker[good_controls[0]['request_id']]='{"accept":false}'
        self.assertTrue(self.summary()['control_gate_passed'])
        self.checker[good_controls[1]['request_id']]='{"accept":false}'
        self.assertFalse(self.summary()['control_gate_passed'])
    def test_checker_bad_schema_is_not_successful_rejection(self):
        bad=next(c for c in self.controls if not c['expected_accept'])
        self.checker[bad['request_id']]='{"accept":0}'
        s=self.summary();self.assertEqual(s['checker_schema_valid'],47)
        self.assertEqual(s['constructed_invalid_rejected'],11);self.assertFalse(s['engineering_gate_passed'])
    def test_missing_calls_keep_denominator(self):
        del self.primary[self.case['request_id']];del self.checker['n_'+self.case['request_id']]
        s=self.summary();self.assertFalse(s['input_complete']);self.assertFalse(s['engineering_gate_passed'])
        self.assertEqual(s['baseline_errors'],1);self.assertEqual(s['baseline_correct_per_offered'],23/24)
    def test_control_labels_independently_validated(self):
        f=[];audit.validate_controls(self.cases,self.controls,f);self.assertEqual(f,[])
        self.controls[0]['expected_accept']=not self.controls[0]['expected_accept']
        f=[];audit.validate_controls(self.cases,self.controls,f);self.assertTrue(f)



class DuplicateInputTests(unittest.TestCase):
    def row(self, identifier, proposal, prefix='Packet and claim\n\nProposed answer:\n'):
        return dict(request_id=identifier, request_prompt=prefix+proposal+'\n\nAudit JSON:',
                    request_model=audit.MODEL, request_format=copy.deepcopy(audit.CHECK_SCHEMA),
                    request_options=dict(num_ctx=4096,num_predict=64,seed=0,temperature=0), request_think=False)
    def diagnostic(self, rows, prefixes=None):
        contexts={r['request_id']:((prefixes or {}).get(r['request_id'],'Packet and claim\n\nProposed answer:\n'),
                                  '\n\nAudit JSON:') for r in rows}
        return audit.checker_duplicate_diagnostics(rows,contexts)
    def test_exact_wire_duplicate_ignores_only_payload_object_order(self):
        rows=[self.row('n_one','{"verdict":"insufficient","evidence":[]}'),
              self.row('c_two','{"verdict":"insufficient","evidence":[]}')]
        rows[1]['request_options']=dict(reversed(list(rows[1]['request_options'].items())))
        d=self.diagnostic(rows)
        self.assertEqual(d['exact_payload']['unique_inputs'],1)
        self.assertEqual(d['exact_payload']['excess_duplicate_calls'],1)
        self.assertEqual(d['exact_payload']['groups'][0]['request_ids'],['c_two','n_one'])
        self.assertEqual(d['observed_checker_rows'],2)
    def test_proposal_formatting_equivalence_separate_from_exact(self):
        rows=[self.row('n_one',' {"verdict": "insufficient", "evidence": []} '),
              self.row('c_two','{"evidence":[],"verdict":"insufficient"}')]
        d=self.diagnostic(rows)
        self.assertEqual(d['exact_payload']['duplicate_group_count'],0)
        self.assertEqual(d['proposal_json_equivalence']['duplicate_group_count'],1)
    def test_options_and_schema_are_part_of_input(self):
        rows=[self.row('n_one','{}'),self.row('c_two','{}')]
        rows[1]['request_options']['num_predict']=32
        self.assertEqual(self.diagnostic(rows)['proposal_json_equivalence']['unique_inputs'],2)
        rows[1]['request_options']['num_predict']=64;rows[1]['request_format']['description']='different schema'
        self.assertEqual(self.diagnostic(rows)['exact_payload']['unique_inputs'],2)
    def test_same_answer_different_claim_is_not_duplicate(self):
        rows=[self.row('n_one','{}'),self.row('c_two','{}','Different packet and claim\n\nProposed answer:\n')]
        d=self.diagnostic(rows,{'c_two':'Different packet and claim\n\nProposed answer:\n'})
        self.assertEqual(d['exact_payload']['unique_inputs'],2)
        self.assertEqual(d['proposal_json_equivalence']['unique_inputs'],2)
    def test_malformed_proposal_can_be_exact_duplicate(self):
        rows=[self.row('n_one','broken JSON'),self.row('c_two','broken JSON')]
        d=self.diagnostic(rows)
        self.assertEqual(d['exact_payload']['duplicate_group_count'],1)
        self.assertEqual(d['proposal_json_equivalence']['input_rows'],0)
        self.assertEqual(d['unavailable_proposal_json_request_ids'],['n_one','c_two'])
    def test_array_order_not_silently_normalized(self):
        rows=[self.row('n_one','{"evidence":["D1","D2"]}'),self.row('c_two','{"evidence":["D2","D1"]}')]
        self.assertEqual(self.diagnostic(rows)['proposal_json_equivalence']['unique_inputs'],2)
    def test_missing_wire_metadata_is_reported(self):
        rows=[self.row('n_one','{}')];del rows[0]['request_think']
        d=self.diagnostic(rows)
        self.assertEqual(d['observed_checker_rows'],1)
        self.assertEqual(d['exact_payload']['input_rows'],0)
        self.assertEqual(d['unavailable_wire_request_ids'],['n_one'])


WALL=1791777600000000000

def stamp(second):
    n=int(second*1e9)
    return dict(monotonic_before_ns=n,monotonic_after_ns=n+100,wall_ns=WALL+n+50)


def iso(second):
    return datetime.fromtimestamp((WALL+int(second*1e9))/1e9,timezone.utc).isoformat()


def make_raw(identifier,prompt,text,cap,schema,second):
    start,end=stamp(second),stamp(second+1)
    final=dict(done=True,model=audit.MODEL,response='',done_reason='stop',prompt_eval_count=100,
               eval_count=10,total_duration=1000,load_duration=0,prompt_eval_duration=500,eval_duration=500)
    row=dict(request_id=identifier,request_prompt=prompt,request_model=audit.MODEL,
             request_think=False,request_format=schema,
             request_options=dict(num_ctx=4096,num_predict=cap,temperature=0,seed=0),arrival_offset_s=0,
             completed=True,error=None,http_status=200,deadline_exceeded=False,
             dispatch_offset_s=.01,first_content_offset_s=.1,terminal_offset_s=.9,
             chunks=[dict(offset_s=.1,data=dict(done=False,model=audit.MODEL,response=text)),
                     dict(offset_s=.9,data=final)],final=final)
    return dict(started_stamp=start,finished_stamp=end,started_utc=iso(second),
                epoch_monotonic_ns=start['monotonic_after_ns'],
                elapsed_seconds=(end['monotonic_before_ns']-start['monotonic_after_ns'])/1e9,requests=[row])


def fixture(root):
    base=root/'source';base.mkdir();(base/'sources').mkdir();capture=root/'capture';capture.mkdir()
    out=capture/'collection';out.mkdir();cases=synthetic_cases();controls=synthetic_controls(cases)
    config=json.loads((SOURCE/'CONFIG.json').read_text());dump(base/'CONFIG.json',config)
    for name in ['MODEL_LOCK.json','MODEL_MANIFEST.json']:(base/name).write_bytes((SOURCE/name).read_bytes())
    sources=[]
    for i in range(6):
        name='source'+str(i);file='sources/'+name+'.txt';lic='sources/'+name+'.LICENSE'
        texts=['Source '+str(i)+' fact '+str(k)+'.' for k in range(4)];raw='\n'.join(texts)
        (base/file).write_text(raw);(base/lic).write_text('Synthetic license')
        sources.append(dict(id=name,source_file=file,sha256=audit.sha(base/file),license_file=lic,
                            license_sha256=audit.sha(base/lic),commit='a'*40))
        for c in cases:
            if c['source_id']!=name:continue
            c['passages']=[];offset=0
            for k,text in enumerate(texts):
                c['passages'].append(dict(id='D'+str(k+1),text=text,source_file=file,
                    source_char_start=offset,source_char_end=offset+len(text),
                    source_text_sha256=hashlib.sha256(text.encode()).hexdigest(),transformation='verbatim'))
                offset+=len(text)+1
    dump(base/'SOURCE_MANIFEST.json',sources);dump(base/'cases.json',cases);dump(base/'controls.json',controls)
    dump(base/'PRIOR_CLAIMS.json',['An old different claim'])
    constants=dict(INSTRUCTION='Public primary instruction\n/no_think\n',CHECK_INSTRUCTION='Public checker instruction\n/no_think\n',SCHEMA=audit.SCHEMA,CHECK_SCHEMA=audit.CHECK_SCHEMA)
    (base/'contract.py').write_text('\n'.join(k+'='+repr(v) for k,v in constants.items())+'\nraise RuntimeError("Do not execute primary contract")\n')
    for name in audit.NEEDED-{'CONFIG.json','MODEL_LOCK.json','MODEL_MANIFEST.json','cases.json','controls.json','PRIOR_CLAIMS.json','contract.py','SOURCE_MANIFEST.json'}:
        (base/name).write_text('Synthetic frozen source\n')
    frozen={str(p.relative_to(base)):audit.sha(p) for p in base.rglob('*') if p.is_file()}
    dump(base/'FREEZE.json',dict(frozen_utc=iso(-3600),sha256=frozen))
    primary,checker=answer_maps(cases,controls);by_id={c['request_id']:c for c in cases};by_control={c['request_id']:c for c in controls}
    order=audit.order_for(cases,controls);stamps=[stamp(3)];entries=[]
    dump(out/'WARMUP.json',make_raw('warm',audit.WARM_PROMPT,'{"accept":false}',32,audit.CHECK_SCHEMA,1))
    for i,key in enumerate(order):
        t=5+i*3;case_id=key[2:] if key.startswith(('p_','n_')) else by_control[key]['case_id'];case=by_id[case_id]
        phase='primary' if key.startswith('p_') else 'checker';cap=256 if phase=='primary' else 64
        proposal=None if phase=='primary' else (primary[case_id] if key.startswith('n_') else json.dumps(by_control[key]['candidate'],sort_keys=True,separators=(',',':'),allow_nan=False))
        raw=make_raw(key,audit.prompt_for(case,constants,proposal),primary[case_id] if phase=='primary' else checker[key],cap,audit.SCHEMA if phase=='primary' else audit.CHECK_SCHEMA,t)
        dump(out/(key+'.json'),raw);before,after=stamp(t-.1),stamp(t+1.1)
        stamps.extend([before,raw['started_stamp'],raw['finished_stamp'],after])
        entries.append(dict(request_id=key,phase=phase,case_id=case_id,api_completed=True,raw_file=key+'.json',
                            observed_context_margin=4096-100-cap,output_tokens=10,done_reason='stop',completion_s=.9,
                            collector_duration=audit.duration(raw['started_stamp'],raw['finished_stamp']),
                            phase_duration=audit.duration(before,after)))
    stamps.append(stamp(222));stage=dict(part='collection',candidate=audit.MODEL,planned=72,status='completed',
             started_utc=iso(0),finished_utc=iso(225),requests=entries,completed_requests=72,
             clock_stamps=stamps,clock_diagnostics=dict(audit.clock_check(stamps),errors=[]));dump(out/'STAGE.json',stage)
    host=dict(power_source='AC Power',external_power_connected=True,battery_percent=80,
              power="Now drawing from 'AC Power'\n -InternalBattery-0 (id=REDACTED)\t80%; charging; present: true",thermal='No thermal warning level has been recorded\nNo performance warning level has been recorded')
    model=dict(name=audit.MODEL,digest=audit.DIGEST,context_length=4096,size_vram=1000)
    meta=dict(status='completed',errors=[],clean_unload_verified=True,loaded_after_unload={'models':[]},
              dedicated_server_returncode=0,model=audit.MODEL,context=4096,parallel=1,runtime_parallel_values=[1],
              version={'version':'0.20.0'},model_tag={'name':audit.MODEL,'digest':audit.DIGEST},options=config['options'],
              server_settings=dict(config['server_settings_common'],OLLAMA_NUM_PARALLEL='1'),
              allow_battery_quality=config['allow_battery_quality'],lock_verification=config['lock'],
              dedicated_server_pid=777,dedicated_process_group=777,
              loaded_checks=[{'response':{'models':[model]}} for _ in range(3)],before=host,after=host,
              original_endpoint_idle_before=True,original_endpoint_idle_after=True,
              host_checks=[dict(phase=prefix+key,passed=True,original_endpoint_idle=True,state=host)
                           for key in order for prefix in ('before_','after_')]);dump(out/'SERVER_CONTROL.json',meta)
    (out/'SERVER.log').write_text('Parallel:1\n')
    dump(capture/'CAMPAIGN.json',dict(status='completed',started_utc=iso(-1),finished_utc=iso(226),
        source_freeze_sha256=audit.sha(base/'FREEZE.json'),planned_requests=72,scored_requests=72,stages=[stage]))
    return base,capture,cases,controls


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base,self.capture,self.cases,self.controls=fixture(Path(self.tmp.name));self.out=self.capture/'collection'
    def run_audit(self):return audit.analyze(self.base,self.capture)
    def edit(self,name,change):
        p=self.out/name;v=json.loads(p.read_text());change(v);dump(p,v)
    def test_full_positive_no_contract_execution(self):
        r=self.run_audit();self.assertEqual(r['faults'],[]);self.assertTrue(r['qualified'])
        self.assertEqual(r['counts']['raw_offered'],72);self.assertEqual(r['quality_summary']['checker_schema_valid'],48)
        d=r['checker_input_duplicates'];self.assertEqual(d['observed_checker_rows'],48)
        self.assertEqual(d['exact_payload']['unique_inputs'],48)
        self.assertEqual(d['proposal_json_equivalence']['unique_inputs'],36)
        self.assertEqual(d['proposal_json_equivalence']['duplicate_group_count'],12)
        self.assertEqual(r['quality_summary']['automatic_correct'],24)
        self.assertNotIn('checker_input_duplicates',r['quality_summary'])
    def test_native_proposal_must_be_byte_exact(self):
        key='n_'+self.cases[0]['request_id']
        self.edit(key+'.json',lambda r:r['requests'][0].update(request_prompt=r['requests'][0]['request_prompt'].replace('Proposed answer:\n','Proposed answer:\n ')))
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertTrue(any('binding differs' in f for f in r['faults']))
        self.assertEqual(r['counts']['raw_offered'],72)
    def test_control_cannot_be_replaced_by_natural(self):
        c=next(c for c in self.controls if not c['expected_accept']);key=c['request_id']
        self.edit(key+'.json',lambda r:r['requests'][0].update(request_prompt=r['requests'][0]['request_prompt'].replace('Proposed answer:', 'Different proposal:')))
        self.assertFalse(self.run_audit()['data_complete_valid'])
    def test_missing_capture_keeps_72_planned(self):
        (self.out/('n_'+self.cases[0]['request_id']+'.json')).unlink();r=self.run_audit()
        self.assertEqual(r['counts']['planned'],72);self.assertEqual(r['counts']['raw_offered'],71)
        self.assertFalse(r['qualified']);self.assertEqual(len(r['missing_ids']),1)
    def test_orphan_postflight_abort_retained(self):
        self.edit('STAGE.json',lambda s:(s.update(status='aborted'),s['requests'].pop()))
        r=self.run_audit();self.assertEqual(r['counts']['raw_offered'],72);self.assertEqual(len(r['orphan_raw_ids']),1)
        self.assertFalse(r['data_complete_valid'])
    def test_transport_fault_does_not_become_acceptance(self):
        key='n_'+self.cases[0]['request_id']
        self.edit(key+'.json',lambda r:r['requests'][0].update(completed=False,error='timeout'))
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertEqual(r['counts']['api_completed'],71)
        self.assertEqual(r['quality_summary']['checker_schema_valid'],47)
    def test_extra_raw_preserved(self):
        key='p_'+self.cases[0]['request_id'];(self.out/'orphan.json').write_bytes((self.out/(key+'.json')).read_bytes())
        r=self.run_audit();self.assertEqual(r['counts']['raw_offered'],73);self.assertFalse(r['qualified'])
    def test_checker_token_cap(self):
        key='n_'+self.cases[0]['request_id']
        def mutate(raw):
            row=raw['requests'][0];row['final']['eval_count']=65;row['chunks'][-1]['data']['eval_count']=65
        self.edit(key+'.json',mutate);self.assertTrue(any('cap failed' in f for f in self.run_audit()['faults']))
    def test_clock_binds_raw_order(self):
        self.edit('STAGE.json',lambda s:s['clock_stamps'].__setitem__(2,s['clock_stamps'][6]))
        self.assertFalse(self.run_audit()['data_complete_valid'])
    def test_wall_chronology_must_match_capture(self):
        key='p_'+self.cases[0]['request_id']
        self.edit(key+'.json',lambda r:r.update(started_utc=iso(-100)))
        self.assertTrue(any('paired wall stamp' in f for f in self.run_audit()['faults']))
    def test_warmup_context_allowance(self):
        def mutate(raw):
            raw['requests'][0]['final']['prompt_eval_count']=4000
            raw['requests'][0]['chunks'][-1]['data']['prompt_eval_count']=4000
        self.edit('WARMUP.json',mutate)
        self.assertTrue(any('warmup context allowance' in f for f in self.run_audit()['faults']))
    def test_cleanup_must_be_verified(self):
        self.edit('SERVER_CONTROL.json',lambda m:m.update(clean_unload_verified=False))
        self.assertFalse(self.run_audit()['data_complete_valid'])
    def test_source_tamper_fails_but_attempts_remain(self):
        (self.base/'PROTOCOL.txt').write_text('Changed after freeze')
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertEqual(r['counts']['raw_offered'],72)
        self.assertTrue(any('frozen file changed' in f for f in r['faults']))
    def test_freeze_after_campaign_rejected(self):
        f=json.loads((self.base/'FREEZE.json').read_text());f['frozen_utc']=iso(100);dump(self.base/'FREEZE.json',f)
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertTrue(any('freeze follows' in f for f in r['faults']))
    def refreeze_excerpt_count(self,count):
        jobs=json.loads((self.base/'cases.json').read_text())
        for job in jobs:job['passages']=job['passages'][:count]
        dump(self.base/'cases.json',jobs)
        freeze=json.loads((self.base/'FREEZE.json').read_text())
        freeze['sha256']['cases.json']=audit.sha(self.base/'cases.json');dump(self.base/'FREEZE.json',freeze)
        campaign=json.loads((self.capture/'CAMPAIGN.json').read_text())
        campaign['source_freeze_sha256']=audit.sha(self.base/'FREEZE.json')
        faults=[];audit.source_check(self.base,campaign,faults)
        return faults
    def test_source_fixture_three_passages_accepted(self):
        self.assertEqual(self.refreeze_excerpt_count(3),[])
    def test_source_fixture_two_passages_rejected(self):
        faults=self.refreeze_excerpt_count(2)
        self.assertTrue(any('three or four distinct excerpts required' in f for f in faults))
    def test_source_slice_mismatch_even_if_hash_refrozen(self):
        jobs=json.loads((self.base/'cases.json').read_text());jobs[0]['passages'][0]['text']='Invented excerpt';dump(self.base/'cases.json',jobs)
        f=json.loads((self.base/'FREEZE.json').read_text());f['sha256']['cases.json']=audit.sha(self.base/'cases.json');dump(self.base/'FREEZE.json',f)
        self.assertTrue(any('excerpt transform differs' in f for f in self.run_audit()['faults']))
    def test_malformed_or_missing_stage_does_not_lose_offers(self):
        (self.out/'STAGE.json').write_text('{broken')
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertEqual(r['counts']['raw_offered'],72)
    def test_model_thinking_is_invalid_collection(self):
        key='p_'+self.cases[0]['request_id']
        self.edit(key+'.json',lambda r:r['requests'][0]['chunks'][0]['data'].update(thinking='unexpected'))
        self.assertFalse(self.run_audit()['data_complete_valid'])


if __name__=='__main__':unittest.main()
