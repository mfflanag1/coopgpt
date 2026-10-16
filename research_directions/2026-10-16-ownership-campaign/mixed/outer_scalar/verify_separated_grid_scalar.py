#!/usr/bin/env python3
"""Exact interval certificate for five constants in the analytic proof."""
from fractions import Fraction as F
from pathlib import Path
import json

def exp_negative(x):
    x=F(x);s=F(1);term=F(1)
    for j in range(1,41):
        term*=-x/j;s+=term
    return s+term*(-x)/41,s

cl,cu=(v/2 for v in exp_negative(1))
# Positive B,T; broad interval operations keep every bound conservative.
Bl,Bu=1-2*cu,1-2*cl
Tl,Tu=2-3*cu,2-3*cl
V0_upper=Tu*Tu/(12*Bl)-F(1,4)
Vp_lower=F(1,4)-Tu/6
Vp_upper=F(1,4)-Tl/6
checks={
 'sqrt(e)<27/16 via e<(27/16)^2':F(729,256)-1/exp_negative(1)[0],
 'V(0)<27/1000':F(27,1000)-V0_upper,
 'Vprime(0)>0':Vp_lower,
 'Vprime(0)<9/1000':F(9,1000)-Vp_upper,
 'exp(-3/4)>15/32':exp_negative(F(3,4))[0]-F(15,32),
 'curvature margin exceeds 1/100':F(15,128)-F(7,66)-F(1,100),
 'quadratic maximum below 1/32':F(1,32)-F(621,20000),
 'c>2/11':cl-F(2,11),
 'c<1/5':F(1,5)-cu,
 'c^2>1/32':cl*cl-F(1,32),
}
for name,value in checks.items():
    if value<=0:raise RuntimeError(f'{name} failed: {value}')
result={'status':'PASS','exact_lower_margins':{k:str(v) for k,v in checks.items()},'approximate_margins':{k:float(v) for k,v in checks.items()}}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'minimum_margin':float(min(checks.values()))}))
