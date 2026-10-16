"""Standalone exact replay ONLY for the closed S>=2 subregime.
No global eight-fifths result is claimed. No optimizer or builder is imported.
"""
from fractions import Fraction as F
from math import factorial, isqrt
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


def reconstruct_original(s0,s1,d0,d1):
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


CAP_PARAMETERS=[F(j,40) for j in range(18,33)]
CAP_TANGENTS=[F(j,8) for j in range(1,9)]
SPILL_WEIGHTS=[F(2),F(8),F(32),F(128)]
K_LOW=E_LOW-1
TARGET=F(8,5)


def rational_sqrt_upper(value):
    require(value>=0,'Square root input')
    scale=10**12
    upper=F(isqrt(value.numerator*scale**2//value.denominator)+1,scale)
    require(upper**2>value,'Certified square root upper bound')
    return upper


def reconstruct(s0,s1,d0,d1,one_cap):
    constraints,_=reconstruct_original(s0,s1,d0,d1)
    def add(coefficients,rhs):
        constraints.append((list(map(F,coefficients)),F(rhs)))
    for eta in SPILL_WEIGHTS:
        spill=1+1/(16*eta)
        add([spill,0,F(1,2)+c_low,c_low-F(1,2),0],eta*d1+spill)
    if one_cap:
        require(1<=s0<=s1<=2 and s0<2,'One-cap row only below S=2; upper enclosure may equal 2')
        for u in CAP_PARAMETERS:
            q_low=negative_exp_polynomial(1/u-1,25)/2
            q_high=negative_exp_polynomial(1/u-1,24)/2
            a_low=1-q_high*(1+1/u);a_high=1-q_low*(1+1/u)
            require(a_low>0 and a_high>0,'One-cap positive A')
            lambda_high=1-q_low*(1+1/u-1/s0)
            phi_high=(s1-1)*(1-q_low*(1+1/u-1/s1))
            p_high=K_HIGH*q_high/s0
            mu_high=K_HIGH**2*(q_high/s0)**2/(4*a_low)
            mu_low=K_LOW**2*(q_low/s1)**2/(4*a_high)
            b_high=q_high*(1+1/u-1/s1)
            kappa_high=max(F(0),p_high-mu_low)*b_high/(b_high+(1-c_high)*p_high)
            for s in CAP_TANGENTS:
                t_high=negative_exp_polynomial(1-s,24)/2
                intercept=2-c_low+d1/s
                coefficient=(t_high-c_low)/s-1
                add([-kappa_high*coefficient,-mu_high,-lambda_high,mu_high,1],
                    phi_high+kappa_high*intercept)
    else:
        require(s0>=2,'General-row partition starts at closed S=2')
    q_high=negative_exp_polynomial(s0-1,24)/2
    exp_negative_k_lower=negative_exp_polynomial(K_HIGH,25)
    require(exp_negative_k_lower>0,'Reciprocal exponential lower bound')
    beta_high=(1/exp_negative_k_lower-2)/(1-c_high)
    beta_c=beta_high*C_BAR
    add([q_high*beta_c,-F(3,4)*q_high,-2*q_high,F(3,4)*q_high,1],
        2*q_high*(s1-1)+q_high*beta_c*(1+K_HIGH*rational_sqrt_upper(c_high*d1)))
    return constraints


def validate_external_regimes():
    require(C_HIGH<C_BAR and c_high<DELTA_BAR,'Global constant upper bounds')
    require(K_HIGH**2<3 and E_HIGH<F(25,9),'Uniform four-fifths saving')
    require(c_high<F(429,1000)**2,'Old Young square-root upper bound')
    require(F(4,15)*K_HIGH**2<4,'Nonnegative grouped curved saving')
    qlo,qhi,_,_=PD_CONSTANTS[F(1,2)]
    require((1-2*qlo)*(PI+C_BAR)+K_HIGH*qhi*C_BAR<3,'Independent Y cap')
    inner=negative_exp_polynomial(C_HIGH,25)
    require(inner>0,'High-grid inner exponential')
    high_grid=1+negative_exp_polynomial(PI-1,24)*(PI+
        negative_exp_polynomial(inner,24)/2)/2
    require(high_grid<TARGET and C_HIGH**2<TARGET,'External regimes below target')
    return high_grid


def replay_partition(filename,one_cap):
    path=BASE/filename
    artifact=json.loads(path.read_text())
    require(F(artifact['target'])==TARGET,'Frozen target')
    require(artifact['delta_partition']=='quadratic','Exact delta partition')
    require(list(map(F,artifact['CAP_US']))==(CAP_PARAMETERS if one_cap else []),'Cap parameter manifest')
    require(list(map(F,artifact['CAP_SS']))==CAP_TANGENTS,'Cap tangent manifest')
    require(list(map(F,artifact['ETAS']))==SPILL_WEIGHTS,'Parametric spill manifest')
    require(F(artifact['S_upper'])==(F(2) if one_cap else PI+C_BAR),'Exact S upper endpoint')
    if not one_cap:require(F(artifact['S_lower'])==2,'Closed high-S lower endpoint')
    ns,nd=artifact['NS'],artifact['ND']
    require(type(ns) is int and type(nd) is int and 1<=ns<=2048 and 1<=nd<=256,'Partition sizes')
    require(len(artifact['cells'])==ns*nd,'Complete rectangular root partition')
    stats={'leaves':0,'geometric':0,'dual_empty':0,'uniform':0,'chord':0,'failed':0,'max_depth':0}
    maximum=F(-1);nweights=0
    def visit(node,s0,s1,d0,d1,v0=F(0),v1=F(1),depth=0,constraints=None):
        nonlocal maximum,nweights
        require(isinstance(node,dict) and depth<=30,'Finite certificate tree')
        stats['max_depth']=max(stats['max_depth'],depth)
        if 'split' in node:
            require(set(node)=={'split','children'} and len(node['children'])==2,'Complete binary split')
            which=node['split'];left,right=node['children']
            if which=='v':
                mid=(v0+v1)/2
                visit(left,s0,s1,d0,d1,v0,mid,depth+1,constraints)
                visit(right,s0,s1,d0,d1,mid,v1,depth+1,constraints)
            elif which=='delta':
                mid=(d0+d1)/2
                visit(left,s0,s1,d0,mid,v0,v1,depth+1)
                visit(right,s0,s1,mid,d1,v0,v1,depth+1)
            elif which=='S':
                mid=(s0+s1)/2
                visit(left,s0,mid,d0,d1,v0,v1,depth+1)
                visit(right,mid,s1,d0,d1,v0,v1,depth+1)
            else:raise RuntimeError('Unknown split coordinate')
            return
        if node.get('empty')=='geometric':
            require(set(node)=={'empty'} and s0>PI+C_HIGH-d0,'Exact geometric emptiness')
            stats['geometric']+=1;return
        require('failed_upper' not in node,'Unresolved leaf forbidden')
        if constraints is None:constraints=reconstruct(s0,s1,d0,d1,one_cap)
        require(len(constraints)==artifact['base_rows'],'Reconstructed row count')
        rows=constraints+[(list(map(F,[0,0,1,0,0])),v1),(list(map(F,[0,0,-1,0,0])),-v0)]
        nweights+=len(node['weights'])
        if node.get('empty')=='dual':
            require(set(node)=={'empty','weights'},'Dual-empty leaf schema')
            require(weighted_upper(rows,[F(0)]*5,node['weights'])<0,'Exact Farkas contradiction')
            stats['dual_empty']+=1;return
        require(set(node)=={'objective','weights'},'Certified leaf schema')
        b_lower=negative_exp_polynomial(s1-1+d1,25)/2
        require(b_lower>0,'Positive exponential saving')
        kind=node['objective']
        if kind=='uniform':objective=[F(0),F(0),-F(4,5)*b_lower,F(0),F(1)]
        elif kind=='chord':objective=[F(0),F(0),-b_lower,b_lower*F(4,15)*K_HIGH**2*v1**2,F(1)]
        else:raise RuntimeError('Unknown objective')
        bound=1+weighted_upper(rows,objective,node['weights'])
        require(bound<TARGET,'Eight-fifths failed on '+str((s0,s1,d0,d1,v0,v1)))
        maximum=max(maximum,bound);stats['leaves']+=1;stats[kind]+=1
    for number,cell in enumerate(artifact['cells']):
        si,di=divmod(number,nd)
        low=F(1) if one_cap else F(2)
        length=F(1) if one_cap else PI+C_BAR-2
        visit(cell,low+length*si/ns,low+length*(si+1)/ns,
            DELTA_BAR*F(di,nd)**2,DELTA_BAR*F(di+1,nd)**2)
    require(stats==artifact['statistics'],'Exact tree statistics')
    require(maximum==F(artifact['max_upper']),'Exact maximum summary')
    return {'file':filename,'status':'PASS','semantics':'1<=S<2' if one_cap else '2<=S<=Pi+Cbar',
        **stats,'weights':nweights,'max_exact':str(maximum),'max_display':float(maximum),
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def replay_obstruction():
    path=BASE/'finite_support_obstruction.json'
    data=json.loads(path.read_text())
    s,delta,v=F(data['S']),F(data['delta']),F(data['v'])
    require((s,delta,v)==(F(47,25),F(1,125),F(1,30)),'Frozen rational relaxation point')
    rows=reconstruct(s,s,delta,delta,True)
    q=negative_exp_polynomial(s-1,24)/2
    beta=(1/negative_exp_polynomial(K_HIGH,25)-2)/(1-c_high)
    require(list(map(F,data['inverse_tangents']))==CAP_TANGENTS,'Finite inverse-support manifest')
    for tangent in CAP_TANGENTS:
        t_high=negative_exp_polynomial(1-tangent,24)/2
        intercept=1-c_low+delta/tangent
        coefficient=(t_high-c_low)/tangent-1
        rows.append(([-q*beta*C_BAR*coefficient,-F(3,4)*q,-2*q,F(3,4)*q,F(1)],
            2*q*(s-1)+q*beta*C_BAR*intercept))
    require(len(rows)==data['rows']==255,'Frozen finite supporting-row set')
    point=list(map(F,data['point']))
    require(len(point)==5 and point[2]==v,'Point dimensions and negative gap')
    require(all(0<=x<=cap for x,cap in zip(point,COORDINATE_CAPS)),'Coordinate bounds')
    slacks=[rhs-sum(a*x for a,x in zip(row,point)) for row,rhs in rows]
    require(min(slacks)>0 and min(slacks)==F(data['minimum_slack']),'Strict exact feasibility of every finite row')
    b=negative_exp_polynomial(s-1+delta,25)/2
    objective=[F(0),F(0),-b,b*F(4,15)*K_HIGH**2*v**2,F(1)]
    require(objective==list(map(F,data['objective'])),'Exact frozen relaxation objective')
    value=1+sum(a*x for a,x in zip(objective,point))
    require(value==F(data['objective_value']) and value>F(8,5),'Finite relaxation cannot certify 8/5')
    return {'status':'PASS','scope':'Finite 255-row rational relaxation only; no actual-profile lower bound and no all-parameter obstruction',
        'point':list(map(str,point)),'objective_exact':str(value),'objective_display':float(value),
        'minimum_slack_exact':str(min(slacks)),'rows':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def replay():
    high=validate_external_regimes()
    upper=replay_partition('high_S_certificate.json',False)
    obstacle=replay_obstruction()
    return {'status':'PASS','target':'8/5','scope':'High-S subregime proved; global 8/5 remains unproved',
        'high_S':upper,'finite_support_obstruction':obstacle,
        'high_grid_upper':float(high),'physical_power_upper':float(C_HIGH**2),
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'arithmetic':'Exact Fraction replay; no builder or optimizer imports; closed S>=2 partition plus finite-row obstruction.'}


if __name__=='__main__':
    print(json.dumps(replay(),indent=2,sort_keys=True))
