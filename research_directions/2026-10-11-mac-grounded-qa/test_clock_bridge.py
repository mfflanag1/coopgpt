import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import clock_bridge as c

def s(m,w=0,width=0):return dict(monotonic_before_ns=m,wall_ns=w,monotonic_after_ns=m+width)
class ClockTests(unittest.TestCase):
 def test_bracket_call_order(self):
  events=[];n=iter([100,120])
  def mono():events.append('m');return next(n)
  def wall():events.append('w');return 300
  self.assertEqual(c.paired_stamp(mono,wall),s(100,300,20));self.assertEqual(events,['m','w','m'])
 def test_duration_ignores_backward_wall(self):
  self.assertEqual(c.duration_bounds_s(s(10,9000000000),s(3000000010,1)),dict(lower_s=3,upper_s=3))
 def test_bounds_and_large_integer_precision(self):
  n=10**24
  self.assertEqual(c.duration_bounds_s(s(n,5,10),s(n+40,-100,10)),dict(lower_s=30e-9,upper_s=50e-9))
 def test_touching_brackets(self):self.assertEqual(c.duration_bounds_s(s(0,0,10),s(10,0,10)),dict(lower_s=0,upper_s=20e-9))
 def test_overlapping_rejected(self):
  with self.assertRaises(ValueError):c.duration_bounds_s(s(10,0,10),s(19,0,10))
 def test_offset_span_uses_outer_bounds(self):
  x=c.bridge_diagnostics([s(0,5,10),s(100,105,10)],max_bracket_s=10e-9,max_observed_offset_span_s=10e-9)
  self.assertTrue(x['valid']);self.assertEqual(x['observed_offset_span_s'],10e-9)
 def test_wall_jump_flagged(self):
  x=c.bridge_diagnostics([s(0,100),s(10**9,2*10**9+100)])
  self.assertFalse(x['valid']);self.assertEqual(x['observed_offset_span_s'],1)
 def test_wide_bracket_and_drift_retained(self):
  x=c.bridge_diagnostics([s(0,0,20_000_000),s(1_000_000_000,2_000_000_000)])
  self.assertFalse(x['valid']);self.assertEqual(len(x['errors']),2)
 def test_invalid_stamps(self):
  for bad in [s(True),s(-1),s(1,width=-1),dict(s(1),wall_ns=1.0),{},None]:
   with self.subTest(bad=bad),self.assertRaises(ValueError):c.duration_bounds_s(bad,s(10))
 def test_invalid_thresholds(self):
  for k in ('max_bracket_s','max_observed_offset_span_s'):
   for v in (-1,float('inf'),float('nan'),True,'a'):
    with self.subTest(k=k,v=v),self.assertRaises(ValueError):c.bridge_diagnostics([s(0),s(1)],**{k:v})
 def test_huge_finite_integer_tolerance(self):
  self.assertTrue(c.bridge_diagnostics([s(0),s(1,1)],max_bracket_s=10**1000,max_observed_offset_span_s=10**1000)['valid'])
 def test_invalid_sequence(self):
  for v in ([],[s(0)],[s(2),s(1)]):
   with self.assertRaises(ValueError):c.bridge_diagnostics(v)
 def test_no_mutation(self):
  a=[s(0,0),s(100,100)];b=copy.deepcopy(a);c.bridge_diagnostics(a);self.assertEqual(a,b)
if __name__=='__main__':unittest.main()
