#!/usr/bin/env python3
from fractions import Fraction as F
from math import factorial
import json
checks={}
def ck(name,value):
    if not value: raise RuntimeError(name)
    checks[name]=True
e_lo=sum((F(1,factorial(k)) for k in range(9)),F(0))
e_hi=e_lo+F(1,factorial(9))*F(10,9)
ck('e lower gives c<3/16',e_lo>F(8,3))
ck('e upper gives negative saving >4/5',e_hi<F(25,9))
ck('K squared<3',(e_hi-1)**2<3)
ck('exp(1/4)>5/4 from quadratic Taylor',1+F(1,4)+F(1,4)**2/2>F(5,4))
ck('high-m derivative < -3/25',-1+F(16,25)*F(11,8)==-F(3,25))
y=F(11,32)
prod=F(29,32)*(1-y+y*y/2-y**3/6)
ck('cubic product exceeds 5/8',prod>F(5,8))
ck('7/5<C squared',F(7,5)<(1+1/(2*e_hi))**2)
ck('unresolved cap count <6',F(30,7)+1+1/(2*e_lo)<6)
ck('unresolved S<7/2',F(15,7)+1+1/(2*e_lo)<F(7,2))
ck('stronger unresolved S<10/3',F(15,7)+1+1/(2*e_lo)<F(10,3))
print(json.dumps({'status':'PASS','checks':checks,'cubic_product':str(prod),'scope':'Exact constants for the analytical theorem; no profile enumeration.'},indent=2))
