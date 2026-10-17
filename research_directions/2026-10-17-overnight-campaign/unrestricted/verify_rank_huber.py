if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
from fractions import Fraction as Q
import json
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def h(t,r):return Q(r,2)*t*t if t<=Q(1,r) else t-Q(1,2*r)
cases=[]
for r in range(2,501):
    a=Q(r,2*(r-1));p0=1-Q(r-1,r)*a;pothers=a/r
    require(Q(0)<=a<=1,'domain');require(p0==Q(1,2),'optimizer price')
    require(pothers<=Q(1,r),'low region');require(p0+(r-1)*pothers==1,'edge feasible')
    require(a*min(r*p0,1)==a,'high stationarity')
    require(min(r*pothers,1)==a,'low stationarity')
    payment=a*p0;exact=Q(r,4*(r-1))
    require(payment==exact,'envelope identity')
    require(r*payment==Q(r*r,4*(r-1)),'total envelope')
    # Complete the square: q(a)-q(t)=((r-1)/r)(t-a)^2.
    for t in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
        q=t-Q(r-1,r)*t*t
        require(payment-q==Q(r-1,r)*(t-a)**2,'global quadratic maximum')
    if r>=3:require(payment>Q(1,r),'strict truthfulness failure')
    cases.append({'r':r,'underreport':str(a),'one_payment':str(payment),'total':str(r*payment)})
require(cases[1]['underreport']=='3/4' and cases[1]['one_payment']=='3/8','rank3 witness')
print(json.dumps({'status':'PASS_EXACT_ANALYTIC_IDENTITIES','ranks':len(cases),'rank3':cases[1],'last':cases[-1]},indent=2))
