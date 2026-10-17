"""Exact algebraic certificate checks accompanying the all-profile proof."""
from fractions import Fraction as Q
from math import comb, isqrt
from pathlib import Path
import json
checks=0
examples=[]
for M in range(2,501):
    P=Q(1)
    for m in range(2,M+1):
        P*=Q(2*m,2*m-1)
    assert P==Q(4**M,2*comb(2*M,M))
    for R in (1,2,3,5,7,10,17,31):
        eps=Q(1,R)
        k=P*R/(R*R+P)
        assert k==P*eps*(1-k*eps)
        assert k>=0
        # Solving the recursive equality is precisely the finite lower.
        t=eps*(1-k*eps)
        for m in range(2,M+1):
            t*=Q(2*m,2*m-1)
        assert t==k
        checks+=1
    for B in range(1,8):
        R=2*B
        bound=P*R/(R*R+P)
        assert (bound>B)==(P>4*B*B)
        checks+=1
    if M in (2,3,4,10,100,500):
        R=max(1,isqrt(P.numerator//P.denominator))
        candidates=[(r,P*r/(r*r+P)) for r in (R,R+1)]
        r,k=max(candidates,key=lambda x:x[1])
        examples.append({'M':M,'R':r,'lower_exact':str(k),'owners':2*M+r})
out={'status':'PASS','exact_fraction_cases':checks,'max_M':500,
     'examples':examples,
     'limits':'Exact algebra/product/equality checks; the finite-owner symmetry and TCWM proof is in the note.'}
Path(__file__).with_name('COMMON_CAP_QUARTER_LOWER_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='examples'},indent=2))
