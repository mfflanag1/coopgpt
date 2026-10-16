#!/usr/bin/env python3
from fractions import Fraction as F
from math import factorial
import json

def ck(test,message):
 if not test:raise RuntimeError(message)
e_lo=sum((F(1,factorial(j)) for j in range(9)),F(0))
e_hi=e_lo+F(1,factorial(9))*F(10,9)
ck(e_lo>F(8,3),'c<3/16')
ck((e_hi-1)**2<3,'K squared<3')
ck(1+F(7,40)+F(3,16)*F(19,16)==F(1789,1280),'funding fraction')
ck(F(1789,1280)<F(7,5)<(1+1/(2*e_hi))**2,'funding comparison')
# Exact algebra checks at rational support inputs; these corroborate formulas,
# while the continuous sign proof is in the companion text.
count=0
for S in (F(1),F(3,2),F(2),F(3)):
 for b in (F(0),F(1,4),F(1,2),F(3,4)):
  for u in ((1+b)/2,F(1)):
   if b==0 and u==1:continue
   D=(S-b)+(u-b)*(S-u)/u**2
   eta_factor=(u-b)**2/(u**2*(S-b))
   lambda_qfactor=1+(u-b)*(S-u)/(u**2*(S-b))
   ck(lambda_qfactor+eta_factor==1+(u-b)/u**2,'A formula')
   ck(D/(S-b)==lambda_qfactor,'stationarity coefficient')
   ck(-(2*b+1)*b*b+(S+b+2*b*S)*b-b*S==2*b*b*(S-b),'Q left endpoint')
   ck(-(2*b+1)+(S+b+2*b*S)-b*S==(1+b)*(S-1),'Q right endpoint')
   count+=1
print(json.dumps({'status':'PASS','rational_formula_cases':count,'balanced_funding':'1789/1280','scope':'Exact constants and algebra corroboration; universal support signs are proved analytically.'},indent=2))
