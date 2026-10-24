import copy
from collections import deque
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import service_driver as d


class SchedulingTests(unittest.TestCase):
    def test_independent_frozen_streams_and_balanced_queries(self):
        cal=d.make_plan('calibration'); ev=d.make_plan('evaluation',100)
        self.assertEqual(len(cal['windows']),16); self.assertEqual(len(ev['windows']),8)
        self.assertFalse({w['seed'] for w in cal['windows']} & {w['seed'] for w in ev['windows']})
        for plan in (cal,ev):
            for a,b in zip(plan['windows'][::2],plan['windows'][1::2]):
                self.assertEqual(a['requests'],b['requests'])
                self.assertNotEqual(a['policy'],b['policy'])
                self.assertEqual(sorted(r['query_id'] for r in a['requests']),sorted(list(range(100))*2))
                self.assertEqual(a['requests'],d.schedule(a['seed'],200,a['rate']))

    def test_wait_deadline_not_restarted_by_dispatch_delay(self):
        pending=deque([{'request_id':'0','planned_ns':10}])
        self.assertIsNone(d.next_batch(pending,'bounded',10+d.WAIT_NS-1))
        self.assertEqual(d.next_batch(pending,'bounded',10+d.WAIT_NS)[0]['request_id'],'0')
        delayed=deque([{'request_id':'1','planned_ns':0}])
        self.assertEqual(len(d.next_batch(delayed,'bounded',5*d.WAIT_NS)),1)

    def test_batch_full_and_fifo_and_immediate(self):
        pending=deque([{'request_id':str(i),'planned_ns':100} for i in range(18)])
        got=d.next_batch(pending,'bounded',100)
        self.assertEqual([r['request_id'] for r in got],[str(i) for i in range(16)])
        self.assertEqual(d.next_batch(pending,'immediate',100)[0]['request_id'],'16')
        self.assertEqual(len(pending),1)

    def test_failure_denominator_and_jitter(self):
        rows=[{'status':'ok','latency_ns':1,'planned_ns':i,'offered_ns':i} for i in range(100)]
        for r in rows[:6]: r['status']='failed_after_submit';r['latency_ns']=None
        result=d.summarize(rows)
        self.assertIsNone(result['p95_ns']);self.assertEqual(result['deadline_success'],94)
        rows[-1]['offered_ns']=20_000_000
        self.assertFalse(d.summarize(rows)['arrival_valid'])

    def test_zero_or_missing_windows_never_pass(self):
        self.assertFalse(d.assess([], 'evaluation')['passed'])
        result={'rate':100,'pair':0,'policy':'bounded','failure':None,
                'summary':{'arrival_valid':True,'planned':200,'correct_delivered':200,
                           'deadline_success':200,'p95_ns':1}}
        self.assertFalse(d.assess([result], 'evaluation')['passed'])

    def test_success_gate_uses_paired_10_percent_and_99_percent_deadlines(self):
        rows=[]
        for pair in range(4):
            for policy,p95 in [('immediate',10),('bounded',9)]:
                rows.append({'rate':100,'pair':pair,'policy':policy,'failure':None,
                  'summary':{'arrival_valid':True,'planned':200,'correct_delivered':200,'deadline_success':198,'p95_ns':p95}})
        self.assertTrue(d.assess(rows,'evaluation')['passed'])
        rows[0]['summary']['deadline_success']=197
        self.assertFalse(d.assess(rows,'evaluation')['passed'])

    def test_approval_absent_denies_collection(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'logs') as tmp:
            f=Path(tmp)/'no.json';f.write_text('{"authorized": false}')
            with self.assertRaises(ValueError): d.validate_freeze(f)

    def test_copied_qualified_table_schema_without_new_distances(self):
        value=json.loads((ROOT/'data/qualified_top10.json').read_text())
        self.assertEqual(d.validate_expected_answers(value),value)
        broken=copy.deepcopy(value);del broken['99']
        with self.assertRaisesRegex(ValueError,'100 canonical'):d.validate_expected_answers(broken)
        broken=copy.deepcopy(value);broken['0'][0]['distance']=float(broken['0'][0]['distance'])
        with self.assertRaisesRegex(ValueError,'distance range/type'):d.validate_expected_answers(broken)
        broken=copy.deepcopy(value);broken['0'][0],broken['0'][1]=broken['0'][1],broken['0'][0]
        with self.assertRaisesRegex(ValueError,'noncanonical'):d.validate_expected_answers(broken)
        broken=copy.deepcopy(value);broken['0'][0]['id']=True
        with self.assertRaisesRegex(ValueError,'ID range/type'):d.validate_expected_answers(broken)
        broken=copy.deepcopy(value);broken['0'][0]['extra']='bad'
        with self.assertRaisesRegex(ValueError,'neighbor schema'):d.validate_expected_answers(broken)

    def test_remaining_budget_caps_startup_and_warmup(self):
        with patch.object(d.time,'monotonic',return_value=100):
            self.assertEqual(d.remaining_timeout(100.25,30,'startup'),.25)
            self.assertEqual(d.remaining_timeout(100.25,2,'warmup'),.25)
            self.assertEqual(d.remaining_timeout(200,2,'batch'),2)
            with self.assertRaisesRegex(TimeoutError,'before startup'):
                d.remaining_timeout(100,30,'startup')


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(dir=ROOT/'logs')
        cls.backend=d.Backend([str(ROOT/'build/retrieval-service'),'--synthetic-service'],Path(cls.tmp.name)/'stderr',5)

    @classmethod
    def tearDownClass(cls):
        cls.backend.close();cls.tmp.cleanup()

    def independent(self,qid):
        base=[[((i*3+j)*7+i)%17 for j in range(3)] for i in range(32)]
        query=[((qid*3+j)*11+3)%19 for j in range(3)]
        distances=[sum((a-b)**2 for a,b in zip(query,row)) for row in base]
        top=sorted(range(32),key=lambda i:(distances[i],i))[:10]
        return ([{'id':i,'distance':distances[i]} for i in top],
                hashlib.sha256(b''.join(v.to_bytes(4,'little') for v in distances)).hexdigest())

    def test_arbitrary_repeated_queries_and_full_batch_independent_oracle(self):
        for batch,qids in enumerate(([99,0,99],list(range(16)),[47])):
            rows=[{'request_id':str(i),'query_id':q} for i,q in enumerate(qids)]
            response=self.backend.solve(batch,rows,2)
            d.validate_response(response,batch,rows,32)
            for r,a in zip(rows,response['answers']):
                top,digest=self.independent(r['query_id'])
                self.assertEqual(a['top10'],top);self.assertEqual(a['distance_sha256'],digest)

    def test_rejected_wrong_identity_and_false_validation(self):
        rows=[{'request_id':'check','query_id':4}]
        response=self.backend.solve(555,rows,2)
        changed=copy.deepcopy(response);changed['answers'][0]['request_id']='other'
        with self.assertRaises(ValueError):d.validate_response(changed,555,rows,32)
        changed=copy.deepcopy(response);changed['answers'][0]['passed']=False
        with self.assertRaises(ValueError):d.validate_response(changed,555,rows,32)

    def test_expected_answers_match_and_deliberate_mismatch(self):
        # Tiny synthetic direct-integer answers, never real SIFT distances.
        expected={str(q):self.independent(q)[0] for q in range(100)}
        d.validate_expected_answers(expected)
        rows=[{'request_id':'expected','query_id':13}]
        response=self.backend.solve(556,rows,2)
        d.validate_response(response,556,rows,32,expected)
        changed=copy.deepcopy(expected)
        changed['13'][-1]['distance']+=1
        d.validate_expected_answers(changed)
        with self.assertRaisesRegex(ValueError,'qualified canonical answer'):
            d.validate_response(response,556,rows,32,changed)


