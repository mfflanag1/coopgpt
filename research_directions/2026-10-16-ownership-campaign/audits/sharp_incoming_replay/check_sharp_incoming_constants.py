#!/usr/bin/env python3
from fractions import Fraction as F
from math import factorial
import json
checks=[]
def ck(name, condition, detail=None):
    if not condition:
        raise RuntimeError(name)
    checks.append({'check':name,'passed':True,'detail':detail})
e_lo=sum((F(1,factorial(i)) for i in range(9)),F(0))
e_hi=e_lo+F(1,factorial(9))*F(10,9)
ck('8/3 < e < 68/25 < 11/4',F(8,3)<e_lo<e_hi<F(68,25)<F(11,4))
ck('log10 < 7/3 via e^7 > 1000',e_lo**7>1000)
ck('sharp-constant combination sign',F(49,88)<F(2,3))
x=F(7,40)
a_hi=1+x+x*x/2+(x**3/6)/(1-x/4)
ck('exp(7/40) < 6/5',a_hi<F(6,5),str(a_hi))
y=F(7,12)
b_lo=1-y+y*y/2-y**3/6
ck('exp(-7/12) > 11/20',b_lo>F(11,20),str(b_lo))
factor=1+F(3,5)/(1+F(11,24)+F(11,24)**2/2)
ck('funding bound rational value',factor==F(12461,9005),str(factor))
ck('funding < 7/5',factor<F(7,5),str(F(7,5)-factor))
ck('7/5 < C^2',F(7,5)<F(161,136)**2)
# Combinatorial identities in sharp-diffuse construction, entirely rational.
for m in [2,3,10,100,1000]:
    z=F(1,2*m); a=F(1,m); b_A=z; b_B=3*z
    ck(f'diffuse profile identities m={m}',m*(a)==1 and 2*m*z==1 and m*(b_A+b_B)==2 and b_B<=1)
print(json.dumps({'status':'PASS','arithmetic':'fractions.Fraction','checks':checks},indent=2))
