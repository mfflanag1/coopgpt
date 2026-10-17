"""Exact algebra checks for the planar L1 scope boundary; general proof is analytic."""
from fractions import Fraction as F


def H(x,y):return (x*(x*x-y*y),y*(y*y-x*x))


def main():
    p2=0
    for den in range(2,50):
        for num in range(1,den):
            u=F(num,den)
            a=2*u/(1-u*u)
            f=(1+u*u)/(1-u*u)
            assert f*f==1+a*a
            fp=a/f
            first_mass=a*fp-f+1
            tail_first=f-a*fp
            assert first_mass>=0 and tail_first>0
            assert a*fp+tail_first==f
            assert f-a*fp==1/f
            p2+=1
    endpoints=0
    for xnum in range(-30,31):
        for ynum in range(-30,31):
            x,y=F(xnum,7),F(ynum,11)
            assert (abs(x+y)+abs(x-y))/2==max(abs(x),abs(y))
            hx,hy=H(x,y)
            assert H(y,x)==(hy,hx)
            assert H(-x,y)==(-hx,hy)
            assert H(x,-y)==(hx,-hy)
            endpoints+=1
    for a in [F(j,13) for j in range(1,100)]:
        assert H(a,a)==(0,0)
        # Along this line H is quadratic, so the central difference is exact.
        h=F(1,17)
        plus,minus=H(a+h,a-h),H(a-h,a+h)
        derivative=tuple((u-v)/(2*h) for u,v in zip(plus,minus))
        assert derivative==(4*a*a,-4*a*a)
    print(f'PASS: {p2} exact p2 antiderivative points; {endpoints} infinity isometries and signed/permutation symmetries; 99 transverse derivatives.')


if __name__=='__main__':main()
