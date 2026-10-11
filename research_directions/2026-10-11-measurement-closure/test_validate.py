"""Hardware-free evidence-validator tests; generated data are never measurements."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from validate import canonical_sha, validate_bundle, compare_bundles

class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def fixture(self,name='a',evidence='synthetic_fixture',gpu='GPU-A',gpu_model='NVIDIA-A'):
        path=self.root/name;path.mkdir()
        trace=[{'request_id':'r1','prompt':'alpha','arrival_offset_s':0.0},
               {'request_id':'r2','prompt':'beta','arrival_offset_s':1.0}]
        raw=''.join(json.dumps(r)+'\n' for r in trace).encode();(path/'trace.jsonl').write_bytes(raw)
        config={'config_id':name,'workload_provenance':'fixed unit-test fixture, never measurement',
          'model':{'id':'pinned-model','revision':'a'*40,'tokenizer_revision':'b'*40,'dtype':'float16','quantization':'none'},
          'engine':{'name':'vllm','version':'0.11.0','container_digest':'sha256:'+'c'*64,
                    'launch_config':{'tensor_parallel_size':1,'pipeline_parallel_size':1,'enable_prefix_caching':False,'cpu_offload_gb':0,'speculative_config':None,'enable_chunked_prefill':False,'max_model_len':2048}},
          'gpu_uuids':[gpu],'server_gpu_worker_pids':{gpu:[123]},'decoding':{'temperature':0,'max_tokens':32,'seed':7,'ignore_eos':False},
          'slo':{'response_seconds':1.0,'first_content_seconds':.5}}
        run={'schema_version':1,'evidence_kind':evidence,'config':config,'config_sha256':canonical_sha(config),
             'trace_sha256':hashlib.sha256(raw).hexdigest(),'engine_probe':{'version':{'version':'0.11.0'},'models':{'data':[{'id':'pinned-model'}]},'quiescence_before':True,'quiescence_after_warmup':True,'quiescence_after_workload':True},
             'hardware':{'driver_version':'555.42','boards':[{'gpu_uuid':gpu,'name':gpu_model,'memory_total_bytes':40000000000,'power_limit_w':250}]},
             'clock':{'kind':'time.monotonic','domain':'single_local_host','unit':'seconds'},
             'windows':{'idle_before':[0.0,1.0],'workload':[1.0,3.0],'idle_after':[3.0,4.0],'total':[0.0,4.0]},
             'collector_errors':[],'warmup_ok':True,'settings':{'idle_seconds':1.0,'poll_seconds':.25,'max_gap_seconds':.3,'max_read_seconds':.01,'request_timeout_s':10.0,'drain_timeout_s':10.0,'concurrency':1}}
        requests=[]
        for i,t in enumerate((1.0,2.0)):
            requests.append({'request_id':trace[i]['request_id'],'prompt_sha256':hashlib.sha256(trace[i]['prompt'].encode()).hexdigest(),
              'scheduled_monotonic':t,'dispatch_monotonic':t+.05,'first_content_monotonic':t+.2,'last_content_monotonic':t+.6,'finish_monotonic':t+.8,
              'chunk_events':[{'received_monotonic':t+.2,'chars':6},{'received_monotonic':t+.6,'chars':4}],
              'usage':{'prompt_tokens':1,'completion_tokens':5},'finish_reason':'stop','http_status':200,'status':'ok','error':None,'output_sha256':'d'*64})
        power=[]
        for i in range(17):
            t=i*.25
            power.append({'sequence':i,'read_start_monotonic':t-.001,'read_end_monotonic':t+.001,'sample_monotonic':t,'status':'ok','readings':[{'gpu_uuid':gpu,'power_w':100.0,'cumulative_energy_j':100.0*t,'status':'ok','energy_counter_status':'ok','compute_process_status':'ok','compute_process_ids':[123]}]})
        self.write(path,'run.json',run);self.write(path,'requests.jsonl',requests);self.write(path,'power.jsonl',power)
        return path
    def write(self,path,file,data):
        (path/file).write_text(''.join(json.dumps(x)+'\n' for x in data) if file.endswith('jsonl') else json.dumps(data))
    def load(self,path,file):
        return [json.loads(x) for x in (path/file).read_text().splitlines()] if file.endswith('jsonl') else json.loads((path/file).read_text())
    def test_synthetic_never_measured_and_phases_reconcile(self):
        result=validate_bundle(self.fixture())
        self.assertTrue(result['data_quality_pass'],result['failures'])
        self.assertFalse(result['measured_data_ready']);self.assertFalse(result['deployment_gate'])
        self.assertAlmostEqual(result['energy']['total']['aggregate_board_energy_j'],400)
        self.assertEqual(result['metrics']['offered_requests'],2)
    def test_hardware_flag_still_never_deployment_or_loaded_model_proof(self):
        r=validate_bundle(self.fixture(evidence='hardware_collection'))
        self.assertTrue(r['measured_data_ready'],r['failures']);self.assertFalse(r['deployment_gate'])
        self.assertTrue(r['attestation_limits'])
    def test_failed_job_retained_denominator(self):
        p=self.fixture();r=self.load(p,'requests.jsonl');r[1].update(status='error',error='HTTP 500',http_status=500,usage=None,finish_reason=None,first_content_monotonic=None,last_content_monotonic=None,chunk_events=[],output_sha256=None)
        self.write(p,'requests.jsonl',r);v=validate_bundle(p)
        self.assertTrue(v['data_quality_pass'],v['failures']);self.assertEqual(v['metrics']['failed_requests'],1)
        self.assertEqual(v['metrics']['slo_success_fraction_of_offered'],.5)
    def test_multitoken_chunks_not_treated_as_tokens(self):
        v=validate_bundle(self.fixture());m=v['metrics']
        self.assertAlmostEqual(m['successful_inter_content_chunk_gap_seconds']['mean'],.4)
        self.assertAlmostEqual(m['successful_client_average_output_token_proxy_seconds']['mean'],.1)
        self.assertIn('not measured individual token',m['token_proxy_warning'])
    def test_missing_or_duplicate_request_rejected(self):
        for name,duplicate in [('missing',False),('duplicate',True)]:
            p=self.fixture(name);r=self.load(p,'requests.jsonl');r=[r[0],copy.deepcopy(r[0])] if duplicate else r[:1]
            self.write(p,'requests.jsonl',r);self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_telemetry_gap_rejected(self):
        p=self.fixture();rows=self.load(p,'power.jsonl');self.write(p,'power.jsonl',rows[:4]+rows[7:]);v=validate_bundle(p)
        self.assertFalse(v['data_quality_pass']);self.assertTrue(any('gap' in x for x in v['failures']))
    def test_unknown_metadata_live_mismatch_and_quiescence_rejected(self):
        p=self.fixture();r=self.load(p,'run.json');r['config']['model']['revision']='unknown';r['config_sha256']=canonical_sha(r['config']);r['engine_probe']['version']['version']='0.10.0';r['engine_probe']['quiescence_after_workload']=False
        self.write(p,'run.json',r);v=validate_bundle(p)
        self.assertFalse(v['data_quality_pass']);self.assertTrue(any('quiescence_after_workload' in x for x in v['failures']))
    def test_window_omitting_drain_rejected(self):
        p=self.fixture();r=self.load(p,'run.json');r['windows']['workload'][1]=2.5;r['windows']['idle_after'][0]=2.5
        self.write(p,'run.json',r);v=validate_bundle(p)
        self.assertFalse(v['data_quality_pass']);self.assertTrue(any('terminal outcome outside' in x for x in v['failures']))
    def test_missing_usage_fails_quality_without_losing_offered_count(self):
        p=self.fixture();r=self.load(p,'requests.jsonl');r[0]['usage']=None;self.write(p,'requests.jsonl',r);v=validate_bundle(p)
        self.assertFalse(v['data_quality_pass']);self.assertEqual(v['metrics']['offered_requests'],2)
    def test_trace_and_prompt_hashes_checked(self):
        p=self.fixture();r=self.load(p,'trace.jsonl');r[0]['prompt']='changed';self.write(p,'trace.jsonl',r);v=validate_bundle(p)
        self.assertFalse(v['data_quality_pass']);self.assertTrue(any('trace_sha256 mismatch'==x for x in v['failures']))
    def test_pair_requires_same_model_and_trace(self):
        a=self.fixture('a',gpu='GPU-A',gpu_model='A100');b=self.fixture('b',gpu='GPU-B',gpu_model='H100')
        good=compare_bundles(a,b);self.assertTrue(good['pair_data_quality_pass'],good['pair_failures']);self.assertFalse(good['paired_measured_data_ready'])
        r=self.load(b,'run.json');r['config']['model']['revision']='e'*40;r['config_sha256']=canonical_sha(r['config']);self.write(b,'run.json',r)
        bad=compare_bundles(a,b);self.assertFalse(bad['pair_data_quality_pass']);self.assertIn('Paired model mismatch',bad['pair_failures'])
    def test_pair_requires_same_concurrency_slo_and_idle_target(self):
        for field in ('concurrency','idle_seconds','slo'):
            a=self.fixture('a_'+field,gpu='GPU-A',gpu_model='A100')
            b=self.fixture('b_'+field,gpu='GPU-B',gpu_model='H100')
            run=self.load(b,'run.json')
            if field=='slo':
                run['config']['slo']['response_seconds']=2.0
                run['config_sha256']=canonical_sha(run['config'])
            elif field=='concurrency':run['settings'][field]=2
            else:run['settings'][field]=.5
            self.write(b,'run.json',run)
            result=compare_bundles(a,b)
            self.assertTrue(result['left']['data_quality_pass'],result['left']['failures'])
            self.assertTrue(result['right']['data_quality_pass'],result['right']['failures'])
            self.assertFalse(result['pair_data_quality_pass'])
    def test_multiple_live_models_rejected(self):
        p=self.fixture();run=self.load(p,'run.json')
        run['engine_probe']['models']['data'].append({'id':'another-model'})
        self.write(p,'run.json',run)
        self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_same_hardware_uuid_change_not_new_configuration(self):
        a=self.fixture('a',gpu='GPU-A');b=self.fixture('b',gpu='GPU-B')
        v=compare_bundles(a,b);self.assertFalse(v['pair_data_quality_pass']);self.assertTrue(any('No observed hardware' in x for x in v['pair_failures']))
    def test_stuck_or_half_rate_counter_rejected(self):
        for label,factor in [('stuck',0.0),('half',0.5)]:
            p=self.fixture(label);power=self.load(p,'power.jsonl')
            for sample in power:
                sample['readings'][0]['cumulative_energy_j']=100.0+factor*100.0*sample['sample_monotonic']
            self.write(p,'power.jsonl',power)
            self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_zero_reported_power_rejected_even_with_positive_counter(self):
        p=self.fixture();power=self.load(p,'power.jsonl')
        for sample in power:sample['readings'][0]['power_w']=0.0
        self.write(p,'power.jsonl',power)
        self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_idle_process_contamination_rejected(self):
        for name,index in [('before',1),('after',15)]:
            p=self.fixture(name);power=self.load(p,'power.jsonl')
            power[index]['readings'][0]['compute_process_ids']=[123,456]
            self.write(p,'power.jsonl',power)
            self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_pair_compares_all_collector_settings(self):
        for setting in ('poll_seconds','max_gap_seconds','max_read_seconds','request_timeout_s','drain_timeout_s'):
            a=self.fixture('a_'+setting,gpu='GPU-A',gpu_model='A100')
            b=self.fixture('b_'+setting,gpu='GPU-B',gpu_model='H100')
            run=self.load(b,'run.json');run['settings'][setting]*=2
            self.write(b,'run.json',run);result=compare_bundles(a,b)
            self.assertTrue(result['left']['data_quality_pass'],result['left']['failures'])
            self.assertTrue(result['right']['data_quality_pass'],result['right']['failures'])
            self.assertFalse(result['pair_data_quality_pass'])
    def test_pair_malformed_settings_returns_failed_report(self):
        a=self.fixture('a',gpu_model='A100');b=self.fixture('b',gpu_model='H100')
        run=self.load(b,'run.json');run['settings']=[];self.write(b,'run.json',run)
        result=compare_bundles(a,b)
        self.assertFalse(result['pair_data_quality_pass'])
        self.assertTrue(any('Pair settings must be objects' in x for x in result['pair_failures']))
    def test_missing_nonpositive_timeout_rejected(self):
        for name,key,value in [('missing','request_timeout_s',None),('zero','drain_timeout_s',0.0),('negative','request_timeout_s',-1.0)]:
            p=self.fixture(name);run=self.load(p,'run.json')
            if value is None:del run['settings'][key]
            else:run['settings'][key]=value
            self.write(p,'run.json',run)
            self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_null_quantization_and_enabled_prefix_caching_rejected(self):
        for name in ('quantization','prefix'):
            p=self.fixture(name);run=self.load(p,'run.json')
            if name=='quantization':run['config']['model']['quantization']=None
            else:run['config']['engine']['launch_config']['enable_prefix_caching']=True
            run['config_sha256']=canonical_sha(run['config']);self.write(p,'run.json',run)
            self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_unsupported_counter_with_positive_power_remains_valid(self):
        p=self.fixture();power=self.load(p,'power.jsonl')
        for sample in power:
            sample['readings'][0]['cumulative_energy_j']=None
            sample['readings'][0]['energy_counter_status']='unsupported'
        self.write(p,'power.jsonl',power);result=validate_bundle(p)
        self.assertTrue(result['data_quality_pass'],result['failures'])
        self.assertEqual(result['energy']['total']['aggregate_board_energy_j'],400.0)
    def test_total_consistency_screen_twenty_percent_boundary(self):
        for label,factor,expected in [('boundary',.8,True),('beyond',.79,False)]:
            p=self.fixture(label);power=self.load(p,'power.jsonl')
            for sample in power:sample['readings'][0]['cumulative_energy_j']=factor*100.0*sample['sample_monotonic']
            self.write(p,'power.jsonl',power);result=validate_bundle(p)
            self.assertEqual(result['data_quality_pass'],expected,result['failures'])
            policy=result['total_energy_consistency_screen']
            self.assertEqual(policy['relative_fraction_of_power_integral'],.20)
            self.assertEqual(policy['absolute_floor_j'],1.0)
    def test_consistency_screen_only_applies_to_total_not_short_phase(self):
        p=self.fixture();power=self.load(p,'power.jsonl')
        for sample in power:
            t=sample['sample_monotonic']
            sample['readings'][0]['cumulative_energy_j']=0.0 if t<=1 else (400.0 if t>=3 else 200.0*(t-1))
        self.write(p,'power.jsonl',power);result=validate_bundle(p)
        self.assertTrue(result['data_quality_pass'],result['failures'])
        self.assertEqual(result['energy']['idle_before']['aggregate_board_energy_j'],0.0)
        self.assertEqual(result['energy']['total']['aggregate_board_energy_j'],400.0)
    def test_counter_screen_checks_each_gpu_not_only_aggregate(self):
        p=self.fixture();run=self.load(p,'run.json');run['config']['gpu_uuids'].append('GPU-B')
        run['config']['server_gpu_worker_pids']['GPU-B']=[456]
        run['config_sha256']=canonical_sha(run['config'])
        board=copy.deepcopy(run['hardware']['boards'][0]);board['gpu_uuid']='GPU-B'
        run['hardware']['boards'].append(board);self.write(p,'run.json',run)
        power=self.load(p,'power.jsonl')
        for sample in power:
            row=copy.deepcopy(sample['readings'][0]);row.update(gpu_uuid='GPU-B',cumulative_energy_j=100.0,compute_process_ids=[456])
            sample['readings'].append(row)
        self.write(p,'power.jsonl',power);result=validate_bundle(p)
        self.assertFalse(result['data_quality_pass'])
        self.assertTrue(any('GPU-B: TOTAL cumulative counter' in failure for failure in result['failures']))
    def test_missing_worker_mapping_rejected(self):
        p=self.fixture();run=self.load(p,'run.json');del run['config']['server_gpu_worker_pids']
        run['config_sha256']=canonical_sha(run['config']);self.write(p,'run.json',run)
        result=validate_bundle(p)
        self.assertFalse(result['data_quality_pass'])
        self.assertTrue(any('server_gpu_worker_pids' in failure for failure in result['failures']))
    def test_missing_wrong_or_extra_compute_process_rejected(self):
        for label,pids in [('missing',[]),('wrong',[456]),('extra',[123,456])]:
            p=self.fixture(label);power=self.load(p,'power.jsonl')
            power[6]['readings'][0]['compute_process_ids']=pids
            self.write(p,'power.jsonl',power);result=validate_bundle(p)
            self.assertFalse(result['data_quality_pass'])
            self.assertTrue(any('compute PIDs differ' in failure for failure in result['failures']))
    def test_unsupported_or_absent_compute_inspection_rejected(self):
        for label in ('unsupported','error','missing'):
            p=self.fixture(label);power=self.load(p,'power.jsonl')
            if label=='missing':del power[6]['readings'][0]['compute_process_status']
            else:power[6]['readings'][0]['compute_process_status']=label
            self.write(p,'power.jsonl',power);result=validate_bundle(p)
            self.assertFalse(result['data_quality_pass'])
            self.assertTrue(any('compute-process inspection' in failure for failure in result['failures']))
    def test_malformed_hardware_uuid_is_reported_not_crash(self):
        p=self.fixture();run=self.load(p,'run.json')
        run['hardware']['boards'][0]['gpu_uuid']=[]
        self.write(p,'run.json',run)
        self.assertFalse(validate_bundle(p)['data_quality_pass'])
    def test_malformed_request_id_is_reported_not_crash(self):
        p=self.fixture();r=self.load(p,'requests.jsonl');r[0]['request_id']=[];self.write(p,'requests.jsonl',r)
        self.assertFalse(validate_bundle(p)['data_quality_pass'])

if __name__=='__main__':unittest.main()
