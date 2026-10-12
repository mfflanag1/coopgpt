import unittest
from calibrate import run_gate
class GateTests(unittest.TestCase):
 def trial(self,passes):
  calls=[]
  def f(part,c):calls.append((part,c));return dict(status='completed',gate_passed=passes[(part,c)])
  return run_gate(f),calls
 def test_a_confirmation_failure_has_no_b_fallback(self):
  x,c=self.trial({('development','A'):True,('confirmation','A'):False});self.assertFalse(x['qualified']);self.assertEqual(c,[('development','A'),('confirmation','A')])
 def test_b_selected_only_after_a_development_failure(self):
  x,c=self.trial({('development','A'):False,('development','B'):True,('confirmation','B'):True});self.assertTrue(x['qualified']);self.assertEqual(c,[('development','A'),('development','B'),('confirmation','B')])
 def test_both_fail_no_confirmation(self):
  x,c=self.trial({('development','A'):False,('development','B'):False});self.assertIsNone(x['selected']);self.assertEqual(len(c),2)
 def test_fault_aborts_no_fallback(self):
  calls=[]
  def f(p,c):calls.append(c);raise RuntimeError('transport failed')
  with self.assertRaises(RuntimeError):run_gate(f)
  self.assertEqual(calls,['A'])
if __name__=='__main__':unittest.main()
