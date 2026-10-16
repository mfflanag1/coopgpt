"""Standalone exact weak-duality replay. No optimizer or builder is imported."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import hashlib
import json

BASE=Path(__file__).resolve().parent
PI=F(11,8); C_BAR=F(148,125); DELTA_BAR=F(23,125)
E_LOW=sum((F(1,factorial(j)) for j in range(9)),F(0))
E_HIGH=E_LOW+F(1,factorial(9))*F(10,9)
C_LOW=1+1/(2*E_HIGH); C_HIGH=1+1/(2*E_LOW)
c_low=C_LOW-1; c_high=C_HIGH-1; K_HIGH=E_HIGH-1
U_PARAMETERS=[F(j,100) for j in range(35,96,2)]+[F(1,2)]
ROLE_PARAMETERS=[F(j,10) for j in range(10)]
ENTROPY_PARAMETERS=[F(j,16) for j in range(17)]
YOUNG_PARAMETERS=[F(1,16),F(1,8),F(1,4),F(1,2),F(3,4),F(1),F(3,2),F(2)]
COORDINATE_CAPS=[F(1),C_BAR,F(1),C_BAR,F(3)]


def require(condition,message):
    if not condition:
        raise RuntimeError(message)


def negative_exp_polynomial(argument,degree):
    require(argument>=0,'Nonnegative Taylor argument required')
    return sum(((-argument)**j/factorial(j) for j in range(degree+1)),F(0))


PD_CONSTANTS={}
for u in U_PARAMETERS:
    lower=negative_exp_polynomial(1/u-1,25)/2
    upper=negative_exp_polynomial(1/u-1,24)/2
    a_lower=1-upper*(1+1/u)
    a_upper=1-lower*(1+1/u)
    require(0<lower<=upper and 0<a_lower<=a_upper,'PD signs')
    PD_CONSTANTS[u]=(lower,upper,a_lower,a_upper)
ROLE_CONSTANTS={t:(negative_exp_polynomial(t,24),
                   negative_exp_polynomial(1/t,48) if t else F(0))
                for t in ROLE_PARAMETERS}
ENTROPY_CONSTANTS={s:(negative_exp_polynomial(1-s,25)/2,
                       negative_exp_polynomial(1-s,24)/2)
                   for s in ENTROPY_PARAMETERS}


def reconstruct(s0,s1,d0,d1):
    constraints=[]
    def add(coefficients,rhs):
        constraints.append((list(map(F,coefficients)),F(rhs)))
    # x=(M,Z,v,zminus,Y). All coordinates are nonnegative.
    add([1,-1,0,0,0],0)
    add([-C_HIGH,1,0,0,0],0)
    add([0,-1,0,0,0],PI-s0)
    add([-1,1,1,0,0],1)
    add([0,1,1,0,0],F(3,2))
    add([0,0,1,1,0],1)
    add([F(4,3),0,1,-1,0],F(4,3))
    add([0,-1,0,1,0],0)
    add([1,0,0,0,0],1)
    add([C_LOW,-1,0,0,0],d1)
    add([-C_HIGH,1,0,0,0],-d0)
    add([0,0,0,0,1],3)
    for t in ROLE_PARAMETERS:
        exp_t,exp_inverse=ROLE_CONSTANTS[t]
        add([0,1,1-t,0,0],1+exp_t/2)
        add([-1-t*exp_inverse/2,1,1-t,0,0],1-t)
    for alpha in YOUNG_PARAMETERS:
        coefficient=K_HIGH*F(429,1000)/2
        add([2-coefficient*alpha,0,1-c_high,-c_high,0],
            2+coefficient*d1/alpha)
    for s in ENTROPY_PARAMETERS:
        t_lower,t_upper=ENTROPY_CONSTANTS[s]
        a_lower=s+c_low-t_upper
        a_upper=s+c_high-t_lower
        require(a_lower+F(1,2)>0,'Entropy spill lower positive')
        add([a_lower+F(1,2),0,a_lower,c_low-t_upper,0],
            d1+a_upper+F(1,2))
    add([F(65,64),0,F(1,2)+c_low,c_low-F(1,2),0],4*d1+F(65,64))
    for u in U_PARAMETERS:
        q_lower,q_upper,a_lower,a_upper=PD_CONSTANTS[u]
        lambda_upper=1-q_lower*(1+1/u-1/s0)
        eta_upper=q_upper/s0
        p_upper=K_HIGH*eta_upper
        mu_upper=K_HIGH**2*eta_upper**2/(4*a_lower)
        intercept=(s1-1)*(1-q_lower*(1+1/u-1/s1))
        require(lambda_upper>0 and intercept>=0,'PD interval coefficients')
        add([0,-p_upper,-lambda_upper,p_upper,1],intercept)
        add([0,-mu_upper-a_upper,-lambda_upper,mu_upper,1],
            intercept+a_upper*(PI-s0))
    saving_lower=F(2,5)*negative_exp_polynomial(s1-1+d1,25)
    require(saving_lower>0,'Positive negative-gap saving')
    return constraints,[F(0),F(0),-saving_lower,F(0),F(1)]


def weighted_upper(constraints,objective,entries):
    require(isinstance(entries,list),'Sparse weights must be a list')
    seen=set();weights=[]
    for entry in entries:
        require(isinstance(entry,list) and len(entry)==2,'Sparse entry shape')
        index,raw=entry
        require(type(index) is int and 0<=index<len(constraints) and index not in seen,
                'Invalid or duplicated dual row index')
        weight=F(raw)
        require(weight>=0,'Nonnegative dual weights required')
        weights.append((index,weight));seen.add(index)
    residual=[max(F(0),objective[j]-sum(
        weight*constraints[index][0][j] for index,weight in weights)) for j in range(5)]
    return sum(weight*constraints[index][1] for index,weight in weights)+sum(
        r*cap for r,cap in zip(residual,COORDINATE_CAPS))


def replay():
    path=BASE/'certificate.json'
    artifact=json.loads(path.read_text())
    target=F(artifact['target'])
    require(target in (F(81,50),F(323,200),F(8,5)),'Authorized target')
    require(F(artifact['PB'])==PI,'Effective-grid threshold')
    for label,expected in [('US',U_PARAMETERS),('TS',ROLE_PARAMETERS),
                           ('SS',ENTROPY_PARAMETERS),('AS',YOUNG_PARAMETERS)]:
        require(list(map(F,artifact[label]))==expected,'Supporting parameter manifest '+label)
    require(C_HIGH<C_BAR and c_high<DELTA_BAR,'Constant upper bounds')
    require(K_HIGH**2<3 and E_HIGH<F(25,9),'Four-fifths negative saving')
    require(c_high<F(429,1000)**2,'Square-root upper bound')
    # The u=1/2 positive dual row bounds actual Y below 3 before it is used
    # as a residual cap or an explicit polytope constraint.
    qlo,qhi,_,_=PD_CONSTANTS[F(1,2)]
    y_cap=(1-2*qlo)*(PI+C_BAR)+K_HIGH*qhi*C_BAR
    require(y_cap<3,'Noncircular Y upper cap')
    inner_lower=negative_exp_polynomial(C_HIGH,25)
    require(inner_lower>0,'Positive inner exponential bound')
    high_pi=1+negative_exp_polynomial(PI-1,24)*(PI+
        negative_exp_polynomial(inner_lower,24)/2)/2
    require(high_pi<F(8,5),'Separate high effective-grid eight-fifths bound')
    require(high_pi<target,'High effective-grid analytic regime')
    require(C_HIGH**2<target,'Physical power-bottleneck regime')
    ns,nd=artifact['NS'],artifact['ND']
    require(type(ns) is int and type(nd) is int and 1<=ns<=2048 and 1<=nd<=256,
            'Finite partition dimensions')
    cells=artifact['cells']
    require(len(cells)==ns*nd,'Complete continuous partition')
    maximum=F(-1); nonempty=0; geometric=0; dual_empty=0; total_weights=0
    for number,cell in enumerate(cells):
        si,di=divmod(number,nd)
        s0=1+(PI+C_BAR-1)*si/ns;s1=1+(PI+C_BAR-1)*(si+1)/ns
        d0=DELTA_BAR*di/nd;d1=DELTA_BAR*(di+1)/nd
        if cell.get('empty')=='geometric':
            require(s0>PI+C_HIGH-d0,'Geometric emptiness')
            require('weights' not in cell,'Conflicting empty certificate')
            geometric+=1;continue
        constraints,objective=reconstruct(s0,s1,d0,d1)
        require(len(constraints)==artifact['rows'],'Fixed row count')
        total_weights+=len(cell['weights'])
        if cell.get('empty')=='dual':
            impossible=weighted_upper(constraints,[F(0)]*5,cell['weights'])
            require(impossible<0,'Exact dual contradiction for empty rectangle')
            dual_empty+=1;continue
        require('empty' not in cell,'Unknown emptiness tag')
        bound=1+weighted_upper(constraints,objective,cell['weights'])
        require(bound<target,'Target failed at rectangle '+str(number))
        maximum=max(maximum,bound);nonempty+=1
    require(F(artifact['max_upper'])==maximum,'Maximum summary replay')
    require(artifact['above_target']==0,'No unverified cells claimed')
    return {'status':'PASS','target':str(target),'rectangles':ns*nd,
            'nonempty':nonempty,'geometric_empty':geometric,'dual_empty':dual_empty,
            'sparse_nonzero_weights':total_weights,
            'max_low_pi_upper_exact':str(maximum),'max_low_pi_upper_display':float(maximum),
            'high_pi_upper_display':float(high_pi),'power_upper_display':float(C_HIGH**2),
            'certificate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'arithmetic':'fractions.Fraction; signed Taylor remainders; nonnegative sparse dual weights with exact residual charges'}


if __name__=='__main__':
    print(json.dumps(replay(),indent=2,sort_keys=True))
