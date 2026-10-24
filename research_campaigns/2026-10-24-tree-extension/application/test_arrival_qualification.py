"""Deterministic fake-clock tests only: no worker, socket, physical wait or timing run."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import arrival_qualification as a


class FakeClock:
    def __init__(self,wake_delay=0,send_delay=100,stop_after=None):
        self.ns=0;self.wake_delay=wake_delay;self.send_delay=send_delay
        self.waits=[];self.messages=[];self.stop_after=stop_after
    def clock(self):return self.ns
    def wait(self,seconds):
        self.waits.append(seconds)
        if self.stop_after is not None and len(self.messages)>=self.stop_after:return True
        self.ns+=round(seconds*1e9)+self.wake_delay;return False
    def send(self,msg):
        self.messages.append(dict(msg,received_ns=self.ns+1))
        self.ns+=self.send_delay


class DeterministicTests(unittest.TestCase):
    def schedule(self):return [{'request_id':i,'offset_ns':i*1_000_000,'planned_ns':1_000_000+i*1_000_000} for i in range(3)]

    def test_frozen_cases_seeds_pairs_and_budget(self):
        p=a.plan();self.assertEqual(len(p['cases']),48)
        self.assertEqual(sum(len(c['requests']) for c in p['cases']),2400)
        self.assertLess(p['planned_offer_horizons_plus_leads_ns'],70_000_000_000)
        self.assertEqual(p['phase_seconds'],80)
        self.assertEqual({c['rate'] for c in p['cases']},{20,50,100,200})
        for left,right in zip(p['cases'][::2],p['cases'][1::2]):
            self.assertEqual(left['requests'],right['requests'])
            self.assertEqual(left['seed'],right['seed'])
            self.assertEqual({left['mode'],right['mode']},{'thread','process'})
        for rep in range(3):
            for rate in (20,50,100,200):
                rows=[c for c in p['cases'] if c['rep']==rep and c['rate']==rate]
                self.assertEqual(len(rows),4)
                self.assertTrue(all(c['requests']==rows[0]['requests'] for c in rows))
        self.assertEqual(len({c['seed'] for c in p['cases']}),12)
        self.assertFalse({c['seed'] for c in p['cases']}&set(range(241024100,241024132)))

    def test_absolute_wait_not_shifted_by_send_work(self):
        clock=FakeClock(send_delay=100)
        done=a.produce(self.schedule(),clock,clock.clock,clock.send)
        rows=a.reconcile(self.schedule(),clock.messages,done)
        self.assertEqual([r['wake_ns'] for r in rows],[1_000_000,2_000_000,3_000_000])
        self.assertEqual([r['admitted_ns']-r['planned_ns'] for r in rows],[100]*3)
        self.assertTrue(a.summarize(rows)['qualification_pass'])

    def test_early_return_rechecks_absolute_time_then_offers_all_fifty(self):
        class EarlyOnce(FakeClock):
            def wait(self,seconds):
                self.waits.append(seconds)
                self.ns+=round(seconds*1e9)-(1 if len(self.waits)==1 else 0)
                return False
        planned=[{'request_id':i,'offset_ns':i*1_000_000,'planned_ns':(i+1)*1_000_000} for i in range(50)]
        clock=EarlyOnce();done=a.produce(planned,clock,clock.clock,clock.send)
        rows=a.reconcile(planned,clock.messages,done)
        self.assertIsNone(done['failure']);self.assertEqual(len(rows),50)
        self.assertEqual(clock.waits[:2],[.001,1e-9])
        self.assertEqual([r['planned_ns'] for r in rows],[r['planned_ns'] for r in planned])
        self.assertEqual([r['wake_ns'] for r in rows],[r['planned_ns'] for r in planned])
        self.assertTrue(a.summarize(rows)['qualification_pass'])

    def test_repeated_early_returns_then_cancel_preserves_fifty(self):
        class EarlyThenStop(FakeClock):
            def wait(self,seconds):
                self.waits.append(seconds)
                if len(self.waits)==4:return True
                self.ns=1_000_000-(4-len(self.waits))
                return False
        planned=[{'request_id':i,'offset_ns':i*1_000_000,'planned_ns':(i+1)*1_000_000} for i in range(50)]
        clock=EarlyThenStop();done=a.produce(planned,clock,clock.clock,clock.send)
        rows=a.reconcile(planned,clock.messages,done);stats=a.summarize(rows)
        self.assertEqual(clock.waits,[.001,3e-9,2e-9,1e-9])
        self.assertEqual(len(rows),50);self.assertEqual(clock.messages,[])
        self.assertEqual([r['request_id'] for r in rows],list(range(50)))
        self.assertIn('stopped',done['failure']);self.assertEqual(stats['admitted'],0)
        self.assertIsNone(stats['admission_jitter']['p99_ns']);self.assertFalse(stats['qualification_pass'])

    def test_incomplete_cpu_join_reports_unknown_final_count(self):
        record,error=a.final_cpu_accounting({'iterations':0},True,True)
        self.assertEqual(record,{'status':'cleanup_incomplete','iterations':None})
        self.assertIn('final accounting unavailable',error)
        self.assertNotIn('did not run',error)
        record,error=a.final_cpu_accounting({'iterations':2048,'checksum':1},True,False)
        self.assertEqual(record['iterations'],2048);self.assertEqual(record['status'],'complete')
        self.assertIsNone(error)

    def test_timely_wake_does_not_hide_transport_backpressure(self):
        clock=FakeClock(send_delay=3_000_000)
        planned=self.schedule()[:1]
        done=a.produce(planned,clock,clock.clock,clock.send)
        rows=a.reconcile(planned,clock.messages,done);stats=a.summarize(rows)
        self.assertEqual(stats['wake_jitter']['maximum_ns'],0)
        self.assertEqual(stats['admission_jitter']['maximum_ns'],3_000_000)
        self.assertFalse(stats['qualification_pass'])
        self.assertLess(rows[0]['received_ns'],rows[0]['admitted_ns'])

    def test_late_wake_stays_late_and_no_omission(self):
        clock=FakeClock(wake_delay=5_000_000)
        done=a.produce(self.schedule(),clock,clock.clock,clock.send)
        rows=a.reconcile(self.schedule(),clock.messages,done)
        self.assertEqual(len(rows),3)
        self.assertFalse(a.summarize(rows)['qualification_pass'])
        self.assertEqual(clock.waits[1:], [0,0])

    def test_stop_preserves_all_future_requests_and_failure_denominator(self):
        clock=FakeClock(stop_after=1)
        done=a.produce(self.schedule(),clock,clock.clock,clock.send)
        rows=a.reconcile(self.schedule(),clock.messages,done);stats=a.summarize(rows)
        self.assertIsNotNone(done['failure']);self.assertEqual(len(rows),3)
        self.assertEqual(stats['admitted'],1);self.assertIsNone(stats['admission_jitter']['p99_ns'])
        self.assertFalse(stats['qualification_pass'])

    def test_send_failure_preserves_planned_ids(self):
        clock=FakeClock()
        def fail(msg):raise OSError('synthetic broken pipe')
        done=a.produce(self.schedule(),clock,clock.clock,fail)
        self.assertIn('synthetic broken pipe',done['failure'])
        rows=a.reconcile(self.schedule(),[],done)
        self.assertEqual([r['request_id'] for r in rows],[0,1,2])
        self.assertEqual(a.summarize(rows)['admitted'],0)

    def test_no_final_metadata_cannot_certify_admission(self):
        clock=FakeClock();a.produce(self.schedule(),clock,clock.clock,clock.send)
        rows=a.reconcile(self.schedule(),clock.messages,None)
        self.assertEqual(a.summarize(rows)['received'],3)
        self.assertFalse(a.summarize(rows)['qualification_pass'])

    def test_receipt_delay_is_separate_and_visible(self):
        clock=FakeClock();done=a.produce(self.schedule(),clock,clock.clock,clock.send)
        for msg in clock.messages:msg['received_ns']+=100_000_000
        rows=a.reconcile(self.schedule(),clock.messages,done);stats=a.summarize(rows)
        self.assertTrue(stats['qualification_pass'])
        self.assertGreater(stats['receipt_delay']['maximum_ns'],100_000_000)

    def test_identity_and_timestamp_corruption_rejected(self):
        clock=FakeClock();done=a.produce(self.schedule(),clock,clock.clock,clock.send)
        with self.assertRaisesRegex(ValueError,'duplicate'):
            a.reconcile(self.schedule(),clock.messages+[clock.messages[0]],done)
        with self.assertRaisesRegex(ValueError,'reordered'):
            a.reconcile(self.schedule(),list(reversed(clock.messages)),done)
        bad=copy.deepcopy(clock.messages);bad[0]['planned_ns']+=1
        with self.assertRaisesRegex(ValueError,'timestamp changed'):a.reconcile(self.schedule(),bad,done)

    def test_nearest_rank_at_fifty_and_strict_threshold(self):
        self.assertEqual(a.nearest(list(range(1,51)),99),50)
        self.assertEqual(a.nearest(list(range(1,201)),99),198)
        rows=[{'planned_ns':0,'wake_ns':0,'emitted_ns':0,'admitted_ns':2_000_000,'received_ns':2_000_001} for _ in range(50)]
        self.assertTrue(a.summarize(rows)['qualification_pass'])
        rows[-1]['admitted_ns']+=1
        self.assertFalse(a.summarize(rows)['qualification_pass'])

    def test_unsigned_authorization_rejected_before_worker_or_output(self):
        with tempfile.TemporaryDirectory(dir=a.ROOT) as tmp:
            path=Path(tmp);approval=path/'unsigned.json';approval.write_text('{"authorized":false}')
            argv=['arrival_qualification.py','--authorization',str(approval),'--output',str(path/'output')]
            with patch.object(sys,'argv',argv),patch.object(a.mp,'get_context',side_effect=AssertionError('Worker launch forbidden')):
                with self.assertRaisesRegex(ValueError,'authorization'):a.main()
            self.assertFalse((path/'output').exists())


if __name__=='__main__':unittest.main()
