"""Independent exact sanity checks of the L1 cone transfer, no author imports."""
from fractions import Fraction as F
from itertools import product, combinations


def sign_expression(k, a, b, r, v):
    return (k-1)*(abs(r)+abs(v))+(2*a-k)*r+(2*b-k)*v+abs(r-v)


def huber(profile):
    k = F(3, 2)
    n, d = len(profile), len(profile[0][1])
    y = [k*(t-sum(map(abs,x))) for t,x in profile]
    for j in range(d):
        aa = [max(x[j],F(0)) for _,x in profile]
        bb = [max(-x[j],F(0)) for _,x in profile]
        A, B = sum(aa), sum(bb)
        if not A or not B:
            continue
        if A >= B:
            r = B/A
            p, q = r/2, 1-r/2
        else:
            r = A/B
            q, p = r/2, 1-r/2
        y = [v+2*(a*p+b*q) for v,a,b in zip(y,aa,bb)]
    return y


def value(profile):
    d = len(profile[0][1])
    return sum(t for t,_ in profile)-sum(abs(sum(x[j] for _,x in profile)) for j in range(d))


def main():
    signs = restorations = coalitions = 0
    for k in [F(1),F(5,4),F(3,2),F(7,4),F(2),F(3)]:
        candidates = {F(0),k,F(1),2*k-1,k-1}
        corners = set()
        for a in candidates:
            for b in candidates | {1-a,2*k-1-a}:
                if 0<=a<=k and 0<=b<=k and 1<=a+b<=2*k-1:
                    corners.add((a,b))
        for a,b in corners:
            for r,v in product(map(F,range(-4,5)),repeat=2):
                expr = sign_expression(k,a,b,r,v)
                assert expr>=0
                if r>=v>=0:
                    assert expr==2*a*(r-v)+2*(a+b-1)*v
                elif r>=0>=v:
                    assert expr==2*a*r+2*(k-b)*(-v)
                elif 0>=r>=v:
                    assert expr==2*(k-b)*((-v)-(-r))+2*(2*k-1-a-b)*(-r)
                signs += 1

    # Deterministic, exact signed directions including sign-crossing restores.
    vectors = list(product(map(F,range(-1,2)), repeat=2))
    for index in range(180):
        n = 2+index%3
        profile=[]
        for i in range(n):
            x=vectors[(index*(i+1)+3*i)%len(vectors)]
            profile.append((sum(map(abs,x))+F((index+i)%2),x))
        y=huber(profile)
        T=value(profile)
        assert min(y)>=0 and sum(y)<=F(3,2)*T
        for size in range(1,n+1):
            for S in combinations(range(n),size):
                assert sum(y[i] for i in S)>=value([profile[i] for i in S])
                high=list(profile)
                for i in S:
                    dx=vectors[(index+2*i+size)%len(vectors)]
                    dt=sum(map(abs,dx))+F((i+index)%2,2)
                    t,x=high[i]
                    high[i]=(t+dt,tuple(a+b for a,b in zip(x,dx)))
                yh=huber(high)
                assert sum(yh[i] for i in S)>=sum(y[i] for i in S)
                restorations+=1
                coalitions+=1
    print(f"PASS: {signs} exact signed-gradient cases; {coalitions} coverage checks; "
          f"{restorations} actual-owner signed cone restorations.")


if __name__ == '__main__':
    main()
