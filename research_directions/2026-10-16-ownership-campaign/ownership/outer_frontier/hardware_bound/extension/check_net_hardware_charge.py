#!/usr/bin/env python3
"""Finite 90-digit direct-primitive checks; not a replacement for the all-real proof."""
from decimal import Decimal,localcontext
from pathlib import Path
import random,json,hashlib
D=Decimal

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

def primitive(a,b):
    sa,sb=sum(a),sum(b)
    if min(sa,sb)==0: return [D(0)]*len(a)
    s,l=(a,b) if sa<=sb else (b,a)
    T=min(sa,sb); caps=[min(x,T) for x in l]
    q=(1-sum(caps)/T).exp()/2
    return [(1-q)*x+q*y for x,y in zip(s,caps)]

def run():
    rng=random.Random(2026101702);e=D(1).exp();K=e-1;c=1/(2*e);tol=D('1e-65')
    checks=switches=net_checks=own_checks=0
    for _ in range(10000):
        n=rng.randrange(2,10)
        raw=[D(rng.randrange(1,21)) for _ in range(n)]
        short=[v/sum(raw) for v in raw]
        long=[D(rng.randrange(0,21))/20 for _ in range(n)]
        long[0]+=D(1)
        # Include many near-balanced, switchable long pools.
        target=D(rng.randrange(1000,3001))/1000
        long=[v*target/sum(long) for v in long]
        own_new=long[0]*D(rng.randrange(1001))/1000
        altered=long[:];altered[0]=own_new
        rho=sum(min(v,D(1)) for v in long);q=(1-rho).exp()/2
        d=min(long[0],D(1));V=q*d;v=rho-d
        full=primitive(short,long);new=primitive(short,altered)
        if sum(altered)>=1:
            qnew=(1-sum(min(x,D(1)) for x in altered)).exp()/2
            R=qnew*min(own_new,D(1));B=qnew-q
        else:
            t=sum(altered)
            qnew=(1-sum(min(x,t) for x in short)/t).exp()/2 if t else D(1)/2
            R=(1-qnew)*own_new;B=1-q-qnew;switches+=1
        require(B>=-tol,'negative response amplitude')
        require(-tol<=R<=V+tol,'remaining long role not monotone')
        require(B+R<=K*V+tol,'retention-amplitude constraint')
        require(sum(new)-sum(full)<=B*(v-1)-(V-R)+tol,'total net response')
        net_checks+=1
        require(full[0]-new[0]>=V-R-tol,'actual own loss below long-role loss')
        own_checks+=1
        checks+=1
    asym=[];limit=-c*(2+K*D(2).ln());lower=-c*(e+1+K*D(2).ln())
    for L in map(D,(12,30,100,1000,10000)):
        eps=(-L).exp();beta=(-K*eps*(1+L)).exp();target=L+1-D(2).ln()-(K+1)/K
        x=target
        for _ in range(100):
            nx=x-(x+x.ln()-target)/(1+1/x)
            if abs(nx-x)<D('1e-75'):break
            x=nx
        a=1/x
        direct=K*(1-a)*(L+a.ln()-D(2).ln())-(K+1)*(1-a)-beta
        closed=K*(x-2+1/x)-beta
        require(abs(direct-closed)<tol,'net-charge optimizer identity')
        coef=c*(2*K+closed-K*(L-L.ln()))
        asym.append({'L':str(L),'A_star':str(a),'linearized_residual':str(coef)})
    require(abs(limit-lower-c*K)<D('1e-70'),'remaining interval width')
    source=Path(__file__).with_name('NET_HARDWARE_RESPONSE_CHARGE.txt')
    return {'status':'PASS','arithmetic':'90-digit Decimal finite direct-primitive corroboration',
      'mixed_long_underreports':checks,'pool_switches':switches,'net_response_checks':net_checks,'actual_own_loss_checks':own_checks,
      'new_upper_residual':str(limit),'accepted_lower_residual':str(lower),'interval_width':str(c*K),
      'asymptotic_diagnostics':asym,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=90
        print(json.dumps(run(),indent=2,sort_keys=True))
