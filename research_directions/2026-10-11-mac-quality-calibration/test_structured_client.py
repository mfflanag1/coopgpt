import unittest,copy
import test_client as f
from client import run_trace
class StructuredTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):f.ClientTests.setUpClass.__func__(cls)
 @classmethod
 def tearDownClass(cls):f.ClientTests.tearDownClass.__func__(cls)
 def test_schema_and_large_cap_sent_but_gold_not_sent(self):
  schema={'type':'object'};job=dict(request_id='test',arrival_offset_s=0,prompt='ok',max_output_tokens=1024,format=schema,expected='NEVER_SEND')
  prior=copy.deepcopy(job)
  result=run_trace(self.base,[job],'fixture',{},2)
  with f.Handler.lock:body=f.Handler.starts[-1][2]
  self.assertEqual(body['format'],schema);self.assertEqual(body['options']['num_predict'],1024);self.assertNotIn('expected',body);self.assertNotIn('NEVER_SEND',str(body));self.assertEqual(job,prior)
  self.assertEqual(result['requests'][0]['request_prompt'],body['prompt']);self.assertEqual(result['requests'][0]['request_model'],body['model'])
  self.assertEqual(result['epoch_monotonic_ns'],result['started_stamp']['monotonic_after_ns']);self.assertGreaterEqual(result['finished_stamp']['monotonic_before_ns'],result['epoch_monotonic_ns'])
 def test_invalid_format_before_dispatch(self):
  for v in (True,123,[],{'bad':float('nan')}):
   with self.assertRaises(ValueError):run_trace(self.base,[dict(request_id='x',prompt='ok',arrival_offset_s=0,format=v)],'fixture',{})
if __name__=='__main__':unittest.main()
