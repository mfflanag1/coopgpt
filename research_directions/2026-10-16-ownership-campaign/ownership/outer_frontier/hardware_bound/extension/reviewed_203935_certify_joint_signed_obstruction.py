#!/usr/bin/env python3
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json,hashlib

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def lower(x,n):return sum((x**k/F(factorial(k)) for k in range(n+1)),F(0))
def upper(x,n):
    require(0<=x<n+2,'Taylor-tail domain')
    return lower(x,n)+x**(n+1)/F(factorial(n+1))/(1-x/F(n+2))

v=F(2,5);w=F(45,128)
elo=lower(v,4);whi=upper(w,12);ehi=upper(v,12)
checks={
 'exp_two_fifths_lower':elo>F(82,55),
 'joint_ratio_above_six_fifths':(11*elo-8)/7>F(6,5),
 'critical_root_above_45_over_128':w*whi<F(1,2),
 'Lambda_below_six_fifths':(1-w)**2/w==F(6889,5760)<F(6,5),
 'each_fragment_diffuse':ehi<F(3,2),
}
for key,ok in checks.items():require(ok,key)
p=Path(__file__).with_name('JOINT_SIGNED_RESPONSE_OBSTRUCTION.txt')
print(json.dumps({'status':'PASS','arithmetic':'exact Fraction Taylor inequalities',
 'checks':checks,'exp_lower':str(elo),'exp_upper_at_w':str(whi),
 'joint_ratio_exact_lower':str((11*elo-8)/7),
 'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2,sort_keys=True))
