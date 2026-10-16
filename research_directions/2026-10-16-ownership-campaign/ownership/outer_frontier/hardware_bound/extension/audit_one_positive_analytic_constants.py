"""Exact elementary constants for the analytical one-positive hardware theorem."""
from fractions import Fraction as F
from pathlib import Path
import json

def exp_upper(x,degree):
 term=F(1);value=term
 for j in range(1,degree+1):
  term*=x/j;value+=term
 next_term=term*x/(degree+1)
 return value+next_term/(1-x/(degree+2))

def main():
 el=F(1957,720);eu=F(11743,4320)
 expu=exp_upper(F(171,250),8)
 checks={
  'e_upper_less_68_25':eu<F(68,25),
  'e_lower_greater_125_46':el>F(125,46),
  'square_root_e_half_greater_4_5':el>F(64,25),
  'negative_savings_fraction_greater_4_5':F(68359,85000)>F(4,5),
  'half_plus_c_upper':F(1,2)+F(23,125)==F(171,250),
  'exp_171_250_less_2':expu<2,
  'seven_fifths_less_C_squared':F(7,5)<(1+1/(2*eu))**2,
  'concave_chord_fraction':1-F(9,34)*F(1849,2500)==F(68359,85000),
 }
 if not all(checks.values()):raise RuntimeError({k:v for k,v in checks.items() if not v})
 out={'status':'PASS','checks':checks,'exp_171_250_upper':str(expu),'exp_upper_margin':str(2-expu),'scope':'Elementary constants only; analytical scalar reduction is in ONE_POSITIVE_HARDWARE_SEVEN_FIFTHS.txt.'}
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
