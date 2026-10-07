"""Exact certificate for the 10-owner common-clipping incentive failure."""
from fractions import Fraction as Q
from math import comb,factorial
import json


def _verify_assert(condition, message=None):
    """Always-active assertion; evaluate an optional message only on failure."""
    if not condition:
        if message is None:
            raise AssertionError
        raise AssertionError(message())


def monomial_integral(a,lo,hi,power,k,sign):
    return sum((comb(power,j)*a**(power-j)*sign**j*(hi**(j+k+1)-lo**(j+k+1))/Q(j+k+1)
                for j in range(power+1)),Q())


def stop(n,u):
    return Q(n**n,factorial(n+1))*sum(((-1)**j*comb(n,j)*max(Q(0),u-Q(j,n))**(n+1)
                                     for j in range(n+1)),Q())


def by_survival(n,h):
    d=Q(1,10);t=1+h;coeff=[Q(1),-2-1/d,1+2/d,-1/d];val=Q()
    for j in range(n+1):
        a=h-Q(j,n)
        if a<=0:continue
        val+=(-1)**j*comb(n,j)*sum((co*monomial_integral(a,Q(0),min(d,a),n,k,-1)
                                   for k,co in enumerate(coeff)),Q())
    return Q(1,2)-stop(n,1-h)+Q(n**n,factorial(n))*val/(2*t)


def by_density(n,h):
    # Independent representation: atom at W=0 plus its quadratic density.
    d=Q(1,10);t=1+h;atom=1-Q(1)/(2*t)
    density=[(2+1/d)/(2*t),-(2+4/d)/(2*t),3/(2*t*d)]
    result=atom*(Q(1,2)-stop(n,1-h))
    result+=sum((co*(d**(k+1)/(2*(k+1))+d**(k+2)/(k+2)) for k,co in enumerate(density)),Q())
    correction=Q()
    for j in range(n+1):
        a=1-h-Q(j,n);lo=max(Q(0),-a)
        if lo>=d:continue
        correction+=(-1)**j*comb(n,j)*sum((co*monomial_integral(a,lo,d,n+1,k,1)
                                         for k,co in enumerate(density)),Q())
    return result-Q(n**n,factorial(n+1))*correction


def run():
    rows=[]
    for n in range(1,13):
        a=by_survival(n,Q(3,4));b=by_survival(n,Q(1))
        _verify_assert((a==by_density(n,Q(3,4)) and b==by_density(n,Q(1))))
        rows.append(dict(N=n,low_payment=str(a),high_payment=str(b),gap=str(a-b)))
    gap=Q(rows[5]['gap'])
    _verify_assert((gap==Q(587847649425223,914457600000000000)>0))
    _verify_assert((Q(rows[4]['gap'])<0))
    large=Q(187,112000)-Q(1,2700)
    _verify_assert((large==Q(3929,3024000)>0))
    return dict(status='PASS',exact_gap=str(gap),owners=10,K=4,rows=rows,
                independent_large_N_bound=str(large),
                scope='Two independent exact integral representations; graph proof in companion note.')


if __name__=='__main__':print(json.dumps(run(),indent=2))
