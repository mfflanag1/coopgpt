"""CPU-only tests of fixed collection and failure-preservation paths."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import run_retrieval as r


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.binary=self.root/'retrieve';self.binary.write_bytes(b'fixture')
        self.profile={'index':1,'profile_id':'b1','batch_size':1,'folder':'p01_b1'}
        self.plan={'campaign_timeout_seconds':300,'window_timeout_seconds':90,
                   'profiles':[self.profile,{'index':2,'profile_id':'b16','batch_size':16,'folder':'p02_b16'}]}
        (self.root/'PLAN.json').write_text(json.dumps(self.plan))
        self.freeze=patch.object(r,'verify_freeze',return_value='fixed');self.freeze.start();self.addCleanup(self.freeze.stop)
        self.diag=patch.object(r,'diagnostics',return_value={'batt':{'fixture':True}});self.diag.start();self.addCleanup(self.diag.stop)
        self.rootpatch=patch.object(r,'ROOT',self.root);self.rootpatch.start();self.addCleanup(self.rootpatch.stop)
        self.inv=patch('capture_inventory.capture',return_value={'hardware':{'gpu_inventory':{'devices':[]}}})
        self.inv.start();self.addCleanup(self.inv.stop)

    def native_success(self,command,**kwargs):
        out=Path(command[-1]);out.mkdir();(out/'RAW.json').write_text('{"gate_passed":true}')
        return subprocess.CompletedProcess(command,0,'complete','')

    def call_profile(self):
        return r.run_profile(self.binary,self.root/'profile',self.profile,90,r.time.monotonic()+300,'fixed')

    def campaign(self):
        return r.collect(self.binary,self.root/'capture')

    def read_campaign(self):
        return json.loads((self.root/'capture/CAMPAIGN.json').read_text())

    def test_two_profiles_in_exact_order_and_arguments(self):
        with patch.object(r.subprocess,'run',side_effect=self.native_success) as call:
            self.assertTrue(self.campaign())
        commands=[c.args[0] for c in call.call_args_list]
        self.assertEqual([c[4] for c in commands],['1','16'])
        self.assertEqual(commands[0][:4],[str(self.binary),'--data',str(self.root/'data'),'--batch-size'])
        self.assertEqual([p['profile_id'] for p in self.read_campaign()['profiles']],['b1','b16'])
        self.assertEqual(self.read_campaign()['unrun_profile_ids'],[])
        self.assertTrue(all(c.kwargs['shell'] is False for c in call.call_args_list))

    def test_timeout_retains_outputs_and_stops_second_profile(self):
        with patch.object(r.subprocess,'run',side_effect=subprocess.TimeoutExpired('test',90,output=b'partial',stderr=b'why')) as call:
            self.assertFalse(self.campaign())
        self.assertEqual(call.call_count,1)
        self.assertEqual((self.root/'capture/p01_b1/STDOUT.txt').read_bytes(),b'partial')
        self.assertEqual(self.read_campaign()['unrun_profile_ids'],['b16'])

    def test_nonzero_status_cannot_pass_raw_gate(self):
        def fail(command,**kwargs):
            self.native_success(command,**kwargs)
            return subprocess.CompletedProcess(command,2,'','')
        with patch.object(r.subprocess,'run',side_effect=fail):meta,ok=self.call_profile()
        self.assertFalse(ok);self.assertTrue(meta['raw_gate_passed'])

    def test_missing_raw_cannot_pass(self):
        with patch.object(r.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'','')):
            meta,ok=self.call_profile()
        self.assertFalse(ok);self.assertFalse(meta['raw_output_present'])

    def test_existing_capture_preserved(self):
        out=self.root/'capture';out.mkdir();(out/'sentinel').write_text('keep')
        with self.assertRaises(FileExistsError):self.campaign()
        self.assertEqual((out/'sentinel').read_text(),'keep')

    def test_expired_deadline_never_launches_native(self):
        with patch.object(r.subprocess,'run') as call:
            meta,ok=r.run_profile(self.binary,self.root/'profile',self.profile,90,-1,'fixed')
        self.assertFalse(ok);call.assert_not_called();self.assertEqual(meta['timeout_seconds'],0)

    def test_before_diagnostics_consume_native_budget(self):
        clock=[0.]
        def diag(deadline):clock[0]+=4;return {'batt':{'fixture':True}}
        with patch.object(r,'diagnostics',side_effect=diag),patch.object(r.time,'monotonic',side_effect=lambda:clock[0]), \
             patch.object(r.subprocess,'run',side_effect=self.native_success) as call:
            meta,ok=r.run_profile(self.binary,self.root/'profile',self.profile,90,10,'fixed')
        self.assertTrue(ok);self.assertEqual(call.call_args.kwargs['timeout'],6)

    def test_after_diagnostic_interrupt_keeps_executed_identity(self):
        with patch.object(r,'diagnostics',side_effect=[{'batt':{}},{'batt':{'error_type':'KeyboardInterrupt'}}]), \
             patch.object(r.subprocess,'run',side_effect=self.native_success):
            self.assertFalse(self.campaign())
        c=self.read_campaign();self.assertEqual(c['profiles'][0]['status'],'invalid');self.assertEqual(c['unrun_profile_ids'],['b16'])
        self.assertEqual((self.root/'capture/p01_b1/STDOUT.txt').read_text(),'complete')

    def test_attempt_exception_is_not_unrun(self):
        with patch.object(r,'run_profile',side_effect=KeyboardInterrupt):self.assertFalse(self.campaign())
        c=self.read_campaign();self.assertEqual(c['profiles'][0]['status'],'started');self.assertEqual(c['unrun_profile_ids'],['b16'])

    def test_unavailable_inventory_retains_all_planned_profiles(self):
        with patch('capture_inventory.capture',return_value={'hardware':{'gpu_inventory':{'devices':None}}}), \
             patch.object(r,'run_profile') as call:self.assertFalse(self.campaign())
        call.assert_not_called();self.assertEqual(self.read_campaign()['unrun_profile_ids'],['b1','b16'])

    def test_source_change_during_profile_closes_gate(self):
        with patch.object(r,'verify_freeze',return_value='changed'),patch.object(r.subprocess,'run',side_effect=self.native_success):
            meta,ok=self.call_profile()
        self.assertFalse(ok);self.assertTrue(meta['source_changed'])

    def test_actual_diagnostics_handle_interrupt_and_deadline(self):
        self.diag.stop()
        with patch.object(r.time,'monotonic',return_value=5),patch.object(r.subprocess,'run',side_effect=KeyboardInterrupt) as call:
            out=r.diagnostics(10);self.assertTrue(r.interrupted(out));self.assertEqual(call.call_args.kwargs['timeout'],5)
            call.reset_mock();out=r.diagnostics(3);call.assert_not_called();self.assertEqual(out['batt']['error_type'],'CampaignDeadline')

    def test_freeze_checks_inputs_and_binary(self):
        self.freeze.stop();src=self.root/'input.bin';src.write_bytes(b'source')
        (self.root/'DESIGN_FREEZE.json').write_text(json.dumps({'source_sha256':{'input.bin':r.sha(src)},'binary_sha256':r.sha(self.binary)}))
        r.verify_freeze(self.binary);src.write_bytes(b'corrupt')
        with self.assertRaises(ValueError):r.verify_freeze(self.binary)
        src.write_bytes(b'source');self.binary.write_bytes(b'corrupt')
        with self.assertRaises(ValueError):r.verify_freeze(self.binary)

if __name__=='__main__':unittest.main()
