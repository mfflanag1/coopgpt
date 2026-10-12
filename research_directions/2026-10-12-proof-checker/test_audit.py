"""Offline synthetic audit checks. No host, collector, model, or scorer calls."""
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get('COOP_CHECKER_SOURCE', str(HERE if (HERE/'transport_audit.py').exists() else Path('/tmp/coop-proof-checker'))))
sys.path.insert(0, str(SOURCE))
spec = importlib.util.spec_from_file_location('independent_proof_audit_under_test', HERE/'audit_runtime.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')


def good(case):
    return dict(verdict=case['label'], evidence=[] if case['label']=='insufficient' else
                ['D1', 'D2'] if case['label']=='supported' else ['D2'])


def inventory(case):
    return {p['id']: {side: p[side] for side in ('support', 'contradict')} for p in case['components']}


def synthetic_cases():
    cases = []
    for i in range(24):
        source = 'source'+str(i//4)
        label = audit.LABELS[i % 3]
        parts = [dict(id='a1', claim='First synthetic fact '+str(i), label='supported',
                      support=[['D1']], contradict=[], rationale='Synthetic support'),
                 dict(id='a2', claim='Second synthetic fact '+str(i), label=label,
                      support=[['D2']] if label=='supported' else [],
                      contradict=[['D2']] if label=='contradicted' else [], rationale='Synthetic relation')]
        claim = 'Both statements hold: (a1) '+parts[0]['claim']+' (a2) '+parts[1]['claim']
        key = hashlib.sha256(('coop-proof-check-20261012:'+source+':'+claim).encode()).hexdigest()[:20]
        passages = [dict(id='D'+str(k+1), text='Evidence '+str(k)) for k in range(4)]
        evidence = [] if label=='insufficient' else ['D1','D2'] if label=='supported' else ['D2']
        cases.append(dict(request_id=key, label=label, claim=claim, source_id=source,
                          max_output_tokens=256, passages=passages, components=parts,
                          acceptable_evidence=[evidence] if evidence else [], relevant_evidence=evidence))
    return sorted(cases, key=lambda c: hashlib.sha256(('order:'+c['request_id']).encode()).hexdigest())


def synthetic_controls(cases):
    controls = []
    for label in audit.LABELS:
        chosen = [c for c in cases if c['label']==label][:4]
        for index,case in enumerate(chosen):
            group = ('unsupported_decisive' if label=='insufficient' else
                     'false_insufficient' if index<2 else 'citation')
            candidate = (dict(verdict='supported' if index<2 else 'contradicted',evidence=['D1'])
                         if label=='insufficient' else dict(verdict='insufficient',evidence=[])
                         if index<2 else dict(verdict=label,evidence=['D1']))
            for valid,proposal in ((True,good(case)),(False,candidate)):
                pair = 'pair_'+case['request_id']
                key = 'c_'+hashlib.sha256(('coop-proof-control:'+pair+':'+str(valid)).encode()).hexdigest()[:20]
                controls.append(dict(request_id=key,case_id=case['request_id'],pair_id=pair,
                                     error_group=group,expected_accept=valid,candidate=proposal))
    return sorted(controls,key=lambda item:hashlib.sha256(('control-order:'+item['request_id']).encode()).hexdigest())


def answer_maps(cases, controls):
    return ({c['request_id']: json.dumps(good(c)) for c in cases},
            {c['request_id']: json.dumps(inventory(c)) for c in cases})


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.cases=synthetic_cases(); self.controls=synthetic_controls(self.cases)
        self.primary,self.inventories=answer_maps(self.cases,self.controls)
        self.case=next(c for c in self.cases if c['label']=='supported')
    def summary(self):
        return audit.quality_summary(self.cases,self.controls,self.primary,self.inventories)
    def decide(self, obj, inv=None, case=None):
        case=case or self.case
        return audit.decision(json.dumps(obj), json.dumps(inv or inventory(case)), case)
    def test_two_conjunct_support_needs_both(self):
        self.assertTrue(self.decide(good(self.case))['accept'])
        for evidence in [[],['D1'],['D2'],['D1','D2','D3'],['D9']]:
            self.assertFalse(self.decide(dict(verdict='supported',evidence=evidence))['accept'])
    def test_one_false_conjunct_suffices(self):
        c=next(c for c in self.cases if c['label']=='contradicted')
        self.assertTrue(self.decide(dict(verdict='contradicted',evidence=['D2']),case=c)['accept'])
        self.assertFalse(self.decide(dict(verdict='contradicted',evidence=['D1','D2']),case=c)['accept'])
    def test_insufficient_with_known_supported_part(self):
        c=next(c for c in self.cases if c['label']=='insufficient')
        self.assertTrue(self.decide(good(c),case=c)['accept'])
        self.assertFalse(self.decide(dict(verdict='insufficient',evidence=['D1']),case=c)['accept'])
    def test_all_nine_relation_combinations(self):
        for a,b in itertools.product(audit.LABELS,repeat=2):
            inv={name:{'support':[['D1']] if state=='supported' else [],
                       'contradict':[['D2']] if state=='contradicted' else []}
                 for name,state in zip(('a1','a2'),(a,b))}
            expected='contradicted' if 'contradicted' in (a,b) else 'supported' if a==b=='supported' else 'insufficient'
            self.assertEqual(audit.parse_inventory(json.dumps(inv),self.case)['aggregate'],expected)
    def test_false_insufficient_is_rejected_for_both_decisive_verdicts(self):
        for c in (c for c in self.cases if c['label']!='insufficient'):
            self.assertEqual(self.decide(dict(verdict='insufficient',evidence=[]),case=c)['reason'],'verdict_mismatch')
    def test_alternative_proof_and_declared_union_policy(self):
        inv=inventory(self.case);inv['a1']['support']=[['D1'],['D3','D4']]
        self.assertTrue(self.decide(dict(verdict='supported',evidence=['D2','D3','D4']),inv)['accept'])
        # Frozen union policy permits a relevant citation from another declared alternative.
        self.assertTrue(self.decide(dict(verdict='supported',evidence=['D1','D2','D3']),inv)['accept'])
    def test_conflict_is_valid_schema_but_unusable(self):
        inv=inventory(self.case);inv['a2']['contradict']=[['D3']]
        parsed=audit.parse_inventory(json.dumps(inv),self.case)
        self.assertTrue(parsed['schema_valid']);self.assertTrue(parsed['conflict']);self.assertFalse(parsed['usable'])
        self.assertEqual(self.decide(good(self.case),inv)['reason'],'inventory_unusable')
    def test_inventory_strict_proof_schema(self):
        bad=[]
        for proof in [[],['D1','D1'],['D1','D2','D3','D4'],[True]]:
            inv=inventory(self.case);inv['a1']['support']=[proof];bad.append(json.dumps(inv))
        inv=inventory(self.case);inv['a1']['support']=[['D1','D2'],['D2','D1']];bad.append(json.dumps(inv))
        inv=inventory(self.case);inv['a1']['support']=[['D1'],['D2'],['D3'],['D4']];bad.append(json.dumps(inv))
        bad += ['null','[]','{"a1":{},"a1":{},"a2":{}}', '['*2000+']'*2000]
        for text in bad:
            with self.subTest(text=text[:100]):self.assertFalse(audit.parse_inventory(text,self.case)['schema_valid'])
    def test_unknown_id_is_schema_valid_unusable(self):
        inv=inventory(self.case);inv['a1']['support']=[['D9']]
        parsed=audit.parse_inventory(json.dumps(inv),self.case)
        self.assertTrue(parsed['schema_valid']);self.assertFalse(parsed['usable'])
        self.assertIsNone(parsed['aggregate'])
    def test_decision_needs_packet_only_never_gold(self):
        job={'passages':self.case['passages']}
        result=audit.decision(json.dumps(good(self.case)),json.dumps(inventory(self.case)),job)
        self.assertTrue(result['accept'])
    def test_missing_valid_alternative_is_not_forgiven(self):
        c=copy.deepcopy(self.case);c['components'][0]['support'].append(['D3'])
        c['acceptable_evidence'].append(['D2','D3']);c['relevant_evidence'].append('D3')
        candidate=dict(verdict='supported',evidence=['D2','D3'])
        inv=inventory(self.case)
        self.assertTrue(audit.score_output(json.dumps(candidate),c)['quality_pass'])
        self.assertFalse(self.decide(candidate,inv,c)['accept'])
        q=audit.inventory_quality(json.dumps(inv),c)
        self.assertTrue(q['quality_pass']);self.assertFalse(q['all_alternatives_recovered'])
    def test_relevant_nonminimal_proof_semantics_separate_from_alternative_recovery(self):
        c=copy.deepcopy(self.case);c['components'][0]['support'].append(['D3'])
        inv=inventory(c);inv['a1']['support']=[['D1','D3']]
        q=audit.inventory_quality(json.dumps(inv),c)
        self.assertTrue(q['quality_pass']);self.assertFalse(q['all_alternatives_recovered'])
    def test_primary_bad_schema(self):
        for text in ['null','[]','{"verdict":"supported","evidence":["D1","D1"]}',
                     '{"verdict":"supported","verdict":"supported","evidence":["D1"]}',
                     '{"verdict":"supported","evidence":["D1"],"extra":0}',
                     '{"verdict":"supported","evidence":[NaN]}','['*2000+']'*2000]:
            self.assertFalse(audit.score_output(text,self.case)['schema_valid'])
    def test_positive_and_sensitivity_unobserved(self):
        s=self.summary();self.assertTrue(s['engineering_gate_passed']);self.assertEqual(s['automatic_correct'],24)
        self.assertFalse(s['native_sensitivity_observed']);self.assertEqual(s['constructed_invalid_rejected'],12)
        self.assertEqual(s['inventory_component_correct'],48)
    def test_correlated_semantic_error_blocks(self):
        key=self.case['request_id'];self.primary[key]='{"verdict":"insufficient","evidence":[]}'
        inv=inventory(self.case);inv['a2']['support']=[];self.inventories[key]=json.dumps(inv)
        s=self.summary();self.assertEqual(s['automatic_errors'],1);self.assertFalse(s['native_gate_passed'])
        self.assertEqual(s['inventory_component_correct'],47)
    def test_rejection_is_referral_not_correction(self):
        self.primary[self.case['request_id']]='{"verdict":"insufficient","evidence":[]}'
        s=self.summary();self.assertTrue(s['engineering_gate_passed']);self.assertEqual(s['semantic_errors_caught'],1)
        self.assertEqual(s['automatic_correct'],23);self.assertEqual(s['referrals'],1)
    def test_malformed_primary_not_semantic_catch(self):
        self.primary[self.case['request_id']]='bad JSON'
        s=self.summary();self.assertEqual(s['format_referrals'],1);self.assertEqual(s['semantic_errors_caught'],0)
        self.assertEqual(s['automatic_errors'],0);self.assertFalse(s['native_sensitivity_observed'])
    def test_malformed_inventory_is_not_semantic_catch(self):
        key=self.case['request_id'];self.primary[key]='{"verdict":"insufficient","evidence":[]}'
        self.inventories[key]='bad JSON';s=self.summary()
        self.assertEqual(s['inventory_schema_valid'],23);self.assertEqual(s['semantic_errors_caught'],0)
        self.assertFalse(s['engineering_gate_passed'])
    def test_retention_integer_threshold(self):
        for c in self.cases[:2]:self.inventories[c['request_id']]='{}'
        self.assertTrue(self.summary()['native_gate_passed'])
        self.inventories[self.cases[2]['request_id']]='{}'
        self.assertFalse(self.summary()['native_gate_passed'])
    def test_18_floor_independent_of_fraction(self):
        for c in self.cases[:7]:self.primary[c['request_id']]='bad JSON'
        s=self.summary();self.assertEqual(s['automatic_correct'],17);self.assertFalse(s['native_gate_passed'])
    def test_all_invalid_controls_must_be_rejected(self):
        control=next(r for r in self.controls if not r['expected_accept'] and
                     r['error_group']=='unsupported_decisive' and r['candidate']['verdict']=='supported')
        self.inventories[control['case_id']]=json.dumps({part:{'support':[['D1']], 'contradict':[]}
                                                       for part in ('a1','a2')})
        result=self.summary()
        self.assertEqual(result['constructed_invalid_rejected'],11)
        self.assertFalse(result['control_gate_passed'])
    def test_valid_control_retention_threshold(self):
        selected=[r for r in self.controls if r['expected_accept'] and r['error_group']=='citation'
                  and r['candidate']['verdict']=='supported']
        for idx,control in enumerate(selected):
            inv=json.loads(self.inventories[control['case_id']]);inv['a1']['support']=[['D3']]
            self.inventories[control['case_id']]=json.dumps(inv)
            result=self.summary()
            self.assertEqual(result['constructed_invalid_rejected'],12)
            self.assertEqual(result['constructed_valid_retained'],11-idx)
            self.assertEqual(result['control_gate_passed'],idx==0)
    def test_missing_calls_keep_denominator(self):
        del self.primary[self.case['request_id']];del self.inventories[self.case['request_id']]
        s=self.summary();self.assertFalse(s['input_complete']);self.assertEqual(s['baseline_errors'],1)
        self.assertEqual(s['baseline_correct_per_offered'],23/24)
    def test_control_labels_independently_validated(self):
        faults=[];audit.validate_controls(self.cases,self.controls,faults);self.assertEqual(faults,[])
        self.controls[0]['expected_accept']=not self.controls[0]['expected_accept']
        faults=[];audit.validate_controls(self.cases,self.controls,faults);self.assertTrue(faults)
    def test_control_group_assignment_cannot_be_swapped_after_selection(self):
        first=next(c for c in self.controls if not c['expected_accept'] and
                   c['error_group']=='false_insufficient' and c['candidate']['verdict']=='insufficient'
                   and next(j for j in self.cases if j['request_id']==c['case_id'])['label']=='supported')
        third=next(c for c in self.controls if not c['expected_accept'] and c['error_group']=='citation'
                   and c['candidate']['verdict']=='supported')
        assignments={first['case_id']:(third['error_group'],copy.deepcopy(third['candidate'])),
                     third['case_id']:(first['error_group'],copy.deepcopy(first['candidate']))}
        for item in self.controls:
            if item['case_id'] in assignments:
                group,proposal=assignments[item['case_id']];item['error_group']=group
                if not item['expected_accept']:item['candidate']=proposal
        faults=[];audit.validate_controls(self.cases,self.controls,faults)
        self.assertEqual(faults,['controls differ from prospective selection/construction/order'])
    def test_control_cannot_select_fifth_case_with_same_label(self):
        candidates=[c for c in self.cases if c['label']=='supported'];old,new=candidates[0],candidates[4]
        for control in self.controls:
            if control['case_id']==old['request_id']:
                control['case_id']=new['request_id'];control['pair_id']='pair_'+new['request_id']
                control['request_id']='c_'+hashlib.sha256(('coop-proof-control:'+control['pair_id']+':'+str(control['expected_accept'])).encode()).hexdigest()[:20]
        self.controls.sort(key=lambda item:hashlib.sha256(('control-order:'+item['request_id']).encode()).hexdigest())
        faults=[];audit.validate_controls(self.cases,self.controls,faults)
        self.assertEqual(faults,['controls differ from prospective selection/construction/order'])
    def test_insufficient_control_polarity_is_tied_to_hash_position(self):
        bad=[c for c in self.controls if not c['expected_accept'] and c['error_group']=='unsupported_decisive']
        first=next(c for c in bad if c['candidate']['verdict']=='supported')
        second=next(c for c in bad if c['candidate']['verdict']=='contradicted')
        first['candidate']['verdict'],second['candidate']['verdict']='contradicted','supported'
        faults=[];audit.validate_controls(self.cases,self.controls,faults)
        self.assertEqual(faults,['controls differ from prospective selection/construction/order'])
    def test_control_order_and_request_hash_are_bound(self):
        self.controls.reverse();faults=[];audit.validate_controls(self.cases,self.controls,faults)
        self.assertEqual(faults,['controls differ from prospective selection/construction/order'])
        self.controls.reverse();self.controls[0]['request_id']='c_'+'0'*20
        faults=[];audit.validate_controls(self.cases,self.controls,faults)
        self.assertIn('controls differ from prospective selection/construction/order',faults)
    def test_valid_control_must_use_first_gold_proof(self):
        case=next(c for c in self.cases if c['label']=='contradicted')
        case['acceptable_evidence'].append(['D3']);case['relevant_evidence'].append('D3')
        control=next(c for c in self.controls if c['case_id']==case['request_id'] and c['expected_accept'])
        control['candidate']['evidence']=['D3']
        faults=[];audit.validate_controls(self.cases,self.controls,faults)
        self.assertEqual(faults,['controls differ from prospective selection/construction/order'])
    def test_citation_control_fallback_first_failing_singleton_then_empty(self):
        case=[c for c in self.cases if c['label']=='contradicted'][2]
        case['components'][0]['support']=[['D2']]
        planned=audit.prescribed_controls(self.cases)
        bad=next(c for c in planned if c['case_id']==case['request_id'] and not c['expected_accept'])
        self.assertEqual(bad['candidate']['evidence'],['D1'])
        case['acceptable_evidence']=[[p['id']] for p in case['passages']]
        case['relevant_evidence']=[p['id'] for p in case['passages']]
        planned=audit.prescribed_controls(self.cases)
        bad=next(c for c in planned if c['case_id']==case['request_id'] and not c['expected_accept'])
        self.assertEqual(bad['candidate']['evidence'],[])
    def test_format_variants_are_local_diagnostics(self):
        d=audit.format_diagnostics(self.cases,self.controls,self.primary,self.inventories)
        self.assertEqual(d['variants_checked'],96);self.assertEqual(d['decision_mismatches'],[])
        self.primary[self.case['request_id']]='bad JSON'
        d=audit.format_diagnostics(self.cases,self.controls,self.primary,self.inventories)
        self.assertEqual(d['malformed_candidates'],1);self.assertEqual(d['variants_checked'],94)


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
        texts=['Source '+str(i)+' fact '+str(k)+'. '+'Synthetic text '*16 for k in range(4)];raw='\n'.join(texts)
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
    constants=dict(INSTRUCTION='Public primary instruction\n/no_think\n',INVENTORY_INSTRUCTION='Public inventory instruction\n/no_think\n',SCHEMA=audit.SCHEMA,INVENTORY_SCHEMA=audit.INVENTORY_SCHEMA)
    (base/'contract.py').write_text('\n'.join(k+'='+repr(v) for k,v in constants.items())+'\nraise RuntimeError("Do not execute primary contract")\n')
    for name in audit.NEEDED-{'CONFIG.json','MODEL_LOCK.json','MODEL_MANIFEST.json','cases.json','controls.json','PRIOR_CLAIMS.json','contract.py','SOURCE_MANIFEST.json'}:
        (base/name).write_text('Synthetic frozen source\n')
    frozen={str(p.relative_to(base)):audit.sha(p) for p in base.rglob('*') if p.is_file()}
    dump(base/'FREEZE.json',dict(frozen_utc=iso(-3600),sha256=frozen))
    primary,inventories=answer_maps(cases,controls);by_id={c['request_id']:c for c in cases};by_control={c['request_id']:c for c in controls}
    order=audit.order_for(cases,controls);stamps=[stamp(3)];entries=[]
    dump(out/'WARMUP.json',make_raw('warm',audit.WARM_PROMPT,'{"verdict":"insufficient","evidence":[]}',32,audit.SCHEMA,1))
    for i,key in enumerate(order):
        t=5+i*3;case_id=key[2:];case=by_id[case_id]
        phase='primary' if key.startswith('p_') else 'inventory';cap=256 if phase=='primary' else 384
        raw=make_raw(key,audit.prompt_for(case,constants,phase),primary[case_id] if phase=='primary' else inventories[case_id],cap,audit.SCHEMA if phase=='primary' else audit.INVENTORY_SCHEMA,t)
        dump(out/(key+'.json'),raw);before,after=stamp(t-.1),stamp(t+1.1)
        stamps.extend([before,raw['started_stamp'],raw['finished_stamp'],after])
        entries.append(dict(request_id=key,phase=phase,case_id=case_id,api_completed=True,raw_file=key+'.json',
                            observed_context_margin=4096-100-cap,output_tokens=10,done_reason='stop',completion_s=.9,
                            collector_duration=audit.duration(raw['started_stamp'],raw['finished_stamp']),
                            phase_duration=audit.duration(before,after)))
    stamps.append(stamp(222));stage=dict(part='collection',candidate=audit.MODEL,planned=48,status='completed',
             started_utc=iso(0),finished_utc=iso(225),requests=entries,completed_requests=48,
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
        source_freeze_sha256=audit.sha(base/'FREEZE.json'),planned_requests=48,scored_requests=48,stages=[stage]))
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
        self.assertEqual(r['counts']['raw_offered'],48);self.assertEqual(r['quality_summary']['inventory_schema_valid'],24)
        self.assertEqual(r['quality_summary']['automatic_correct'],24)
        self.assertEqual(r['format_variants']['decision_mismatches'],[])
    def test_inventory_exact_prompt_binding(self):
        key='i_'+self.cases[0]['request_id']
        self.edit(key+'.json',lambda r:r['requests'][0].update(request_prompt=r['requests'][0]['request_prompt']+' '))
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertTrue(any('binding differs' in f for f in r['faults']))
        self.assertEqual(r['counts']['raw_offered'],48)
    def test_inventory_is_blind_to_gold_and_candidate(self):
        key='i_'+self.cases[0]['request_id'];raw=json.loads((self.out/(key+'.json')).read_text())
        prompt=raw['requests'][0]['request_prompt']
        self.assertNotIn('Synthetic relation',prompt);self.assertNotIn('Synthetic support',prompt)
        self.assertNotIn('Proposed answer:',prompt)
    def test_missing_capture_keeps_48_planned(self):
        (self.out/('i_'+self.cases[0]['request_id']+'.json')).unlink();r=self.run_audit()
        self.assertEqual(r['counts']['planned'],48);self.assertEqual(r['counts']['raw_offered'],47)
        self.assertFalse(r['qualified']);self.assertEqual(len(r['missing_ids']),1)
    def test_orphan_postflight_abort_retained(self):
        self.edit('STAGE.json',lambda s:(s.update(status='aborted'),s['requests'].pop()))
        r=self.run_audit();self.assertEqual(r['counts']['raw_offered'],48);self.assertEqual(len(r['orphan_raw_ids']),1)
        self.assertFalse(r['data_complete_valid'])
    def test_transport_fault_does_not_become_acceptance(self):
        key='i_'+self.cases[0]['request_id']
        self.edit(key+'.json',lambda r:r['requests'][0].update(completed=False,error='timeout'))
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertEqual(r['counts']['api_completed'],47)
        self.assertEqual(r['quality_summary']['inventory_schema_valid'],23)
    def test_extra_raw_preserved(self):
        key='p_'+self.cases[0]['request_id'];(self.out/'orphan.json').write_bytes((self.out/(key+'.json')).read_bytes())
        r=self.run_audit();self.assertEqual(r['counts']['raw_offered'],49);self.assertFalse(r['qualified'])
    def test_inventory_token_cap(self):
        key='i_'+self.cases[0]['request_id']
        def mutate(raw):
            row=raw['requests'][0];row['final']['eval_count']=385;row['chunks'][-1]['data']['eval_count']=385
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
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertEqual(r['counts']['raw_offered'],48)
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
        r=self.run_audit();self.assertFalse(r['qualified']);self.assertEqual(r['counts']['raw_offered'],48)
    def test_model_thinking_is_invalid_collection(self):
        key='p_'+self.cases[0]['request_id']
        self.edit(key+'.json',lambda r:r['requests'][0]['chunks'][0]['data'].update(thinking='unexpected'))
        self.assertFalse(self.run_audit()['data_complete_valid'])
    def test_gold_component_inconsistent_with_whole(self):
        jobs=json.loads((self.base/'cases.json').read_text());jobs[0]['components'][0]['label']='insufficient'
        dump(self.base/'cases.json',jobs)
        r=self.run_audit();self.assertFalse(r['qualified'])
        self.assertTrue(any('component relation' in f for f in r['faults']))
    def test_supported_component_overlap_rejected_even_with_consistent_whole_gold(self):
        jobs=json.loads((self.base/'cases.json').read_text())
        case=next(c for c in jobs if c['label']=='supported')
        case['components'][1]['support']=[['D1']]
        case['acceptable_evidence']=[['D1']];case['relevant_evidence']=['D1']
        dump(self.base/'cases.json',jobs)
        result=self.run_audit()
        self.assertFalse(result['data_complete_valid'])
        self.assertTrue(any('genuinely distinct premises' in f for f in result['faults']))
    def test_supported_component_strict_subset_rejected(self):
        jobs=json.loads((self.base/'cases.json').read_text())
        case=next(c for c in jobs if c['label']=='supported')
        case['components'][1]['support']=[['D1','D2']]
        dump(self.base/'cases.json',jobs)
        result=self.run_audit()
        self.assertTrue(any('genuinely distinct premises' in f for f in result['faults']))
    def test_inventory_must_precede_every_primary(self):
        self.edit('STAGE.json',lambda stage:stage['requests'].reverse())
        self.assertFalse(self.run_audit()['data_complete_valid'])


if __name__=='__main__':unittest.main()

