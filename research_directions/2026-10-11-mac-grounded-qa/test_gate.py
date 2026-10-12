import unittest
from calibrate import run_gate, no_thinking
class GateTests(unittest.TestCase):
    def run_decision(self, passes):
        calls=[]
        def run(part):
            calls.append(part)
            return dict(status='completed',gate_passed=passes[part])
        return run_gate(run), calls
    def test_development_failure_stops(self):
        result,calls=self.run_decision({'development':False})
        self.assertEqual(calls,['development']);self.assertFalse(result['qualified']);self.assertIsNone(result['selected'])
    def test_confirmation_failure_has_no_retry(self):
        result,calls=self.run_decision({'development':True,'confirmation':False})
        self.assertEqual(calls,['development','confirmation']);self.assertFalse(result['qualified'])
    def test_qualification(self):
        result,_=self.run_decision({'development':True,'confirmation':True});self.assertTrue(result['qualified'])
    def test_fault_aborts(self):
        def fault(part):raise RuntimeError('infrastructure')
        with self.assertRaises(RuntimeError):run_gate(fault)
    def test_thinking_is_not_silently_ignored(self):
        self.assertTrue(no_thinking({'chunks':[{'data':{'response':'x'}},{'data':{'thinking':''}}]}))
        self.assertFalse(no_thinking({'chunks':[{'data':{'thinking':'hidden work'}}]}))
if __name__=='__main__':unittest.main()
