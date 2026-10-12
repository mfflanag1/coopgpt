import unittest
import test_client as fixture
from client import run_trace

class MixedClientTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixture.ClientTests.setUpClass.__func__(cls)
 @classmethod
 def tearDownClass(cls):fixture.ClientTests.tearDownClass.__func__(cls)
 def test_independent_caps_transmitted_without_mutating_base(self):
  options={'num_predict':64,'num_ctx':4096}
  trace=[dict(request_id=str(i),prompt='ok',arrival_offset_s=0,max_output_tokens=n) for i,n in enumerate([64,192,384])]
  rows=run_trace(self.base,trace,'fixture',options,2)['requests']
  self.assertEqual([r['request_options']['num_predict'] for r in rows],[64,192,384])
  self.assertEqual(options,{'num_predict':64,'num_ctx':4096})
 def test_invalid_cap_fails_before_dispatch(self):
  for cap in [0,-1,1025,True,1.5]:
   with self.assertRaises(ValueError):run_trace(self.base,[dict(request_id='x',prompt='ok',arrival_offset_s=0,max_output_tokens=cap)],'fixture',{})
if __name__=='__main__':unittest.main()
