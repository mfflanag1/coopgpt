"""Rational checks for the fixed normalized spectral-shape stopping proof."""
from fractions import Fraction as F


def main():
    identities=0
    for m in range(2,25):
        k=m-1
        for s in [F(3,2),F(2),F(5),F(11)]:
            for f in [F(1,10),F(1,3),F(1),F(3,2)]:
                for fp in [F(-3),F(-1),F(-1,10),F(0),F(1)]:
                    D=1+k*f
                    payment_derivative=(f*D+s*fp*(D-f))/(D*D)
                    invariant_log_derivative=1/s+fp*(1+(k-1)*f)/(f*(1+k*f))
                    assert invariant_log_derivative==payment_derivative*D/(s*f)
                    assert (payment_derivative>=0)==(invariant_log_derivative>=0)
                    identities+=1
    enclosures=0
    for m in range(2,101):
        k=m-1
        lo,hi=F(0),F(1)
        for _ in range(36):
            mid=(lo+hi)/2
            if m*mid**k<=1:lo=mid
            else:hi=mid
        assert m*lo**k<=1<=m*hi**k
        for s in (F(2),F(5),F(100)):
            for q in (hi,1+hi,7+hi):
                total=(1+k*q)/(1+k*q/s)
                assert total>=(1+k*lo)/(1+k*lo/s)
        enclosures+=1
    print(f'PASS: {identities} exact derivative identities; {enclosures} certified c_m enclosures and funding comparisons.')


if __name__=='__main__':main()
