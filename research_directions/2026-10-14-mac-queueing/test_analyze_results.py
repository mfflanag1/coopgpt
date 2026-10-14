"""Synthetic fixtures and mutations; no GPU execution or collector imports."""
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
import analyze_results as a

PLAN = json.loads(Path(__file__).with_name('PLAN.json').read_text())
HASHES = {n:a.expected_hash(n) for n in (256,512,1024)}


def native_window(cap=1,rate=100,service=.005):
    def row(jid,n,kind,offer,admit):
        submit = admit+.0002; completed = admit+.0004; validated = admit+service; release = validated+.0001
        return {'id':jid,'n':n,'kind':kind,'planned_offer_s':offer if kind=='measured' else 0,
                'deadline_s':offer+.1 if kind=='measured' else 0,'status':'passed','passed':True,
                'admission_sequence':jid,'observed_enqueue_s':offer+.001,'admission_s':admit,
                'encode_done_s':admit+.0001,'submit_s':submit,'gpu_completion_observed_s':completed,
                'validated_completion_s':validated,'resource_release_s':release,
                'row_bytes':4*n,'buffer_payload_bytes':12*n*n,'buffer_length_bytes':12*n*n,
                'buffer_allocated_bytes':12*n*n,'cpu_reference_payload_bytes':4*n*n,'cpu_hash_scratch_bytes':4*n,
                'device_allocated_before_buffers_sample':0,'device_allocated_with_buffers_sample':12*n*n,
                'device_allocated_after_release_sample':0,'gpu_start_time':100+submit,
                'gpu_end_time':100+completed,'gpu_interval_seconds':(100+completed)-(100+submit),
                'command_buffer_status':4,'gpu_output_sha256':HASHES[n],'cpu_reference_sha256':HASHES[n],
                'check':{'compared_elements':n*n,'mismatch_count':0,'nonfinite_count':0,
                         'max_abs_error':0,'max_abs_finite_error':0}}
    jobs=[]; available=[0]*cap
    for i,n in enumerate(PLAN['dimensions']):
        worker=min(range(cap),key=lambda k:available[k]); admit=max(i/rate+.001,available[worker])
        r=row(i,n,'measured',i/rate,admit); jobs.append(r); available[worker]=r['resource_release_s']
    warmups=[row(i,n,'warmup',0,i*.02) for i,n in enumerate((256,512,1024))]
    events=[]
    for r in jobs:
        for kind,key,priority in [('enqueue','observed_enqueue_s',1),('admit','admission_s',2),('release','resource_release_s',0)]:
            events.append((r[key],priority,r['id'],kind))
    active=0; queued=0; result=[]; maximum=0
    for t,_,jid,kind in sorted(events):
        if kind=='enqueue': queued+=1
        elif kind=='admit': queued-=1; active+=1
        else: active-=1
        maximum=max(maximum,active)
        result.append({'sequence':len(result),'job_id':jid,'kind':kind,'time_s':t,'active_count':active,'queue_count':queued})
    return {'schema_version':1,'protocol_id':'mac-mps-queueing-v1','concurrency':cap,'rate':rate,
            'gate_passed':True,'cpu_self_test_passed':True,'device_name':'Fixture Mac GPU','has_unified_memory':True,
            'max_buffer_length':CAP,'recommended_max_working_set_size':1024**3,
            'per_job_explicit_byte_cap':CAP,'active_explicit_byte_cap':CAP*cap,
            'epoch_uptime_ns':2_000_000_000,'warmup_epoch_uptime_ns':1_000_000_000,
            'started_at':'2026-10-14T00:00:00Z','completed_at':'2026-10-14T00:00:10Z',
            'jobs':jobs,'warmups':warmups,'events':result,'max_active_observed':maximum,
            'window_end_s':max(r['resource_release_s'] for r in jobs)+.001}


CAP=a.CAP


