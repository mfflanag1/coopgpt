#!/usr/bin/env python3
"""Independent exact scalar replay of the all-Q proof. No numerical solver.
Finite cases are diagnostics; the accompanying audit proves all Q>=3.
"""
from fractions import Fraction as F
from pathlib import Path
import json

reports=[]
for Q in (3,4,5,6,10):
    d=16*Q*(Q-1)*(Q+2);h=8*Q*(Q-1)
    n=Q**d;M=n//Q;m=n-(Q-1)*d-1
    x=F(h,d);mu=F(Q-2, Q-1)+x/(Q-1)
    delta=F(1,4*Q*(Q-1));beta0=mu+delta;b0=1-beta0
    K=(beta0.numerator*m)//beta0.denominator
    beta=F(K,m);b=1-beta;a=1-mu
    e=(Q-1)**2*d*(d-1)//2
    f=[M-1-(Q-1)*d*(d-1)//2]+[M-d-(Q-2)*d*(d-1)//2]*(Q-1)
    k=n-(Q-2)*d-h-K
    t=1+(Q-1)*d*a*a+m*b*b
    rho=F(n,k*k);ell=1/t
    cond={}
    def check(name,predicate):
        assert predicate,(Q,name)
        cond[name]=bool(predicate)
    check('x identity',x==F(1,2*(Q+2)))
    check('neighbor marginal',(mu+x+Q-2)/Q==mu)
    B=F(Q-1,Q)-2*x/(Q*(Q-1))
    check('exceptional availability margin',B-mu==2*delta and B>beta0>=beta)
    check('far counts',sum(f)==m-e)
    check('large M',M>100*Q**4*d*d)
    check('far class bounds',all(M-Q*d*d<=v<=M and v>0 for v in f))
    check('error bound',e+Q*d+2<=Q*Q*d*d)
    check('floor lower',K-e>=beta0*Q*M-Q*Q*d*d)
    check('beta and neighbor ordering',beta0>=beta>mu and a>b>F(1,Q))
    check('Hall small-class cuts',K-e>=(Q-2)*M)
    check('Hall full available capacity',all(K<=sum(f)-v for v in f))
    check('Hall Q-1-class cuts',all(K-e>=(Q*beta-Q+2)*(sum(f)-v) for v in f))
    check('Hall expected size',K-e*beta==beta*sum(f))
    check('norm support potential',t==1+(d-h)*a+(m-K)*b)
    gap=h*(beta-mu)-beta
    check('off-row identity',d*a+(k-d)*b-t==gap)
    check('all off-row strictness',gap>0)
    check('density upper',0<k<F(n,Q-1))
    check('density lower',k>n*b>F(n,Q))
    check('norm bound',t<=n*b*b+Q*d)
    check('mass ratios',F(1,2)<ell/rho<=1)
    check('rho small',0<rho<F(1,2))
    blocks=(k*k)//n
    c=blocks*rho;N=blocks*n+1
    private=blocks*n*ell/(1+(blocks-1)*rho+ell)
    check('balanced blocks',F(1,2)<c<=1)
    check('N range',n<=N<=n*n and N<=2*blocks*n)
    check('funding exact square lower',private*private>F((Q-1)**2,64)*N)
    check('dimension cubic bound',d<=18*Q**3)
    reports.append({'Q':Q,'d':d,'h':h,'n_definition':f'{Q}^{d}',
                    'checks':cond,'number_of_checks':len(cond)})
result={'status':'PASS','scope':'Exact finite diagnostics; all-Q proof is in mass_geometry_qary_audit.txt',
        'cases':reports,'total_checks':sum(r['number_of_checks'] for r in reports)}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
