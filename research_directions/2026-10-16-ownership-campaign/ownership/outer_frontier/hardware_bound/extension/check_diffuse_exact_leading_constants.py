from fractions import Fraction as F
from math import factorial
import json
checks=[]
def ck(name,condition,value=None):
    if not condition:raise RuntimeError(name)
    checks.append({'check':name,'passed':True,'value':value})
elo=sum((F(1,factorial(j)) for j in range(9)),F(0));ehi=elo+F(1,factorial(9))*F(10,9)
ck('elementary e interval',F(65,24)<elo<ehi<F(11,4))
ck('hardware fragments sufficient',2*F(11,4)**7-1<3000)
ck('linear coefficient lower',(42*F(65,24)-57)/8==F(227,32))
positive=F(227,32)-F(2527,131072)
ck('positive finite actual gain',positive==F(927265,131072)>0,str(positive))
ck('branch and active owner counts',8*3000+8+2==24010)
print(json.dumps({'status':'PASS','arithmetic':'fractions.Fraction','checks':checks},indent=2))
