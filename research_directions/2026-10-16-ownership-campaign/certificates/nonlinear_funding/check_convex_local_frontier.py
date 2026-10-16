#!/usr/bin/env python3
"""Finite high-precision checks of the exact frontier, not an optimization proof."""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import random

BASE=Path(__file__).resolve().parent
D=Decimal
TOL=D('1e-62')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def dec(x):
    return D(x.numerator)/D(x.denominator) if isinstance(x,Fraction) else D(x)


def primitive(a,b):
    a,b=list(map(dec,a)),list(map(dec,b))
    sa,sb=sum(a),sum(b)
    if min(sa,sb)==0:
        return [D(0)]*len(a)
    short,long=(a,b) if sa<=sb else (b,a)
    t=min(sa,sb)
    capped=[min(x,t) for x in long]
    q=(1-sum(capped)/t).exp()/2
    return [(1-q)*x+q*y for x,y in zip(short,capped)]


def local_vector(h,l):
    result=[D(0)]*len(h[0])
    for hr,lr in zip(h,l):
        result=[x+y for x,y in zip(result,primitive(hr,lr))]
    return result


def run():
    rng=random.Random(2026101603)
    e=D(1).exp()
    profiles=0
    response_checks=0
    objective_checks=0
    jensen_checks=0
    recovery_checks=0
    positive=0
    for n in (3,5,9):
        for m in (1,2,5):
            for trial in range(12):
                h,l=[],[]
                for branch in range(m):
                    hw=[1]+[rng.randrange(1,5) for _ in range(n-1)]
                    h.append([Fraction(v,m*sum(hw)) for v in hw])
                    others=[rng.randrange(1,5) for _ in range(n-1)]
                    scale=rng.choice((Fraction(1),Fraction(3,2),Fraction(3)))
                    l.append([rng.choice((Fraction(1,4),Fraction(1,2),Fraction(1),Fraction(2)))/m]
                             +[scale*Fraction(v,m*sum(others)) for v in others])
                a=[sum(dec(row[k]) for row in h) for k in range(n)]
                full_z=local_vector(h,l)
                p=[a[0]]+[rng.choice((D(0),D(1)/4,D(1)/2,D(1),D(2))) for _ in range(n-1)]
                threshold=D(3)/2+e*full_z[0]
                for k in range(1,n):
                    if sum(min(p[j]+full_z[j],D(1)) for j in range(n))>=threshold:
                        break
                    p[k]=D(1)
                full_s=sum(min(p[j]+full_z[j],D(1)) for j in range(n))
                require(full_s+TOL>=threshold,'Restoration threshold not met in test profile')
                require(min(p[0]+full_z[0],D(1))>a[0], 'Full positive gap missing')
                q0=[]
                qlo=[]
                for branch in range(m):
                    t=D(1)/m
                    othercaps=sum(min(dec(l[branch][k]),t) for k in range(1,n))
                    q0.append((1-othercaps/t).exp()/2)
                    qlo.append(q0[-1]*(-min(dec(l[branch][0]),t)/t).exp())

                def beta(q):
                    result=p[:]
                    for branch in range(m):
                        t=D(1)/m
                        hh=dec(h[branch][0])
                        result[0]+=hh-hh*q[branch]-t*q[branch]*(q[branch]/q0[branch]).ln()
                        for k in range(1,n):
                            hk=dec(h[branch][k])
                            ck=min(dec(l[branch][k]),t)
                            result[k]+=hk+q[branch]*(ck-hk)
                    return result

                def pattern(b):
                    return tuple(k for k in range(1,n) if b[k]>=1)

                def objective(b,x):
                    caps=sum(min(b[k],D(1)) for k in range(1,n))
                    return (x-a[0]).ln()-x-caps

                samples=[]
                for sample in range(8):
                    q=[lo+(hi-lo)*D(rng.randrange(17))/16 for lo,hi in zip(qlo,q0)]
                    recovered=[row[:] for row in l]
                    for branch in range(m):
                        t=D(1)/m
                        u=-t*(q[branch]/q0[branch]).ln()
                        require(u>=-TOL and u<=min(dec(l[branch][0]),t)+TOL,'Report recovery outside box')
                        recovered[branch][0]=max(D(0),min(u,dec(l[branch][0])))
                        recovery_checks+=1
                    z=local_vector(h,recovered)
                    b=beta(q)
                    require(max(abs(b[k]-p[k]-z[k]) for k in range(n))<=TOL,'Joint response mismatch')
                    response_checks+=n
                    require(sum(z)+TOL>=1,'Physical output not preserved')
                    x=min(b[0],D(1))
                    raw=primitive(a,[p[k]+z[k] for k in range(n)])[0]
                    if x>a[0]+TOL:
                        from_program=a[0]+e*objective(b,x).exp()/2
                        require(abs(raw-from_program)<=TOL,'Program objective mismatch')
                        # A relaxed hypograph point need not be physically real,
                        # but increasing it to the actual cap must improve the objective.
                        relaxed=(x+a[0])/2
                        require(objective(b,relaxed)<=objective(b,x)+TOL,'Hypograph monotonicity failed')
                        objective_checks+=1
                        positive+=1
                    samples.append((q,b,x))
                for first,second in zip(samples,samples[1:]):
                    qa,ba,xa=first
                    qb,bb,xb=second
                    qm=[(u+v)/2 for u,v in zip(qa,qb)]
                    bm=beta(qm)
                    require(bm[0]+TOL>=(ba[0]+bb[0])/2,'Own concavity failed')
                    require(max(abs(bm[k]-(ba[k]+bb[k])/2) for k in range(1,n))<=TOL,'Opponent affinity failed')
                    if pattern(ba)==pattern(bb) and min(xa,xb)>a[0]+TOL:
                        xm=(xa+xb)/2
                        require(xm<=bm[0]+TOL,'Mixed hypograph feasibility failed')
                        require(xm+sum(min(bm[k],D(1)) for k in range(1,n))+TOL>=1,'Mixed outer feasibility failed')
                        require(objective(bm,xm)+TOL>=(objective(ba,xa)+objective(bb,xb))/2,'Objective concavity failed')
                        jensen_checks+=1
                profiles+=1
    source='JOINT_RESPONSE_CONVEX_LOCAL_FRONTIER.txt'
    return {'status':'PASS','arithmetic':'90-digit Decimal finite corroboration; no numerical optimum used as proof',
            'full_profiles':profiles,'joint_recipient_response_checks':response_checks,
            'positive_gap_objective_checks':objective_checks,'same_cap_region_jensen_checks':jensen_checks,
            'actual_report_recovery_checks':recovery_checks,
            'source_sha256':{source:hashlib.sha256((BASE/source).read_bytes()).hexdigest()}}


if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=90
        print(json.dumps(run(),indent=2,sort_keys=True))
