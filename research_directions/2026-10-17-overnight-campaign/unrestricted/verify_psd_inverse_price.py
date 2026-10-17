from fractions import Fraction as F
from itertools import combinations,product

def worth(xs):return min(map(sum,zip(*xs)))
def pay(xs):
    totals=list(map(sum,zip(*xs))); T=min(totals)
    return [T*sum(x/t for x,t in zip(row,totals)) for row in xs] if T else [F(0)]*len(xs)

checks=0
for m in (2,3,4):
    vs=list(product(map(F,range(3)),repeat=m))
    for index in range(180):
        n=2+index%3
        xs=[vs[(index*(i+1)+7*i)%len(vs)] for i in range(n)]
        ys=pay(xs)
        assert sum(ys)==m*worth(xs)
        for k in range(1,n+1):
            for S in combinations(range(n),k):
                assert sum(ys[i] for i in S)>=worth([xs[i] for i in S])
                high=list(xs);ds=[]
                for i in S:
                    d=vs[(index+3*i+k)%len(vs)];ds.append(d)
                    high[i]=tuple(x+y for x,y in zip(xs[i],d))
                yh=pay(high)
                assert sum(yh[i]-ys[i] for i in S)>=worth(ds)
                checks+=1
print(f'PASS: {checks} exact coalition coverage/full-OUT comparisons, including singular starts.')
