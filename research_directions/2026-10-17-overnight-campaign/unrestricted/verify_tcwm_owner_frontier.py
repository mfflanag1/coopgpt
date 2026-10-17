from fractions import Fraction as Q
from math import isqrt
if not __debug__:
    raise RuntimeError('Assertions required: run without Python -O')
checks=0
for r in range(2,82):
    for s in range(2,122):
        m=(r-1)*s; u=s-1; L=m-1
        original=Q((s-1)*((r-1)*s-1),2*s*s+(r-3)*s-1)
        harmonic=Q(L*u,2*u*u+2*u+L)
        assert original==harmonic
        # Rational equivalent of the continuous envelope bound:
        # L/beta-2 >= 2sqrt(2L), with nonnegative left side.
        lhs=Q(L,1)/harmonic-2
        assert lhs>=0 and lhs*lhs>=8*L
        # Derivative numerator, after cancellation of positive denominators.
        derivative_num=L*(2*u*u+2*u+L)-L*u*(4*u+2)
        assert derivative_num==L*(L-2*u*u)
        checks+=1
for t in range(2,202):
    r=2*t+1;s=t;n=2*t*t+1
    assert (r-1)*s+1==n
    assert Q((s-1)*((r-1)*s-1),2*s*s+(r-3)*s-1)==Q((t-1)*(2*t*t-1),4*t*t-2*t-1)
    for nn in range(n,min(n+10,2*(t+1)**2+1)):
        tt=isqrt((nn-1)//2)
        assert tt==t and 2*tt*tt+1<=nn
    checks+=1
print(f'PASS {checks} exact rational owner-frontier checks; asymptotic limits analytic')
