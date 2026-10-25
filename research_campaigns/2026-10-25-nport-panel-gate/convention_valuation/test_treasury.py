import unittest
from treasury_benchmark import weights,loss,tangent,decimal_loss
class Tests(unittest.TestCase):
 def test_closed_form_one_year(self):
  p=100/(1.025**2)
  self.assertAlmostEqual(loss(p,100,1,.01),p-100/(1.03**2),places=12)
  self.assertAlmostEqual(loss(p,100,1,-.01),p-100/(1.02**2),places=12)
 def test_weight_geometry(self):
  self.assertEqual(weights(20),[0,0,0,.5,.5]);self.assertEqual(weights(40),[0,0,0,0,1]);self.assertEqual(weights(.01),[1,0,0,0,0]);self.assertAlmostEqual(sum(weights(27.123)),1)
 def test_positive_convexity_direction(self):
  self.assertLess(loss(100,200,30,.01),100*loss(100,200,30,.0001))
  self.assertGreater(-loss(100,200,30,-.01),loss(100,200,30,.01))
 def test_noncommutation(self):
  # Half the full-shock response differs from repricing at half the shock.
  self.assertLess(.5*loss(100,200,20,.01),loss(100,200,20,.005))
 def test_tangent_and_zero(self):
  self.assertEqual(loss(100,200,30,0),0)
  numerical=(loss(100,200,30,1e-7)-loss(100,200,30,-1e-7))/(2e-7)*.0001
  self.assertAlmostEqual(tangent(100,200,30),numerical,places=9)
 def test_independent_decimal(self):
  self.assertAlmostEqual(loss(55,100,20,.01),float(decimal_loss('55','100',7305,'365.25','.01')),places=12)
if __name__=='__main__':unittest.main()
