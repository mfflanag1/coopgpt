#!/usr/bin/env python3
"""Finite high-precision corroboration, not an all-real proof or optimizer certificate."""
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib,json,random
D=Decimal

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

def run():
    rng=random.Random(2026101701)
    e=D(1).exp(); K=e-1; c=1/(2*e); log2=D(2).ln()
    tol=D('1e-65')
    branches=0; bundles=0
    for _ in range(10000):
        rho=D(rng.randrange(1000,100001))/1000
        d=D(rng.randrange(1,1001))/1000
        q=(1-rho).exp()/2
        V=q*d
        a=1-q
        u=a/V
        v=rho-d
        require(u>=1,'effective role ratio below one')
        require(v<=(u/2).ln()+1/u+tol,'first effective entropy inequality')
        require((u/2).ln()+1/u<=((u+2)/2).ln()+tol,'second effective entropy inequality')
        require(v<=((a+2*V)/(2*V)).ln()+tol,'effective entropy inequality')
        branches+=1
    for _ in range(1000):
        m=rng.randrange(1,30)
        rows=[]
        for _ in range(m):
            t=D(rng.randrange(1,1001))/1000
            rho=D(rng.randrange(1000,20001))/1000
            d=D(rng.randrange(1,1001))/1000
            q=(1-rho).exp()/2
            V=q*d*t
            R=V*D(rng.randrange(1001))/1000
            W=K*V-R
            rows.append((t*(1-q),V,W,rho-d))
        a=sum(r[0] for r in rows); V=sum(r[1] for r in rows); W=sum(r[2] for r in rows)
        lhs=sum(r[2]*r[3] for r in rows)
        rhs=W*(K*(a+2*V)/(2*W)).ln()
        require(lhs<=rhs+tol,'branchwise retained entropy log-sum')
        bundles+=1
    asymptotics=[]
    limit=c*(K-2-K*log2)
    for L in map(D,(12,30,100,1000,10000)):
        eps=(-L).exp(); beta=(-K*eps*(1+L)).exp()
        target=L+1-log2-beta/K
        x=target
        for _ in range(100):
            nx=x-(x+x.ln()-target)/(1+1/x)
            if abs(nx-x)<D('1e-75'): break
            x=nx
        require(abs(x+x.ln()-target)<D('1e-65'),'stationarity root')
        a=1/x
        require(eps.sqrt()<a<D(1)/4,'optimizer outside asymptotic middle region')
        direct=K*(1-a)*(L+a.ln()-log2)-beta*(2-a)
        closed=K*(x-2+1/x)-beta
        require(abs(direct-closed)<D('1e-65'),'optimizer value identity')
        coefficient=c*(2*K+closed-K*(L-L.ln()))
        asymptotics.append({'L':str(L),'A_star':str(a),'scaled_residual_linearized':str(coefficient)})
    lower=-c*(e+1+K*log2)
    require(abs((limit-lower)-2*c*K)<D('1e-70'),'residual interval width')
    source=Path(__file__).with_name('EFFECTIVE_HARDWARE_ENTROPY_MASS.txt')
    return {'status':'PASS','arithmetic':'90-digit Decimal finite corroboration, not a universal numerical certificate',
      'pointwise_branch_checks':branches,'retained_bundle_checks':bundles,'optimizer_checks':len(asymptotics),
      'new_upper_residual':str(limit),'accepted_lower_residual':str(lower),'interval_width':str(2*c*K),
      'asymptotic_diagnostics':asymptotics,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}

if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=90
        result=run()
        print(json.dumps(result,indent=2,sort_keys=True))
