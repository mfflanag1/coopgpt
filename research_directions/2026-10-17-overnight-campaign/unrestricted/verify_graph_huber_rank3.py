if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
from fractions import Fraction as Q
import json
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
E=((0,3,6),(0,3,5),(0,5,6),(0,1,2),(1,4,5),(1,3,6))
b=tuple(map(Q,(0,0,1,3,1,3,3)));a=tuple(map(Q,(4,3,0,0,0,0,0)))
c=tuple(x+y for x,y in zip(a,b));p=(Q(1,3),)*7;lam=(Q(2,3),)*6
bp=list(b);bp[2]+=1;cp=tuple(x+y for x,y in zip(a,bp))
pp=tuple(Q(v,35) for v in (13,13,9,11,11,11,11))
ll=tuple(Q(v,35) for v in (24,22,22,36,22,20))
for cap,price,mult in ((c,p,lam),(cp,pp,ll)):
    require(all(0<t<Q(1,2) for t in price),'strict quadratic interior')
    require(all(l>0 for l in mult),'positive dual multipliers')
    require(all(sum(price[v] for v in edge)==1 for edge in E),'edge equalities')
    for v in range(7):
        require(sum(mult[j] for j,e in enumerate(E) if v in e)==2*cap[v]*price[v],'stationarity')
before=sum(x*y for x,y in zip(b,p));after=sum(x*y for x,y in zip(bp,pp))
require(before==Q(11,3) and after==Q(128,35),'payments')
require(before-after==Q(1,105),'strict incentive failure')
z=(-2,-2,4,1,1,1,1)
require(all(sum(z[v] for v in e)==0 for e in E),'kernel')
norm=sum(c[v]*z[v]**2 for v in range(7));require(norm==54,'weighted norm')
row=[Q(z[2])*c[v]*z[v]/norm for v in range(7)]
require(sum(max(Q(0),v) for v in row)==Q(28,27),'projection obstruction')
print(json.dumps({'status':'PASS_EXACT_KKT_AND_INCENTIVE_CERTIFICATE','old_payment':str(before),
 'new_payment':str(after),'profitable_underreport_gain':str(before-after),'positive_projection_sum':'28/27'},indent=2))
