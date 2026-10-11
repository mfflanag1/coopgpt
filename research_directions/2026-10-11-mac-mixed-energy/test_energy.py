import unittest
from pathlib import Path
import energy

def fixture(second,cpu=1000,gpu=2000,ane=0,elapsed=1000):
 return f'''*** Sampled system activity (Sun Oct 11 16:29:{second:02d} 2026 -0400) ({elapsed}ms elapsed) ***
**** Processor usage ****
CPU Power: {cpu} mW
GPU Power: {gpu} mW
ANE Power: {ane} mW
Combined Power (CPU + GPU + ANE): {cpu+gpu+ane} mW
**** GPU usage ****
GPU Power: 9999 mW
'''
class EnergyTests(unittest.TestCase):
 def test_units_and_no_duplicate_gpu(self):
  got=energy.parse_text(fixture(10))
  self.assertEqual(got['errors'],[]);r=got['samples'][0]
  self.assertEqual(r['gpu_mw'],2000);self.assertEqual(r['gpu_j'],2);self.assertEqual(r['combined_j'],3)
 def test_actual_preflight(self):
  got=energy.parse_text((Path(__file__).parent/'ENERGY_PREFLIGHT.txt').read_text())
  self.assertEqual(got['errors'],[]);self.assertEqual(len(got['samples']),3)
  self.assertEqual(got['samples'][0]['cpu_mw'],20811);self.assertEqual(got['samples'][1]['gpu_mw'],166)
 def test_invalid_sample_is_not_silent_zero(self):
  for raw in [fixture(10).replace('ANE Power: 0 mW',''),fixture(10,elapsed=-1),fixture(10,cpu=-1)]:
   got=energy.parse_text(raw);self.assertTrue(got['errors'])
 def test_conservative_boundary_energy(self):
  samples=energy.parse_text(''.join(fixture(s) for s in range(10,21)))['samples']
  result=energy.energy_bounds(samples,'2026-10-11T20:29:12+00:00','2026-10-11T20:29:18+00:00')
  self.assertTrue(result['valid'],result['errors'])
  self.assertEqual(result['fully_inside_count'],4);self.assertEqual(result['possibly_overlapping_count'],8)
  self.assertEqual(result['lower_j']['combined'],12);self.assertEqual(result['upper_j']['combined'],24)
 def test_missing_coverage_and_clock_gap(self):
  samples=energy.parse_text(fixture(10)+fixture(11))['samples']
  self.assertFalse(energy.energy_bounds(samples,'2026-10-11T20:29:10+00:00','2026-10-11T20:29:12+00:00')['valid'])
  samples=energy.parse_text(fixture(10)+fixture(20))['samples']
  self.assertFalse(energy.energy_bounds(samples,'2026-10-11T20:29:12+00:00','2026-10-11T20:29:18+00:00')['valid'])
 def test_malformed_header_and_timezone(self):
  for corrupt in [fixture(11).replace('ms elapsed','elapsed'),fixture(11).replace('-0400','+0060'),fixture(11).replace('Sun Oct','Xyz Oct')]:
   self.assertTrue(energy.parse_text(fixture(10)+corrupt)['errors'])
 def test_prefix_drift_cannot_hide_in_final_total(self):
  elapsed=[1,2,2,2,.25,.25,.25,.25,1,1,1]
  raw=''.join(fixture(10+i,elapsed=1000*d) for i,d in enumerate(elapsed))
  samples=energy.parse_text(raw)['samples']
  got=energy.energy_bounds(samples,'2026-10-11T20:29:12+00:00','2026-10-11T20:29:18+00:00')
  self.assertFalse(got['valid']);self.assertIn('continuous timeline',' '.join(got['errors']))
if __name__=='__main__':unittest.main()
