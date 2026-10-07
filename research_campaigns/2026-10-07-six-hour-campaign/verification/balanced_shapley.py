"""Exact parameter and finite-threshold checks for the balanced pool proof."""
from fractions import Fraction as Q
import json


def _verify_assert(condition, message=None):
    """Always-active assertion; evaluate an optional message only on failure."""
    if not condition:
        if message is None:
            raise AssertionError
        raise AssertionError(message())


def run():
    bands=0;boolean_checks=0;endpoint_checks=0;diagonals=0
    for M in range(2,31):
        a=Q(1,4*M*M);q=lambda n:2*M*(n+1)-1
        beta=(Q(q(M),M+1)+Q(q(M-1),M))/2
        _verify_assert((q(M)-beta*(M+1)==Q(1,2*M)))
        for n in range(1,M):
            _verify_assert((q(n)-beta*(n+1)<=-Q(1,M*(M+1))));endpoint_checks+=1
        for n in range(2,M+1):
            b=(1-a)/n
            for j in range(1,n):
                d=n-j;r=d+1;m=(n+d-1)//d-1;bm=(1-a)/m
                _verify_assert((1<=m<n and m*d<n<=(m+1)*d))
                _verify_assert((Q(j,n)-Q(m-1,m)==Q(n-m*d,m*n)>=Q(1,M*M)))
                _verify_assert(((m-1)*bm+a<j*b<j*b+a<1-a))
                gap=q(m)*r-q(n)
                _verify_assert((gap==2*M*((m+1)*d+m-n)-d>=M+1))
                _verify_assert((Q(gap,2)>=Q(1,2) and Q(gap,2*r)>=Q(1,2)))
                bands+=1
                if M<=8:
                    theta=j*b+a/2
                    for mask in range(1<<(n+1)):
                        actual=a*(mask&1)+b*(mask>>1).bit_count()>=theta
                        expected=mask.bit_count()>=j+1
                        _verify_assert((actual==expected));boolean_checks+=1
                    for mask in range(1<<(m+1)):
                        actual=a*(mask&1)+bm*(mask>>1).bit_count()>=theta
                        expected=(mask>>1).bit_count()==m
                        _verify_assert((actual==expected));boolean_checks+=1
        R=4*(M+1)*M*(2**(M+1)+1);target=Q(1,4*(M+1))
        bounds=[Q(M-1,R*R),Q(1,R),Q(M-1,R*R),
                Q(M*(M-1)*(2**(M+1)+1),2*R*R)]
        _verify_assert((all(x<=target for x in bounds)));diagonals+=1
    finite=Q(2,5)+Q(3,100)+Q(1,100000)+Q(3,10**320)+Q(198,10**20)
    _verify_assert((finite<Q(431,1000)<Q(1,2)))
    return dict(status='PASS',interior_band_parameter_cases=bands,
                finite_boolean_threshold_checks=boolean_checks,
                endpoint_exponent_checks=endpoint_checks,growing_diagonal_checks=diagonals,
                finite_M4_upper_bound=str(finite),
                scope='Exact algebra, finite threshold truth tables, and explicit rational error bound; no enumeration of the enormous full game, whose proof is analytic.')


if __name__=='__main__':print(json.dumps(run(),indent=2))
