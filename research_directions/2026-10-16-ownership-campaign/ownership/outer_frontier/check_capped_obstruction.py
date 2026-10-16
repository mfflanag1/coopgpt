"""Exact rational certificates used in the analytical cap obstruction."""
from fractions import Fraction as F
import json,math

def require(b,s):
 if not b:raise RuntimeError(s)

n=8
esum=sum((F(1,math.factorial(k)) for k in range(n+1)),F(0))
eupper=esum+F(n+2,(n+1)*math.factorial(n+1))
require(eupper<3,'e<3 certificate')
results=[]
for eta in (F(0),F(1,10000)):
 cap_growth_lower=F(1,24)-eta
 defect_lower=F(13,1152)-eta/3
 exponent_lower=F(7,24)-eta
 ratio_lower=F(3,4)*(1+exponent_lower+exponent_lower**2/2)
 require(cap_growth_lower>0,'cap status')
 require(defect_lower>0,'positive cap-retention defect')
 require(ratio_lower>1,'actual nested-payment gain')
 require(1-F(1,2)-eta>0,'positive grid')
 require(1<2-eta<=2,'outer ratio range')
 results.append({'eta':str(eta),'full_outer_ratio':str(2-eta),'cap_growth_strict_lower':str(cap_growth_lower),'capped_retention_defect_strict_lower':str(defect_lower),'own_payment_ratio_strict_lower':str(ratio_lower)})
require(results[1]['own_payment_ratio_strict_lower']==str(1+F(1330009,2400000000)),'printed ratio identity')
print(json.dumps({'status':'PASS','scope':'Rational certificates for the analytic three-owner obstruction; exponential comparison steps are in the proof.','e_rational_upper':str(eupper),'cases':results},indent=2))
