"""Exact rational certificate for the personal-ceiling coverage obstruction."""
from fractions import Fraction as Q
from math import factorial
import json


def _verify_assert(condition, message=None):
    """Always-active assertion; evaluate an optional message only on failure."""
    if not condition:
        if message is None:
            raise AssertionError
        raise AssertionError(message())


def bound(q):
    m=q*q;t=Q(q-2,2*q*q)
    return Q(2*q,q*q-1)+Q(2,q)+Q(1,1+2**m)+q*q*(Q(1,2**m)+(1-t)**m)


def run():
    rows=[]
    for q in [4,8,16,32,64,128]:
        m=q*q;delta=Q(1,m);t=Q(1,2*q)-delta
        _verify_assert((t==Q(q-2,2*q*q)>0))
        # Avoid materializing N, its graph, or its probability power: cancel it
        # algebraically in the two CDF products using exact rational arithmetic.
        _verify_assert((Q(q,1)**m*Q(1,2*q)**m==Q(1,2**m)))
        _verify_assert((Q(q,1)**m*Q(2,q)**m==2**m))
        _verify_assert((Q(2,q)/(1-delta)==Q(2*q,q*q-1)))
        r=bound(q)
        target={16:Q(1,2),32:Q(1,4),64:Q(1,8),128:Q(1,16)}.get(q)
        if target:_verify_assert((r<target))
        rows.append(dict(q=q,m=m,R_upper_decimal=float(r),
                         coverage_multiplier_lower_decimal=float(1/r),
                         certified_R_less_than=str(target) if target else None,
                         rational_numerator_bits=r.numerator.bit_length(),
                         rational_denominator_bits=r.denominator.bit_length()))
    # Finite sanity check; the all-N Bernoulli inequality is proved analytically.
    for n in range(1,30):
        for den in range(2,20):
            for num in range(den):
                x=Q(num,den)
                _verify_assert(((1-x)**n<=1/(1+n*x)))
    return dict(status='PASS',rows=rows,
                scope='Exact rational tail bounds; no huge graph enumeration or Monte Carlo claim.')


if __name__=='__main__':
    # Python limits conversion of huge integers to strings; digit counts above
    # are descriptive only and can use bit lengths instead for larger q.
    import sys
    if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
    print(json.dumps(run(),indent=2))
