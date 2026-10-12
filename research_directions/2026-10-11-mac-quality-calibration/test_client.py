import json
import threading
import time
import unittest
from unittest.mock import patch
import inspect
import client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from client import run_trace

class Handler(BaseHTTPRequestHandler):
    starts=[]
    lock=threading.Lock()
    def log_message(self,*args):pass
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        prompt=body['prompt']
        with self.lock:self.starts.append((prompt,time.monotonic(),body))
        if prompt=='http-error':self.send_error(503);return
        self.send_response(200);self.send_header('Content-Type','application/x-ndjson');self.end_headers()
        if prompt=='malformed':self.wfile.write(b'bad json\n');return
        if prompt=='server-error':self.wfile.write(b'{"error":"fixture rejected"}\n');return
        if prompt=='slow':time.sleep(.25)
        chunks=[{'model':'fixture','response':'','thinking':'hidden','done':False},
                {'model':'fixture','response':'hello','done':False}]
        final=dict(model='fixture',response='',done=True,done_reason='length',
                   prompt_eval_count=7,eval_count=2,total_duration=100,load_duration=2,
                   prompt_eval_duration=20,eval_duration=78)
        if prompt=='missing-usage':del final['eval_count']
        if prompt=='bool-usage':final['eval_count']=True
        if prompt=='wrong-model':final['model']='other'
        if prompt=='empty':chunks=[]
        if prompt!='no-done':chunks.append(final)
        for item in chunks:self.wfile.write(json.dumps(item).encode()+b'\n');self.wfile.flush()

class ClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def collect(self,prompts,offsets=None):
        trace=[dict(request_id=str(i),prompt=p,arrival_offset_s=(offsets or [0]*len(prompts))[i]) for i,p in enumerate(prompts)]
        return run_trace(self.base,trace,'fixture',{'num_predict':64},timeout_s=2)
    def test_valid_stream_clock_and_usage(self):
        result=self.collect(['ok']);r=result['requests'][0]
        self.assertTrue(r['completed']);self.assertIsNone(r['error'])
        self.assertEqual(r['final']['done_reason'],'length')
        self.assertEqual(r['first_content_offset_s'],r['chunks'][1]['offset_s'])
        self.assertLessEqual(r['dispatch_offset_s'],r['first_content_offset_s'])
        self.assertLessEqual(r['first_content_offset_s'],r['terminal_offset_s'])
        self.assertLessEqual(r['terminal_offset_s'],result['elapsed_seconds'])
        self.assertEqual(r['request_id'],'0');self.assertEqual(r['arrival_offset_s'],0)
    def test_open_loop_later_request_does_not_wait_for_slow_response(self):
        with Handler.lock:Handler.starts=[]
        result=self.collect(['slow','fast'],[0,.03])
        a,b=result['requests'];self.assertTrue(a['completed'] and b['completed'])
        self.assertLess(b['dispatch_offset_s'],a['terminal_offset_s'])
        self.assertGreaterEqual(b['dispatch_offset_s'],.03)
        self.assertLess(b['terminal_offset_s'],a['terminal_offset_s'])
        with Handler.lock:seen=list(Handler.starts)
        for _,_,body in seen:
            self.assertTrue(body['stream']);self.assertEqual(body['keep_alive'],'120s')
            self.assertEqual(body['options'],{'num_predict':64})
    def test_failures_retain_every_offered_id_and_received_chunks(self):
        prompts=['http-error','malformed','server-error','no-done','missing-usage','bool-usage','wrong-model','empty']
        rows=self.collect(prompts)['requests'];self.assertEqual(len(rows),len(prompts))
        self.assertEqual([r['request_id'] for r in rows],list(map(str,range(len(prompts)))))
        for r in rows:
            self.assertFalse(r['completed']);self.assertIsInstance(r['error'],str)
            self.assertGreaterEqual(r['terminal_offset_s'],r['dispatch_offset_s'])
        self.assertEqual(len(rows[3]['chunks']),2)
    def test_invalid_trace_rejected_before_dispatch(self):
        cases=[[dict(request_id='a',prompt='x',arrival_offset_s=-1)],
               [dict(request_id='a',prompt='x',arrival_offset_s=float('nan'))],
               [dict(request_id='a',prompt='x',arrival_offset_s=0)]*2]
        for trace in cases:
            with self.subTest(trace=trace):
                with self.assertRaises(ValueError):run_trace(self.base,trace,'fixture',{})
    def test_nonlocal_or_credentialed_urls_rejected(self):
        for url in ['https://127.0.0.1','http://example.com','http://user:pass@127.0.0.1','http://127.0.0.1/path']:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):run_trace(url,[],'fixture',{})
    def test_empty_trace(self):self.assertEqual(run_trace(self.base,[],'fixture',{})['requests'],[])
    def test_thread_start_failure_retains_failed_job_and_continues_others(self):
        real_start=threading.Thread.start
        def selective_start(thread):
            if thread.name=='trace-0':raise RuntimeError('injected lifecycle failure')
            return real_start(thread)
        with patch.object(threading.Thread,'start',selective_start):
            rows=self.collect(['ok','ok'])['requests']
        self.assertEqual([r['request_id'] for r in rows],['0','1'])
        self.assertFalse(rows[0]['completed']);self.assertIsInstance(rows[0]['error'],str)
        self.assertIsNone(rows[0]['dispatch_offset_s']);self.assertTrue(rows[1]['completed'])
    def test_exact_signature_and_list_contract(self):
        self.assertEqual(list(inspect.signature(run_trace).parameters),['base_url','trace','model','options','timeout_s','checkpoint','hard_timeout_s'])
        with self.assertRaises(ValueError):run_trace(self.base,(),'fixture',{})
    def test_hard_bound_preserves_checkpoint(self):
        retained=[]
        trace=[dict(request_id='slow',prompt='slow',arrival_offset_s=0)]
        start=time.monotonic()
        with self.assertRaises(TimeoutError):
            run_trace(self.base,trace,'fixture',{},timeout_s=2,hard_timeout_s=.06,
                      checkpoint=lambda value:retained.append(json.loads(json.dumps(value))))
        self.assertLess(time.monotonic()-start,.2)
        self.assertTrue(retained[-1]['collection_incomplete'])
        self.assertEqual(retained[-1]['requests'][0]['request_id'],'slow')
        self.assertIsNotNone(retained[-1]['requests'][0]['dispatch_offset_s'])
        time.sleep(.25)  # let fixture worker finish before server teardown
    def test_omitted_http_port_is_standard_port80(self):
        self.assertEqual(client._parse_base_url('http://127.0.0.1'),('127.0.0.1',80))

if __name__=='__main__':unittest.main()
