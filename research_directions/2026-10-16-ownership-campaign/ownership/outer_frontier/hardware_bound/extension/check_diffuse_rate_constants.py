from fractions import Fraction as F
from math import factorial
import json
checks=[]
def ck(name,cond,value=None):
    if not cond:raise RuntimeError(name)
    checks.append({'check':name,'passed':True,'value':value})
elo=sum((F(1,factorial(j)) for j in range(9)),F(0))
ehi=elo+F(1,factorial(9))*F(10,9)
ck('65/24 < e < 11/4',F(65,24)<elo<ehi<F(11,4))
ck('fragment count m3000 sufficient',2*F(11,4)**7-1<3000)
ck('linear gain >3/32',(42*F(65,24)-113)/8==F(3,32))
ck('quadratic error <2527/131072',F(7,16)*F(1,2048)*F(19,2)**2==F(2527,131072))
positive=F(3,32)-F(2527,131072)
ck('exact positive finite surplus',positive==F(9761,131072)>0,str(positive))
ck('fixed T1/4 lower coefficient positive',3*elo>7)
ck('asymptotic lower coefficient positive',elo>2)
print(json.dumps({'status':'PASS','arithmetic':'fractions.Fraction','checks':checks},indent=2))
