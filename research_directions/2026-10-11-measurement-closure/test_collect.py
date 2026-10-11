import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

from collect import collect, load_trace, local_url, stream_request, validate_config


def fixture_config():
    return {'config_id':'fixture-only', 'model':{'id':'fixture/model','revision':'1'*40,
            'tokenizer_revision':'2'*40,'dtype':'float16','quantization':'none'},
            'engine':{'name':'vllm','version':'fixture-version','container_digest':'sha256:'+'3'*64,
                      'launch_config':{'tensor_parallel_size':1,'pipeline_parallel_size':1,
                          'enable_prefix_caching':False,'enable_chunked_prefill':False,
                          'cpu_offload_gb':0,'speculative_config':None,'max_model_len':1024}},
            'gpu_uuids':['GPU-fixture'],'server_gpu_worker_pids':{'GPU-fixture':[123]},
            'decoding':{'temperature':0,'max_tokens':16,
                                                 'seed':0,'ignore_eos':False},
            'workload_provenance':'Synthetic protocol test; not a workload sample',
            'slo':{'response_seconds':60,'first_content_seconds':1,'client_tpot_seconds':1}}


class FakeBackend:
    def __init__(self, uuids):
        self.uuids=uuids
        self.closed=False
        self.metadata={'gpu_uuids':uuids,'driver_version':'fixture-driver',
            'boards':[{'gpu_uuid':u,'name':'Synthetic GPU','memory_total_bytes':1024,
                       'power_limit_w':20,'default_power_limit_w':20,
                       'power_limit_constraints_w':[10,30]} for u in uuids]}

    def read(self):
        return [{'gpu_uuid':u,'power_w':10.,'cumulative_energy_j':time.monotonic()*10.,
                 'energy_counter_status':'ok','status':'ok','error':None,
                 'compute_process_ids':[123],'compute_process_status':'ok'} for u in self.uuids]

    def close(self):
        self.closed=True


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def do_GET(self):
        if self.path=='/version':
            payload=json.dumps({'version':'fixture-version'}).encode()
        elif self.path=='/v1/models':
            payload=json.dumps({'data':[{'id':'fixture/model'}]}).encode()
        elif self.path=='/metrics':
            payload=b'vllm:num_requests_running{model_name="fixture/model"} 0\nvllm:num_requests_waiting 0\n'
        else:
            self.send_error(404);return
        self.send_response(200);self.end_headers();self.wfile.write(payload)

    def do_POST(self):
        req=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
        mode=req['prompt']
        def emit(value):
            self.wfile.write(('data: '+json.dumps(value)+'\n\n').encode());self.wfile.flush()
        if mode=='slow_first_content':
            time.sleep(10.1)
        emit({'choices':[{'text':'','finish_reason':None}]})
        time.sleep(.01)
        # Multiple tokens can be bundled into each content event; chars != tokens.
        emit({'choices':[{'text':'one two','finish_reason':None}]})
        time.sleep(.01)
        emit({'choices':[{'text':' three four','finish_reason':'stop'}]})
        if mode!='missing_usage':
            emit({'choices':[],'usage':{'prompt_tokens':3,'completion_tokens':4}})
        if mode!='truncated':
            self.wfile.write(b'data: [DONE]\n\n');self.wfile.flush()


class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start();cls.url='http://127.0.0.1:'+str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def stream(self,prompt):
        return stream_request(self.url,'fixture/model',fixture_config()['decoding'],
                              {'request_id':'r1','prompt':prompt},time.monotonic())

    def test_stream_retains_chunks_and_server_usage_separately(self):
        result=self.stream('normal')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['usage']['completion_tokens'],4)
        self.assertEqual(len(result['chunk_events']),2)
        self.assertEqual(result['output_sha256'],hashlib.sha256(b'one two three four').hexdigest())
        self.assertGreater(result['first_content_monotonic'],result['dispatch_monotonic'])
        self.assertGreater(result['last_content_monotonic'],result['first_content_monotonic'])

    def test_truncated_stream_is_not_success(self):
        result=self.stream('truncated')
        self.assertEqual(result['status'],'error')
        self.assertIn('Truncated',result['error'])

    def test_missing_usage_is_not_invented_from_characters(self):
        result=self.stream('missing_usage')
        self.assertEqual(result['status'],'error')
        self.assertIsNone(result['usage'])

    def test_slow_first_content_within_declared_budget_is_not_truncated_at_ten_seconds(self):
        result=stream_request(self.url,'fixture/model',fixture_config()['decoding'],
            {'request_id':'slow','prompt':'slow_first_content'},time.monotonic(),timeout=12)
        self.assertEqual(result['status'],'ok',result['error'])
        self.assertGreaterEqual(result['first_content_monotonic']-result['dispatch_monotonic'],10)

    def test_only_loopback_existing_servers_supported(self):
        self.assertEqual(local_url(self.url+'/'),self.url)
        for invalid in ('https://example.com','http://example.com','http://user:pw@localhost',
                        'http://localhost/v1','http://localhost?key=secret'):
            with self.assertRaises(ValueError):local_url(invalid)

    def test_placeholder_config_and_duplicate_requests_rejected(self):
        config=fixture_config();config['model']['revision']='FILL_ME'
        with self.assertRaises(ValueError):validate_config(config)
        config=fixture_config();config['engine']['launch_config']['enable_prefix_caching']=True
        with self.assertRaises(ValueError):validate_config(config)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'trace.jsonl'
            row={'request_id':'x','prompt':'normal','arrival_offset_s':0}
            p.write_text(json.dumps(row)+'\n'+json.dumps(row)+'\n')
            with self.assertRaises(ValueError):load_trace(p)

    def run_fixture(self, tmp, config=None):
        root=Path(tmp);cp=root/'config.json';tp=root/'trace.jsonl';out=root/'run'
        cp.write_text(json.dumps(config or fixture_config()))
        tp.write_text('\n'.join(json.dumps({'request_id':str(i),'prompt':prompt,
                  'arrival_offset_s':i*.005}) for i,prompt in enumerate(['normal','missing_usage']))+'\n')
        run=collect(cp,tp,out,self.url,concurrency=2,idle_seconds=.05,poll_seconds=.005,
                    drain_timeout=2,backend_factory=FakeBackend)
        return out,run

    def test_full_collection_is_labeled_fixture_and_preserves_failed_demand(self):
        with tempfile.TemporaryDirectory() as tmp:
            out,run=self.run_fixture(tmp)
            rows=[json.loads(x) for x in (out/'requests.jsonl').read_text().splitlines()]
            self.assertEqual(run['evidence_kind'],'synthetic_fixture')
            self.assertEqual({r['request_id'] for r in rows},{'0','1'})
            self.assertEqual(sum(r['status']=='error' for r in rows),1)
            self.assertEqual(run['collector_errors'],[])
            self.assertTrue(run['warmup_ok'])
            self.assertTrue((out/'power.jsonl').stat().st_size>0)
            from validate import validate_bundle
            report=validate_bundle(out)
            self.assertTrue(report['data_quality_pass'], report['failures'])
            self.assertFalse(report['measured_data_ready'])
            self.assertFalse(report['deployment_gate'])

    def test_preflight_failure_still_saves_offered_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            config=fixture_config();config['engine']['version']='different-version'
            out,run=self.run_fixture(tmp,config)
            self.assertTrue(run['collector_errors'])
            rows=[json.loads(x) for x in (out/'requests.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows),2)
            self.assertTrue(all(r['status']=='not_dispatched' for r in rows))


if __name__=='__main__':
    unittest.main()
