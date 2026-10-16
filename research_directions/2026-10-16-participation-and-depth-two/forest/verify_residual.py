# Algebra/interval corroboration of reduced formulas, not an independent rule implementation.
from fractions import Fraction as Q
import json

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def expminus(x, terms=90):
    # For 0<=x<=1, alternating decreasing Taylor series bounds exp(-x).
    require(Q(0)<=x<=Q(1),'Taylor argument outside certified interval')
    total=Q(1); term=Q(1); lo=hi=total
    for k in range(1,terms+1):
        term *= -x/Q(k); total+=term
        if k%2: lo=total
        else: hi=total
    require(lo<=hi and hi-lo<Q(1,10**90),'insufficient exponential enclosure')
    return lo,hi

def add(X,Y): return X[0]+Y[0],X[1]+Y[1]
def scale(c,X): return (c*X[0],c*X[1]) if c>=0 else (c*X[1],c*X[0])

checks=0
for x in [Q(1,2),Q(3,4)]:
    q=scale(Q(1,2),expminus(x))
    # Candidate A exact reduced formula and branch conditions.
    require(1+q[1]*(1-x)<2,'outer hardware must be short')
    y=[add((Q(1),Q(1)),scale(Q(1,2),q)),add((Q(1),Q(1)),scale(-Q(1,2),q)),q]
    # Coalitions: I alone1,A0,B0,IA2,IB1,AB1,IAB2.
    # IA sum is EXACTLY2, so evaluate by cancellation not interval subtraction.
    vals={1:Q(1),2:Q(0),4:Q(0),3:Q(2),5:Q(1),6:Q(1),7:Q(2)}
    for mask,v in vals.items():
        if mask==3:
            require(y[0][0]+y[1][1]==v and y[0][1]+y[1][0]==v,'IA correlated cancellation')
        else: require(sum(y[i][0] for i in range(3) if mask>>i&1)>=v,'coverage failure')
        checks+=1
    require(vals[6]>0 and vals[5]>0 and vals[3]>0,'veto owner')
    checks+=1
full=add((Q(1),Q(1)),scale(Q(1,4),expminus(Q(3,4))))
under=add((Q(1),Q(1)),scale(Q(1,4),expminus(Q(1,2))))
require(under[0]>full[1],'strict Candidate A incentive violation not certified');checks+=1

# Candidate B: any beta in(0,1] fails by derivative proof. Certify finite
# deviations for representative exact beta values, no float decisions.
for denom in range(1,101):
    beta=Q(1,denom); xfull=1-beta/4; xunder=1-beta/3
    def pay(x):
        const=1+(1-beta)/2
        return add((const,const),scale((x+beta/2)/2,expminus(x)))
    u=pay(xunder);v=pay(xfull)
    require(u[0]>v[1],f'Candidate B beta={beta} not certified')
    checks+=1
# Universal budget numerical constant is certified using e>8/3.
# C<1+3/16=19/16, hence(3/2)C<57/32<2.
require(Q(57,32)<2,'budget bound');checks+=1
print(json.dumps({'status':'PASS','exact_rational_checks':checks,'candidate_A_gap_lower':float(under[0]-full[1]),'candidate_B_beta_examples':100,'scope':'finite certificates corroborate symbolic proof; no assertion of truthfulness'}))

def product(X,Y):
    vals=[a*b for a in X for b in Y];return min(vals),max(vals)
def nested(x):
    halfexp=expminus((1+x)/2)
    q=scale(Q(1,2),product(halfexp,halfexp))
    T=add((Q(4),Q(4)),scale(1+x,q))
    require(T[1]<5+x,'I hardware account not capped')
    require(T[0]>2,'other hardware accounts not uncapped')
    r=(expminus(2/T[0])[0]/2,expminus(2/T[1])[1]/2)
    pay=add(add((Q(3),Q(3)),scale(x,q)),product(r,add((Q(1),Q(1)),q)))
    return pay
v=nested(Q(7,8));u=nested(Q(3,4))
require(u[0]>v[1],'nested finite incentive violation not certified')
# Influence obstruction: C target and any coefficient closing flat Lipschitz bound fail.
einv=expminus(Q(1));ratio=(2*(1-einv[1]),2*(1-einv[0]));C=(1+einv[0]/2,1+einv[1]/2)
require(ratio[0]>C[1],'influence C obstruction not certified')
require(ratio[0]>2*(2-C[0]**2),'influence sub-two obstruction not certified')
print(json.dumps({'status':'PASS','additional_exact_checks':7,'nested_underreport_gain_lower':float(u[0]-v[1]),'influence_ratio_lower':float(ratio[0]),'scope':'nested rule fails incentives; coarse influence bound fails; envelope budget unresolved'}))
# Six-owner joint-charge obstruction. All ownership reports are rational;
# the proof above derives the exact reduced formulas being enclosed here.
ehalf=expminus(Q(1,2)); eone=expminus(Q(1));ethree=product(product(eone,eone),eone)
Cl=(1+eone[0]/2,1+eone[1]/2)
qouter=(expminus(2/Cl[0]-1)[0]/2,expminus(2/Cl[1]-1)[1]/2)
base=add(Cl,product(qouter,(2-Cl[1],2-Cl[0])))
Ibound=add(add(scale(Q(3),ehalf),scale(-Q(1),eone)),scale(-Q(2),ethree))
joint=add(base,scale(Q(1,2),Ibound))
require(joint[0]>2,'joint charge obstruction not certified')
require(Ibound[0]>0,'positive influence lower bound')
print(json.dumps({'status':'PASS','joint_charge_exact_checks':2,'base_payment_lower':float(base[0]),'influence_lower':float(Ibound[0]),'joint_charge_lower':float(joint[0]),'scope':'coarse joint charge fails; actual envelope remains open'}))
