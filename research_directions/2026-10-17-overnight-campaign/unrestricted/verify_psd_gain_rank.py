"""Exact diagonal checks of the original-rank PSD gain theorem."""
from fractions import Fraction as F
from itertools import combinations, product


def production(xs):
    return min(map(sum,zip(*xs)))


def payments(xs, residual=False):
    m=len(xs[0])
    fs=list(map(min,xs))
    g=production(xs)-sum(fs)
    if residual:
        ranks=[sum(x>f for x in row) for row,f in zip(xs,fs)]
    else:
        ranks=[sum(x>0 for x in row) for row in xs]
    return [f+F(r,m)*g for f,r in zip(fs,ranks)]


def subsets(n):
    return [S for k in range(1,n+1) for S in combinations(range(n),k)]


def main():
    covers=individual=coalitional=0
    for m in (2,3,4):
        vectors=list(product(map(F,range(3)),repeat=m))
        for index in range(250):
            n=2+index%4
            xs=[vectors[(index*(i+1)+7*i)%len(vectors)] for i in range(n)]
            y=payments(xs)
            fs=list(map(min,xs))
            g=production(xs)-sum(fs)
            R=sum(sum(x>0 for x in row) for row in xs)
            assert min(y)>=0
            assert sum(y)==sum(fs)+F(R,m)*g
            for S in subsets(n):
                assert sum(y[i] for i in S)>=production([xs[i] for i in S])
                covers+=1
            for i in range(n):
                D=vectors[(index+11*i+1)%len(vectors)]
                high=list(xs)
                high[i]=tuple(x+d for x,d in zip(xs[i],D))
                yh=payments(high)
                assert yh[i]-y[i]>=min(D)
                individual+=1

            # Fixed singular diagonal face per owner: retain a designated zero.
            singular=[]
            for i,row in enumerate(xs):
                singular.append(tuple(F(0) if j==i%m else x for j,x in enumerate(row)))
            y0=payments(singular)
            for S in subsets(n):
                high=list(singular)
                Ds=[]
                for i in S:
                    D=tuple(F(0) if j==i%m else F((index+i+j)%3) for j in range(m))
                    Ds.append(D)
                    high[i]=tuple(x+d for x,d in zip(high[i],D))
                yh=payments(high)
                assert sum(yh[i]-y0[i] for i in S)>=production(Ds)
                coalitional+=1

    low=[(F(0),F(1,10),F(2)),(F(1),F(1),F(0))]
    high=[(F(1,10),F(1,10),F(2)),low[1]]
    assert payments(low,True)[0]==F(2,3)
    assert payments(high,True)[0]==F(13,30)
    assert payments(high,True)[0]-payments(low,True)[0]==-F(7,30)
    assert payments(high)[0]==F(11,10)
    low=[(F(1),F(0)),(F(0),F(1)),(F(0),F(1))]
    high=[(F(1),F(1)),low[1],low[2]]
    assert payments(low)==[F(1,2)]*3
    assert payments(high)==[F(1),F(0),F(0)]
    assert sum(payments(high))-sum(payments(low))==-F(1,2)
    print(f"PASS: {covers} exact coalition covers; {individual} own full-OUT restorations; "
          f"{coalitional} singular-domain coalition OUT comparisons; both exact scope obstructions.")


if __name__=='__main__':
    main()