class FailureAccountingTests(unittest.TestCase):
    def test_backend_timeout_has_descriptive_error(self):
        backend=d.Backend.__new__(d.Backend);backend.lines=d.queue.Queue()
        with self.assertRaisesRegex(TimeoutError,'No backend response within 0.001 seconds'):
            backend.receive(.001)

    def test_shared_phase_deadline_does_not_reset_for_window(self):
        class NeverCalled:
            ready={'base_count':32}
            def solve(self,*args):raise AssertionError('Expired phase dispatched work')
        config=d.make_plan('evaluation',100)
        spec={'window_id':'budget','policy':'immediate','rate':100,'pair':0,'requests':[
            {'request_id':'0','query_id':0,'offset_ns':1_000_000_000}]}
        with tempfile.TemporaryDirectory(dir=ROOT/'logs') as tmp:
            result=d.run_window(spec,NeverCalled(),Path(tmp)/'window',config,phase_deadline=time.monotonic()+.005)
            self.assertIn('watchdog',result['failure'])
            self.assertEqual(result['requests'][0]['status'],'not_offered_after_abort')
            self.assertEqual(result['summary']['planned'],1)

    def test_arrival_exception_interrupts_wait_and_retains_all_requests(self):
        class WaitingBackend:
            ready={'base_count':32}
            def solve(self,batch_id,rows,timeout,interrupt):
                backend=d.Backend.__new__(d.Backend);backend.lines=d.queue.Queue()
                return backend.receive(timeout,interrupt)
        original=d.queue.Queue.put
        def failing_put(q,item,*args,**kwargs):
            if threading.current_thread().name=='external-arrivals' and isinstance(item,dict) and item['request_id']=='1':
                raise RuntimeError('Synthetic arrival failure')
            return original(q,item,*args,**kwargs)
        spec={'window_id':'arrival-failure','policy':'immediate','rate':100,'pair':0,'requests':[
            {'request_id':'0','query_id':0,'offset_ns':0},
            {'request_id':'1','query_id':1,'offset_ns':10_000_000},
            {'request_id':'2','query_id':2,'offset_ns':1_000_000_000}]}
        with tempfile.TemporaryDirectory(dir=ROOT/'logs') as tmp, patch.object(d.queue.Queue,'put',failing_put):
            result=d.run_window(spec,WaitingBackend(),Path(tmp)/'window',d.make_plan('evaluation',100))
            self.assertIn('Arrival scheduler failed: RuntimeError: Synthetic arrival failure',result['failure'])
            self.assertEqual([r['status'] for r in result['requests']],
                             ['failed_after_submit','unserved_after_offer','not_offered_after_abort'])
            self.assertEqual(result['summary']['planned'],3)
            self.assertEqual(result['summary']['deadline_success'],0)

    def test_timeout_retains_submitted_queued_and_future_requests(self):
        class FailureBackend:
            ready={'base_count':32}
            def solve(self,*args):raise TimeoutError('Synthetic timeout')
        config=d.make_plan('evaluation',100)
        spec={'window_id':'failure','policy':'immediate','rate':100,'pair':0,'requests':[
            {'request_id':str(i),'query_id':i,'offset_ns':i*100_000_000} for i in range(3)]}
        with tempfile.TemporaryDirectory(dir=ROOT/'logs') as tmp:
            result=d.run_window(spec,FailureBackend(),Path(tmp)/'window',config)
            self.assertEqual(len(result['requests']),3)
            self.assertEqual(result['requests'][0]['status'],'failed_after_submit')
            self.assertEqual(result['requests'][2]['status'],'not_offered_after_abort')
            self.assertEqual(result['summary']['deadline_success'],0)
            self.assertIsNone(result['summary']['p95_ns'])
            self.assertTrue((Path(tmp)/'window/RESULT.json').exists())

    def test_malformed_response_retained(self):
        class BadBackend:
            ready={'base_count':32}
            def solve(self,*args):return {'event':'fatal','error':'synthetic failure'}
        config=d.make_plan('evaluation',100)
        spec={'window_id':'bad','policy':'immediate','rate':100,'pair':0,'requests':[
            {'request_id':'0','query_id':0,'offset_ns':0}]}
        with tempfile.TemporaryDirectory(dir=ROOT/'logs') as tmp:
            result=d.run_window(spec,BadBackend(),Path(tmp)/'window',config)
            self.assertIn('Wrong response',result['failure'])
            self.assertIn('synthetic failure',(Path(tmp)/'window/RESPONSES.jsonl').read_text())


if __name__=='__main__':unittest.main()
