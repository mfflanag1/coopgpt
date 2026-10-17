from fractions import Fraction as F
import json

def require(ok, message):
    if not ok:
        raise ValueError(message)

high = (F(20,19),F(1),F(10,9),F(1))
delta=F(1,100)
low=(high[0]-delta,high[1],high[2],high[3]-delta)
for caps in (high,low):
    a,b,d,e=caps
    t1=b/a
    t2=e/d
    require(F(7,8)<t2<t1<1,'upper branches and cross-edge strictness')
    old=(t1/2,1-t1/2,t2/2,1-t2/2)
    require(old[0]+old[1]==1 and old[2]+old[3]==1,'tight pair edges')
    require(old[0]+old[3]>1,'strict cross-edge')
    flows=(b,e)
    require(a*min(2*old[0],1)==flows[0],'KKT L1')
    require(b*min(2*old[1],1)==flows[0],'KKT H1')
    require(d*min(2*old[2],1)==flows[1],'KKT L2')
    require(e*min(2*old[3],1)==flows[1],'KKT H2')
    symbolic_log_payment = a*t1+e/t2
    require(symbolic_log_payment==F(19,9),'coalition payment divided by c')
require(low[1]/low[0]==F(1900,1981),'post-withholding first ratio')
require(low[3]/low[2]==F(891,1000),'post-withholding second ratio')
require(F(11,4)**2<8,'elementary exponential upper bound suffices')
print(json.dumps({'status':'PASS','withheld_outside_worth':str(delta),
 'mechanism_payment_loss_exact':'0','coalition_payment_divided_by_c':'19/9',
 'scope':'exact rational counterexample checks; class-wide lower uses analytic proof'},indent=2))
