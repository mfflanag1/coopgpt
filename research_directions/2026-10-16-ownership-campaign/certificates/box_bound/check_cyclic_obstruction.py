#!/usr/bin/env python3
"""Exact-rational exponential enclosure plus independent cyclic-family replay.
The mathematical family proof is in CYCLIC_THREE_HALVES_OBSTRUCTION.txt.
Fractions prove the strict inequality. Float replay corroborates implementation.
"""
from fractions import Fraction as Q
from math import exp
from pathlib import Path
import json, sys

BASE=Path(__file__).parent

def taylor_exp_minus(x,degree):
    if x<0:raise ValueError('nonnegative exponential argument required')
    term=Q(1);total=term
    for k in range(1,degree+1):
        term *= -x/k
        total += term
    return total

def exp_interval(x):
    # Taylor's Lagrange remainder has the sign of the first omitted term.
    # For x>=0, odd partial sum <= exp(-x) <= even partial sum.
    return taylor_exp_minus(x,25),taylor_exp_minus(x,24)

def decimal_enclosure(lo,hi,digits=15):
    scale=10**digits
    floor=(lo.numerator*scale)//lo.denominator
    ceil=-((-hi.numerator*scale)//hi.denominator)
    return Q(floor,scale),Q(ceil,scale)

def fs(q):return f'{q.numerator}/{q.denominator}'

def exact_certificate():
    r=Q(19,10);s=Q(83,40)
    eL,eU=exp_interval(r-1)
    qL,qU=decimal_enclosure(eL/2,eU/2)
    aL,aU=r*qL,r*qU
    bL,bU=1-qU,1-qL
    zL,zU=1+(r-1)*qL,1+(r-1)*qU
    if not (0<qL<qU<Q(1,2) and 0<aL<aU<s and 0<bL<bU<zL<zU<s):
        raise ArithmeticError('parameter ordering failed')
    # n>=3 guarantees every outer hardware account s <= n*b.
    if not s<3*bL:raise ArithmeticError('uncapped-hardware condition failed')
    posL=exp_interval(s/zL-1)[0]
    posU=exp_interval(s/zU-1)[1]
    negL=exp_interval(s/bL-1)[0]
    negU=exp_interval(s/bU-1)[1]
    gL=zL+(s-aU)*posL/2-bU*negU/2
    gU=zU+(s-aL)*posU/2-bL*negL/2
    if not gL>Q(15001,10000):raise ArithmeticError('strict 1.5001 certificate failed')
    rounded=decimal_enclosure(gL,gU)
    # Actual-envelope consequence of the response-coupling lemma, k=2.
    inv_eL,inv_eU=exp_interval(Q(1))
    eL,eU=1/inv_eU,1/inv_eL
    kL,kU=2/(2*eU-1),2/(2*eL-1)
    if not (1+kU)*bU<s:raise ArithmeticError('coupled total regime failed')
    coupled_negative_lower=exp_interval(s/((1+kL)*bL)-1)[0]
    actual_envelope_upper=zU+(s-aL)*posU/2-bL*coupled_negative_lower/2
    if not actual_envelope_upper<Q(1401,1000):raise ArithmeticError('actual-envelope bound failed')
    return {'status':'EXACT PASS','r':fs(r),'s':fs(s),'hardware_per_branch':[fs(s-r+1),fs(r-1)],'q_interval':[fs(qL),fs(qU)],'g_interval':[fs(x) for x in rounded],'strictly_exceeds':'15001/10000','actual_envelope_strict_upper_bound':'1401/1000','method':'Fraction arithmetic; degree-25 lower and degree-24 upper Taylor bounds for exp(-x); outward rational rounding','n_condition':'all integers n>=3'}

def primitive(a,b):
    # Independent implementation, not imported from the source implementation.
    A=sum(a);B=sum(b);T=min(A,B)
    if T<=0:return [0.]*len(a)
    if A<=B:
        q=.5*exp(1-sum(min(y,T) for y in b)/T)
        return [(1-q)*x+q*min(y,T) for x,y in zip(a,b)]
    q=.5*exp(1-sum(min(x,T) for x in a)/T)
    return [(1-q)*y+q*min(x,T) for x,y in zip(a,b)]

def rows(n,r=Q(19,10),s=Q(83,40)):
    result=[]
    for i in range(n):
        h=[Q(0)]*n
        h[i]=s-r+1
        h[(i-1)%n]=r-1
        result.append([Q(0)]+h+[Q(0)]*n)
    result.append([Q(0)]+[Q(0)]*n+[Q(1)]*n)
    return result

def replay():
    sys.path.insert(0,'/private/tmp/coopgpt-ownership-20261016/mixed')
    from owner_box_reference import box_range_rule
    r=1.9;s=83/40;q=.5*exp(1-r);a=r*q;b=1-q;z=a+b
    q0=.5*exp(1-s/z);q1=.5*exp(1-s/b)
    g=z+(s-a)*q0-b*q1
    records=[]
    for n in [3,4,5,7,11,23]:
        rr=[[float(v) for v in row] for row in rows(n)]
        answer,w,lo,up,K,v=box_range_rule(rr)
        expected=[a+(s-a)*q0]*n+[n*b*(1-q1)]
        tol=2e-11*n
        if any(abs(x-y)>tol for x,y in zip(answer,expected)):
            raise ArithmeticError(f'formula mismatch n={n}')
        if abs(sum(answer)/v['F']-g)>tol:raise ArithmeticError('ratio mismatch')
        # Independently recompute branch primitives and outer payments.
        zvec=[0.]*(n+1)
        for j in range(n):
            pp=primitive([row[1+j] for row in rr],[row[1+n+j] for row in rr])
            zvec=[x+y for x,y in zip(zvec,pp)]
        H=[s]*n+[0.]
        nested=primitive(H,zvec)
        power_aux=[0.]*n+[n*b]
        power_value=primitive(H,power_aux)[-1]
        if abs(power_value-answer[-1])>tol:raise ArithmeticError('power witness failed')
        if any(abs(nested[i]-answer[i])>tol for i in range(n)):
            raise ArithmeticError('hardware baseline failed')
        if abs(K-n*z)>tol:raise ArithmeticError('local total ceiling mismatch')
        # Null-owner invariance at evaluated profile (no merger claim).
        augmented=rr+[[0.]*(2*n+1)]
        aug,*_=box_range_rule(augmented)
        if abs(aug[-1])>tol or any(abs(x-y)>tol for x,y in zip(aug[:-1],answer)):
            raise ArithmeticError('null-owner invariance failed')
        records.append({'n_hardware_owners':n,'n_actual_owners':n+1,'n_branches':n,'ratio':sum(answer)/v['F'],'max_payment_error':max(abs(x-y) for x,y in zip(answer,expected))})
    return {'status':'FLOAT CORROBORATION PASS','scope':'finite replay of a separately proved all-n family, not a universal funding bound','records':records}

if __name__=='__main__':
    out={'exact_certificate':exact_certificate(),'implementation_replay':replay()}
    (BASE/'cyclic-obstruction-certificate.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