class MathematicsAndGates(unittest.TestCase):
    def test_independent_known_digest(self):
        self.assertEqual(a.expected_hash(4),'3528d12e2f4ce4f09b261bebe1f87a9bf13961f72a9f8fb5e8b10517db08d24a')
        self.assertEqual(HASHES[1024],'c0da4554c43e4a77e27df3b25883e7bc74a427df2e74412ab017f6fb109e0c91')

    def test_nearest_rank_and_even_median(self):
        self.assertEqual(a.quantile95(list(range(1,61))),57)
        self.assertEqual(a.summary([1,2,100,101])['median'],51)

    def test_frozen_cohort_changes_rejected(self):
        a.check_plan(PLAN)
        for key,value in [('primary_median_ratio_limit',.95),('deadline_seconds',.2),('dimensions',[256]*60)]:
            altered=copy.deepcopy(PLAN);altered[key]=value
            with self.assertRaises(ValueError):a.check_plan(altered)

    def test_power_known_source_and_fraction(self):
        self.assertEqual(a.power({'returncode':0,'stdout':"Now drawing from 'Battery Power'\n-InternalBattery-0 48%;"}),
                         {'source':'Battery Power','battery_percent':48})
        for record in ({'returncode':1,'stdout':"Now drawing from 'AC Power'"},
                       {'returncode':0,'stdout':"Now drawing from 'AC Power'\nNow drawing from 'Battery Power'"}):
            self.assertIsNone(a.power(record)['source'])

    def test_gate_thresholds_and_invalidity_are_not_overridden(self):
        windows=[]
        for w in PLAN['windows']:
            ratio=.90 if w['rate']==100 else 1.10 if w['rate']==10 else 1
            p95=1 if w['concurrency']==1 else ratio
            windows.append(dict(w,latency_complete=True,nominal_offer_latency_seconds={'p95':p95},
                                producer_lateness_seconds={'count':60,'p95':.01},on_time_successes=60,
                                power=[{'source':'AC Power'},{'source':'AC Power'}]))
        result=a.paired_gates(windows,PLAN,True)
        self.assertTrue(result['promotion_gate_passed'])
        self.assertFalse(a.paired_gates(windows,PLAN,False)['promotion_gate_passed'])
        windows[0]['producer_lateness_seconds']['p95']=.010000001
        self.assertFalse(a.paired_gates(windows,PLAN,True)['validity_passed'])
        windows[0]['producer_lateness_seconds']['p95']=.01
        for w in windows:
            if w['rate']==100 and w['concurrency']==2:w['nominal_offer_latency_seconds']['p95']=.900000001
        self.assertFalse(a.paired_gates(windows,PLAN,True)['promotion_gate_passed'])


class WindowMutations(unittest.TestCase):
    def run_audit(self,raw,cap=1):
        w=next(w for w in PLAN['windows'] if w['round']==1 and w['rate']==100 and w['concurrency']==cap)
        return a.audit_window(raw,w,PLAN,HASHES,{'Fixture Mac GPU'})

    def test_valid_window_and_actual_two_active_slots(self):
        self.assertTrue(self.run_audit(native_window())['checks_passed'])
        result=self.run_audit(native_window(cap=2,service=.015),cap=2)
        self.assertTrue(result['checks_passed'],result['errors'])
        self.assertEqual(result['max_active_from_events'],2)

    def test_hash_count_gate_and_nominal_schedule_mutations(self):
        base=native_window()
        mutations=[lambda r:r['jobs'][17].update(gpu_output_sha256='0'*64),
                   lambda r:r['jobs'][17].update(cpu_reference_sha256='0'*64),
                   lambda r:r['jobs'][17]['check'].update(compared_elements=1),
                   lambda r:r['jobs'][17]['check'].update(mismatch_count=False),
                   lambda r:r['jobs'][17].update(planned_offer_s=.171),
                   lambda r:r['jobs'][17].update(deadline_s=.4),
                   lambda r:r.update(gate_passed=False),lambda r:r['warmups'].pop()]
        for mutate in mutations:
            raw=copy.deepcopy(base);mutate(raw)
            self.assertFalse(self.run_audit(raw)['checks_passed'])

    def test_fifo_release_before_cleanup_and_count_tampering(self):
        base=native_window()
        mutations=[lambda r:r['events'][1].update(job_id=1),
                   lambda r:r['events'][1].update(active_count=2),
                   lambda r:r['events'][1].update(queue_count=4),
                   lambda r:r['events'][1].update(sequence=99),
                   lambda r:r['jobs'][0].update(resource_release_s=.001),
                   lambda r:r['events'].pop()]
        for mutate in mutations:
            raw=copy.deepcopy(base);mutate(raw)
            self.assertFalse(self.run_audit(raw)['checks_passed'])

    def test_missing_jobs_do_not_shrink_planned_denominator(self):
        raw=native_window();raw['jobs'].pop()
        result=self.run_audit(raw)
        self.assertFalse(result['checks_passed']);self.assertEqual(result['planned_jobs'],60)
        self.assertEqual(result['on_time_successes'],59);self.assertEqual(result['on_time_fraction'],59/60)

    def test_late_correct_jobs_count_against_deadline(self):
        result=self.run_audit(native_window(service=.02))
        self.assertTrue(result['checks_passed'],result['errors'])
        self.assertLess(result['on_time_successes'],60)
        self.assertEqual(result['independently_correct_jobs'],60)


class CampaignFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.capture=self.root/'capture';self.capture.mkdir()
        for name in a.REQUIRED:(self.root/name).write_text('fixture '+name)
        self.save(self.root/'PLAN.json',PLAN)
        self.binary=self.root/'binary';self.binary.write_bytes(b'fixture only never executed')
        self.freeze={'source_sha256':{name:a.sha(self.root/name) for name in a.REQUIRED},'binary_sha256':a.sha(self.binary)}
        self.save(self.root/'DESIGN_FREEZE.json',self.freeze);frozen=a.sha(self.root/'DESIGN_FREEZE.json')
        self.save(self.capture/'INVENTORY.json',{'capacity_kind':'hardware_totals','placement_ready':False,
                  'hardware':{'platform':'Darwin','physical_ram_bytes':{'status':'observed','value':8*1024**3},
                              'gpu_inventory':{'status':'observed','devices':[{'model':'Fixture Mac GPU'}]}}})
        self.campaign={'schema_version':1,'started_utc':'2026-10-14T00:00:00Z','finished_utc':'2026-10-14T00:04:00Z',
                       'monotonic_duration_seconds':240,'campaign_timeout_seconds':600,'plan_sha256':a.sha(self.root/'PLAN.json'),
                       'freeze_sha256':frozen,'source_changed':False,'stop_reason':None,'unrun_window_ids':[],'windows':[]}
        for w in PLAN['windows']:
            folder_name=f"w{w['index']:02d}_{w['window_id']}";folder=self.capture/folder_name;folder.mkdir()
            raw=native_window(cap=w['concurrency'],rate=w['rate'],service=.004 if w['concurrency']==2 else .005)
            self.save(folder/'RAW.json',raw)
            start=datetime(2026,10,14,tzinfo=timezone.utc)+timedelta(seconds=10*(w['index']-1))
            meta={key:w[key] for key in ('window_id','round','rate','concurrency')}
            meta.update(freeze_sha256=frozen,source_changed=False,returncode=0,process_status='completed',
                        raw_output_present=True,raw_gate_passed=True,independent_window_checks_passed=True,
                        independent_window_errors=[],diagnostic_interrupted=False,started_utc=start.isoformat(),
                        finished_utc=(start+timedelta(seconds=raw['window_end_s'])).isoformat(),
                        process_elapsed_seconds=raw['window_end_s'],timeout_seconds=90,
                        command=[str(self.binary),'--concurrency',str(w['concurrency']),'--rate',str(w['rate']),'--output',str(folder/'RAW.json')],
                        before={'batt':{'returncode':0,'stdout':"Now drawing from 'AC Power'\n100%;"}},
                        after={'batt':{'returncode':0,'stdout':"Now drawing from 'AC Power'\n100%;"}})
            self.save(folder/'EXECUTION.json',meta)
            item={key:w[key] for key in ('window_id','index','round','rate','concurrency')}
            item.update(folder=folder_name,status='completed',returncode=0);self.campaign['windows'].append(item)
        self.save(self.capture/'CAMPAIGN.json',self.campaign)

    def save(self,path,value):path.write_text(json.dumps(value))
    def audit(self):return a.analyze(self.root,self.capture,self.binary)

    def test_complete_fixed_campaign(self):
        result=self.audit()
        self.assertTrue(result['validity_passed'],result['errors'])
        self.assertTrue(result['promotion_gate_passed'])
        self.assertEqual(result['independently_correct_measured_jobs'],1440)
        self.assertEqual(result['independently_correct_warmups'],72)
        self.assertEqual(len(result['pairs']),12)

    def test_missing_window_unknown_power_and_frozen_source_rejected(self):
        first=self.campaign['windows'][0]
        path=self.capture/first['folder']/'EXECUTION.json';meta=a.load(path);meta['after']['batt']['returncode']=1;self.save(path,meta)
        self.assertFalse(self.audit()['validity_passed'])
        meta['after']['batt']['returncode']=0;self.save(path,meta)
        last=self.campaign['windows'].pop();self.campaign['unrun_window_ids']=[last['window_id']]
        self.campaign['stop_reason']='synthetic interruption';self.save(self.capture/'CAMPAIGN.json',self.campaign)
        result=self.audit();self.assertFalse(result['validity_passed']);self.assertEqual(result['planned_measured_jobs'],1440)
        self.assertEqual(result['reported_measured_jobs'],1380)
        (self.root/'queue_benchmark.swift').write_text('changed')
        self.assertTrue(any('Frozen source mismatch' in e for e in self.audit()['errors']))

    def test_duplicate_json_is_not_accepted(self):
        (self.capture/'CAMPAIGN.json').write_text('{"windows": [], "windows": []}')
        self.assertFalse(self.audit()['validity_passed'])


if __name__=='__main__':unittest.main()
