#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json

def exp_negative(x):
    x=F(x);s=F(1);term=F(1)
    for j in range(1,41):term*=-x/j;s+=term
    return s+term*(-x)/41,s

low12,up12=exp_negative(F(6,5))
low03,up03=exp_negative(F(3,10))
low1,up1=exp_negative(1)
low2,up2=exp_negative(2)
low87,up87=exp_negative(F(8,7))
checks={
 'exp(-6/5)>3/10':low12-F(3,10),
 'exp(-3/10)<3/4':F(3,4)-up03,
 'C^2 funding at pi=15/7':low1+low2/4-F(141,112)*up87,
}
for name,value in checks.items():
    if value<=0:raise RuntimeError(f'{name} failed: {value}')
result={'status':'PASS','exact_lower_margins':{k:str(v) for k,v in checks.items()},'approximate_margins':{k:float(v) for k,v in checks.items()}}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'minimum_margin':float(min(checks.values()))}))
