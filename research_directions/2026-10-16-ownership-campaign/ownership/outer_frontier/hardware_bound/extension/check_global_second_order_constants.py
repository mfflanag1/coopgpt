"""Exact rational checks of elementary signs; analytic proof is in the note."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json
lo=sum((F(1,factorial(k))for k in range(9)),F(0))
# Remaining terms begin at 1/9!, and later ratios are at most 1/10.
hi=lo+F(1,factorial(9))/(1-F(1,10))
checks={
 'e_lower_eight_thirds':lo>F(8,3),
 'e_upper_eleven_fourths':hi<F(11,4),
 'negative_restoration_sqrt_e_gt_three_halves':lo>F(9,4),
 'positive_restoration_coefficient_lt_three':2+2/lo<F(11,4)<3,
 'small_S_gap_sqrt_e_lt_two':hi<4,
 'all_positive_local_derivative_lt_seven_fourths':1+2/lo<F(7,4),
 'large_S_threshold_feasible_for_small_epsilon':F(3,2)+hi*F(1,10)<2,
}
if not all(checks.values()):raise RuntimeError(checks)
out={'status':'PASS','checks':checks,'e_lower':str(lo),'e_upper':str(hi),
 'scope':'Elementary rational signs only; global proof, calculus and asymptotics are analytic.'}
Path(__file__).with_name('global_second_order_constants.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
