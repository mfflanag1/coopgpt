"""Offline synthetic regressions; no collector modules or hardware imported."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import analyze as audit


def save(path,value):
    path.write_text(json.dumps(value,sort_keys=True)+'\n')


def stamp(ns):
    return dict(monotonic_before_ns=ns,monotonic_after_ns=ns+100,wall_ns=ns+10**15+50)


def raw(request_id,text,model,ns,prompt='warm',options=None,format_=None):
    final=dict(model=model,done=True,response='',prompt_eval_count=100,eval_count=30,
               total_duration=700000000,load_duration=1000,prompt_eval_duration=200000000,
               eval_duration=499999000,done_reason='stop')
    row=dict(request_id=request_id,arrival_offset_s=0,dispatch_offset_s=.01,
             first_content_offset_s=.1,terminal_offset_s=.8,http_status=200,
             completed=True,error=None,deadline_exceeded=False,request_prompt=prompt,
             request_model=model,request_options=options or {},request_format=format_,
             chunks=[dict(offset_s=.1,data=dict(response=text,done=False,model=model)),
                     dict(offset_s=.8,data=copy.deepcopy(final))],final=final)
    start,end=stamp(ns),stamp(ns+10**9)
    return dict(started_stamp=start,finished_stamp=end,epoch_monotonic_ns=start['monotonic_after_ns'],
                elapsed_seconds=(end['monotonic_before_ns']-start['monotonic_after_ns'])/10**9,
                requests=[row])


class Fixture:
    def __init__(self,root):
        self.base=root/'source';self.capture=root/'capture'
        self.base.mkdir();self.capture.mkdir()
        self.config=dict(model='llama3.2:3b',digest='digest',context=4096,
                         options=dict(num_ctx=4096,num_predict=192,temperature=0,seed=0),
                         allow_battery_quality=True,server_settings_common={'OLLAMA_CONTEXT_LENGTH':'4096'},
                         lock=dict(binary_sha256='binary',manifest_sha256='manifest'))
        self.instruction='Select KEEP rows.\n';self.example='Example only:\nR9001 value=123 flag=KEEP\n'
        self.jobs={}
        for part,repeats,prefix,delta in [('development',1,'dev',0),('confirmation',3,'confirm',1)]:
            jobs=[]
            for repeat in range(repeats):
                for n in (32,96,192):
                    for k in (4,12,24):
                        rows=[dict(id=f'R{i:04d}',value=f'{(100+i+delta+repeat)%1000:03d}',flag='KEEP' if i<=k else 'DROP') for i in range(1,n+1)]
                        jobs.append(dict(request_id=f'{prefix}-{len(jobs)+1:03d}',input_rows=n,keep_count=k,
                                         max_output_tokens=audit.CAPS[k],rows=rows,expected=audit.gold(rows)))
            self.jobs[part]=jobs;save(self.base/(part+'.json'),jobs)
        save(self.base/'CONFIG.json',self.config)
        (self.base/'design.py').write_text('INSTRUCTION = '+repr(self.instruction)+'\nEXAMPLE = '+repr(self.example)+'\n')
        for name in ('client.py','calibrate.py','server_control.py','clock_bridge.py','PROTOCOL.txt'):
            (self.base/name).write_text('synthetic test source only\n')
        self.freeze()
        self.stage_names=[]

    def freeze(self):
        save(self.base/'FREEZE.json',{'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.base.iterdir() if p.is_file() and p.name!='FREEZE.json'}})

    def prompt(self,job,candidate):
        return (self.instruction+(self.example if candidate=='B' else '')+'Output schema: '+json.dumps(audit.SCHEMA,separators=(',',':'))+'\nInput records:\n'+'\n'.join(f"{r['id']} value={r['value']} flag={r['flag']}" for r in job['rows'])+'\nJSON answer:')

    def stage(self,part,candidate,bad_indices=()):
        name=part+'-'+candidate;path=self.capture/name;path.mkdir();jobs=self.jobs[part]
        seq=len(self.stage_names);self.stage_names.append(name)
        ns=(1000+seq*1000)*10**9;stamps=[stamp(ns)];entries=[]
        for i,job in enumerate(jobs):
            t=ns+(3*i+1)*10**9
            text=json.dumps(job['expected']) if i not in bad_indices else '{"records":[]}'
            data=raw(job['request_id'],text,self.config['model'],t+10**8,self.prompt(job,candidate),
                     dict(self.config['options'],num_predict=job['max_output_tokens']),audit.SCHEMA)
            save(path/(job['request_id']+'.json'),data)
            stamps.extend([stamp(t),data['started_stamp'],data['finished_stamp'],stamp(t+2*10**9)])
            entries.append(dict(request_id=job['request_id'],input_rows=job['input_rows'],keep_count=job['keep_count'],
                                api_completed=True,quality_pass=i not in bad_indices,observed_context_margin=4096-100-job['max_output_tokens'],
                                output_tokens=30,raw_file=job['request_id']+'.json'))
        stamps.append(stamp(ns+(3*len(jobs)+3)*10**9))
        stage=dict(candidate=candidate,planned=len(jobs),status='completed',requests=entries,
                   started_utc=f'2026-01-01T00:{seq*2:02d}:00+00:00',finished_utc=f'2026-01-01T00:{seq*2+1:02d}:00+00:00',
                   quality_count=len(jobs)-len(bad_indices),gate_passed=not bad_indices,
                   clock_stamps=stamps,clock_diagnostics=audit.clock_check(stamps))
        save(path/'STAGE.json',stage)
        save(path/'WARMUP.json',raw('warm','ready',self.config['model'],ns-2*10**9))
        state=dict(power="Now drawing from 'Battery Power'\n -InternalBattery-0 (id=REDACTED) 80%; discharging;",power_source='Battery Power',battery_percent=80,external_power_connected=False,
                   thermal='No thermal warning level has been recorded\nNo performance warning level has been recorded')
        loaded=dict(name=self.config['model'],digest=self.config['digest'],context_length=4096,size_vram=2000000000)
        meta=dict(status='completed',errors=[],clean_unload_verified=True,loaded_after_unload={'models':[]},dedicated_server_returncode=-15,
                  model=self.config['model'],context=4096,parallel=1,runtime_parallel_values=[1],version={'version':'0.20.0'},
                  model_tag={'name':self.config['model'],'digest':self.config['digest']},options=self.config['options'],
                  server_settings=dict(self.config['server_settings_common'],OLLAMA_NUM_PARALLEL='1'),allow_battery_quality=True,
                  lock_verification=self.config['lock'],dedicated_server_pid=12345,dedicated_process_group=12345,
                  loaded_checks=[{'response':{'models':[loaded]}} for _ in range(3)],before=state,after=state,
                  original_endpoint_idle_before=True,original_endpoint_idle_after=True,
                  host_checks=[dict(phase=prefix+job['request_id'],passed=True,original_endpoint_idle=True,state=state) for job in jobs for prefix in ('before_','after_')])
        save(path/'SERVER_CONTROL.json',meta);(path/'SERVER.log').write_text('n_seq_max = 1\n')
        return path

    def campaign(self,selected='A',qualified=True,status='completed'):
        campaign=dict(status=status,selected=selected,qualified=qualified,
                      source_freeze_sha256=hashlib.sha256((self.base/'FREEZE.json').read_bytes()).hexdigest(),
                      stages=[json.loads((self.capture/name/'STAGE.json').read_text()) for name in self.stage_names])
        save(self.capture/'CAMPAIGN.json',campaign)

    def passing(self):
        self.stage('development','A');self.stage('confirmation','A');self.campaign()

    def change(self,relative,fn):
        path=self.capture/relative;value=json.loads(path.read_text());fn(value);save(path,value)

    def analyze(self):
        return audit.analyze(self.base,self.capture)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.fx=Fixture(Path(self.tmp.name))

    def test_complete_confirmation_gate(self):
        self.fx.passing();out=self.fx.analyze()
        self.assertTrue(out['qualified'],out['faults']);self.assertTrue(out['data_complete_valid'])
        self.assertEqual(out['counts']['all']['raw_offered'],36)
        self.assertEqual(out['counts']['confirmation']['exact_quality'],27)

    def test_strict_answer_contract(self):
        gold={'records':[{'id':'R0001','value':'123'},{'id':'R0002','value':'456'}]}
        self.assertTrue(audit.score_output('{"records":[{"value":"123","id":"R0001"},{"id":"R0002","value":"456"}]}',gold))
        bad=['{"records":[],"records":[]}','{"records":[{"id":"R0001","value":123}]}',
             json.dumps({'records':list(reversed(gold['records']))}),json.dumps(gold)+' trailing',
             json.dumps({'records':gold['records'],'extra':1}),'{"records":NaN}',
             '{"records":[{"id":"R0001","value":"123","id":"R0001"}]}',
             json.dumps({'records':[{'id':'R0001','value':'123','extra':0}]}),
             json.dumps({'records':[{'id':'R0001'}]})]
        for text in bad:
            with self.subTest(text=text):self.assertFalse(audit.score_output(text,gold))

    def test_example_keep_excluded_from_actual_input(self):
        job=self.fx.jobs['development'][0]
        rows=audit.prompt_rows(self.fx.prompt(job,'B'))
        self.assertEqual(rows,job['rows']);self.assertNotIn('R9001',[r['id'] for r in rows])

    def test_both_development_fail_is_valid_completed_no_confirmation(self):
        self.fx.stage('development','A',(0,));self.fx.stage('development','B',(1,));self.fx.campaign(None,False)
        out=self.fx.analyze();self.assertTrue(out['data_complete_valid'],out['faults']);self.assertFalse(out['qualified'])
        self.assertEqual(out['counts']['confirmation']['raw_offered'],0);self.assertEqual(out['counts']['confirmation']['planned'],0)

    def test_b_selected_only_after_a_development_fails(self):
        self.fx.stage('development','A',(0,));self.fx.stage('development','B');self.fx.stage('confirmation','B');self.fx.campaign('B',True)
        out=self.fx.analyze();self.assertTrue(out['qualified'],out['faults']);self.assertEqual(out['counts']['all']['raw_offered'],45)

    def test_confirmation_failure_cannot_fallback(self):
        self.fx.stage('development','A');self.fx.stage('confirmation','A',(0,));self.fx.stage('development','B');self.fx.campaign('A',False)
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertIn('development-B',out['extra_stages'])

    def test_missing_confirmation_not_zero_of_twenty_seven_observed(self):
        self.fx.stage('development','A');self.fx.campaign('A',False,'aborted')
        out=self.fx.analyze();self.assertFalse(out['data_complete_valid']);self.assertEqual(out['missing_stages'],['confirmation-A'])
        self.assertEqual(out['counts']['confirmation']['raw_offered'],0)

    def test_reported_score_cannot_override_raw_wrong_answer(self):
        self.fx.passing()
        self.fx.change('confirmation-A/confirm-001.json',lambda x:x['requests'][0]['chunks'][0]['data'].update(response='{"records":[]}'))
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertEqual(out['counts']['confirmation']['exact_quality'],26)
        self.assertTrue(any('summary quality_pass differs' in f for f in out['faults']))

    def test_postflight_abort_keeps_orphan_raw_in_offered_and_api_counts(self):
        self.fx.stage('development','A')
        path=self.fx.capture/'development-A'
        for job in self.fx.jobs['development'][1:]: (path/(job['request_id']+'.json')).unlink()
        self.fx.change('development-A/STAGE.json',lambda x:x.update(status='aborted',requests=[],gate_passed=False))
        self.fx.campaign(None,False,'aborted')
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertEqual(out['counts']['all']['raw_offered'],1)
        self.assertEqual(out['counts']['all']['api_completed'],1);self.assertEqual(out['counts']['all']['exact_quality'],1)
        self.assertEqual(out['stages'][0]['orphan_raw_ids'],['dev-001'])

    def test_incomplete_raw_checkpoint_not_certified(self):
        self.fx.passing()
        self.fx.change('development-A/dev-001.json',lambda x:x.update(collection_incomplete=True))
        self.assertFalse(self.fx.analyze()['qualified'])

    def test_context_failure_blocks_even_exact_answer(self):
        self.fx.passing()
        def change(x):
            x['requests'][0]['final']['prompt_eval_count']=4000
            x['requests'][0]['chunks'][-1]['data']['prompt_eval_count']=4000
        self.fx.change('development-A/dev-001.json',change)
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertEqual(out['counts']['all']['exact_quality'],36)

    def test_saved_schema_and_payload_required(self):
        for key,value in [('request_format',{}),('request_prompt',None),('request_model','other')]:
            with self.subTest(key=key):
                with tempfile.TemporaryDirectory() as d:
                    fx=Fixture(Path(d));fx.passing()
                    fx.change('development-A/dev-001.json',lambda x:x['requests'][0].update({key:value}))
                    self.assertFalse(fx.analyze()['qualified'])

    def test_clock_offset_and_raw_epoch_independently_checked(self):
        self.fx.passing()
        self.fx.change('development-A/dev-001.json',lambda x:x.update(epoch_monotonic_ns=1))
        self.fx.change('confirmation-A/STAGE.json',lambda x:x['clock_stamps'][-1].update(wall_ns=x['clock_stamps'][-1]['wall_ns']+10**9))
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertTrue(any('raw epoch differs' in f for f in out['faults']))
        self.assertTrue(any('stage clock diagnostics fail' in f for f in out['faults']))

    def test_cleanup_failure_blocks_quality_gate(self):
        self.fx.passing()
        self.fx.change('development-A/SERVER_CONTROL.json',lambda x:x.update(clean_unload_verified=False,forced_stop=True))
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertTrue(any('clean unload' in f for f in out['faults']))

    def test_battery_metadata_independently_reparsed(self):
        self.fx.passing()
        self.fx.change('development-A/SERVER_CONTROL.json',lambda x:x['host_checks'][0]['state'].update(power="Now drawing from 'Battery Power'\n -InternalBattery-0 (id=REDACTED) 59%; discharging;"))
        self.assertFalse(self.fx.analyze()['qualified'])

    def test_source_freeze_mismatch(self):
        self.fx.passing();(self.fx.base/'PROTOCOL.txt').write_text('changed')
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertTrue(any('source freeze mismatch' in f for f in out['faults']))

    def test_failed_transport_stays_in_denominator(self):
        self.fx.passing()
        self.fx.change('development-A/dev-001.json',lambda x:x['requests'][0].update(completed=False,error='timeout'))
        out=self.fx.analyze();self.assertEqual(out['counts']['all']['raw_offered'],36);self.assertEqual(out['counts']['all']['api_completed'],35)
        self.assertFalse(out['qualified'])

    def test_duplicate_raw_job_retained_and_rejected(self):
        self.fx.passing();p=self.fx.capture/'development-A'
        (p/'duplicate.json').write_bytes((p/'dev-001.json').read_bytes())
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertEqual(out['counts']['all']['raw_offered'],37)
        self.assertTrue(any('duplicate/non-string raw IDs' in f for f in out['faults']))

    def test_stage_order_violation(self):
        self.fx.passing()
        self.fx.change('confirmation-A/STAGE.json',lambda x:x.update(started_utc='2025-01-01T00:00:00+00:00'))
        out=self.fx.analyze();self.assertFalse(out['qualified']);self.assertTrue(any('chronology' in f for f in out['faults']))

if __name__=='__main__':unittest.main()
