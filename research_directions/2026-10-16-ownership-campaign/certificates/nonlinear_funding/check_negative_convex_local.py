#!/usr/bin/env python3
"""Independent finite corroboration of the negative-gap exact convex program."""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import random

BASE=Path(__file__).resolve().parent
D=Decimal
TOL=D('1e-61')


def require(ok,message):
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
    caps=[min(x,t) for x in long]
    q=(1-sum(caps)/t).exp()/2
    return [(1-q)*x+q*y for x,y in zip(short,caps)]


def local_vector(h,l):
    out=[D(0)]*len(h[0])
    for hr,lr in zip(h,l):
        out=[x+y for x,y in zip(out,primitive(hr,lr))]
    return out


def run():
    rng=random.Random(2026101605)
    e=D(1).exp()
    profiles=0
    actual_checks=0
    jensen_checks=0
    curvature_checks=0
    slope_checks=0
    smallest_margin=None
    for n in (3,5,9):
        for m in (1,2,5):
            for trial in range(15):
                h,l=[],[]
                for branch in range(m):
                    hw=[rng.randrange(1,5) for _ in range(n-1)]
                    h.append([Fraction(1,4*m)]+[Fraction(3*x,4*m*sum(hw)) for x in hw])
                    other=[rng.randrange(1,5) for _ in range(n-1)]
                    scale=rng.choice((Fraction(1),Fraction(3,2),Fraction(3)))
                    own=Fraction(1,4*m)*rng.choice((Fraction(1,4),Fraction(1,2),Fraction(3,4)))
                    l.append([own]+[scale*Fraction(x,m*sum(other)) for x in other])
                a=[sum(dec(row[k]) for row in h) for k in range(n)]
                full_z=local_vector(h,l)
                require(full_z[0]<a[0],'Negative full gap missing')
                p=[D(0)]+[rng.choice((D(0),D(1)/4,D(3)/4,D(1),D(2))) for _ in range(n-1)]
                threshold=D(3)/2+e*full_z[0]
                for k in range(1,n):
                    if sum(min(p[j]+full_z[j],D(1)) for j in range(n))>=threshold:
                        break
                    p[k]=D(1)
                full_s=sum(min(p[j]+full_z[j],D(1)) for j in range(n))
                require(full_s+TOL>=threshold,'Hardware restoration threshold not met')
                q0,qlo,ratios=[],[],[]
                for branch in range(m):
                    t=D(1)/m
                    r=sum(min(dec(l[branch][k]),t) for k in range(1,n))/t
                    require(r+TOL>=1,'Opposing local cover missing')
                    ratios.append(r)
                    q0.append((1-r).exp()/2)
                    qlo.append(q0[-1]*(-dec(l[branch][0])/t).exp())

                def evaluate(q):
                    altered=[row[:] for row in l]
                    u=[]
                    for branch in range(m):
                        t=D(1)/m
                        uj=-t*(q[branch]/q0[branch]).ln()
                        require(-TOL<=uj<=dec(l[branch][0])+TOL,'Recovered report outside box')
                        u.append(uj)
                        altered[branch][0]=max(D(0),min(uj,dec(l[branch][0])))
                    z=local_vector(h,altered)
                    b=[pk+zk for pk,zk in zip(p,z)]
                    caps=[min(x,D(1)) for x in b]
                    w=a[0]-b[0]
                    require(w>0,'Negative gap did not persist')
                    require(sum(caps)+TOL>=1,'Outer hardware short condition lost')
                    loss=w*(-sum(caps)).exp()
                    actual=primitive(a,b)[0]
                    require(abs(actual-(a[0]-e*loss/2))<=TOL,'Loss does not equal actual payment')
                    pattern=tuple(k for k in range(1,n) if b[k]>=1)
                    return loss,pattern,w,u,b

                samples=[]
                for sample in range(10):
                    q=[lo+(hi-lo)*D(rng.randrange(33))/32 for lo,hi in zip(qlo,q0)]
                    loss,pattern,w,u,b=evaluate(q)
                    actual_checks+=1
                    v=[D(rng.randrange(-7,8))/7 for _ in range(m)]
                    if not any(v):
                        v[0]=D(1)
                    xdir=D(0)
                    sdir=D(0)
                    weighted=D(0)
                    slope=D(0)
                    for j in range(m):
                        t=D(1)/m
                        xj=dec(h[j][0])+t-u[j]
                        vj=sum(min(dec(l[j][k]),t)-dec(h[j][k])
                               for k in range(1,n) if k not in pattern)
                        xdir+=xj*v[j]
                        sdir+=(vj-xj)*v[j]
                        weighted+=(t/q[j])*v[j]*v[j]
                        slope+=q[j]*vj*vj/t
                    require(slope<=2/e+TOL,'Weighted affine slope bound failed')
                    slope_checks+=1
                    hessian=(1+w)*weighted-2*xdir*sdir+w*sdir*sdir
                    lower=(1-1/e+w)*weighted
                    require(hessian+TOL>=lower,'Strict curvature lower bound failed')
                    margin=(hessian-lower)/weighted
                    smallest_margin=margin if smallest_margin is None else min(smallest_margin,margin)
                    curvature_checks+=1
                    samples.append((q,loss,pattern))
                for first,second in zip(samples,samples[1:]):
                    qa,fa,pa=first
                    qb,fb,pb=second
                    if pa!=pb:
                        continue
                    qm=[(x+y)/2 for x,y in zip(qa,qb)]
                    fm,pm,_,_,_=evaluate(qm)
                    require(pm==pa,'Affine cap region was not convex')
                    require(fm<=(fa+fb)/2+TOL,'Actual loss Jensen inequality failed')
                    jensen_checks+=1
                profiles+=1
    sources=('NEGATIVE_GAP_CONVEX_LOCAL_EXTENSION.txt','JOINT_RESPONSE_CONVEX_LOCAL_FRONTIER.txt','CONVEX_LOCAL_FOUR_PROGRAM_BOUND.txt')
    return {'status':'PASS','arithmetic':'90-digit Decimal finite corroboration; no numerical optimization claim',
            'negative_full_profiles':profiles,'actual_payment_identity_checks':actual_checks,
            'weighted_slope_checks':slope_checks,'strict_curvature_checks':curvature_checks,
            'same_cap_actual_loss_jensen_checks':jensen_checks,'minimum_normalized_curvature_margin':str(smallest_margin),
            'source_sha256':{name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in sources}}


if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=90
        print(json.dumps(run(),indent=2,sort_keys=True))
