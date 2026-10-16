from fractions import Fraction as F
from pathlib import Path
import json

def main():
 el=F(1957,720);eu=F(11743,4320)
 checks={
  'negative_saving_less_one_eighth':el>F(64,25),
  'parameter_coefficient':F(14017,10000)-1+F(1,8)==F(5267,10000),
  'quarter_exponential_less_nine_sevenths':eu<F(68,25)<F(9,7)**4,
  'quarter_bound_fraction':F(7,8)+F(5267,10000)*F(9,7)==F(108653,70000),
  'quarter_bound_less_25_16':F(108653,70000)<F(25,16),
  'zero_overlap_target_less_C_squared':F(14017,10000)<(1+1/(2*eu))**2,
 }
 if not all(checks.values()):raise RuntimeError('exact overlap constant failure')
 out={'status':'PASS','checks':checks,'scope':'Constants only; the cap-safe exponential majorant and use of the prior high-total scalar certificate are proved in FULL_UTILIZATION_OVERLAP_PARAMETER.txt.'}
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
