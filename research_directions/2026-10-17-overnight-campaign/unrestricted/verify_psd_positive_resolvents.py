"""Exact checks of spectral-order and positive-resolvent funding identity."""
from fractions import Fraction as F


def main():
    checks=0
    for m in range(2,16):
        for scale in range(1,20):
            vals=[F(1)+F((j+1)**2-1,scale) for j in range(m)]
            for shifts in [(F(0),),(F(1),F(3)),(F(0),F(1,3),F(7,2))]:
                weights=[F(j+1,j+2) for j in range(len(shifts))]
                for const in [F(0),F(2,7)]:
                    f=[const+sum(w/(v+s) for w,s in zip(weights,shifts)) for v in vals]
                    left=sum(v*t for v,t in zip(vals,f))*sum(1/v for v in vals)-m*sum(f)
                    right=sum((vals[j]-vals[i])/(vals[i]*vals[j])*(vals[j]*f[j]-vals[i]*f[i])
                              for i in range(m) for j in range(i+1,m))
                    assert left==right and right>=0
                    total=sum(v*t for v,t in zip(vals,f))/sum(f)
                    assert total>=F(m)/sum(1/v for v in vals)
                    checks+=1
    for m in range(2,1000):
        for factor in (1,2,10,100):
            L=F(factor*m*m)
            baseline=F(m)/(1+F(m-1)/L)
            assert baseline<m and baseline>m-F(1,factor)
    print(f'PASS: {checks} rational mixture identities; 3992 growing-dimension lower-limit checks.')


if __name__=='__main__':main()
