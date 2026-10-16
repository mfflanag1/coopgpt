from fractions import Fraction as F
import json
checks=[]
def ck(name,condition,value=None):
    if not condition:raise RuntimeError(name)
    checks.append({'check':name,'passed':True,'value':value})
x=F(7,20);B=1-x+x*x/2-x*x*x/6
ck('negative factor lower',B==F(33797,48000),str(B))
tail=(F(11,10)-B)/2
ck('tail charge',tail==F(19003,96000),str(tail))
delta=F(25,136)*F(161,136)
residual=delta-tail
ck('aggregate heavy witness',residual==F(545633,27744000)>0,str(residual))
ck('one heavy witness',residual/23==F(545633,638112000),str(residual/23))
ck('count at most23',20*F(6,5)==24)
print(json.dumps({'status':'PASS','arithmetic':'fractions.Fraction','checks':checks},indent=2))
