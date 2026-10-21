#!/usr/bin/env python3
"""Independent exact checks for sharp-Q extension; all-Q proof is in note."""
from fractions import Fraction as F
from pathlib import Path
import json
result=[]
for Q,mult in [(3,1),(3,2),(3,5),(4,1),(4,2),(5,1),(10,1)]:
    h=8*Q*(Q-1);d=mult*16*Q*(Q-1)*(Q+3)
    n=Q**d;M=n//Q;m=n-(Q-1)*d-1
    x=F(h,d);mu=F(Q-2,Q-1)+x/(Q-1)
    beta0=F(Q-1,Q)-F(24,d)
    K=(beta0.numerator*m)//beta0.denominator
    beta=F(K,m);a=1-mu;b=1-beta
    e=(Q-1)**2*d*(d-1)//2
    f=[M-1-(Q-1)*d*(d-1)//2]+[M-d-(Q-2)*d*(d-1)//2]*(Q-1)
    checks={}
    def check(label,predicate):
        checks[label]=bool(predicate)
        assert predicate,(Q,mult,label)
    avail=F(Q-1,Q)-2*x/(Q*(Q-1))
    check('availability gap',avail-beta0==F(8,d))
    check('neighbor gap',beta0-mu==F(1,Q*(Q-1))-F(8*(Q+3),d))
    check('neighbor gap lower',beta0-mu>=F(1,2*Q*(Q-1)))
    check('large color class',M>100*Q**4*d**3)
    check('m large',m>M>h)
    check('beta ordering',0<mu<beta<=beta0<1)
    check('cut coefficient',Q*beta0-Q+2>=F(7,8))
    check('Hall i',K-e>=(Q-2)*M)
    check('Hall ii',all(K<=sum(f)-z for z in f))
    check('Hall iii',all(K-e>=(Q*beta-Q+2)*(sum(f)-z) for z in f))
    check('off-row strict gap',h*(beta-mu)-beta>2)
    k=n-(Q-2)*d-h-K
    t=1+(Q-1)*d*a*a+m*b*b
    check('support potential',t==1+(d-h)*a+(m-K)*b)
    check('density',k>=F(n,Q))
    rho=F(n,k*k);ell=1/t
    check('unit mass bound',ell<=rho)
    # Exact scalar squared-envelope identity for three rational R values.
    A=Q*Q
    for R in [F(1,2),F(1),F(A,A-2)]:
        maximum=F(A*A,4*(A-1))
        value=(R*R+A*R)/(1+R)**2
        remainder=((A-2)*R-A)**2/(4*(A-1)*(1+R)**2)
        check('squared identity '+str(R),maximum-value==remainder)
    result.append({'Q':Q,'multiple':mult,'d':d,'checks':checks})
out={'status':'PASS','cases':result,'total_checks':sum(len(r['checks']) for r in result),
     'scope':'Finite exact diagnostics; conventional all-Q proof is separate.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],out['total_checks'])
