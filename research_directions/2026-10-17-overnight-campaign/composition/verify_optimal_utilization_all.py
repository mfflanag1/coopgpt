#!/usr/bin/env python3
from fractions import Fraction as Q
import itertools,json

def require(test,message):
 if not test:raise RuntimeError(message)
# Payments affine in x: constant + slope*x.
truth=[(Q(1),Q(0)),(Q(0),Q(1)),(Q(2),Q(-1))]
low_hide_c=[Q(1),Q(1),Q(1)];low_hide_a=[Q(1),Q(0),Q(2)]
requirements=[]
for coalition,low in [([0,1],low_hide_c),([0,2],low_hide_a)]:
 constant=sum(truth[i][0] for i in coalition)-sum(low[i] for i in coalition)
 slope=sum(truth[i][1] for i in coalition)
 requirements.append((constant,slope))
require(requirements==[(Q(-1),Q(1)),(Q(0),Q(-1))],'TCWM inequalities are x-1>=0 and -x>=0')
require(sum(x for x,y in requirements)==-1 and sum(y for x,y in requirements)==0,'sum is impossible -1>=0')
# Actual-owner games: low is unanimity ABC, high is unanimity AC.
def shapley(v):
 p=[Q(0)]*3
 for order in itertools.permutations(range(3)):
  S=frozenset()
  for i in order:
   T=S|{i};p[i]+=Q(v(T)-v(S),6);S=T
 return p
lo=shapley(lambda S:int({0,1,2}<=S));hi=shapley(lambda S:int({0,2}<=S))
require(lo==[Q(1,3)]*3 and hi==[Q(1,2),0,Q(1,2)],'exact Shapley games')
require(sum(lo[:2])-sum(hi[:2])==Q(1,6),'Shapley coalition gain')
print(json.dumps({'status':'PASS','arithmetic':'Fraction; analytic three-profile certificate',
 'true_payment_affine':truth,'low_hide_c':low_hide_c,'low_hide_a':low_hide_a,
 'TCWM_left_minus_right_coefficients':requirements,'sum_of_required_nonnegative_expressions':'-1',
 'Shapley_low':lo,'Shapley_high':hi,'Shapley_coalition_underreport_gain':Q(1,6)},default=str,indent=2))
